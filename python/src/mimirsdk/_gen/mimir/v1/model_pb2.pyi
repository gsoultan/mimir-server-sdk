import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ModelVersionSource(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MODEL_VERSION_SOURCE_UNSPECIFIED: _ClassVar[ModelVersionSource]
    MODEL_VERSION_SOURCE_UPLOADED: _ClassVar[ModelVersionSource]
    MODEL_VERSION_SOURCE_TRAINED: _ClassVar[ModelVersionSource]
    MODEL_VERSION_SOURCE_KEEP_LEARNING: _ClassVar[ModelVersionSource]

class ModelStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MODEL_STATUS_UNSPECIFIED: _ClassVar[ModelStatus]
    MODEL_STATUS_READY: _ClassVar[ModelStatus]
    MODEL_STATUS_FAILED: _ClassVar[ModelStatus]
MODEL_VERSION_SOURCE_UNSPECIFIED: ModelVersionSource
MODEL_VERSION_SOURCE_UPLOADED: ModelVersionSource
MODEL_VERSION_SOURCE_TRAINED: ModelVersionSource
MODEL_VERSION_SOURCE_KEEP_LEARNING: ModelVersionSource
MODEL_STATUS_UNSPECIFIED: ModelStatus
MODEL_STATUS_READY: ModelStatus
MODEL_STATUS_FAILED: ModelStatus

class GetModelQualityRequest(_message.Message):
    __slots__ = ("model_id", "days")
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    DAYS_FIELD_NUMBER: _ClassVar[int]
    model_id: str
    days: int
    def __init__(self, model_id: _Optional[str] = ..., days: _Optional[int] = ...) -> None: ...

class QualityDay(_message.Message):
    __slots__ = ("day", "answers", "feedback", "correct")
    DAY_FIELD_NUMBER: _ClassVar[int]
    ANSWERS_FIELD_NUMBER: _ClassVar[int]
    FEEDBACK_FIELD_NUMBER: _ClassVar[int]
    CORRECT_FIELD_NUMBER: _ClassVar[int]
    day: _timestamp_pb2.Timestamp
    answers: int
    feedback: int
    correct: int
    def __init__(self, day: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., answers: _Optional[int] = ..., feedback: _Optional[int] = ..., correct: _Optional[int] = ...) -> None: ...

class GetModelQualityResponse(_message.Message):
    __slots__ = ("days", "week_answers", "week_feedback", "week_accuracy", "dropped")
    DAYS_FIELD_NUMBER: _ClassVar[int]
    WEEK_ANSWERS_FIELD_NUMBER: _ClassVar[int]
    WEEK_FEEDBACK_FIELD_NUMBER: _ClassVar[int]
    WEEK_ACCURACY_FIELD_NUMBER: _ClassVar[int]
    DROPPED_FIELD_NUMBER: _ClassVar[int]
    days: _containers.RepeatedCompositeFieldContainer[QualityDay]
    week_answers: int
    week_feedback: int
    week_accuracy: float
    dropped: bool
    def __init__(self, days: _Optional[_Iterable[_Union[QualityDay, _Mapping]]] = ..., week_answers: _Optional[int] = ..., week_feedback: _Optional[int] = ..., week_accuracy: _Optional[float] = ..., dropped: bool = ...) -> None: ...

class ModelVersion(_message.Message):
    __slots__ = ("id", "number", "source", "create_time", "size_bytes", "sha256", "accuracy", "job_id", "note", "live")
    ID_FIELD_NUMBER: _ClassVar[int]
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    CREATE_TIME_FIELD_NUMBER: _ClassVar[int]
    SIZE_BYTES_FIELD_NUMBER: _ClassVar[int]
    SHA256_FIELD_NUMBER: _ClassVar[int]
    ACCURACY_FIELD_NUMBER: _ClassVar[int]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    NOTE_FIELD_NUMBER: _ClassVar[int]
    LIVE_FIELD_NUMBER: _ClassVar[int]
    id: str
    number: int
    source: ModelVersionSource
    create_time: _timestamp_pb2.Timestamp
    size_bytes: int
    sha256: str
    accuracy: float
    job_id: str
    note: str
    live: bool
    def __init__(self, id: _Optional[str] = ..., number: _Optional[int] = ..., source: _Optional[_Union[ModelVersionSource, str]] = ..., create_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., size_bytes: _Optional[int] = ..., sha256: _Optional[str] = ..., accuracy: _Optional[float] = ..., job_id: _Optional[str] = ..., note: _Optional[str] = ..., live: bool = ...) -> None: ...

class ListModelVersionsRequest(_message.Message):
    __slots__ = ("model_id",)
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    model_id: str
    def __init__(self, model_id: _Optional[str] = ...) -> None: ...

class ListModelVersionsResponse(_message.Message):
    __slots__ = ("versions",)
    VERSIONS_FIELD_NUMBER: _ClassVar[int]
    versions: _containers.RepeatedCompositeFieldContainer[ModelVersion]
    def __init__(self, versions: _Optional[_Iterable[_Union[ModelVersion, _Mapping]]] = ...) -> None: ...

class UseModelVersionRequest(_message.Message):
    __slots__ = ("model_id", "version_id")
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    model_id: str
    version_id: str
    def __init__(self, model_id: _Optional[str] = ..., version_id: _Optional[str] = ...) -> None: ...

class UseModelVersionResponse(_message.Message):
    __slots__ = ("model",)
    MODEL_FIELD_NUMBER: _ClassVar[int]
    model: Model
    def __init__(self, model: _Optional[_Union[Model, _Mapping]] = ...) -> None: ...

class SaveArchitectureRequest(_message.Message):
    __slots__ = ("name", "title", "description", "input", "output", "items")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    INPUT_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    name: str
    title: str
    description: str
    input: str
    output: str
    items: int
    def __init__(self, name: _Optional[str] = ..., title: _Optional[str] = ..., description: _Optional[str] = ..., input: _Optional[str] = ..., output: _Optional[str] = ..., items: _Optional[int] = ...) -> None: ...

class SaveArchitectureResponse(_message.Message):
    __slots__ = ("architecture",)
    ARCHITECTURE_FIELD_NUMBER: _ClassVar[int]
    architecture: Architecture
    def __init__(self, architecture: _Optional[_Union[Architecture, _Mapping]] = ...) -> None: ...

class DeleteArchitectureRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class DeleteArchitectureResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SetModelWorkerRequest(_message.Message):
    __slots__ = ("id", "worker_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    WORKER_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    worker_id: str
    def __init__(self, id: _Optional[str] = ..., worker_id: _Optional[str] = ...) -> None: ...

class SetModelWorkerResponse(_message.Message):
    __slots__ = ("model",)
    MODEL_FIELD_NUMBER: _ClassVar[int]
    model: Model
    def __init__(self, model: _Optional[_Union[Model, _Mapping]] = ...) -> None: ...

class ExplainRequest(_message.Message):
    __slots__ = ("model_id", "fields", "label")
    class FieldsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    model_id: str
    fields: _containers.ScalarMap[str, str]
    label: str
    def __init__(self, model_id: _Optional[str] = ..., fields: _Optional[_Mapping[str, str]] = ..., label: _Optional[str] = ...) -> None: ...

class ExplainResponse(_message.Message):
    __slots__ = ("label", "number", "value", "typical", "contributions", "exact")
    LABEL_FIELD_NUMBER: _ClassVar[int]
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    TYPICAL_FIELD_NUMBER: _ClassVar[int]
    CONTRIBUTIONS_FIELD_NUMBER: _ClassVar[int]
    EXACT_FIELD_NUMBER: _ClassVar[int]
    label: str
    number: bool
    value: float
    typical: float
    contributions: _containers.RepeatedCompositeFieldContainer[Contribution]
    exact: bool
    def __init__(self, label: _Optional[str] = ..., number: bool = ..., value: _Optional[float] = ..., typical: _Optional[float] = ..., contributions: _Optional[_Iterable[_Union[Contribution, _Mapping]]] = ..., exact: bool = ...) -> None: ...

class Contribution(_message.Message):
    __slots__ = ("column", "value", "typical", "effect")
    COLUMN_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    TYPICAL_FIELD_NUMBER: _ClassVar[int]
    EFFECT_FIELD_NUMBER: _ClassVar[int]
    column: str
    value: str
    typical: str
    effect: float
    def __init__(self, column: _Optional[str] = ..., value: _Optional[str] = ..., typical: _Optional[str] = ..., effect: _Optional[float] = ...) -> None: ...

class ExplainModelRequest(_message.Message):
    __slots__ = ("model_id",)
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    model_id: str
    def __init__(self, model_id: _Optional[str] = ...) -> None: ...

class ExplainModelResponse(_message.Message):
    __slots__ = ("columns", "rows", "source", "number")
    COLUMNS_FIELD_NUMBER: _ClassVar[int]
    ROWS_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    columns: _containers.RepeatedCompositeFieldContainer[ColumnImportance]
    rows: int
    source: str
    number: bool
    def __init__(self, columns: _Optional[_Iterable[_Union[ColumnImportance, _Mapping]]] = ..., rows: _Optional[int] = ..., source: _Optional[str] = ..., number: bool = ...) -> None: ...

class ColumnImportance(_message.Message):
    __slots__ = ("column", "importance", "share")
    COLUMN_FIELD_NUMBER: _ClassVar[int]
    IMPORTANCE_FIELD_NUMBER: _ClassVar[int]
    SHARE_FIELD_NUMBER: _ClassVar[int]
    column: str
    importance: float
    share: float
    def __init__(self, column: _Optional[str] = ..., importance: _Optional[float] = ..., share: _Optional[float] = ...) -> None: ...

class SendFeedbackRequest(_message.Message):
    __slots__ = ("prediction_id", "label", "value")
    PREDICTION_ID_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    prediction_id: str
    label: str
    value: float
    def __init__(self, prediction_id: _Optional[str] = ..., label: _Optional[str] = ..., value: _Optional[float] = ...) -> None: ...

class SendFeedbackResponse(_message.Message):
    __slots__ = ("correct",)
    CORRECT_FIELD_NUMBER: _ClassVar[int]
    correct: bool
    def __init__(self, correct: bool = ...) -> None: ...

class Architecture(_message.Message):
    __slots__ = ("name", "title", "description", "input_shape", "labels", "trainable", "input", "output", "custom", "items", "designable", "learned", "target")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    INPUT_SHAPE_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    TRAINABLE_FIELD_NUMBER: _ClassVar[int]
    INPUT_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    DESIGNABLE_FIELD_NUMBER: _ClassVar[int]
    LEARNED_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    name: str
    title: str
    description: str
    input_shape: _containers.RepeatedScalarFieldContainer[int]
    labels: _containers.RepeatedScalarFieldContainer[str]
    trainable: bool
    input: str
    output: str
    custom: bool
    items: int
    designable: bool
    learned: bool
    target: str
    def __init__(self, name: _Optional[str] = ..., title: _Optional[str] = ..., description: _Optional[str] = ..., input_shape: _Optional[_Iterable[int]] = ..., labels: _Optional[_Iterable[str]] = ..., trainable: bool = ..., input: _Optional[str] = ..., output: _Optional[str] = ..., custom: bool = ..., items: _Optional[int] = ..., designable: bool = ..., learned: bool = ..., target: _Optional[str] = ...) -> None: ...

class Column(_message.Message):
    __slots__ = ("name", "kind", "values", "fill")
    NAME_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    FILL_FIELD_NUMBER: _ClassVar[int]
    name: str
    kind: str
    values: _containers.RepeatedScalarFieldContainer[str]
    fill: float
    def __init__(self, name: _Optional[str] = ..., kind: _Optional[str] = ..., values: _Optional[_Iterable[str]] = ..., fill: _Optional[float] = ...) -> None: ...

class Model(_message.Message):
    __slots__ = ("id", "name", "description", "architecture", "status", "status_detail", "size_bytes", "create_time", "update_time", "input_shape", "labels", "features", "job_id", "accuracy", "worker_id", "columns", "language", "on_device", "version", "version_id", "base_model_id", "base_model_name")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ARCHITECTURE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    STATUS_DETAIL_FIELD_NUMBER: _ClassVar[int]
    SIZE_BYTES_FIELD_NUMBER: _ClassVar[int]
    CREATE_TIME_FIELD_NUMBER: _ClassVar[int]
    UPDATE_TIME_FIELD_NUMBER: _ClassVar[int]
    INPUT_SHAPE_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    FEATURES_FIELD_NUMBER: _ClassVar[int]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    ACCURACY_FIELD_NUMBER: _ClassVar[int]
    WORKER_ID_FIELD_NUMBER: _ClassVar[int]
    COLUMNS_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    ON_DEVICE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    BASE_MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    BASE_MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    architecture: str
    status: ModelStatus
    status_detail: str
    size_bytes: int
    create_time: _timestamp_pb2.Timestamp
    update_time: _timestamp_pb2.Timestamp
    input_shape: _containers.RepeatedScalarFieldContainer[int]
    labels: _containers.RepeatedScalarFieldContainer[str]
    features: _containers.RepeatedScalarFieldContainer[str]
    job_id: str
    accuracy: float
    worker_id: str
    columns: _containers.RepeatedCompositeFieldContainer[Column]
    language: LanguageSettings
    on_device: bool
    version: str
    version_id: str
    base_model_id: str
    base_model_name: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., architecture: _Optional[str] = ..., status: _Optional[_Union[ModelStatus, str]] = ..., status_detail: _Optional[str] = ..., size_bytes: _Optional[int] = ..., create_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., update_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., input_shape: _Optional[_Iterable[int]] = ..., labels: _Optional[_Iterable[str]] = ..., features: _Optional[_Iterable[str]] = ..., job_id: _Optional[str] = ..., accuracy: _Optional[float] = ..., worker_id: _Optional[str] = ..., columns: _Optional[_Iterable[_Union[Column, _Mapping]]] = ..., language: _Optional[_Union[LanguageSettings, _Mapping]] = ..., on_device: bool = ..., version: _Optional[str] = ..., version_id: _Optional[str] = ..., base_model_id: _Optional[str] = ..., base_model_name: _Optional[str] = ...) -> None: ...

class LanguageSettings(_message.Message):
    __slots__ = ("instructions", "temperature", "max_tokens", "api_name")
    INSTRUCTIONS_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    MAX_TOKENS_FIELD_NUMBER: _ClassVar[int]
    API_NAME_FIELD_NUMBER: _ClassVar[int]
    instructions: str
    temperature: float
    max_tokens: int
    api_name: str
    def __init__(self, instructions: _Optional[str] = ..., temperature: _Optional[float] = ..., max_tokens: _Optional[int] = ..., api_name: _Optional[str] = ...) -> None: ...

class Tensor(_message.Message):
    __slots__ = ("shape", "values")
    SHAPE_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    shape: _containers.RepeatedScalarFieldContainer[int]
    values: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, shape: _Optional[_Iterable[int]] = ..., values: _Optional[_Iterable[float]] = ...) -> None: ...

class Guess(_message.Message):
    __slots__ = ("label", "probability")
    LABEL_FIELD_NUMBER: _ClassVar[int]
    PROBABILITY_FIELD_NUMBER: _ClassVar[int]
    label: str
    probability: float
    def __init__(self, label: _Optional[str] = ..., probability: _Optional[float] = ...) -> None: ...

class Box(_message.Message):
    __slots__ = ("label", "score", "left", "top", "width", "height")
    LABEL_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    LEFT_FIELD_NUMBER: _ClassVar[int]
    TOP_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    label: str
    score: float
    left: float
    top: float
    width: float
    height: float
    def __init__(self, label: _Optional[str] = ..., score: _Optional[float] = ..., left: _Optional[float] = ..., top: _Optional[float] = ..., width: _Optional[float] = ..., height: _Optional[float] = ...) -> None: ...

class ListArchitecturesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListArchitecturesResponse(_message.Message):
    __slots__ = ("architectures",)
    ARCHITECTURES_FIELD_NUMBER: _ClassVar[int]
    architectures: _containers.RepeatedCompositeFieldContainer[Architecture]
    def __init__(self, architectures: _Optional[_Iterable[_Union[Architecture, _Mapping]]] = ...) -> None: ...

class ListModelsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListModelsResponse(_message.Message):
    __slots__ = ("models",)
    MODELS_FIELD_NUMBER: _ClassVar[int]
    models: _containers.RepeatedCompositeFieldContainer[Model]
    def __init__(self, models: _Optional[_Iterable[_Union[Model, _Mapping]]] = ...) -> None: ...

class GetModelRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetModelResponse(_message.Message):
    __slots__ = ("model",)
    MODEL_FIELD_NUMBER: _ClassVar[int]
    model: Model
    def __init__(self, model: _Optional[_Union[Model, _Mapping]] = ...) -> None: ...

class CreateModelRequest(_message.Message):
    __slots__ = ("name", "description", "architecture", "weights", "labels", "input_shape", "upload")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ARCHITECTURE_FIELD_NUMBER: _ClassVar[int]
    WEIGHTS_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    INPUT_SHAPE_FIELD_NUMBER: _ClassVar[int]
    UPLOAD_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    architecture: str
    weights: bytes
    labels: _containers.RepeatedScalarFieldContainer[str]
    input_shape: _containers.RepeatedScalarFieldContainer[int]
    upload: str
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., architecture: _Optional[str] = ..., weights: _Optional[bytes] = ..., labels: _Optional[_Iterable[str]] = ..., input_shape: _Optional[_Iterable[int]] = ..., upload: _Optional[str] = ...) -> None: ...

class CreateModelResponse(_message.Message):
    __slots__ = ("model",)
    MODEL_FIELD_NUMBER: _ClassVar[int]
    model: Model
    def __init__(self, model: _Optional[_Union[Model, _Mapping]] = ...) -> None: ...

class UpdateModelRequest(_message.Message):
    __slots__ = ("id", "name", "description", "language", "on_device")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    ON_DEVICE_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    language: LanguageSettings
    on_device: bool
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., language: _Optional[_Union[LanguageSettings, _Mapping]] = ..., on_device: bool = ...) -> None: ...

class UpdateModelResponse(_message.Message):
    __slots__ = ("model",)
    MODEL_FIELD_NUMBER: _ClassVar[int]
    model: Model
    def __init__(self, model: _Optional[_Union[Model, _Mapping]] = ...) -> None: ...

class DeleteModelRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteModelResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PredictRequest(_message.Message):
    __slots__ = ("model_id", "input", "top_k", "fields", "photo", "sound")
    class FieldsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    INPUT_FIELD_NUMBER: _ClassVar[int]
    TOP_K_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    PHOTO_FIELD_NUMBER: _ClassVar[int]
    SOUND_FIELD_NUMBER: _ClassVar[int]
    model_id: str
    input: Tensor
    top_k: int
    fields: _containers.ScalarMap[str, str]
    photo: bytes
    sound: bytes
    def __init__(self, model_id: _Optional[str] = ..., input: _Optional[_Union[Tensor, _Mapping]] = ..., top_k: _Optional[int] = ..., fields: _Optional[_Mapping[str, str]] = ..., photo: _Optional[bytes] = ..., sound: _Optional[bytes] = ...) -> None: ...

class PredictResponse(_message.Message):
    __slots__ = ("output", "guesses", "duration_micros", "probabilities", "number", "value", "prediction_id", "boxes")
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    GUESSES_FIELD_NUMBER: _ClassVar[int]
    DURATION_MICROS_FIELD_NUMBER: _ClassVar[int]
    PROBABILITIES_FIELD_NUMBER: _ClassVar[int]
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    PREDICTION_ID_FIELD_NUMBER: _ClassVar[int]
    BOXES_FIELD_NUMBER: _ClassVar[int]
    output: Tensor
    guesses: _containers.RepeatedCompositeFieldContainer[Guess]
    duration_micros: int
    probabilities: Tensor
    number: bool
    value: float
    prediction_id: str
    boxes: _containers.RepeatedCompositeFieldContainer[Box]
    def __init__(self, output: _Optional[_Union[Tensor, _Mapping]] = ..., guesses: _Optional[_Iterable[_Union[Guess, _Mapping]]] = ..., duration_micros: _Optional[int] = ..., probabilities: _Optional[_Union[Tensor, _Mapping]] = ..., number: bool = ..., value: _Optional[float] = ..., prediction_id: _Optional[str] = ..., boxes: _Optional[_Iterable[_Union[Box, _Mapping]]] = ...) -> None: ...

class GenerateRequest(_message.Message):
    __slots__ = ("model_id", "prompt", "max_tokens", "temperature", "seed")
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PROMPT_FIELD_NUMBER: _ClassVar[int]
    MAX_TOKENS_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    SEED_FIELD_NUMBER: _ClassVar[int]
    model_id: str
    prompt: str
    max_tokens: int
    temperature: float
    seed: int
    def __init__(self, model_id: _Optional[str] = ..., prompt: _Optional[str] = ..., max_tokens: _Optional[int] = ..., temperature: _Optional[float] = ..., seed: _Optional[int] = ...) -> None: ...

class ChatMessage(_message.Message):
    __slots__ = ("role", "content")
    ROLE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    role: str
    content: str
    def __init__(self, role: _Optional[str] = ..., content: _Optional[str] = ...) -> None: ...

class ChatRequest(_message.Message):
    __slots__ = ("model_id", "messages", "instructions", "max_tokens", "temperature", "seed")
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGES_FIELD_NUMBER: _ClassVar[int]
    INSTRUCTIONS_FIELD_NUMBER: _ClassVar[int]
    MAX_TOKENS_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    SEED_FIELD_NUMBER: _ClassVar[int]
    model_id: str
    messages: _containers.RepeatedCompositeFieldContainer[ChatMessage]
    instructions: str
    max_tokens: int
    temperature: float
    seed: int
    def __init__(self, model_id: _Optional[str] = ..., messages: _Optional[_Iterable[_Union[ChatMessage, _Mapping]]] = ..., instructions: _Optional[str] = ..., max_tokens: _Optional[int] = ..., temperature: _Optional[float] = ..., seed: _Optional[int] = ...) -> None: ...

class ChatResponse(_message.Message):
    __slots__ = ("text", "done", "prompt_tokens", "generated_tokens", "finished", "duration_micros", "context_tokens")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    DONE_FIELD_NUMBER: _ClassVar[int]
    PROMPT_TOKENS_FIELD_NUMBER: _ClassVar[int]
    GENERATED_TOKENS_FIELD_NUMBER: _ClassVar[int]
    FINISHED_FIELD_NUMBER: _ClassVar[int]
    DURATION_MICROS_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_TOKENS_FIELD_NUMBER: _ClassVar[int]
    text: str
    done: bool
    prompt_tokens: int
    generated_tokens: int
    finished: bool
    duration_micros: int
    context_tokens: int
    def __init__(self, text: _Optional[str] = ..., done: bool = ..., prompt_tokens: _Optional[int] = ..., generated_tokens: _Optional[int] = ..., finished: bool = ..., duration_micros: _Optional[int] = ..., context_tokens: _Optional[int] = ...) -> None: ...

class GenerateStreamRequest(_message.Message):
    __slots__ = ("model_id", "prompt", "max_tokens", "temperature", "seed")
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PROMPT_FIELD_NUMBER: _ClassVar[int]
    MAX_TOKENS_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    SEED_FIELD_NUMBER: _ClassVar[int]
    model_id: str
    prompt: str
    max_tokens: int
    temperature: float
    seed: int
    def __init__(self, model_id: _Optional[str] = ..., prompt: _Optional[str] = ..., max_tokens: _Optional[int] = ..., temperature: _Optional[float] = ..., seed: _Optional[int] = ...) -> None: ...

class GenerateStreamResponse(_message.Message):
    __slots__ = ("text", "done", "prompt_tokens", "generated_tokens", "finished", "duration_micros", "context_tokens")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    DONE_FIELD_NUMBER: _ClassVar[int]
    PROMPT_TOKENS_FIELD_NUMBER: _ClassVar[int]
    GENERATED_TOKENS_FIELD_NUMBER: _ClassVar[int]
    FINISHED_FIELD_NUMBER: _ClassVar[int]
    DURATION_MICROS_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_TOKENS_FIELD_NUMBER: _ClassVar[int]
    text: str
    done: bool
    prompt_tokens: int
    generated_tokens: int
    finished: bool
    duration_micros: int
    context_tokens: int
    def __init__(self, text: _Optional[str] = ..., done: bool = ..., prompt_tokens: _Optional[int] = ..., generated_tokens: _Optional[int] = ..., finished: bool = ..., duration_micros: _Optional[int] = ..., context_tokens: _Optional[int] = ...) -> None: ...

class GenerateResponse(_message.Message):
    __slots__ = ("text", "prompt_tokens", "generated_tokens", "finished", "duration_micros")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    PROMPT_TOKENS_FIELD_NUMBER: _ClassVar[int]
    GENERATED_TOKENS_FIELD_NUMBER: _ClassVar[int]
    FINISHED_FIELD_NUMBER: _ClassVar[int]
    DURATION_MICROS_FIELD_NUMBER: _ClassVar[int]
    text: str
    prompt_tokens: int
    generated_tokens: int
    finished: bool
    duration_micros: int
    def __init__(self, text: _Optional[str] = ..., prompt_tokens: _Optional[int] = ..., generated_tokens: _Optional[int] = ..., finished: bool = ..., duration_micros: _Optional[int] = ...) -> None: ...

class GetDeviceModelRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetDeviceModelResponse(_message.Message):
    __slots__ = ("model", "weights")
    MODEL_FIELD_NUMBER: _ClassVar[int]
    WEIGHTS_FIELD_NUMBER: _ClassVar[int]
    model: Model
    weights: bytes
    def __init__(self, model: _Optional[_Union[Model, _Mapping]] = ..., weights: _Optional[bytes] = ...) -> None: ...
