import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TwoFactorPolicy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TWO_FACTOR_POLICY_UNSPECIFIED: _ClassVar[TwoFactorPolicy]
    TWO_FACTOR_POLICY_OPTIONAL: _ClassVar[TwoFactorPolicy]
    TWO_FACTOR_POLICY_ADMINS: _ClassVar[TwoFactorPolicy]
    TWO_FACTOR_POLICY_EVERYONE: _ClassVar[TwoFactorPolicy]
TWO_FACTOR_POLICY_UNSPECIFIED: TwoFactorPolicy
TWO_FACTOR_POLICY_OPTIONAL: TwoFactorPolicy
TWO_FACTOR_POLICY_ADMINS: TwoFactorPolicy
TWO_FACTOR_POLICY_EVERYONE: TwoFactorPolicy

class EmailAlerts(_message.Message):
    __slots__ = ("enabled", "host", "port", "username", "password", "password_set", "to")
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    HOST_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_SET_FIELD_NUMBER: _ClassVar[int]
    FROM_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    enabled: bool
    host: str
    port: int
    username: str
    password: str
    password_set: bool
    to: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, enabled: bool = ..., host: _Optional[str] = ..., port: _Optional[int] = ..., username: _Optional[str] = ..., password: _Optional[str] = ..., password_set: bool = ..., to: _Optional[_Iterable[str]] = ..., **kwargs) -> None: ...

class TelegramAlerts(_message.Message):
    __slots__ = ("enabled", "bot_token", "token_set", "chat_id")
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    BOT_TOKEN_FIELD_NUMBER: _ClassVar[int]
    TOKEN_SET_FIELD_NUMBER: _ClassVar[int]
    CHAT_ID_FIELD_NUMBER: _ClassVar[int]
    enabled: bool
    bot_token: str
    token_set: bool
    chat_id: str
    def __init__(self, enabled: bool = ..., bot_token: _Optional[str] = ..., token_set: bool = ..., chat_id: _Optional[str] = ...) -> None: ...

class Retention(_message.Message):
    __slots__ = ("audit_days", "delivery_days")
    AUDIT_DAYS_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DAYS_FIELD_NUMBER: _ClassVar[int]
    audit_days: int
    delivery_days: int
    def __init__(self, audit_days: _Optional[int] = ..., delivery_days: _Optional[int] = ...) -> None: ...

class GetSettingsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetSettingsResponse(_message.Message):
    __slots__ = ("email", "telegram", "retention", "security", "limits", "training")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    TELEGRAM_FIELD_NUMBER: _ClassVar[int]
    RETENTION_FIELD_NUMBER: _ClassVar[int]
    SECURITY_FIELD_NUMBER: _ClassVar[int]
    LIMITS_FIELD_NUMBER: _ClassVar[int]
    TRAINING_FIELD_NUMBER: _ClassVar[int]
    email: EmailAlerts
    telegram: TelegramAlerts
    retention: Retention
    security: Security
    limits: Limits
    training: Training
    def __init__(self, email: _Optional[_Union[EmailAlerts, _Mapping]] = ..., telegram: _Optional[_Union[TelegramAlerts, _Mapping]] = ..., retention: _Optional[_Union[Retention, _Mapping]] = ..., security: _Optional[_Union[Security, _Mapping]] = ..., limits: _Optional[_Union[Limits, _Mapping]] = ..., training: _Optional[_Union[Training, _Mapping]] = ...) -> None: ...

class Training(_message.Message):
    __slots__ = ("train_here", "can_train_here", "group_workers")
    TRAIN_HERE_FIELD_NUMBER: _ClassVar[int]
    CAN_TRAIN_HERE_FIELD_NUMBER: _ClassVar[int]
    GROUP_WORKERS_FIELD_NUMBER: _ClassVar[int]
    train_here: bool
    can_train_here: bool
    group_workers: int
    def __init__(self, train_here: bool = ..., can_train_here: bool = ..., group_workers: _Optional[int] = ...) -> None: ...

class UpdateTrainingRequest(_message.Message):
    __slots__ = ("train_here", "group_workers")
    TRAIN_HERE_FIELD_NUMBER: _ClassVar[int]
    GROUP_WORKERS_FIELD_NUMBER: _ClassVar[int]
    train_here: bool
    group_workers: int
    def __init__(self, train_here: bool = ..., group_workers: _Optional[int] = ...) -> None: ...

class UpdateTrainingResponse(_message.Message):
    __slots__ = ("training",)
    TRAINING_FIELD_NUMBER: _ClassVar[int]
    training: Training
    def __init__(self, training: _Optional[_Union[Training, _Mapping]] = ...) -> None: ...

class Limits(_message.Message):
    __slots__ = ("predictions_per_minute", "predictions_per_month", "training_runs_per_person")
    PREDICTIONS_PER_MINUTE_FIELD_NUMBER: _ClassVar[int]
    PREDICTIONS_PER_MONTH_FIELD_NUMBER: _ClassVar[int]
    TRAINING_RUNS_PER_PERSON_FIELD_NUMBER: _ClassVar[int]
    predictions_per_minute: int
    predictions_per_month: int
    training_runs_per_person: int
    def __init__(self, predictions_per_minute: _Optional[int] = ..., predictions_per_month: _Optional[int] = ..., training_runs_per_person: _Optional[int] = ...) -> None: ...

class UpdateLimitsRequest(_message.Message):
    __slots__ = ("limits",)
    LIMITS_FIELD_NUMBER: _ClassVar[int]
    limits: Limits
    def __init__(self, limits: _Optional[_Union[Limits, _Mapping]] = ...) -> None: ...

class UpdateLimitsResponse(_message.Message):
    __slots__ = ("limits",)
    LIMITS_FIELD_NUMBER: _ClassVar[int]
    limits: Limits
    def __init__(self, limits: _Optional[_Union[Limits, _Mapping]] = ...) -> None: ...

class GetUsageRequest(_message.Message):
    __slots__ = ("month",)
    MONTH_FIELD_NUMBER: _ClassVar[int]
    month: str
    def __init__(self, month: _Optional[str] = ...) -> None: ...

class UsageRow(_message.Message):
    __slots__ = ("user_id", "user_name", "email", "key_name", "predictions")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    USER_NAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    KEY_NAME_FIELD_NUMBER: _ClassVar[int]
    PREDICTIONS_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    user_name: str
    email: str
    key_name: str
    predictions: int
    def __init__(self, user_id: _Optional[str] = ..., user_name: _Optional[str] = ..., email: _Optional[str] = ..., key_name: _Optional[str] = ..., predictions: _Optional[int] = ...) -> None: ...

class GetUsageResponse(_message.Message):
    __slots__ = ("month", "rows", "total", "limit")
    MONTH_FIELD_NUMBER: _ClassVar[int]
    ROWS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    month: str
    rows: _containers.RepeatedCompositeFieldContainer[UsageRow]
    total: int
    limit: int
    def __init__(self, month: _Optional[str] = ..., rows: _Optional[_Iterable[_Union[UsageRow, _Mapping]]] = ..., total: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class Security(_message.Message):
    __slots__ = ("two_factor",)
    TWO_FACTOR_FIELD_NUMBER: _ClassVar[int]
    two_factor: TwoFactorPolicy
    def __init__(self, two_factor: _Optional[_Union[TwoFactorPolicy, str]] = ...) -> None: ...

class UpdateSecurityRequest(_message.Message):
    __slots__ = ("security",)
    SECURITY_FIELD_NUMBER: _ClassVar[int]
    security: Security
    def __init__(self, security: _Optional[_Union[Security, _Mapping]] = ...) -> None: ...

class UpdateSecurityResponse(_message.Message):
    __slots__ = ("security",)
    SECURITY_FIELD_NUMBER: _ClassVar[int]
    security: Security
    def __init__(self, security: _Optional[_Union[Security, _Mapping]] = ...) -> None: ...

class UpdateAlertsRequest(_message.Message):
    __slots__ = ("email", "telegram")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    TELEGRAM_FIELD_NUMBER: _ClassVar[int]
    email: EmailAlerts
    telegram: TelegramAlerts
    def __init__(self, email: _Optional[_Union[EmailAlerts, _Mapping]] = ..., telegram: _Optional[_Union[TelegramAlerts, _Mapping]] = ...) -> None: ...

class UpdateAlertsResponse(_message.Message):
    __slots__ = ("email", "telegram")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    TELEGRAM_FIELD_NUMBER: _ClassVar[int]
    email: EmailAlerts
    telegram: TelegramAlerts
    def __init__(self, email: _Optional[_Union[EmailAlerts, _Mapping]] = ..., telegram: _Optional[_Union[TelegramAlerts, _Mapping]] = ...) -> None: ...

class SendTestAlertRequest(_message.Message):
    __slots__ = ("channel",)
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    channel: str
    def __init__(self, channel: _Optional[str] = ...) -> None: ...

class SendTestAlertResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UpdateRetentionRequest(_message.Message):
    __slots__ = ("retention",)
    RETENTION_FIELD_NUMBER: _ClassVar[int]
    retention: Retention
    def __init__(self, retention: _Optional[_Union[Retention, _Mapping]] = ...) -> None: ...

class UpdateRetentionResponse(_message.Message):
    __slots__ = ("retention",)
    RETENTION_FIELD_NUMBER: _ClassVar[int]
    retention: Retention
    def __init__(self, retention: _Optional[_Union[Retention, _Mapping]] = ...) -> None: ...

class GetDatabaseInfoRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetDatabaseInfoResponse(_message.Message):
    __slots__ = ("kind", "path", "size_bytes", "schema_version", "latest_schema_version", "models", "users", "audit_events", "deliveries", "last_trim_time", "last_trim_rows", "log_path")
    KIND_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    SIZE_BYTES_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_VERSION_FIELD_NUMBER: _ClassVar[int]
    LATEST_SCHEMA_VERSION_FIELD_NUMBER: _ClassVar[int]
    MODELS_FIELD_NUMBER: _ClassVar[int]
    USERS_FIELD_NUMBER: _ClassVar[int]
    AUDIT_EVENTS_FIELD_NUMBER: _ClassVar[int]
    DELIVERIES_FIELD_NUMBER: _ClassVar[int]
    LAST_TRIM_TIME_FIELD_NUMBER: _ClassVar[int]
    LAST_TRIM_ROWS_FIELD_NUMBER: _ClassVar[int]
    LOG_PATH_FIELD_NUMBER: _ClassVar[int]
    kind: str
    path: str
    size_bytes: int
    schema_version: int
    latest_schema_version: int
    models: int
    users: int
    audit_events: int
    deliveries: int
    last_trim_time: _timestamp_pb2.Timestamp
    last_trim_rows: int
    log_path: str
    def __init__(self, kind: _Optional[str] = ..., path: _Optional[str] = ..., size_bytes: _Optional[int] = ..., schema_version: _Optional[int] = ..., latest_schema_version: _Optional[int] = ..., models: _Optional[int] = ..., users: _Optional[int] = ..., audit_events: _Optional[int] = ..., deliveries: _Optional[int] = ..., last_trim_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., last_trim_rows: _Optional[int] = ..., log_path: _Optional[str] = ...) -> None: ...
