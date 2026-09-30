"""Adaptateur local écrivant les notifications dans le journal applicatif."""

import logging

from app.application.ports.notification_service import NotificationService

logger = logging.getLogger("nouankany.notifications")


class ConsoleNotificationAdapter(NotificationService):
    """Émet une notification dans la sortie configurée du logger."""

    async def notify(self, recipient: str, message: str) -> None:
        """Journalise le destinataire et le message sans accéder à un service externe."""
        logger.info("Notification destinataire=%s message=%s", recipient, message)
