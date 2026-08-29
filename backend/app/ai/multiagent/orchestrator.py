"""
app/ai/multiagent/orchestrator.py — Orchestrateur central multi-agents de NouanKanyAI.

Rapproche, route et coordonne les 10 agents IA spécialisés à travers le tableau partagé (Blackboard),
exécute les tâches en mode séquentiel, parallèle ou consensus, et synthétise les résultats.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import time
from typing import Any, Dict, List, Optional, Union

from app.ai.multiagent.base import BaseAgent
from app.ai.multiagent.blackboard import SharedAgentBlackboard
from app.ai.multiagent.models import (
    AgentResult,
    AgentTask,
    AgentType,
    ExecutionMode,
    OrchestratorResponse,
)
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

logger = logging.getLogger("nouankany.multiagent")


class MultiAgentOrchestrator:
    """
    Orchestrateur central responsable du routage des tâches, de la synchronisation
    du contexte partagé et de la fusion des résultats multi-experts.
    """

    def __init__(self, blackboard: Optional[SharedAgentBlackboard] = None) -> None:
        self.blackboard = blackboard or SharedAgentBlackboard()
        self._agents: Dict[AgentType, BaseAgent] = {}
        logger.debug("[MultiAgentOrchestrator] Orchestrateur multi-agents initialisé.")

    def register_agent(self, agent: BaseAgent) -> None:
        """Enregistre un agent spécialisé dans le pool d'orchestration."""
        self._agents[agent.agent_type] = agent
        logger.info(f"[MultiAgentOrchestrator] Agent enregistré : '{agent.name}' ({agent.agent_type.value})")

    def get_agent(self, agent_type: Union[AgentType, str]) -> Optional[BaseAgent]:
        """Récupère un agent par son type énuméré ou sa clé textuelle."""
        key = agent_type if isinstance(agent_type, AgentType) else AgentType(str(agent_type).lower())
        return self._agents.get(key)

    def list_agents(self) -> List[BaseAgent]:
        """Retourne la liste de tous les agents enregistrés."""
        return list(self._agents.values())

    def route_task(self, task: AgentTask, min_score_threshold: float = 0.20) -> List[BaseAgent]:
        """
        Détermine intelligemment les agents les plus qualifiés pour traiter une tâche.

        :param task: Tâche soumise.
        :param min_score_threshold: Seuil minimal de pertinence pour retenir un agent.
        :return: Liste ordonnée des agents sélectionnés.
        """
        # 1. Si des agents cibles sont explicitement désignés dans la tâche
        if task.target_agents:
            selected = []
            for at in task.target_agents:
                agent = self.get_agent(at)
                if agent:
                    selected.append(agent)
            if selected:
                return selected

        # 2. Routage sémantique par évaluation d'adéquation (can_handle)
        scored_agents: List[tuple[BaseAgent, float]] = []
        for agent in self._agents.values():
            score = agent.can_handle(task)
            if score >= min_score_threshold:
                scored_agents.append((agent, score))

        # Tri décroissant par score de pertinence
        scored_agents.sort(key=lambda x: x[1], reverse=True)

        # Si aucun agent ne dépasse le seuil, assigner l'EnergyAgent ou l'AdministratorAgent par défaut
        if not scored_agents:
            fallback = self.get_agent(AgentType.ENERGY) or self.get_agent(AgentType.ADMINISTRATOR)
            return [fallback] if fallback else list(self._agents.values())[:1]

        return [agent for agent, _ in scored_agents]

    def execute_task(self, task: AgentTask) -> OrchestratorResponse:
        """
        Orchestre l'exécution de la tâche selon le mode défini (Single, Sequential, Parallel, Consensus).

        :param task: Tâche à exécuter.
        :return: Réponse unifiée `OrchestratorResponse`.
        """
        start_time = time.perf_counter()
        selected_agents = self.route_task(task)
        logger.info(
            f"[MultiAgentOrchestrator] Tâche '{task.task_id}' routée vers {len(selected_agents)} agent(s) "
            f"en mode {task.execution_mode.value.upper()}."
        )

        # Injection du contexte initial dans le tableau partagé
        for k, v in task.context_data.items():
            self.blackboard.set_value(k, v)

        agent_results: Dict[str, AgentResult] = {}

        # 1. Mode SÉQUENTIEL (Pipeline en cascade)
        if task.execution_mode == ExecutionMode.SEQUENTIAL_PIPELINE:
            for agent in selected_agents:
                res = agent.run(task=task, blackboard=self.blackboard)
                agent_results[agent.agent_type.value] = res
                if not res.success:
                    logger.warning(f"[MultiAgentOrchestrator] Arrêt de séquence : l'agent '{agent.name}' a échoué.")
                    break

        # 2. Mode PARALLÈLE ou CONSENSUS (Fan-Out simultané)
        else:
            with ThreadPoolExecutor(max_workers=min(len(selected_agents), 8)) as executor:
                future_to_agent = {
                    executor.submit(agent.run, task, self.blackboard): agent
                    for agent in selected_agents
                }
                for future in as_completed(future_to_agent):
                    agent = future_to_agent[future]
                    try:
                        res = future.result()
                        agent_results[agent.agent_type.value] = res
                    except Exception as e:
                        logger.error(f"[MultiAgentOrchestrator] Exception sur '{agent.name}' : {e}")

        # 3. Synthèse collective des résultats
        combined_summary = self._synthesize_results(task, agent_results)
        total_latency = round((time.perf_counter() - start_time) * 1000.0, 2)

        return OrchestratorResponse(
            task_id=task.task_id,
            execution_mode=task.execution_mode,
            participating_agents=[AgentType(k) for k in agent_results.keys()],
            combined_summary=combined_summary,
            agent_results=agent_results,
            total_latency_ms=total_latency,
            metadata={
                "target_count": len(selected_agents),
                "success_count": sum(1 for r in agent_results.values() if r.success),
                "timestamp": time.time(),
            },
        )

    def _synthesize_results(self, task: AgentTask, results: Dict[str, AgentResult]) -> str:
        """Génère un résumé textuel clair agrégeant les insights et recommandations des experts."""
        if not results:
            return "Aucun agent n'a pu traiter la tâche soumise."

        all_insights: List[str] = []
        all_recs: List[str] = []

        for res in results.values():
            if res.success:
                all_insights.extend(res.insights)
                all_recs.extend(res.recommendations)

        summary_lines = [
            f"### 🤝 Diagnostic Multi-Agents pour la mission : « {task.query} »\n",
            "**Observations des Agents Experts :**",
        ]
        for ins in all_insights:
            summary_lines.append(f"- {ins}")

        if all_recs:
            summary_lines.append("\n**Plan d'Action Collectif :**")
            for rec in all_recs:
                summary_lines.append(f"• {rec}")

        return "\n".join(summary_lines)

    @classmethod
    def create_default_orchestrator(cls) -> "MultiAgentOrchestrator":
        """
        Instancie et initialise un orchestrateur complet pré-configuré avec les 10 agents spécialisés.
        """
        orch = cls()
        orch.register_agent(EnergyAgent())
        orch.register_agent(ForecastAgent())
        orch.register_agent(AnomalyAgent())
        orch.register_agent(MaintenanceAgent())
        orch.register_agent(OptimizationAgent())
        orch.register_agent(ReportingAgent())
        orch.register_agent(CostSavingAgent())
        orch.register_agent(CarbonAgent())
        orch.register_agent(IoTAgent())
        orch.register_agent(AdministratorAgent())
        return orch
