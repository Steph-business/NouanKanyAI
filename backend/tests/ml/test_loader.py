"""
backend/tests/ml/test_loader.py — Tests unitaires pour ModelLoader.

Vérifie le chargement sécurisé des modèles XGBoost et Isolation Forest,
la détection d'artefacts manquants et la gestion d'erreurs d'initialisation.
"""

from pathlib import Path
import pytest
from app.ml.loader import ModelLoader
from app.ml.exceptions import ArtifactMissingError, ModelNotLoadedError, ManifestError


class TestModelLoader:
    """Suite de tests unitaires pour le chargeur d'artefacts ModelLoader."""

    def test_loader_initialization_default_path(self):
        """Vérifie l'initialisation du chargeur avec le chemin d'artefacts par défaut."""
        loader = ModelLoader()
        assert loader.artifacts_dir is not None
        assert loader.artifacts_dir.exists()

    def test_loader_custom_path_resolution(self, tmp_path):
        """Vérifie le comportement du chargeur avec un chemin d'artefacts personnalisé."""
        custom_dir = tmp_path / "custom_artifacts"
        custom_dir.mkdir()
        loader = ModelLoader(artifacts_dir=custom_dir)
        assert loader.artifacts_dir == custom_dir

    def test_load_manifest_success(self):
        """Vérifie la lecture correcte du manifest de déploiement."""
        loader = ModelLoader()
        manifest = loader.load_manifest()
        assert isinstance(manifest, dict)
        assert len(manifest) > 0

    def test_load_joblib_models_success(self):
        """Vérifie le chargement des modèles joblib."""
        loader = ModelLoader()
        forecaster = loader.load_joblib_model("forecasting/xgb_pipeline_v2.0.0.joblib")
        assert forecaster is not None
        assert hasattr(forecaster, "predict")

        anomaly = loader.load_joblib_model("anomaly/if_pipeline_v2.0.0.joblib")
        assert anomaly is not None
        assert hasattr(anomaly, "predict")

    def test_load_feature_schema_success(self):
        """Vérifie le chargement du schéma des caractéristiques."""
        loader = ModelLoader()
        schema = loader.load_feature_schema()
        assert isinstance(schema, dict)
        assert len(schema) > 0

    def test_loader_missing_manifest_raises_error(self, tmp_path):
        """Vérifie qu'un manifest absent lève une exception ArtifactMissingError."""
        empty_dir = tmp_path / "empty_artifacts"
        empty_dir.mkdir()
        loader = ModelLoader(artifacts_dir=empty_dir)
        
        with pytest.raises(ArtifactMissingError):
            loader.load_manifest()

    def test_loader_missing_joblib_raises_error(self, tmp_path):
        """Vérifie qu'un fichier modèle absent lève une exception ArtifactMissingError."""
        empty_dir = tmp_path / "empty_artifacts"
        empty_dir.mkdir()
        loader = ModelLoader(artifacts_dir=empty_dir)

        with pytest.raises(ArtifactMissingError):
            loader.load_joblib_model("modele_introuvable.joblib")
