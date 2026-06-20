"""Timing utilities for logging pipeline duration."""

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from time import perf_counter


@dataclass(slots=True)
class TimerResult:
    """Elapsed-time container populated by `timer`."""

    elapsed_seconds: float = 0.0


@contextmanager
def timer() -> Iterator[TimerResult]:
    """Measure elapsed wall-clock time for a code block.

    Yields:
        A `TimerResult` updated after the context exits.
    """
    result = TimerResult()
    start_time = perf_counter()
    try:
        yield result
    finally:
        result.elapsed_seconds = perf_counter() - start_time
