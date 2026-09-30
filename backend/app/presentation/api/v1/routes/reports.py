"""Routes HTTP de génération de rapports énergétiques exportables."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.application.use_cases.generate_report import GenerateReportCommand, GenerateReportUseCase
from app.presentation.api.dependencies import get_generate_report_use_case

router = APIRouter()


class ReportRequest(BaseModel):
    """Options de génération et site cible du rapport."""

    report_type: str = Field(default="daily")
    export_format: str = Field(default="pdf")
    site_name: str = Field(..., min_length=1)
    building_type: str = Field(default="Industrie")


@router.post("/reports", tags=["reports"], summary="Générer un rapport énergétique")
async def generate_report(
    payload: ReportRequest,
    use_case: GenerateReportUseCase = Depends(get_generate_report_use_case),
) -> Response:
    """Exécute le use case puis renvoie le fichier avec son type MIME."""
    try:
        report = await use_case.execute(
            GenerateReportCommand(
                report_type=payload.report_type,
                export_format=payload.export_format,
                site_name=payload.site_name,
                building_type=payload.building_type,
            )
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    return Response(
        content=report.content,
        media_type=report.media_type,
        headers={"Content-Disposition": f'attachment; filename="{report.filename}"'},
    )
