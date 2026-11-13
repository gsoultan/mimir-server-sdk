import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from mimirsdk._gen.mimir.v1 import model_pb2 as _model_pb2
from mimirsdk._gen.mimir.v1 import training_pb2 as _training_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Collection(_message.Message):
    __slots__ = ("id", "name", "api_name", "embedding_model_id", "embedding_model_name", "language_model_id", "language_model_name", "instructions", "documents", "passages", "bytes", "created_by", "create_time")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    API_NAME_FIELD_NUMBER: _ClassVar[int]
    EMBEDDING_MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    EMBEDDING_MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    INSTRUCTIONS_FIELD_NUMBER: _ClassVar[int]
    DOCUMENTS_FIELD_NUMBER: _ClassVar[int]
    PASSAGES_FIELD_NUMBER: _ClassVar[int]
    BYTES_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    CREATE_TIME_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    api_name: str
    embedding_model_id: str
    embedding_model_name: str
    language_model_id: str
    language_model_name: str
    instructions: str
    documents: int
    passages: int
    bytes: int
    created_by: str
    create_time: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., api_name: _Optional[str] = ..., embedding_model_id: _Optional[str] = ..., embedding_model_name: _Optional[str] = ..., language_model_id: _Optional[str] = ..., language_model_name: _Optional[str] = ..., instructions: _Optional[str] = ..., documents: _Optional[int] = ..., passages: _Optional[int] = ..., bytes: _Optional[int] = ..., created_by: _Optional[str] = ..., create_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Document(_message.Message):
    __slots__ = ("id", "collection_id", "name", "kind", "bytes", "status", "error", "passages", "created_by", "create_time", "end_time")
    ID_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    BYTES_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    PASSAGES_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    CREATE_TIME_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    id: str
    collection_id: str
    name: str
    kind: str
    bytes: int
    status: _training_pb2.JobStatus
    error: str
    passages: int
    created_by: str
    create_time: _timestamp_pb2.Timestamp
    end_time: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., collection_id: _Optional[str] = ..., name: _Optional[str] = ..., kind: _Optional[str] = ..., bytes: _Optional[int] = ..., status: _Optional[_Union[_training_pb2.JobStatus, str]] = ..., error: _Optional[str] = ..., passages: _Optional[int] = ..., created_by: _Optional[str] = ..., create_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., end_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Passage(_message.Message):
    __slots__ = ("id", "document_id", "document_name", "number", "text", "score")
    ID_FIELD_NUMBER: _ClassVar[int]
    DOCUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    DOCUMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    id: str
    document_id: str
    document_name: str
    number: int
    text: str
    score: float
    def __init__(self, id: _Optional[str] = ..., document_id: _Optional[str] = ..., document_name: _Optional[str] = ..., number: _Optional[int] = ..., text: _Optional[str] = ..., score: _Optional[float] = ...) -> None: ...

class ListCollectionsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListCollectionsResponse(_message.Message):
    __slots__ = ("collections",)
    COLLECTIONS_FIELD_NUMBER: _ClassVar[int]
    collections: _containers.RepeatedCompositeFieldContainer[Collection]
    def __init__(self, collections: _Optional[_Iterable[_Union[Collection, _Mapping]]] = ...) -> None: ...

class GetCollectionRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetCollectionResponse(_message.Message):
    __slots__ = ("collection", "documents")
    COLLECTION_FIELD_NUMBER: _ClassVar[int]
    DOCUMENTS_FIELD_NUMBER: _ClassVar[int]
    collection: Collection
    documents: _containers.RepeatedCompositeFieldContainer[Document]
    def __init__(self, collection: _Optional[_Union[Collection, _Mapping]] = ..., documents: _Optional[_Iterable[_Union[Document, _Mapping]]] = ...) -> None: ...

class CreateCollectionRequest(_message.Message):
    __slots__ = ("name", "embedding_model_id", "language_model_id", "instructions")
    NAME_FIELD_NUMBER: _ClassVar[int]
    EMBEDDING_MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    INSTRUCTIONS_FIELD_NUMBER: _ClassVar[int]
    name: str
    embedding_model_id: str
    language_model_id: str
    instructions: str
    def __init__(self, name: _Optional[str] = ..., embedding_model_id: _Optional[str] = ..., language_model_id: _Optional[str] = ..., instructions: _Optional[str] = ...) -> None: ...

class CreateCollectionResponse(_message.Message):
    __slots__ = ("collection",)
    COLLECTION_FIELD_NUMBER: _ClassVar[int]
    collection: Collection
    def __init__(self, collection: _Optional[_Union[Collection, _Mapping]] = ...) -> None: ...

class UpdateCollectionRequest(_message.Message):
    __slots__ = ("id", "name", "language_model_id", "instructions")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    INSTRUCTIONS_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    language_model_id: str
    instructions: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., language_model_id: _Optional[str] = ..., instructions: _Optional[str] = ...) -> None: ...

class UpdateCollectionResponse(_message.Message):
    __slots__ = ("collection",)
    COLLECTION_FIELD_NUMBER: _ClassVar[int]
    collection: Collection
    def __init__(self, collection: _Optional[_Union[Collection, _Mapping]] = ...) -> None: ...

class DeleteCollectionRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteCollectionResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AddDocumentRequest(_message.Message):
    __slots__ = ("collection_id", "name", "data")
    COLLECTION_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    collection_id: str
    name: str
    data: bytes
    def __init__(self, collection_id: _Optional[str] = ..., name: _Optional[str] = ..., data: _Optional[bytes] = ...) -> None: ...

class AddDocumentResponse(_message.Message):
    __slots__ = ("document",)
    DOCUMENT_FIELD_NUMBER: _ClassVar[int]
    document: Document
    def __init__(self, document: _Optional[_Union[Document, _Mapping]] = ...) -> None: ...

class GetDocumentRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetDocumentResponse(_message.Message):
    __slots__ = ("document",)
    DOCUMENT_FIELD_NUMBER: _ClassVar[int]
    document: Document
    def __init__(self, document: _Optional[_Union[Document, _Mapping]] = ...) -> None: ...

class DeleteDocumentRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteDocumentResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SearchRequest(_message.Message):
    __slots__ = ("collection_id", "query", "limit")
    COLLECTION_ID_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    collection_id: str
    query: str
    limit: int
    def __init__(self, collection_id: _Optional[str] = ..., query: _Optional[str] = ..., limit: _Optional[int] = ...) -> None: ...

class SearchResponse(_message.Message):
    __slots__ = ("passages",)
    PASSAGES_FIELD_NUMBER: _ClassVar[int]
    passages: _containers.RepeatedCompositeFieldContainer[Passage]
    def __init__(self, passages: _Optional[_Iterable[_Union[Passage, _Mapping]]] = ...) -> None: ...

class AskRequest(_message.Message):
    __slots__ = ("collection_id", "messages", "max_tokens", "temperature", "sources")
    COLLECTION_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGES_FIELD_NUMBER: _ClassVar[int]
    MAX_TOKENS_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    SOURCES_FIELD_NUMBER: _ClassVar[int]
    collection_id: str
    messages: _containers.RepeatedCompositeFieldContainer[_model_pb2.ChatMessage]
    max_tokens: int
    temperature: float
    sources: int
    def __init__(self, collection_id: _Optional[str] = ..., messages: _Optional[_Iterable[_Union[_model_pb2.ChatMessage, _Mapping]]] = ..., max_tokens: _Optional[int] = ..., temperature: _Optional[float] = ..., sources: _Optional[int] = ...) -> None: ...

class AskResponse(_message.Message):
    __slots__ = ("sources", "text", "done", "prompt_tokens", "generated_tokens", "finished", "duration_micros")
    SOURCES_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    DONE_FIELD_NUMBER: _ClassVar[int]
    PROMPT_TOKENS_FIELD_NUMBER: _ClassVar[int]
    GENERATED_TOKENS_FIELD_NUMBER: _ClassVar[int]
    FINISHED_FIELD_NUMBER: _ClassVar[int]
    DURATION_MICROS_FIELD_NUMBER: _ClassVar[int]
    sources: _containers.RepeatedCompositeFieldContainer[Passage]
    text: str
    done: bool
    prompt_tokens: int
    generated_tokens: int
    finished: bool
    duration_micros: int
    def __init__(self, sources: _Optional[_Iterable[_Union[Passage, _Mapping]]] = ..., text: _Optional[str] = ..., done: bool = ..., prompt_tokens: _Optional[int] = ..., generated_tokens: _Optional[int] = ..., finished: bool = ..., duration_micros: _Optional[int] = ...) -> None: ...
