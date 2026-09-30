"""Exceptions précises utilisées par les règles et services du domaine."""

from app.domain.exceptions.domain_exception import DomainException


class MachineNotFoundError(DomainException):
    """La machine demandée n'existe pas dans le référentiel métier."""

    code = "MACHINE_NOT_FOUND"


class InvalidReadingError(DomainException):
    """Un relevé de capteur viole les invariants de mesure."""

    code = "INVALID_READING"


class OverloadError(DomainException):
    """Une machine dépasse sa limite de puissance admissible."""

    code = "MACHINE_OVERLOADED"
