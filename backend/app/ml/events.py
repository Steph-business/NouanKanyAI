"""
app/ml/events.py — Système d'événements internes de la couche Machine Learning.

Définit les types d'événements, la structure des payloads d'événements et
un bus d'événements (MLEventDispatcher) découplé et thread-safe.
"""

from datetime import datetime, timezone
from enum import Enum
import logging
import threading
from typing import Any, Callable, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger("nouankany.ml")


class MLEventType(str, Enum):
    """
    Types d'événements internes émis par le sous-système ML.
    """

    MODEL_LOADED = "model.loaded"
    MODEL_RELOADED = "model.reloaded"
    MODEL_LOAD_FAILED = "model.load_failed"
    PREDICTION_REQUESTED = "prediction.requested"
    PREDICTION_SUCCESS = "prediction.success"
    PREDICTION_ERROR = "prediction.error"
    ANOMALY_DETECTED = "anomaly.detected"
    ANOMALY_CHECK_NORMAL = "anomaly.normal"
    VALIDATION_ERROR = "validation.error"
    HEALTH_CHECKED = "health.checked"
    HEALTH_DEGRADED = "health.degraded"


class MLEvent(BaseModel):
    """
    Structure immuable représentant un événement ML interne.
    """

    model_config = ConfigDict(frozen=True)

    event_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Identifiant unique de l'événement (UUID)",
    )
    event_type: MLEventType = Field(
        ..., description="Type canonique de l'événement"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Horodatage UTC précis de l'émission",
    )
    request_id: Optional[str] = Field(
        default=None, description="Identifiant unique de la requête associée si applicable"
    )
    model_name: Optional[str] = Field(
        default=None, description="Nom du modèle concerné"
    )
    model_version: Optional[str] = Field(
        default=None, description="Version du modèle concerné"
    )
    payload: Dict[str, Any] = Field(
        default_factory=dict, description="Données contextuelles associées à l'événement"
    )
    level: str = Field(
        default="INFO", description="Niveau de gravité (DEBUG, INFO, WARNING, ERROR)"
    )


EventHandler = Callable[[MLEvent], None]


class MLEventDispatcher:
    """
    Bus d'événements interne pour la couche ML.
    Permet la publication d'événements, l'enregistrement d'écouteurs (subscribers)
    et la conservation d'un tampon historique en mémoire.
    """

    def __init__(self, max_history: int = 1000) -> None:
        """
        Initialise le gestionnaire d'événements.

        :param max_history: Nombre maximal d'événements conservés en mémoire.
        """
        self._max_history = max_history
        self._history: List[MLEvent] = []
        self._handlers: Dict[MLEventType, List[EventHandler]] = {}
        self._global_handlers: List[EventHandler] = []
        self._lock = threading.RLock()

        logger.debug("[MLEventDispatcher] Bus d'événements ML initialisé.")

    def subscribe(
        self, event_type: Optional[MLEventType], handler: EventHandler
    ) -> None:
        """
        Abonne une fonction de rappel à un type d'événement (ou à tous si event_type is None).

        :param event_type: Type d'événement cible ou None pour écouter tous les événements.
        :param handler: Fonction recevant l'instance `MLEvent`.
        """
        with self._lock:
            if event_type is None:
                self._global_handlers.append(handler)
            else:
                if event_type not in self._handlers:
                    self._handlers[event_type] = []
                self._handlers[event_type].append(handler)

    def dispatch(
        self,
        event_type: MLEventType,
        payload: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        model_name: Optional[str] = None,
        model_version: Optional[str] = None,
        level: str = "INFO",
    ) -> MLEvent:
        """
        Crée, journalise, archive et notifie un événement ML.

        :param event_type: Type de l'événement.
        :param payload: Dictionnaire de données associées.
        :param request_id: Identifiant de requête corrélé.
        :param model_name: Nom du modèle.
        :param model_version: Version du modèle.
        :param level: Niveau de log.
        :return: L'instance `MLEvent` générée.
        """
        event = MLEvent(
            event_type=event_type,
            timestamp=datetime.now(timezone.utc),
            request_id=request_id,
            model_name=model_name,
            model_version=model_version,
            payload=payload or {},
            level=level,
        )

        with self._lock:
            self._history.append(event)
            if len(self._history) > self._max_history:
                self._history.pop(0)

            # Liste des gestionnaires à exécuter
            target_handlers = self._handlers.get(event_type, []).copy()
            globals_to_call = self._global_handlers.copy()

        # Journalisation via le logger nouankany.ml
        log_msg = f"[Event:{event_type.value}] [req_id={request_id or 'N/A'}] {event.payload}"
        if level == "DEBUG":
            logger.debug(log_msg)
        elif level == "WARNING":
            logger.warning(log_msg)
        elif level == "ERROR":
            logger.error(log_msg)
        else:
            logger.info(log_msg)

        # Exécution des écouteurs hors verrou
        for h in target_handlers + globals_to_call:
            try:
                h(event)
            except Exception as e:
                logger.error(f"[MLEventDispatcher] Échec de l'écouteur d'événement : {e}")

        return event

    def get_recent_events(
        self,
        limit: int = 50,
        event_type: Optional[MLEventType] = None,
        request_id: Optional[str] = None,
    ) -> List[MLEvent]:
        """
        Récupère les événements récents filtrés.

        :param limit: Nombre maximal d'événements retournés.
        :param event_type: Filtre optionnel sur le type d'événement.
        :param request_id: Filtre optionnel sur l'identifiant de requête.
        :return: Liste chronologique inversée (les plus récents d'abord).
        """
        with self._lock:
            filtered = self._history
            if event_type is not None:
                filtered = [e for e in filtered if e.event_type == event_type]
            if request_id is not None:
                filtered = [e for e in filtered if e.request_id == request_id]

            return list(reversed(filtered[-limit:]))

    def clear(self) -> None:
        """
        Efface l'historique des événements en mémoire.
        """
        with self._lock:
            self._history.clear()
