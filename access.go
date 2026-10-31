package mimirsdk

import (
	"context"
	"errors"
	"iter"

	mimirv1 "github.com/gsoultan/mimir-server/gen/mimir/v1"
	"github.com/gsoultan/mimir-server/gen/mimir/v1/mimirv1connect"
)

// AuthService says who the caller is, signs people in with a password and
// looks after their password, two-step verification and sessions. Apps
// should use an API key (WithAPIKey) rather than signing in; signing in
// needs a client with a cookie jar (WithHTTPClient).
type AuthService struct {
	raw mimirv1connect.AuthServiceClient
}

// WhoAmI returns the caller and the permissions they have.
func (s *AuthService) WhoAmI(ctx context.Context) (*WhoAmIResponse, error) {
	return call(ctx, mimirv1connect.AuthServiceWhoAmIProcedure, s.raw.WhoAmI, nil)
}

// SetupState says whether the server still needs first-run setup. Anyone
// may call it, so it doubles as a check that the server is reachable.
func (s *AuthService) SetupState(ctx context.Context) (*GetSetupStateResponse, error) {
	return call(ctx, mimirv1connect.AuthServiceGetSetupStateProcedure, s.raw.GetSetupState, nil)
}

// SignIn signs in with an email and password. When the response says
// SecondFactorRequired, finish with VerifySecondFactor.
func (s *AuthService) SignIn(ctx context.Context, email, password string) (*SignInResponse, error) {
	return call(ctx, mimirv1connect.AuthServiceSignInProcedure, s.raw.SignIn, &mimirv1.SignInRequest{Email: email, Password: password})
}

// VerifySecondFactor finishes a sign-in with a code from an authenticator
// app, or a recovery code.
func (s *AuthService) VerifySecondFactor(ctx context.Context, code string) (*VerifySecondFactorResponse, error) {
	return call(ctx, mimirv1connect.AuthServiceVerifySecondFactorProcedure, s.raw.VerifySecondFactor, &mimirv1.VerifySecondFactorRequest{Code: code})
}

// SignOut ends the signed-in session.
func (s *AuthService) SignOut(ctx context.Context) error {
	_, err := call(ctx, mimirv1connect.AuthServiceSignOutProcedure, s.raw.SignOut, nil)
	return err
}

// APIKeyService manages the caller's own API keys.
type APIKeyService struct {
	raw mimirv1connect.ApiKeyServiceClient
}

// List returns the caller's keys. Secrets are never returned after Create.
func (s *APIKeyService) List(ctx context.Context) ([]*APIKey, error) {
	res, err := call(ctx, mimirv1connect.ApiKeyServiceListApiKeysProcedure, s.raw.ListApiKeys, nil)
	return res.GetApiKeys(), err
}

// Create makes a key with the given access, such as
// AllModels(RoleEditor); a key never gets more than its owner has. Its
// Secret is in the response only this once: store it somewhere safe.
func (s *APIKeyService) Create(ctx context.Context, name string, access *Access) (*CreateAPIKeyResponse, error) {
	return call(ctx, mimirv1connect.ApiKeyServiceCreateApiKeyProcedure, s.raw.CreateApiKey, &mimirv1.CreateApiKeyRequest{Name: name, Access: access})
}

// Revoke stops a key working at once.
func (s *APIKeyService) Revoke(ctx context.Context, id string) error {
	_, err := call(ctx, mimirv1connect.ApiKeyServiceRevokeApiKeyProcedure, s.raw.RevokeApiKey, &mimirv1.RevokeApiKeyRequest{Id: id})
	return err
}

// AllModels is access with role on every model, including future ones.
func AllModels(role Role) *Access {
	return &mimirv1.Access{Role: role, AllModels: true}
}

// SomeModels is access with role on the listed models only.
func SomeModels(role Role, modelIDs ...string) *Access {
	return &mimirv1.Access{Role: role, ModelIds: modelIDs}
}

// UserService manages people. It needs an admin.
type UserService struct {
	raw mimirv1connect.UserServiceClient
}

// List returns everyone the caller may manage.
func (s *UserService) List(ctx context.Context) ([]*User, error) {
	res, err := call(ctx, mimirv1connect.UserServiceListUsersProcedure, s.raw.ListUsers, nil)
	return res.GetUsers(), err
}

// Create adds a person.
func (s *UserService) Create(ctx context.Context, req *CreateUserRequest) (*User, error) {
	res, err := call(ctx, mimirv1connect.UserServiceCreateUserProcedure, s.raw.CreateUser, req)
	return res.GetUser(), err
}

// Update changes a person's name, access, team or password, or disables
// them.
func (s *UserService) Update(ctx context.Context, req *UpdateUserRequest) (*User, error) {
	res, err := call(ctx, mimirv1connect.UserServiceUpdateUserProcedure, s.raw.UpdateUser, req)
	return res.GetUser(), err
}

// Delete removes a person.
func (s *UserService) Delete(ctx context.Context, id string) error {
	_, err := call(ctx, mimirv1connect.UserServiceDeleteUserProcedure, s.raw.DeleteUser, &mimirv1.DeleteUserRequest{Id: id})
	return err
}

// TeamService manages teams. It needs an owner.
type TeamService struct {
	raw mimirv1connect.TeamServiceClient
}

// List returns every team.
func (s *TeamService) List(ctx context.Context) ([]*Team, error) {
	res, err := call(ctx, mimirv1connect.TeamServiceListTeamsProcedure, s.raw.ListTeams, nil)
	return res.GetTeams(), err
}

// Create adds a team.
func (s *TeamService) Create(ctx context.Context, name string) (*Team, error) {
	res, err := call(ctx, mimirv1connect.TeamServiceCreateTeamProcedure, s.raw.CreateTeam, &mimirv1.CreateTeamRequest{Name: name})
	return res.GetTeam(), err
}

// Rename changes a team's name.
func (s *TeamService) Rename(ctx context.Context, id, name string) (*Team, error) {
	res, err := call(ctx, mimirv1connect.TeamServiceUpdateTeamProcedure, s.raw.UpdateTeam, &mimirv1.UpdateTeamRequest{Id: id, Name: name})
	return res.GetTeam(), err
}

// Delete removes an empty team.
func (s *TeamService) Delete(ctx context.Context, id string) error {
	_, err := call(ctx, mimirv1connect.TeamServiceDeleteTeamProcedure, s.raw.DeleteTeam, &mimirv1.DeleteTeamRequest{Id: id})
	return err
}

// AuditService reads the record of who changed what. It needs an admin.
type AuditService struct {
	raw mimirv1connect.AuditServiceClient
}

// ListOptions page through a long list.
type ListOptions struct {
	// PageSize is how many to fetch per request; 0 lets the server choose.
	PageSize int32
	// PageToken starts from a page an earlier call returned.
	PageToken string
}

// ListPage returns one page of audit events, newest first.
func (s *AuditService) ListPage(ctx context.Context, opts ListOptions) (*Page[*AuditEvent], error) {
	res, err := call(ctx, mimirv1connect.AuditServiceListAuditEventsProcedure, s.raw.ListAuditEvents,
		&mimirv1.ListAuditEventsRequest{PageSize: opts.PageSize, PageToken: opts.PageToken})
	if err != nil {
		return nil, err
	}
	return &Page[*AuditEvent]{Items: res.GetEvents(), NextPageToken: res.GetNextPageToken()}, nil
}

// All walks every audit event, newest first, fetching pages as the loop
// needs them:
//
//	for ev, err := range client.Audit.All(ctx, mimirsdk.ListOptions{}) {
//		if err != nil {
//			return err
//		}
//		fmt.Println(ev.GetActor(), ev.GetAction())
//	}
func (s *AuditService) All(ctx context.Context, opts ListOptions) iter.Seq2[*AuditEvent, error] {
	return paginate(ctx, opts.PageToken, func(ctx context.Context, token string) (*Page[*AuditEvent], error) {
		return s.ListPage(ctx, ListOptions{PageSize: opts.PageSize, PageToken: token})
	})
}

// CheckDatabase tries a PostgreSQL URL during first-run setup, before the
// server has a database. It needs the setup token the server printed in
// its log, and works only until setup is done.
func (s *AuthService) CheckDatabase(ctx context.Context, setupToken, databaseURL string) (*CheckDatabaseResponse, error) {
	return call(ctx, mimirv1connect.AuthServiceCheckDatabaseProcedure, s.raw.CheckDatabase,
		&mimirv1.CheckDatabaseRequest{SetupToken: setupToken, DatabaseUrl: databaseURL})
}

// Setup finishes first-run setup: it writes the configuration when
// SetupState says NeedsConfig, then makes the first owner. It needs the
// setup token and works only while the server has no users. When the
// response says SignInNext, sign in once the server has restarted.
func (s *AuthService) Setup(ctx context.Context, req *SetupRequest) (*SetupResponse, error) {
	return call(ctx, mimirv1connect.AuthServiceSetupProcedure, s.raw.Setup, req)
}

// ChangePassword changes the signed-in person's password.
func (s *AuthService) ChangePassword(ctx context.Context, current, next string) error {
	_, err := call(ctx, mimirv1connect.AuthServiceChangePasswordProcedure, s.raw.ChangePassword,
		&mimirv1.ChangePasswordRequest{CurrentPassword: current, NewPassword: next})
	return err
}

// StartTwoFactor makes a fresh authenticator secret for the signed-in
// person: show OtpauthUrl as a QR code, or Secret to type in. It takes
// effect only once EnableTwoFactor confirms a code from it. code is needed
// only when two-step verification is already on.
func (s *AuthService) StartTwoFactor(ctx context.Context, password, code string) (*StartTwoFactorResponse, error) {
	return call(ctx, mimirv1connect.AuthServiceStartTwoFactorProcedure, s.raw.StartTwoFactor,
		&mimirv1.StartTwoFactorRequest{Password: password, Code: code})
}

// EnableTwoFactor turns two-step verification on with a code from the
// secret StartTwoFactor made. It returns the recovery codes, shown only
// this once; each works a single time.
func (s *AuthService) EnableTwoFactor(ctx context.Context, code string) ([]string, error) {
	res, err := call(ctx, mimirv1connect.AuthServiceEnableTwoFactorProcedure, s.raw.EnableTwoFactor,
		&mimirv1.EnableTwoFactorRequest{Code: code})
	return res.GetRecoveryCodes(), err
}

// DisableTwoFactor turns two-step verification off. It needs the password
// and a current code from the authenticator app, or a recovery code.
func (s *AuthService) DisableTwoFactor(ctx context.Context, password, code string) error {
	_, err := call(ctx, mimirv1connect.AuthServiceDisableTwoFactorProcedure, s.raw.DisableTwoFactor,
		&mimirv1.DisableTwoFactorRequest{Password: password, Code: code})
	return err
}

// Sessions lists where the signed-in person is signed in; Current marks
// this one.
func (s *AuthService) Sessions(ctx context.Context) ([]*Session, error) {
	res, err := call(ctx, mimirv1connect.AuthServiceListSessionsProcedure, s.raw.ListSessions, nil)
	return res.GetSessions(), err
}

// RevokeSession signs out one session by its id.
func (s *AuthService) RevokeSession(ctx context.Context, id string) error {
	if id == "" {
		return errors.New("mimirsdk: RevokeSession needs a session id; use RevokeOtherSessions to sign out everywhere else")
	}
	_, err := call(ctx, mimirv1connect.AuthServiceRevokeSessionsProcedure, s.raw.RevokeSessions,
		&mimirv1.RevokeSessionsRequest{Id: id})
	return err
}

// RevokeOtherSessions signs out every session but this one, and says how
// many it signed out.
func (s *AuthService) RevokeOtherSessions(ctx context.Context) (int32, error) {
	res, err := call(ctx, mimirv1connect.AuthServiceRevokeSessionsProcedure, s.raw.RevokeSessions, nil)
	return res.GetRevoked(), err
}

// SignInService sets up signing in with an outside account: Google,
// GitHub, or a company's own identity provider through OpenID Connect.
// Options may be called by anyone; the rest needs an owner.
type SignInService struct {
	raw mimirv1connect.SignInServiceClient
}

// Options returns the buttons the sign-in page offers next to the
// password. Anyone may call it.
func (s *SignInService) Options(ctx context.Context) ([]*SignInOption, error) {
	res, err := call(ctx, mimirv1connect.SignInServiceListSignInOptionsProcedure, s.raw.ListSignInOptions, nil)
	return res.GetOptions(), err
}

// Providers returns every sign-in provider with its settings. Client
// secrets are never returned; ClientSecretSet says whether one is saved.
func (s *SignInService) Providers(ctx context.Context) ([]*SignInProvider, error) {
	res, err := call(ctx, mimirv1connect.SignInServiceListSignInProvidersProcedure, s.raw.ListSignInProviders, nil)
	return res.GetProviders(), err
}

// SaveProvider adds a provider, or changes the one with its Id. An empty
// ClientSecret keeps the saved one. Nobody new gets an account unless one
// of its Rules matches them.
func (s *SignInService) SaveProvider(ctx context.Context, p *SignInProvider) (*SignInProvider, error) {
	res, err := call(ctx, mimirv1connect.SignInServiceSaveSignInProviderProcedure, s.raw.SaveSignInProvider,
		&mimirv1.SaveSignInProviderRequest{Provider: p})
	return res.GetProvider(), err
}

// DeleteProvider removes a sign-in provider.
func (s *SignInService) DeleteProvider(ctx context.Context, id string) error {
	_, err := call(ctx, mimirv1connect.SignInServiceDeleteSignInProviderProcedure, s.raw.DeleteSignInProvider,
		&mimirv1.DeleteSignInProviderRequest{Id: id})
	return err
}
