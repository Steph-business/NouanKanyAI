"""
backend/tests/reports/test_reports.py — Tests unitaires et d'intégration pour le générateur de rapports énergétiques.
"""

import os
from pathlib import Path
import pytest

from app.reports import (
    EnergyReportGenerator,
    EnergyReportService,
    EnergyReportData,
    ReportType,
    ExportFormat,
    ChartGenerator,
    PDFReportExporter,
    DOCXReportExporter,
    XLSXReportExporter,
    PPTXReportExporter,
)


class TestEnergyReportsSuite:
    """Suite de tests pour la génération et l'exportation des rapports énergétiques multi-formats."""

    @pytest.fixture(autouse=True)
    def setup_generator(self):
        self.generator = EnergyReportGenerator()
        self.service = EnergyReportService()

    def test_all_six_report_types_data_generation(self):
        """Vérifie la génération des 6 types de rapports requis avec leurs KPIs et résumés."""
        types_to_test = [
            ReportType.DAILY,
            ReportType.WEEKLY,
            ReportType.MONTHLY,
            ReportType.ENERGY_AUDIT,
            ReportType.ANOMALY_REPORT,
            ReportType.PERFORMANCE_REPORT,
        ]

        for rep_type in types_to_test:
            data = self.generator.create_mock_report_data(report_type=rep_type)
            assert isinstance(data, EnergyReportData)
            assert data.report_type == rep_type
            assert len(data.title) > 5
            assert len(data.executive_summary) > 20
            assert data.kpis.total_energy_kwh > 0
            assert data.kpis.total_cost_fcfa > 0
            assert len(data.machines) >= 3
            assert len(data.recommendations) >= 2

    def test_chart_generator_png_buffers(self):
        """Vérifie que le générateur de graphiques produit des flux PNG valides."""
        data = self.generator.create_mock_report_data(report_type=ReportType.DAILY)
        charts = ChartGenerator.generate_all_charts(data)

        assert "load_curve" in charts
        assert "tariff_pie" in charts
        assert "machines_bar" in charts

        png_header = b"\x89PNG\r\n\x1a\n"
        for name, img_bytes in charts.items():
            assert isinstance(img_bytes, bytes)
            assert len(img_bytes) > 1000
            assert img_bytes.startswith(png_header), f"Le graphique '{name}' n'a pas un en-tête PNG valide."

    def test_pdf_exporter(self):
        """Vérifie la génération d'un document PDF valide (signature %PDF)."""
        data = self.generator.create_mock_report_data(report_type=ReportType.DAILY)
        charts = ChartGenerator.generate_all_charts(data)
        pdf_exporter = PDFReportExporter()

        pdf_bytes = pdf_exporter.export(data, chart_images=charts)
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 2000
        assert pdf_bytes.startswith(b"%PDF"), "Le fichier généré n'est pas un document PDF valide."

    def test_docx_exporter(self):
        """Vérifie la génération d'un document Microsoft Word (.docx)."""
        data = self.generator.create_mock_report_data(report_type=ReportType.WEEKLY)
        charts = ChartGenerator.generate_all_charts(data)
        docx_exporter = DOCXReportExporter()

        docx_bytes = docx_exporter.export(data, chart_images=charts)
        assert isinstance(docx_bytes, bytes)
        assert len(docx_bytes) > 2000
        # Signature ZIP / OpenXML
        assert docx_bytes.startswith(b"PK\x03\x04"), "Le fichier généré n'est pas une archive OpenXML valide."

    def test_xlsx_exporter(self):
        """Vérifie la génération d'un classeur Excel multi-onglets (.xlsx)."""
        data = self.generator.create_mock_report_data(report_type=ReportType.MONTHLY)
        xlsx_exporter = XLSXReportExporter()

        xlsx_bytes = xlsx_exporter.export(data)
        assert isinstance(xlsx_bytes, bytes)
        assert len(xlsx_bytes) > 2000
        assert xlsx_bytes.startswith(b"PK\x03\x04"), "Le fichier généré n'est pas un classeur Excel valide."

    def test_pptx_exporter(self):
        """Vérifie la génération d'une présentation PowerPoint (.pptx)."""
        data = self.generator.create_mock_report_data(report_type=ReportType.ENERGY_AUDIT)
        charts = ChartGenerator.generate_all_charts(data)
        pptx_exporter = PPTXReportExporter()

        pptx_bytes = pptx_exporter.export(data, chart_images=charts)
        assert isinstance(pptx_bytes, bytes)
        assert len(pptx_bytes) > 2000
        assert pptx_bytes.startswith(b"PK\x03\x04"), "Le fichier généré n'est pas une présentation PowerPoint valide."

    def test_generator_export_all_four_formats(self, tmp_path):
        """Vérifie que EnergyReportGenerator peut exporter dans les 4 formats avec sauvegarde sur disque."""
        data = self.generator.create_mock_report_data(report_type=ReportType.PERFORMANCE_REPORT)

        formats = [
            (ExportFormat.PDF, "test_report.pdf"),
            (ExportFormat.DOCX, "test_report.docx"),
            (ExportFormat.XLSX, "test_report.xlsx"),
            (ExportFormat.PPTX, "test_report.pptx"),
        ]

        for fmt, filename in formats:
            out_file = tmp_path / filename
            doc_bytes = self.generator.export(
                report_data=data,
                export_format=fmt,
                output_path=out_file,
                generate_charts=True,
            )
            assert isinstance(doc_bytes, bytes)
            assert out_file.is_file()
            assert out_file.stat().st_size > 1000

    def test_energy_report_service_end_to_end(self, tmp_path):
        """Vérifie le service de haut niveau avec création de fichier."""
        service = EnergyReportService(output_dir=tmp_path)
        report_data, file_bytes, file_path = service.generate_report(
            report_type="monthly",
            export_format="pdf",
            site_name="Usine Agro Test",
            save_to_disk=True,
        )

        assert report_data.site_name == "Usine Agro Test"
        assert len(file_bytes) > 1000
        assert file_path is not None
        assert file_path.is_file()
        assert file_path.suffix == ".pdf"
