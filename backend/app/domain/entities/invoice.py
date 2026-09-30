"""Facture énergétique émise pour un site et une période."""

from dataclasses import dataclass
from datetime import date

from app.domain.value_objects.kwh import Kwh
from app.domain.value_objects.money import Money


@dataclass(frozen=True)
class Invoice:
    """Facture portant un identifiant, une période et un total à payer."""

    invoice_id: str
    site_id: str
    period_start: date
    period_end: date
    consumption: Kwh
    total: Money
    is_paid: bool = False

    def __post_init__(self) -> None:
        if not self.invoice_id.strip() or not self.site_id.strip():
            raise ValueError("La facture doit référencer un identifiant et un site")
        if self.period_end < self.period_start:
            raise ValueError("La période de facture est invalide")
