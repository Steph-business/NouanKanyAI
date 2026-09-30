"""Use case de génération d'un rapport exportable pour un site."""

from dataclasses import dataclass

from app.application.ports.report_service import GeneratedReport, ReportService


@dataclass(frozen=True)
class GenerateReportCommand:
    """Critères de génération d'un rapport et de son format d'export."""

    report_type: str
    export_format: str
    site_name: str
    building_type: str = "Industrie"


class GenerateReportUseCase:
    """Valide les options de rapport puis appelle le port de génération."""

    REPORT_TYPES = frozenset(
        {"daily", "weekly", "monthly", "energy_audit", "anomaly_report", "performance_report"}
    )
    EXPORT_FORMATS = frozenset({"pdf", "docx", "xlsx", "pptx"})

    def __init__(self, report_service: ReportService) -> None:
        self.report_service = report_service

    async def execute(self, cmd: GenerateReportCommand) -> GeneratedReport:
        """Retourne le rapport produit par l'adaptateur configuré."""
        report_type = cmd.report_type.strip().lower()
        export_format = cmd.export_format.strip().lower()
        if report_type not in self.REPORT_TYPES:
            raise ValueError("Type de rapport non pris en charge")
        if export_format not in self.EXPORT_FORMATS:
            raise ValueError("Format d'export non pris en charge")
        if not cmd.site_name.strip():
            raise ValueError("Le nom du site est obligatoire")
        return await self.report_service.generate(
            report_type, export_format, cmd.site_name.strip(), cmd.building_type.strip()
        )
