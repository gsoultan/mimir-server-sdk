import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from mimirsdk._gen.mimir.v1 import settings_pb2 as _settings_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Role(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ROLE_UNSPECIFIED: _ClassVar[Role]
    ROLE_VIEWER: _ClassVar[Role]
    ROLE_EDITOR: _ClassVar[Role]
    ROLE_ADMIN: _ClassVar[Role]
    ROLE_OWNER: _ClassVar[Role]

class SecretKeySource(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SECRET_KEY_SOURCE_UNSPECIFIED: _ClassVar[SecretKeySource]
    SECRET_KEY_SOURCE_NONE: _ClassVar[SecretKeySource]
    SECRET_KEY_SOURCE_ENVIRONMENT: _ClassVar[SecretKeySource]
    SECRET_KEY_SOURCE_FILE: _ClassVar[SecretKeySource]
ROLE_UNSPECIFIED: Role
ROLE_VIEWER: Role
ROLE_EDITOR: Role
ROLE_ADMIN: Role
ROLE_OWNER: Role
SECRET_KEY_SOURCE_UNSPECIFIED: SecretKeySource
SECRET_KEY_SOURCE_NONE: SecretKeySource
SECRET_KEY_SOURCE_ENVIRONMENT: SecretKeySource
SECRET_KEY_SOURCE_FILE: SecretKeySource

class Access(_message.Message):
    __slots__ = ("role", "all_models", "model_ids")
    ROLE_FIELD_NUMBER: _ClassVar[int]
    ALL_MODELS_FIELD_NUMBER: _ClassVar[int]
    MODEL_IDS_FIELD_NUMBER: _ClassVar[int]
    role: Role
    all_models: bool
    model_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, role: _Optional[_Union[Role, str]] = ..., all_models: bool = ..., model_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class User(_message.Message):
    __slots__ = ("id", "email", "name", "access", "disabled", "create_time", "last_sign_in_time", "two_factor", "team_id", "team_name")
    ID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ACCESS_FIELD_NUMBER: _ClassVar[int]
    DISABLED_FIELD_NUMBER: _ClassVar[int]
    CREATE_TIME_FIELD_NUMBER: _ClassVar[int]
    LAST_SIGN_IN_TIME_FIELD_NUMBER: _ClassVar[int]
    TWO_FACTOR_FIELD_NUMBER: _ClassVar[int]
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    TEAM_NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    email: str
    name: str
    access: Access
    disabled: bool
    create_time: _timestamp_pb2.Timestamp
    last_sign_in_time: _timestamp_pb2.Timestamp
    two_factor: bool
    team_id: str
    team_name: str
    def __init__(self, id: _Optional[str] = ..., email: _Optional[str] = ..., name: _Optional[str] = ..., access: _Optional[_Union[Access, _Mapping]] = ..., disabled: bool = ..., create_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., last_sign_in_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., two_factor: bool = ..., team_id: _Optional[str] = ..., team_name: _Optional[str] = ...) -> None: ...

class GetSetupStateRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetSetupStateResponse(_message.Message):
    __slots__ = ("needs_setup", "needs_config", "secret_key", "retention")
    NEEDS_SETUP_FIELD_NUMBER: _ClassVar[int]
    NEEDS_CONFIG_FIELD_NUMBER: _ClassVar[int]
    SECRET_KEY_FIELD_NUMBER: _ClassVar[int]
    RETENTION_FIELD_NUMBER: _ClassVar[int]
    needs_setup: bool
    needs_config: bool
    secret_key: SecretKeySource
    retention: _settings_pb2.Retention
    def __init__(self, needs_setup: bool = ..., needs_config: bool = ..., secret_key: _Optional[_Union[SecretKeySource, str]] = ..., retention: _Optional[_Union[_settings_pb2.Retention, _Mapping]] = ...) -> None: ...

class CheckDatabaseRequest(_message.Message):
    __slots__ = ("setup_token", "database_url")
    SETUP_TOKEN_FIELD_NUMBER: _ClassVar[int]
    DATABASE_URL_FIELD_NUMBER: _ClassVar[int]
    setup_token: str
    database_url: str
    def __init__(self, setup_token: _Optional[str] = ..., database_url: _Optional[str] = ...) -> None: ...

class CheckDatabaseResponse(_message.Message):
    __slots__ = ("version", "has_accounts")
    VERSION_FIELD_NUMBER: _ClassVar[int]
    HAS_ACCOUNTS_FIELD_NUMBER: _ClassVar[int]
    version: str
    has_accounts: bool
    def __init__(self, version: _Optional[str] = ..., has_accounts: bool = ...) -> None: ...

class SetupRequest(_message.Message):
    __slots__ = ("email", "name", "password", "setup_token", "database_url", "log_database_url", "secret_key", "retention")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    SETUP_TOKEN_FIELD_NUMBER: _ClassVar[int]
    DATABASE_URL_FIELD_NUMBER: _ClassVar[int]
    LOG_DATABASE_URL_FIELD_NUMBER: _ClassVar[int]
    SECRET_KEY_FIELD_NUMBER: _ClassVar[int]
    RETENTION_FIELD_NUMBER: _ClassVar[int]
    email: str
    name: str
    password: str
    setup_token: str
    database_url: str
    log_database_url: str
    secret_key: str
    retention: _settings_pb2.Retention
    def __init__(self, email: _Optional[str] = ..., name: _Optional[str] = ..., password: _Optional[str] = ..., setup_token: _Optional[str] = ..., database_url: _Optional[str] = ..., log_database_url: _Optional[str] = ..., secret_key: _Optional[str] = ..., retention: _Optional[_Union[_settings_pb2.Retention, _Mapping]] = ...) -> None: ...

class SetupResponse(_message.Message):
    __slots__ = ("user", "sign_in_next")
    USER_FIELD_NUMBER: _ClassVar[int]
    SIGN_IN_NEXT_FIELD_NUMBER: _ClassVar[int]
    user: User
    sign_in_next: bool
    def __init__(self, user: _Optional[_Union[User, _Mapping]] = ..., sign_in_next: bool = ...) -> None: ...

class SignInRequest(_message.Message):
    __slots__ = ("email", "password")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    email: str
    password: str
    def __init__(self, email: _Optional[str] = ..., password: _Optional[str] = ...) -> None: ...

class SignInResponse(_message.Message):
    __slots__ = ("user", "second_factor_required")
    USER_FIELD_NUMBER: _ClassVar[int]
    SECOND_FACTOR_REQUIRED_FIELD_NUMBER: _ClassVar[int]
    user: User
    second_factor_required: bool
    def __init__(self, user: _Optional[_Union[User, _Mapping]] = ..., second_factor_required: bool = ...) -> None: ...

class SignOutRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SignOutResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WhoAmIRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WhoAmIResponse(_message.Message):
    __slots__ = ("user", "permissions", "session_id", "must_set_up_two_factor")
    USER_FIELD_NUMBER: _ClassVar[int]
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MUST_SET_UP_TWO_FACTOR_FIELD_NUMBER: _ClassVar[int]
    user: User
    permissions: _containers.RepeatedScalarFieldContainer[str]
    session_id: str
    must_set_up_two_factor: bool
    def __init__(self, user: _Optional[_Union[User, _Mapping]] = ..., permissions: _Optional[_Iterable[str]] = ..., session_id: _Optional[str] = ..., must_set_up_two_factor: bool = ...) -> None: ...

class ChangePasswordRequest(_message.Message):
    __slots__ = ("current_password", "new_password")
    CURRENT_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    NEW_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    current_password: str
    new_password: str
    def __init__(self, current_password: _Optional[str] = ..., new_password: _Optional[str] = ...) -> None: ...

class ChangePasswordResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class VerifySecondFactorRequest(_message.Message):
    __slots__ = ("code",)
    CODE_FIELD_NUMBER: _ClassVar[int]
    code: str
    def __init__(self, code: _Optional[str] = ...) -> None: ...

class VerifySecondFactorResponse(_message.Message):
    __slots__ = ("user", "recovery_codes_left", "used_recovery_code")
    USER_FIELD_NUMBER: _ClassVar[int]
    RECOVERY_CODES_LEFT_FIELD_NUMBER: _ClassVar[int]
    USED_RECOVERY_CODE_FIELD_NUMBER: _ClassVar[int]
    user: User
    recovery_codes_left: int
    used_recovery_code: bool
    def __init__(self, user: _Optional[_Union[User, _Mapping]] = ..., recovery_codes_left: _Optional[int] = ..., used_recovery_code: bool = ...) -> None: ...

class StartTwoFactorRequest(_message.Message):
    __slots__ = ("password", "code")
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    password: str
    code: str
    def __init__(self, password: _Optional[str] = ..., code: _Optional[str] = ...) -> None: ...

class StartTwoFactorResponse(_message.Message):
    __slots__ = ("secret", "otpauth_url")
    SECRET_FIELD_NUMBER: _ClassVar[int]
    OTPAUTH_URL_FIELD_NUMBER: _ClassVar[int]
    secret: str
    otpauth_url: str
    def __init__(self, secret: _Optional[str] = ..., otpauth_url: _Optional[str] = ...) -> None: ...

class EnableTwoFactorRequest(_message.Message):
    __slots__ = ("code",)
    CODE_FIELD_NUMBER: _ClassVar[int]
    code: str
    def __init__(self, code: _Optional[str] = ...) -> None: ...

class EnableTwoFactorResponse(_message.Message):
    __slots__ = ("recovery_codes",)
    RECOVERY_CODES_FIELD_NUMBER: _ClassVar[int]
    recovery_codes: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, recovery_codes: _Optional[_Iterable[str]] = ...) -> None: ...

class DisableTwoFactorRequest(_message.Message):
    __slots__ = ("password", "code")
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    password: str
    code: str
    def __init__(self, password: _Optional[str] = ..., code: _Optional[str] = ...) -> None: ...

class DisableTwoFactorResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Session(_message.Message):
    __slots__ = ("id", "device", "ip", "create_time", "last_seen_time", "current")
    ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_FIELD_NUMBER: _ClassVar[int]
    IP_FIELD_NUMBER: _ClassVar[int]
    CREATE_TIME_FIELD_NUMBER: _ClassVar[int]
    LAST_SEEN_TIME_FIELD_NUMBER: _ClassVar[int]
    CURRENT_FIELD_NUMBER: _ClassVar[int]
    id: str
    device: str
    ip: str
    create_time: _timestamp_pb2.Timestamp
    last_seen_time: _timestamp_pb2.Timestamp
    current: bool
    def __init__(self, id: _Optional[str] = ..., device: _Optional[str] = ..., ip: _Optional[str] = ..., create_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., last_seen_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., current: bool = ...) -> None: ...

class ListSessionsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListSessionsResponse(_message.Message):
    __slots__ = ("sessions",)
    SESSIONS_FIELD_NUMBER: _ClassVar[int]
    sessions: _containers.RepeatedCompositeFieldContainer[Session]
    def __init__(self, sessions: _Optional[_Iterable[_Union[Session, _Mapping]]] = ...) -> None: ...

class RevokeSessionsRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class RevokeSessionsResponse(_message.Message):
    __slots__ = ("revoked",)
    REVOKED_FIELD_NUMBER: _ClassVar[int]
    revoked: int
    def __init__(self, revoked: _Optional[int] = ...) -> None: ...

class ListUsersRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListUsersResponse(_message.Message):
    __slots__ = ("users",)
    USERS_FIELD_NUMBER: _ClassVar[int]
    users: _containers.RepeatedCompositeFieldContainer[User]
    def __init__(self, users: _Optional[_Iterable[_Union[User, _Mapping]]] = ...) -> None: ...

class CreateUserRequest(_message.Message):
    __slots__ = ("email", "name", "password", "access", "team_id")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    ACCESS_FIELD_NUMBER: _ClassVar[int]
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    email: str
    name: str
    password: str
    access: Access
    team_id: str
    def __init__(self, email: _Optional[str] = ..., name: _Optional[str] = ..., password: _Optional[str] = ..., access: _Optional[_Union[Access, _Mapping]] = ..., team_id: _Optional[str] = ...) -> None: ...

class CreateUserResponse(_message.Message):
    __slots__ = ("user",)
    USER_FIELD_NUMBER: _ClassVar[int]
    user: User
    def __init__(self, user: _Optional[_Union[User, _Mapping]] = ...) -> None: ...

class UpdateUserRequest(_message.Message):
    __slots__ = ("id", "name", "access", "disabled", "new_password", "reset_two_factor", "team_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ACCESS_FIELD_NUMBER: _ClassVar[int]
    DISABLED_FIELD_NUMBER: _ClassVar[int]
    NEW_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    RESET_TWO_FACTOR_FIELD_NUMBER: _ClassVar[int]
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    access: Access
    disabled: bool
    new_password: str
    reset_two_factor: bool
    team_id: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., access: _Optional[_Union[Access, _Mapping]] = ..., disabled: bool = ..., new_password: _Optional[str] = ..., reset_two_factor: bool = ..., team_id: _Optional[str] = ...) -> None: ...

class UpdateUserResponse(_message.Message):
    __slots__ = ("user",)
    USER_FIELD_NUMBER: _ClassVar[int]
    user: User
    def __init__(self, user: _Optional[_Union[User, _Mapping]] = ...) -> None: ...

class DeleteUserRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteUserResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ApiKey(_message.Message):
    __slots__ = ("id", "name", "prefix", "access", "create_time", "last_used_time")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PREFIX_FIELD_NUMBER: _ClassVar[int]
    ACCESS_FIELD_NUMBER: _ClassVar[int]
    CREATE_TIME_FIELD_NUMBER: _ClassVar[int]
    LAST_USED_TIME_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    prefix: str
    access: Access
    create_time: _timestamp_pb2.Timestamp
    last_used_time: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., prefix: _Optional[str] = ..., access: _Optional[_Union[Access, _Mapping]] = ..., create_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., last_used_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ListApiKeysRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListApiKeysResponse(_message.Message):
    __slots__ = ("api_keys",)
    API_KEYS_FIELD_NUMBER: _ClassVar[int]
    api_keys: _containers.RepeatedCompositeFieldContainer[ApiKey]
    def __init__(self, api_keys: _Optional[_Iterable[_Union[ApiKey, _Mapping]]] = ...) -> None: ...

class CreateApiKeyRequest(_message.Message):
    __slots__ = ("name", "access")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ACCESS_FIELD_NUMBER: _ClassVar[int]
    name: str
    access: Access
    def __init__(self, name: _Optional[str] = ..., access: _Optional[_Union[Access, _Mapping]] = ...) -> None: ...

class CreateApiKeyResponse(_message.Message):
    __slots__ = ("api_key", "secret")
    API_KEY_FIELD_NUMBER: _ClassVar[int]
    SECRET_FIELD_NUMBER: _ClassVar[int]
    api_key: ApiKey
    secret: str
    def __init__(self, api_key: _Optional[_Union[ApiKey, _Mapping]] = ..., secret: _Optional[str] = ...) -> None: ...

class RevokeApiKeyRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class RevokeApiKeyResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AuditEvent(_message.Message):
    __slots__ = ("id", "time", "actor", "action", "target", "detail", "team_name")
    ID_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    ACTOR_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    DETAIL_FIELD_NUMBER: _ClassVar[int]
    TEAM_NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    time: _timestamp_pb2.Timestamp
    actor: str
    action: str
    target: str
    detail: str
    team_name: str
    def __init__(self, id: _Optional[str] = ..., time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., actor: _Optional[str] = ..., action: _Optional[str] = ..., target: _Optional[str] = ..., detail: _Optional[str] = ..., team_name: _Optional[str] = ...) -> None: ...

class ListAuditEventsRequest(_message.Message):
    __slots__ = ("page_size", "page_token")
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    page_size: int
    page_token: str
    def __init__(self, page_size: _Optional[int] = ..., page_token: _Optional[str] = ...) -> None: ...

class ListAuditEventsResponse(_message.Message):
    __slots__ = ("events", "next_page_token")
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    events: _containers.RepeatedCompositeFieldContainer[AuditEvent]
    next_page_token: str
    def __init__(self, events: _Optional[_Iterable[_Union[AuditEvent, _Mapping]]] = ..., next_page_token: _Optional[str] = ...) -> None: ...
