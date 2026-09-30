"""Port abstrait de notification des événements opérationnels."""

from abc import ABC, abstractmethod


class NotificationService(ABC):
    """Contrat indépendant du canal de notification choisi."""

    @abstractmethod
    async def notify(self, recipient: str, message: str) -> None:
        """Envoie un message à un destinataire métier."""
        raise NotImplementedError
