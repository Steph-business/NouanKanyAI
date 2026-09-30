"""Exceptions métier indépendantes des codes et protocoles HTTP."""

from app.domain.exceptions.domain_exception import DomainException
from app.domain.exceptions.specific_exceptions import (
    InvalidReadingError,
    MachineNotFoundError,
    OverloadError,
)

__all__ = ["DomainException", "InvalidReadingError", "MachineNotFoundError", "OverloadError"]
