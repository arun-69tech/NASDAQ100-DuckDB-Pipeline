"""CSV export stage for DuckDB-backed market data."""

from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

from config.constants import CSV_EXPORT_EXTENSION, CSV_EXPORT_PREFIX, DAILY_PRICES_TABLE
from src.utils.logger import get_logger

if TYPE_CHECKING:
    import duckdb

LOGGER = get_logger(__name__)


def build_daily_export_filename(export_date: date) -> str:
    """Build the daily NASDAQ-100 CSV export filename.

    Parameters:
        export_date: Logical export date.

    Returns:
        Filename using the `US_NASDAQ100_YYYY-MM-DD.csv` format.
    """
    return f"{CSV_EXPORT_PREFIX}_{export_date.isoformat()}.{CSV_EXPORT_EXTENSION}"


def export_daily_prices_to_csv(
    connection: "duckdb.DuckDBPyConnection",
    export_date: date,
    output_directory: Path,
) -> Path:
    """Export one trading date of prices from DuckDB to CSV.

    Parameters:
        connection: Open DuckDB connection.
        export_date: Date to export.
        output_directory: Directory where the CSV file should be written.

    Returns:
        Path to the generated CSV file.

    Raises:
        duckdb.Error: If DuckDB export fails.
    """
    output_directory.mkdir(parents=True, exist_ok=True)
    export_path = output_directory / build_daily_export_filename(export_date)
    export_path_literal = str(export_path).replace("'", "''")

    connection.execute(
        f"""
        COPY (
            SELECT
                ticker,
                date,
                open,
                high,
                low,
                close,
                volume,
                fetched_at
            FROM {DAILY_PRICES_TABLE}
            WHERE date = ?
            ORDER BY ticker
        )
        TO '{export_path_literal}'
        WITH (HEADER, DELIMITER ',');
        """,
        [export_date],
    )

    LOGGER.info("Generated DuckDB-backed CSV export: %s", export_path)
    return export_path
