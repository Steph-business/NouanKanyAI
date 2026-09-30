"""Endpoint de santé HTTP léger pour le serveur d'API."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["Santé"])
def health() -> dict[str, str]:
    """Confirme la disponibilité de la couche HTTP."""
    return {"status": "ok"}
