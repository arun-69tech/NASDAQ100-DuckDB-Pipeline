"""Alpha Vantage API client."""

from dataclasses import dataclass
from datetime import date
from typing import Any

import requests

from config.constants import (
    ALPHA_VANTAGE_DAILY_FUNCTION,
    ALPHA_VANTAGE_TIME_SERIES_KEY,
)
from src.api.retry import ExternalAPIRetryableError, alpha_vantage_retry
from src.utils.logger import get_logger

LOGGER = get_logger(__name__)


class AlphaVantageError(RuntimeError):
    """Base exception for Alpha Vantage client failures."""


class AlphaVantageResponseError(AlphaVantageError):
    """Raised when Alpha Vantage returns an invalid or error response."""


class AlphaVantageRateLimitError(AlphaVantageResponseError, ExternalAPIRetryableError):
    """Raised when Alpha Vantage returns a retryable rate-limit response."""


@dataclass(frozen=True, slots=True)
class AlphaVantageDailyBar:
    """Typed daily bar extracted from an Alpha Vantage response."""

    ticker: str
    price_date: date
    open: str
    high: str
    low: str
    close: str
    volume: str


class AlphaVantageClient:
    """Client for fetching daily OHLCV data from Alpha Vantage."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        timeout_seconds: int,
        output_size: str,
        session: requests.Session | None = None,
    ) -> None:
        """Initialize the Alpha Vantage client.

        Parameters:
            api_key: Alpha Vantage API key.
            base_url: Alpha Vantage REST endpoint.
            timeout_seconds: Request timeout in seconds.
            output_size: Alpha Vantage output size, usually `compact` or `full`.
            session: Optional requests session for dependency injection.
        """
        self._api_key = api_key
        self._base_url = base_url
        self._timeout_seconds = timeout_seconds
        self._output_size = output_size
        self._session = session or requests.Session()

    @alpha_vantage_retry
    def fetch_daily_prices(self, ticker: str) -> list[AlphaVantageDailyBar]:
        """Fetch daily OHLCV bars for a ticker.

        Parameters:
            ticker: Stock ticker symbol.

        Returns:
            List of typed daily bars sorted by date ascending.

        Raises:
            requests.RequestException: If the HTTP request fails.
            AlphaVantageResponseError: If the API payload is invalid.
        """
        normalized_ticker = ticker.strip().upper()
        LOGGER.info("Fetching Alpha Vantage daily prices for %s", normalized_ticker)

        response = self._session.get(
            self._base_url,
            params={
                "function": ALPHA_VANTAGE_DAILY_FUNCTION,
                "symbol": normalized_ticker,
                "outputsize": self._output_size,
                "apikey": self._api_key,
            },
            timeout=self._timeout_seconds,
        )
        response.raise_for_status()

        try:
            payload = response.json()
        except ValueError as exc:
            raise AlphaVantageResponseError(
                f"Alpha Vantage returned non-JSON response for {normalized_ticker}."
            ) from exc

        self._validate_payload(payload, normalized_ticker)
        return self._parse_daily_bars(payload, normalized_ticker)

    def _validate_payload(self, payload: dict[str, Any], ticker: str) -> None:
        """Validate high-level Alpha Vantage response structure.

        Parameters:
            payload: Decoded JSON payload.
            ticker: Requested ticker symbol.

        Returns:
            None.

        Raises:
            AlphaVantageResponseError: If the response contains an API error.
        """
        if not payload:
            raise AlphaVantageResponseError(f"Empty API response for ticker {ticker}.")

        error_message = payload.get("Error Message")
        if error_message:
            raise AlphaVantageResponseError(
                f"Alpha Vantage returned an error for {ticker}: {error_message}"
            )

        rate_limit_message = payload.get("Note") or payload.get("Information")
        if rate_limit_message and ALPHA_VANTAGE_TIME_SERIES_KEY not in payload:
            raise AlphaVantageRateLimitError(
                f"Alpha Vantage returned a rate-limit or informational response "
                f"for {ticker}: {rate_limit_message}"
            )

        time_series = payload.get(ALPHA_VANTAGE_TIME_SERIES_KEY)
        if not isinstance(time_series, dict) or not time_series:
            raise AlphaVantageResponseError(
                f"Missing or empty daily time series for ticker {ticker}."
            )

    def _parse_daily_bars(
        self,
        payload: dict[str, Any],
        ticker: str,
    ) -> list[AlphaVantageDailyBar]:
        """Parse Alpha Vantage response data into typed daily bars.

        Parameters:
            payload: Validated Alpha Vantage payload.
            ticker: Requested ticker symbol.

        Returns:
            List of typed bars sorted by date ascending.

        Raises:
            AlphaVantageResponseError: If a response date is malformed.
        """
        time_series = payload[ALPHA_VANTAGE_TIME_SERIES_KEY]
        bars: list[AlphaVantageDailyBar] = []

        for raw_date, raw_bar in time_series.items():
            try:
                price_date = date.fromisoformat(raw_date)
            except ValueError as exc:
                raise AlphaVantageResponseError(
                    f"Invalid date key in API response for ticker {ticker}: {raw_date}."
                ) from exc

            if not isinstance(raw_bar, dict):
                raise AlphaVantageResponseError(
                    f"Invalid daily bar structure for ticker {ticker} on {raw_date}."
                )

            bars.append(
                AlphaVantageDailyBar(
                    ticker=ticker,
                    price_date=price_date,
                    open=str(raw_bar.get("1. open", "")),
                    high=str(raw_bar.get("2. high", "")),
                    low=str(raw_bar.get("3. low", "")),
                    close=str(raw_bar.get("4. close", "")),
                    volume=str(raw_bar.get("5. volume", "")),
                )
            )

        return sorted(bars, key=lambda bar: bar.price_date)
