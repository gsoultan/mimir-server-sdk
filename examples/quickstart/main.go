// Quickstart lists the models on a server and asks one a question.
//
//	MIMIR_URL=http://localhost:8080 MIMIR_API_KEY=mimir_... go run ./examples/quickstart
package main

import (
	"context"
	"errors"
	"fmt"
	"log"
	"os"

	mimirsdk "github.com/gsoultan/mimir-server-sdk"
)

func main() {
	if err := run(context.Background()); err != nil {
		log.Fatal(err)
	}
}

func run(ctx context.Context) error {
	client, err := mimirsdk.NewFromEnv()
	if err != nil {
		return err
	}

	me, err := client.Auth.WhoAmI(ctx)
	if errors.Is(err, mimirsdk.ErrUnauthenticated) {
		return fmt.Errorf("the API key in %s isn't valid: %w", mimirsdk.EnvAPIKey, err)
	}
	if err != nil {
		return err
	}
	fmt.Printf("Signed in as %s\n\n", me.GetUser().GetEmail())

	models, err := client.Models.List(ctx)
	if err != nil {
		return err
	}
	if len(models) == 0 {
		fmt.Println("No models yet. Train one in the console, or run examples/train.")
		return nil
	}
	for _, m := range models {
		fmt.Printf("%-24s %-14s %s\n", m.GetName(), m.GetArchitecture(), m.GetId())
	}

	// Ask the first model that reads a table row about a made-up row: the
	// most common value of each category column, and empty (the column's
	// usual fill) for the rest.
	for _, m := range models {
		if len(m.GetColumns()) == 0 {
			continue
		}
		row := map[string]string{}
		for _, col := range m.GetColumns() {
			row[col.GetName()] = ""
			if v := col.GetValues(); len(v) > 0 {
				row[col.GetName()] = v[0]
			}
		}
		answer, err := client.Models.PredictFields(ctx, m.GetId(), row)
		if err != nil {
			return err
		}
		fmt.Printf("\n%s answers:", m.GetName())
		if answer.GetNumber() {
			fmt.Printf(" %.3f\n", answer.GetValue())
			return nil
		}
		for _, g := range answer.GetGuesses() {
			fmt.Printf(" %s (%.0f%%)", g.GetLabel(), g.GetProbability()*100)
		}
		fmt.Println()
		return nil
	}
	fmt.Fprintln(os.Stderr, "\nNo model reads a table row, so nothing was asked.")
	return nil
}
