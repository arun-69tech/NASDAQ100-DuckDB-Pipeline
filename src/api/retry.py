"""Retry policy helpers for external API calls."""

import logging
from collections.abc import Callable
from typing import ParamSpec, TypeVar

from requests import RequestException
from tenacity import (
    RetryCallState,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

LOGGER = logging.getLogger(__name__)

P = ParamSpec("P")
R = TypeVar("R")


class ExternalAPIRetryableError(RuntimeError):
    """Raised for API failures that should be retried."""


def log_retry_attempt(retry_state: RetryCallState) -> None:
    """Log retry attempts triggered by retryable exceptions.

    Parameters:
        retry_state: Tenacity retry state for the failed call.

    Returns:
        None.
    """
    exception = retry_state.outcome.exception() if retry_state.outcome else None
    LOGGER.warning(
        "Retrying external API call",
        extra={
            "attempt": retry_state.attempt_number,
            "exception": repr(exception),
        },
    )


def alpha_vantage_retry(
    function: Callable[P, R],
) -> Callable[P, R]:
    """Apply the Alpha Vantage retry policy to a callable.

    Parameters:
        function: Callable that performs an Alpha Vantage operation.

    Returns:
        Wrapped callable with exponential backoff.
    """
    return retry(
        retry=retry_if_exception_type((RequestException, ExternalAPIRetryableError)),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        stop=stop_after_attempt(5),
        before_sleep=log_retry_attempt,
        reraise=True,
    )(function)
