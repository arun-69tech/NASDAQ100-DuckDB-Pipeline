"""Domain model for validated daily stock price records."""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class StockPrice:
    """Validated daily OHLCV stock price record."""

    ticker: str
    date: date
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    fetched_at: datetime

    def as_database_tuple(
        self,
    ) -> tuple[str, date, Decimal, Decimal, Decimal, Decimal, int, datetime]:
        """Convert the model into a DuckDB insert tuple.

        Returns:
            Tuple ordered to match the `daily_prices` table columns.
        """
        return (
            self.ticker,
            self.date,
            self.open,
            self.high,
            self.low,
            self.close,
            self.volume,
            self.fetched_at,
        )
