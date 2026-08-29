"""
app/ai/multiagent/base.py — Classe de base abstraite pour les agents spécialisés.
"""

from abc import ABC, abstractmethod
import logging
import time
from typing import Any, Dict, List, Optional

from app.ai.multiagent.blackboard import SharedAgentBlackboard
from app.ai.multiagent.models import AgentResult, AgentTask, AgentType

logger = logging.getLogger("nouankany.multiagent")


class BaseAgent(ABC):
    """
    Interface abstraite définissant le contrat de tout agent spécialisé au sein de NouanKanyAI.
    """

    @property
    @abstractmethod
    def agent_type(self) -> AgentType:
        """Type unique de l'agent."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Nom lisible de l'agent."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description du rôle et de la mission de l'agent."""
        pass

    @property
    @abstractmethod
    def capabilities(self) -> List[str]:
        """Liste des compétences techniques et mots-clés d'expertise."""
        pass

    @abstractmethod
    def can_handle(self, task: AgentTask) -> float:
        """
        Évalue l'adéquation de l'agent pour traiter une tâche donnée.

        :param task: Tâche à analyser.
        :return: Score de pertinence entre 0.0 (incompétent) et 1.0 (expert absolu).
        """
        pass

    @abstractmethod
    def process(
        self,
        task: AgentTask,
        blackboard: SharedAgentBlackboard,
    ) -> AgentResult:
        """
        Exécute la logique de traitement de l'agent en interagissant avec le tableau partagé.

        :param task: Tâche à exécuter.
        :param blackboard: Espace d'échange et de mémoire partagée.
        :return: Résultat typé `AgentResult`.
        """
        pass

    def run(
        self,
        task: AgentTask,
        blackboard: SharedAgentBlackboard,
    ) -> AgentResult:
        """
        Exécute l'agent avec mesure du temps de latence et interception sécurisée des erreurs.
        """
        start_time = time.perf_counter()
        try:
            logger.info(f"[{self.name}] Début d'exécution pour la tâche '{task.task_id}'...")
            result = self.process(task=task, blackboard=blackboard)
            latency = round((time.perf_counter() - start_time) * 1000.0, 2)

            final_result = AgentResult(
                agent_type=self.agent_type,
                agent_name=self.name,
                success=result.success,
                data=result.data,
                insights=result.insights,
                recommendations=result.recommendations,
                confidence_score=result.confidence_score,
                latency_ms=latency,
                error=result.error,
            )
            # Enregistrement automatique dans le tableau partagé
            blackboard.set_agent_output(self.agent_type, final_result.data)
            return final_result

        except Exception as e:
            latency = round((time.perf_counter() - start_time) * 1000.0, 2)
            logger.error(f"[{self.name}] Erreur lors de l'exécution : {e}")
            return AgentResult(
                agent_type=self.agent_type,
                agent_name=self.name,
                success=False,
                data={},
                insights=[],
                recommendations=[],
                confidence_score=0.0,
                latency_ms=latency,
                error=str(e),
            )
