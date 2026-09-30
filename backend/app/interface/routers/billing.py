"""Compatibilité d'import vers le routeur de facturation de Presentation."""

from app.presentation.api.v1.routes.billing import get_billing, router

__all__ = ["get_billing", "router"]
