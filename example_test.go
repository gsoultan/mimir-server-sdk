package mimirsdk_test

import (
	"context"
	"errors"
	"fmt"
	"log"
	"time"

	mimirsdk "github.com/gsoultan/mimir-server-sdk"
)

func ExampleNew() {
	client, err := mimirsdk.New("http://localhost:8080",
		mimirsdk.WithAPIKey("mimir_..."),
		mimirsdk.WithTimeout(30*time.Second),
		mimirsdk.WithUserAgent("my-app/1.0"),
	)
	if err != nil {
		log.Fatal(err)
	}
	models, err := client.Models.List(context.Background())
	if err != nil {
		log.Fatal(err)
	}
	for _, m := range models {
		fmt.Println(m.GetName(), m.GetArchitecture())
	}
}

func ExampleModelService_Chat() {
	client, _ := mimirsdk.NewFromEnv()
	req := &mimirsdk.ChatRequest{
		ModelId:  "llama",
		Messages: []*mimirsdk.ChatMessage{mimirsdk.UserMessage("Write a haiku about Go.")},
	}
	for piece, err := range client.Models.Chat(context.Background(), req) {
		if err != nil {
			log.Fatal(err)
		}
		fmt.Print(piece.GetText())
	}
}

func ExampleModelService_PredictFields() {
	client, _ := mimirsdk.NewFromEnv()
	answer, err := client.Models.PredictFields(context.Background(), "churn-model-id", map[string]string{
		"plan":   "monthly",
		"tenure": "3",
	})
	if err != nil {
		log.Fatal(err)
	}
	best := answer.GetGuesses()[0]
	fmt.Printf("%s (%.0f%% sure)\n", best.GetLabel(), best.GetProbability()*100)
}

func ExampleModelService_SendFeedback() {
	client, _ := mimirsdk.NewFromEnv()
	ctx := context.Background()
	answer, err := client.Models.PredictFields(ctx, "churn-model-id", map[string]string{"plan": "monthly"})
	if err != nil {
		log.Fatal(err)
	}
	// Later, once the customer has stayed or left:
	right, err := client.Models.SendFeedback(ctx, answer.GetPredictionId(), "stayed")
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println("the model was right:", right)
}

func ExampleTrainingService_Wait() {
	client, _ := mimirsdk.NewFromEnv()
	ctx, cancel := context.WithTimeout(context.Background(), time.Hour)
	defer cancel()
	job, err := client.Training.Start(ctx, &mimirsdk.CreateJobRequest{
		Name: "churn", Architecture: "table-mlp", DatasetId: "dataset-id",
	})
	if err != nil {
		log.Fatal(err)
	}
	job, err = client.Training.Wait(ctx, job.GetId(), mimirsdk.WaitOptions{
		OnProgress: func(j *mimirsdk.Job) { fmt.Println("epoch", j.GetEpoch()) },
	})
	var failed *mimirsdk.JobError
	if errors.As(err, &failed) {
		log.Fatalf("training stopped: %s", failed.Job.GetError())
	}
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println("model", job.GetModelId())
}

func ExampleAuditService_All() {
	client, _ := mimirsdk.NewFromEnv()
	for ev, err := range client.Audit.All(context.Background(), mimirsdk.ListOptions{PageSize: 100}) {
		if err != nil {
			log.Fatal(err)
		}
		fmt.Println(ev.GetTime().AsTime(), ev.GetActor(), ev.GetAction(), ev.GetTarget())
	}
}

func ExampleError() {
	client, _ := mimirsdk.NewFromEnv()
	_, err := client.Models.Get(context.Background(), "missing")
	var apiErr *mimirsdk.Error
	switch {
	case errors.Is(err, mimirsdk.ErrNotFound):
		fmt.Println("no such model")
	case errors.Is(err, mimirsdk.ErrResourceExhausted) && errors.As(err, &apiErr):
		fmt.Println("slow down; try again in", apiErr.RetryAfter)
	case err != nil:
		log.Fatal(err)
	}
}
