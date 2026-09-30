"""Adaptateur spécialisé pour l'export XLSX du service de rapports."""

from app.application.ports.report_service import GeneratedReport
from app.infrastructure.reports.energy_report_adapter import EnergyReportAdapter


class ExcelReportGenerator:
    """Expose l'export Excel en réutilisant le générateur de rapports existant."""

    def __init__(self, adapter: EnergyReportAdapter | None = None) -> None:
        self.adapter = adapter or EnergyReportAdapter()

    async def generate(
        self, report_type: str, site_name: str, building_type: str
    ) -> GeneratedReport:
        """Produit le rapport demandé au format XLSX."""
        return await self.adapter.generate(report_type, "xlsx", site_name, building_type)
