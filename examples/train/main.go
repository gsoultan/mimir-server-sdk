// Train uploads a CSV, teaches a model from it, waits for it to finish and
// asks it about the first row.
//
//	MIMIR_URL=http://localhost:8080 MIMIR_API_KEY=mimir_... go run ./examples/train data.csv [answer-column]
package main

import (
	"context"
	"encoding/csv"
	"errors"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strings"
	"time"

	mimirsdk "github.com/gsoultan/mimir-server-sdk"
)

func main() {
	if len(os.Args) < 2 {
		log.Fatal("usage: train <file.csv> [answer-column]")
	}
	target := ""
	if len(os.Args) > 2 {
		target = os.Args[2]
	}
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Minute)
	defer cancel()
	if err := run(ctx, os.Args[1], target); err != nil {
		log.Fatal(err)
	}
}

func run(ctx context.Context, path, target string) error {
	client, err := mimirsdk.NewFromEnv()
	if err != nil {
		return err
	}
	f, err := os.Open(path)
	if err != nil {
		return err
	}
	defer f.Close()
	name := strings.TrimSuffix(filepath.Base(path), filepath.Ext(path))

	created, err := client.Datasets.UploadCSV(ctx, name, target, f)
	if err != nil {
		return err
	}
	ds := created.GetDataset()
	fmt.Printf("Stored %d rows; %s is the answer.\n", ds.GetRows(), ds.GetTarget())
	if len(ds.GetArchitectures()) == 0 {
		return errors.New("no model type can learn from this data")
	}

	job, err := client.Training.Start(ctx, &mimirsdk.CreateJobRequest{
		Name:         name,
		Architecture: ds.GetArchitectures()[0],
		DatasetId:    ds.GetId(),
	})
	if err != nil {
		return err
	}
	job, err = client.Training.Wait(ctx, job.GetId(), mimirsdk.WaitOptions{
		OnProgress: func(j *mimirsdk.Job) {
			fmt.Printf("\r%-10s epoch %d of %d", strings.ToLower(strings.TrimPrefix(j.GetStatus().String(), "JOB_STATUS_")), j.GetEpoch(), j.GetSettings().GetEpochs())
		},
	})
	fmt.Println()
	if err != nil {
		return err
	}
	fmt.Printf("Model %s gets %.1f%% of held-out examples right.\n", job.GetModelId(), job.GetAccuracy()*100)

	// Ask about the first row of the file.
	if _, err := f.Seek(0, 0); err != nil {
		return err
	}
	rows, err := csv.NewReader(f).ReadAll()
	if err != nil || len(rows) < 2 {
		return err
	}
	fields := map[string]string{}
	for i, col := range rows[0] {
		if col != ds.GetTarget() && i < len(rows[1]) {
			fields[col] = rows[1][i]
		}
	}
	answer, err := client.Models.PredictFields(ctx, job.GetModelId(), fields)
	if err != nil {
		return err
	}
	if answer.GetNumber() {
		fmt.Printf("First row: %.3f\n", answer.GetValue())
	} else if g := answer.GetGuesses(); len(g) > 0 {
		fmt.Printf("First row: %s (%.0f%% sure)\n", g[0].GetLabel(), g[0].GetProbability()*100)
	}
	return nil
}
