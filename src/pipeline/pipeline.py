"""Top-level ETL pipeline orchestration."""

from dataclasses import dataclass
from pathlib import Path

from src.pipeline.extract import PriceExtractor
from src.pipeline.load import PriceLoader
from src.pipeline.transform import PriceTransformer
from src.utils.file_handler import read_tickers
from src.utils.logger import get_logger
from src.utils.timer import timer

LOGGER = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class PipelineResult:
    """Summary statistics for a pipeline run."""

    requested_tickers: int
    successful_tickers: int
    extracted_records: int
    loaded_records: int
    elapsed_seconds: float


class Nasdaq100Pipeline:
    """Orchestrate the NASDAQ-100 daily price ETL workflow."""

    def __init__(
        self,
        *,
        tickers_file_path: Path,
        extractor: PriceExtractor,
        transformer: PriceTransformer,
        loader: PriceLoader,
    ) -> None:
        """Initialize the pipeline.

        Parameters:
            tickers_file_path: Path to the ticker input CSV.
            extractor: Extraction stage.
            transformer: Transformation stage.
            loader: Load stage.
        """
        self._tickers_file_path = tickers_file_path
        self._extractor = extractor
        self._transformer = transformer
        self._loader = loader

    def run(self) -> PipelineResult:
        """Execute the ETL pipeline.

        Returns:
            Pipeline execution summary.

        Raises:
            TickerFileError: If ticker input cannot be loaded.
            duckdb.Error: If database load fails.
        """
        LOGGER.info("NASDAQ-100 DuckDB ETL pipeline started.")

        with timer() as timer_result:
            tickers = read_tickers(self._tickers_file_path)
            LOGGER.info("Loaded %s ticker(s) from input file.", len(tickers))

            extracted_data = self._extractor.extract(tickers)
            extracted_records = sum(len(records) for records in extracted_data.values())

            stock_prices = self._transformer.transform(extracted_data)
            loaded_records = self._loader.load(stock_prices)

        result = PipelineResult(
            requested_tickers=len(tickers),
            successful_tickers=len(extracted_data),
            extracted_records=extracted_records,
            loaded_records=loaded_records,
            elapsed_seconds=timer_result.elapsed_seconds,
        )

        LOGGER.info(
            "NASDAQ-100 DuckDB ETL pipeline completed. "
            "requested_tickers=%s successful_tickers=%s extracted_records=%s "
            "loaded_records=%s elapsed_seconds=%.2f",
            result.requested_tickers,
            result.successful_tickers,
            result.extracted_records,
            result.loaded_records,
            result.elapsed_seconds,
        )
        return result
