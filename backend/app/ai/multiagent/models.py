"""
app/ai/multiagent/models.py — Modèles Pydantic v2 pour l'architecture Multi-Agents.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class AgentType(str, Enum):
    """Types d'agents spécialisés dans NouanKanyAI."""

    ENERGY = "energy_agent"
    FORECAST = "forecast_agent"
    ANOMALY = "anomaly_agent"
    MAINTENANCE = "maintenance_agent"
    OPTIMIZATION = "optimization_agent"
    REPORTING = "reporting_agent"
    COST_SAVING = "cost_saving_agent"
    CARBON = "carbon_agent"
    IOT = "iot_agent"
    ADMINISTRATOR = "administrator_agent"


class ExecutionMode(str, Enum):
    """Modes d'exécution et de coordination des agents."""

    SINGLE = "single"                    # Un seul agent ciblé
    SEQUENTIAL_PIPELINE = "sequential"  # Exécution en cascade (l'agent N enrichit les données pour N+1)
    PARALLEL_FANOUT = "parallel"        # Exécution simultanée des agents avec agrégation
    CONSENSUS_SYNTHESIS = "consensus"   # Consultation multi-experts avec arbitrage synthétisé


class TaskPriority(str, Enum):
    """Niveau de priorité d'une tâche multi-agents."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class AgentTask(BaseModel):
    """Tâche ou mission soumise à l'orchestrateur multi-agents."""

    model_config = ConfigDict(extra="allow")

    task_id: str = Field(default_factory=lambda: f"TASK-{uuid.uuid4().hex[:8].upper()}")
    query: str = Field(..., description="Requête ou instruction initiale de l'utilisateur/système")
    target_agents: Optional[List[AgentType]] = Field(
        default=None, description="Agents cibles explicites (si omis, routage dynamique)"
    )
    execution_mode: ExecutionMode = Field(
        default=ExecutionMode.CONSENSUS_SYNTHESIS, description="Mode de coordination"
    )
    priority: TaskPriority = Field(default=TaskPriority.NORMAL, description="Niveau d'urgence")
    context_data: Dict[str, Any] = Field(default_factory=dict, description="Données contextuelles partagées")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AgentResult(BaseModel):
    """Résultat individuel produit par un agent spécialisé."""

    model_config = ConfigDict(frozen=True)

    agent_type: AgentType = Field(..., description="Type de l'agent émetteur")
    agent_name: str = Field(..., description="Nom lisible de l'agent")
    success: bool = Field(default=True, description="Indique si la tâche a réussi")
    data: Dict[str, Any] = Field(default_factory=dict, description="Données brutes produites")
    insights: List[str] = Field(default_factory=list, description="Observations clés et diagnostics")
    recommendations: List[str] = Field(default_factory=list, description="Recommandations d'action")
    confidence_score: float = Field(default=1.0, description="Niveau de confiance (0.0 à 1.0)")
    latency_ms: float = Field(default=0.0, description="Durée de traitement en millisecondes")
    error: Optional[str] = Field(default=None, description="Message d'erreur en cas d'échec")


class OrchestratorResponse(BaseModel):
    """Réponse consolidée fusionnée par l'orchestrateur multi-agents."""

    model_config = ConfigDict(frozen=True)

    task_id: str = Field(..., description="Identifiant de la tâche traitée")
    execution_mode: ExecutionMode = Field(..., description="Mode de coordination utilisé")
    participating_agents: List[AgentType] = Field(..., description="Agents ayant contribué")
    combined_summary: str = Field(..., description="Synthèse unifiée pour l'utilisateur")
    agent_results: Dict[str, AgentResult] = Field(
        default_factory=dict, description="Détail des résultats par agent"
    )
    total_latency_ms: float = Field(default=0.0, description="Latence totale de l'orchestration")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Métadonnées d'exécution")
