"""
app/reports/exporters/pdf_exporter.py — Exportateur de rapports énergétiques au format PDF (ReportLab).
"""

import io
import logging
from typing import Dict, List, Optional
from xml.sax.saxutils import escape as _xml_escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import HRFlowable, Image as RLImage, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.reports.exporters.base import BaseReportExporter
from app.reports.models import EnergyReportData

logger = logging.getLogger("nouankany.reports")


def _safe(value) -> str:
    """Échappe une valeur avant insertion dans un Paragraph() ReportLab, qui
    interprète un sous-ensemble de balises façon HTML dans le texte fourni —
    un champ libre utilisateur (titre, résumé, nom de machine...) ne doit
    jamais y être inséré brut."""
    return _xml_escape(str(value))

PRIMARY_COLOR = colors.HexColor("#0284C7")
SECONDARY_COLOR = colors.HexColor("#0F172A")
ACCENT_COLOR = colors.HexColor("#10B981")
BG_LIGHT = colors.HexColor("#F8FAFC")


class PDFReportExporter(BaseReportExporter):
    """
    Générateur de rapports PDF professionnels et élégants via ReportLab.
    """

    def export(
        self,
        report_data: EnergyReportData,
        chart_images: Optional[Dict[str, bytes]] = None,
    ) -> bytes:
        """
        Génère le document PDF complet avec en-têtes, tableaux de bord, graphiques et recommandations.
        """
        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf,
            pagesize=A4,
            leftMargin=1.5 * cm,
            rightMargin=1.5 * cm,
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=SECONDARY_COLOR,
            alignment=0,
        )
        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#64748B"),
        )
        h2_style = ParagraphStyle(
            "Heading2Custom",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=PRIMARY_COLOR,
            spaceBefore=10,
            spaceAfter=6,
        )
        body_style = ParagraphStyle(
            "BodyCustom",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#334155"),
        )
        bold_body_style = ParagraphStyle(
            "BoldBodyCustom",
            parent=body_style,
            fontName="Helvetica-Bold",
        )

        elements: List[Any] = []

        # 1. En-tête Corporate
        header_table = Table(
            [
                [
                    Paragraph("<b>NOUANKANY.AI</b> | Plateforme d'Efficacité Énergétique", ParagraphStyle("Brand", fontName="Helvetica-Bold", fontSize=11, textColor=PRIMARY_COLOR)),
                    Paragraph(f"Réf : {_safe(report_data.report_id)}", ParagraphStyle("Ref", fontName="Helvetica", fontSize=8, textColor=colors.gray, alignment=2)),
                ]
            ],
            colWidths=[12 * cm, 6 * cm],
        )
        header_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
        elements.append(header_table)
        elements.append(HRFlowable(width="100%", thickness=1, color=PRIMARY_COLOR, spaceBefore=4, spaceAfter=12))

        # 2. Titre du rapport et Métadonnées
        elements.append(Paragraph(_safe(report_data.title), title_style))
        meta_text = (
            f"<b>Site :</b> {_safe(report_data.site_name)} ({_safe(report_data.building_type)}) | "
            f"<b>Période :</b> {_safe(report_data.period_start)} au {_safe(report_data.period_end)} | "
            f"<b>Émis le :</b> {_safe(report_data.generated_at)}"
        )
        elements.append(Paragraph(meta_text, subtitle_style))
        elements.append(Spacer(1, 10))

        # 3. Résumé Exécutif
        elements.append(Paragraph("1. Résumé Exécutif & Faits Marquants", h2_style))
        elements.append(Paragraph(_safe(report_data.executive_summary), body_style))
        elements.append(Spacer(1, 10))

        # 4. Tableau des Indicateurs Clés (KPIs)
        elements.append(Paragraph("2. Indicateurs Clés de Performance (KPIs)", h2_style))
        kpis = report_data.kpis
        kpi_data = [
            [
                Paragraph("<b>Consommation Totale</b>", bold_body_style),
                Paragraph(f"<b>{kpis.total_energy_kwh:,.1f} kWh</b>", body_style),
                Paragraph("<b>Facture Globale</b>", bold_body_style),
                Paragraph(f"<b>{kpis.total_cost_fcfa:,.0f} FCFA</b>", body_style),
            ],
            [
                Paragraph("<b>Consommation Pointe (CIE)</b>", bold_body_style),
                Paragraph(f"{kpis.peak_hours_energy_kwh:,.1f} kWh", body_style),
                Paragraph("<b>Coût Heures de Pointe</b>", bold_body_style),
                Paragraph(f"{kpis.peak_hours_cost_fcfa:,.0f} FCFA", body_style),
            ],
            [
                Paragraph("<b>Économies Effacement</b>", bold_body_style),
                Paragraph(f"<font color='#10B981'><b>+{kpis.peak_shaving_savings_fcfa:,.0f} FCFA</b></font>", body_style),
                Paragraph("<b>Facteur de Puissance</b>", bold_body_style),
                Paragraph(f"cos φ = {kpis.average_power_factor_cos_phi:.2f}", body_style),
            ],
            [
                Paragraph("<b>Puissance Max Atteinte</b>", bold_body_style),
                Paragraph(f"{kpis.max_peak_power_kw:.1f} kW / {kpis.subscribed_power_limit_kw:.0f} kW", body_style),
                Paragraph("<b>Anomalies Détectées</b>", bold_body_style),
                Paragraph(f"{kpis.anomaly_incidents_count} incident(s)", body_style),
            ],
        ]
        kpi_table = Table(kpi_data, colWidths=[4.5 * cm, 4.5 * cm, 4.5 * cm, 4.5 * cm])
        kpi_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), BG_LIGHT),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ])
        )
        elements.append(kpi_table)
        elements.append(Spacer(1, 12))

        # 5. Graphiques Visuels
        if chart_images:
            elements.append(Paragraph("3. Analyse Graphique & Courbes de Charge", h2_style))
            if "load_curve" in chart_images:
                img_stream = io.BytesIO(chart_images["load_curve"])
                elements.append(RLImage(img_stream, width=17.5 * cm, height=8.2 * cm))
                elements.append(Spacer(1, 8))

            if "tariff_pie" in chart_images and "machines_bar" in chart_images:
                pie_stream = io.BytesIO(chart_images["tariff_pie"])
                bar_stream = io.BytesIO(chart_images["machines_bar"])
                charts_row = Table(
                    [
                        [
                            RLImage(pie_stream, width=7.5 * cm, height=5.2 * cm),
                            RLImage(bar_stream, width=9.8 * cm, height=5.2 * cm),
                        ]
                    ],
                    colWidths=[8.0 * cm, 10.0 * cm],
                )
                charts_row.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
                elements.append(charts_row)
                elements.append(Spacer(1, 12))

        # 6. Tableau Détaillé des Machines
        if report_data.machines:
            elements.append(Paragraph("4. Détail par Équipement Majeur", h2_style))
            mach_headers = [
                Paragraph("<b>Machine</b>", bold_body_style),
                Paragraph("<b>Catégorie</b>", bold_body_style),
                Paragraph("<b>Énergie (kWh)</b>", bold_body_style),
                Paragraph("<b>Coût (FCFA)</b>", bold_body_style),
                Paragraph("<b>Heures</b>", bold_body_style),
                Paragraph("<b>Note</b>", bold_body_style),
            ]
            mach_rows = [mach_headers]
            for m in report_data.machines[:8]:
                mach_rows.append([
                    Paragraph(_safe(m.machine_name), body_style),
                    Paragraph(_safe(m.category), body_style),
                    Paragraph(f"{m.energy_kwh:,.1f}", body_style),
                    Paragraph(f"{m.cost_fcfa:,.0f}", body_style),
                    Paragraph(f"{m.running_hours:.1f}h", body_style),
                    Paragraph(f"<b>{_safe(m.efficiency_grade)}</b>", body_style),
                ])
            mach_table = Table(mach_rows, colWidths=[4.5 * cm, 3.5 * cm, 3.0 * cm, 3.2 * cm, 2.0 * cm, 1.8 * cm])
            mach_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG_LIGHT]),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ])
            )
            elements.append(mach_table)
            elements.append(Spacer(1, 12))

        # 7. Recommandations IA & Plan d'Action
        if report_data.recommendations:
            elements.append(Paragraph("5. Recommandations IA & Plan d'Action Énergétique", h2_style))
            for rec in report_data.recommendations:
                prio_color = "#EF4444" if rec.priority == 1 else ("#F59E0B" if rec.priority == 2 else "#10B981")
                prio_label = "PRIORITÉ 1 (IMMÉDIAT)" if rec.priority == 1 else ("PRIORITÉ 2 (COURT TERME)" if rec.priority == 2 else "PRIORITÉ 3 (PRÉVENTIF)")
                rec_card = [
                    [
                        Paragraph(f"<b><font color='{prio_color}'>{prio_label}</font> : {_safe(rec.title)}</b>", bold_body_style),
                        Paragraph(f"<b>Gains : +{rec.estimated_savings_fcfa:,.0f} FCFA ({rec.estimated_savings_kwh:,.0f} kWh)</b>", ParagraphStyle("Gain", parent=bold_body_style, textColor=ACCENT_COLOR, alignment=2)),
                    ],
                    [
                        Paragraph(f"{_safe(rec.description)} <i>(Cible : {_safe(rec.target_equipment)})</i>", body_style),
                        Paragraph("", body_style),
                    ],
                ]
                card_table = Table(rec_card, colWidths=[12.0 * cm, 6.0 * cm])
                card_table.setStyle(
                    TableStyle([
                        ("BACKGROUND", (0, 0), (-1, -1), BG_LIGHT),
                        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
                        ("SPAN", (0, 1), (1, 1)),
                        ("TOPPADDING", (0, 0), (-1, -1), 5),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ])
                )
                elements.append(card_table)
                elements.append(Spacer(1, 6))

        # Construction du PDF
        doc.build(elements)
        buf.seek(0)
        return buf.getvalue()
