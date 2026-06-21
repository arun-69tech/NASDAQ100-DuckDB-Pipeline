# MarketVault Application Design

## Scope

This application is responsible for the Python ETL workflow only. AWS deployment, scheduling, IAM, S3 upload automation, and infrastructure provisioning are intentionally outside this codebase.

## Runtime Flow

1. `src.main` loads environment-backed settings and configures logging.
2. `src.utils.file_handler.read_tickers` reads `config/tickers.csv`.
3. `src.api.yahoo_finance.YahooFinanceClient` fetches daily OHLCV data.
4. `src.validators.validator.StockPriceValidator` validates and converts API bars.
5. `src.database.schema` ensures the DuckDB table exists.
6. `src.database.upsert` writes records using `(ticker, date)` UPSERT semantics.
7. After a successful run, a daily CSV export is generated from DuckDB.

## Design Decisions

- Tickers are static CSV configuration so index membership can be updated without code changes.
- Yahoo Finance is the only market data source for Version 1.
- Yahoo Finance was selected because it requires no API key, reduces runtime
  configuration, and supports bulk NASDAQ-100 downloads through `yfinance`.
- The API client returns typed daily bars and does not expose raw dataframes outside the API layer.
- Invalid records are logged and skipped; ticker-level extraction failures are isolated.
- DuckDB writes are idempotent through a primary key on `(ticker, date)`.
- Required environment variables are validated at startup to fail fast on deployment misconfiguration.
- DuckDB is the master data store and single source of truth.
- CSV exports are generated from DuckDB, never directly from market data download results.

## Database

Database path:

```text
data/marketvault.duckdb
```

### `daily_prices`

Purpose: complete historical OHLCV data.

| Column | Type | Notes |
| --- | --- | --- |
| ticker | VARCHAR | Primary key component |
| date | DATE | Primary key component |
| open | DECIMAL(18, 6) | Daily open |
| high | DECIMAL(18, 6) | Daily high |
| low | DECIMAL(18, 6) | Daily low |
| close | DECIMAL(18, 6) | Daily close |
| volume | BIGINT | Daily volume |
| fetched_at | TIMESTAMP WITH TIME ZONE | ETL fetch timestamp |

Primary key: `(ticker, date)`

### `pipeline_runs`

Purpose: ETL execution history.

Suggested columns:

| Column | Notes |
| --- | --- |
| run_id | Unique pipeline run identifier |
| run_date | Logical run date |
| start_time | Run start timestamp |
| end_time | Run end timestamp |
| duration_seconds | Total execution duration |
| total_tickers | Number of requested tickers |
| successful_tickers | Number of successfully processed tickers |
| failed_tickers | Number of failed tickers |
| status | Run status |
| error_message | Failure details, when applicable |

## CSV Export

After every successful run, the pipeline generates one CSV file from DuckDB.

Filename format:

```text
US_NASDAQ100_YYYY-MM-DD.csv
```

Example:

```text
US_NASDAQ100_2026-06-20.csv
```

## S3 Layout

Configured bucket:

```text
marketvault-data
```

Expected object layout:

```text
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

Scheduling and AWS infrastructure are external to this Python application.

```text
US Market closes at 4:00 PM ET
Wait one hour
5:00 PM ET
EventBridge Scheduler
AWS Lambda
Python ETL Pipeline
Validate Data
Update DuckDB
Generate Daily CSV
Upload DuckDB and CSV to Amazon S3
CloudWatch Logs
SNS Failure Notifications
```
