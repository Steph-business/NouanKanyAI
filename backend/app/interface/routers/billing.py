"""
app/interface/routers/billing.py — Routeur FastAPI pour la synthèse de facturation et partage de gains.

Expose les données d'économies brutes, de gain-share et l'historique financier pour le dashboard.
"""

from typing import Any, Dict
from fastapi import APIRouter

router = APIRouter()


@router.get(
    "/billing",
    summary="Synthèse de facturation et économies",
    description="Retourne les économies brutes réalisées, la part de gain (Gain-Share 10%) et les données de facturation.",
)
def get_billing() -> Dict[str, Any]:
    """
    Fournit un récapitulatif des gains financiers générés par l'optimisation énergétique.
    """
    return {
        "grossSavings": 125000.0,
        "gainShare": 12500.0,
        "barData": [{"name": "W1", "savings": 18000.0}],
        "auditTrail": [],
        "invoices": [],
    }
