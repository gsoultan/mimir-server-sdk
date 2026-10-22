package webhook_test

import (
	"context"
	"log"
	"net/http"

	"github.com/gsoultan/mimir-server-sdk/webhook"
)

func ExampleHandler() {
	secret := "whsec_..." // shown once, when the webhook is made
	http.Handle("POST /hooks/mimir", webhook.Handler(secret, func(ctx context.Context, ev *webhook.Event) error {
		if ev.Type != webhook.TrainingFinished {
			return nil
		}
		job, err := ev.Job()
		if err != nil {
			return err
		}
		log.Printf("%s is ready: model %s, %.0f%% right", job.Name, job.ModelID, job.Accuracy*100)
		return nil
	}))
}

func ExampleVerify() {
	var r *http.Request // an incoming delivery
	var body []byte     // its raw body, read before decoding
	if err := webhook.Verify("whsec_...", r.Header.Get(webhook.SignatureHeader), body, 0); err != nil {
		log.Print("not from mimir-server: ", err)
	}
}
