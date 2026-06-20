"""DuckDB schema management."""

import duckdb

from config.constants import DAILY_PRICES_TABLE, PIPELINE_RUNS_TABLE
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


def create_pipeline_runs_table(connection: duckdb.DuckDBPyConnection) -> None:
    """Create the pipeline runs table when it does not already exist.

    Parameters:
        connection: Open DuckDB connection.

    Returns:
        None.

    Raises:
        duckdb.Error: If schema creation fails.
    """
    connection.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {PIPELINE_RUNS_TABLE} (
            run_id VARCHAR PRIMARY KEY,
            run_date DATE NOT NULL,
            start_time TIMESTAMP WITH TIME ZONE NOT NULL,
            end_time TIMESTAMP WITH TIME ZONE,
            duration_seconds DOUBLE,
            total_tickers INTEGER NOT NULL,
            successful_tickers INTEGER NOT NULL,
            failed_tickers INTEGER NOT NULL,
            status VARCHAR NOT NULL,
            error_message VARCHAR
        );
        """
    )
    LOGGER.info("Ensured DuckDB table exists: %s", PIPELINE_RUNS_TABLE)


def create_application_tables(connection: duckdb.DuckDBPyConnection) -> None:
    """Create all application-owned DuckDB tables.

    Parameters:
        connection: Open DuckDB connection.

    Returns:
        None.

    Raises:
        duckdb.Error: If schema creation fails.
    """
    create_daily_prices_table(connection)
    create_pipeline_runs_table(connection)
