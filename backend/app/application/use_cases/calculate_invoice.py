"""Use case de calcul d'une estimation de facture selon le tarif métier."""

from dataclasses import dataclass
from decimal import Decimal

from app.domain.value_objects.kwh import Kwh
from app.domain.value_objects.money import Money
from app.domain.value_objects.tariff_tier import TariffTier


@dataclass(frozen=True)
class CalculateInvoiceCommand:
    """Paramètres nécessaires à l'estimation d'une facture énergétique."""

    consumption_kwh: Decimal


@dataclass(frozen=True)
class CalculateInvoiceResult:
    """Consommation, tranche applicable et estimation financière."""

    consumption: Kwh
    tariff: TariffTier
    total: Money


class CalculateInvoiceUseCase:
    """Applique la tranche tarifaire correspondant à la consommation fournie."""

    async def execute(self, cmd: CalculateInvoiceCommand) -> CalculateInvoiceResult:
        """Retourne le coût estimé par application du prix unitaire de la tranche."""
        consumption = Kwh(cmd.consumption_kwh)
        tariff = TariffTier.for_consumption(consumption.value)
        total = Money(consumption.value * tariff.rate_fcfa_per_kwh)
        return CalculateInvoiceResult(consumption=consumption, tariff=tariff, total=total)
