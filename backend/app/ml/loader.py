"""
app/ml/loader.py — Composant responsable du chargement sécurisé des artefacts ML.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import joblib

from app.ml.exceptions import (
    ArtifactMissingError,
    ManifestError,
    ModelNotLoadedError,
)

logger = logging.getLogger("nouankany.ml")


class ModelLoader:
    """
    Gestionnaire d'E/S et de chargement des artefacts de Machine Learning.
    Responsable de l'inspection du système de fichiers, du décodage du manifeste
    de déploiement et de la désérialisation des objets joblib et métadonnées.
    """

    def __init__(self, artifacts_dir: Optional[str | Path] = None) -> None:
        """
        Initialise le chargeur d'artefacts.

        :param artifacts_dir: Chemin racine du dossier contenant les artefacts.
                              Par défaut : backend/artifacts.
        """
        if artifacts_dir is None:
            # backend/artifacts par rapport à l'emplacement actuel
            base_backend_dir = Path(__file__).resolve().parent.parent.parent
            self.artifacts_dir = base_backend_dir / "artifacts"
        else:
            self.artifacts_dir = Path(artifacts_dir)

        logger.debug(f"[ModelLoader] Initialisé avec le répertoire d'artefacts: {self.artifacts_dir}")

    def load_manifest(self) -> Dict[str, Any]:
        """
        Lit et valide le fichier `deployment_manifest.json`.

        :return: Dictionnaire représentant le contenu du manifeste.
        :raises ArtifactMissingError: Si le fichier manifeste est introuvable.
        :raises ManifestError: Si le contenu JSON est invalide.
        """
        manifest_path = self.artifacts_dir / "registry" / "deployment_manifest.json"
        if not manifest_path.is_file():
            logger.error(f"[ModelLoader] Fichier manifeste introuvable : {manifest_path}")
            raise ArtifactMissingError(
                f"Le manifeste de déploiement est introuvable : {manifest_path}",
                details={"path": str(manifest_path)},
            )

        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
            logger.debug(
                f"[ModelLoader] Manifeste chargé avec succès. Projet={manifest_data.get('project')}, Version={manifest_data.get('version')}"
            )
            return manifest_data
        except json.JSONDecodeError as e:
            logger.error(f"[ModelLoader] Erreur de décodage JSON pour le manifeste : {e}")
            raise ManifestError(
                f"Le fichier manifeste contient du JSON invalide : {e}",
                details={"path": str(manifest_path), "error": str(e)},
            ) from e

    def load_joblib_model(self, model_relative_path: str) -> Any:
        """
        Désérialise un modèle Python via `joblib.load`.

        :param model_relative_path: Chemin relatif du fichier d'artefact depuis `artifacts_dir`
                                    ou nom absolu si déjà fourni.
        :return: L'objet Pipeline / modèle scikit-learn ou XGBoost désérialisé.
        :raises ArtifactMissingError: Si le fichier joblib n'existe pas.
        :raises ModelNotLoadedError: Si le chargement échoue lors de la désérialisation.
        """
        target_path = Path(model_relative_path)
        if not target_path.is_absolute():
            target_path = self.artifacts_dir / model_relative_path

        # Si le chemin relatif échoue, essayer des chemins alternatifs connus
        if not target_path.is_file():
            # Essayer sous artifacts/forecasting/ ou artifacts/anomaly/
            possible_paths = [
                self.artifacts_dir / "forecasting" / target_path.name,
                self.artifacts_dir / "anomaly" / target_path.name,
                self.artifacts_dir / target_path.name,
            ]
            found = False
            for p in possible_paths:
                if p.is_file():
                    target_path = p
                    found = True
                    break

            if not found:
                logger.error(f"[ModelLoader] Artefact modèle joblib introuvable : {target_path}")
                raise ArtifactMissingError(
                    f"Fichier modèle joblib introuvable : {model_relative_path}",
                    details={"requested_path": model_relative_path, "resolved_path": str(target_path)},
                )

        try:
            logger.debug(f"[ModelLoader] Chargement du modèle joblib depuis : {target_path}")
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model_obj = joblib.load(target_path)

            # Patch pour compatibilité cross-versions scikit-learn (ex: 1.6.1 -> 1.8.0 SimpleImputer)
            self._patch_estimator_compatibility(model_obj)

            logger.debug(f"[ModelLoader] Modèle chargé avec succès : {target_path.name}")
            return model_obj
        except Exception as e:
            logger.error(f"[ModelLoader] Échec lors de joblib.load({target_path}) : {e}")
            raise ModelNotLoadedError(
                f"Impossible de charger l'objet modèle depuis {target_path.name} : {e}",
                details={"path": str(target_path), "error": str(e)},
            ) from e

    def _patch_estimator_compatibility(self, estimator: Any) -> None:
        """
        Corrige dynamiquement les attributs internes manquants lors du désarchivage
        d'estimateurs sérialisés sous des versions antérieures de scikit-learn.

        :param estimator: Pipeline ou estimateur scikit-learn.
        """
        import numpy as np

        estimators_to_check = []
        if hasattr(estimator, "steps"):
            estimators_to_check.extend([step[1] for step in estimator.steps])
        else:
            estimators_to_check.append(estimator)

        for est in estimators_to_check:
            # Correctif SimpleImputer (sklearn 1.6.1 -> 1.8.0)
            if est.__class__.__name__ == "SimpleImputer" and not hasattr(est, "_fill_dtype"):
                setattr(est, "_fill_dtype", getattr(est, "_fit_dtype", np.float64))

    def load_json_file(self, relative_path: str) -> Dict[str, Any]:
        """
        Lit un fichier JSON d'artefact (métriques, cartes de modèles, schéma de caractéristiques).

        :param relative_path: Chemin relatif ou nom du fichier.
        :return: Dictionnaire décodé.
        :raises ArtifactMissingError: Si le fichier est manquant.
        :raises ManifestError: Si le contenu est corrompu.
        """
        target_path = Path(relative_path)
        if not target_path.is_absolute():
            target_path = self.artifacts_dir / relative_path

        if not target_path.is_file():
            # Chercher dans les sous-dossiers
            possible_paths = [
                self.artifacts_dir / "anomaly" / target_path.name,
                self.artifacts_dir / "forecasting" / target_path.name,
                self.artifacts_dir / "registry" / target_path.name,
            ]
            found = False
            for p in possible_paths:
                if p.is_file():
                    target_path = p
                    found = True
                    break

            if not found:
                logger.error(f"[ModelLoader] Fichier JSON introuvable : {relative_path}")
                raise ArtifactMissingError(
                    f"Fichier JSON d'artefact introuvable : {relative_path}",
                    details={"path": str(target_path)},
                )

        try:
            with open(target_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.debug(f"[ModelLoader] Fichier JSON chargé : {target_path.name}")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"[ModelLoader] Erreur de décodage JSON pour {target_path} : {e}")
            raise ManifestError(
                f"Fichier JSON corrompu : {target_path.name}",
                details={"path": str(target_path), "error": str(e)},
            ) from e

    def load_feature_schema(self, schema_name: str = "feature_schema_v2.json") -> Dict[str, Any]:
        """
        Charge le schéma des caractéristiques du projet.

        :param schema_name: Nom du fichier de schéma (v2 ou v1 par défaut).
        :return: Dictionnaire décrivant les caractéristiques.
        """
        try:
            return self.load_json_file(schema_name)
        except ArtifactMissingError:
            logger.warning(
                f"[ModelLoader] {schema_name} non trouvé, bascule vers feature_schema.json"
            )
            return self.load_json_file("feature_schema.json")
