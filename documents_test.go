package mimirsdk_test

import (
	"context"
	"errors"
	"testing"
	"time"

	mimirv1 "github.com/gsoultan/mimir-server/gen/mimir/v1"

	mimirsdk "github.com/gsoultan/mimir-server-sdk"
)

func TestWaitDocument(t *testing.T) {
	f := &fake{getDocument: func(n int) (*mimirv1.GetDocumentResponse, error) {
		status := mimirv1.JobStatus_JOB_STATUS_RUNNING
		if n > 1 {
			status = mimirv1.JobStatus_JOB_STATUS_SUCCEEDED
		}
		return &mimirv1.GetDocumentResponse{Document: &mimirv1.Document{Id: "d1", Name: "guide.pdf", Status: status, Passages: 12}}, nil
	}}
	c := start(t, f)
	d, err := c.Documents.WaitDocument(context.Background(), "d1", time.Millisecond)
	if err != nil || d.GetPassages() != 12 {
		t.Fatalf("document %v, %v", d, err)
	}

	f = &fake{getDocument: func(int) (*mimirv1.GetDocumentResponse, error) {
		return &mimirv1.GetDocumentResponse{Document: &mimirv1.Document{Id: "d2", Name: "scan.pdf", Status: mimirv1.JobStatus_JOB_STATUS_FAILED, Error: "It couldn't be read: its pages have no text."}}, nil
	}}
	c = start(t, f)
	_, err = c.Documents.WaitDocument(context.Background(), "d2", time.Millisecond)
	var de *mimirsdk.DocumentError
	if !errors.As(err, &de) || err.Error() != "mimirsdk: document scan.pdf not read: It couldn't be read: its pages have no text." {
		t.Fatalf("error %v", err)
	}
}

func TestAskText(t *testing.T) {
	f := &fake{ask: func(req *mimirv1.AskRequest, send func(*mimirv1.AskResponse) error) error {
		if req.GetCollectionId() != "c1" || len(req.GetMessages()) != 1 {
			t.Errorf("request %v", req)
		}
		sources := []*mimirv1.Passage{{Id: "p1", DocumentName: "returns.html", Number: 1, Text: "Items can be returned within 30 days."}}
		for _, m := range []*mimirv1.AskResponse{
			{Sources: sources, Text: "Within 30 days "},
			{Text: "[1]."},
			{Done: true, Finished: true, PromptTokens: 80, GeneratedTokens: 6, DurationMicros: 1500},
		} {
			if err := send(m); err != nil {
				return err
			}
		}
		return nil
	}}
	c := start(t, f)
	a, err := c.Documents.AskText(context.Background(), &mimirsdk.AskRequest{CollectionId: "c1", Messages: []*mimirsdk.ChatMessage{mimirsdk.UserMessage("How long do I have to return an item?")}})
	if err != nil {
		t.Fatal(err)
	}
	if a.Text != "Within 30 days [1]." || len(a.Sources) != 1 || a.Sources[0].GetDocumentName() != "returns.html" || !a.Finished || a.GeneratedTokens != 6 || a.Duration != 1500*time.Microsecond {
		t.Fatalf("answer %+v", a)
	}
}
