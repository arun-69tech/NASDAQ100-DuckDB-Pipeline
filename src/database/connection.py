"""DuckDB connection management."""

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import duckdb


@contextmanager
def duckdb_connection(database_path: Path) -> Iterator[duckdb.DuckDBPyConnection]:
    """Create a managed DuckDB connection.

    Parameters:
        database_path: Path to the DuckDB database file.

    Yields:
        Open DuckDB connection.

    Raises:
        duckdb.Error: If DuckDB cannot open or use the database.
    """
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = duckdb.connect(str(database_path))
    try:
        yield connection
    finally:
        connection.close()
