# Application Design

## Scope

This application is responsible for the Python ETL workflow only. AWS deployment, scheduling, IAM, S3 upload automation, and infrastructure provisioning are intentionally outside this codebase.

## Runtime Flow

1. `src.main` loads environment-backed settings and configures logging.
2. `src.utils.file_handler.read_tickers` reads `config/tickers.csv`.
3. `src.api.alpha_vantage.AlphaVantageClient` fetches daily OHLCV data.
4. `src.validators.validator.StockPriceValidator` validates and converts API bars.
5. `src.database.schema` ensures the DuckDB table exists.
6. `src.database.upsert` writes records using `(ticker, date)` UPSERT semantics.

## Design Decisions

- Tickers are static CSV configuration so index membership can be updated without code changes.
- The API client returns typed daily bars and does not expose raw Alpha Vantage payloads.
- Invalid records are logged and skipped; ticker-level extraction failures are isolated.
- DuckDB writes are idempotent through a primary key on `(ticker, date)`.
- Required environment variables are validated at startup to fail fast on deployment misconfiguration.

## Database Table

`daily_prices`

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
