import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from mimirsdk._gen.mimir.v1 import training_pb2 as _training_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Benchmark(_message.Message):
    __slots__ = ("id", "name", "description", "dataset_id", "dataset_name", "target", "kind", "rows", "created_by", "create_time", "metric", "lower_is_better", "scored", "leader_name", "leader_headline")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    DATASET_NAME_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    ROWS_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    CREATE_TIME_FIELD_NUMBER: _ClassVar[int]
    METRIC_FIELD_NUMBER: _ClassVar[int]
    LOWER_IS_BETTER_FIELD_NUMBER: _ClassVar[int]
    SCORED_FIELD_NUMBER: _ClassVar[int]
    LEADER_NAME_FIELD_NUMBER: _ClassVar[int]
    LEADER_HEADLINE_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    dataset_id: str
    dataset_name: str
    target: str
    kind: str
    rows: int
    created_by: str
    create_time: _timestamp_pb2.Timestamp
    metric: str
    lower_is_better: bool
    scored: int
    leader_name: str
    leader_headline: float
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., dataset_id: _Optional[str] = ..., dataset_name: _Optional[str] = ..., target: _Optional[str] = ..., kind: _Optional[str] = ..., rows: _Optional[int] = ..., created_by: _Optional[str] = ..., create_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., metric: _Optional[str] = ..., lower_is_better: bool = ..., scored: _Optional[int] = ..., leader_name: _Optional[str] = ..., leader_headline: _Optional[float] = ...) -> None: ...

class BenchmarkScore(_message.Message):
    __slots__ = ("model_id", "model_name", "architecture", "status", "error", "report", "headline", "scored_time", "rank", "stale")
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    ARCHITECTURE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    REPORT_FIELD_NUMBER: _ClassVar[int]
    HEADLINE_FIELD_NUMBER: _ClassVar[int]
    SCORED_TIME_FIELD_NUMBER: _ClassVar[int]
    RANK_FIELD_NUMBER: _ClassVar[int]
    STALE_FIELD_NUMBER: _ClassVar[int]
    model_id: str
    model_name: str
    architecture: str
    status: _training_pb2.JobStatus
    error: str
    report: _training_pb2.RunReport
    headline: float
    scored_time: _timestamp_pb2.Timestamp
    rank: int
    stale: bool
    def __init__(self, model_id: _Optional[str] = ..., model_name: _Optional[str] = ..., architecture: _Optional[str] = ..., status: _Optional[_Union[_training_pb2.JobStatus, str]] = ..., error: _Optional[str] = ..., report: _Optional[_Union[_training_pb2.RunReport, _Mapping]] = ..., headline: _Optional[float] = ..., scored_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., rank: _Optional[int] = ..., stale: bool = ...) -> None: ...

class Candidate(_message.Message):
    __slots__ = ("model_id", "model_name", "architecture")
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    ARCHITECTURE_FIELD_NUMBER: _ClassVar[int]
    model_id: str
    model_name: str
    architecture: str
    def __init__(self, model_id: _Optional[str] = ..., model_name: _Optional[str] = ..., architecture: _Optional[str] = ...) -> None: ...

class ListBenchmarksRequest(_message.Message):
    __slots__ = ("dataset_id",)
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    dataset_id: str
    def __init__(self, dataset_id: _Optional[str] = ...) -> None: ...

class ListBenchmarksResponse(_message.Message):
    __slots__ = ("benchmarks",)
    BENCHMARKS_FIELD_NUMBER: _ClassVar[int]
    benchmarks: _containers.RepeatedCompositeFieldContainer[Benchmark]
    def __init__(self, benchmarks: _Optional[_Iterable[_Union[Benchmark, _Mapping]]] = ...) -> None: ...

class GetBenchmarkRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetBenchmarkResponse(_message.Message):
    __slots__ = ("benchmark", "scores", "candidates")
    BENCHMARK_FIELD_NUMBER: _ClassVar[int]
    SCORES_FIELD_NUMBER: _ClassVar[int]
    CANDIDATES_FIELD_NUMBER: _ClassVar[int]
    benchmark: Benchmark
    scores: _containers.RepeatedCompositeFieldContainer[BenchmarkScore]
    candidates: _containers.RepeatedCompositeFieldContainer[Candidate]
    def __init__(self, benchmark: _Optional[_Union[Benchmark, _Mapping]] = ..., scores: _Optional[_Iterable[_Union[BenchmarkScore, _Mapping]]] = ..., candidates: _Optional[_Iterable[_Union[Candidate, _Mapping]]] = ...) -> None: ...

class CreateBenchmarkRequest(_message.Message):
    __slots__ = ("name", "description", "dataset_id", "share", "csv")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    SHARE_FIELD_NUMBER: _ClassVar[int]
    CSV_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    dataset_id: str
    share: float
    csv: bytes
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., dataset_id: _Optional[str] = ..., share: _Optional[float] = ..., csv: _Optional[bytes] = ...) -> None: ...

class CreateBenchmarkResponse(_message.Message):
    __slots__ = ("benchmark",)
    BENCHMARK_FIELD_NUMBER: _ClassVar[int]
    benchmark: Benchmark
    def __init__(self, benchmark: _Optional[_Union[Benchmark, _Mapping]] = ...) -> None: ...

class DeleteBenchmarkRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteBenchmarkResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ScoreModelsRequest(_message.Message):
    __slots__ = ("benchmark_id", "model_ids")
    BENCHMARK_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_IDS_FIELD_NUMBER: _ClassVar[int]
    benchmark_id: str
    model_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, benchmark_id: _Optional[str] = ..., model_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class ScoreModelsResponse(_message.Message):
    __slots__ = ("scores",)
    SCORES_FIELD_NUMBER: _ClassVar[int]
    scores: _containers.RepeatedCompositeFieldContainer[BenchmarkScore]
    def __init__(self, scores: _Optional[_Iterable[_Union[BenchmarkScore, _Mapping]]] = ...) -> None: ...
