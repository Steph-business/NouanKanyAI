"""Compatibilité d'import vers le routeur machines de Presentation."""

from app.presentation.api.v1.routes.machines import list_machines, router

__all__ = ["list_machines", "router"]
