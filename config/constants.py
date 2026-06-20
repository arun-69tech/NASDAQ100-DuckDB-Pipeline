"""Application-wide constants for the MarketVault ETL pipeline."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_DUCKDB_DATABASE_PATH = PROJECT_ROOT / "data" / "marketvault.duckdb"
DEFAULT_TICKERS_FILE_PATH = PROJECT_ROOT / "config" / "tickers.csv"
DEFAULT_LOG_FILE_PATH = PROJECT_ROOT / "logs" / "pipeline.log"

DEFAULT_ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"
DEFAULT_ALPHA_VANTAGE_TIMEOUT_SECONDS = 30
DEFAULT_ALPHA_VANTAGE_OUTPUT_SIZE = "compact"

ALPHA_VANTAGE_DAILY_FUNCTION = "TIME_SERIES_DAILY"
ALPHA_VANTAGE_TIME_SERIES_KEY = "Time Series (Daily)"

DAILY_PRICES_TABLE = "daily_prices"
PIPELINE_RUNS_TABLE = "pipeline_runs"

CSV_EXPORT_PREFIX = "US_NASDAQ100"
CSV_EXPORT_EXTENSION = "csv"

S3_DATABASE_PREFIX = "database"
S3_EXPORTS_CSV_PREFIX = "exports/csv"
S3_LOGS_PREFIX = "logs"
S3_DATABASE_OBJECT_KEY = "database/marketvault.duckdb"
S3_PIPELINE_LOG_OBJECT_KEY = "logs/pipeline.log"

REQUIRED_ENVIRONMENT_VARIABLES = (
    "ALPHA_VANTAGE_API_KEY",
    "AWS_REGION",
    "S3_BUCKET",
)
