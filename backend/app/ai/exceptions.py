"""
app/ai/exceptions.py — Hiérarchie d'exceptions typées pour la couche GenAI de NouanKanyAI.
"""

from typing import Any, Dict, Optional


class AIException(Exception):
    """
    Exception de base pour toutes les erreurs de la couche Intelligence Artificielle générative.
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class AIGatewayError(AIException):
    """
    Levée lorsqu'une communication avec l'API LLM (Gemini) échoue ou renvoie une erreur serveur.
    """

    pass


class AuthenticationError(AIException):
    """
    Levée lorsque la clé API du fournisseur LLM est absente ou invalide.
    """

    pass


class RateLimitExceededError(AIException):
    """
    Levée lorsque le quota d'appels à l'API LLM est dépassé (HTTP 429).
    """

    pass


class InvalidPromptError(AIException):
    """
    Levée lorsque le prompt ou le template fourni est invalide ou incomplet.
    """

    pass


class ToolExecutionError(AIException):
    """
    Levée lors de l'échec de l'exécution d'un outil métier appelé par l'IA.
    """

    pass


class MemoryError(AIException):
    """
    Levée lors d'un échec de persistance ou de récupération de la mémoire conversationnelle.
    """

    pass


class RAGRetrievalError(AIException):
    """
    Levée lorsqu'une erreur survient lors de la recherche documentaire vectorielle.
    """

    pass
