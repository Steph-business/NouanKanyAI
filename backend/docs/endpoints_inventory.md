# Inventaire des endpoints HTTP — avant refactoring

Source : routes montées dans `backend/main.py` et routeurs inclus par cette application. Les réponses indiquées décrivent le contrat/code actuel. Les routes des rapports ne sont pas exposées par FastAPI dans cette version : elles sont des services Python internes.

## Routes racine et legacy (`main.py`)

| Méthode et chemin | Entrée | Réponse attendue | Source et fonction |
|---|---|---|---|
| GET `/` | Aucune | Objet `{message, version}` | `backend/main.py` — `root` |
| GET `/api/ml/health` | Aucune | État ML sérialisé ou statut indisponible | `backend/main.py` — `ml_health` |
| GET `/api/ml/models` | Aucune | Liste d'informations modèle | `backend/main.py` — `ml_models` |
| GET `/api/ml/metrics` | Aucune | Métriques ML consolidées | `backend/main.py` — `ml_metrics` |
| GET `/api/machines` | Aucune | Liste des machines et dernières mesures (Supabase ou démo) | `backend/main.py` — `get_machines` |
| GET `/api/facturation` | Aucune | Synthèse de gains, historique et factures | `backend/main.py` — `get_facturation` |
| GET `/api/admin/metrics` | Aucune | Statistiques plateforme, utilisateurs, santé et système | `backend/main.py` — `get_admin_metrics` |
| POST `/api/sites` | JSON `NewSite` (nom, localisation, type de bâtiment et champs facultatifs) | Site créé ou erreur | `backend/main.py` — `add_site` |
| POST `/api/machines` | JSON `NewMachine` (site, nom, code et caractéristiques machine) | Machine créée ou erreur | `backend/main.py` — `add_machine` |
| POST `/api/machines/{machine_id}/simulate` | `machine_id` dans le chemin | État de simulation/anomalie de la machine | `backend/main.py` — `simulate_anomaly` |
| POST `/api/machines/{machine_id}/toggle` | `machine_id` dans le chemin | Nouvel état activé/désactivé | `backend/main.py` — `toggle_machine_status` |
| POST `/api/machines/{machine_id}/eco` | `machine_id` dans le chemin | Résultat d'activation du mode éco | `backend/main.py` — `eco_machine_status` |
| POST `/api/predict` | JSON `PredictionRequest`: `machine_id`, `temperature_c`, `vibration_hz`, `pressure_bar`, `hours_ahead` facultatif | Liste de projections horaires avec puissance et coût | `backend/main.py` — `predict` |
| POST `/api/anomaly` | JSON `SensorReading`: id machine, puissance, température, vibration, pression, priorité facultative | Diagnostic d'anomalie | `backend/main.py` — `check_anomaly` |
| POST `/api/recommend` | Tableau JSON de `SensorReading` | Liste de recommandations | `backend/main.py` — `get_recommendations` |
| POST `/api/chat` | JSON `ChatRequest` (message et contexte éventuel) | Réponse textuelle du Copilot | `backend/main.py` — `chat_with_gemini` |
| POST `/api/machines/{machine_id}/analyze-media` | `machine_id` dans le chemin et fichier multipart `file` | Résultat d'analyse média/vision | `backend/main.py` — `analyze_machine_media` |

## Routes versionnées (`/api/v1`)

| Méthode et chemin | Entrée | Réponse attendue | Source et fonction |
|---|---|---|---|
| GET `/api/v1/machines` | Aucune | Liste de machines démo | `backend/app/interface/routers/machines.py` — `list_machines` |
| POST `/api/v1/predictions` | JSON `PredictionPayload`: id machine, température, vibration, pression, horizon facultatif | Charge prédite et horizon | `backend/app/interface/routers/predictions.py` — `get_predictions` |
| GET `/api/v1/billing` | Aucune | Synthèse fixe de gains, données de graphique et factures | `backend/app/interface/routers/billing.py` — `get_billing` |
| GET `/api/v1/recommendations` | Aucune | Liste et nombre de recommandations | `backend/app/interface/routers/recommendations.py` — `get_recommendations` |
| POST `/api/v1/chat` | JSON `ChatPayload`: `message` | Écho de message et statut | `backend/app/interface/routers/chat.py` — `chat_health` |
| GET `/api/v1/admin` | Aucune | Résumé administrateur fixe | `backend/app/interface/routers/admin.py` — `admin_health` |
| POST `/api/v1/ml/predict` | JSON `ForecastingRequest`: puissance, champs météo/temps/lags/history facultatifs, `strict_bounds` facultatif | `PredictionResponseSchema` avec valeur, version et métadonnées | `backend/app/api/v1/ml/router.py` — `predict_forecasting` |
| POST `/api/v1/ml/detect-anomaly` | JSON `AnomalyDetectionRequest`: puissance, température, vibration, pression et champs complémentaires facultatifs | `AnomalyResponseSchema` avec anomalie, score, sévérité et métadonnées | `backend/app/api/v1/ml/router.py` — `detect_anomaly` |
| GET `/api/v1/ml/health` | Aucune | `HealthStatus`; HTTP 503 si état unhealthy | `backend/app/api/v1/ml/router.py` — `get_ml_health` |
| GET `/api/v1/ml/models` | Aucune | Liste `ModelInfo` | `backend/app/api/v1/ml/router.py` — `list_models` |
| GET `/api/v1/ml/models/{model_name}` | `model_name` dans le chemin | `ModelInfo`, 404 si modèle absent | `backend/app/api/v1/ml/router.py` — `get_model_details` |
| GET `/api/v1/ml/metrics` | Aucune | Métriques runtime, entraînement, audit et santé | `backend/app/api/v1/ml/router.py` — `get_ml_metrics` |
| POST `/api/v1/ml/reload` | Clé par `X-API-Key` ou `Authorization: Bearer` | `ReloadResponseSchema`; authentification administrateur requise | `backend/app/api/v1/ml/router.py` — `reload_ml_models` |
| GET `/api/v1/ml/audit` | Query facultative: `limit` (1–500), `model_name`, `status`, `operation`, `request_id` | Liste de transactions d'audit | `backend/app/api/v1/ml/router.py` — `get_audit_logs` |

## Documentation et services sans route HTTP

- FastAPI fournit aussi `/docs`, `/redoc` et `/openapi.json` automatiquement.
- `backend/app/reports/service.py` expose un service Python de génération/export de rapports, mais aucun routeur de rapports n'est monté dans `main.py`.
- Aucun endpoint WebSocket ou route dynamique ajoutée par `add_api_route` n'a été trouvé.
