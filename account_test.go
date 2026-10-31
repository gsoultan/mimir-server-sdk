package mimirsdk_test

import (
	"context"
	"errors"
	"net/http"
	"strings"
	"sync"
	"testing"

	"connectrpc.com/connect"
	mimirv1 "github.com/gsoultan/mimir-server/gen/mimir/v1"
	"google.golang.org/protobuf/proto"

	mimirsdk "github.com/gsoultan/mimir-server-sdk"
)

// fakeAuth keeps the account and sign-in state the fake server's
// AuthService, SignInService and SettingsService share.
type fakeAuth struct {
	mu        sync.Mutex
	pending   string // the secret StartTwoFactor made, until enabled
	twoFactor bool
	sessions  []*mimirv1.Session
	providers []*mimirv1.SignInProvider
	security  *mimirv1.Security
}

const fakePassword = "correct horse"

func (f *fake) ChangePassword(_ context.Context, req *connect.Request[mimirv1.ChangePasswordRequest]) (*connect.Response[mimirv1.ChangePasswordResponse], error) {
	if req.Msg.GetCurrentPassword() != fakePassword {
		return nil, connect.NewError(connect.CodePermissionDenied, errors.New("That isn't your current password."))
	}
	return connect.NewResponse(&mimirv1.ChangePasswordResponse{}), nil
}

func (f *fake) StartTwoFactor(_ context.Context, req *connect.Request[mimirv1.StartTwoFactorRequest]) (*connect.Response[mimirv1.StartTwoFactorResponse], error) {
	a := f.auth
	a.mu.Lock()
	defer a.mu.Unlock()
	if req.Msg.GetPassword() != fakePassword || (a.twoFactor && req.Msg.GetCode() != "123456") {
		return nil, connect.NewError(connect.CodePermissionDenied, errors.New("Check your password and code."))
	}
	a.pending = "JBSWY3DPEHPK3PXP"
	return connect.NewResponse(&mimirv1.StartTwoFactorResponse{Secret: a.pending, OtpauthUrl: "otpauth://totp/mimir?secret=" + a.pending}), nil
}

func (f *fake) EnableTwoFactor(_ context.Context, req *connect.Request[mimirv1.EnableTwoFactorRequest]) (*connect.Response[mimirv1.EnableTwoFactorResponse], error) {
	a := f.auth
	a.mu.Lock()
	defer a.mu.Unlock()
	if a.pending == "" || req.Msg.GetCode() != "123456" {
		return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("That code doesn't match."))
	}
	a.twoFactor, a.pending = true, ""
	return connect.NewResponse(&mimirv1.EnableTwoFactorResponse{RecoveryCodes: []string{"aaaa-bbbb", "cccc-dddd"}}), nil
}

func (f *fake) DisableTwoFactor(_ context.Context, req *connect.Request[mimirv1.DisableTwoFactorRequest]) (*connect.Response[mimirv1.DisableTwoFactorResponse], error) {
	a := f.auth
	a.mu.Lock()
	defer a.mu.Unlock()
	if req.Msg.GetPassword() != fakePassword || req.Msg.GetCode() != "aaaa-bbbb" {
		return nil, connect.NewError(connect.CodePermissionDenied, errors.New("Check your password and code."))
	}
	a.twoFactor = false
	return connect.NewResponse(&mimirv1.DisableTwoFactorResponse{}), nil
}

func (f *fake) ListSessions(context.Context, *connect.Request[mimirv1.ListSessionsRequest]) (*connect.Response[mimirv1.ListSessionsResponse], error) {
	a := f.auth
	a.mu.Lock()
	defer a.mu.Unlock()
	return connect.NewResponse(&mimirv1.ListSessionsResponse{Sessions: a.sessions}), nil
}

func (f *fake) RevokeSessions(_ context.Context, req *connect.Request[mimirv1.RevokeSessionsRequest]) (*connect.Response[mimirv1.RevokeSessionsResponse], error) {
	a := f.auth
	a.mu.Lock()
	defer a.mu.Unlock()
	var kept []*mimirv1.Session
	for _, s := range a.sessions {
		if s.GetCurrent() || (req.Msg.GetId() != "" && s.GetId() != req.Msg.GetId()) {
			kept = append(kept, s)
		}
	}
	n := int32(len(a.sessions) - len(kept))
	a.sessions = kept
	return connect.NewResponse(&mimirv1.RevokeSessionsResponse{Revoked: n}), nil
}

func (f *fake) ListSignInOptions(context.Context, *connect.Request[mimirv1.ListSignInOptionsRequest]) (*connect.Response[mimirv1.ListSignInOptionsResponse], error) {
	a := f.auth
	a.mu.Lock()
	defer a.mu.Unlock()
	var opts []*mimirv1.SignInOption
	for _, p := range a.providers {
		if p.GetEnabled() {
			opts = append(opts, &mimirv1.SignInOption{Id: p.GetId(), Name: p.GetName(), Kind: p.GetKind()})
		}
	}
	return connect.NewResponse(&mimirv1.ListSignInOptionsResponse{Options: opts}), nil
}

func (f *fake) ListSignInProviders(context.Context, *connect.Request[mimirv1.ListSignInProvidersRequest]) (*connect.Response[mimirv1.ListSignInProvidersResponse], error) {
	a := f.auth
	a.mu.Lock()
	defer a.mu.Unlock()
	return connect.NewResponse(&mimirv1.ListSignInProvidersResponse{Providers: a.providers}), nil
}

func (f *fake) SaveSignInProvider(_ context.Context, req *connect.Request[mimirv1.SaveSignInProviderRequest]) (*connect.Response[mimirv1.SaveSignInProviderResponse], error) {
	a := f.auth
	a.mu.Lock()
	defer a.mu.Unlock()
	p := proto.Clone(req.Msg.GetProvider()).(*mimirv1.SignInProvider)
	p.ClientSecretSet, p.ClientSecret = p.GetClientSecret() != "", ""
	a.providers = append(a.providers, p)
	return connect.NewResponse(&mimirv1.SaveSignInProviderResponse{Provider: p}), nil
}

func (f *fake) DeleteSignInProvider(_ context.Context, req *connect.Request[mimirv1.DeleteSignInProviderRequest]) (*connect.Response[mimirv1.DeleteSignInProviderResponse], error) {
	a := f.auth
	a.mu.Lock()
	defer a.mu.Unlock()
	for i, p := range a.providers {
		if p.GetId() == req.Msg.GetId() {
			a.providers = append(a.providers[:i], a.providers[i+1:]...)
			return connect.NewResponse(&mimirv1.DeleteSignInProviderResponse{}), nil
		}
	}
	return nil, connect.NewError(connect.CodeNotFound, errors.New("There's no such sign-in provider."))
}

func (f *fake) UpdateSecurity(_ context.Context, req *connect.Request[mimirv1.UpdateSecurityRequest]) (*connect.Response[mimirv1.UpdateSecurityResponse], error) {
	a := f.auth
	a.mu.Lock()
	defer a.mu.Unlock()
	a.security = req.Msg.GetSecurity()
	return connect.NewResponse(&mimirv1.UpdateSecurityResponse{Security: a.security}), nil
}

func TestTwoFactorAndSessions(t *testing.T) {
	f := &fake{auth: &fakeAuth{sessions: []*mimirv1.Session{
		{Id: "s1", Device: "Chrome on Mac", Current: true},
		{Id: "s2", Device: "Safari on iPhone"},
		{Id: "s3", Device: "Firefox on Linux"},
	}}}
	c := start(t, f)
	ctx := t.Context()

	if err := c.Auth.ChangePassword(ctx, "wrong", "new one"); !errors.Is(err, mimirsdk.ErrPermissionDenied) {
		t.Errorf("wrong password err = %v", err)
	}
	if err := c.Auth.ChangePassword(ctx, fakePassword, "new one"); err != nil {
		t.Fatal(err)
	}

	secret, err := c.Auth.StartTwoFactor(ctx, fakePassword, "")
	if err != nil || secret.GetSecret() == "" || !strings.HasPrefix(secret.GetOtpauthUrl(), "otpauth://") {
		t.Fatalf("start = %v, %v", secret, err)
	}
	codes, err := c.Auth.EnableTwoFactor(ctx, "123456")
	if err != nil || len(codes) != 2 {
		t.Fatalf("enable = %v, %v", codes, err)
	}
	// With it on, starting again needs a code.
	if _, err := c.Auth.StartTwoFactor(ctx, fakePassword, ""); !errors.Is(err, mimirsdk.ErrPermissionDenied) {
		t.Errorf("restart without a code err = %v", err)
	}
	if err := c.Auth.DisableTwoFactor(ctx, fakePassword, codes[0]); err != nil {
		t.Fatal(err)
	}

	if err := c.Auth.RevokeSession(ctx, ""); err == nil {
		t.Error("RevokeSession with no id signed out every other session")
	}
	if err := c.Auth.RevokeSession(ctx, "s2"); err != nil {
		t.Fatal(err)
	}
	sessions, err := c.Auth.Sessions(ctx)
	if err != nil || len(sessions) != 2 {
		t.Fatalf("sessions = %v, %v", sessions, err)
	}
	n, err := c.Auth.RevokeOtherSessions(ctx)
	if err != nil || n != 1 {
		t.Fatalf("revoked %d, %v", n, err)
	}
	if sessions, _ := c.Auth.Sessions(ctx); len(sessions) != 1 || !sessions[0].GetCurrent() {
		t.Errorf("left signed in: %v", sessions)
	}
}

func TestSignInProviders(t *testing.T) {
	f := &fake{auth: &fakeAuth{}}
	c := start(t, f)
	ctx := t.Context()

	saved, err := c.SignIn.SaveProvider(ctx, &mimirsdk.SignInProvider{
		Id: "google", Kind: mimirsdk.SignInKindGoogle, Name: "Google", Enabled: true,
		ClientId: "id.apps.googleusercontent.com", ClientSecret: "shh",
		Rules: []*mimirsdk.SignInRule{{Domain: "example.com", TeamId: "t1", Role: mimirsdk.RoleViewer}},
	})
	if err != nil || !saved.GetClientSecretSet() || saved.GetClientSecret() != "" {
		t.Fatalf("saved = %v, %v", saved, err)
	}
	opts, err := c.SignIn.Options(ctx)
	if err != nil || len(opts) != 1 || opts[0].GetKind() != mimirsdk.SignInKindGoogle {
		t.Fatalf("options = %v, %v", opts, err)
	}
	if ps, err := c.SignIn.Providers(ctx); err != nil || len(ps) != 1 || ps[0].GetRules()[0].GetDomain() != "example.com" {
		t.Fatalf("providers = %v, %v", ps, err)
	}
	if err := c.SignIn.DeleteProvider(ctx, "google"); err != nil {
		t.Fatal(err)
	}
	if err := c.SignIn.DeleteProvider(ctx, "google"); !errors.Is(err, mimirsdk.ErrNotFound) {
		t.Errorf("second delete err = %v", err)
	}
}

func TestSecurityAndBackup(t *testing.T) {
	f := &fake{
		auth: &fakeAuth{},
		backup: http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			if r.Header.Get("Authorization") != "Bearer "+testKey {
				http.Error(w, "Sign in as an admin to download a backup.", http.StatusForbidden)
				return
			}
			w.Write([]byte("PGDMP"))
		}),
	}
	c := start(t, f)
	ctx := t.Context()

	sec, err := c.Settings.UpdateSecurity(ctx, &mimirsdk.Security{TwoFactor: mimirsdk.TwoFactorEveryone})
	if err != nil || sec.GetTwoFactor() != mimirsdk.TwoFactorEveryone {
		t.Fatalf("security = %v, %v", sec, err)
	}

	var b strings.Builder
	n, err := c.Settings.Backup(ctx, &b)
	if err != nil || n != 5 || b.String() != "PGDMP" {
		t.Fatalf("backup %q, %d, %v", b.String(), n, err)
	}

	// Without the key the server's plain-text refusal comes back as an *Error.
	other, err := mimirsdk.New(c.BaseURL())
	if err != nil {
		t.Fatal(err)
	}
	_, err = other.Settings.Backup(ctx, &b)
	var e *mimirsdk.Error
	if !errors.As(err, &e) || !errors.Is(err, mimirsdk.ErrPermissionDenied) || !strings.Contains(e.Message, "admin") || e.Procedure != "/api/backup" {
		t.Fatalf("backup error %v", err)
	}
}
