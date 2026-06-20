"""Extraction stage for Alpha Vantage daily prices."""

from src.api.alpha_vantage import AlphaVantageClient, AlphaVantageDailyBar
from src.utils.logger import get_logger

LOGGER = get_logger(__name__)


class PriceExtractor:
    """Fetch daily price data for a collection of tickers."""

    def __init__(self, client: AlphaVantageClient) -> None:
        """Initialize the extractor.

        Parameters:
            client: Alpha Vantage API client.
        """
        self._client = client

    def extract(self, tickers: list[str]) -> dict[str, list[AlphaVantageDailyBar]]:
        """Fetch daily bars for each ticker.

        Parameters:
            tickers: Ticker symbols to fetch.

        Returns:
            Mapping of ticker to fetched daily bars. Failed tickers are omitted.
        """
        extracted_data: dict[str, list[AlphaVantageDailyBar]] = {}

        for ticker in tickers:
            try:
                bars = self._client.fetch_daily_prices(ticker)
            except Exception as exc:
                LOGGER.exception(
                    "Failed to extract data for ticker %s: %s",
                    ticker,
                    exc,
                )
                continue

            extracted_data[ticker] = bars
            LOGGER.info("Extracted %s daily bar(s) for %s.", len(bars), ticker)

        return extracted_data
