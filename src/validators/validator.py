"""Validation logic for daily stock price records."""

from datetime import datetime, timezone
from decimal import Decimal

from src.api.yahoo_finance import YahooFinanceDailyBar
from src.models.stock_price import StockPrice
from src.utils.helpers import parse_decimal, parse_int
from src.utils.logger import get_logger

LOGGER = get_logger(__name__)


class StockPriceValidator:
    """Validate and convert API daily bars into domain models."""

    def validate(self, bar: YahooFinanceDailyBar) -> StockPrice | None:
        """Validate an API daily bar.

        Parameters:
            bar: Daily bar returned by the API layer.

        Returns:
            A `StockPrice` object when valid, otherwise `None`.
        """
        try:
            stock_price = StockPrice(
                ticker=bar.ticker,
                date=bar.price_date,
                open=parse_decimal(bar.open, "open"),
                high=parse_decimal(bar.high, "high"),
                low=parse_decimal(bar.low, "low"),
                close=parse_decimal(bar.close, "close"),
                volume=parse_int(bar.volume, "volume"),
                fetched_at=datetime.now(timezone.utc),
            )
            self._validate_business_rules(stock_price)
        except ValueError as exc:
            LOGGER.warning(
                "Skipping invalid stock price record for %s on %s: %s",
                bar.ticker,
                bar.price_date,
                exc,
            )
            return None

        return stock_price

    def _validate_business_rules(self, stock_price: StockPrice) -> None:
        """Validate numeric consistency rules.

        Parameters:
            stock_price: Parsed stock price object.

        Returns:
            None.

        Raises:
            ValueError: If a numeric business rule is violated.
        """
        price_fields: dict[str, Decimal] = {
            "open": stock_price.open,
            "high": stock_price.high,
            "low": stock_price.low,
            "close": stock_price.close,
        }
        for field_name, value in price_fields.items():
            if value <= 0:
                raise ValueError(f"{field_name} must be greater than zero.")

        if stock_price.volume < 0:
            raise ValueError("volume cannot be negative.")

        if stock_price.high < stock_price.low:
            raise ValueError("high cannot be lower than low.")

        if stock_price.open > stock_price.high or stock_price.open < stock_price.low:
            raise ValueError("open must be between low and high.")

        if stock_price.close > stock_price.high or stock_price.close < stock_price.low:
            raise ValueError("close must be between low and high.")
