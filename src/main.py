"""Application entry point for the MarketVault ETL pipeline."""

import logging
import sys

from config.settings import ConfigurationError, Settings
from src.api.yahoo_finance import YahooFinanceClient
from src.pipeline.extract import PriceExtractor
from src.pipeline.load import PriceLoader
from src.pipeline.pipeline import Nasdaq100Pipeline
from src.pipeline.transform import PriceTransformer
from src.utils.file_handler import TickerFileError
from src.utils.logger import configure_logging, get_logger
from src.validators.validator import StockPriceValidator

LOGGER = get_logger(__name__)


def build_pipeline(settings: Settings) -> Nasdaq100Pipeline:
    """Build the ETL pipeline dependency graph.

    Parameters:
        settings: Validated application settings.

    Returns:
        Configured `Nasdaq100Pipeline` instance.
    """
    yahoo_finance_client = YahooFinanceClient()

    return Nasdaq100Pipeline(
        tickers_file_path=settings.tickers_file_path,
        extractor=PriceExtractor(yahoo_finance_client),
        transformer=PriceTransformer(StockPriceValidator()),
        loader=PriceLoader(settings.duckdb_database_path),
    )


def main() -> int:
    """Run the MarketVault ETL pipeline.

    Returns:
        Process exit code. `0` indicates success; `1` indicates failure.
    """
    try:
        settings = Settings.from_environment()
        configure_logging(settings.log_level, settings.log_file_path)
        pipeline = build_pipeline(settings)
        pipeline.run()
    except (ConfigurationError, TickerFileError, ValueError) as exc:
        logging.basicConfig(level=logging.ERROR)
        LOGGER.error("Pipeline configuration failed: %s", exc)
        return 1
    except Exception as exc:
        LOGGER.exception("Pipeline execution failed: %s", exc)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
