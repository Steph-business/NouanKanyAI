"""
app/reports/models.py — Modèles Pydantic v2 pour les rapports énergétiques industriels.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class ReportType(str, Enum):
    """Types de rapports pris en charge par le générateur."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ENERGY_AUDIT = "energy_audit"
    ANOMALY_REPORT = "anomaly_report"
    PERFORMANCE_REPORT = "performance_report"


class ExportFormat(str, Enum):
    """Formats d'exportation supportés."""

    PDF = "pdf"
    DOCX = "docx"
    XLSX = "xlsx"
    PPTX = "pptx"


class ReportKPIs(BaseModel):
    """Indicateurs clés de performance énergétique (KPIs)."""

    model_config = ConfigDict(frozen=True)

    total_energy_kwh: float = Field(..., description="Consommation totale en kWh")
    total_cost_fcfa: float = Field(..., description="Facture globale estimée en FCFA")
    peak_hours_energy_kwh: float = Field(default=0.0, description="Consommation en heures de pointe CIE (19h-23h) en kWh")
    peak_hours_cost_fcfa: float = Field(default=0.0, description="Coût en heures de pointe en FCFA")
    peak_shaving_savings_fcfa: float = Field(default=0.0, description="Économies financières réalisées par effacement (FCFA)")
    average_power_factor_cos_phi: float = Field(default=0.94, description="Facteur de puissance moyen (cos phi)")
    max_peak_power_kw: float = Field(default=0.0, description="Puissance maximale atteinte en kW")
    subscribed_power_limit_kw: float = Field(default=250.0, description="Puissance souscrite au contrat CIE en kW")
    carbon_emissions_kg_co2: float = Field(default=0.0, description="Émissions de CO2 estimées en kg")
    anomaly_incidents_count: int = Field(default=0, description="Nombre d'anomalies détectées sur la période")


class MachineConsumptionItem(BaseModel):
    """Détail de consommation d'un équipement surveillé."""

    model_config = ConfigDict(frozen=True)

    machine_name: str = Field(..., description="Nom ou repère technique de la machine")
    category: str = Field(default="Production", description="Catégorie (Air comprimé, Froid, Cuisson, Force motrice)")
    energy_kwh: float = Field(..., description="Consommation sur la période en kWh")
    cost_fcfa: float = Field(..., description="Coût associé en FCFA")
    running_hours: float = Field(default=0.0, description="Nombre d'heures de fonctionnement")
    status: str = Field(default="RUNNING", description="Statut opérationnel")
    efficiency_grade: str = Field(default="A", description="Note d'efficacité énergétique (A, B, C, D)")


class AnomalyIncidentItem(BaseModel):
    """Incident ou dérive opérationnelle enregistrée."""

    model_config = ConfigDict(frozen=True)

    incident_id: str = Field(default_factory=lambda: f"INC-{uuid.uuid4().hex[:6].upper()}")
    timestamp: str = Field(..., description="Date et heure de survenue")
    equipment: str = Field(..., description="Équipement concerné")
    severity: str = Field(default="modérée", description="Niveau de gravité (faible, modérée, critique)")
    anomaly_score: float = Field(default=-0.15, description="Score d'anomalie Isolation Forest")
    description: str = Field(..., description="Description de l'anomalie constatée")
    action_taken: str = Field(default="Notification envoyée à l'équipe maintenance", description="Action corrective")


class AIRecommendationItem(BaseModel):
    """Préconisation d'optimisation énergétique formulée par l'IA."""

    model_config = ConfigDict(frozen=True)

    priority: int = Field(default=1, description="Niveau de priorité (1 = Immédiat/Urgent, 2 = Court terme, 3 = Préventif)")
    title: str = Field(..., description="Titre concis de la recommandation")
    description: str = Field(..., description="Détail des actions à entreprendre")
    estimated_savings_fcfa: float = Field(default=0.0, description="Économies financières estimées en FCFA")
    estimated_savings_kwh: float = Field(default=0.0, description="Économies d'énergie estimées en kWh")
    target_equipment: str = Field(default="Site Global", description="Équipement ou secteur cible")


class EnergyReportData(BaseModel):
    """Données intégrales normalisées pour la génération d'un rapport énergétique."""

    model_config = ConfigDict(extra="allow")

    report_id: str = Field(default_factory=lambda: f"REP-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}")
    title: str = Field(..., description="Titre officiel du rapport")
    report_type: ReportType = Field(default=ReportType.DAILY, description="Typologie du rapport")
    organization_name: str = Field(default="Industrie Agroalimentaire CI", description="Nom de l'entreprise")
    site_name: str = Field(default="Site Industriel Abidjan Nord", description="Nom du site")
    building_type: str = Field(default="Industrie", description="Typologie du bâtiment")
    period_start: str = Field(..., description="Date/Heure de début de période")
    period_end: str = Field(..., description="Date/Heure de fin de période")
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))
    author: str = Field(default="NouanKanyAI Copilot Engine", description="Auteur ou système émetteur")
    executive_summary: str = Field(..., description="Résumé exécutif structuré pour la direction")
    kpis: ReportKPIs = Field(..., description="KPIs consolidés")
    machines: List[MachineConsumptionItem] = Field(default_factory=list, description="Tableau machine par machine")
    anomalies: List[AnomalyIncidentItem] = Field(default_factory=list, description="Registre des anomalies")
    recommendations: List[AIRecommendationItem] = Field(default_factory=list, description="Recommandations IA")
    hourly_curve: Optional[List[Dict[str, Any]]] = Field(default=None, description="Données de courbe de charge horaire (kW)")
