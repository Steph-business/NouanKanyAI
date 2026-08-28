"""
app/interface/routers/machines.py — Routeur FastAPI pour la consultation des équipements industriels.

Fournit l'état courant, les puissances nominales, températures et vibrations
des machines enregistrées sur la plateforme.
"""

from typing import Any, Dict, List
from fastapi import APIRouter

from app.services.demo_data import load_demo_machine_state

router = APIRouter()


@router.get(
    "/machines",
    summary="Liste des équipements et états capteurs",
    description="Retourne l'état opérationnel et les métriques de base de tous les équipements industriels.",
)
def list_machines() -> List[Dict[str, Any]]:
    """
    Récupère l'état instantané des équipements.
    Bascule sur le jeu de données démo prédéfini pour garantir la fluidité de l'interface.
    """
    return load_demo_machine_state()
