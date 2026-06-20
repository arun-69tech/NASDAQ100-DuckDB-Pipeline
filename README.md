# NASDAQ100-DuckDB-Pipeline

Production-oriented Python ETL pipeline for fetching daily OHLCV data for NASDAQ-100 constituents from Alpha Vantage and storing deduplicated records in DuckDB.

## Features

- Reads NASDAQ-100 tickers from `config/tickers.csv`
- Fetches daily adjusted time series data from Alpha Vantage
- Validates API-level and record-level data quality
- Transforms records into typed Python domain objects
- Creates and maintains a DuckDB `daily_prices` table
- Uses idempotent UPSERT semantics on `(ticker, date)`
- Produces structured application logs
- Keeps database output ready for separate S3 upload automation

## Requirements

- Python 3.12
- Alpha Vantage API key
- DuckDB local database file

## Configuration

Create a `.env` file from `.env.example` and provide the required values:

```bash
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
AWS_REGION=us-east-1
S3_BUCKET=your-bucket-name
```

`AWS_REGION` and `S3_BUCKET` are validated because the database artifact is intended for downstream S3 upload, although this application does not perform AWS deployment.

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
