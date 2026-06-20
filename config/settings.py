"""Environment-backed application settings."""

from dataclasses import dataclass
from pathlib import Path
from typing import Self

from dotenv import load_dotenv

from config.constants import (
    DEFAULT_ALPHA_VANTAGE_BASE_URL,
    DEFAULT_ALPHA_VANTAGE_OUTPUT_SIZE,
    DEFAULT_ALPHA_VANTAGE_TIMEOUT_SECONDS,
    DEFAULT_DUCKDB_DATABASE_PATH,
    DEFAULT_LOG_FILE_PATH,
    DEFAULT_TICKERS_FILE_PATH,
    PROJECT_ROOT,
    REQUIRED_ENVIRONMENT_VARIABLES,
)
from src.utils.helpers import get_env_value


class ConfigurationError(RuntimeError):
    """Raised when required runtime configuration is missing or invalid."""


@dataclass(frozen=True, slots=True)
class Settings:
    """Validated runtime settings for the ETL application."""

    alpha_vantage_api_key: str
    aws_region: str
    s3_bucket: str
    duckdb_database_path: Path
    tickers_file_path: Path
    log_level: str
    log_file_path: Path
    alpha_vantage_base_url: str
    alpha_vantage_timeout_seconds: int
    alpha_vantage_output_size: str

    @classmethod
    def from_environment(cls) -> Self:
        """Build settings from environment variables.

        Returns:
            A validated `Settings` instance.

        Raises:
            ConfigurationError: If required variables are missing or invalid.
        """
        load_dotenv()
        cls._validate_required_environment()

        return cls(
            alpha_vantage_api_key=get_env_value("ALPHA_VANTAGE_API_KEY"),
            aws_region=get_env_value("AWS_REGION"),
            s3_bucket=get_env_value("S3_BUCKET"),
            duckdb_database_path=_resolve_path(
                get_env_value(
                    "DUCKDB_DATABASE_PATH",
                    str(DEFAULT_DUCKDB_DATABASE_PATH),
                    required=False,
                )
            ),
            tickers_file_path=_resolve_path(
                get_env_value(
                    "TICKERS_FILE_PATH",
                    str(DEFAULT_TICKERS_FILE_PATH),
                    required=False,
                )
            ),
            log_level=get_env_value("LOG_LEVEL", "INFO", required=False).upper(),
            log_file_path=_resolve_path(
                get_env_value(
                    "LOG_FILE_PATH",
                    str(DEFAULT_LOG_FILE_PATH),
                    required=False,
                )
            ),
            alpha_vantage_base_url=get_env_value(
                "ALPHA_VANTAGE_BASE_URL",
                DEFAULT_ALPHA_VANTAGE_BASE_URL,
                required=False,
            ),
            alpha_vantage_timeout_seconds=_parse_positive_int(
                get_env_value(
                    "ALPHA_VANTAGE_TIMEOUT_SECONDS",
                    str(DEFAULT_ALPHA_VANTAGE_TIMEOUT_SECONDS),
                    required=False,
                ),
                "ALPHA_VANTAGE_TIMEOUT_SECONDS",
            ),
            alpha_vantage_output_size=get_env_value(
                "ALPHA_VANTAGE_OUTPUT_SIZE",
                DEFAULT_ALPHA_VANTAGE_OUTPUT_SIZE,
                required=False,
            ),
        )

    @staticmethod
    def _validate_required_environment() -> None:
        missing_variables = [
            name
            for name in REQUIRED_ENVIRONMENT_VARIABLES
            if not get_env_value(name, required=False)
        ]
        if missing_variables:
            missing = ", ".join(missing_variables)
            raise ConfigurationError(
                f"Missing required environment variable(s): {missing}."
            )


def _resolve_path(path_value: str) -> Path:
    """Resolve an absolute or project-relative path.

    Parameters:
        path_value: Raw path string from configuration.

    Returns:
        A resolved `Path`.
    """
    path = Path(path_value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def _parse_positive_int(value: str, variable_name: str) -> int:
    """Parse a positive integer environment variable.

    Parameters:
        value: Raw string value.
        variable_name: Environment variable name used in errors.

    Returns:
        Parsed positive integer.

    Raises:
        ConfigurationError: If parsing fails or the value is not positive.
    """
    try:
        parsed_value = int(value)
    except ValueError as exc:
        raise ConfigurationError(
            f"{variable_name} must be a positive integer."
        ) from exc

    if parsed_value <= 0:
        raise ConfigurationError(f"{variable_name} must be greater than zero.")

    return parsed_value
