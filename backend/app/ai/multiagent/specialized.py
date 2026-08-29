"""
app/ai/multiagent/specialized.py — Abstractions et squelettes pour les 10 agents spécialisés.

Définit les contrats d'expertise, les capacités de routage sémantique et les interfaces
des 10 agents collaboratifs de NouanKanyAI.
"""

from typing import Any, Dict, List
from app.ai.multiagent.base import BaseAgent
from app.ai.multiagent.blackboard import SharedAgentBlackboard
from app.ai.multiagent.models import AgentResult, AgentTask, AgentType


def _match_keywords(query: str, keywords: List[str]) -> float:
    """Calcule un score d'adéquation basé sur la présence de mots-clés dans la requête."""
    q = query.lower()
    matches = sum(1 for kw in keywords if kw.lower() in q)
    return min(1.0, float(matches) / max(len(keywords) * 0.4, 1.0))


# =====================================================================
# 1. Energy Agent
# =====================================================================

class EnergyAgent(BaseAgent):
    """Agent expert en monitoring global de la puissance et du bilan énergétique."""

    @property
    def agent_type(self) -> AgentType:
        return AgentType.ENERGY

    @property
    def name(self) -> str:
        return "Energy Monitoring Agent"

    @property
    def description(self) -> str:
        return "Supervise la puissance active globale, le facteur de puissance et le respect de la puissance souscrite CIE."

    @property
    def capabilities(self) -> List[str]:
        return ["puissance", "énergie", "kwh", "kw", "charge", "cos phi", "consommation", "souscrite", "tgbt", "compteur"]

    def can_handle(self, task: AgentTask) -> float:
        return _match_keywords(task.query, self.capabilities)

    def process(self, task: AgentTask, blackboard: SharedAgentBlackboard) -> AgentResult:
        total_kw = float(blackboard.get_value("total_power_kw", 118.5))
        subscribed = float(blackboard.get_value("subscribed_limit_kw", 250.0))
        blackboard.set_value("active_power_kw", total_kw, author=self.agent_type)

        return AgentResult(
            agent_type=self.agent_type,
            agent_name=self.name,
            data={"total_power_kw": total_kw, "subscribed_limit_kw": subscribed, "load_factor_pct": 72.4},
            insights=[f"Puissance active actuelle : {total_kw} kW (Marge disponible : {subscribed - total_kw:.1f} kW)."],
            recommendations=["Maintenir la surveillance de charge avant l'entrée en pointe CIE (19h)."],
            confidence_score=0.98,
        )


# =====================================================================
# 2. Forecast Agent
# =====================================================================

class ForecastAgent(BaseAgent):
    """Agent d'inférence et de projection de charge via XGBoost."""

    @property
    def agent_type(self) -> AgentType:
        return AgentType.FORECAST

    @property
    def name(self) -> str:
        return "Load Forecasting Agent"

    @property
    def description(self) -> str:
        return "Prédit la demande électrique future (t+1h à t+24h) à partir des modèles ML XGBoost et de la météo."

    @property
    def capabilities(self) -> List[str]:
        return ["prévision", "prédire", "forecast", "future", "demain", "t+1", "xgboost", "tendance", "projection"]

    def can_handle(self, task: AgentTask) -> float:
        return _match_keywords(task.query, self.capabilities)

    def process(self, task: AgentTask, blackboard: SharedAgentBlackboard) -> AgentResult:
        predicted_kw = 125.0
        blackboard.set_value("forecast_t_plus_1_kw", predicted_kw, author=self.agent_type)

        return AgentResult(
            agent_type=self.agent_type,
            agent_name=self.name,
            data={"predicted_power_kw": predicted_kw, "model": "XGBoost_Forecaster_v2", "horizon": "t+1h"},
            insights=[f"Prévision de charge pour la prochaine heure : {predicted_kw} kW."],
            recommendations=["Préparer un délestage séquentiel si la puissance prévue dépasse 140 kW."],
            confidence_score=0.94,
        )


# =====================================================================
# 3. Anomaly Agent
# =====================================================================

class AnomalyAgent(BaseAgent):
    """Agent de détection précoce des dérives et anomalies opérationnelles via Isolation Forest."""

    @property
    def agent_type(self) -> AgentType:
        return AgentType.ANOMALY

    @property
    def name(self) -> str:
        return "Anomaly Detection Agent"

    @property
    def description(self) -> str:
        return "Détecte les comportements anormaux, les surconsommations inexpliquées et les dérives thermiques/vibratoires."

    @property
    def capabilities(self) -> List[str]:
        return ["anomalie", "dérive", "isolation forest", "alarme", "bizarre", "surchauffe", "dysfonctionnement", "fuite"]

    def can_handle(self, task: AgentTask) -> float:
        return _match_keywords(task.query, self.capabilities)

    def process(self, task: AgentTask, blackboard: SharedAgentBlackboard) -> AgentResult:
        is_anom = False
        blackboard.set_value("has_active_anomaly", is_anom, author=self.agent_type)

        return AgentResult(
            agent_type=self.agent_type,
            agent_name=self.name,
            data={"anomaly_detected": is_anom, "severity": "normal", "score": 0.18},
            insights=["Fonctionnement nominal détecté sur l'ensemble des groupes surveillés."],
            recommendations=["Poursuivre la surveillance en continu des signatures vibratoires."],
            confidence_score=0.96,
        )


# =====================================================================
# 4. Maintenance Agent
# =====================================================================

class MaintenanceAgent(BaseAgent):
    """Agent expert en maintenance prédictive et santé des actifs industriels."""

    @property
    def agent_type(self) -> AgentType:
        return AgentType.MAINTENANCE

    @property
    def name(self) -> str:
        return "Predictive Maintenance Agent"

    @property
    def description(self) -> str:
        return "Évalue l'usure des équipements, le MTBF et préconise les interventions de maintenance avant défaillance."

    @property
    def capabilities(self) -> List[str]:
        return ["maintenance", "panne", "usure", "révision", "filtre", "moteur", "vidange", "roulement", "mtbf", "vibration"]

    def can_handle(self, task: AgentTask) -> float:
        return _match_keywords(task.query, self.capabilities)

    def process(self, task: AgentTask, blackboard: SharedAgentBlackboard) -> AgentResult:
        return AgentResult(
            agent_type=self.agent_type,
            agent_name=self.name,
            data={"critical_equipment": "Compresseur C1", "health_score_pct": 88, "next_maintenance_days": 18},
            insights=["Le Compresseur C1 montre un encrassement léger du filtre à air."],
            recommendations=["Planifier le nettoyage du filtre d'aspiration lors du prochain arrêt programmé."],
            confidence_score=0.91,
        )


# =====================================================================
# 5. Optimization Agent
# =====================================================================

class OptimizationAgent(BaseAgent):
    """Agent d'optimisation opérationnelle et d'effacement de pointe (Peak Shaving)."""

    @property
    def agent_type(self) -> AgentType:
        return AgentType.OPTIMIZATION

    @property
    def name(self) -> str:
        return "Peak Shaving & Optimization Agent"

    @property
    def description(self) -> str:
        return "Génère des plans de délestage dynamique, de modulation de charge et d'arbitrage heures pleines/pointes CIE."

    @property
    def capabilities(self) -> List[str]:
        return ["optimiser", "délestage", "effacement", "pointe", "shaving", "arbitrage", "planning", "modulation", "report"]

    def can_handle(self, task: AgentTask) -> float:
        return _match_keywords(task.query, self.capabilities)

    def process(self, task: AgentTask, blackboard: SharedAgentBlackboard) -> AgentResult:
        savings = 45000.0
        blackboard.set_value("potential_savings_fcfa", savings, author=self.agent_type)

        return AgentResult(
            agent_type=self.agent_type,
            agent_name=self.name,
            data={"strategy": "Effacement séquentiel", "target_window": "19h00-23h00", "estimated_savings_fcfa": savings},
            insights=["Report de charge du Four F2 possible entre 19h et 23h."],
            recommendations=["Activer la consigne de délestage automatique à partir de 18h45."],
            confidence_score=0.95,
        )


# =====================================================================
# 6. Reporting Agent
# =====================================================================

class ReportingAgent(BaseAgent):
    """Agent de synthèse, d'audit documentaire et de génération de rapports."""

    @property
    def agent_type(self) -> AgentType:
        return AgentType.REPORTING

    @property
    def name(self) -> str:
        return "Executive Reporting Agent"

    @property
    def description(self) -> str:
        return "Compile les bilans énergétiques exécutifs et produit les rapports multi-formats (PDF, DOCX, XLSX, PPTX)."

    @property
    def capabilities(self) -> List[str]:
        return ["rapport", "synthèse", "bilan", "pdf", "excel", "docx", "pptx", "document", "audit", "direction"]

    def can_handle(self, task: AgentTask) -> float:
        return _match_keywords(task.query, self.capabilities)

    def process(self, task: AgentTask, blackboard: SharedAgentBlackboard) -> AgentResult:
        return AgentResult(
            agent_type=self.agent_type,
            agent_name=self.name,
            data={"available_formats": ["PDF", "DOCX", "XLSX", "PPTX"], "status": "READY"},
            insights=["Synthèse des indicateurs énergétiques prête pour compilation documentaire."],
            recommendations=["Générer le rapport PDF mensuel pour la direction générale."],
            confidence_score=0.99,
        )


# =====================================================================
# 7. Cost Saving Agent
# =====================================================================

class CostSavingAgent(BaseAgent):
    """Agent d'optimisation financière et d'audit des factures CIE (FCFA)."""

    @property
    def agent_type(self) -> AgentType:
        return AgentType.COST_SAVING

    @property
    def name(self) -> str:
        return "Financial Cost Saving Agent"

    @property
    def description(self) -> str:
        return "Analyse la tarification électrique CIE, traque les économies réalisées en FCFA et calcule le ROI des actions."

    @property
    def capabilities(self) -> List[str]:
        return ["coût", "facture", "fcfa", "prix", "tarif", "cie", "roi", "argent", "dépense", "économies"]

    def can_handle(self, task: AgentTask) -> float:
        return _match_keywords(task.query, self.capabilities)

    def process(self, task: AgentTask, blackboard: SharedAgentBlackboard) -> AgentResult:
        return AgentResult(
            agent_type=self.agent_type,
            agent_name=self.name,
            data={"monthly_bill_fcfa": 4250000.0, "total_savings_fcfa": 680000.0, "currency": "FCFA"},
            insights=["Facture prévisionnelle optimisée grâce à la réduction de 28% de la pointe CIE."],
            recommendations=["Conserver la consigne de préchauffage en heures creuses (55 FCFA/kWh)."],
            confidence_score=0.97,
        )


# =====================================================================
# 8. Carbon Agent
# =====================================================================

class CarbonAgent(BaseAgent):
    """Agent de calcul d'empreinte carbone et de conformité environnementale (ESG)."""

    @property
    def agent_type(self) -> AgentType:
        return AgentType.CARBON

    @property
    def name(self) -> str:
        return "Carbon & ESG Agent"

    @property
    def description(self) -> str:
        return "Quantifie les émissions de gaz à effet de serre (kg CO2) et suit la trajectoire de décarbonation du site."

    @property
    def capabilities(self) -> List[str]:
        return ["carbone", "co2", "climat", "esg", "émissions", "écologie", "décarbonation", "vert", "environnement"]

    def can_handle(self, task: AgentTask) -> float:
        return _match_keywords(task.query, self.capabilities)

    def process(self, task: AgentTask, blackboard: SharedAgentBlackboard) -> AgentResult:
        co2_kg = 480.0
        return AgentResult(
            agent_type=self.agent_type,
            agent_name=self.name,
            data={"emissions_kg_co2": co2_kg, "factor_g_co2_kwh": 223.0, "status": "ON_TRACK"},
            insights=[f"Émissions journalières estimées à {co2_kg} kg de CO2 (mix électrique ouest-africain)."],
            recommendations=["Intégrer les ratios d'émissions évités dans le rapport RSE trimestriel."],
            confidence_score=0.92,
        )


# =====================================================================
# 9. IoT Agent
# =====================================================================

class IoTAgent(BaseAgent):
    """Agent de gestion des passerelles, capteurs et flux de télémétrie (MQTT/LoRaWAN)."""

    @property
    def agent_type(self) -> AgentType:
        return AgentType.IOT

    @property
    def name(self) -> str:
        return "IoT Telemetry & Gateway Agent"

    @property
    def description(self) -> str:
        return "Surveille la connectivité des capteurs, la qualité des signaux LoRaWAN et la fraîcheur des données MQTT."

    @property
    def capabilities(self) -> List[str]:
        return ["iot", "capteur", "passerelle", "lorawan", "mqtt", "connectivité", "signal", "batterie", "télémétrie", "onde"]

    def can_handle(self, task: AgentTask) -> float:
        return _match_keywords(task.query, self.capabilities)

    def process(self, task: AgentTask, blackboard: SharedAgentBlackboard) -> AgentResult:
        return AgentResult(
            agent_type=self.agent_type,
            agent_name=self.name,
            data={"active_gateways": 2, "connected_sensors": 18, "packet_loss_pct": 0.2},
            insights=["Passerelle Spark-4G et tous les capteurs LoRaWAN sont 100% opérationnels."],
            recommendations=["Aucune action requise sur l'infrastructure IoT."],
            confidence_score=0.99,
        )


# =====================================================================
# 10. Administrator Agent
# =====================================================================

class AdministratorAgent(BaseAgent):
    """Agent de gouvernance, sécurité, gestion des accès et coordination générale."""

    @property
    def agent_type(self) -> AgentType:
        return AgentType.ADMINISTRATOR

    @property
    def name(self) -> str:
        return "System Governance & Admin Agent"

    @property
    def description(self) -> str:
        return "Supervise les politiques de sécurité, les accès utilisateurs, les journaux d'audit et la santé des agents."

    @property
    def capabilities(self) -> List[str]:
        return ["admin", "sécurité", "droit", "rôle", "audit", "utilisateur", "accès", "gouvernance", "système", "santé"]

    def can_handle(self, task: AgentTask) -> float:
        return _match_keywords(task.query, self.capabilities)

    def process(self, task: AgentTask, blackboard: SharedAgentBlackboard) -> AgentResult:
        return AgentResult(
            agent_type=self.agent_type,
            agent_name=self.name,
            data={"system_status": "HEALTHY", "agents_registered": 10, "active_sessions": 3},
            insights=["Tous les sous-systèmes IA et agents experts fonctionnent dans les paramètres nominaux."],
            recommendations=["Effectuer la rotation programmée des clés d'accès API."],
            confidence_score=1.0,
        )
