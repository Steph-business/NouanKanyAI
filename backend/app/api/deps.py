"""Compatibilité d'import vers les dépendances HTTP de Presentation."""

from app.presentation.api.dependencies import (
    get_model_manager,
    set_model_manager,
    verify_ml_admin_key,
)

__all__ = ["get_model_manager", "set_model_manager", "verify_ml_admin_key"]
