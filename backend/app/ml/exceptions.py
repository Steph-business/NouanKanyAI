"""
app/ml/exceptions.py — Exceptions personnalisées de la couche ML de NouanKanyAI.
"""


class MLException(Exception):
    """
    Exception de base pour toutes les erreurs de la couche ML.
    """

    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class ModelNotLoadedError(MLException):
    """
    Levée lorsqu'un modèle requis n'est pas chargé en mémoire.
    """

    pass


class RegistryError(MLException):
    """
    Levée lors d'un échec de lecture ou d'incohérence dans le registre de modèles.
    """

    pass


class FeatureValidationError(MLException):
    """
    Levée lorsque les données fournies ne respectent pas le schéma de caractéristiques.
    """

    pass


class PredictionError(MLException):
    """
    Levée lors d'un échec pendant le calcul d'une prédiction ou d'une détection d'anomalies.
    """

    pass


class PreprocessingError(MLException):
    """
    Levée lorsqu'une erreur survient lors du prétraitement ou de l'alignement des caractéristiques.
    """

    pass


class ManifestError(MLException):
    """
    Levée lorsque le manifeste de déploiement est absent, invalide ou corrompu.
    """

    pass


class ArtifactMissingError(MLException):
    """
    Levée lorsqu'un fichier d'artefact (modèle joblib, schéma JSON, model card) est introuvable.
    """

    pass
