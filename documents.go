package mimirsdk

import (
	"context"
	"fmt"
	"iter"
	"os"
	"path/filepath"
	"strings"
	"time"

	mimirv1 "github.com/gsoultan/mimir-server/gen/mimir/v1"
	"github.com/gsoultan/mimir-server/gen/mimir/v1/mimirv1connect"
)

// DocumentService answers questions from a team's own files. A
// collection holds documents (PDF, Word, Markdown, web pages or text);
// the server reads each into passages in the background, and Ask answers
// from the passages that best match a question, citing them as [1], [2].
//
// Apps that speak the OpenAI API can ask a collection too, by sending its
// ApiName as the model to /v1/chat/completions.
type DocumentService struct {
	raw mimirv1connect.DocumentServiceClient
}

// ListCollections returns the collections the caller may see, by name.
func (s *DocumentService) ListCollections(ctx context.Context) ([]*Collection, error) {
	res, err := call(ctx, mimirv1connect.DocumentServiceListCollectionsProcedure, s.raw.ListCollections, nil)
	return res.GetCollections(), err
}

// GetCollection returns a collection with its documents, newest first.
func (s *DocumentService) GetCollection(ctx context.Context, id string) (*GetCollectionResponse, error) {
	return call(ctx, mimirv1connect.DocumentServiceGetCollectionProcedure, s.raw.GetCollection, &mimirv1.GetCollectionRequest{Id: id})
}

// CreateCollection makes a collection. EmbeddingModelId reads the
// documents and can't change later; LanguageModelId writes the answers
// and defaults to the same model.
func (s *DocumentService) CreateCollection(ctx context.Context, req *CreateCollectionRequest) (*Collection, error) {
	res, err := call(ctx, mimirv1connect.DocumentServiceCreateCollectionProcedure, s.raw.CreateCollection, req)
	return res.GetCollection(), err
}

// UpdateCollection changes a collection's name, language model and
// instructions.
func (s *DocumentService) UpdateCollection(ctx context.Context, req *UpdateCollectionRequest) (*Collection, error) {
	res, err := call(ctx, mimirv1connect.DocumentServiceUpdateCollectionProcedure, s.raw.UpdateCollection, req)
	return res.GetCollection(), err
}

// DeleteCollection removes a collection with its documents.
func (s *DocumentService) DeleteCollection(ctx context.Context, id string) error {
	_, err := call(ctx, mimirv1connect.DocumentServiceDeleteCollectionProcedure, s.raw.DeleteCollection, &mimirv1.DeleteCollectionRequest{Id: id})
	return err
}

// Add adds a file's contents to a collection; name's extension (.pdf,
// .docx, .md, .html, .txt) says how to read it. The server reads it in
// the background: WaitDocument follows it.
func (s *DocumentService) Add(ctx context.Context, collectionID, name string, data []byte) (*Document, error) {
	res, err := call(ctx, mimirv1connect.DocumentServiceAddDocumentProcedure, s.raw.AddDocument, &mimirv1.AddDocumentRequest{CollectionId: collectionID, Name: name, Data: data})
	return res.GetDocument(), err
}

// AddFile is Add for a file on disk.
func (s *DocumentService) AddFile(ctx context.Context, collectionID, path string) (*Document, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("mimirsdk: read %s: %w", path, err)
	}
	return s.Add(ctx, collectionID, filepath.Base(path), data)
}

// GetDocument returns one document.
func (s *DocumentService) GetDocument(ctx context.Context, id string) (*Document, error) {
	res, err := call(ctx, mimirv1connect.DocumentServiceGetDocumentProcedure, s.raw.GetDocument, &mimirv1.GetDocumentRequest{Id: id})
	return res.GetDocument(), err
}

// DeleteDocument removes a document and its passages. One being read
// can't be deleted until it's done.
func (s *DocumentService) DeleteDocument(ctx context.Context, id string) error {
	_, err := call(ctx, mimirv1connect.DocumentServiceDeleteDocumentProcedure, s.raw.DeleteDocument, &mimirv1.DeleteDocumentRequest{Id: id})
	return err
}

// WaitDocument follows a document until it is read or fails, looking
// every interval (0 means a second). One that fails returns a
// *DocumentError along with it. Bound the wait with ctx.
func (s *DocumentService) WaitDocument(ctx context.Context, id string, interval time.Duration) (*Document, error) {
	if interval <= 0 {
		interval = time.Second
	}
	t := time.NewTicker(interval)
	defer t.Stop()
	for {
		d, err := s.GetDocument(ctx, id)
		if err != nil {
			return nil, err
		}
		switch d.GetStatus() {
		case JobStatusSucceeded:
			return d, nil
		case JobStatusFailed, JobStatusCancelled:
			return d, &DocumentError{Document: d}
		}
		select {
		case <-ctx.Done():
			return d, ctx.Err()
		case <-t.C:
		}
	}
}

// Search returns up to limit passages that best match query, best first;
// 0 means 5.
func (s *DocumentService) Search(ctx context.Context, collectionID, query string, limit int) ([]*Passage, error) {
	res, err := call(ctx, mimirv1connect.DocumentServiceSearchProcedure, s.raw.Search, &mimirv1.SearchRequest{CollectionId: collectionID, Query: query, Limit: int32(limit)})
	return res.GetPassages(), err
}

// Ask answers the last question of a chat from a collection's documents,
// yielding the answer as it is written. The first message carries the
// sources the answer cites as [1], [2] and so on; the last has Done set.
//
//	for piece, err := range client.Documents.Ask(ctx, &mimirsdk.AskRequest{
//		CollectionId: id,
//		Messages:     []*mimirsdk.ChatMessage{mimirsdk.UserMessage("Can I return a used item?")},
//	}) {
//		if err != nil {
//			return err
//		}
//		fmt.Print(piece.GetText())
//	}
func (s *DocumentService) Ask(ctx context.Context, req *AskRequest) iter.Seq2[*AskResponse, error] {
	return stream(ctx, mimirv1connect.DocumentServiceAskProcedure, s.raw.Ask, req)
}

// Answer is a whole answer from a collection, as AskText collects it.
type Answer struct {
	Text    string
	Sources []*Passage
	// Finished is false when the answer stopped at the most tokens it
	// may write.
	Finished        bool
	PromptTokens    int
	GeneratedTokens int
	Duration        time.Duration
}

// AskText is Ask, waiting for the whole answer.
func (s *DocumentService) AskText(ctx context.Context, req *AskRequest) (*Answer, error) {
	var b strings.Builder
	a := &Answer{}
	for piece, err := range s.Ask(ctx, req) {
		if err != nil {
			return nil, err
		}
		if len(piece.GetSources()) > 0 {
			a.Sources = piece.GetSources()
		}
		b.WriteString(piece.GetText())
		if piece.GetDone() {
			a.Finished = piece.GetFinished()
			a.PromptTokens, a.GeneratedTokens = int(piece.GetPromptTokens()), int(piece.GetGeneratedTokens())
			a.Duration = time.Duration(piece.GetDurationMicros()) * time.Microsecond
		}
	}
	a.Text = b.String()
	return a, nil
}

// DocumentError is what WaitDocument returns for a document that
// couldn't be read.
type DocumentError struct {
	Document *Document
}

func (e *DocumentError) Error() string {
	if msg := e.Document.GetError(); msg != "" {
		return fmt.Sprintf("mimirsdk: document %s not read: %s", e.Document.GetName(), msg)
	}
	return fmt.Sprintf("mimirsdk: document %s not read", e.Document.GetName())
}
