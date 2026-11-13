import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from mimirsdk._gen.mimir.v1 import model_pb2 as _model_pb2
from mimirsdk._gen.mimir.v1 import template_pb2 as _template_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DatasetKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DATASET_KIND_UNSPECIFIED: _ClassVar[DatasetKind]
    DATASET_KIND_TABLE: _ClassVar[DatasetKind]
    DATASET_KIND_MNIST: _ClassVar[DatasetKind]
    DATASET_KIND_PHOTOS: _ClassVar[DatasetKind]
    DATASET_KIND_PHOTO_TABLE: _ClassVar[DatasetKind]
    DATASET_KIND_TEXT: _ClassVar[DatasetKind]
    DATASET_KIND_SOUNDS: _ClassVar[DatasetKind]
    DATASET_KIND_BOXES: _ClassVar[DatasetKind]

class JobStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    JOB_STATUS_UNSPECIFIED: _ClassVar[JobStatus]
    JOB_STATUS_QUEUED: _ClassVar[JobStatus]
    JOB_STATUS_RUNNING: _ClassVar[JobStatus]
    JOB_STATUS_SUCCEEDED: _ClassVar[JobStatus]
    JOB_STATUS_FAILED: _ClassVar[JobStatus]
    JOB_STATUS_CANCELLED: _ClassVar[JobStatus]
DATASET_KIND_UNSPECIFIED: DatasetKind
DATASET_KIND_TABLE: DatasetKind
DATASET_KIND_MNIST: DatasetKind
DATASET_KIND_PHOTOS: DatasetKind
DATASET_KIND_PHOTO_TABLE: DatasetKind
DATASET_KIND_TEXT: DatasetKind
DATASET_KIND_SOUNDS: DatasetKind
DATASET_KIND_BOXES: DatasetKind
JOB_STATUS_UNSPECIFIED: JobStatus
JOB_STATUS_QUEUED: JobStatus
JOB_STATUS_RUNNING: JobStatus
JOB_STATUS_SUCCEEDED: JobStatus
JOB_STATUS_FAILED: JobStatus
JOB_STATUS_CANCELLED: JobStatus

class CheckDatasetRequest(_message.Message):
    __slots__ = ("dataset_id", "template_id", "match", "apply")
    class MatchEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_ID_FIELD_NUMBER: _ClassVar[int]
    MATCH_FIELD_NUMBER: _ClassVar[int]
    APPLY_FIELD_NUMBER: _ClassVar[int]
    dataset_id: str
    template_id: str
    match: _containers.ScalarMap[str, str]
    apply: bool
    def __init__(self, dataset_id: _Optional[str] = ..., template_id: _Optional[str] = ..., match: _Optional[_Mapping[str, str]] = ..., apply: bool = ...) -> None: ...

class CheckDatasetResponse(_message.Message):
    __slots__ = ("check", "dataset")
    CHECK_FIELD_NUMBER: _ClassVar[int]
    DATASET_FIELD_NUMBER: _ClassVar[int]
    check: _template_pb2.DataCheck
    dataset: Dataset
    def __init__(self, check: _Optional[_Union[_template_pb2.DataCheck, _Mapping]] = ..., dataset: _Optional[_Union[Dataset, _Mapping]] = ...) -> None: ...

class CompareJobsRequest(_message.Message):
    __slots__ = ("ids",)
    IDS_FIELD_NUMBER: _ClassVar[int]
    ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, ids: _Optional[_Iterable[str]] = ...) -> None: ...

class CompareJobsResponse(_message.Message):
    __slots__ = ("jobs", "differs", "best_id")
    JOBS_FIELD_NUMBER: _ClassVar[int]
    DIFFERS_FIELD_NUMBER: _ClassVar[int]
    BEST_ID_FIELD_NUMBER: _ClassVar[int]
    jobs: _containers.RepeatedCompositeFieldContainer[Job]
    differs: _containers.RepeatedScalarFieldContainer[str]
    best_id: str
    def __init__(self, jobs: _Optional[_Iterable[_Union[Job, _Mapping]]] = ..., differs: _Optional[_Iterable[str]] = ..., best_id: _Optional[str] = ...) -> None: ...

class SetRepeatRequest(_message.Message):
    __slots__ = ("id", "repeat_seconds", "min_new_rows")
    ID_FIELD_NUMBER: _ClassVar[int]
    REPEAT_SECONDS_FIELD_NUMBER: _ClassVar[int]
    MIN_NEW_ROWS_FIELD_NUMBER: _ClassVar[int]
    id: str
    repeat_seconds: int
    min_new_rows: int
    def __init__(self, id: _Optional[str] = ..., repeat_seconds: _Optional[int] = ..., min_new_rows: _Optional[int] = ...) -> None: ...

class SetRepeatResponse(_message.Message):
    __slots__ = ("job",)
    JOB_FIELD_NUMBER: _ClassVar[int]
    job: Job
    def __init__(self, job: _Optional[_Union[Job, _Mapping]] = ...) -> None: ...

class Dataset(_message.Message):
    __slots__ = ("id", "name", "kind", "rows", "features", "labels", "input_shape", "target", "size_bytes", "create_time", "driver", "query", "refresh_time", "architectures", "columns", "number_target", "skipped", "storage")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    ROWS_FIELD_NUMBER: _ClassVar[int]
    FEATURES_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    INPUT_SHAPE_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    SIZE_BYTES_FIELD_NUMBER: _ClassVar[int]
    CREATE_TIME_FIELD_NUMBER: _ClassVar[int]
    DRIVER_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    REFRESH_TIME_FIELD_NUMBER: _ClassVar[int]
    ARCHITECTURES_FIELD_NUMBER: _ClassVar[int]
    COLUMNS_FIELD_NUMBER: _ClassVar[int]
    NUMBER_TARGET_FIELD_NUMBER: _ClassVar[int]
    SKIPPED_FIELD_NUMBER: _ClassVar[int]
    STORAGE_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    kind: DatasetKind
    rows: int
    features: _containers.RepeatedScalarFieldContainer[str]
    labels: _containers.RepeatedScalarFieldContainer[str]
    input_shape: _containers.RepeatedScalarFieldContainer[int]
    target: str
    size_bytes: int
    create_time: _timestamp_pb2.Timestamp
    driver: str
    query: str
    refresh_time: _timestamp_pb2.Timestamp
    architectures: _containers.RepeatedScalarFieldContainer[str]
    columns: _containers.RepeatedCompositeFieldContainer[_model_pb2.Column]
    number_target: bool
    skipped: int
    storage: StorageSource
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., kind: _Optional[_Union[DatasetKind, str]] = ..., rows: _Optional[int] = ..., features: _Optional[_Iterable[str]] = ..., labels: _Optional[_Iterable[str]] = ..., input_shape: _Optional[_Iterable[int]] = ..., target: _Optional[str] = ..., size_bytes: _Optional[int] = ..., create_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., driver: _Optional[str] = ..., query: _Optional[str] = ..., refresh_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., architectures: _Optional[_Iterable[str]] = ..., columns: _Optional[_Iterable[_Union[_model_pb2.Column, _Mapping]]] = ..., number_target: bool = ..., skipped: _Optional[int] = ..., storage: _Optional[_Union[StorageSource, _Mapping]] = ...) -> None: ...

class StorageSource(_message.Message):
    __slots__ = ("provider", "endpoint", "bucket", "path")
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    BUCKET_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    provider: str
    endpoint: str
    bucket: str
    path: str
    def __init__(self, provider: _Optional[str] = ..., endpoint: _Optional[str] = ..., bucket: _Optional[str] = ..., path: _Optional[str] = ...) -> None: ...

class ListDatasetsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListDatasetsResponse(_message.Message):
    __slots__ = ("datasets",)
    DATASETS_FIELD_NUMBER: _ClassVar[int]
    datasets: _containers.RepeatedCompositeFieldContainer[Dataset]
    def __init__(self, datasets: _Optional[_Iterable[_Union[Dataset, _Mapping]]] = ...) -> None: ...

class GetDatasetRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetDatasetResponse(_message.Message):
    __slots__ = ("dataset", "sample")
    DATASET_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_FIELD_NUMBER: _ClassVar[int]
    dataset: Dataset
    sample: _containers.RepeatedCompositeFieldContainer[Row]
    def __init__(self, dataset: _Optional[_Union[Dataset, _Mapping]] = ..., sample: _Optional[_Iterable[_Union[Row, _Mapping]]] = ...) -> None: ...

class Row(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, values: _Optional[_Iterable[str]] = ...) -> None: ...

class CreateDatasetRequest(_message.Message):
    __slots__ = ("name", "kind", "csv", "target", "connection", "query", "archive", "template_id", "example", "bucket", "path", "text")
    NAME_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    CSV_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    ARCHIVE_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_ID_FIELD_NUMBER: _ClassVar[int]
    EXAMPLE_FIELD_NUMBER: _ClassVar[int]
    BUCKET_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    name: str
    kind: DatasetKind
    csv: bytes
    target: str
    connection: Connection
    query: str
    archive: bytes
    template_id: str
    example: bool
    bucket: Bucket
    path: str
    text: bytes
    def __init__(self, name: _Optional[str] = ..., kind: _Optional[_Union[DatasetKind, str]] = ..., csv: _Optional[bytes] = ..., target: _Optional[str] = ..., connection: _Optional[_Union[Connection, _Mapping]] = ..., query: _Optional[str] = ..., archive: _Optional[bytes] = ..., template_id: _Optional[str] = ..., example: bool = ..., bucket: _Optional[_Union[Bucket, _Mapping]] = ..., path: _Optional[str] = ..., text: _Optional[bytes] = ...) -> None: ...

class Bucket(_message.Message):
    __slots__ = ("provider", "endpoint", "region", "account_id", "bucket", "access_key_id", "secret_access_key")
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    REGION_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    BUCKET_FIELD_NUMBER: _ClassVar[int]
    ACCESS_KEY_ID_FIELD_NUMBER: _ClassVar[int]
    SECRET_ACCESS_KEY_FIELD_NUMBER: _ClassVar[int]
    provider: str
    endpoint: str
    region: str
    account_id: str
    bucket: str
    access_key_id: str
    secret_access_key: str
    def __init__(self, provider: _Optional[str] = ..., endpoint: _Optional[str] = ..., region: _Optional[str] = ..., account_id: _Optional[str] = ..., bucket: _Optional[str] = ..., access_key_id: _Optional[str] = ..., secret_access_key: _Optional[str] = ...) -> None: ...

class TestBucketRequest(_message.Message):
    __slots__ = ("bucket", "path", "kind")
    BUCKET_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    bucket: Bucket
    path: str
    kind: DatasetKind
    def __init__(self, bucket: _Optional[_Union[Bucket, _Mapping]] = ..., path: _Optional[str] = ..., kind: _Optional[_Union[DatasetKind, str]] = ...) -> None: ...

class TestBucketResponse(_message.Message):
    __slots__ = ("files", "size_bytes", "names", "columns", "sample", "rows")
    FILES_FIELD_NUMBER: _ClassVar[int]
    SIZE_BYTES_FIELD_NUMBER: _ClassVar[int]
    NAMES_FIELD_NUMBER: _ClassVar[int]
    COLUMNS_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_FIELD_NUMBER: _ClassVar[int]
    ROWS_FIELD_NUMBER: _ClassVar[int]
    files: int
    size_bytes: int
    names: _containers.RepeatedScalarFieldContainer[str]
    columns: _containers.RepeatedScalarFieldContainer[str]
    sample: _containers.RepeatedCompositeFieldContainer[Row]
    rows: int
    def __init__(self, files: _Optional[int] = ..., size_bytes: _Optional[int] = ..., names: _Optional[_Iterable[str]] = ..., columns: _Optional[_Iterable[str]] = ..., sample: _Optional[_Iterable[_Union[Row, _Mapping]]] = ..., rows: _Optional[int] = ...) -> None: ...

class Connection(_message.Message):
    __slots__ = ("driver", "dsn")
    DRIVER_FIELD_NUMBER: _ClassVar[int]
    DSN_FIELD_NUMBER: _ClassVar[int]
    driver: str
    dsn: str
    def __init__(self, driver: _Optional[str] = ..., dsn: _Optional[str] = ...) -> None: ...

class TestQueryRequest(_message.Message):
    __slots__ = ("connection", "query")
    CONNECTION_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    connection: Connection
    query: str
    def __init__(self, connection: _Optional[_Union[Connection, _Mapping]] = ..., query: _Optional[str] = ...) -> None: ...

class TestQueryResponse(_message.Message):
    __slots__ = ("columns", "sample", "rows")
    COLUMNS_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_FIELD_NUMBER: _ClassVar[int]
    ROWS_FIELD_NUMBER: _ClassVar[int]
    columns: _containers.RepeatedScalarFieldContainer[str]
    sample: _containers.RepeatedCompositeFieldContainer[Row]
    rows: int
    def __init__(self, columns: _Optional[_Iterable[str]] = ..., sample: _Optional[_Iterable[_Union[Row, _Mapping]]] = ..., rows: _Optional[int] = ...) -> None: ...

class RefreshDatasetRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class RefreshDatasetResponse(_message.Message):
    __slots__ = ("dataset",)
    DATASET_FIELD_NUMBER: _ClassVar[int]
    dataset: Dataset
    def __init__(self, dataset: _Optional[_Union[Dataset, _Mapping]] = ...) -> None: ...

class CreateDatasetResponse(_message.Message):
    __slots__ = ("dataset", "check")
    DATASET_FIELD_NUMBER: _ClassVar[int]
    CHECK_FIELD_NUMBER: _ClassVar[int]
    dataset: Dataset
    check: _template_pb2.DataCheck
    def __init__(self, dataset: _Optional[_Union[Dataset, _Mapping]] = ..., check: _Optional[_Union[_template_pb2.DataCheck, _Mapping]] = ...) -> None: ...

class DeleteDatasetRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteDatasetResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TrainingSettings(_message.Message):
    __slots__ = ("epochs", "batch_size", "learning_rate", "hold_out", "layers")
    EPOCHS_FIELD_NUMBER: _ClassVar[int]
    BATCH_SIZE_FIELD_NUMBER: _ClassVar[int]
    LEARNING_RATE_FIELD_NUMBER: _ClassVar[int]
    HOLD_OUT_FIELD_NUMBER: _ClassVar[int]
    LAYERS_FIELD_NUMBER: _ClassVar[int]
    epochs: int
    batch_size: int
    learning_rate: float
    hold_out: float
    layers: _containers.RepeatedCompositeFieldContainer[Layer]
    def __init__(self, epochs: _Optional[int] = ..., batch_size: _Optional[int] = ..., learning_rate: _Optional[float] = ..., hold_out: _Optional[float] = ..., layers: _Optional[_Iterable[_Union[Layer, _Mapping]]] = ...) -> None: ...

class Layer(_message.Message):
    __slots__ = ("kind", "units", "rate")
    KIND_FIELD_NUMBER: _ClassVar[int]
    UNITS_FIELD_NUMBER: _ClassVar[int]
    RATE_FIELD_NUMBER: _ClassVar[int]
    kind: str
    units: int
    rate: float
    def __init__(self, kind: _Optional[str] = ..., units: _Optional[int] = ..., rate: _Optional[float] = ...) -> None: ...

class EpochResult(_message.Message):
    __slots__ = ("epoch", "loss", "accuracy", "val_loss", "duration_millis", "typical_error")
    EPOCH_FIELD_NUMBER: _ClassVar[int]
    LOSS_FIELD_NUMBER: _ClassVar[int]
    ACCURACY_FIELD_NUMBER: _ClassVar[int]
    VAL_LOSS_FIELD_NUMBER: _ClassVar[int]
    DURATION_MILLIS_FIELD_NUMBER: _ClassVar[int]
    TYPICAL_ERROR_FIELD_NUMBER: _ClassVar[int]
    epoch: int
    loss: float
    accuracy: float
    val_loss: float
    duration_millis: int
    typical_error: float
    def __init__(self, epoch: _Optional[int] = ..., loss: _Optional[float] = ..., accuracy: _Optional[float] = ..., val_loss: _Optional[float] = ..., duration_millis: _Optional[int] = ..., typical_error: _Optional[float] = ...) -> None: ...

class Job(_message.Message):
    __slots__ = ("id", "name", "description", "architecture", "dataset_id", "dataset_name", "settings", "status", "error", "epoch", "history", "model_id", "created_by", "create_time", "start_time", "end_time", "accuracy", "steps_per_epoch", "step", "worker", "repeat_seconds", "next_run_time", "parent_id", "base_model_id", "note", "run_on", "min_new_rows", "trained_rows", "check_time", "check_note", "report", "start_from_model_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ARCHITECTURE_FIELD_NUMBER: _ClassVar[int]
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    DATASET_NAME_FIELD_NUMBER: _ClassVar[int]
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    EPOCH_FIELD_NUMBER: _ClassVar[int]
    HISTORY_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    CREATE_TIME_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    ACCURACY_FIELD_NUMBER: _ClassVar[int]
    STEPS_PER_EPOCH_FIELD_NUMBER: _ClassVar[int]
    STEP_FIELD_NUMBER: _ClassVar[int]
    WORKER_FIELD_NUMBER: _ClassVar[int]
    REPEAT_SECONDS_FIELD_NUMBER: _ClassVar[int]
    NEXT_RUN_TIME_FIELD_NUMBER: _ClassVar[int]
    PARENT_ID_FIELD_NUMBER: _ClassVar[int]
    BASE_MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    NOTE_FIELD_NUMBER: _ClassVar[int]
    RUN_ON_FIELD_NUMBER: _ClassVar[int]
    MIN_NEW_ROWS_FIELD_NUMBER: _ClassVar[int]
    TRAINED_ROWS_FIELD_NUMBER: _ClassVar[int]
    CHECK_TIME_FIELD_NUMBER: _ClassVar[int]
    CHECK_NOTE_FIELD_NUMBER: _ClassVar[int]
    REPORT_FIELD_NUMBER: _ClassVar[int]
    START_FROM_MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    architecture: str
    dataset_id: str
    dataset_name: str
    settings: TrainingSettings
    status: JobStatus
    error: str
    epoch: int
    history: _containers.RepeatedCompositeFieldContainer[EpochResult]
    model_id: str
    created_by: str
    create_time: _timestamp_pb2.Timestamp
    start_time: _timestamp_pb2.Timestamp
    end_time: _timestamp_pb2.Timestamp
    accuracy: float
    steps_per_epoch: int
    step: int
    worker: str
    repeat_seconds: int
    next_run_time: _timestamp_pb2.Timestamp
    parent_id: str
    base_model_id: str
    note: str
    run_on: str
    min_new_rows: int
    trained_rows: int
    check_time: _timestamp_pb2.Timestamp
    check_note: str
    report: RunReport
    start_from_model_id: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., architecture: _Optional[str] = ..., dataset_id: _Optional[str] = ..., dataset_name: _Optional[str] = ..., settings: _Optional[_Union[TrainingSettings, _Mapping]] = ..., status: _Optional[_Union[JobStatus, str]] = ..., error: _Optional[str] = ..., epoch: _Optional[int] = ..., history: _Optional[_Iterable[_Union[EpochResult, _Mapping]]] = ..., model_id: _Optional[str] = ..., created_by: _Optional[str] = ..., create_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., start_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., end_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., accuracy: _Optional[float] = ..., steps_per_epoch: _Optional[int] = ..., step: _Optional[int] = ..., worker: _Optional[str] = ..., repeat_seconds: _Optional[int] = ..., next_run_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., parent_id: _Optional[str] = ..., base_model_id: _Optional[str] = ..., note: _Optional[str] = ..., run_on: _Optional[str] = ..., min_new_rows: _Optional[int] = ..., trained_rows: _Optional[int] = ..., check_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., check_note: _Optional[str] = ..., report: _Optional[_Union[RunReport, _Mapping]] = ..., start_from_model_id: _Optional[str] = ...) -> None: ...

class RunReport(_message.Message):
    __slots__ = ("kind", "examples", "on_training", "millis_per_example", "size_bytes", "accuracy", "macro_f1", "log_loss", "classes", "confusion", "mae", "rmse", "r2", "within10", "points", "k", "hit_at", "mrr", "ndcg")
    KIND_FIELD_NUMBER: _ClassVar[int]
    EXAMPLES_FIELD_NUMBER: _ClassVar[int]
    ON_TRAINING_FIELD_NUMBER: _ClassVar[int]
    MILLIS_PER_EXAMPLE_FIELD_NUMBER: _ClassVar[int]
    SIZE_BYTES_FIELD_NUMBER: _ClassVar[int]
    ACCURACY_FIELD_NUMBER: _ClassVar[int]
    MACRO_F1_FIELD_NUMBER: _ClassVar[int]
    LOG_LOSS_FIELD_NUMBER: _ClassVar[int]
    CLASSES_FIELD_NUMBER: _ClassVar[int]
    CONFUSION_FIELD_NUMBER: _ClassVar[int]
    MAE_FIELD_NUMBER: _ClassVar[int]
    RMSE_FIELD_NUMBER: _ClassVar[int]
    R2_FIELD_NUMBER: _ClassVar[int]
    WITHIN10_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    K_FIELD_NUMBER: _ClassVar[int]
    HIT_AT_FIELD_NUMBER: _ClassVar[int]
    MRR_FIELD_NUMBER: _ClassVar[int]
    NDCG_FIELD_NUMBER: _ClassVar[int]
    kind: str
    examples: int
    on_training: bool
    millis_per_example: float
    size_bytes: int
    accuracy: float
    macro_f1: float
    log_loss: float
    classes: _containers.RepeatedCompositeFieldContainer[ClassScore]
    confusion: _containers.RepeatedCompositeFieldContainer[ConfusionRow]
    mae: float
    rmse: float
    r2: float
    within10: float
    points: _containers.RepeatedCompositeFieldContainer[GuessPoint]
    k: int
    hit_at: _containers.RepeatedScalarFieldContainer[float]
    mrr: float
    ndcg: float
    def __init__(self, kind: _Optional[str] = ..., examples: _Optional[int] = ..., on_training: bool = ..., millis_per_example: _Optional[float] = ..., size_bytes: _Optional[int] = ..., accuracy: _Optional[float] = ..., macro_f1: _Optional[float] = ..., log_loss: _Optional[float] = ..., classes: _Optional[_Iterable[_Union[ClassScore, _Mapping]]] = ..., confusion: _Optional[_Iterable[_Union[ConfusionRow, _Mapping]]] = ..., mae: _Optional[float] = ..., rmse: _Optional[float] = ..., r2: _Optional[float] = ..., within10: _Optional[float] = ..., points: _Optional[_Iterable[_Union[GuessPoint, _Mapping]]] = ..., k: _Optional[int] = ..., hit_at: _Optional[_Iterable[float]] = ..., mrr: _Optional[float] = ..., ndcg: _Optional[float] = ...) -> None: ...

class ClassScore(_message.Message):
    __slots__ = ("label", "precision", "recall", "f1", "support")
    LABEL_FIELD_NUMBER: _ClassVar[int]
    PRECISION_FIELD_NUMBER: _ClassVar[int]
    RECALL_FIELD_NUMBER: _ClassVar[int]
    F1_FIELD_NUMBER: _ClassVar[int]
    SUPPORT_FIELD_NUMBER: _ClassVar[int]
    label: str
    precision: float
    recall: float
    f1: float
    support: int
    def __init__(self, label: _Optional[str] = ..., precision: _Optional[float] = ..., recall: _Optional[float] = ..., f1: _Optional[float] = ..., support: _Optional[int] = ...) -> None: ...

class ConfusionRow(_message.Message):
    __slots__ = ("counts",)
    COUNTS_FIELD_NUMBER: _ClassVar[int]
    counts: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, counts: _Optional[_Iterable[int]] = ...) -> None: ...

class GuessPoint(_message.Message):
    __slots__ = ("real", "guess")
    REAL_FIELD_NUMBER: _ClassVar[int]
    GUESS_FIELD_NUMBER: _ClassVar[int]
    real: float
    guess: float
    def __init__(self, real: _Optional[float] = ..., guess: _Optional[float] = ...) -> None: ...

class ListJobsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListJobsResponse(_message.Message):
    __slots__ = ("jobs",)
    JOBS_FIELD_NUMBER: _ClassVar[int]
    jobs: _containers.RepeatedCompositeFieldContainer[Job]
    def __init__(self, jobs: _Optional[_Iterable[_Union[Job, _Mapping]]] = ...) -> None: ...

class GetJobRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetJobResponse(_message.Message):
    __slots__ = ("job",)
    JOB_FIELD_NUMBER: _ClassVar[int]
    job: Job
    def __init__(self, job: _Optional[_Union[Job, _Mapping]] = ...) -> None: ...

class CreateJobRequest(_message.Message):
    __slots__ = ("name", "description", "architecture", "dataset_id", "settings", "repeat_seconds", "worker_id", "min_new_rows", "base_model_id", "start_from_model_id")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ARCHITECTURE_FIELD_NUMBER: _ClassVar[int]
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    REPEAT_SECONDS_FIELD_NUMBER: _ClassVar[int]
    WORKER_ID_FIELD_NUMBER: _ClassVar[int]
    MIN_NEW_ROWS_FIELD_NUMBER: _ClassVar[int]
    BASE_MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    START_FROM_MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    architecture: str
    dataset_id: str
    settings: TrainingSettings
    repeat_seconds: int
    worker_id: str
    min_new_rows: int
    base_model_id: str
    start_from_model_id: str
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., architecture: _Optional[str] = ..., dataset_id: _Optional[str] = ..., settings: _Optional[_Union[TrainingSettings, _Mapping]] = ..., repeat_seconds: _Optional[int] = ..., worker_id: _Optional[str] = ..., min_new_rows: _Optional[int] = ..., base_model_id: _Optional[str] = ..., start_from_model_id: _Optional[str] = ...) -> None: ...

class CreateJobResponse(_message.Message):
    __slots__ = ("job",)
    JOB_FIELD_NUMBER: _ClassVar[int]
    job: Job
    def __init__(self, job: _Optional[_Union[Job, _Mapping]] = ...) -> None: ...

class CancelJobRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class CancelJobResponse(_message.Message):
    __slots__ = ("job",)
    JOB_FIELD_NUMBER: _ClassVar[int]
    job: Job
    def __init__(self, job: _Optional[_Union[Job, _Mapping]] = ...) -> None: ...

class ResumeJobRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class ResumeJobResponse(_message.Message):
    __slots__ = ("job",)
    JOB_FIELD_NUMBER: _ClassVar[int]
    job: Job
    def __init__(self, job: _Optional[_Union[Job, _Mapping]] = ...) -> None: ...

class DeleteJobRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteJobResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
