"""Tranche tarifaire électrique applicable à une consommation donnée."""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class TariffBand(str, Enum):
    """Niveaux tarifaires métier utilisés par le calcul de facture."""

    SOCIAL = "sociale"
    DOMESTIC = "domestique"
    NON_DOMESTIC = "non_domestique"
    INDUSTRIAL = "professionnelle_industrielle"


@dataclass(frozen=True)
class TariffTier:
    """Tranche avec limites de consommation et prix unitaire en FCFA/kWh."""

    band: TariffBand
    rate_fcfa_per_kwh: Decimal
    minimum_kwh: Decimal
    maximum_kwh: Decimal | None

    def __post_init__(self) -> None:
        rate = Decimal(str(self.rate_fcfa_per_kwh))
        minimum = Decimal(str(self.minimum_kwh))
        maximum = Decimal(str(self.maximum_kwh)) if self.maximum_kwh is not None else None
        valid_numbers = (
            rate.is_finite() and minimum.is_finite() and (maximum is None or maximum.is_finite())
        )
        if (
            not valid_numbers
            or rate < 0
            or minimum < 0
            or (maximum is not None and maximum < minimum)
        ):
            raise ValueError("Bornes et tarif de tranche invalides")
        object.__setattr__(self, "rate_fcfa_per_kwh", rate)
        object.__setattr__(self, "minimum_kwh", minimum)
        object.__setattr__(self, "maximum_kwh", maximum)

    @classmethod
    def for_consumption(cls, consumption_kwh: Decimal | float) -> "TariffTier":
        """Retourne la tranche correspondant à la consommation totale fournie."""
        amount = Decimal(str(consumption_kwh))
        if not amount.is_finite() or amount < 0:
            raise ValueError("La consommation ne peut pas être négative")
        tiers = (
            cls(TariffBand.SOCIAL, Decimal("36"), Decimal("0"), Decimal("80")),
            cls(TariffBand.DOMESTIC, Decimal("46"), Decimal("81"), Decimal("150")),
            cls(TariffBand.NON_DOMESTIC, Decimal("68"), Decimal("151"), Decimal("500")),
            cls(TariffBand.INDUSTRIAL, Decimal("96"), Decimal("501"), None),
        )
        return next(
            tier for tier in tiers if tier.maximum_kwh is None or amount <= tier.maximum_kwh
        )
