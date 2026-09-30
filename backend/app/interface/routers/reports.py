"""
app/interface/routers/reports.py — Routeur FastAPI d'utilisation réelle du
générateur de rapports (app/reports/).

⚠️ DONNÉES ENCORE FACTICES : EnergyReportService.generate_report() appelle
`EnergyReportGenerator.create_mock_report_data()` (app/reports/generator.py) —
il n'existe pas de constructeur qui compile de vraies données en
`EnergyReportData` (ce backend n'a d'ailleurs pas de source de données réelle
équivalente — voir app/services/demo_data.py, déjà du démo statique/CSV).
Cette route est fonctionnelle (génère un vrai fichier PDF/DOCX/XLSX/PPTX
téléchargeable) mais le contenu n'est représentatif d'aucun site réel.
"""

import logging

from fastapi import APIRouter, Response
from pydantic import BaseModel

from app.reports.models import ExportFormat, ReportType
from app.reports.service import EnergyReportService

logger = logging.getLogger("nouankany.reports")

router = APIRouter()

_service: EnergyReportService | None = None


def _get_service() -> EnergyReportService:
    global _service
    if _service is None:
        _service = EnergyReportService()
    return _service


_MEDIA_TYPES = {
    ExportFormat.PDF: "application/pdf",
    ExportFormat.DOCX: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ExportFormat.XLSX: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ExportFormat.PPTX: "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}


class ReportGenerateRequest(BaseModel):
    report_type: ReportType = ReportType.DAILY
    export_format: ExportFormat = ExportFormat.PDF
    site_name: str = "Site Industriel Principal"


@router.post(
    "/reports/generate",
    summary="Génère un rapport énergétique (PDF/DOCX/XLSX/PPTX)",
    description="Données factices pour le moment — voir docstring du module.",
)
def generate_report(req: ReportGenerateRequest) -> Response:
    report_data, file_bytes, _ = _get_service().generate_report(
        report_type=req.report_type,
        export_format=req.export_format,
        site_name=req.site_name,
        save_to_disk=False,
    )
    logger.info(
        f"[reports] Rapport {req.report_type.value}/{req.export_format.value} généré "
        f"(report_id={report_data.report_id}, données factices)."
    )
    filename = f"{report_data.report_id}_{req.report_type.value}.{req.export_format.value}"
    return Response(
        content=file_bytes,
        media_type=_MEDIA_TYPES[req.export_format],
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
