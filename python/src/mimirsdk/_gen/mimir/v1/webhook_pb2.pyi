import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DeliveryStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DELIVERY_STATUS_UNSPECIFIED: _ClassVar[DeliveryStatus]
    DELIVERY_STATUS_PENDING: _ClassVar[DeliveryStatus]
    DELIVERY_STATUS_DELIVERED: _ClassVar[DeliveryStatus]
    DELIVERY_STATUS_FAILED: _ClassVar[DeliveryStatus]
DELIVERY_STATUS_UNSPECIFIED: DeliveryStatus
DELIVERY_STATUS_PENDING: DeliveryStatus
DELIVERY_STATUS_DELIVERED: DeliveryStatus
DELIVERY_STATUS_FAILED: DeliveryStatus

class Webhook(_message.Message):
    __slots__ = ("id", "name", "url", "events", "enabled", "create_time", "last_delivery")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    CREATE_TIME_FIELD_NUMBER: _ClassVar[int]
    LAST_DELIVERY_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    url: str
    events: _containers.RepeatedScalarFieldContainer[str]
    enabled: bool
    create_time: _timestamp_pb2.Timestamp
    last_delivery: Delivery
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., url: _Optional[str] = ..., events: _Optional[_Iterable[str]] = ..., enabled: bool = ..., create_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., last_delivery: _Optional[_Union[Delivery, _Mapping]] = ...) -> None: ...

class Delivery(_message.Message):
    __slots__ = ("id", "webhook_id", "event_type", "event_id", "status", "attempts", "response_code", "error", "create_time", "last_attempt_time", "next_attempt_time", "payload")
    ID_FIELD_NUMBER: _ClassVar[int]
    WEBHOOK_ID_FIELD_NUMBER: _ClassVar[int]
    EVENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    EVENT_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ATTEMPTS_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_CODE_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    CREATE_TIME_FIELD_NUMBER: _ClassVar[int]
    LAST_ATTEMPT_TIME_FIELD_NUMBER: _ClassVar[int]
    NEXT_ATTEMPT_TIME_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    id: str
    webhook_id: str
    event_type: str
    event_id: str
    status: DeliveryStatus
    attempts: int
    response_code: int
    error: str
    create_time: _timestamp_pb2.Timestamp
    last_attempt_time: _timestamp_pb2.Timestamp
    next_attempt_time: _timestamp_pb2.Timestamp
    payload: str
    def __init__(self, id: _Optional[str] = ..., webhook_id: _Optional[str] = ..., event_type: _Optional[str] = ..., event_id: _Optional[str] = ..., status: _Optional[_Union[DeliveryStatus, str]] = ..., attempts: _Optional[int] = ..., response_code: _Optional[int] = ..., error: _Optional[str] = ..., create_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., last_attempt_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., next_attempt_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., payload: _Optional[str] = ...) -> None: ...

class ListWebhooksRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListWebhooksResponse(_message.Message):
    __slots__ = ("webhooks", "event_types")
    WEBHOOKS_FIELD_NUMBER: _ClassVar[int]
    EVENT_TYPES_FIELD_NUMBER: _ClassVar[int]
    webhooks: _containers.RepeatedCompositeFieldContainer[Webhook]
    event_types: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, webhooks: _Optional[_Iterable[_Union[Webhook, _Mapping]]] = ..., event_types: _Optional[_Iterable[str]] = ...) -> None: ...

class CreateWebhookRequest(_message.Message):
    __slots__ = ("name", "url", "events")
    NAME_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    name: str
    url: str
    events: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, name: _Optional[str] = ..., url: _Optional[str] = ..., events: _Optional[_Iterable[str]] = ...) -> None: ...

class CreateWebhookResponse(_message.Message):
    __slots__ = ("webhook", "secret")
    WEBHOOK_FIELD_NUMBER: _ClassVar[int]
    SECRET_FIELD_NUMBER: _ClassVar[int]
    webhook: Webhook
    secret: str
    def __init__(self, webhook: _Optional[_Union[Webhook, _Mapping]] = ..., secret: _Optional[str] = ...) -> None: ...

class UpdateWebhookRequest(_message.Message):
    __slots__ = ("id", "name", "url", "events", "enabled")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    url: str
    events: _containers.RepeatedScalarFieldContainer[str]
    enabled: bool
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., url: _Optional[str] = ..., events: _Optional[_Iterable[str]] = ..., enabled: bool = ...) -> None: ...

class UpdateWebhookResponse(_message.Message):
    __slots__ = ("webhook",)
    WEBHOOK_FIELD_NUMBER: _ClassVar[int]
    webhook: Webhook
    def __init__(self, webhook: _Optional[_Union[Webhook, _Mapping]] = ...) -> None: ...

class DeleteWebhookRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteWebhookResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SendTestEventRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class SendTestEventResponse(_message.Message):
    __slots__ = ("delivery",)
    DELIVERY_FIELD_NUMBER: _ClassVar[int]
    delivery: Delivery
    def __init__(self, delivery: _Optional[_Union[Delivery, _Mapping]] = ...) -> None: ...

class ListDeliveriesRequest(_message.Message):
    __slots__ = ("webhook_id", "page_size", "page_token")
    WEBHOOK_ID_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    webhook_id: str
    page_size: int
    page_token: str
    def __init__(self, webhook_id: _Optional[str] = ..., page_size: _Optional[int] = ..., page_token: _Optional[str] = ...) -> None: ...

class ListDeliveriesResponse(_message.Message):
    __slots__ = ("deliveries", "next_page_token")
    DELIVERIES_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    deliveries: _containers.RepeatedCompositeFieldContainer[Delivery]
    next_page_token: str
    def __init__(self, deliveries: _Optional[_Iterable[_Union[Delivery, _Mapping]]] = ..., next_page_token: _Optional[str] = ...) -> None: ...

class RedeliverRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class RedeliverResponse(_message.Message):
    __slots__ = ("delivery",)
    DELIVERY_FIELD_NUMBER: _ClassVar[int]
    delivery: Delivery
    def __init__(self, delivery: _Optional[_Union[Delivery, _Mapping]] = ...) -> None: ...
