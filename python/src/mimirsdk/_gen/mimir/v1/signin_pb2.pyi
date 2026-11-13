from mimirsdk._gen.mimir.v1 import access_pb2 as _access_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SignInKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SIGN_IN_KIND_UNSPECIFIED: _ClassVar[SignInKind]
    SIGN_IN_KIND_GOOGLE: _ClassVar[SignInKind]
    SIGN_IN_KIND_GITHUB: _ClassVar[SignInKind]
    SIGN_IN_KIND_OIDC: _ClassVar[SignInKind]
SIGN_IN_KIND_UNSPECIFIED: SignInKind
SIGN_IN_KIND_GOOGLE: SignInKind
SIGN_IN_KIND_GITHUB: SignInKind
SIGN_IN_KIND_OIDC: SignInKind

class SignInOption(_message.Message):
    __slots__ = ("id", "name", "kind")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    kind: SignInKind
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., kind: _Optional[_Union[SignInKind, str]] = ...) -> None: ...

class SignInProvider(_message.Message):
    __slots__ = ("id", "kind", "name", "enabled", "issuer", "client_id", "client_secret", "client_secret_set", "groups_claim", "trust_emails", "rules")
    ID_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    ISSUER_FIELD_NUMBER: _ClassVar[int]
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_SECRET_FIELD_NUMBER: _ClassVar[int]
    CLIENT_SECRET_SET_FIELD_NUMBER: _ClassVar[int]
    GROUPS_CLAIM_FIELD_NUMBER: _ClassVar[int]
    TRUST_EMAILS_FIELD_NUMBER: _ClassVar[int]
    RULES_FIELD_NUMBER: _ClassVar[int]
    id: str
    kind: SignInKind
    name: str
    enabled: bool
    issuer: str
    client_id: str
    client_secret: str
    client_secret_set: bool
    groups_claim: str
    trust_emails: bool
    rules: _containers.RepeatedCompositeFieldContainer[SignInRule]
    def __init__(self, id: _Optional[str] = ..., kind: _Optional[_Union[SignInKind, str]] = ..., name: _Optional[str] = ..., enabled: bool = ..., issuer: _Optional[str] = ..., client_id: _Optional[str] = ..., client_secret: _Optional[str] = ..., client_secret_set: bool = ..., groups_claim: _Optional[str] = ..., trust_emails: bool = ..., rules: _Optional[_Iterable[_Union[SignInRule, _Mapping]]] = ...) -> None: ...

class SignInRule(_message.Message):
    __slots__ = ("domain", "group", "team_id", "role", "team_name")
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    TEAM_NAME_FIELD_NUMBER: _ClassVar[int]
    domain: str
    group: str
    team_id: str
    role: _access_pb2.Role
    team_name: str
    def __init__(self, domain: _Optional[str] = ..., group: _Optional[str] = ..., team_id: _Optional[str] = ..., role: _Optional[_Union[_access_pb2.Role, str]] = ..., team_name: _Optional[str] = ...) -> None: ...

class ListSignInOptionsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListSignInOptionsResponse(_message.Message):
    __slots__ = ("options",)
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    options: _containers.RepeatedCompositeFieldContainer[SignInOption]
    def __init__(self, options: _Optional[_Iterable[_Union[SignInOption, _Mapping]]] = ...) -> None: ...

class ListSignInProvidersRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListSignInProvidersResponse(_message.Message):
    __slots__ = ("providers",)
    PROVIDERS_FIELD_NUMBER: _ClassVar[int]
    providers: _containers.RepeatedCompositeFieldContainer[SignInProvider]
    def __init__(self, providers: _Optional[_Iterable[_Union[SignInProvider, _Mapping]]] = ...) -> None: ...

class SaveSignInProviderRequest(_message.Message):
    __slots__ = ("provider",)
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    provider: SignInProvider
    def __init__(self, provider: _Optional[_Union[SignInProvider, _Mapping]] = ...) -> None: ...

class SaveSignInProviderResponse(_message.Message):
    __slots__ = ("provider",)
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    provider: SignInProvider
    def __init__(self, provider: _Optional[_Union[SignInProvider, _Mapping]] = ...) -> None: ...

class DeleteSignInProviderRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteSignInProviderResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
