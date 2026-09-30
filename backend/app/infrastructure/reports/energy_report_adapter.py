"""Adaptateur du service de rapports historiques vers le port application."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from app.application.ports.report_service import GeneratedReport, ReportService

if TYPE_CHECKING:
    from app.reports.service import EnergyReportService


class EnergyReportAdapter(ReportService):
    """Convertit le résultat du service documentaire en payload applicatif."""

    MEDIA_TYPES = {
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    }

    def __init__(self, service: EnergyReportService | None = None) -> None:
        if service is None:
            from app.reports.service import EnergyReportService

            service = EnergyReportService()
        self.service = service

    async def generate(
        self, report_type: str, export_format: str, site_name: str, building_type: str
    ) -> GeneratedReport:
        """Exécute la génération synchrone existante hors de la boucle async."""
        report_data, content, _ = await asyncio.to_thread(
            self.service.generate_report,
            report_type=report_type,
            export_format=export_format,
            site_name=site_name,
            building_type=building_type,
        )
        suffix = export_format.lower()
        return GeneratedReport(
            filename=f"{report_data.report_id}.{suffix}",
            content=content,
            media_type=self.MEDIA_TYPES[suffix],
        )
