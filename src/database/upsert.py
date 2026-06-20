"""DuckDB upsert operations."""

import duckdb

from config.constants import DAILY_PRICES_TABLE
from src.models.stock_price import StockPrice
from src.utils.logger import get_logger

LOGGER = get_logger(__name__)


def upsert_daily_prices(
    connection: duckdb.DuckDBPyConnection,
    stock_prices: list[StockPrice],
) -> int:
    """UPSERT stock price records into DuckDB.

    Parameters:
        connection: Open DuckDB connection.
        stock_prices: Validated stock price records.

    Returns:
        Number of records submitted for upsert.

    Raises:
        duckdb.Error: If the upsert fails.
    """
    if not stock_prices:
        LOGGER.info("No stock price records to upsert.")
        return 0

    sql = f"""
        INSERT INTO {DAILY_PRICES_TABLE} (
            ticker,
            date,
            open,
            high,
            low,
            close,
            volume,
            fetched_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (ticker, date) DO UPDATE SET
            open = excluded.open,
            high = excluded.high,
            low = excluded.low,
            close = excluded.close,
            volume = excluded.volume,
            fetched_at = excluded.fetched_at;
    """

    connection.executemany(
        sql,
        [stock_price.as_database_tuple() for stock_price in stock_prices],
    )
    LOGGER.info("Upserted %s daily price record(s).", len(stock_prices))
    return len(stock_prices)
