"""General-purpose helper functions."""

import os
from decimal import Decimal, InvalidOperation


def get_env_value(
    name: str,
    default: str | None = None,
    *,
    required: bool = True,
) -> str:
    """Read and normalize an environment variable.

    Parameters:
        name: Environment variable name.
        default: Value returned when the variable is absent and not required.
        required: Whether a missing or blank value should raise an error.

    Returns:
        The stripped environment value or default.

    Raises:
        ValueError: If the value is required but missing.
    """
    value = os.getenv(name, default)
    if value is None or value.strip() == "":
        if required:
            raise ValueError(f"Missing required environment variable: {name}.")
        return "" if default is None else default
    return value.strip()


def parse_decimal(value: object, field_name: str) -> Decimal:
    """Convert a value to `Decimal`.

    Parameters:
        value: Raw input value.
        field_name: Field name used in error messages.

    Returns:
        Parsed decimal value.

    Raises:
        ValueError: If the value is missing or not numeric.
    """
    if value is None or str(value).strip() == "":
        raise ValueError(f"{field_name} is missing.")

    try:
        return Decimal(str(value).strip())
    except InvalidOperation as exc:
        raise ValueError(f"{field_name} must be numeric.") from exc


def parse_int(value: object, field_name: str) -> int:
    """Convert a value to `int`.

    Parameters:
        value: Raw input value.
        field_name: Field name used in error messages.

    Returns:
        Parsed integer value.

    Raises:
        ValueError: If the value is missing or not an integer.
    """
    if value is None or str(value).strip() == "":
        raise ValueError(f"{field_name} is missing.")

    try:
        return int(str(value).strip())
    except ValueError as exc:
        raise ValueError(f"{field_name} must be an integer.") from exc
