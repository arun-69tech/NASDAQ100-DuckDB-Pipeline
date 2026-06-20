# MarketVault

Production-oriented Python ETL pipeline for fetching daily OHLCV data for NASDAQ-100 constituents from Alpha Vantage and storing deduplicated records in DuckDB.

## Features

- Reads NASDAQ-100 tickers from `config/tickers.csv`
- Fetches daily adjusted time series data from Alpha Vantage
- Validates API-level and record-level data quality
- Transforms records into typed Python domain objects
- Uses DuckDB as the master data store and single source of truth
- Creates and maintains historical `daily_prices` records
- Tracks ETL execution history in `pipeline_runs`
- Uses idempotent UPSERT semantics on `(ticker, date)`
- Generates a daily CSV export from DuckDB after each successful run
- Produces structured application logs
- Keeps DuckDB and CSV artifacts ready for separate S3 upload automation

## Requirements

- Python 3.12
- Alpha Vantage API key
- DuckDB local database file

## Configuration

Create a `.env` file from `.env.example` and provide the required values:

```bash
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
AWS_REGION=us-east-1
S3_BUCKET=marketvault-data
DUCKDB_DATABASE_PATH=data/marketvault.duckdb
```

`AWS_REGION` and `S3_BUCKET` are validated because the DuckDB database, CSV exports, and logs are intended for downstream S3 upload, although this application does not implement AWS infrastructure.

## Data Architecture

DuckDB is the master data store. CSV exports must be generated from DuckDB, never directly from Alpha Vantage API responses.

Database path:

```text
data/marketvault.duckdb
```

Tables:

- `daily_prices`: complete historical OHLCV data keyed by `(ticker, date)`
- `pipeline_runs`: ETL execution history and run status

Daily CSV export format:

```text
US_NASDAQ100_YYYY-MM-DD.csv
```

Expected S3 layout:

```text
marketvault-data/
database/
marketvault.duckdb

exports/
csv/
YYYY/
MM/
US_NASDAQ100_YYYY-MM-DD.csv

logs/
pipeline.log
```

## Production Schedule

The production workflow is scheduled outside this Python application:

```text
US Market closes at 4:00 PM ET
Wait one hour
5:00 PM ET EventBridge Scheduler
AWS Lambda
Python ETL Pipeline
Validate Data
Update DuckDB
Generate Daily CSV from DuckDB
Upload DuckDB and CSV to Amazon S3
CloudWatch Logs
SNS Failure Notifications
```

## Run

```bash
python -m src.main
```

## Development

```bash
black .
ruff check .
isort .
pytest
```

## Project Layout

```text
config/       Configuration, constants, ticker input
src/api/      Alpha Vantage client and retry utilities
src/database/ DuckDB connection, schema, and upsert logic
src/models/   Domain models
src/pipeline/ ETL orchestration
src/utils/    Logging, file, timing, and helper utilities
```
