// Copyright (c) 2026 Gembit Soultan Shirazi
// SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0 OR PolyForm-Small-Business-1.0.0 OR LicenseRef-Commercial
//
// This file is part of mimir-server-sdk, the Go client for mimir-server,
// created and owned by Gembit Soultan Shirazi.
// It is free to use for personal and other noncommercial purposes, for
// nonprofits, and for companies with fewer than 100 people and under
// 1,000,000 USD in yearly revenue, under the PolyForm Noncommercial and
// PolyForm Small Business licenses. Any other use needs a commercial
// license from Gembit Soultan Shirazi. See the LICENSE and LICENSING.md files
// at the root of this repository.

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
