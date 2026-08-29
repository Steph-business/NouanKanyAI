"""
app/reports — Module de génération automatique de rapports énergétiques multi-formats (PDF, DOCX, XLSX, PPTX).
"""

from app.reports.charts import ChartGenerator
from app.reports.exporters.base import BaseReportExporter
from app.reports.exporters.docx_exporter import DOCXReportExporter
from app.reports.exporters.pdf_exporter import PDFReportExporter
from app.reports.exporters.pptx_exporter import PPTXReportExporter
from app.reports.exporters.xlsx_exporter import XLSXReportExporter
from app.reports.generator import EnergyReportGenerator
from app.reports.models import (
    AIRecommendationItem,
    AnomalyIncidentItem,
    EnergyReportData,
    ExportFormat,
    MachineConsumptionItem,
    ReportKPIs,
    ReportType,
)
from app.reports.service import EnergyReportService

__all__ = [
    # Modèles
    "ReportType",
    "ExportFormat",
    "ReportKPIs",
    "MachineConsumptionItem",
    "AnomalyIncidentItem",
    "AIRecommendationItem",
    "EnergyReportData",
    # Moteur & Service
    "EnergyReportGenerator",
    "EnergyReportService",
    "ChartGenerator",
    # Exportateurs
    "BaseReportExporter",
    "PDFReportExporter",
    "DOCXReportExporter",
    "XLSXReportExporter",
    "PPTXReportExporter",
]
