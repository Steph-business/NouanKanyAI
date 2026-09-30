"""Adaptateur spécialisé pour l'export PDF du service de rapports."""

from app.application.ports.report_service import GeneratedReport
from app.infrastructure.reports.energy_report_adapter import EnergyReportAdapter


class PDFReportGenerator:
    """Expose l'export PDF en réutilisant le générateur de rapports existant."""

    def __init__(self, adapter: EnergyReportAdapter | None = None) -> None:
        self.adapter = adapter or EnergyReportAdapter()

    async def generate(
        self, report_type: str, site_name: str, building_type: str
    ) -> GeneratedReport:
        """Produit le rapport demandé au format PDF."""
        return await self.adapter.generate(report_type, "pdf", site_name, building_type)
