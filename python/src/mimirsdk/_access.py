from __future__ import annotations

import builtins
from typing import Any, Iterator, Mapping, Union

from . import types as t
from ._base import Page, Service, paginate
from ._transport import to_message


def all_models(role: Union[t.Role, str]) -> t.Access:
    """Access with ``role`` on every model, including future ones."""
    return t.Access(role=role, all_models=True)


def some_models(role: Union[t.Role, str], *model_ids: str) -> t.Access:
    """Access with ``role`` on the listed models only."""
    return t.Access(role=role, model_ids=list(model_ids))


class AuthService(Service):
    """Says who the caller is, signs people in with a password and looks
    after their password, two-step verification and sessions. Apps should
    use an API key rather than signing in; signing in keeps the session in
    the client's cookies."""

    def who_am_i(self) -> t.WhoAmIResponse:
        """The caller and the permissions they have."""
        return self._call("mimir.v1.AuthService.WhoAmI", t.WhoAmIRequest())

    def setup_state(self) -> t.GetSetupStateResponse:
        """Whether the server still needs first-run setup. Anyone may call
        it, so it doubles as a check that the server is reachable."""
        return self._call("mimir.v1.AuthService.GetSetupState", t.GetSetupStateRequest())

    def check_database(self, setup_token: str, database_url: str) -> t.CheckDatabaseResponse:
        """Try a PostgreSQL URL during first-run setup, before the server
        has a database. It needs the setup token the server printed in its
        log, and works only until setup is done."""
        req = t.CheckDatabaseRequest(setup_token=setup_token, database_url=database_url)
        return self._call("mimir.v1.AuthService.CheckDatabase", req)

    def setup(self, request: Union[t.SetupRequest, Mapping[str, Any], None] = None, **fields: Any) -> t.SetupResponse:
        """Finish first-run setup: write the configuration when
        ``setup_state`` says ``needs_config``, then make the first owner. It
        needs the setup token and works only while the server has no users.
        When the response says ``sign_in_next``, sign in once the server has
        restarted."""
        return self._call("mimir.v1.AuthService.Setup", to_message(t.SetupRequest, request, fields))

    def sign_in(self, email: str, password: str) -> t.SignInResponse:
        """Sign in with an email and password. When the response says
        ``second_factor_required``, finish with ``verify_second_factor``."""
        return self._call("mimir.v1.AuthService.SignIn", t.SignInRequest(email=email, password=password))

    def verify_second_factor(self, code: str) -> t.VerifySecondFactorResponse:
        """Finish a sign-in with a code from an authenticator app, or a
        recovery code."""
        return self._call("mimir.v1.AuthService.VerifySecondFactor", t.VerifySecondFactorRequest(code=code))

    def sign_out(self) -> None:
        """End the signed-in session."""
        self._call("mimir.v1.AuthService.SignOut", t.SignOutRequest())

    def change_password(self, current: str, new: str) -> None:
        """Change the signed-in person's password."""
        req = t.ChangePasswordRequest(current_password=current, new_password=new)
        self._call("mimir.v1.AuthService.ChangePassword", req)

    def start_two_factor(self, password: str, code: str = "") -> t.StartTwoFactorResponse:
        """Make a fresh authenticator secret for the signed-in person: show
        ``otpauth_url`` as a QR code, or ``secret`` to type in. It takes
        effect only once ``enable_two_factor`` confirms a code from it.
        ``code`` is needed only when two-step verification is already on."""
        return self._call("mimir.v1.AuthService.StartTwoFactor", t.StartTwoFactorRequest(password=password, code=code))

    def enable_two_factor(self, code: str) -> builtins.list[str]:
        """Turn two-step verification on with a code from the secret
        ``start_two_factor`` made. Returns the recovery codes, shown only
        this once; each works a single time."""
        res = self._call("mimir.v1.AuthService.EnableTwoFactor", t.EnableTwoFactorRequest(code=code))
        return list(res.recovery_codes)

    def disable_two_factor(self, password: str, code: str) -> None:
        """Turn two-step verification off. It needs the password and a
        current code from the authenticator app, or a recovery code."""
        self._call("mimir.v1.AuthService.DisableTwoFactor", t.DisableTwoFactorRequest(password=password, code=code))

    def sessions(self) -> builtins.list[t.Session]:
        """Where the signed-in person is signed in; ``current`` marks this
        one."""
        return list(self._call("mimir.v1.AuthService.ListSessions", t.ListSessionsRequest()).sessions)

    def revoke_session(self, id: str) -> None:
        """Sign out one session by its id."""
        if not id:
            raise ValueError(
                "mimirsdk: revoke_session needs a session id; use revoke_other_sessions to sign out everywhere else"
            )
        self._call("mimir.v1.AuthService.RevokeSessions", t.RevokeSessionsRequest(id=id))

    def revoke_other_sessions(self) -> int:
        """Sign out every session but this one, and say how many it signed
        out."""
        return self._call("mimir.v1.AuthService.RevokeSessions", t.RevokeSessionsRequest()).revoked


class SignInService(Service):
    """Sets up signing in with an outside account: Google, GitHub, or a
    company's own identity provider through OpenID Connect. ``options`` may
    be called by anyone; the rest needs an owner."""

    def options(self) -> builtins.list[t.SignInOption]:
        """The buttons the sign-in page offers next to the password."""
        return list(self._call("mimir.v1.SignInService.ListSignInOptions", t.ListSignInOptionsRequest()).options)

    def providers(self) -> builtins.list[t.SignInProvider]:
        """Every sign-in provider with its settings. Client secrets are
        never returned; ``client_secret_set`` says whether one is saved."""
        res = self._call("mimir.v1.SignInService.ListSignInProviders", t.ListSignInProvidersRequest())
        return list(res.providers)

    def save_provider(self, provider: Union[t.SignInProvider, Mapping[str, Any]]) -> t.SignInProvider:
        """Add a provider, or change the one with its id. An empty
        ``client_secret`` keeps the saved one. Nobody new gets an account
        unless one of its rules matches them."""
        req = to_message(t.SaveSignInProviderRequest, {"provider": provider}, {})
        return self._call("mimir.v1.SignInService.SaveSignInProvider", req).provider

    def delete_provider(self, id: str) -> None:
        """Remove a sign-in provider."""
        self._call("mimir.v1.SignInService.DeleteSignInProvider", t.DeleteSignInProviderRequest(id=id))


class APIKeyService(Service):
    """Manages the caller's own API keys."""

    def list(self) -> builtins.list[t.ApiKey]:
        """The caller's keys. Secrets are never returned after ``create``."""
        return list(self._call("mimir.v1.ApiKeyService.ListApiKeys", t.ListApiKeysRequest()).api_keys)

    def create(self, name: str, access: Union[t.Access, Mapping[str, Any], None] = None) -> t.CreateApiKeyResponse:
        """Make a key with the given access, such as
        ``all_models(ROLE_EDITOR)``; a key never gets more than its owner
        has. Its ``secret`` is in the response only this once: store it
        somewhere safe."""
        req = to_message(t.CreateApiKeyRequest, {"name": name, "access": access} if access else {"name": name}, {})
        return self._call("mimir.v1.ApiKeyService.CreateApiKey", req)

    def revoke(self, id: str) -> None:
        """Stop a key working at once."""
        self._call("mimir.v1.ApiKeyService.RevokeApiKey", t.RevokeApiKeyRequest(id=id))


class UserService(Service):
    """Manages people. It needs an admin."""

    def list(self) -> builtins.list[t.User]:
        """Everyone the caller may manage."""
        return list(self._call("mimir.v1.UserService.ListUsers", t.ListUsersRequest()).users)

    def create(self, request: Union[t.CreateUserRequest, Mapping[str, Any], None] = None, **fields: Any) -> t.User:
        """Add a person."""
        return self._call("mimir.v1.UserService.CreateUser", to_message(t.CreateUserRequest, request, fields)).user

    def update(self, request: Union[t.UpdateUserRequest, Mapping[str, Any], None] = None, **fields: Any) -> t.User:
        """Change a person's name, access, team or password, or disable
        them."""
        return self._call("mimir.v1.UserService.UpdateUser", to_message(t.UpdateUserRequest, request, fields)).user

    def delete(self, id: str) -> None:
        """Remove a person."""
        self._call("mimir.v1.UserService.DeleteUser", t.DeleteUserRequest(id=id))


class TeamService(Service):
    """Manages teams. It needs an owner."""

    def list(self) -> builtins.list[t.Team]:
        """Every team."""
        return list(self._call("mimir.v1.TeamService.ListTeams", t.ListTeamsRequest()).teams)

    def create(self, name: str) -> t.Team:
        """Add a team."""
        return self._call("mimir.v1.TeamService.CreateTeam", t.CreateTeamRequest(name=name)).team

    def rename(self, id: str, name: str) -> t.Team:
        """Change a team's name."""
        return self._call("mimir.v1.TeamService.UpdateTeam", t.UpdateTeamRequest(id=id, name=name)).team

    def delete(self, id: str) -> None:
        """Remove an empty team."""
        self._call("mimir.v1.TeamService.DeleteTeam", t.DeleteTeamRequest(id=id))


class AuditService(Service):
    """Reads the record of who changed what. It needs an admin."""

    def list_page(self, *, page_size: int = 0, page_token: str = "") -> Page[t.AuditEvent]:
        """One page of audit events, newest first. A page_size of 0 lets the
        server choose."""
        req = t.ListAuditEventsRequest(page_size=page_size, page_token=page_token)
        res = self._call("mimir.v1.AuditService.ListAuditEvents", req)
        return Page(items=list(res.events), next_page_token=res.next_page_token)

    def all(self, *, page_size: int = 0, page_token: str = "") -> Iterator[t.AuditEvent]:
        """Every audit event, newest first, fetching pages as the loop needs
        them::

            for ev in client.audit.all():
                print(ev.actor, ev.action)
        """
        return paginate(page_token, lambda token: self.list_page(page_size=page_size, page_token=token))
