from __future__ import annotations

import builtins
from typing import Any, Callable, Mapping, Optional, Union

from . import types as t
from ._base import Service, Source, poll, read_source
from ._errors import JobError
from ._transport import to_message


class DatasetService(Service):
    """Keeps the examples models learn from."""

    def list(self) -> builtins.list[t.Dataset]:
        """Every dataset the caller may see."""
        return list(self._call("mimir.v1.DatasetService.ListDatasets", t.ListDatasetsRequest()).datasets)

    def get(self, id: str) -> t.GetDatasetResponse:
        """A dataset with its first few rows."""
        return self._call("mimir.v1.DatasetService.GetDataset", t.GetDatasetRequest(id=id))

    def create(
        self, request: Union[t.CreateDatasetRequest, Mapping[str, Any], None] = None, **fields: Any
    ) -> t.CreateDatasetResponse:
        """Store a dataset: a CSV, a ZIP of photos, a database query, files
        in a bucket, or a template's example data. The response says how
        well the data fits."""
        return self._call("mimir.v1.DatasetService.CreateDataset", to_message(t.CreateDatasetRequest, request, fields))

    def upload_csv(self, name: str, csv: Source, target: str = "") -> t.CreateDatasetResponse:
        """Store a table with a header row. ``target`` is the column to
        predict; "" means the last one. ``csv`` is bytes, a binary file
        object or a path."""
        req = t.CreateDatasetRequest(name=name, kind=t.DATASET_KIND_TABLE, csv=read_source(csv), target=target)
        return self.create(req)

    def upload_photos(self, name: str, zip: Source) -> t.CreateDatasetResponse:
        """Store a ZIP of photos, with one folder per answer."""
        return self.create(t.CreateDatasetRequest(name=name, kind=t.DATASET_KIND_PHOTOS, archive=read_source(zip)))

    def upload_sounds(self, name: str, zip: Source) -> t.CreateDatasetResponse:
        """Store a ZIP of WAV sounds, with one folder per answer."""
        return self.create(t.CreateDatasetRequest(name=name, kind=t.DATASET_KIND_SOUNDS, archive=read_source(zip)))

    def upload_boxes(self, name: str, zip: Source) -> t.CreateDatasetResponse:
        """Store a ZIP of photos and a boxes.csv saying where the things in
        them are: one row per thing, with the columns photo, what, left,
        top, width and height (or right and bottom), in pixels."""
        return self.create(t.CreateDatasetRequest(name=name, kind=t.DATASET_KIND_BOXES, archive=read_source(zip)))

    def upload_text(self, name: str, text: Source) -> t.CreateDatasetResponse:
        """Store writing for a language model to learn from: plain text, or
        JSON Lines of chats, prompts and completions."""
        return self.create(t.CreateDatasetRequest(name=name, kind=t.DATASET_KIND_TEXT, text=read_source(text)))

    def test_query(self, connection: Union[t.Connection, Mapping[str, Any]], query: str) -> t.TestQueryResponse:
        """Run a database query and return its columns, a few rows and how
        many rows it has, so the answer column can be picked before a
        dataset is made from it."""
        req = to_message(t.TestQueryRequest, {"connection": connection, "query": query}, {})
        return self._call("mimir.v1.DatasetService.TestQuery", req)

    def test_bucket(
        self, request: Union[t.TestBucketRequest, Mapping[str, Any], None] = None, **fields: Any
    ) -> t.TestBucketResponse:
        """Read a file, or a folder ending in a slash, from S3-compatible
        storage and say what is there: how many files, and for a table its
        columns and a few rows."""
        return self._call("mimir.v1.DatasetService.TestBucket", to_message(t.TestBucketRequest, request, fields))

    def refresh(self, id: str) -> t.Dataset:
        """Run a database dataset's query again and replace its rows."""
        return self._call("mimir.v1.DatasetService.RefreshDataset", t.RefreshDatasetRequest(id=id)).dataset

    def check(
        self, request: Union[t.CheckDatasetRequest, Mapping[str, Any], None] = None, **fields: Any
    ) -> t.CheckDatasetResponse:
        """Check a dataset against a template, and with ``apply`` keep the
        match."""
        return self._call("mimir.v1.DatasetService.CheckDataset", to_message(t.CheckDatasetRequest, request, fields))

    def delete(self, id: str) -> None:
        """Remove a dataset."""
        self._call("mimir.v1.DatasetService.DeleteDataset", t.DeleteDatasetRequest(id=id))


class TrainingService(Service):
    """Teaches models and follows their progress."""

    def list(self) -> builtins.list[t.Job]:
        """Every training run the caller may see."""
        return list(self._call("mimir.v1.TrainingService.ListJobs", t.ListJobsRequest()).jobs)

    def get(self, id: str) -> t.Job:
        """One training run with its progress."""
        return self._call("mimir.v1.TrainingService.GetJob", t.GetJobRequest(id=id)).job

    def start(self, request: Union[t.CreateJobRequest, Mapping[str, Any], None] = None, **fields: Any) -> t.Job:
        """Queue a training run. ``wait`` follows it to the end."""
        return self._call("mimir.v1.TrainingService.CreateJob", to_message(t.CreateJobRequest, request, fields)).job

    def cancel(self, id: str) -> t.Job:
        """Stop a queued or running run, keeping its progress."""
        return self._call("mimir.v1.TrainingService.CancelJob", t.CancelJobRequest(id=id)).job

    def resume(self, id: str) -> t.Job:
        """Queue a cancelled or failed run again, from its last finished
        epoch."""
        return self._call("mimir.v1.TrainingService.ResumeJob", t.ResumeJobRequest(id=id)).job

    def delete(self, id: str) -> None:
        """Remove a run. The model it made stays."""
        self._call("mimir.v1.TrainingService.DeleteJob", t.DeleteJobRequest(id=id))

    def compare(self, *ids: str) -> t.CompareJobsResponse:
        """Two to six runs side by side, with every pass of each, what their
        settings differ in, and the id of the best of them."""
        return self._call("mimir.v1.TrainingService.CompareJobs", t.CompareJobsRequest(ids=list(ids)))

    def keep_learning(self, id: str, every_seconds: float, min_new_rows: int = 0) -> t.Job:
        """Make a run learn again from fresh examples every
        ``every_seconds``; 0 stops it. ``min_new_rows`` above 0 makes each
        pass wait until the source has that many new rows, looking again
        every interval until it has; 0 starts a pass every interval."""
        req = t.SetRepeatRequest(id=id, repeat_seconds=int(every_seconds), min_new_rows=min_new_rows)
        return self._call("mimir.v1.TrainingService.SetRepeat", req).job

    def wait(
        self,
        id: str,
        *,
        interval: float = 2.0,
        timeout: Optional[float] = None,
        on_progress: Optional[Callable[[t.Job], Any]] = None,
    ) -> t.Job:
        """Follow a run until it succeeds, fails or is cancelled, looking
        every ``interval`` seconds, and return it as it ended. A run that
        fails or is cancelled raises JobError, which holds the run. Raises
        TimeoutError after ``timeout`` seconds (None waits for ever)."""
        job = poll(lambda: self.get(id), _ended, interval, timeout, on_progress)
        if job.status != t.JOB_STATUS_SUCCEEDED:
            raise JobError(job)
        return job


def _ended(item: Any) -> bool:
    return item.status in (t.JOB_STATUS_SUCCEEDED, t.JOB_STATUS_FAILED, t.JOB_STATUS_CANCELLED)
