"""Compatibilité d'import vers le routeur de recommandations de Presentation."""

from app.presentation.api.v1.routes.recommendations import get_recommendations, router

__all__ = ["get_recommendations", "router"]
