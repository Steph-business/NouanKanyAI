"""
app/ai/multiagent/blackboard.py — Espace de travail partagé (Blackboard Pattern) pour la collaboration inter-agents.
"""

from collections import defaultdict
from datetime import datetime, timezone
import logging
import threading
from typing import Any, Dict, List, Optional

from app.ai.multiagent.models import AgentType

logger = logging.getLogger("nouankany.multiagent")


class SharedAgentBlackboard:
    """
    Tableau partagé thread-safe permettant aux agents d'échanger des faits,
    des métriques de télémétrie, des alertes et des états intermédiaires au cours d'une mission.
    """

    def __init__(self, initial_state: Optional[Dict[str, Any]] = None) -> None:
        self._state: Dict[str, Any] = dict(initial_state or {})
        self._event_log: List[Dict[str, Any]] = []
        self._agent_outputs: Dict[str, Any] = {}
        self._lock = threading.RLock()
        logger.debug("[SharedAgentBlackboard] Tableau partagé initialisé.")

    def set_value(self, key: str, value: Any, author: Optional[AgentType] = None) -> None:
        """Enregistre ou met à jour une information dans l'espace partagé."""
        with self._lock:
            self._state[key] = value
            self._event_log.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": "SET",
                "key": key,
                "author": author.value if author else "system",
            })

    def get_value(self, key: str, default: Any = None) -> Any:
        """Récupère une valeur de l'espace partagé."""
        with self._lock:
            return self._state.get(key, default)

    def set_agent_output(self, agent_type: AgentType, output_data: Any) -> None:
        """Stocke la contribution finale d'un agent spécifique."""
        with self._lock:
            self._agent_outputs[agent_type.value] = output_data

    def get_agent_output(self, agent_type: AgentType, default: Any = None) -> Any:
        """Consulte la contribution d'un agent tiers."""
        with self._lock:
            return self._agent_outputs.get(agent_type.value, default)

    def get_all_outputs(self) -> Dict[str, Any]:
        """Retourne l'ensemble des résultats inter-agents."""
        with self._lock:
            return dict(self._agent_outputs)

    def get_snapshot(self) -> Dict[str, Any]:
        """Exporte un instantané complet de l'état du tableau partagé."""
        with self._lock:
            return {
                "state": dict(self._state),
                "agent_outputs": dict(self._agent_outputs),
                "event_count": len(self._event_log),
            }

    def clear(self) -> None:
        """Réinitialise le tableau partagé."""
        with self._lock:
            self._state.clear()
            self._event_log.clear()
            self._agent_outputs.clear()
