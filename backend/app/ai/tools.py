"""
app/ai/tools.py — Registre d'outils et interface de Function Calling pour les agents IA.

Permet au modèle Gemini d'invoquer des fonctions métier déterministes (lecture de télémétrie,
calculs financiers précis, simulation de délestage) de manière sécurisée et typée.
"""

from abc import ABC, abstractmethod
import logging
from typing import Any, Callable, Dict, List, Optional
from app.ai.exceptions import ToolExecutionError
from app.ai.types import ToolDefinition

logger = logging.getLogger("nouankany.ai")


class BaseTool(ABC):
    """
    Classe de base abstraite pour tous les outils métier invocables par le LLM.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Nom technique unique de l'outil."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description détaillée de la fonction pour le modèle."""
        pass

    @property
    @abstractmethod
    def parameters_schema(self) -> Dict[str, Any]:
        """Schéma JSON des paramètres acceptés."""
        pass

    @abstractmethod
    def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Exécute la logique métier de l'outil.

        :param kwargs: Arguments transmis par le modèle.
        :return: Dictionnaire des résultats sérialisables en JSON.
        """
        pass

    def to_definition(self) -> ToolDefinition:
        """Exporte l'outil au format standard `ToolDefinition`."""
        return ToolDefinition(
            name=self.name,
            description=self.description,
            parameters_schema=self.parameters_schema,
        )

    def to_gemini_schema(self) -> Dict[str, Any]:
        """Exporte l'outil au format attendu par Google Gemini Function Calling."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters_schema,
        }


class ToolRegistry:
    """
    Registre centralisé des outils métier disponibles pour l'AI Gateway.
    """

    def __init__(self) -> None:
        self._tools: Dict[str, BaseTool] = {}
        logger.debug("[ToolRegistry] Registre d'outils initialisé.")

    def register(self, tool: BaseTool) -> None:
        """
        Enregistre un nouvel outil dans le registre.

        :param tool: Instance de `BaseTool`.
        """
        self._tools[tool.name] = tool
        logger.info(f"[ToolRegistry] Outil enregistré : '{tool.name}'")

    def get(self, tool_name: str) -> Optional[BaseTool]:
        """Récupère un outil par son nom."""
        return self._tools.get(tool_name)

    def list_tools(self) -> List[BaseTool]:
        """Liste tous les outils enregistrés."""
        return list(self._tools.values())

    def get_gemini_schemas(self) -> List[Dict[str, Any]]:
        """Retourne la liste des déclarations de fonctions au format Gemini."""
        return [tool.to_gemini_schema() for tool in self._tools.values()]

    def execute_tool(self, tool_name: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Exécute un outil enregistré par son nom avec gestion d'erreurs.

        :param tool_name: Nom de l'outil à exécuter.
        :param kwargs: Paramètres d'appel.
        :return: Résultat de l'outil.
        """
        tool = self.get(tool_name)
        if not tool:
            raise ToolExecutionError(f"Outil '{tool_name}' non trouvé dans le registre.")

        try:
            logger.debug(f"[ToolRegistry] Exécution de l'outil '{tool_name}' avec args={kwargs}")
            return tool.execute(**kwargs)
        except Exception as e:
            logger.error(f"[ToolRegistry] Échec d'exécution de l'outil '{tool_name}' : {e}")
            raise ToolExecutionError(
                f"Erreur lors de l'exécution de l'outil '{tool_name}' : {str(e)}",
                details={"tool_name": tool_name, "args": kwargs},
            ) from e


# =====================================================================
# Exemples d'outils métier industriels (Points d'extension)
# =====================================================================

class CalculateEnergyCostTool(BaseTool):
    """Outil de calcul déterministe du coût financier CIE en FCFA."""

    @property
    def name(self) -> str:
        return "calculate_energy_cost"

    @property
    def description(self) -> str:
        return "Calcule le coût électrique exact en FCFA selon la consommation (kWh) et l'heure (CIE)."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "energy_kwh": {
                    "type": "number",
                    "description": "Quantité d'énergie consommée en kilowatt-heures (kWh)",
                },
                "hour": {
                    "type": "integer",
                    "description": "Heure de la journée (0 à 23) pour déterminer la tranche CIE",
                },
            },
            "required": ["energy_kwh", "hour"],
        }

    def execute(self, **kwargs: Any) -> Dict[str, Any]:
        kwh = float(kwargs.get("energy_kwh", 0.0))
        hour = int(kwargs.get("hour", 12))

        # Barème CIE
        if 19 <= hour <= 23:
            tariff_name = "Heure de Pointe"
            rate = 145.0
        elif hour < 7 or hour >= 23:
            tariff_name = "Heure Creuse"
            rate = 55.0
        else:
            tariff_name = "Heure Pleine"
            rate = 85.0

        total_cost_fcfa = round(kwh * rate, 2)
        return {
            "energy_kwh": kwh,
            "hour": hour,
            "tariff_name": tariff_name,
            "unit_rate_fcfa": rate,
            "total_cost_fcfa": total_cost_fcfa,
            "currency": "FCFA",
        }
