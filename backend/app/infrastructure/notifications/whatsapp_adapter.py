"""Adaptateur WhatsApp Business Cloud API, initialisé uniquement si configuré."""

import asyncio
import json
from urllib.request import Request, urlopen

from app.application.ports.notification_service import NotificationService
from app.config.settings import settings


class WhatsAppNotificationAdapter(NotificationService):
    """Envoie un message texte via l'API Cloud WhatsApp configurée."""

    def __init__(self, token: str | None = None, phone_number_id: str | None = None) -> None:
        self.token = token if token is not None else settings.WHATSAPP_TOKEN
        self.phone_number_id = (
            phone_number_id if phone_number_id is not None else settings.WHATSAPP_PHONE_NUMBER_ID
        )
        if not self.token or not self.phone_number_id:
            raise ValueError("WHATSAPP_TOKEN et WHATSAPP_PHONE_NUMBER_ID sont requis")

    async def notify(self, recipient: str, message: str) -> None:
        """Transmet un message texte au destinataire configuré."""
        payload = json.dumps(
            {
                "messaging_product": "whatsapp",
                "to": recipient,
                "type": "text",
                "text": {"body": message},
            }
        ).encode("utf-8")
        request = Request(
            f"https://graph.facebook.com/v20.0/{self.phone_number_id}/messages",
            data=payload,
            headers={"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"},
            method="POST",
        )
        await asyncio.to_thread(self._send, request)

    @staticmethod
    def _send(request: Request) -> None:
        """Effectue la requête HTTP synchrone dans un thread."""
        with urlopen(request, timeout=15) as response:
            response.read()
