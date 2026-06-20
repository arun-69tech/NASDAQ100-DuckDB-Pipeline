"""Logging configuration for the ETL application."""

import logging
from pathlib import Path


LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def configure_logging(log_level: str, log_file_path: Path) -> None:
    """Configure application logging.

    Parameters:
        log_level: Logging level name, such as `INFO` or `DEBUG`.
        log_file_path: File path for persistent application logs.

    Returns:
        None.
    """
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    handlers: list[logging.Handler] = [
        logging.StreamHandler(),
        logging.FileHandler(log_file_path, encoding="utf-8"),
    ]

    logging.basicConfig(
        level=numeric_level,
        format=LOG_FORMAT,
        handlers=handlers,
        force=True,
    )


def get_logger(name: str) -> logging.Logger:
    """Return a named application logger.

    Parameters:
        name: Logger name, usually `__name__`.

    Returns:
        Configured logger instance.
    """
    return logging.getLogger(name)
