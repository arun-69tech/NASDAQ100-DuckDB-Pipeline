"""Load stage for validated daily stock prices."""

from pathlib import Path

from src.database.connection import duckdb_connection
from src.database.schema import create_daily_prices_table
from src.database.upsert import upsert_daily_prices
from src.models.stock_price import StockPrice
from src.utils.logger import get_logger

LOGGER = get_logger(__name__)


class PriceLoader:
    """Load validated stock prices into DuckDB."""

    def __init__(self, database_path: Path) -> None:
        """Initialize the loader.

        Parameters:
            database_path: DuckDB database path.
        """
        self._database_path = database_path

    def load(self, stock_prices: list[StockPrice]) -> int:
        """Load stock price records into DuckDB using UPSERT.

        Parameters:
            stock_prices: Validated stock price records.

        Returns:
            Number of records submitted for upsert.

        Raises:
            duckdb.Error: If database operations fail.
        """
        with duckdb_connection(self._database_path) as connection:
            create_daily_prices_table(connection)
            upserted_count = upsert_daily_prices(connection, stock_prices)

        LOGGER.info(
            "DuckDB load completed with %s submitted record(s).",
            upserted_count,
        )
        return upserted_count
