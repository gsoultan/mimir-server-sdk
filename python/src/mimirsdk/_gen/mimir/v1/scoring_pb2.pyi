import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from mimirsdk._gen.mimir.v1 import training_pb2 as _training_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Scoring(_message.Message):
    __slots__ = ("id", "name", "model_id", "model_name", "source", "source_detail", "dataset_id", "status", "error", "rows", "done", "failed", "columns", "result_bytes", "created_by", "create_time", "start_time", "end_time", "repeat_seconds", "next_run_time", "runs", "model_version_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_DETAIL_FIELD_NUMBER: _ClassVar[int]
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    ROWS_FIELD_NUMBER: _ClassVar[int]
    DONE_FIELD_NUMBER: _ClassVar[int]
    FAILED_FIELD_NUMBER: _ClassVar[int]
    COLUMNS_FIELD_NUMBER: _ClassVar[int]
    RESULT_BYTES_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    CREATE_TIME_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    REPEAT_SECONDS_FIELD_NUMBER: _ClassVar[int]
    NEXT_RUN_TIME_FIELD_NUMBER: _ClassVar[int]
    RUNS_FIELD_NUMBER: _ClassVar[int]
    MODEL_VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    model_id: str
    model_name: str
    source: str
    source_detail: str
    dataset_id: str
    status: _training_pb2.JobStatus
    error: str
    rows: int
    done: int
    failed: int
    columns: _containers.RepeatedScalarFieldContainer[str]
    result_bytes: int
    created_by: str
    create_time: _timestamp_pb2.Timestamp
    start_time: _timestamp_pb2.Timestamp
    end_time: _timestamp_pb2.Timestamp
    repeat_seconds: int
    next_run_time: _timestamp_pb2.Timestamp
    runs: int
    model_version_id: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., model_id: _Optional[str] = ..., model_name: _Optional[str] = ..., source: _Optional[str] = ..., source_detail: _Optional[str] = ..., dataset_id: _Optional[str] = ..., status: _Optional[_Union[_training_pb2.JobStatus, str]] = ..., error: _Optional[str] = ..., rows: _Optional[int] = ..., done: _Optional[int] = ..., failed: _Optional[int] = ..., columns: _Optional[_Iterable[str]] = ..., result_bytes: _Optional[int] = ..., created_by: _Optional[str] = ..., create_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., start_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., end_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., repeat_seconds: _Optional[int] = ..., next_run_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., runs: _Optional[int] = ..., model_version_id: _Optional[str] = ...) -> None: ...

class ListScoringsRequest(_message.Message):
    __slots__ = ("model_id",)
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    model_id: str
    def __init__(self, model_id: _Optional[str] = ...) -> None: ...

class ListScoringsResponse(_message.Message):
    __slots__ = ("scorings",)
    SCORINGS_FIELD_NUMBER: _ClassVar[int]
    scorings: _containers.RepeatedCompositeFieldContainer[Scoring]
    def __init__(self, scorings: _Optional[_Iterable[_Union[Scoring, _Mapping]]] = ...) -> None: ...

class GetScoringRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetScoringResponse(_message.Message):
    __slots__ = ("scoring", "sample")
    SCORING_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_FIELD_NUMBER: _ClassVar[int]
    scoring: Scoring
    sample: _containers.RepeatedCompositeFieldContainer[_training_pb2.Row]
    def __init__(self, scoring: _Optional[_Union[Scoring, _Mapping]] = ..., sample: _Optional[_Iterable[_Union[_training_pb2.Row, _Mapping]]] = ...) -> None: ...

class CreateScoringRequest(_message.Message):
    __slots__ = ("name", "model_id", "csv", "connection", "query", "bucket", "path", "dataset_id", "repeat_seconds")
    NAME_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    CSV_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    BUCKET_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    REPEAT_SECONDS_FIELD_NUMBER: _ClassVar[int]
    name: str
    model_id: str
    csv: bytes
    connection: _training_pb2.Connection
    query: str
    bucket: _training_pb2.Bucket
    path: str
    dataset_id: str
    repeat_seconds: int
    def __init__(self, name: _Optional[str] = ..., model_id: _Optional[str] = ..., csv: _Optional[bytes] = ..., connection: _Optional[_Union[_training_pb2.Connection, _Mapping]] = ..., query: _Optional[str] = ..., bucket: _Optional[_Union[_training_pb2.Bucket, _Mapping]] = ..., path: _Optional[str] = ..., dataset_id: _Optional[str] = ..., repeat_seconds: _Optional[int] = ...) -> None: ...

class CreateScoringResponse(_message.Message):
    __slots__ = ("scoring",)
    SCORING_FIELD_NUMBER: _ClassVar[int]
    scoring: Scoring
    def __init__(self, scoring: _Optional[_Union[Scoring, _Mapping]] = ...) -> None: ...

class RunScoringRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class RunScoringResponse(_message.Message):
    __slots__ = ("scoring",)
    SCORING_FIELD_NUMBER: _ClassVar[int]
    scoring: Scoring
    def __init__(self, scoring: _Optional[_Union[Scoring, _Mapping]] = ...) -> None: ...

class CancelScoringRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class CancelScoringResponse(_message.Message):
    __slots__ = ("scoring",)
    SCORING_FIELD_NUMBER: _ClassVar[int]
    scoring: Scoring
    def __init__(self, scoring: _Optional[_Union[Scoring, _Mapping]] = ...) -> None: ...

class SetScoringRepeatRequest(_message.Message):
    __slots__ = ("id", "repeat_seconds")
    ID_FIELD_NUMBER: _ClassVar[int]
    REPEAT_SECONDS_FIELD_NUMBER: _ClassVar[int]
    id: str
    repeat_seconds: int
    def __init__(self, id: _Optional[str] = ..., repeat_seconds: _Optional[int] = ...) -> None: ...

class SetScoringRepeatResponse(_message.Message):
    __slots__ = ("scoring",)
    SCORING_FIELD_NUMBER: _ClassVar[int]
    scoring: Scoring
    def __init__(self, scoring: _Optional[_Union[Scoring, _Mapping]] = ...) -> None: ...

class DeleteScoringRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteScoringResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
