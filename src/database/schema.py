"""DuckDB schema management."""

import duckdb

from config.constants import DAILY_PRICES_TABLE
from src.utils.logger import get_logger

LOGGER = get_logger(__name__)


def create_daily_prices_table(connection: duckdb.DuckDBPyConnection) -> None:
    """Create the daily prices table when it does not already exist.

    Parameters:
        connection: Open DuckDB connection.

    Returns:
        None.

    Raises:
        duckdb.Error: If schema creation fails.
    """
    connection.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {DAILY_PRICES_TABLE} (
            ticker VARCHAR NOT NULL,
            date DATE NOT NULL,
            open DECIMAL(18, 6) NOT NULL,
            high DECIMAL(18, 6) NOT NULL,
            low DECIMAL(18, 6) NOT NULL,
            close DECIMAL(18, 6) NOT NULL,
            volume BIGINT NOT NULL,
            fetched_at TIMESTAMP WITH TIME ZONE NOT NULL,
            PRIMARY KEY (ticker, date)
        );
        """
    )
    LOGGER.info("Ensured DuckDB table exists: %s", DAILY_PRICES_TABLE)
