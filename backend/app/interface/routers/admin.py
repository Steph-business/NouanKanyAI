"""Compatibilité d'import vers le routeur administrateur de Presentation."""

from app.presentation.api.v1.routes.admin import admin_health, router

__all__ = ["admin_health", "router"]
