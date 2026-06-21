"""Extraction stage for Yahoo Finance daily prices."""

from src.api.yahoo_finance import YahooFinanceClient, YahooFinanceDailyBar
from src.utils.logger import get_logger

LOGGER = get_logger(__name__)


class PriceExtractor:
    """Fetch daily price data for a collection of tickers."""

    def __init__(self, client: YahooFinanceClient) -> None:
        """Initialize the extractor.

        Parameters:
            client: Yahoo Finance API client.
        """
        self._client = client

    def extract(self, tickers: list[str]) -> dict[str, list[YahooFinanceDailyBar]]:
        """Fetch daily bars for each ticker.

        Parameters:
            tickers: Ticker symbols to fetch.

        Returns:
            Mapping of ticker to fetched daily bars. Failed tickers are omitted.
        """
        try:
            extracted_data = self._client.fetch_daily_prices_for_tickers(tickers)
        except Exception as exc:
            LOGGER.exception("Failed to extract Yahoo Finance data: %s", exc)
            return {}

        for ticker, bars in extracted_data.items():
            LOGGER.info("Extracted %s daily bar(s) for %s.", len(bars), ticker)

        return extracted_data
