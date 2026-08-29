"""
app/reports/service.py — Service métier pour la gestion et la génération de rapports énergétiques.
"""

from datetime import datetime, timezone
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from app.reports.generator import EnergyReportGenerator
from app.reports.models import EnergyReportData, ExportFormat, ReportType

logger = logging.getLogger("nouankany.reports")

DEFAULT_REPORTS_OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "storage" / "reports"


class EnergyReportService:
    """
    Service d'orchestration pour la génération planifiée ou à la demande de rapports énergétiques.
    """

    def __init__(
        self,
        generator: Optional[EnergyReportGenerator] = None,
        output_dir: Optional[Union[str, Path]] = None,
    ) -> None:
        self.generator = generator or EnergyReportGenerator()
        self.output_dir = Path(output_dir) if output_dir else DEFAULT_REPORTS_OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"[EnergyReportService] Service initialisé (dossier={self.output_dir}).")

    def generate_report(
        self,
        report_type: Union[ReportType, str] = ReportType.DAILY,
        export_format: Union[ExportFormat, str] = ExportFormat.PDF,
        site_name: str = "Site Industriel Principal",
        building_type: str = "Industrie",
        save_to_disk: bool = False,
    ) -> tuple[EnergyReportData, bytes, Optional[Path]]:
        """
        Produit un rapport complet et retourne les métadonnées, le contenu binaire et le chemin optionnel.

        :param report_type: Type de rapport (daily, weekly, monthly, energy_audit, anomaly_report, performance_report).
        :param export_format: Format (pdf, docx, xlsx, pptx).
        :param site_name: Nom du site.
        :param building_type: Typologie du bâtiment.
        :param save_to_disk: Si True, enregistre le fichier dans le répertoire de stockage.
        :return: Tuple (report_data, file_bytes, file_path_or_none).
        """
        rep_type = (
            report_type
            if isinstance(report_type, ReportType)
            else ReportType(str(report_type).lower())
        )
        exp_fmt = (
            export_format
            if isinstance(export_format, ExportFormat)
            else ExportFormat(str(export_format).lower())
        )

        # 1. Compilation des données métier
        report_data = self.generator.create_mock_report_data(
            report_type=rep_type,
            site_name=site_name,
            building_type=building_type,
        )

        # 2. Détermination du chemin de sortie si sauvegarde activée
        file_path: Optional[Path] = None
        if save_to_disk:
            filename = f"{report_data.report_id}_{rep_type.value}.{exp_fmt.value}"
            file_path = self.output_dir / filename

        # 3. Exportation du document
        file_bytes = self.generator.export(
            report_data=report_data,
            export_format=exp_fmt,
            output_path=file_path,
            generate_charts=True,
        )

        return report_data, file_bytes, file_path
