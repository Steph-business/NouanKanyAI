"""
app/ml/registry.py — Service de gestion et de consultation du registre de modèles.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.ml.exceptions import ArtifactMissingError, RegistryError
from app.ml.types import ModelInfo, RegistryEntry

logger = logging.getLogger("nouankany.ml")


class RegistryManager:
    """
    Gestionnaire du registre des modèles et métadonnées d'expérimentation.
    Interroge les fichiers `deployment_manifest.json` et `experiment_history.json`
    sans effectuer de désérialisation d'objets lourds.
    """

    def __init__(self, registry_dir: Optional[str | Path] = None) -> None:
        """
        Initialise le gestionnaire de registre.

        :param registry_dir: Dossier contenant le registre (registry/ ou artifacts/registry/).
        """
        if registry_dir is None:
            base_backend = Path(__file__).resolve().parent.parent.parent
            self.registry_dir = base_backend / "artifacts" / "registry"
        else:
            self.registry_dir = Path(registry_dir)

        logger.debug(f"[RegistryManager] Initialisé sur le dossier : {self.registry_dir}")

    def get_deployment_manifest(self) -> Dict[str, Any]:
        """
        Lit et retourne le manifeste de déploiement courant.

        :return: Dictionnaire décrivant la version déployée et ses artefacts.
        :raises RegistryError: En cas d'impossibilité de lire le manifeste.
        """
        manifest_file = self.registry_dir / "deployment_manifest.json"
        if not manifest_file.is_file():
            logger.error(f"[RegistryManager] Manifeste introuvable : {manifest_file}")
            raise RegistryError(
                f"Fichier de manifeste de déploiement introuvable : {manifest_file}"
            )

        try:
            with open(manifest_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except Exception as e:
            logger.error(f"[RegistryManager] Erreur de lecture du manifeste : {e}")
            raise RegistryError(
                f"Erreur de lecture du manifeste de déploiement : {e}"
            ) from e

    def get_latest_version(self) -> str:
        """
        Récupère la version active courante enregistrée dans le manifeste.

        :return: Chaîne de version (ex: "2.0.0").
        """
        manifest = self.get_deployment_manifest()
        return manifest.get("version", "1.0.0")

    def get_experiment_history(self) -> List[RegistryEntry]:
        """
        Charge l'historique de toutes les exécutions et entraînements enregistrés.

        :return: Liste des entrées de registre typées (`RegistryEntry`).
        """
        history_file = self.registry_dir / "experiment_history.json"
        if not history_file.is_file():
            logger.warning(
                f"[RegistryManager] Fichier d'historique introuvable : {history_file}"
            )
            return []

        try:
            with open(history_file, "r", encoding="utf-8") as f:
                raw_history = json.load(f)

            entries = [RegistryEntry(**item) for item in raw_history]
            logger.info(
                f"[RegistryManager] Historique chargé ({len(entries)} exécution(s))."
            )
            return entries
        except Exception as e:
            logger.error(
                f"[RegistryManager] Erreur lors du parsing de l'historique : {e}"
            )
            raise RegistryError(
                f"Échec de chargement de l'historique d'expériences : {e}"
            ) from e

    def get_model_metadata(self, model_name: str) -> Dict[str, Any]:
        """
        Recherche les métadonnées associées à un modèle donné par son nom.

        :param model_name: Nom du modèle (ex: 'XGBoost_Forecaster', 'IsolationForest_AnomalyDetector').
        :return: Dictionnaire des métadonnées du modèle.
        :raises RegistryError: Si le modèle est inconnu.
        """
        artifacts_dir = self.registry_dir.parent

        # Recherche des fichiers de cartes de modèles
        card_paths = [
            artifacts_dir / "forecasting" / f"{model_name}_card.json",
            artifacts_dir / "anomaly" / f"{model_name}_card.json",
            artifacts_dir / "anomaly" / "model_cards_v2.json",
            artifacts_dir / "forecasting" / "model_cards_v2.json",
        ]

        for path in card_paths:
            if path.is_file():
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = json.load(f)
                    if path.name == "model_cards_v2.json":
                        if model_name in content:
                            return content[model_name]
                        # essayer de matcher partiellement
                        for k, v in content.items():
                            if model_name.lower() in k.lower():
                                return v
                    else:
                        return content
                except Exception as e:
                    logger.warning(
                        f"[RegistryManager] Impossible de lire {path} : {e}"
                    )

        logger.error(
            f"[RegistryManager] Métadonnées introuvables pour le modèle '{model_name}'"
        )
        raise RegistryError(
            f"Aucune métadonnée enregistrée pour le modèle '{model_name}'"
        )

    def get_model_info(self, model_name: str) -> ModelInfo:
        """
        Construit un objet `ModelInfo` complet à partir du registre et des métadonnées.

        :param model_name: Nom du modèle cible.
        :return: Instance typée `ModelInfo`.
        """
        meta = self.get_model_metadata(model_name)
        version = meta.get("version", self.get_latest_version())
        metrics = meta.get("metrics", {})
        status = meta.get("status", "RESEARCH")
        trained_at = meta.get("trained_at", "")
        features = meta.get("features", [])

        # Identifier le type de modèle
        if "xgboost" in model_name.lower() or "forecaster" in model_name.lower():
            model_type = "XGBoost"
        elif "isolation" in model_name.lower() or "anomaly" in model_name.lower():
            model_type = "IsolationForest"
        else:
            model_type = "Unknown"

        return ModelInfo(
            name=model_name,
            version=version,
            model_type=model_type,
            status=status,
            trained_at=trained_at,
            features=features,
            metrics=metrics,
            artifact_path=None,
        )

    def prepare_future_version(self, new_version: str) -> Dict[str, Any]:
        """
        Prépare une ébauche de manifeste pour une version ultérieure.

        :param new_version: Numéro de la nouvelle version (ex: "2.1.0").
        :return: Ébauche de dictionnaire de manifeste.
        """
        current_manifest = self.get_deployment_manifest()
        new_manifest = current_manifest.copy()
        new_manifest["version"] = new_version
        logger.info(
            f"[RegistryManager] Ébauche de version préparée : {new_version}"
        )
        return new_manifest
