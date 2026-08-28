"""
app/ml/audit.py — Journalisation d'audit pour la traçabilité des inférences IA.

Consigne de manière immuable et structurée chaque inférence (UUID, timestamp UTC,
modèle, empreinte des entrées, sortie métier, latence, statut d'exécution).
"""

from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import threading
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger("nouankany.ml")


class AuditRecord(BaseModel):
    """
    Entrée d'audit immuable consignant une transaction d'inférence complète.
    """

    model_config = ConfigDict(frozen=True)

    audit_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Identifiant unique de l'enregistrement d'audit",
    )
    request_id: str = Field(
        ..., description="Identifiant unique universel (UUID) de la requête métier"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Horodatage UTC précis de l'opération",
    )
    operation: str = Field(
        ..., description="Nature de l'opération (ex: forecasting, anomaly_detection, health_check)"
    )
    model_name: str = Field(
        ..., description="Nom du modèle ayant traité la transaction"
    )
    model_version: str = Field(
        ..., description="Version du modèle utilisé"
    )
    input_hash: Optional[str] = Field(
        default=None, description="Empreinte SHA-256 des données d'entrée"
    )
    input_summary: Dict[str, Any] = Field(
        default_factory=dict, description="Aperçu ou synthèse des caractéristiques d'entrée"
    )
    output_summary: Dict[str, Any] = Field(
        default_factory=dict, description="Résultat métier produit par l'inférence"
    )
    execution_time_ms: float = Field(
        ..., description="Temps total d'exécution en millisecondes"
    )
    status: str = Field(
        ..., description="Statut de l'opération (SUCCESS, ERROR, VALIDATION_FAILED)"
    )
    error_message: Optional[str] = Field(
        default=None, description="Détail de l'erreur en cas d'échec"
    )


class AuditLogger:
    """
    Gestionnaire de journalisation d'audit pour le sous-système ML.
    Conserve les enregistrements en mémoire tampon circulaire et permet la persistance
    optionnelle dans un fichier JSON Lines.
    """

    def __init__(
        self,
        max_buffer_size: int = 2000,
        log_file_path: Optional[Path | str] = None,
    ) -> None:
        """
        Initialise le journal d'audit.

        :param max_buffer_size: Capacité maximale du tampon mémoire.
        :param log_file_path: Chemin du fichier JSONL d'audit optionnel.
        """
        self._max_buffer_size = max_buffer_size
        self._records: List[AuditRecord] = []
        self._lock = threading.RLock()
        self._log_file_path = Path(log_file_path) if log_file_path else None

        if self._log_file_path:
            try:
                self._log_file_path.parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.warning(
                    f"[AuditLogger] Impossible de préparer le répertoire de log : {e}"
                )

        logger.debug(
            f"[AuditLogger] Initialisé (max_buffer_size={max_buffer_size}, log_file={self._log_file_path})"
        )

    def log_inference(
        self,
        request_id: str,
        operation: str,
        model_name: str,
        model_version: str,
        execution_time_ms: float,
        input_summary: Dict[str, Any],
        output_summary: Dict[str, Any],
        input_hash: Optional[str] = None,
        status: str = "SUCCESS",
        error_message: Optional[str] = None,
    ) -> AuditRecord:
        """
        Enregistre une transaction d'inférence dans l'audit.

        :param request_id: Identifiant de requête UUID.
        :param operation: Nature de l'opération (forecasting, anomaly_detection).
        :param model_name: Nom du modèle.
        :param model_version: Version du modèle.
        :param execution_time_ms: Durée d'inférence en millisecondes.
        :param input_summary: Synthèse des entrées.
        :param output_summary: Synthèse des sorties.
        :param input_hash: Hash SHA-256 des données.
        :param status: SUCCESS, ERROR, ou VALIDATION_FAILED.
        :param error_message: Message d'erreur éventuel.
        :return: Instance `AuditRecord` créée.
        """
        record = AuditRecord(
            request_id=request_id,
            timestamp=datetime.now(timezone.utc),
            operation=operation,
            model_name=model_name,
            model_version=model_version,
            input_hash=input_hash,
            input_summary=input_summary,
            output_summary=output_summary,
            execution_time_ms=round(execution_time_ms, 3),
            status=status,
            error_message=error_message,
        )

        with self._lock:
            self._records.append(record)
            if len(self._records) > self._max_buffer_size:
                self._records.pop(0)

        # Écriture asynchrone / append dans le fichier d'audit si configuré
        if self._log_file_path:
            try:
                with open(self._log_file_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(record.model_dump(mode="json")) + "\n")
            except Exception as e:
                logger.debug(f"[AuditLogger] Erreur lors de l'écriture disque de l'audit: {e}")

        logger.debug(
            f"[AuditLogger] [audit_id={record.audit_id}] Enregistré: {operation} sur {model_name} "
            f"(status={status}, {record.execution_time_ms}ms)"
        )
        return record

    def get_records(
        self,
        limit: int = 50,
        model_name: Optional[str] = None,
        status: Optional[str] = None,
        operation: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> List[AuditRecord]:
        """
        Interroge et filtre les enregistrements d'audit récents.

        :param limit: Nombre maximum d'enregistrements retournés.
        :param model_name: Filtre optionnel par modèle.
        :param status: Filtre optionnel par statut (SUCCESS, ERROR).
        :param operation: Filtre optionnel par opération.
        :param request_id: Filtre optionnel par UUID de requête.
        :return: Liste ordonnée chronologiquement inversée (plus récents en tête).
        """
        with self._lock:
            filtered = self._records
            if model_name:
                filtered = [r for r in filtered if r.model_name == model_name]
            if status:
                filtered = [r for r in filtered if r.status == status]
            if operation:
                filtered = [r for r in filtered if r.operation == operation]
            if request_id:
                filtered = [r for r in filtered if r.request_id == request_id]

            return list(reversed(filtered[-limit:]))

    def get_summary(self) -> Dict[str, Any]:
        """
        Génère une synthèse agrégée de l'ensemble des enregistrements présents dans le tampon.

        :return: Dictionnaire des statistiques d'audit.
        """
        with self._lock:
            total = len(self._records)
            if total == 0:
                return {
                    "total_audited_transactions": 0,
                    "by_status": {},
                    "by_operation": {},
                    "by_model": {},
                    "avg_latency_ms": 0.0,
                }

            by_status: Dict[str, int] = {}
            by_operation: Dict[str, int] = {}
            by_model: Dict[str, int] = {}
            total_lat = 0.0

            for r in self._records:
                by_status[r.status] = by_status.get(r.status, 0) + 1
                by_operation[r.operation] = by_operation.get(r.operation, 0) + 1
                by_model[r.model_name] = by_model.get(r.model_name, 0) + 1
                total_lat += r.execution_time_ms

            return {
                "total_audited_transactions": total,
                "by_status": by_status,
                "by_operation": by_operation,
                "by_model": by_model,
                "avg_latency_ms": round(total_lat / total, 2),
            }

    def clear(self) -> None:
        """
        Réinitialise le tampon d'audit mémoire.
        """
        with self._lock:
            self._records.clear()
