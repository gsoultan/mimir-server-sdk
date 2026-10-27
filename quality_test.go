package mimirsdk_test

import (
	"context"
	"errors"
	"testing"

	"connectrpc.com/connect"
	mimirv1 "github.com/gsoultan/mimir-server/gen/mimir/v1"

	mimirsdk "github.com/gsoultan/mimir-server-sdk"
)

func (f *fake) ListModelVersions(_ context.Context, req *connect.Request[mimirv1.ListModelVersionsRequest]) (*connect.Response[mimirv1.ListModelVersionsResponse], error) {
	f.record(req.Header())
	res, err := f.versions(req.Msg)
	if err != nil {
		return nil, err
	}
	return connect.NewResponse(res), nil
}

func (f *fake) UseModelVersion(_ context.Context, req *connect.Request[mimirv1.UseModelVersionRequest]) (*connect.Response[mimirv1.UseModelVersionResponse], error) {
	f.record(req.Header())
	res, err := f.useVersion(req.Msg)
	if err != nil {
		return nil, err
	}
	return connect.NewResponse(res), nil
}

func (f *fake) GetModelQuality(_ context.Context, req *connect.Request[mimirv1.GetModelQualityRequest]) (*connect.Response[mimirv1.GetModelQualityResponse], error) {
	f.record(req.Header())
	res, err := f.quality(req.Msg)
	if err != nil {
		return nil, err
	}
	return connect.NewResponse(res), nil
}

func (f *fake) SendFeedback(_ context.Context, req *connect.Request[mimirv1.SendFeedbackRequest]) (*connect.Response[mimirv1.SendFeedbackResponse], error) {
	f.record(req.Header())
	res, err := f.feedback(req.Msg)
	if err != nil {
		return nil, err
	}
	return connect.NewResponse(res), nil
}

func TestVersionsAndRollback(t *testing.T) {
	f := &fake{
		versions: func(req *mimirv1.ListModelVersionsRequest) (*mimirv1.ListModelVersionsResponse, error) {
			if req.GetModelId() != "m1" {
				t.Errorf("model id = %q", req.GetModelId())
			}
			return &mimirv1.ListModelVersionsResponse{Versions: []*mimirv1.ModelVersion{
				{Id: "v2", Number: 2, Source: mimirsdk.ModelVersionSourceKeepLearning, Live: true},
				{Id: "v1", Number: 1, Source: mimirsdk.ModelVersionSourceUploaded},
			}}, nil
		},
		useVersion: func(req *mimirv1.UseModelVersionRequest) (*mimirv1.UseModelVersionResponse, error) {
			return &mimirv1.UseModelVersionResponse{Model: &mimirv1.Model{Id: req.GetModelId(), VersionId: req.GetVersionId()}}, nil
		},
	}
	c := start(t, f)

	vs, err := c.Models.Versions(t.Context(), "m1")
	if err != nil {
		t.Fatal(err)
	}
	if len(vs) != 2 || !vs[0].GetLive() || vs[1].GetSource() != mimirsdk.ModelVersionSourceUploaded {
		t.Fatalf("versions = %v", vs)
	}
	m, err := c.Models.UseVersion(t.Context(), "m1", "v1")
	if err != nil {
		t.Fatal(err)
	}
	if m.GetVersionId() != "v1" {
		t.Errorf("live version = %q", m.GetVersionId())
	}
}

func TestFeedback(t *testing.T) {
	var got []*mimirv1.SendFeedbackRequest
	f := &fake{feedback: func(req *mimirv1.SendFeedbackRequest) (*mimirv1.SendFeedbackResponse, error) {
		got = append(got, req)
		if req.GetPredictionId() == "gone" {
			return nil, connect.NewError(connect.CodeNotFound, errors.New("no prediction"))
		}
		return &mimirv1.SendFeedbackResponse{Correct: req.GetLabel() == "stays" || req.GetValue() == 12.5}, nil
	}}
	c := start(t, f)

	right, err := c.Models.SendFeedback(t.Context(), "p1", "stays")
	if err != nil || !right {
		t.Errorf("SendFeedback = %v, %v", right, err)
	}
	right, err = c.Models.SendFeedbackValue(t.Context(), "p2", 12.5)
	if err != nil || !right {
		t.Errorf("SendFeedbackValue = %v, %v", right, err)
	}
	if len(got) != 2 || got[1].GetLabel() != "" || got[1].GetValue() != 12.5 {
		t.Errorf("requests = %v", got)
	}
	if _, err := c.Models.SendFeedback(t.Context(), "gone", "stays"); !errors.Is(err, mimirsdk.ErrNotFound) {
		t.Errorf("err = %v, want ErrNotFound", err)
	}
}

func TestQuality(t *testing.T) {
	f := &fake{quality: func(req *mimirv1.GetModelQualityRequest) (*mimirv1.GetModelQualityResponse, error) {
		if req.GetModelId() != "m1" || req.GetDays() != 7 {
			t.Errorf("request = %v", req)
		}
		return &mimirv1.GetModelQualityResponse{
			Days:         []*mimirv1.QualityDay{{Answers: 40, Feedback: 25, Correct: 15}},
			WeekAnswers:  40,
			WeekFeedback: 25,
			WeekAccuracy: 0.6,
			Dropped:      true,
		}, nil
	}}
	c := start(t, f)

	q, err := c.Models.Quality(t.Context(), "m1", 7)
	if err != nil {
		t.Fatal(err)
	}
	if !q.GetDropped() || q.GetWeekAccuracy() != 0.6 || len(q.GetDays()) != 1 {
		t.Errorf("quality = %v", q)
	}
}
