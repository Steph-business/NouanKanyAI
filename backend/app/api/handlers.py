"""
app/api/handlers.py — Gestionnaires centralisés d'exceptions pour l'API REST ML.

Intercepte toutes les exceptions métier de la couche `app.ml` et produit
des réponses JSON uniformisées, typées et conformes au standard d'erreur HTTP.
"""

from datetime import datetime, timezone
import logging
from typing import Any, Dict
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.ml.exceptions import (
    ArtifactMissingError,
    FeatureValidationError,
    ManifestError,
    MLException,
    ModelNotLoadedError,
    PredictionError,
    PreprocessingError,
    RegistryError,
)

logger = logging.getLogger("nouankany.ml")


def build_error_response(
    status_code: int,
    code: str,
    message: str,
    details: Dict[str, Any] | None = None,
    request_id: str | None = None,
) -> JSONResponse:
    """
    Construit une réponse JSON d'erreur standardisée.
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "request_id": request_id,
            },
        },
    )


async def feature_validation_exception_handler(
    request: Request, exc: FeatureValidationError
) -> JSONResponse:
    logger.warning(f"[API Exception] Validation des caractéristiques échouée : {exc}")
    req_id = exc.details.get("request_id") if isinstance(exc.details, dict) else None
    return build_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        code="FEATURE_VALIDATION_ERROR",
        message=exc.message,
        details=exc.details,
        request_id=req_id,
    )


async def preprocessing_exception_handler(
    request: Request, exc: PreprocessingError
) -> JSONResponse:
    logger.warning(f"[API Exception] Prétraitement échoué : {exc}")
    req_id = exc.details.get("request_id") if isinstance(exc.details, dict) else None
    return build_error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        code="PREPROCESSING_ERROR",
        message=exc.message,
        details=exc.details,
        request_id=req_id,
    )


async def model_not_loaded_exception_handler(
    request: Request, exc: ModelNotLoadedError
) -> JSONResponse:
    logger.error(f"[API Exception] Modèle non chargé : {exc}")
    return build_error_response(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        code="MODEL_NOT_LOADED",
        message=exc.message,
        details=exc.details,
    )


async def prediction_exception_handler(
    request: Request, exc: PredictionError
) -> JSONResponse:
    logger.error(f"[API Exception] Échec du calcul d'inférence : {exc}")
    req_id = exc.details.get("request_id") if isinstance(exc.details, dict) else None
    return build_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="PREDICTION_EXECUTION_ERROR",
        message=exc.message,
        details=exc.details,
        request_id=req_id,
    )


async def artifact_missing_exception_handler(
    request: Request, exc: ArtifactMissingError
) -> JSONResponse:
    logger.error(f"[API Exception] Artefact ML introuvable : {exc}")
    return build_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="ARTIFACT_MISSING",
        message=exc.message,
        details=exc.details,
    )


async def ml_general_exception_handler(
    request: Request, exc: MLException
) -> JSONResponse:
    logger.error(f"[API Exception] Erreur générale ML : {exc}")
    return build_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="ML_SUBSYSTEM_ERROR",
        message=exc.message,
        details=exc.details,
    )


def register_ml_exception_handlers(app: FastAPI) -> None:
    """
    Enregistre l'ensemble des gestionnaires d'exceptions ML sur l'application FastAPI.
    """
    app.add_exception_handler(FeatureValidationError, feature_validation_exception_handler)
    app.add_exception_handler(PreprocessingError, preprocessing_exception_handler)
    app.add_exception_handler(ModelNotLoadedError, model_not_loaded_exception_handler)
    app.add_exception_handler(PredictionError, prediction_exception_handler)
    app.add_exception_handler(ArtifactMissingError, artifact_missing_exception_handler)
    app.add_exception_handler(ManifestError, artifact_missing_exception_handler)
    app.add_exception_handler(RegistryError, artifact_missing_exception_handler)
    app.add_exception_handler(MLException, ml_general_exception_handler)
    logger.debug("[API] Gestionnaires d'exceptions ML enregistrés avec succès.")
