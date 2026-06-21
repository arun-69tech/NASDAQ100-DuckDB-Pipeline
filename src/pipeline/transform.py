"""Transformation stage for daily stock prices."""

from src.api.yahoo_finance import YahooFinanceDailyBar
from src.models.stock_price import StockPrice
from src.utils.logger import get_logger
from src.validators.validator import StockPriceValidator

LOGGER = get_logger(__name__)


class PriceTransformer:
    """Transform API daily bars into validated domain models."""

    def __init__(self, validator: StockPriceValidator) -> None:
        """Initialize the transformer.

        Parameters:
            validator: Stock price validator.
        """
        self._validator = validator

    def transform(
        self,
        extracted_data: dict[str, list[YahooFinanceDailyBar]],
    ) -> list[StockPrice]:
        """Transform extracted API records into stock price models.

        Parameters:
            extracted_data: Mapping of ticker to API daily bars.

        Returns:
            Validated stock price records.
        """
        stock_prices: list[StockPrice] = []
        invalid_count = 0

        for bars in extracted_data.values():
            for bar in bars:
                stock_price = self._validator.validate(bar)
                if stock_price is None:
                    invalid_count += 1
                    continue
                stock_prices.append(stock_price)

        LOGGER.info(
            "Transformed %s valid record(s); skipped %s invalid record(s).",
            len(stock_prices),
            invalid_count,
        )
        return stock_prices
