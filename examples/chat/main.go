// Chat talks with a language model, printing its answers as they are
// written. Upload a GGUF model in the console first.
//
//	MIMIR_URL=http://localhost:8080 MIMIR_API_KEY=mimir_... go run ./examples/chat <model-id>
package main

import (
	"bufio"
	"context"
	"fmt"
	"log"
	"os"
	"os/signal"
	"strings"

	mimirsdk "github.com/gsoultan/mimir-server-sdk"
)

func main() {
	if len(os.Args) != 2 {
		log.Fatal("usage: chat <model-id>")
	}
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt)
	defer stop()
	if err := run(ctx, os.Args[1]); err != nil {
		log.Fatal(err)
	}
}

func run(ctx context.Context, modelID string) error {
	client, err := mimirsdk.NewFromEnv()
	if err != nil {
		return err
	}
	var history []*mimirsdk.ChatMessage
	in := bufio.NewScanner(os.Stdin)
	for {
		fmt.Print("you> ")
		if !in.Scan() {
			return in.Err()
		}
		line := strings.TrimSpace(in.Text())
		if line == "" {
			continue
		}
		history = append(history, mimirsdk.UserMessage(line))

		var answer strings.Builder
		fmt.Print("model> ")
		for piece, err := range client.Models.Chat(ctx, &mimirsdk.ChatRequest{ModelId: modelID, Messages: history}) {
			if err != nil {
				return err
			}
			fmt.Print(piece.GetText())
			answer.WriteString(piece.GetText())
			if piece.GetDone() {
				fmt.Printf("\n  (%d tokens in %.1fs)\n", piece.GetGeneratedTokens(), float64(piece.GetDurationMicros())/1e6)
			}
		}
		history = append(history, mimirsdk.AssistantMessage(answer.String()))
	}
}
