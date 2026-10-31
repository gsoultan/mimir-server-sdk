// Webhook-receiver serves an address for mimir-server's webhooks, checks
// each delivery's signature and prints it.
//
//	MIMIR_WEBHOOK_SECRET=whsec_... go run ./examples/webhook-receiver
//
// Add the webhook in the console (Settings → Webhooks) or with
// client.Webhooks.Create; its secret is shown once, when it's made.
package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"sync"

	"github.com/gsoultan/mimir-server-sdk/webhook"
)

func main() {
	secret := os.Getenv("MIMIR_WEBHOOK_SECRET")
	if secret == "" {
		log.Fatal("set MIMIR_WEBHOOK_SECRET to the webhook's signing secret")
	}

	// The server retries until it gets a 2xx, so the same event can come
	// twice. Remember the ones already handled (a real app would use its
	// database).
	var mu sync.Mutex
	seen := map[string]bool{}

	http.Handle("POST /hooks/mimir", webhook.Handler(secret, func(_ context.Context, ev *webhook.Event) error {
		mu.Lock()
		dup := seen[ev.ID]
		seen[ev.ID] = true
		mu.Unlock()
		if dup {
			return nil
		}
		switch ev.Type {
		case webhook.TrainingFinished, webhook.TrainingFailed:
			job, err := ev.Job()
			if err != nil {
				return err
			}
			fmt.Printf("%s: %s %s (accuracy %.1f%%) %s\n", ev.Type, job.Name, job.Status, job.Accuracy*100, job.Error)
		case webhook.ScoringFinished, webhook.ScoringFailed:
			sc, err := ev.Scoring()
			if err != nil {
				return err
			}
			fmt.Printf("%s: %s with %s, %d of %d rows answered %s\n", ev.Type, sc.Name, sc.Model, sc.Done-sc.Failed, sc.Rows, sc.Error)
		case webhook.ModelCreated, webhook.ModelUpdated, webhook.ModelDeleted:
			m, err := ev.Model()
			if err != nil {
				return err
			}
			fmt.Printf("%s: %s (%s) by %s\n", ev.Type, m.Model.Name, m.Model.ID, m.Actor)
		default:
			fmt.Printf("%s: %s\n", ev.Type, ev.Data)
		}
		return nil
	}))
	addr := ":9000"
	log.Printf("listening on %s/hooks/mimir", addr)
	log.Fatal(http.ListenAndServe(addr, nil))
}
