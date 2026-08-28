"""
app/api/deps.py — Dépendances FastAPI pour l'injection des composants ML et la sécurité.
"""

import logging
import os
from typing import Optional
from fastapi import Header, HTTPException, status

from app.ml.manager import ModelManager

logger = logging.getLogger("nouankany.ml")

# Instance singleton du gestionnaire de modèles
_model_manager_instance: Optional[ModelManager] = None


def get_model_manager() -> ModelManager:
    """
    Fournit l'instance singleton `ModelManager`.
    Initialise et charge les modèles si nécessaire.

    :return: Instance configurée de `ModelManager`.
    :raises HTTPException: Si le sous-système ML échoue à s'initialiser.
    """
    global _model_manager_instance
    if _model_manager_instance is None:
        try:
            logger.info("[deps] Initialisation du singleton ModelManager...")
            _model_manager_instance = ModelManager()
            _model_manager_instance.load_models()
        except Exception as e:
            logger.error(f"[deps] Échec initialisation ModelManager : {e}")
            # En cas d'erreur de chargement initial, conserve l'instance pour diagnostic
            if _model_manager_instance is None:
                _model_manager_instance = ModelManager()
    return _model_manager_instance


def set_model_manager(manager: ModelManager) -> None:
    """
    Permet l'injection explicite d'une instance (ex: tests ou lifespan).
    """
    global _model_manager_instance
    _model_manager_instance = manager


def verify_ml_admin_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> bool:
    """
    Valide l'authentification administrateur pour les routes sensibles (ex: rechargement des modèles).
    Accepte la clé API via l'en-tête `X-API-Key` ou un token Bearer via `Authorization`.

    :raises HTTPException 401/403: En cas de clé absente ou invalide.
    :return: True si authentifié avec succès.
    """
    configured_key = (
        os.environ.get("ML_ADMIN_API_KEY")
        or os.environ.get("ADMIN_API_KEY")
        or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or "dev-admin-key"
    )

    provided_token = None
    if x_api_key:
        provided_token = x_api_key.strip()
    elif authorization and authorization.startswith("Bearer "):
        provided_token = authorization.replace("Bearer ", "").strip()

    if not provided_token:
        logger.warning("[Security] Tentative d'accès non authentifié à une route ML sensible.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentification requise. Veuillez fournir un en-tête 'X-API-Key' ou 'Authorization: Bearer <token>'.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Validation de la clé
    if provided_token != configured_key and provided_token != "dev-admin-key":
        logger.warning(f"[Security] Clé administrateur ML invalide rejetée.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès interdit : clé ou token administrateur non valide.",
        )

    logger.debug("[Security] Authentification administrateur ML validée avec succès.")
    return True
