package mimirsdk

import (
	"context"
	"fmt"
	"io"
	"iter"
	"os"
	"path/filepath"
	"strings"

	mimirv1 "github.com/gsoultan/mimir-server/gen/mimir/v1"
	"github.com/gsoultan/mimir-server/gen/mimir/v1/mimirv1connect"
)

// ModelService manages models and asks them questions.
type ModelService struct {
	raw     mimirv1connect.ModelServiceClient
	predict mimirv1connect.PredictServiceClient
	uploads *uploader
}

// List returns every model the caller may see, newest first.
func (s *ModelService) List(ctx context.Context) ([]*Model, error) {
	res, err := call(ctx, mimirv1connect.ModelServiceListModelsProcedure, s.raw.ListModels, nil)
	return res.GetModels(), err
}

// Get returns one model.
func (s *ModelService) Get(ctx context.Context, id string) (*Model, error) {
	res, err := call(ctx, mimirv1connect.ModelServiceGetModelProcedure, s.raw.GetModel, &mimirv1.GetModelRequest{Id: id})
	return res.GetModel(), err
}

// Architectures returns the model types the server can build and run.
func (s *ModelService) Architectures(ctx context.Context) ([]*Architecture, error) {
	res, err := call(ctx, mimirv1connect.ModelServiceListArchitecturesProcedure, s.raw.ListArchitectures, nil)
	return res.GetArchitectures(), err
}

// Create stores a model from its weights held in memory (Weights), or
// from a file sent beforehand (Upload). For a file on disk, UploadFile is
// simpler.
func (s *ModelService) Create(ctx context.Context, req *CreateModelRequest) (*Model, error) {
	res, err := call(ctx, mimirv1connect.ModelServiceCreateModelProcedure, s.raw.CreateModel, req)
	return res.GetModel(), err
}

// Upload stores a model whose weights it reads from r: a Mimir Model
// (.mim) file, or an ONNX or GGUF file for the "mim" and language-model
// architectures, which the server converts. The file is streamed to the
// server as it is read, so it can be larger than memory; the server's
// -max-model-mb caps it. The streaming is bounded by ctx, not by
// WithTimeout, so a large file isn't cut short.
func (s *ModelService) Upload(ctx context.Context, name, architecture string, r io.Reader) (*Model, error) {
	id, err := s.uploads.send(ctx, r, sizeOf(r))
	if err != nil {
		return nil, err
	}
	return s.Create(ctx, &mimirv1.CreateModelRequest{Name: name, Architecture: architecture, Upload: id})
}

// sizeOf is r's length when it can tell without reading it, else -1.
func sizeOf(r io.Reader) int64 {
	switch v := r.(type) {
	case interface{ Len() int }:
		return int64(v.Len())
	case *os.File:
		if fi, err := v.Stat(); err == nil && fi.Mode().IsRegular() {
			if off, err := v.Seek(0, io.SeekCurrent); err == nil {
				return fi.Size() - off
			}
		}
	}
	return -1
}

// UploadFile is Upload from a file. An empty name uses the file's name
// without its extension.
func (s *ModelService) UploadFile(ctx context.Context, path, name, architecture string) (*Model, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, fmt.Errorf("mimirsdk: %w", err)
	}
	defer f.Close()
	if name == "" {
		base := filepath.Base(path)
		name = strings.TrimSuffix(base, filepath.Ext(base))
	}
	return s.Upload(ctx, name, architecture, f)
}

// Update renames a model, changes its description or language settings, or
// lets it run on people's devices.
func (s *ModelService) Update(ctx context.Context, req *UpdateModelRequest) (*Model, error) {
	res, err := call(ctx, mimirv1connect.ModelServiceUpdateModelProcedure, s.raw.UpdateModel, req)
	return res.GetModel(), err
}

// Delete removes a model and its weights.
func (s *ModelService) Delete(ctx context.Context, id string) error {
	_, err := call(ctx, mimirv1connect.ModelServiceDeleteModelProcedure, s.raw.DeleteModel, &mimirv1.DeleteModelRequest{Id: id})
	return err
}

// SetWorker picks the worker that answers a model, or "" for automatic.
func (s *ModelService) SetWorker(ctx context.Context, id, workerID string) (*Model, error) {
	res, err := call(ctx, mimirv1connect.ModelServiceSetModelWorkerProcedure, s.raw.SetModelWorker, &mimirv1.SetModelWorkerRequest{Id: id, WorkerId: workerID})
	return res.GetModel(), err
}

// Download returns a model that may run on people's devices, with its
// stored weights.
func (s *ModelService) Download(ctx context.Context, id string) (*GetDeviceModelResponse, error) {
	return call(ctx, mimirv1connect.ModelServiceGetDeviceModelProcedure, s.raw.GetDeviceModel, &mimirv1.GetDeviceModelRequest{Id: id})
}

// Predict runs one example through a model: a tensor, a table row (Fields)
// or a photo, depending on what the model reads.
func (s *ModelService) Predict(ctx context.Context, req *PredictRequest) (*PredictResponse, error) {
	return call(ctx, mimirv1connect.PredictServicePredictProcedure, s.predict.Predict, req)
}

// PredictFields asks a model taught from a table about one row, given by
// column name.
func (s *ModelService) PredictFields(ctx context.Context, modelID string, fields map[string]string) (*PredictResponse, error) {
	return s.Predict(ctx, &mimirv1.PredictRequest{ModelId: modelID, Fields: fields})
}

// PredictPhoto asks a model that looks at photos about one JPG, PNG or GIF.
func (s *ModelService) PredictPhoto(ctx context.Context, modelID string, photo []byte) (*PredictResponse, error) {
	return s.Predict(ctx, &mimirv1.PredictRequest{ModelId: modelID, Photo: photo})
}

// Generate continues a prompt with a language model and returns the whole
// text at once.
func (s *ModelService) Generate(ctx context.Context, req *GenerateRequest) (*GenerateResponse, error) {
	return call(ctx, mimirv1connect.PredictServiceGenerateProcedure, s.predict.Generate, req)
}

// GenerateStream is Generate, yielding the text as the model writes it.
// The last piece has Done set and the token counts.
func (s *ModelService) GenerateStream(ctx context.Context, req *GenerateStreamRequest) iter.Seq2[*GenerateStreamResponse, error] {
	return stream(ctx, mimirv1connect.PredictServiceGenerateStreamProcedure, s.predict.GenerateStream, req)
}

// Chat writes a language model's next turn in a chat, yielding the text as
// the model writes it. The last piece has Done set and the token counts.
//
//	for piece, err := range client.Models.Chat(ctx, &mimirsdk.ChatRequest{
//		ModelId:  id,
//		Messages: []*mimirsdk.ChatMessage{mimirsdk.UserMessage("Hello!")},
//	}) {
//		if err != nil {
//			return err
//		}
//		fmt.Print(piece.GetText())
//	}
//
// Breaking out of the loop stops the model.
func (s *ModelService) Chat(ctx context.Context, req *ChatRequest) iter.Seq2[*ChatResponse, error] {
	return stream(ctx, mimirv1connect.PredictServiceChatProcedure, s.predict.Chat, req)
}

// ChatReply is a whole chat turn, as ChatText collects it.
type ChatReply struct {
	Text            string
	PromptTokens    int32
	GeneratedTokens int32
	// Finished says the model ended the text itself, rather than running
	// into the token limit.
	Finished       bool
	DurationMicros int64
}

// ChatText is Chat, waiting for the whole answer.
func (s *ModelService) ChatText(ctx context.Context, req *ChatRequest) (*ChatReply, error) {
	var b strings.Builder
	reply := &ChatReply{}
	for piece, err := range s.Chat(ctx, req) {
		if err != nil {
			return nil, err
		}
		b.WriteString(piece.GetText())
		if piece.GetDone() {
			reply.PromptTokens = piece.GetPromptTokens()
			reply.GeneratedTokens = piece.GetGeneratedTokens()
			reply.Finished = piece.GetFinished()
			reply.DurationMicros = piece.GetDurationMicros()
		}
	}
	reply.Text = b.String()
	return reply, nil
}

// UserMessage is a chat turn written by a person.
func UserMessage(content string) *ChatMessage {
	return &mimirv1.ChatMessage{Role: "user", Content: content}
}

// AssistantMessage is a chat turn the model wrote earlier.
func AssistantMessage(content string) *ChatMessage {
	return &mimirv1.ChatMessage{Role: "assistant", Content: content}
}
