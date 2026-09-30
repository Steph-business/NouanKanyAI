"""Compatibilité d'import vers le routeur ML désormais situé dans Presentation."""

from app.presentation.api.v1.routes.ml import router

__all__ = ["router"]
