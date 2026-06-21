"""Yahoo Finance market data client."""

from dataclasses import dataclass
from datetime import date
from typing import Any

import pandas as pd
import yfinance as yf

from config.constants import YAHOO_FINANCE_INTERVAL, YAHOO_FINANCE_PERIOD
from src.utils.logger import get_logger

LOGGER = get_logger(__name__)


class YahooFinanceError(RuntimeError):
    """Raised when Yahoo Finance data cannot be fetched or parsed."""


@dataclass(frozen=True, slots=True)
class YahooFinanceDailyBar:
    """Typed daily OHLCV bar returned by Yahoo Finance."""

    ticker: str
    price_date: date
    open: str
    high: str
    low: str
    close: str
    volume: str


class YahooFinanceClient:
    """Client for downloading daily OHLCV data from Yahoo Finance."""

    def __init__(
        self,
        *,
        period: str = YAHOO_FINANCE_PERIOD,
        interval: str = YAHOO_FINANCE_INTERVAL,
    ) -> None:
        """Initialize the Yahoo Finance client.

        Parameters:
            period: yfinance period value, such as `max` or `1y`.
            interval: yfinance interval value, such as `1d`.
        """
        self._period = period
        self._interval = interval

    def fetch_daily_prices(self, ticker: str) -> list[YahooFinanceDailyBar]:
        """Fetch daily OHLCV bars for one ticker.

        Parameters:
            ticker: Stock ticker symbol.

        Returns:
            List of typed daily bars sorted by date ascending.

        Raises:
            YahooFinanceError: If Yahoo Finance returns no usable data.
        """
        data_by_ticker = self.fetch_daily_prices_for_tickers([ticker])
        return data_by_ticker.get(ticker.strip().upper(), [])

    def fetch_daily_prices_for_tickers(
        self,
        tickers: list[str],
    ) -> dict[str, list[YahooFinanceDailyBar]]:
        """Fetch daily OHLCV bars for multiple tickers in one request.

        Parameters:
            tickers: Stock ticker symbols.

        Returns:
            Mapping of ticker to typed daily bars.

        Raises:
            YahooFinanceError: If no tickers are provided or no data is returned.
        """
        normalized_tickers = _normalize_tickers(tickers)
        if not normalized_tickers:
            raise YahooFinanceError("At least one ticker is required.")

        LOGGER.info(
            "Downloading Yahoo Finance daily prices for %s ticker(s).",
            len(normalized_tickers),
        )
        dataframe = yf.download(
            tickers=normalized_tickers,
            period=self._period,
            interval=self._interval,
            group_by="ticker",
            auto_adjust=False,
            actions=False,
            threads=True,
            progress=False,
        )

        if dataframe.empty:
            raise YahooFinanceError("Yahoo Finance returned no price data.")

        return self._parse_downloaded_data(dataframe, normalized_tickers)

    def _parse_downloaded_data(
        self,
        dataframe: pd.DataFrame,
        tickers: list[str],
    ) -> dict[str, list[YahooFinanceDailyBar]]:
        """Parse a yfinance dataframe into typed bars.

        Parameters:
            dataframe: DataFrame returned by yfinance.
            tickers: Requested ticker symbols.

        Returns:
            Mapping of ticker to daily bars. Tickers with no rows are omitted.
        """
        parsed_data: dict[str, list[YahooFinanceDailyBar]] = {}

        if len(tickers) == 1 and not isinstance(dataframe.columns, pd.MultiIndex):
            bars = self._parse_ticker_frame(tickers[0], dataframe)
            if bars:
                parsed_data[tickers[0]] = bars
            return parsed_data

        for ticker in tickers:
            if ticker not in dataframe.columns.get_level_values(0):
                LOGGER.warning(
                    "Yahoo Finance returned no columns for ticker %s.",
                    ticker,
                )
                continue

            ticker_frame = dataframe[ticker].dropna(how="all")
            bars = self._parse_ticker_frame(ticker, ticker_frame)
            if bars:
                parsed_data[ticker] = bars
            else:
                LOGGER.warning("Yahoo Finance returned no usable rows for %s.", ticker)

        return parsed_data

    def _parse_ticker_frame(
        self,
        ticker: str,
        dataframe: pd.DataFrame,
    ) -> list[YahooFinanceDailyBar]:
        """Parse one ticker dataframe into typed daily bars.

        Parameters:
            ticker: Stock ticker symbol.
            dataframe: Ticker-specific OHLCV dataframe.

        Returns:
            List of daily bars sorted by date ascending.
        """
        required_columns = ("Open", "High", "Low", "Close", "Volume")
        missing_columns = [
            column for column in required_columns if column not in dataframe.columns
        ]
        if missing_columns:
            LOGGER.warning(
                "Yahoo Finance data for %s is missing columns: %s.",
                ticker,
                ", ".join(missing_columns),
            )
            return []

        bars: list[YahooFinanceDailyBar] = []
        clean_frame = dataframe.dropna(subset=list(required_columns), how="any")

        for index_value, row in clean_frame.iterrows():
            price_date = _coerce_price_date(index_value)
            bars.append(
                YahooFinanceDailyBar(
                    ticker=ticker,
                    price_date=price_date,
                    open=_stringify_value(row["Open"]),
                    high=_stringify_value(row["High"]),
                    low=_stringify_value(row["Low"]),
                    close=_stringify_value(row["Close"]),
                    volume=_stringify_value(row["Volume"]),
                )
            )

        return sorted(bars, key=lambda bar: bar.price_date)


def _normalize_tickers(tickers: list[str]) -> list[str]:
    """Normalize and deduplicate ticker symbols.

    Parameters:
        tickers: Raw ticker symbols.

    Returns:
        Unique uppercase ticker symbols in input order.
    """
    normalized_tickers: list[str] = []
    seen_tickers: set[str] = set()

    for raw_ticker in tickers:
        ticker = raw_ticker.strip().upper()
        if ticker and ticker not in seen_tickers:
            normalized_tickers.append(ticker)
            seen_tickers.add(ticker)

    return normalized_tickers


def _coerce_price_date(index_value: Any) -> date:
    """Convert a yfinance dataframe index value to a date.

    Parameters:
        index_value: DataFrame index value.

    Returns:
        Calendar date for the price row.
    """
    if hasattr(index_value, "date"):
        return index_value.date()
    return date.fromisoformat(str(index_value)[:10])


def _stringify_value(value: Any) -> str:
    """Convert a dataframe scalar to a validator-friendly string.

    Parameters:
        value: Raw dataframe scalar.

    Returns:
        String representation of the value.
    """
    if pd.isna(value):
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)
