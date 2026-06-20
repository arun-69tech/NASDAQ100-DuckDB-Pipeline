"""Application-wide constants for the NASDAQ-100 ETL pipeline."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_DUCKDB_DATABASE_PATH = PROJECT_ROOT / "data" / "prices.duckdb"
DEFAULT_TICKERS_FILE_PATH = PROJECT_ROOT / "config" / "tickers.csv"
DEFAULT_LOG_FILE_PATH = PROJECT_ROOT / "logs" / "pipeline.log"

DEFAULT_ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"
DEFAULT_ALPHA_VANTAGE_TIMEOUT_SECONDS = 30
DEFAULT_ALPHA_VANTAGE_OUTPUT_SIZE = "compact"

ALPHA_VANTAGE_DAILY_FUNCTION = "TIME_SERIES_DAILY"
ALPHA_VANTAGE_TIME_SERIES_KEY = "Time Series (Daily)"

DAILY_PRICES_TABLE = "daily_prices"

REQUIRED_ENVIRONMENT_VARIABLES = (
    "ALPHA_VANTAGE_API_KEY",
    "AWS_REGION",
    "S3_BUCKET",
)
