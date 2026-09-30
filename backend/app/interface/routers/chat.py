"""Compatibilité d'import vers le routeur Copilot de Presentation."""

from app.presentation.api.v1.routes.copilot import ChatRequest, chat, router

__all__ = ["ChatRequest", "chat", "router"]
