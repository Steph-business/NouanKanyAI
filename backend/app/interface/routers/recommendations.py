"""
app/interface/routers/recommendations.py — Routeur FastAPI pour les recommandations d'efficacité énergétique.

Expose la liste des actions générées pour optimiser les plannings et éviter les surconsommations.
"""

from typing import Any, Dict
from fastapi import APIRouter

router = APIRouter()


@router.get(
    "/recommendations",
    summary="Liste des recommandations d'optimisation",
    description="Retourne les conseils et actions correctives prioritaires pour les équipements.",
)
def get_recommendations() -> Dict[str, Any]:
    """
    Fournit la liste des actions d'efficacité énergétique recommandées.
    """
    return {
        "recommendations": [
            "Vérifier la pression de la pompe hydraulique",
            "Optimiser la programmation de la climatisation",
        ],
        "count": 2,
    }
