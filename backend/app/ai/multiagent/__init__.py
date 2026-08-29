"""
app/ai/multiagent — Architecture Multi-Agents et Orchestrateur Central de NouanKanyAI.

Fournit l'infrastructure d'orchestration, le bus d'échange partagé (Blackboard) et les abstractions
des 10 agents IA spécialisés pour l'efficacité énergétique, la prévision, la maintenance et l'optimisation.
"""

from app.ai.multiagent.base import BaseAgent
from app.ai.multiagent.blackboard import SharedAgentBlackboard
from app.ai.multiagent.models import (
    AgentResult,
    AgentTask,
    AgentType,
    ExecutionMode,
    OrchestratorResponse,
    TaskPriority,
)
from app.ai.multiagent.orchestrator import MultiAgentOrchestrator
from app.ai.multiagent.specialized import (
    AdministratorAgent,
    AnomalyAgent,
    CarbonAgent,
    CostSavingAgent,
    EnergyAgent,
    ForecastAgent,
    IoTAgent,
    MaintenanceAgent,
    OptimizationAgent,
    ReportingAgent,
)

__all__ = [
    # Modèles
    "AgentType",
    "ExecutionMode",
    "TaskPriority",
    "AgentTask",
    "AgentResult",
    "OrchestratorResponse",
    # Abstraction et Blackboard
    "BaseAgent",
    "SharedAgentBlackboard",
    # Orchestrateur Central
    "MultiAgentOrchestrator",
    # Les 10 Agents Spécialisés
    "EnergyAgent",
    "ForecastAgent",
    "AnomalyAgent",
    "MaintenanceAgent",
    "OptimizationAgent",
    "ReportingAgent",
    "CostSavingAgent",
    "CarbonAgent",
    "IoTAgent",
    "AdministratorAgent",
]
