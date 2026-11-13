from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TemplateCategory(_message.Message):
    __slots__ = ("id", "label", "blurb", "icon")
    ID_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    BLURB_FIELD_NUMBER: _ClassVar[int]
    ICON_FIELD_NUMBER: _ClassVar[int]
    id: str
    label: str
    blurb: str
    icon: str
    def __init__(self, id: _Optional[str] = ..., label: _Optional[str] = ..., blurb: _Optional[str] = ..., icon: _Optional[str] = ...) -> None: ...

class TemplateColumn(_message.Message):
    __slots__ = ("name", "kind", "meaning", "examples")
    NAME_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    MEANING_FIELD_NUMBER: _ClassVar[int]
    EXAMPLES_FIELD_NUMBER: _ClassVar[int]
    name: str
    kind: str
    meaning: str
    examples: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, name: _Optional[str] = ..., kind: _Optional[str] = ..., meaning: _Optional[str] = ..., examples: _Optional[_Iterable[str]] = ...) -> None: ...

class TemplateFolder(_message.Message):
    __slots__ = ("name", "meaning", "count")
    NAME_FIELD_NUMBER: _ClassVar[int]
    MEANING_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    name: str
    meaning: str
    count: int
    def __init__(self, name: _Optional[str] = ..., meaning: _Optional[str] = ..., count: _Optional[int] = ...) -> None: ...

class Template(_message.Message):
    __slots__ = ("id", "category", "kind", "data", "name", "question", "predicts", "row_means", "source", "source_short", "rows_min", "rows_good", "rows_great", "balance", "table", "tips", "columns", "folders", "architecture", "query")
    ID_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    QUESTION_FIELD_NUMBER: _ClassVar[int]
    PREDICTS_FIELD_NUMBER: _ClassVar[int]
    ROW_MEANS_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_SHORT_FIELD_NUMBER: _ClassVar[int]
    ROWS_MIN_FIELD_NUMBER: _ClassVar[int]
    ROWS_GOOD_FIELD_NUMBER: _ClassVar[int]
    ROWS_GREAT_FIELD_NUMBER: _ClassVar[int]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    TABLE_FIELD_NUMBER: _ClassVar[int]
    TIPS_FIELD_NUMBER: _ClassVar[int]
    COLUMNS_FIELD_NUMBER: _ClassVar[int]
    FOLDERS_FIELD_NUMBER: _ClassVar[int]
    ARCHITECTURE_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    id: str
    category: str
    kind: str
    data: str
    name: str
    question: str
    predicts: str
    row_means: str
    source: str
    source_short: str
    rows_min: int
    rows_good: int
    rows_great: int
    balance: str
    table: str
    tips: _containers.RepeatedScalarFieldContainer[str]
    columns: _containers.RepeatedCompositeFieldContainer[TemplateColumn]
    folders: _containers.RepeatedCompositeFieldContainer[TemplateFolder]
    architecture: str
    query: str
    def __init__(self, id: _Optional[str] = ..., category: _Optional[str] = ..., kind: _Optional[str] = ..., data: _Optional[str] = ..., name: _Optional[str] = ..., question: _Optional[str] = ..., predicts: _Optional[str] = ..., row_means: _Optional[str] = ..., source: _Optional[str] = ..., source_short: _Optional[str] = ..., rows_min: _Optional[int] = ..., rows_good: _Optional[int] = ..., rows_great: _Optional[int] = ..., balance: _Optional[str] = ..., table: _Optional[str] = ..., tips: _Optional[_Iterable[str]] = ..., columns: _Optional[_Iterable[_Union[TemplateColumn, _Mapping]]] = ..., folders: _Optional[_Iterable[_Union[TemplateFolder, _Mapping]]] = ..., architecture: _Optional[str] = ..., query: _Optional[str] = ...) -> None: ...

class ListTemplatesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListTemplatesResponse(_message.Message):
    __slots__ = ("categories", "templates")
    CATEGORIES_FIELD_NUMBER: _ClassVar[int]
    TEMPLATES_FIELD_NUMBER: _ClassVar[int]
    categories: _containers.RepeatedCompositeFieldContainer[TemplateCategory]
    templates: _containers.RepeatedCompositeFieldContainer[Template]
    def __init__(self, categories: _Optional[_Iterable[_Union[TemplateCategory, _Mapping]]] = ..., templates: _Optional[_Iterable[_Union[Template, _Mapping]]] = ...) -> None: ...

class GetTemplateExampleRequest(_message.Message):
    __slots__ = ("template_id",)
    TEMPLATE_ID_FIELD_NUMBER: _ClassVar[int]
    template_id: str
    def __init__(self, template_id: _Optional[str] = ...) -> None: ...

class GetTemplateExampleResponse(_message.Message):
    __slots__ = ("file_name", "content_type", "data")
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    CONTENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    file_name: str
    content_type: str
    data: bytes
    def __init__(self, file_name: _Optional[str] = ..., content_type: _Optional[str] = ..., data: _Optional[bytes] = ...) -> None: ...

class DataCheck(_message.Message):
    __slots__ = ("rows", "skipped", "answer_column", "columns", "extra_columns", "answers", "notes", "missing_photos", "missing_photo_count", "folders", "verdict", "number_answer", "rows_min", "rows_good", "rows_great")
    ROWS_FIELD_NUMBER: _ClassVar[int]
    SKIPPED_FIELD_NUMBER: _ClassVar[int]
    ANSWER_COLUMN_FIELD_NUMBER: _ClassVar[int]
    COLUMNS_FIELD_NUMBER: _ClassVar[int]
    EXTRA_COLUMNS_FIELD_NUMBER: _ClassVar[int]
    ANSWERS_FIELD_NUMBER: _ClassVar[int]
    NOTES_FIELD_NUMBER: _ClassVar[int]
    MISSING_PHOTOS_FIELD_NUMBER: _ClassVar[int]
    MISSING_PHOTO_COUNT_FIELD_NUMBER: _ClassVar[int]
    FOLDERS_FIELD_NUMBER: _ClassVar[int]
    VERDICT_FIELD_NUMBER: _ClassVar[int]
    NUMBER_ANSWER_FIELD_NUMBER: _ClassVar[int]
    ROWS_MIN_FIELD_NUMBER: _ClassVar[int]
    ROWS_GOOD_FIELD_NUMBER: _ClassVar[int]
    ROWS_GREAT_FIELD_NUMBER: _ClassVar[int]
    rows: int
    skipped: int
    answer_column: str
    columns: _containers.RepeatedCompositeFieldContainer[ColumnCheck]
    extra_columns: _containers.RepeatedScalarFieldContainer[str]
    answers: _containers.RepeatedCompositeFieldContainer[AnswerCount]
    notes: _containers.RepeatedCompositeFieldContainer[CheckNote]
    missing_photos: _containers.RepeatedScalarFieldContainer[str]
    missing_photo_count: int
    folders: _containers.RepeatedCompositeFieldContainer[FolderCheck]
    verdict: str
    number_answer: bool
    rows_min: int
    rows_good: int
    rows_great: int
    def __init__(self, rows: _Optional[int] = ..., skipped: _Optional[int] = ..., answer_column: _Optional[str] = ..., columns: _Optional[_Iterable[_Union[ColumnCheck, _Mapping]]] = ..., extra_columns: _Optional[_Iterable[str]] = ..., answers: _Optional[_Iterable[_Union[AnswerCount, _Mapping]]] = ..., notes: _Optional[_Iterable[_Union[CheckNote, _Mapping]]] = ..., missing_photos: _Optional[_Iterable[str]] = ..., missing_photo_count: _Optional[int] = ..., folders: _Optional[_Iterable[_Union[FolderCheck, _Mapping]]] = ..., verdict: _Optional[str] = ..., number_answer: bool = ..., rows_min: _Optional[int] = ..., rows_good: _Optional[int] = ..., rows_great: _Optional[int] = ...) -> None: ...

class ColumnCheck(_message.Message):
    __slots__ = ("name", "kind", "found", "found_kind", "empty", "unreadable", "words", "status", "answer")
    NAME_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    FOUND_FIELD_NUMBER: _ClassVar[int]
    FOUND_KIND_FIELD_NUMBER: _ClassVar[int]
    EMPTY_FIELD_NUMBER: _ClassVar[int]
    UNREADABLE_FIELD_NUMBER: _ClassVar[int]
    WORDS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ANSWER_FIELD_NUMBER: _ClassVar[int]
    name: str
    kind: str
    found: str
    found_kind: str
    empty: int
    unreadable: int
    words: float
    status: str
    answer: bool
    def __init__(self, name: _Optional[str] = ..., kind: _Optional[str] = ..., found: _Optional[str] = ..., found_kind: _Optional[str] = ..., empty: _Optional[int] = ..., unreadable: _Optional[int] = ..., words: _Optional[float] = ..., status: _Optional[str] = ..., answer: bool = ...) -> None: ...

class FolderCheck(_message.Message):
    __slots__ = ("name", "photos", "expected")
    NAME_FIELD_NUMBER: _ClassVar[int]
    PHOTOS_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_FIELD_NUMBER: _ClassVar[int]
    name: str
    photos: int
    expected: bool
    def __init__(self, name: _Optional[str] = ..., photos: _Optional[int] = ..., expected: bool = ...) -> None: ...

class AnswerCount(_message.Message):
    __slots__ = ("value", "count")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    value: str
    count: int
    def __init__(self, value: _Optional[str] = ..., count: _Optional[int] = ...) -> None: ...

class CheckNote(_message.Message):
    __slots__ = ("level", "title", "body")
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    level: str
    title: str
    body: str
    def __init__(self, level: _Optional[str] = ..., title: _Optional[str] = ..., body: _Optional[str] = ...) -> None: ...
