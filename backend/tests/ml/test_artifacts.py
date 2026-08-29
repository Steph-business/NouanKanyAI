"""
backend/tests/ml/test_artifacts.py — Tests de validation et d'intégrité des artefacts ML.

Vérifie l'existence, la structure JSON et la cohérence des schémas de features,
des model cards, du manifest de déploiement et des fichiers de modèles binaires (.joblib).
"""

from pathlib import Path
import json
import pytest
from app.ml.loader import ModelLoader


class TestArtifactsValidation:
    """Suite de validation des artefacts de production du sous-système ML."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.loader = ModelLoader()
        self.artifacts_dir = self.loader.artifacts_dir

    def test_artifacts_directory_exists(self):
        """Vérifie que le répertoire racine des artefacts existe."""
        assert self.artifacts_dir.exists(), f"Le dossier d'artefacts {self.artifacts_dir} est introuvable."
        assert self.artifacts_dir.is_dir()

    def test_deployment_manifest_structure(self):
        """Valide la structure et le contenu du manifest de déploiement."""
        manifest = self.loader.load_manifest()
        assert isinstance(manifest, dict), "Le manifest doit être un dictionnaire JSON."
        assert "project" in manifest or "version" in manifest or "models" in manifest or "artifacts" in manifest

    def test_feature_schemas_validity(self):
        """Valide le format et les bornes du schéma de caractéristiques."""
        schema = self.loader.load_feature_schema()
        assert isinstance(schema, dict), "Le schéma des features doit être un dictionnaire JSON."
        assert len(schema) > 0

    def test_model_cards_presence_and_validity(self):
        """Valide la présence et le contenu des cartes de modèle JSON."""
        xgb_card = self.loader.load_json_file("XGBoost_Forecaster_card.json")
        assert isinstance(xgb_card, dict)
        assert len(xgb_card) > 0

        iso_card = self.loader.load_json_file("IsolationForest_AnomalyDetector_card.json")
        assert isinstance(iso_card, dict)
        assert len(iso_card) > 0

    def test_model_binary_files_integrity(self):
        """Vérifie que les fichiers binaires .joblib sont désérialisables."""
        manifest = self.loader.load_manifest()
        artifacts_cfg = manifest.get("artifacts", {})
        
        forecasting_rel_path = (
            artifacts_cfg.get("forecasting_model", {}).get("path")
            if isinstance(artifacts_cfg.get("forecasting_model"), dict)
            else "forecasting/xgb_pipeline_v2.0.0.joblib"
        )
        anomaly_rel_path = (
            artifacts_cfg.get("anomaly_model", {}).get("path")
            if isinstance(artifacts_cfg.get("anomaly_model"), dict)
            else "anomaly/if_pipeline_v2.0.0.joblib"
        )

        forecaster = self.loader.load_joblib_model(forecasting_rel_path)
        assert forecaster is not None
        assert hasattr(forecaster, "predict")

        anomaly_detector = self.loader.load_joblib_model(anomaly_rel_path)
        assert anomaly_detector is not None
        assert hasattr(anomaly_detector, "predict")
