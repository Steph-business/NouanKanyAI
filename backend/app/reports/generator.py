"""
app/reports/generator.py — Moteur central de génération et d'exportation de rapports énergétiques.
"""

from datetime import datetime, timezone
import io
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from app.reports.charts import ChartGenerator
from app.reports.exporters.base import BaseReportExporter
from app.reports.exporters.docx_exporter import DOCXReportExporter
from app.reports.exporters.pdf_exporter import PDFReportExporter
from app.reports.exporters.pptx_exporter import PPTXReportExporter
from app.reports.exporters.xlsx_exporter import XLSXReportExporter
from app.reports.models import (
    AIRecommendationItem,
    AnomalyIncidentItem,
    EnergyReportData,
    ExportFormat,
    MachineConsumptionItem,
    ReportKPIs,
    ReportType,
)

logger = logging.getLogger("nouankany.reports")


class EnergyReportGenerator:
    """
    Générateur modulaire capable de compiler les données d'audit et de produire
    les documents aux formats PDF, DOCX, XLSX et PPTX.
    """

    def __init__(self) -> None:
        self._exporters: Dict[ExportFormat, BaseReportExporter] = {
            ExportFormat.PDF: PDFReportExporter(),
            ExportFormat.DOCX: DOCXReportExporter(),
            ExportFormat.XLSX: XLSXReportExporter(),
            ExportFormat.PPTX: PPTXReportExporter(),
        }
        logger.debug("[EnergyReportGenerator] Initialisé avec 4 exportateurs (PDF, DOCX, XLSX, PPTX).")

    def create_mock_report_data(
        self,
        report_type: ReportType = ReportType.DAILY,
        site_name: str = "Site Industriel Abidjan Nord",
        building_type: str = "Usine Agroalimentaire",
        organization_name: str = "Agro-Industrie Côte d'Ivoire",
    ) -> EnergyReportData:
        """
        Construit un jeu complet de données de rapport selon le type demandé.
        """
        now = datetime.now(timezone.utc)
        date_str = now.strftime("%Y-%m-%d")

        if report_type == ReportType.DAILY:
            title = f"Rapport Énergétique Journalier — {date_str}"
            p_start = f"{date_str} 00:00:00"
            p_end = f"{date_str} 23:59:59"
            kpis = ReportKPIs(
                total_energy_kwh=2150.0,
                total_cost_fcfa=182750.0,
                peak_hours_energy_kwh=680.0,
                peak_hours_cost_fcfa=98600.0,
                peak_shaving_savings_fcfa=32500.0,
                average_power_factor_cos_phi=0.95,
                max_peak_power_kw=118.4,
                subscribed_power_limit_kw=250.0,
                carbon_emissions_kg_co2=480.0,
                anomaly_incidents_count=1,
            )
            summary = (
                f"Sur la journée du {date_str}, la consommation globale s'établit à 2 150 kWh pour une facture estimée à 182 750 FCFA. "
                "Le délestage préventif du Compresseur C2 entre 19h15 et 21h00 a permis de maintenir la puissance sous la limite contractuelle (118.4 kW / 250 kW), "
                "générant une économie nette de 32 500 FCFA sur la tranche critique de pointe CIE."
            )

        elif report_type == ReportType.WEEKLY:
            title = f"Bilan Énergétique Hebdomadaire — Semaine {now.isocalendar()[1]}"
            p_start = "2026-08-22 00:00:00"
            p_end = "2026-08-28 23:59:59"
            kpis = ReportKPIs(
                total_energy_kwh=14850.0,
                total_cost_fcfa=1262250.0,
                peak_hours_energy_kwh=4600.0,
                peak_hours_cost_fcfa=667000.0,
                peak_shaving_savings_fcfa=215000.0,
                average_power_factor_cos_phi=0.94,
                max_peak_power_kw=128.0,
                subscribed_power_limit_kw=250.0,
                carbon_emissions_kg_co2=3320.0,
                anomaly_incidents_count=2,
            )
            summary = (
                "Bilan hebdomadaire positif avec une baisse de 6.2% de la consommation en heures pleines. "
                "Deux alertes de dérive thermique ont été traitées sur le Four F2 sans impact sur la chaîne de production."
            )

        elif report_type == ReportType.MONTHLY:
            title = f"Rapport Mensuel d'Efficacité Énergétique — {now.strftime('%B %Y')}"
            p_start = "2026-08-01 00:00:00"
            p_end = "2026-08-28 23:59:59"
            kpis = ReportKPIs(
                total_energy_kwh=62400.0,
                total_cost_fcfa=5304000.0,
                peak_hours_energy_kwh=18900.0,
                peak_hours_cost_fcfa=2740500.0,
                peak_shaving_savings_fcfa=890000.0,
                average_power_factor_cos_phi=0.96,
                max_peak_power_kw=132.5,
                subscribed_power_limit_kw=250.0,
                carbon_emissions_kg_co2=13950.0,
                anomaly_incidents_count=4,
            )
            summary = (
                "Le suivi continu par NouanKanyAI a permis d'économiser 890 000 FCFA sur le mois grâce à l'optimisation des tranches CIE "
                "et à la régulation automatisée du groupe froid. Le facteur de puissance moyen reste excellent (cos φ = 0.96)."
            )

        elif report_type == ReportType.ENERGY_AUDIT:
            title = "Rapport d'Audit Énergétique Approfondi (ISO 50001)"
            p_start = "2026-01-01 00:00:00"
            p_end = "2026-08-28 23:59:59"
            kpis = ReportKPIs(
                total_energy_kwh=480000.0,
                total_cost_fcfa=40800000.0,
                peak_hours_energy_kwh=145000.0,
                peak_hours_cost_fcfa=21025000.0,
                peak_shaving_savings_fcfa=6500000.0,
                average_power_factor_cos_phi=0.94,
                max_peak_power_kw=145.0,
                subscribed_power_limit_kw=250.0,
                carbon_emissions_kg_co2=107500.0,
                anomaly_incidents_count=8,
            )
            summary = (
                "Audit de conformité ISO 50001. Identification d'un potentiel d'économies additionnelles de 18% "
                "par l'installation de variateurs de vitesse sur les moteurs de ventilation et l'optimisation du réseau vapeur."
            )

        elif report_type == ReportType.ANOMALY_REPORT:
            title = "Rapport Spécial d'Anomalies & Diagnostic Prédictif"
            p_start = "2026-08-20 00:00:00"
            p_end = "2026-08-28 23:59:59"
            kpis = ReportKPIs(
                total_energy_kwh=18500.0,
                total_cost_fcfa=1572500.0,
                peak_hours_energy_kwh=5800.0,
                peak_hours_cost_fcfa=841000.0,
                peak_shaving_savings_fcfa=140000.0,
                average_power_factor_cos_phi=0.91,
                max_peak_power_kw=142.0,
                subscribed_power_limit_kw=250.0,
                carbon_emissions_kg_co2=4140.0,
                anomaly_incidents_count=5,
            )
            summary = (
                "Analyse des 5 incidents détectés par Isolation Forest. Une anomalie critique sur le Compresseur C1 (surchauffe 92°C) "
                "a été résolue par le nettoyage préventif des échangeurs."
            )

        else:  # PERFORMANCE_REPORT
            title = "Rapport de Performance Énergétique & Bilan Carbone"
            p_start = "2026-08-01 00:00:00"
            p_end = "2026-08-28 23:59:59"
            kpis = ReportKPIs(
                total_energy_kwh=58200.0,
                total_cost_fcfa=4947000.0,
                peak_hours_energy_kwh=17200.0,
                peak_hours_cost_fcfa=2494000.0,
                peak_shaving_savings_fcfa=780000.0,
                average_power_factor_cos_phi=0.95,
                max_peak_power_kw=125.0,
                subscribed_power_limit_kw=250.0,
                carbon_emissions_kg_co2=13020.0,
                anomaly_incidents_count=2,
            )
            summary = (
                "Indicateurs d'intensité énergétique par tonne produite en amélioration de 4.8%. "
                "Conformité réglementaire CIE et respect strict des seuils de puissance."
            )

        machines = [
            MachineConsumptionItem(machine_name="Compresseur d'Air C1", category="Air Comprimé", energy_kwh=620.0, cost_fcfa=52700.0, running_hours=18.5, status="RUNNING", efficiency_grade="A"),
            MachineConsumptionItem(machine_name="Four Industriel F2", category="Thermique", energy_kwh=850.0, cost_fcfa=72250.0, running_hours=14.0, status="RUNNING", efficiency_grade="B"),
            MachineConsumptionItem(machine_name="Groupe Froid GF1", category="Froid", energy_kwh=410.0, cost_fcfa=34850.0, running_hours=24.0, status="RUNNING", efficiency_grade="A"),
            MachineConsumptionItem(machine_name="Ligne d'Embouteillage", category="Force Motrice", energy_kwh=180.0, cost_fcfa=15300.0, running_hours=12.5, status="STOPPED", efficiency_grade="A"),
            MachineConsumptionItem(machine_name="Climatisation Administrative", category="CVC", energy_kwh=90.0, cost_fcfa=7650.0, running_hours=10.0, status="RUNNING", efficiency_grade="C"),
        ]

        anomalies = [
            AnomalyIncidentItem(
                incident_id="INC-0828-A",
                timestamp=f"{date_str} 15:42:00",
                equipment="Compresseur d'Air C1",
                severity="modérée",
                anomaly_score=-0.22,
                description="Élévation anormale de température (78°C vs 65°C nominal) et pic de vibration.",
                action_taken="Nettoyage du filtre d'aspiration et contrôle lubrifiant.",
            ),
            AnomalyIncidentItem(
                incident_id="INC-0828-B",
                timestamp=f"{date_str} 19:10:00",
                equipment="Four Industriel F2",
                severity="critique",
                anomaly_score=-0.38,
                description="Tentative de préchauffage pendant la pointe CIE (19h10).",
                action_taken="Délestage automatique activé et report à 23h05.",
            ),
        ]

        recommendations = [
            AIRecommendationItem(
                priority=1,
                title="Délestage automatique du Four F2 de 19h00 à 23h00",
                description="Reporter la phase de cuisson secondaire en heures creuses (23h-07h) pour économiser le différentiel tarifaire CIE (145 vs 55 FCFA/kWh).",
                estimated_savings_fcfa=245000.0,
                estimated_savings_kwh=2700.0,
                target_equipment="Four Industriel F2",
            ),
            AIRecommendationItem(
                priority=2,
                title="Calorifugeage des conduits d'eau glacée du Groupe Froid GF1",
                description="Réduire les pertes thermiques sur le réseau de distribution pour améliorer le COP de 0.4 point.",
                estimated_savings_fcfa=180000.0,
                estimated_savings_kwh=2100.0,
                target_equipment="Groupe Froid GF1",
            ),
            AIRecommendationItem(
                priority=3,
                title="Installation d'un banc de condensateurs de 50 kVAR",
                description="Relever le facteur de puissance de 0.94 à 0.98 pour annuler toute pénalité réactive CIE.",
                estimated_savings_fcfa=95000.0,
                estimated_savings_kwh=0.0,
                target_equipment="TGBT Principal",
            ),
        ]

        return EnergyReportData(
            title=title,
            report_type=report_type,
            organization_name=organization_name,
            site_name=site_name,
            building_type=building_type,
            period_start=p_start,
            period_end=p_end,
            executive_summary=summary,
            kpis=kpis,
            machines=machines,
            anomalies=anomalies,
            recommendations=recommendations,
        )

    def export(
        self,
        report_data: EnergyReportData,
        export_format: Union[ExportFormat, str] = ExportFormat.PDF,
        output_path: Optional[Union[str, Path]] = None,
        generate_charts: bool = True,
    ) -> bytes:
        """
        Exporte un rapport dans le format cible (PDF, DOCX, XLSX, PPTX).

        :param report_data: Données complètes du rapport.
        :param export_format: Format d'exportation souhaité.
        :param output_path: Chemin de fichier de destination optionnel.
        :param generate_charts: Si True, calcule et intègre les graphiques.
        :return: Octets du document généré.
        """
        # Normalisation du format
        fmt = (
            export_format
            if isinstance(export_format, ExportFormat)
            else ExportFormat(str(export_format).lower())
        )

        exporter = self._exporters.get(fmt)
        if not exporter:
            raise ValueError(f"Format d'exportation non supporté : '{export_format}'")

        # 1. Génération des graphiques si demandé
        chart_images: Optional[Dict[str, bytes]] = None
        if generate_charts:
            try:
                chart_images = ChartGenerator.generate_all_charts(report_data)
            except Exception as e:
                logger.warning(f"[EnergyReportGenerator] Erreur lors de la génération des graphiques : {e}")

        # 2. Exportation binaire via le module spécialisé
        document_bytes = exporter.export(report_data, chart_images=chart_images)

        # 3. Sauvegarde sur disque si un chemin est fourni
        if output_path:
            p = Path(output_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, "wb") as f:
                f.write(document_bytes)
            logger.info(f"[EnergyReportGenerator] Rapport sauvegardé sous : {p.resolve()}")

        return document_bytes
