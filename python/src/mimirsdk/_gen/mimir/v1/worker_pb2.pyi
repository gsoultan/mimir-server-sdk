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

class Worker(_message.Message):
    __slots__ = ("id", "name", "online", "last_seen", "create_time", "device", "cpus", "memory_bytes", "architectures", "trains", "capacity", "busy", "version", "address", "created_by", "stats", "connect_time", "key_fingerprint", "security", "tls_version", "models", "waiting", "training_only", "tasks", "gpus")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ONLINE_FIELD_NUMBER: _ClassVar[int]
    LAST_SEEN_FIELD_NUMBER: _ClassVar[int]
    CREATE_TIME_FIELD_NUMBER: _ClassVar[int]
    DEVICE_FIELD_NUMBER: _ClassVar[int]
    CPUS_FIELD_NUMBER: _ClassVar[int]
    MEMORY_BYTES_FIELD_NUMBER: _ClassVar[int]
    ARCHITECTURES_FIELD_NUMBER: _ClassVar[int]
    TRAINS_FIELD_NUMBER: _ClassVar[int]
    CAPACITY_FIELD_NUMBER: _ClassVar[int]
    BUSY_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    STATS_FIELD_NUMBER: _ClassVar[int]
    CONNECT_TIME_FIELD_NUMBER: _ClassVar[int]
    KEY_FINGERPRINT_FIELD_NUMBER: _ClassVar[int]
    SECURITY_FIELD_NUMBER: _ClassVar[int]
    TLS_VERSION_FIELD_NUMBER: _ClassVar[int]
    MODELS_FIELD_NUMBER: _ClassVar[int]
    WAITING_FIELD_NUMBER: _ClassVar[int]
    TRAINING_ONLY_FIELD_NUMBER: _ClassVar[int]
    TASKS_FIELD_NUMBER: _ClassVar[int]
    GPUS_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    online: bool
    last_seen: _timestamp_pb2.Timestamp
    create_time: _timestamp_pb2.Timestamp
    device: str
    cpus: int
    memory_bytes: int
    architectures: _containers.RepeatedScalarFieldContainer[str]
    trains: bool
    capacity: int
    busy: int
    version: str
    address: str
    created_by: str
    stats: Stats
    connect_time: _timestamp_pb2.Timestamp
    key_fingerprint: str
    security: str
    tls_version: str
    models: int
    waiting: int
    training_only: bool
    tasks: str
    gpus: int
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., online: bool = ..., last_seen: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., create_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., device: _Optional[str] = ..., cpus: _Optional[int] = ..., memory_bytes: _Optional[int] = ..., architectures: _Optional[_Iterable[str]] = ..., trains: bool = ..., capacity: _Optional[int] = ..., busy: _Optional[int] = ..., version: _Optional[str] = ..., address: _Optional[str] = ..., created_by: _Optional[str] = ..., stats: _Optional[_Union[Stats, _Mapping]] = ..., connect_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., key_fingerprint: _Optional[str] = ..., security: _Optional[str] = ..., tls_version: _Optional[str] = ..., models: _Optional[int] = ..., waiting: _Optional[int] = ..., training_only: bool = ..., tasks: _Optional[str] = ..., gpus: _Optional[int] = ...) -> None: ...

class Stats(_message.Message):
    __slots__ = ("cpu_percent", "memory_used_bytes", "memory_total_bytes", "disk_used_bytes", "disk_total_bytes", "uptime_seconds", "load_average", "memory_pressure", "memory_budget_bytes")
    CPU_PERCENT_FIELD_NUMBER: _ClassVar[int]
    MEMORY_USED_BYTES_FIELD_NUMBER: _ClassVar[int]
    MEMORY_TOTAL_BYTES_FIELD_NUMBER: _ClassVar[int]
    DISK_USED_BYTES_FIELD_NUMBER: _ClassVar[int]
    DISK_TOTAL_BYTES_FIELD_NUMBER: _ClassVar[int]
    UPTIME_SECONDS_FIELD_NUMBER: _ClassVar[int]
    LOAD_AVERAGE_FIELD_NUMBER: _ClassVar[int]
    MEMORY_PRESSURE_FIELD_NUMBER: _ClassVar[int]
    MEMORY_BUDGET_BYTES_FIELD_NUMBER: _ClassVar[int]
    cpu_percent: float
    memory_used_bytes: int
    memory_total_bytes: int
    disk_used_bytes: int
    disk_total_bytes: int
    uptime_seconds: int
    load_average: float
    memory_pressure: int
    memory_budget_bytes: int
    def __init__(self, cpu_percent: _Optional[float] = ..., memory_used_bytes: _Optional[int] = ..., memory_total_bytes: _Optional[int] = ..., disk_used_bytes: _Optional[int] = ..., disk_total_bytes: _Optional[int] = ..., uptime_seconds: _Optional[int] = ..., load_average: _Optional[float] = ..., memory_pressure: _Optional[int] = ..., memory_budget_bytes: _Optional[int] = ...) -> None: ...

class WorkerSample(_message.Message):
    __slots__ = ("time", "cpu_percent", "memory_used_bytes", "memory_total_bytes", "disk_used_bytes", "disk_total_bytes", "busy", "capacity")
    TIME_FIELD_NUMBER: _ClassVar[int]
    CPU_PERCENT_FIELD_NUMBER: _ClassVar[int]
    MEMORY_USED_BYTES_FIELD_NUMBER: _ClassVar[int]
    MEMORY_TOTAL_BYTES_FIELD_NUMBER: _ClassVar[int]
    DISK_USED_BYTES_FIELD_NUMBER: _ClassVar[int]
    DISK_TOTAL_BYTES_FIELD_NUMBER: _ClassVar[int]
    BUSY_FIELD_NUMBER: _ClassVar[int]
    CAPACITY_FIELD_NUMBER: _ClassVar[int]
    time: _timestamp_pb2.Timestamp
    cpu_percent: float
    memory_used_bytes: int
    memory_total_bytes: int
    disk_used_bytes: int
    disk_total_bytes: int
    busy: int
    capacity: int
    def __init__(self, time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., cpu_percent: _Optional[float] = ..., memory_used_bytes: _Optional[int] = ..., memory_total_bytes: _Optional[int] = ..., disk_used_bytes: _Optional[int] = ..., disk_total_bytes: _Optional[int] = ..., busy: _Optional[int] = ..., capacity: _Optional[int] = ...) -> None: ...

class WorkerTask(_message.Message):
    __slots__ = ("kind", "model_id", "model_name", "job_id", "job_name", "start_time", "count")
    KIND_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    JOB_NAME_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    kind: str
    model_id: str
    model_name: str
    job_id: str
    job_name: str
    start_time: _timestamp_pb2.Timestamp
    count: int
    def __init__(self, kind: _Optional[str] = ..., model_id: _Optional[str] = ..., model_name: _Optional[str] = ..., job_id: _Optional[str] = ..., job_name: _Optional[str] = ..., start_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., count: _Optional[int] = ...) -> None: ...

class WorkerItem(_message.Message):
    __slots__ = ("id", "name", "status", "time")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    status: str
    time: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., status: _Optional[str] = ..., time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class GetWorkerRequest(_message.Message):
    __slots__ = ("id", "hours")
    ID_FIELD_NUMBER: _ClassVar[int]
    HOURS_FIELD_NUMBER: _ClassVar[int]
    id: str
    hours: int
    def __init__(self, id: _Optional[str] = ..., hours: _Optional[int] = ...) -> None: ...

class GetWorkerResponse(_message.Message):
    __slots__ = ("worker", "samples", "tasks", "models", "runs", "events")
    WORKER_FIELD_NUMBER: _ClassVar[int]
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    TASKS_FIELD_NUMBER: _ClassVar[int]
    MODELS_FIELD_NUMBER: _ClassVar[int]
    RUNS_FIELD_NUMBER: _ClassVar[int]
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    worker: Worker
    samples: _containers.RepeatedCompositeFieldContainer[WorkerSample]
    tasks: _containers.RepeatedCompositeFieldContainer[WorkerTask]
    models: _containers.RepeatedCompositeFieldContainer[WorkerItem]
    runs: _containers.RepeatedCompositeFieldContainer[WorkerItem]
    events: _containers.RepeatedCompositeFieldContainer[WorkerItem]
    def __init__(self, worker: _Optional[_Union[Worker, _Mapping]] = ..., samples: _Optional[_Iterable[_Union[WorkerSample, _Mapping]]] = ..., tasks: _Optional[_Iterable[_Union[WorkerTask, _Mapping]]] = ..., models: _Optional[_Iterable[_Union[WorkerItem, _Mapping]]] = ..., runs: _Optional[_Iterable[_Union[WorkerItem, _Mapping]]] = ..., events: _Optional[_Iterable[_Union[WorkerItem, _Mapping]]] = ...) -> None: ...

class ReplaceWorkerTokenRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class ReplaceWorkerTokenResponse(_message.Message):
    __slots__ = ("token",)
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    token: str
    def __init__(self, token: _Optional[str] = ...) -> None: ...

class SetWorkerTasksRequest(_message.Message):
    __slots__ = ("id", "tasks")
    ID_FIELD_NUMBER: _ClassVar[int]
    TASKS_FIELD_NUMBER: _ClassVar[int]
    id: str
    tasks: str
    def __init__(self, id: _Optional[str] = ..., tasks: _Optional[str] = ...) -> None: ...

class SetWorkerTasksResponse(_message.Message):
    __slots__ = ("worker",)
    WORKER_FIELD_NUMBER: _ClassVar[int]
    worker: Worker
    def __init__(self, worker: _Optional[_Union[Worker, _Mapping]] = ...) -> None: ...

class ListWorkerChoicesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListWorkerChoicesResponse(_message.Message):
    __slots__ = ("workers",)
    WORKERS_FIELD_NUMBER: _ClassVar[int]
    workers: _containers.RepeatedCompositeFieldContainer[Worker]
    def __init__(self, workers: _Optional[_Iterable[_Union[Worker, _Mapping]]] = ...) -> None: ...

class ListWorkersRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListWorkersResponse(_message.Message):
    __slots__ = ("workers", "secure_join")
    WORKERS_FIELD_NUMBER: _ClassVar[int]
    SECURE_JOIN_FIELD_NUMBER: _ClassVar[int]
    workers: _containers.RepeatedCompositeFieldContainer[Worker]
    secure_join: bool
    def __init__(self, workers: _Optional[_Iterable[_Union[Worker, _Mapping]]] = ..., secure_join: bool = ...) -> None: ...

class CreateWorkerRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class CreateWorkerResponse(_message.Message):
    __slots__ = ("worker", "token")
    WORKER_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    worker: Worker
    token: str
    def __init__(self, worker: _Optional[_Union[Worker, _Mapping]] = ..., token: _Optional[str] = ...) -> None: ...

class DeleteWorkerRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteWorkerResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class LinkRequest(_message.Message):
    __slots__ = ("hello", "predict_result", "train_progress", "train_result", "heartbeat", "proof", "load_result", "group_share")
    HELLO_FIELD_NUMBER: _ClassVar[int]
    PREDICT_RESULT_FIELD_NUMBER: _ClassVar[int]
    TRAIN_PROGRESS_FIELD_NUMBER: _ClassVar[int]
    TRAIN_RESULT_FIELD_NUMBER: _ClassVar[int]
    HEARTBEAT_FIELD_NUMBER: _ClassVar[int]
    PROOF_FIELD_NUMBER: _ClassVar[int]
    LOAD_RESULT_FIELD_NUMBER: _ClassVar[int]
    GROUP_SHARE_FIELD_NUMBER: _ClassVar[int]
    hello: Hello
    predict_result: PredictResult
    train_progress: TrainProgress
    train_result: TrainResult
    heartbeat: Heartbeat
    proof: Proof
    load_result: LoadResult
    group_share: GroupShare
    def __init__(self, hello: _Optional[_Union[Hello, _Mapping]] = ..., predict_result: _Optional[_Union[PredictResult, _Mapping]] = ..., train_progress: _Optional[_Union[TrainProgress, _Mapping]] = ..., train_result: _Optional[_Union[TrainResult, _Mapping]] = ..., heartbeat: _Optional[_Union[Heartbeat, _Mapping]] = ..., proof: _Optional[_Union[Proof, _Mapping]] = ..., load_result: _Optional[_Union[LoadResult, _Mapping]] = ..., group_share: _Optional[_Union[GroupShare, _Mapping]] = ...) -> None: ...

class LinkResponse(_message.Message):
    __slots__ = ("welcome", "predict", "train", "cancel", "challenge", "load", "group_mean", "forget")
    WELCOME_FIELD_NUMBER: _ClassVar[int]
    PREDICT_FIELD_NUMBER: _ClassVar[int]
    TRAIN_FIELD_NUMBER: _ClassVar[int]
    CANCEL_FIELD_NUMBER: _ClassVar[int]
    CHALLENGE_FIELD_NUMBER: _ClassVar[int]
    LOAD_FIELD_NUMBER: _ClassVar[int]
    GROUP_MEAN_FIELD_NUMBER: _ClassVar[int]
    FORGET_FIELD_NUMBER: _ClassVar[int]
    welcome: Welcome
    predict: PredictTask
    train: TrainTask
    cancel: CancelTask
    challenge: Challenge
    load: LoadTask
    group_mean: GroupMean
    forget: ForgetModel
    def __init__(self, welcome: _Optional[_Union[Welcome, _Mapping]] = ..., predict: _Optional[_Union[PredictTask, _Mapping]] = ..., train: _Optional[_Union[TrainTask, _Mapping]] = ..., cancel: _Optional[_Union[CancelTask, _Mapping]] = ..., challenge: _Optional[_Union[Challenge, _Mapping]] = ..., load: _Optional[_Union[LoadTask, _Mapping]] = ..., group_mean: _Optional[_Union[GroupMean, _Mapping]] = ..., forget: _Optional[_Union[ForgetModel, _Mapping]] = ...) -> None: ...

class LoadTask(_message.Message):
    __slots__ = ("task_id", "model_id", "architecture", "spec", "weights")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    ARCHITECTURE_FIELD_NUMBER: _ClassVar[int]
    SPEC_FIELD_NUMBER: _ClassVar[int]
    WEIGHTS_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    model_id: str
    architecture: str
    spec: ModelSpec
    weights: bytes
    def __init__(self, task_id: _Optional[str] = ..., model_id: _Optional[str] = ..., architecture: _Optional[str] = ..., spec: _Optional[_Union[ModelSpec, _Mapping]] = ..., weights: _Optional[bytes] = ...) -> None: ...

class LoadResult(_message.Message):
    __slots__ = ("task_id", "error")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    error: str
    def __init__(self, task_id: _Optional[str] = ..., error: _Optional[str] = ...) -> None: ...

class ForgetModel(_message.Message):
    __slots__ = ("model_id",)
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    model_id: str
    def __init__(self, model_id: _Optional[str] = ...) -> None: ...

class Challenge(_message.Message):
    __slots__ = ("nonce",)
    NONCE_FIELD_NUMBER: _ClassVar[int]
    nonce: bytes
    def __init__(self, nonce: _Optional[bytes] = ...) -> None: ...

class Proof(_message.Message):
    __slots__ = ("signature",)
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    signature: bytes
    def __init__(self, signature: _Optional[bytes] = ...) -> None: ...

class Hello(_message.Message):
    __slots__ = ("device", "cpus", "memory_bytes", "architectures", "trains", "capacity", "version", "public_key", "stats", "training_only", "group_architectures", "gpus")
    DEVICE_FIELD_NUMBER: _ClassVar[int]
    CPUS_FIELD_NUMBER: _ClassVar[int]
    MEMORY_BYTES_FIELD_NUMBER: _ClassVar[int]
    ARCHITECTURES_FIELD_NUMBER: _ClassVar[int]
    TRAINS_FIELD_NUMBER: _ClassVar[int]
    CAPACITY_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    STATS_FIELD_NUMBER: _ClassVar[int]
    TRAINING_ONLY_FIELD_NUMBER: _ClassVar[int]
    GROUP_ARCHITECTURES_FIELD_NUMBER: _ClassVar[int]
    GPUS_FIELD_NUMBER: _ClassVar[int]
    device: str
    cpus: int
    memory_bytes: int
    architectures: _containers.RepeatedScalarFieldContainer[str]
    trains: bool
    capacity: int
    version: str
    public_key: bytes
    stats: Stats
    training_only: bool
    group_architectures: _containers.RepeatedScalarFieldContainer[str]
    gpus: int
    def __init__(self, device: _Optional[str] = ..., cpus: _Optional[int] = ..., memory_bytes: _Optional[int] = ..., architectures: _Optional[_Iterable[str]] = ..., trains: bool = ..., capacity: _Optional[int] = ..., version: _Optional[str] = ..., public_key: _Optional[bytes] = ..., stats: _Optional[_Union[Stats, _Mapping]] = ..., training_only: bool = ..., group_architectures: _Optional[_Iterable[str]] = ..., gpus: _Optional[int] = ...) -> None: ...

class Heartbeat(_message.Message):
    __slots__ = ("stats",)
    STATS_FIELD_NUMBER: _ClassVar[int]
    stats: Stats
    def __init__(self, stats: _Optional[_Union[Stats, _Mapping]] = ...) -> None: ...

class Welcome(_message.Message):
    __slots__ = ("worker_id", "name", "tasks")
    WORKER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TASKS_FIELD_NUMBER: _ClassVar[int]
    worker_id: str
    name: str
    tasks: str
    def __init__(self, worker_id: _Optional[str] = ..., name: _Optional[str] = ..., tasks: _Optional[str] = ...) -> None: ...

class ModelSpec(_message.Message):
    __slots__ = ("input_shape", "labels", "features", "columns")
    INPUT_SHAPE_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    FEATURES_FIELD_NUMBER: _ClassVar[int]
    COLUMNS_FIELD_NUMBER: _ClassVar[int]
    input_shape: _containers.RepeatedScalarFieldContainer[int]
    labels: _containers.RepeatedScalarFieldContainer[str]
    features: _containers.RepeatedScalarFieldContainer[str]
    columns: _containers.RepeatedCompositeFieldContainer[_model_pb2.Column]
    def __init__(self, input_shape: _Optional[_Iterable[int]] = ..., labels: _Optional[_Iterable[str]] = ..., features: _Optional[_Iterable[str]] = ..., columns: _Optional[_Iterable[_Union[_model_pb2.Column, _Mapping]]] = ...) -> None: ...

class PredictTask(_message.Message):
    __slots__ = ("task_id", "model_id", "architecture", "spec", "weights", "input")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    ARCHITECTURE_FIELD_NUMBER: _ClassVar[int]
    SPEC_FIELD_NUMBER: _ClassVar[int]
    WEIGHTS_FIELD_NUMBER: _ClassVar[int]
    INPUT_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    model_id: str
    architecture: str
    spec: ModelSpec
    weights: bytes
    input: _model_pb2.Tensor
    def __init__(self, task_id: _Optional[str] = ..., model_id: _Optional[str] = ..., architecture: _Optional[str] = ..., spec: _Optional[_Union[ModelSpec, _Mapping]] = ..., weights: _Optional[bytes] = ..., input: _Optional[_Union[_model_pb2.Tensor, _Mapping]] = ...) -> None: ...

class PredictResult(_message.Message):
    __slots__ = ("task_id", "output", "probabilities", "error", "need_weights")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    PROBABILITIES_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    NEED_WEIGHTS_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    output: _model_pb2.Tensor
    probabilities: _model_pb2.Tensor
    error: str
    need_weights: bool
    def __init__(self, task_id: _Optional[str] = ..., output: _Optional[_Union[_model_pb2.Tensor, _Mapping]] = ..., probabilities: _Optional[_Union[_model_pb2.Tensor, _Mapping]] = ..., error: _Optional[str] = ..., need_weights: bool = ...) -> None: ...

class TrainTask(_message.Message):
    __slots__ = ("task_id", "job_id", "architecture", "settings", "dataset_kind", "csv", "target", "history", "base_weights", "base_labels", "base_features", "archive", "columns", "group_rank", "group_size", "text", "base_adapter")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    ARCHITECTURE_FIELD_NUMBER: _ClassVar[int]
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    DATASET_KIND_FIELD_NUMBER: _ClassVar[int]
    CSV_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    HISTORY_FIELD_NUMBER: _ClassVar[int]
    BASE_WEIGHTS_FIELD_NUMBER: _ClassVar[int]
    BASE_LABELS_FIELD_NUMBER: _ClassVar[int]
    BASE_FEATURES_FIELD_NUMBER: _ClassVar[int]
    ARCHIVE_FIELD_NUMBER: _ClassVar[int]
    COLUMNS_FIELD_NUMBER: _ClassVar[int]
    GROUP_RANK_FIELD_NUMBER: _ClassVar[int]
    GROUP_SIZE_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    BASE_ADAPTER_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    job_id: str
    architecture: str
    settings: _training_pb2.TrainingSettings
    dataset_kind: _training_pb2.DatasetKind
    csv: bytes
    target: str
    history: _containers.RepeatedCompositeFieldContainer[_training_pb2.EpochResult]
    base_weights: bytes
    base_labels: _containers.RepeatedScalarFieldContainer[str]
    base_features: _containers.RepeatedScalarFieldContainer[str]
    archive: bytes
    columns: _containers.RepeatedCompositeFieldContainer[_model_pb2.Column]
    group_rank: int
    group_size: int
    text: bytes
    base_adapter: bytes
    def __init__(self, task_id: _Optional[str] = ..., job_id: _Optional[str] = ..., architecture: _Optional[str] = ..., settings: _Optional[_Union[_training_pb2.TrainingSettings, _Mapping]] = ..., dataset_kind: _Optional[_Union[_training_pb2.DatasetKind, str]] = ..., csv: _Optional[bytes] = ..., target: _Optional[str] = ..., history: _Optional[_Iterable[_Union[_training_pb2.EpochResult, _Mapping]]] = ..., base_weights: _Optional[bytes] = ..., base_labels: _Optional[_Iterable[str]] = ..., base_features: _Optional[_Iterable[str]] = ..., archive: _Optional[bytes] = ..., columns: _Optional[_Iterable[_Union[_model_pb2.Column, _Mapping]]] = ..., group_rank: _Optional[int] = ..., group_size: _Optional[int] = ..., text: _Optional[bytes] = ..., base_adapter: _Optional[bytes] = ...) -> None: ...

class GroupShare(_message.Message):
    __slots__ = ("task_id", "round", "values", "weight")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    ROUND_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    WEIGHT_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    round: int
    values: _containers.RepeatedScalarFieldContainer[float]
    weight: float
    def __init__(self, task_id: _Optional[str] = ..., round: _Optional[int] = ..., values: _Optional[_Iterable[float]] = ..., weight: _Optional[float] = ...) -> None: ...

class GroupMean(_message.Message):
    __slots__ = ("task_id", "round", "values")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    ROUND_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    round: int
    values: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, task_id: _Optional[str] = ..., round: _Optional[int] = ..., values: _Optional[_Iterable[float]] = ...) -> None: ...

class TrainProgress(_message.Message):
    __slots__ = ("task_id", "epoch", "step", "steps_per_epoch", "history")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    EPOCH_FIELD_NUMBER: _ClassVar[int]
    STEP_FIELD_NUMBER: _ClassVar[int]
    STEPS_PER_EPOCH_FIELD_NUMBER: _ClassVar[int]
    HISTORY_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    epoch: int
    step: int
    steps_per_epoch: int
    history: _containers.RepeatedCompositeFieldContainer[_training_pb2.EpochResult]
    def __init__(self, task_id: _Optional[str] = ..., epoch: _Optional[int] = ..., step: _Optional[int] = ..., steps_per_epoch: _Optional[int] = ..., history: _Optional[_Iterable[_Union[_training_pb2.EpochResult, _Mapping]]] = ...) -> None: ...

class TrainResult(_message.Message):
    __slots__ = ("task_id", "weights", "history", "spec", "error", "cancelled", "fresh", "low_memory", "report", "devices")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    WEIGHTS_FIELD_NUMBER: _ClassVar[int]
    HISTORY_FIELD_NUMBER: _ClassVar[int]
    SPEC_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    CANCELLED_FIELD_NUMBER: _ClassVar[int]
    FRESH_FIELD_NUMBER: _ClassVar[int]
    LOW_MEMORY_FIELD_NUMBER: _ClassVar[int]
    REPORT_FIELD_NUMBER: _ClassVar[int]
    DEVICES_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    weights: bytes
    history: _containers.RepeatedCompositeFieldContainer[_training_pb2.EpochResult]
    spec: ModelSpec
    error: str
    cancelled: bool
    fresh: bool
    low_memory: bool
    report: bytes
    devices: int
    def __init__(self, task_id: _Optional[str] = ..., weights: _Optional[bytes] = ..., history: _Optional[_Iterable[_Union[_training_pb2.EpochResult, _Mapping]]] = ..., spec: _Optional[_Union[ModelSpec, _Mapping]] = ..., error: _Optional[str] = ..., cancelled: bool = ..., fresh: bool = ..., low_memory: bool = ..., report: _Optional[bytes] = ..., devices: _Optional[int] = ...) -> None: ...

class CancelTask(_message.Message):
    __slots__ = ("task_id",)
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    def __init__(self, task_id: _Optional[str] = ...) -> None: ...

class CloudGpu(_message.Message):
    __slots__ = ("enabled", "provider", "token_id", "has_token_secret", "gpu", "region", "ssh_key", "console_url", "idle_minutes", "max_hours", "capacity", "program_url", "can_serve_program", "worker_id", "state", "state_time", "error")
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    TOKEN_ID_FIELD_NUMBER: _ClassVar[int]
    HAS_TOKEN_SECRET_FIELD_NUMBER: _ClassVar[int]
    GPU_FIELD_NUMBER: _ClassVar[int]
    REGION_FIELD_NUMBER: _ClassVar[int]
    SSH_KEY_FIELD_NUMBER: _ClassVar[int]
    CONSOLE_URL_FIELD_NUMBER: _ClassVar[int]
    IDLE_MINUTES_FIELD_NUMBER: _ClassVar[int]
    MAX_HOURS_FIELD_NUMBER: _ClassVar[int]
    CAPACITY_FIELD_NUMBER: _ClassVar[int]
    PROGRAM_URL_FIELD_NUMBER: _ClassVar[int]
    CAN_SERVE_PROGRAM_FIELD_NUMBER: _ClassVar[int]
    WORKER_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    STATE_TIME_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    enabled: bool
    provider: str
    token_id: str
    has_token_secret: bool
    gpu: str
    region: str
    ssh_key: str
    console_url: str
    idle_minutes: int
    max_hours: int
    capacity: int
    program_url: str
    can_serve_program: bool
    worker_id: str
    state: str
    state_time: _timestamp_pb2.Timestamp
    error: str
    def __init__(self, enabled: bool = ..., provider: _Optional[str] = ..., token_id: _Optional[str] = ..., has_token_secret: bool = ..., gpu: _Optional[str] = ..., region: _Optional[str] = ..., ssh_key: _Optional[str] = ..., console_url: _Optional[str] = ..., idle_minutes: _Optional[int] = ..., max_hours: _Optional[int] = ..., capacity: _Optional[int] = ..., program_url: _Optional[str] = ..., can_serve_program: bool = ..., worker_id: _Optional[str] = ..., state: _Optional[str] = ..., state_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., error: _Optional[str] = ...) -> None: ...

class GetCloudGpuRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetCloudGpuResponse(_message.Message):
    __slots__ = ("cloud_gpu", "providers")
    CLOUD_GPU_FIELD_NUMBER: _ClassVar[int]
    PROVIDERS_FIELD_NUMBER: _ClassVar[int]
    cloud_gpu: CloudGpu
    providers: _containers.RepeatedCompositeFieldContainer[CloudGpuProvider]
    def __init__(self, cloud_gpu: _Optional[_Union[CloudGpu, _Mapping]] = ..., providers: _Optional[_Iterable[_Union[CloudGpuProvider, _Mapping]]] = ...) -> None: ...

class CloudGpuProvider(_message.Message):
    __slots__ = ("id", "name", "gpus", "default_gpu", "regions", "default_region")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    GPUS_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_GPU_FIELD_NUMBER: _ClassVar[int]
    REGIONS_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_REGION_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    gpus: _containers.RepeatedCompositeFieldContainer[CloudGpuChoice]
    default_gpu: str
    regions: _containers.RepeatedScalarFieldContainer[str]
    default_region: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., gpus: _Optional[_Iterable[_Union[CloudGpuChoice, _Mapping]]] = ..., default_gpu: _Optional[str] = ..., regions: _Optional[_Iterable[str]] = ..., default_region: _Optional[str] = ...) -> None: ...

class CloudGpuChoice(_message.Message):
    __slots__ = ("id", "label")
    ID_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    id: str
    label: str
    def __init__(self, id: _Optional[str] = ..., label: _Optional[str] = ...) -> None: ...

class UpdateCloudGpuRequest(_message.Message):
    __slots__ = ("enabled", "provider", "token_id", "token_secret", "gpu", "region", "ssh_key", "console_url", "idle_minutes", "max_hours", "capacity", "program_url")
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    TOKEN_ID_FIELD_NUMBER: _ClassVar[int]
    TOKEN_SECRET_FIELD_NUMBER: _ClassVar[int]
    GPU_FIELD_NUMBER: _ClassVar[int]
    REGION_FIELD_NUMBER: _ClassVar[int]
    SSH_KEY_FIELD_NUMBER: _ClassVar[int]
    CONSOLE_URL_FIELD_NUMBER: _ClassVar[int]
    IDLE_MINUTES_FIELD_NUMBER: _ClassVar[int]
    MAX_HOURS_FIELD_NUMBER: _ClassVar[int]
    CAPACITY_FIELD_NUMBER: _ClassVar[int]
    PROGRAM_URL_FIELD_NUMBER: _ClassVar[int]
    enabled: bool
    provider: str
    token_id: str
    token_secret: str
    gpu: str
    region: str
    ssh_key: str
    console_url: str
    idle_minutes: int
    max_hours: int
    capacity: int
    program_url: str
    def __init__(self, enabled: bool = ..., provider: _Optional[str] = ..., token_id: _Optional[str] = ..., token_secret: _Optional[str] = ..., gpu: _Optional[str] = ..., region: _Optional[str] = ..., ssh_key: _Optional[str] = ..., console_url: _Optional[str] = ..., idle_minutes: _Optional[int] = ..., max_hours: _Optional[int] = ..., capacity: _Optional[int] = ..., program_url: _Optional[str] = ...) -> None: ...

class UpdateCloudGpuResponse(_message.Message):
    __slots__ = ("cloud_gpu",)
    CLOUD_GPU_FIELD_NUMBER: _ClassVar[int]
    cloud_gpu: CloudGpu
    def __init__(self, cloud_gpu: _Optional[_Union[CloudGpu, _Mapping]] = ...) -> None: ...

class StopCloudGpuRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StopCloudGpuResponse(_message.Message):
    __slots__ = ("cloud_gpu",)
    CLOUD_GPU_FIELD_NUMBER: _ClassVar[int]
    cloud_gpu: CloudGpu
    def __init__(self, cloud_gpu: _Optional[_Union[CloudGpu, _Mapping]] = ...) -> None: ...
