package mimirsdk_test

import (
	"context"
	"errors"
	"testing"

	"connectrpc.com/connect"
	mimirv1 "github.com/gsoultan/mimir-server/gen/mimir/v1"

	mimirsdk "github.com/gsoultan/mimir-server-sdk"
)

func (f *fake) Explain(_ context.Context, req *connect.Request[mimirv1.ExplainRequest]) (*connect.Response[mimirv1.ExplainResponse], error) {
	f.record(req.Header())
	res, err := f.explain(req.Msg)
	if err != nil {
		return nil, err
	}
	return connect.NewResponse(res), nil
}

func (f *fake) ExplainModel(_ context.Context, req *connect.Request[mimirv1.ExplainModelRequest]) (*connect.Response[mimirv1.ExplainModelResponse], error) {
	f.record(req.Header())
	res, err := f.overview(req.Msg)
	if err != nil {
		return nil, err
	}
	return connect.NewResponse(res), nil
}

func TestExplain(t *testing.T) {
	f := &fake{
		explain: func(req *mimirv1.ExplainRequest) (*mimirv1.ExplainResponse, error) {
			if req.GetModelId() != "m1" || req.GetFields()["plan"] != "monthly" {
				t.Errorf("request = %v", req)
			}
			if req.GetLabel() == "maybe" {
				return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("the model never answers maybe"))
			}
			return &mimirv1.ExplainResponse{Label: "left", Value: 0.8, Typical: 0.3, Exact: true, Contributions: []*mimirv1.Contribution{
				{Column: "plan", Value: "monthly", Typical: "yearly", Effect: 0.4},
				{Column: "logins_30d", Value: "1", Typical: "12", Effect: 0.1},
			}}, nil
		},
		overview: func(req *mimirv1.ExplainModelRequest) (*mimirv1.ExplainModelResponse, error) {
			return &mimirv1.ExplainModelResponse{Rows: 24, Source: "answers", Columns: []*mimirv1.ColumnImportance{
				{Column: "plan", Importance: 0.3, Share: 0.75},
				{Column: "logins_30d", Importance: 0.1, Share: 0.25},
			}}, nil
		},
	}
	c := start(t, f)

	why, err := c.Models.Explain(t.Context(), "m1", map[string]string{"plan": "monthly", "logins_30d": "1"}, "")
	if err != nil {
		t.Fatal(err)
	}
	var sum float64
	for _, e := range why.GetContributions() {
		sum += e.GetEffect()
	}
	if why.GetLabel() != "left" || !why.GetExact() || sum < 0.499 || sum > 0.501 {
		t.Fatalf("explanation = %v", why)
	}
	if _, err := c.Models.Explain(t.Context(), "m1", map[string]string{"plan": "monthly"}, "maybe"); !errors.Is(err, mimirsdk.ErrInvalidArgument) {
		t.Errorf("bad label err = %v", err)
	}

	cols, err := c.Models.ExplainModel(t.Context(), "m1")
	if err != nil {
		t.Fatal(err)
	}
	if cols.GetRows() != 24 || cols.GetColumns()[0].GetColumn() != "plan" {
		t.Errorf("columns = %v", cols)
	}
}
