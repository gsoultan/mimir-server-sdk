import { create } from "@bufbuild/protobuf";
import {
  AccessSchema,
  ApiKeyService as ApiKeyRPC,
  AuditService as AuditRPC,
  AuthService as AuthRPC,
  UserService as UserRPC,
  type Access,
  type ApiKey,
  type AuditEvent,
  type CheckDatabaseResponse,
  type CreateApiKeyResponse,
  type CreateUserRequestSchema,
  type GetSetupStateResponse,
  type Role,
  type Session,
  type SetupRequestSchema,
  type SetupResponse,
  type SignInResponse,
  type StartTwoFactorResponse,
  type UpdateUserRequestSchema,
  type User,
  type VerifySecondFactorResponse,
  type WhoAmIResponse,
} from "./gen/mimir/v1/access_pb.js";
import {
  SignInService as SignInRPC,
  type SignInOption,
  type SignInProvider,
  type SignInProviderSchema,
} from "./gen/mimir/v1/signin_pb.js";
import { TeamService as TeamRPC, type Team } from "./gen/mimir/v1/team_pb.js";
import type { Caller, CallOptions } from "./transport.js";
import { paginate, type Init, type ListOptions, type Page } from "./util.js";

/** Access with role on every model, including future ones. */
export function allModels(role: Role): Access {
  return create(AccessSchema, { role, allModels: true });
}

/** Access with role on the listed models only. */
export function someModels(role: Role, ...modelIds: string[]): Access {
  return create(AccessSchema, { role, modelIds });
}

/** Says who the caller is, signs people in with a password and looks after
 * their password, two-step verification and sessions. Apps should use an
 * API key rather than signing in; in a browser, signing in sets the
 * session cookie. */
export class AuthService {
  constructor(private readonly c: Caller) {}

  /** The caller and the permissions they have. */
  async whoAmI(opts?: CallOptions): Promise<WhoAmIResponse> {
    return this.c.unary(AuthRPC.method.whoAmI, {}, opts);
  }

  /** Whether the server still needs first-run setup. Anyone may call it, so
   * it doubles as a check that the server is reachable. */
  async setupState(opts?: CallOptions): Promise<GetSetupStateResponse> {
    return this.c.unary(AuthRPC.method.getSetupState, {}, opts);
  }

  /** Try a PostgreSQL URL during first-run setup, with the setup token the
   * server printed in its log. */
  async checkDatabase(setupToken: string, databaseUrl: string, opts?: CallOptions): Promise<CheckDatabaseResponse> {
    return this.c.unary(AuthRPC.method.checkDatabase, { setupToken, databaseUrl }, opts);
  }

  /** Finish first-run setup: write the configuration when setupState says
   * needsConfig, then make the first owner. */
  async setup(req: Init<typeof SetupRequestSchema>, opts?: CallOptions): Promise<SetupResponse> {
    return this.c.unary(AuthRPC.method.setup, req, opts);
  }

  /** Sign in with an email and password. When the response says
   * secondFactorRequired, finish with verifySecondFactor. */
  async signIn(email: string, password: string, opts?: CallOptions): Promise<SignInResponse> {
    return this.c.unary(AuthRPC.method.signIn, { email, password }, opts);
  }

  /** Finish a sign-in with a code from an authenticator app, or a recovery
   * code. */
  async verifySecondFactor(code: string, opts?: CallOptions): Promise<VerifySecondFactorResponse> {
    return this.c.unary(AuthRPC.method.verifySecondFactor, { code }, opts);
  }

  /** End the signed-in session. */
  async signOut(opts?: CallOptions): Promise<void> {
    await this.c.unary(AuthRPC.method.signOut, {}, opts);
  }

  /** Change the signed-in person's password. */
  async changePassword(currentPassword: string, newPassword: string, opts?: CallOptions): Promise<void> {
    await this.c.unary(AuthRPC.method.changePassword, { currentPassword, newPassword }, opts);
  }

  /** Make a fresh authenticator secret for the signed-in person. It takes
   * effect only once enableTwoFactor confirms a code from it. code is needed
   * only when two-step verification is already on. */
  async startTwoFactor(password: string, code = "", opts?: CallOptions): Promise<StartTwoFactorResponse> {
    return this.c.unary(AuthRPC.method.startTwoFactor, { password, code }, opts);
  }

  /** Turn two-step verification on. Resolves to the recovery codes, shown
   * only this once. */
  async enableTwoFactor(code: string, opts?: CallOptions): Promise<string[]> {
    return (await this.c.unary(AuthRPC.method.enableTwoFactor, { code }, opts)).recoveryCodes;
  }

  /** Turn two-step verification off, with the password and a current code
   * or a recovery code. */
  async disableTwoFactor(password: string, code: string, opts?: CallOptions): Promise<void> {
    await this.c.unary(AuthRPC.method.disableTwoFactor, { password, code }, opts);
  }

  /** Where the signed-in person is signed in; current marks this one. */
  async sessions(opts?: CallOptions): Promise<Session[]> {
    return (await this.c.unary(AuthRPC.method.listSessions, {}, opts)).sessions;
  }

  /** Sign out one session by its id. */
  async revokeSession(id: string, opts?: CallOptions): Promise<void> {
    if (!id) {
      throw new Error(
        "mimirsdk: revokeSession needs a session id; use revokeOtherSessions to sign out everywhere else",
      );
    }
    await this.c.unary(AuthRPC.method.revokeSessions, { id }, opts);
  }

  /** Sign out every session but this one, and resolve to how many it signed
   * out. */
  async revokeOtherSessions(opts?: CallOptions): Promise<number> {
    return (await this.c.unary(AuthRPC.method.revokeSessions, {}, opts)).revoked;
  }
}

/** Sets up signing in with an outside account: Google, GitHub, or OpenID
 * Connect. options may be called by anyone; the rest needs an owner. */
export class SignInService {
  constructor(private readonly c: Caller) {}

  /** The buttons the sign-in page offers next to the password. */
  async options(opts?: CallOptions): Promise<SignInOption[]> {
    return (await this.c.unary(SignInRPC.method.listSignInOptions, {}, opts)).options;
  }

  /** Every sign-in provider with its settings. Client secrets are never
   * returned; clientSecretSet says whether one is saved. */
  async providers(opts?: CallOptions): Promise<SignInProvider[]> {
    return (await this.c.unary(SignInRPC.method.listSignInProviders, {}, opts)).providers;
  }

  /** Add a provider, or change the one with its id. An empty clientSecret
   * keeps the saved one. */
  async saveProvider(provider: Init<typeof SignInProviderSchema>, opts?: CallOptions): Promise<SignInProvider> {
    return (await this.c.unary(SignInRPC.method.saveSignInProvider, { provider }, opts)).provider!;
  }

  /** Remove a sign-in provider. */
  async deleteProvider(id: string, opts?: CallOptions): Promise<void> {
    await this.c.unary(SignInRPC.method.deleteSignInProvider, { id }, opts);
  }
}

/** Manages the caller's own API keys. */
export class APIKeyService {
  constructor(private readonly c: Caller) {}

  /** The caller's keys. Secrets are never returned after create. */
  async list(opts?: CallOptions): Promise<ApiKey[]> {
    return (await this.c.unary(ApiKeyRPC.method.listApiKeys, {}, opts)).apiKeys;
  }

  /** Make a key with the given access, such as allModels(Role.EDITOR). Its
   * secret is in the response only this once. */
  async create(name: string, access?: Access, opts?: CallOptions): Promise<CreateApiKeyResponse> {
    return this.c.unary(ApiKeyRPC.method.createApiKey, { name, access }, opts);
  }

  /** Stop a key working at once. */
  async revoke(id: string, opts?: CallOptions): Promise<void> {
    await this.c.unary(ApiKeyRPC.method.revokeApiKey, { id }, opts);
  }
}

/** Manages people. It needs an admin. */
export class UserService {
  constructor(private readonly c: Caller) {}

  /** Everyone the caller may manage. */
  async list(opts?: CallOptions): Promise<User[]> {
    return (await this.c.unary(UserRPC.method.listUsers, {}, opts)).users;
  }

  /** Add a person. */
  async create(req: Init<typeof CreateUserRequestSchema>, opts?: CallOptions): Promise<User> {
    return (await this.c.unary(UserRPC.method.createUser, req, opts)).user!;
  }

  /** Change a person's name, access, team or password, or disable them. */
  async update(req: Init<typeof UpdateUserRequestSchema>, opts?: CallOptions): Promise<User> {
    return (await this.c.unary(UserRPC.method.updateUser, req, opts)).user!;
  }

  /** Remove a person. */
  async delete(id: string, opts?: CallOptions): Promise<void> {
    await this.c.unary(UserRPC.method.deleteUser, { id }, opts);
  }
}

/** Manages teams. It needs an owner. */
export class TeamService {
  constructor(private readonly c: Caller) {}

  /** Every team. */
  async list(opts?: CallOptions): Promise<Team[]> {
    return (await this.c.unary(TeamRPC.method.listTeams, {}, opts)).teams;
  }

  /** Add a team. */
  async create(name: string, opts?: CallOptions): Promise<Team> {
    return (await this.c.unary(TeamRPC.method.createTeam, { name }, opts)).team!;
  }

  /** Change a team's name. */
  async rename(id: string, name: string, opts?: CallOptions): Promise<Team> {
    return (await this.c.unary(TeamRPC.method.updateTeam, { id, name }, opts)).team!;
  }

  /** Remove an empty team. */
  async delete(id: string, opts?: CallOptions): Promise<void> {
    await this.c.unary(TeamRPC.method.deleteTeam, { id }, opts);
  }
}

/** Reads the record of who changed what. It needs an admin. */
export class AuditService {
  constructor(private readonly c: Caller) {}

  /** One page of audit events, newest first. */
  async listPage(opts: ListOptions = {}): Promise<Page<AuditEvent>> {
    const { pageSize = 0, pageToken = "", ...call } = opts;
    const res = await this.c.unary(AuditRPC.method.listAuditEvents, { pageSize, pageToken }, call);
    return { items: res.events, nextPageToken: res.nextPageToken };
  }

  /** Every audit event, newest first, fetching pages as the loop needs
   * them:
   *
   *     for await (const ev of client.audit.all()) console.log(ev.actor, ev.action);
   */
  all(opts: ListOptions = {}): AsyncGenerator<AuditEvent> {
    return paginate(opts.pageToken ?? "", (pageToken) => this.listPage({ ...opts, pageToken }));
  }
}
