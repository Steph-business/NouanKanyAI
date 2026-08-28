"""
app/interface/routers/admin.py — Routeur FastAPI pour les statistiques administratives de base.

Expose un endpoint de contrôle global des machines actives, alertes et indicateurs d'efficacité.
"""

from typing import Any, Dict
from fastapi import APIRouter

router = APIRouter()


@router.get(
    "/admin",
    summary="État de synthèse administrateur",
    description="Retourne le nombre de machines actives, les alertes en cours et le taux d'efficacité énergétique global.",
)
def admin_health() -> Dict[str, Any]:
    """
    Fournit un résumé rapide de la santé de l'infrastructure pour le dashboard admin.
    """
    return {
        "status": "ok",
        "activeMachines": 4,
        "alerts": 1,
        "efficiency": 87.5,
    }
