"""Adaptateurs de notification externes et de développement."""

from app.infrastructure.notifications.console_adapter import ConsoleNotificationAdapter
from app.infrastructure.notifications.whatsapp_adapter import WhatsAppNotificationAdapter

__all__ = ["ConsoleNotificationAdapter", "WhatsAppNotificationAdapter"]
