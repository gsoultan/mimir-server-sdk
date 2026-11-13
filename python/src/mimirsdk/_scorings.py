from __future__ import annotations

import builtins
import os
from typing import IO, Any, Callable, Mapping, Optional, Union
from urllib.parse import quote

from . import types as t
from ._base import Service, Source, poll, read_source
from ._errors import ScoringError
from ._training import _ended
from ._transport import to_message

Dest = Union[str, "os.PathLike[str]", IO[bytes]]


def download_to(transport: Any, path: str, dest: Dest) -> int:
    """Stream the file at path to dest, a path or a binary file object,
    and return how many bytes were written."""
    if isinstance(dest, (str, os.PathLike)):
        with open(dest, "wb") as f:
            return transport.download(path, f.write)
    return transport.download(path, dest.write)


class ScoringService(Service):
    """Answers every row of a table with one model at once: a CSV, a
    database query, files in storage or a dataset. The server scores in the
    background and keeps the rows with each answer next to them as a CSV,
    which ``download`` fetches."""

    def list(self, model_id: str = "") -> builtins.list[t.Scoring]:
        """Every scoring the caller may see, or one model's, newest first."""
        res = self._call("mimir.v1.ScoringService.ListScorings", t.ListScoringsRequest(model_id=model_id))
        return list(res.scorings)

    def get(self, id: str) -> t.GetScoringResponse:
        """A scoring with the first rows of its results."""
        return self._call("mimir.v1.ScoringService.GetScoring", t.GetScoringRequest(id=id))

    def create(
        self, request: Union[t.CreateScoringRequest, Mapping[str, Any], None] = None, **fields: Any
    ) -> t.Scoring:
        """Queue a scoring. Give the rows one way: ``csv``, ``connection``
        and ``query``, ``bucket`` and ``path``, or ``dataset_id``. ``wait``
        follows it to the end."""
        req = to_message(t.CreateScoringRequest, request, fields)
        return self._call("mimir.v1.ScoringService.CreateScoring", req).scoring

    def score_csv(self, model_id: str, csv: Source, name: str = "") -> t.Scoring:
        """Queue a scoring of a CSV with a header row; it needs no answer
        column. An empty name lets the server choose one."""
        return self.create(t.CreateScoringRequest(model_id=model_id, name=name, csv=read_source(csv)))

    def score_query(
        self,
        model_id: str,
        connection: Union[t.Connection, Mapping[str, Any]],
        query: str,
        *,
        name: str = "",
        every_seconds: float = 0,
    ) -> t.Scoring:
        """Queue a scoring of a database query's rows, run again every
        ``every_seconds`` when that is at least an hour; 0 runs it once. It
        needs an admin."""
        return self.create(
            {"model_id": model_id, "name": name, "connection": connection, "query": query},
            repeat_seconds=int(every_seconds),
        )

    def run(self, id: str) -> t.Scoring:
        """Queue a finished, failed or cancelled scoring again now, fetching
        its rows afresh."""
        return self._call("mimir.v1.ScoringService.RunScoring", t.RunScoringRequest(id=id)).scoring

    def cancel(self, id: str) -> t.Scoring:
        """Stop a queued or running scoring."""
        return self._call("mimir.v1.ScoringService.CancelScoring", t.CancelScoringRequest(id=id)).scoring

    def set_repeat(self, id: str, every_seconds: float) -> t.Scoring:
        """Change how often a scoring from a database or storage runs again,
        from an hour to 30 days; 0 stops it."""
        req = t.SetScoringRepeatRequest(id=id, repeat_seconds=int(every_seconds))
        return self._call("mimir.v1.ScoringService.SetScoringRepeat", req).scoring

    def delete(self, id: str) -> None:
        """Remove a scoring and its results. A running one must be cancelled
        first."""
        self._call("mimir.v1.ScoringService.DeleteScoring", t.DeleteScoringRequest(id=id))

    def wait(
        self,
        id: str,
        *,
        interval: float = 2.0,
        timeout: Optional[float] = None,
        on_progress: Optional[Callable[[t.Scoring], Any]] = None,
    ) -> t.Scoring:
        """Follow a scoring until it succeeds, fails or is cancelled, and
        return it as it ended. One that fails or is cancelled raises
        ScoringError, which holds the scoring."""
        sc = poll(lambda: self.get(id).scoring, _ended, interval, timeout, on_progress)
        if sc.status != t.JOB_STATUS_SUCCEEDED:
            raise ScoringError(sc)
        return sc

    def download(self, id: str, dest: Dest) -> int:
        """Write a scoring's latest results to ``dest``, a path or a binary
        file object: a CSV of every row, in order, with the model's answer
        after it (predicted, then confidence or suggestions, and problem,
        which says why a row couldn't be answered). Returns how many bytes
        it wrote."""
        return download_to(self._t, f"/api/scorings/{quote(id, safe='')}/results", dest)
