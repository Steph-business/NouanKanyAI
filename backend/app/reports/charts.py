"""
app/reports/charts.py — Générateur de visualisations et graphiques pour les rapports énergétiques.
"""

import io
import logging
from typing import Any, Dict, List, Optional
import matplotlib
matplotlib.use("Agg")  # Backend non-interactif sécurisé pour serveurs
import matplotlib.pyplot as plt

from app.reports.models import EnergyReportData

logger = logging.getLogger("nouankany.reports")

# Palette corporate NouanKanyAI
PRIMARY_COLOR = "#0284C7"    # Bleu cyan ciel
SECONDARY_COLOR = "#0F172A"  # Bleu marine profond
ACCENT_COLOR = "#10B981"     # Vert émeraude
WARNING_COLOR = "#F59E0B"    # Ambre
DANGER_COLOR = "#EF4444"     # Rouge écarlate
BACKGROUND_COLOR = "#F8FAFC" # Gris très clair


class ChartGenerator:
    """
    Générateur de graphiques haute résolution (PNG) pour insertion dans PDF, DOCX, PPTX.
    """

    @classmethod
    def generate_load_curve(cls, report: EnergyReportData) -> bytes:
        """
        Génère le graphique de la courbe de charge horaire (kW) avec mise en évidence des heures de pointe CIE (19h-23h).
        """
        fig, ax = plt.subplots(figsize=(8, 3.8), dpi=150, facecolor=BACKGROUND_COLOR)
        ax.set_facecolor("#FFFFFF")

        hours = list(range(24))
        # Profil réaliste si non fourni
        if report.hourly_curve:
            powers = [item.get("power_kw", 40.0) for item in report.hourly_curve[:24]]
            while len(powers) < 24:
                powers.append(powers[-1] if powers else 40.0)
        else:
            powers = [
                35.0, 32.0, 30.0, 30.0, 32.0, 38.0, 55.0, 75.0, 92.0, 98.0, 95.0, 90.0,
                88.0, 94.0, 96.0, 92.0, 85.0, 80.0, 95.0, 118.0, 122.0, 110.0, 85.0, 50.0
            ]

        # Tracé de la courbe
        ax.plot(hours, powers, color=PRIMARY_COLOR, linewidth=2.5, marker="o", markersize=4, label="Puissance active (kW)")
        ax.axhline(y=report.kpis.subscribed_power_limit_kw, color=DANGER_COLOR, linestyle="--", linewidth=1.5, label=f"Puissance souscrite ({int(report.kpis.subscribed_power_limit_kw)} kW)")

        # Zone Heures de Pointe CIE (19h - 23h)
        ax.axvspan(19, 23, color=WARNING_COLOR, alpha=0.25, label="Heures de Pointe CIE (19h-23h)")

        ax.set_title("Courbe de Charge Journalière & Respect de la Puissance Souscrite", fontsize=11, fontweight="bold", color=SECONDARY_COLOR, pad=10)
        ax.set_xlabel("Heure de la journée (h)", fontsize=9, fontweight="bold", color=SECONDARY_COLOR)
        ax.set_ylabel("Puissance (kW)", fontsize=9, fontweight="bold", color=SECONDARY_COLOR)
        ax.set_xticks(hours[::2])
        ax.grid(True, linestyle=":", alpha=0.6, color="#CBD5E1")
        ax.legend(loc="upper left", fontsize=8, framealpha=0.9)
        plt.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=150)
        plt.close(fig)
        buf.seek(0)
        return buf.getvalue()

    @classmethod
    def generate_tariff_pie_chart(cls, report: EnergyReportData) -> bytes:
        """
        Génère le camembert de répartition de consommation par tranche tarifaire CIE.
        """
        fig, ax = plt.subplots(figsize=(5.5, 3.8), dpi=150, facecolor=BACKGROUND_COLOR)
        ax.set_facecolor(BACKGROUND_COLOR)

        total = report.kpis.total_energy_kwh or 1000.0
        peak = report.kpis.peak_hours_energy_kwh or (total * 0.32)
        off_peak = total * 0.20
        standard = max(0.0, total - peak - off_peak)

        slices = [standard, peak, off_peak]
        labels = ["Heures Pleines\n(07h-19h)", "Heures de Pointe\n(19h-23h)", "Heures Creuses\n(23h-07h)"]
        colors = [PRIMARY_COLOR, WARNING_COLOR, ACCENT_COLOR]

        wedges, texts, autotexts = ax.pie(
            slices,
            labels=labels,
            autopct="%1.1f%%",
            startangle=140,
            colors=colors,
            textprops={"fontsize": 8, "color": SECONDARY_COLOR, "fontweight": "bold"},
            wedgeprops={"edgecolor": "#FFFFFF", "linewidth": 1.5},
        )
        for at in autotexts:
            at.set_color("#FFFFFF")
            at.set_fontweight("bold")

        ax.set_title("Répartition de l'Énergie par Tranche CIE", fontsize=10, fontweight="bold", color=SECONDARY_COLOR, pad=10)
        plt.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=150)
        plt.close(fig)
        buf.seek(0)
        return buf.getvalue()

    @classmethod
    def generate_machines_bar_chart(cls, report: EnergyReportData) -> bytes:
        """
        Génère un histogramme horizontal des consommations par équipement.
        """
        fig, ax = plt.subplots(figsize=(7, 3.8), dpi=150, facecolor=BACKGROUND_COLOR)
        ax.set_facecolor("#FFFFFF")

        if report.machines:
            names = [m.machine_name for m in report.machines[:6]]
            values = [m.energy_kwh for m in report.machines[:6]]
        else:
            names = ["Compresseur C1", "Four Industriel F2", "Groupe Froid GF1", "Ligne Convoyeur", "Climatisation Centrale"]
            values = [450.0, 680.0, 320.0, 180.0, 210.0]

        # Inverser pour affichage descendant
        names = names[::-1]
        values = values[::-1]

        bars = ax.barh(names, values, color=PRIMARY_COLOR, edgecolor="#0284C7", height=0.55)
        for bar in bars:
            w = bar.get_width()
            ax.text(w + max(values)*0.02, bar.get_y() + bar.get_height()/2, f"{w:,.0f} kWh", va="center", ha="left", fontsize=8, fontweight="bold", color=SECONDARY_COLOR)

        ax.set_title("Consommation par Équipement Majeur", fontsize=10, fontweight="bold", color=SECONDARY_COLOR, pad=10)
        ax.set_xlabel("Énergie (kWh)", fontsize=9, fontweight="bold", color=SECONDARY_COLOR)
        ax.set_xlim(0, max(values) * 1.25)
        ax.grid(True, linestyle=":", alpha=0.5, axis="x", color="#CBD5E1")
        plt.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=150)
        plt.close(fig)
        buf.seek(0)
        return buf.getvalue()

    @classmethod
    def generate_all_charts(cls, report: EnergyReportData) -> Dict[str, bytes]:
        """Génère l'ensemble des graphiques pour un rapport donné."""
        return {
            "load_curve": cls.generate_load_curve(report),
            "tariff_pie": cls.generate_tariff_pie_chart(report),
            "machines_bar": cls.generate_machines_bar_chart(report),
        }
