from __future__ import annotations

import builtins
from typing import Any, Callable, Mapping, Optional, Union

from . import types as t
from ._base import Service, poll
from ._transport import to_message


def _scoring(s: t.BenchmarkScore) -> bool:
    return s.status in (t.JOB_STATUS_QUEUED, t.JOB_STATUS_RUNNING)


class BenchmarkService(Service):
    """Keeps the fixed tests models are ranked on. A benchmark's rows are
    frozen from a dataset and left out of training on it, so every model
    answers examples it never learned from, and the same ones."""

    def list(self, dataset_id: str = "") -> builtins.list[t.Benchmark]:
        """Every benchmark the caller may see, or those frozen from one
        dataset."""
        res = self._call("mimir.v1.BenchmarkService.ListBenchmarks", t.ListBenchmarksRequest(dataset_id=dataset_id))
        return list(res.benchmarks)

    def get(self, id: str) -> t.GetBenchmarkResponse:
        """A benchmark with its leaderboard, best first, and the models that
        could still take it."""
        return self._call("mimir.v1.BenchmarkService.GetBenchmark", t.GetBenchmarkRequest(id=id))

    def create(
        self, request: Union[t.CreateBenchmarkRequest, Mapping[str, Any], None] = None, **fields: Any
    ) -> t.Benchmark:
        """Make a benchmark. ``share`` is the part of the dataset's rows to
        keep aside, from 0.05 to 0.5, or 0 for a fifth; ``csv`` instead
        holds test rows of your own, with the dataset's columns."""
        req = to_message(t.CreateBenchmarkRequest, request, fields)
        return self._call("mimir.v1.BenchmarkService.CreateBenchmark", req).benchmark

    def freeze(self, name: str, dataset_id: str, share: float = 0) -> t.Benchmark:
        """Make a benchmark that keeps ``share`` of a dataset's rows aside;
        0 keeps a fifth."""
        return self.create(t.CreateBenchmarkRequest(name=name, dataset_id=dataset_id, share=share))

    def delete(self, id: str) -> None:
        """Remove a benchmark, its rows and its scores. The models stay."""
        self._call("mimir.v1.BenchmarkService.DeleteBenchmark", t.DeleteBenchmarkRequest(id=id))

    def score(self, benchmark_id: str, *model_ids: str) -> builtins.list[t.BenchmarkScore]:
        """Put models on a benchmark's leaderboard. Scoring runs on the
        server; the scores come back queued, and ``wait_for_scores``
        follows them. A model scored before is scored again with the weights
        it has now."""
        req = t.ScoreModelsRequest(benchmark_id=benchmark_id, model_ids=list(model_ids))
        return list(self._call("mimir.v1.BenchmarkService.ScoreModels", req).scores)

    def wait_for_scores(
        self,
        benchmark_id: str,
        *,
        interval: float = 2.0,
        timeout: Optional[float] = None,
        on_progress: Optional[Callable[[builtins.list[t.BenchmarkScore]], Any]] = None,
    ) -> builtins.list[t.BenchmarkScore]:
        """Follow a benchmark until no score on it is still queued or
        running, and return the leaderboard, best first. A score that failed
        is in the list with its reason, and is not an error here."""
        return poll(
            lambda: list(self.get(benchmark_id).scores),
            lambda scores: not any(_scoring(s) for s in scores),
            interval,
            timeout,
            on_progress,
        )

    def leader(self, benchmark_id: str) -> Optional[t.BenchmarkScore]:
        """The best finished score on a benchmark, or None when none has
        finished."""
        for sc in self.get(benchmark_id).scores:
            if sc.rank == 1:
                return sc
        return None
