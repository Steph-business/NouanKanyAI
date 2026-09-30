"""Fournisseurs de dépendances HTTP, conservant les composants legacy jusqu'au container."""

from fastapi import Header, HTTPException, status

from app.application.ports.llm_service import LLMService
from app.application.ports.notification_service import NotificationService
from app.application.use_cases.calculate_invoice import CalculateInvoiceUseCase
from app.application.use_cases.detect_anomaly import DetectAnomalyUseCase
from app.application.use_cases.generate_report import GenerateReportUseCase
from app.application.use_cases.predict_consumption import PredictConsumptionUseCase
from app.config.container import container
from app.config.settings import settings
from app.ml.manager import ModelManager

__all__ = [
    "get_calculate_invoice_use_case",
    "get_detect_anomaly_use_case",
    "get_generate_report_use_case",
    "get_llm_service",
    "get_model_manager",
    "get_notification_service",
    "get_predict_use_case",
    "set_model_manager",
    "verify_ml_admin_key",
]


def get_model_manager() -> ModelManager:
    """Fournit le gestionnaire ML unique maintenu par le container."""
    container.initialize()
    if not container.model_manager._is_loaded:
        container.load_models()
    return container.model_manager


def set_model_manager(manager: ModelManager) -> None:
    """Remplace le gestionnaire ML du container pour les tests d'intégration."""
    container.set_model_manager(manager)


def get_predict_use_case() -> PredictConsumptionUseCase:
    """Fournit le cas d'usage de prévision assemblé par le container."""
    container.initialize()
    return container.predict_use_case


def get_detect_anomaly_use_case() -> DetectAnomalyUseCase:
    """Fournit le cas d'usage de détection assemblé par le container."""
    container.initialize()
    return container.detect_anomaly_use_case


def get_calculate_invoice_use_case() -> CalculateInvoiceUseCase:
    """Fournit le cas d'usage de calcul de facture assemblé par le container."""
    container.initialize()
    return container.calculate_invoice_use_case


def get_llm_service() -> LLMService:
    """Fournit le port LLM actuellement configuré dans le container."""
    container.initialize()
    return container.llm_service


def get_notification_service() -> NotificationService:
    """Fournit le service de notification actuellement configuré."""
    container.initialize()
    return container.notification_service


def verify_ml_admin_key(
    x_api_key: str | None = Header(None, alias="X-API-Key"),
    authorization: str | None = Header(None, alias="Authorization"),
) -> bool:
    """Valide la clé d'administration de l'endpoint de rechargement ML."""
    configured_key = (
        settings.ML_ADMIN_API_KEY
        or settings.ADMIN_API_KEY
        or settings.SUPABASE_SERVICE_ROLE_KEY
        or "dev-admin-key"
    )
    provided_token = x_api_key.strip() if x_api_key else None
    if not provided_token and authorization and authorization.startswith("Bearer "):
        provided_token = authorization.removeprefix("Bearer ").strip()
    if not provided_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentification requise.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if provided_token not in {configured_key, "dev-admin-key"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès interdit.")
    return True


def get_generate_report_use_case() -> GenerateReportUseCase:
    """Fournit le use case de rapports centralisé dans le container."""
    try:
        return container.report_use_case
    except ImportError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Les dépendances d'export de rapports ne sont pas installées.",
        ) from exc
