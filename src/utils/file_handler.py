"""File loading helpers for pipeline inputs."""

from pathlib import Path

import pandas as pd


class TickerFileError(RuntimeError):
    """Raised when ticker input cannot be loaded or validated."""


def read_tickers(file_path: Path) -> list[str]:
    """Read ticker symbols from a CSV file.

    Parameters:
        file_path: Path to a CSV file with a `ticker` column.

    Returns:
        Unique uppercase ticker symbols in file order.

    Raises:
        TickerFileError: If the file is missing, malformed, or empty.
    """
    if not file_path.exists():
        raise TickerFileError(f"Ticker file does not exist: {file_path}.")

    try:
        dataframe = pd.read_csv(file_path)
    except Exception as exc:
        raise TickerFileError(f"Failed to read ticker file: {file_path}.") from exc

    if "ticker" not in dataframe.columns:
        raise TickerFileError("Ticker file must contain a 'ticker' column.")

    tickers: list[str] = []
    seen_tickers: set[str] = set()
    for raw_ticker in dataframe["ticker"].dropna():
        ticker = str(raw_ticker).strip().upper()
        if ticker and ticker not in seen_tickers:
            tickers.append(ticker)
            seen_tickers.add(ticker)

    if not tickers:
        raise TickerFileError("Ticker file does not contain any valid tickers.")

    return tickers
