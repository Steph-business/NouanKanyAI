# Manuel du Backend NouanKanyAI

## 1. Vue d’ensemble

Le backend de NouanKanyAI est la couche centrale de traitement, d’API et d’intelligence artificielle du système. Son objectif est de :

- exposer des endpoints FastAPI au frontend ;
- fournir des données de machines et de consommation ;
- entraîner et utiliser des modèles de prédiction et d’anomalie ;
- générer des recommandations métier utiles pour l’optimisation énergétique ;
- fonctionner localement, même sans base Supabase distante.

Le backend a été consolidé pour rester robuste tout en adoptant une structure plus propre et professionnelle.

---

## 2. Architecture générale

Le backend suit désormais une organisation simple et maintenable avec quatre grandes responsabilités :

1. Couche API
   - gestion des requêtes HTTP via FastAPI ;
   - définition des routes et des réponses JSON.

2. Couche métier / services
   - logique de préparation des données de démonstration ;
   - services applicatifs pour les routes structurées.

3. Intelligence Artificielle
   - génération de données synthétiques ;
   - entraînement de modèles XGBoost et Isolation Forest ;
   - génération de recommandations.

4. Validation
   - tests automatisés pour sécuriser les endpoints principaux.

---

## 3. Structure réelle du projet

```text
backend/
├── main.py                         # Point d’entrée principal de l’API FastAPI
├── requirements.txt                # Dépendances Python du backend
├── .env                            # Variables d’environnement locales
├── .env.example                    # Exemple de configuration
├── app/
│   ├── __init__.py
│   ├── api/
│   ├── application/
│   ├── core/
│   ├── domain/
│   ├── infrastructure/
│   ├── interface/
│   │   └── routers/
│   │       ├── machines.py
│   │       ├── predictions.py
│   │       ├── billing.py
│   │       ├── recommendations.py
│   │       ├── chat.py
│   │       └── admin.py
│   └── services/
│       └── demo_data.py           # Service central de données de démonstration
├── ml/
│   ├── generate_data.py            # Génération des données synthétiques
│   ├── train_xgboost.py            # Entraînement du modèle de prédiction
│   ├── train_anomaly.py            # Entraînement du modèle d’anomalie
│   ├── recommendation_engine.py    # Moteur de recommandations
│   ├── data/
│   │   └── sensor_data.csv         # Données de capteurs générées
│   └── models/
│       ├── xgboost_model.pkl       # Modèle prédictif entraîné
│       └── isolation_forest.pkl    # Modèle d’anomalies entraîné
├── data/
│   ├── synthetic_data.py           # Données de référence métier
│   └── cie_tariffs.json            # Grille tarifaire CIE
└── tests/
    └── test_backend.py             # Tests de validation du backend
```

---

## 4. Rôle des composants principaux

### 4.1 Point d’entrée : main.py

Le fichier [backend/main.py](backend/main.py) est le cœur du backend.

Il assure :

- l’initialisation de l’application FastAPI ;
- la configuration CORS ;
- le chargement des modèles ML au démarrage ;
- l’inclusion des routers structurés ;
- un mode démo local si Supabase n’est pas disponible.

### 4.2 Routers structurés

Les routes sont maintenant organisées sous [backend/app/interface/routers](backend/app/interface/routers) :

- [backend/app/interface/routers/machines.py](backend/app/interface/routers/machines.py)
  - expose la liste des machines.

- [backend/app/interface/routers/predictions.py](backend/app/interface/routers/predictions.py)
  - expose un endpoint de prédiction simple et cohérent.

- [backend/app/interface/routers/billing.py](backend/app/interface/routers/billing.py)
  - expose les données de facturation.

- [backend/app/interface/routers/recommendations.py](backend/app/interface/routers/recommendations.py)
  - expose des recommandations métier.

- [backend/app/interface/routers/chat.py](backend/app/interface/routers/chat.py)
  - expose une interface d’assistant simple.

- [backend/app/interface/routers/admin.py](backend/app/interface/routers/admin.py)
  - expose des métriques administratives.

### 4.3 Service de données de démonstration

Le fichier [backend/app/services/demo_data.py](backend/app/services/demo_data.py) centralise la logique de données locales.

Il sert à :

- fournir des données cohérentes quand Supabase n’est pas configuré ;
- éviter les dépendances circulaires entre les modules ;
- conserver la logique métier indépendante de l’API.

### 4.4 Scripts ML

Le dossier [backend/ml](backend/ml) contient toujours l’intelligence du système :

- [backend/ml/generate_data.py](backend/ml/generate_data.py)
  - génère des données synthétiques réalistes sur plusieurs machines ;
  - simule des données de température, vibration, pression et consommation.

- [backend/ml/train_xgboost.py](backend/ml/train_xgboost.py)
  - entraîne un modèle XGBoost pour prédire la consommation énergétique.

- [backend/ml/train_anomaly.py](backend/ml/train_anomaly.py)
  - entraîne un modèle Isolation Forest pour détecter les anomalies.

- [backend/ml/recommendation_engine.py](backend/ml/recommendation_engine.py)
  - combine prédiction + détection d’anomalies ;
  - produit des recommandations concrètes.

### 4.5 Données métier

Le dossier [backend/data](backend/data) contient les ressources de référence :

- [backend/data/synthetic_data.py](backend/data/synthetic_data.py)
  - définit une base de machines et d’équipements simulés ;
  - sert de fond métier pour les démonstrations.

- [backend/data/cie_tariffs.json](backend/data/cie_tariffs.json)
  - contient la logique de tarification utile pour les calculs énergétiques.

### 4.6 Tests

Le dossier [backend/tests](backend/tests) contient des tests automatiques pour garantir le bon fonctionnement du backend.

Le fichier [backend/tests/test_backend.py](backend/tests/test_backend.py) vérifie :

- l’endpoint racine ;
- l’endpoint des machines ;
- l’endpoint structuré des machines.

---

## 5. Endpoints principaux

| Endpoint | Description |
|---|---|
| GET / | Vérifie que l’API fonctionne |
| GET /api/machines | Retourne l’état des machines |
| GET /api/facturation | Retourne les données de facturation |
| GET /api/v1/machines | Retourne les machines via le router structuré |
| POST /api/v1/predictions | Retourne une prédiction simple à partir d’une requête |
| GET /api/v1/billing | Retourne un payload de facturation |
| GET /api/v1/recommendations | Retourne des recommandations |
| POST /api/v1/chat | Répond à un message de type assistant |
| GET /api/v1/admin | Retourne des métriques administratives |

---

## 6. Workflow de fonctionnement

### 6.1 Démarrage du backend

Le backend peut être lancé localement avec la commande :

```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8001
```

Une fois démarré, l’API est accessible sur :

- http://127.0.0.1:8001
- http://127.0.0.1:8001/docs

### 6.2 Pipeline de données

1. Génération des données
   - le script [backend/ml/generate_data.py](backend/ml/generate_data.py) crée un dataset complet.

2. Entraînement des modèles
   - [backend/ml/train_xgboost.py](backend/ml/train_xgboost.py) entraîne le modèle de consommation.
   - [backend/ml/train_anomaly.py](backend/ml/train_anomaly.py) entraîne le modèle d’anomalies.

3. Exécution API
   - le backend charge ces modèles au démarrage.
   - chaque endpoint peut ensuite utiliser les modèles pour faire des prédictions et générer des recommandations.

### 6.3 Mode démo local

Si Supabase n’est pas configuré :

- l’API bascule en mode démo ;
- les données sont servies localement à partir des fichiers générés ;
- le système reste fonctionnel sans erreur bloquante.

---

## 7. Dépendances principales

Le backend repose sur :

- FastAPI pour l’API REST ;
- Uvicorn pour le serveur ASGI ;
- Pydantic pour la validation des entrées ;
- Pandas et NumPy pour le traitement des données ;
- Scikit-learn pour l’anomalie ;
- XGBoost pour la prédiction ;
- Joblib pour la sérialisation des modèles ;
- Supabase pour une intégration optionnelle de base de données.

---

## 8. Variables d’environnement

Le backend attend un minimum de configuration pour fonctionner proprement.

Exemple dans [backend/.env.example](backend/.env.example) :

```env
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
GEMINI_API_KEY=
FRONTEND_URL=http://localhost:3000
```

Si ces variables ne sont pas présentes, le backend continue en mode démo local.

---

## 9. Tests et qualité

Pour exécuter les tests :

```bash
python -m pytest backend/tests/test_backend.py
```

Résultat vérifié :

- 3 tests passés
- validation des endpoints principaux et du router structuré

---

## 10. Recommandations de structuration future

Pour garder ce backend propre et évolutif, il est recommandé de continuer dans cette direction :

- séparer davantage les responsabilités API / services / ML ;
- créer des services métier dédiés ;
- introduire des repositories si la base de données devient plus complexe ;
- ajouter des tests d’intégration et de performance ;
- isoler la logique de configuration dans un module dédié.

Cette structure est déjà solide pour un MVP professionnel et peut évoluer vers une architecture plus propre sans réécrire toute la base.

---

## 11. Conclusion

Le backend actuel est fonctionnel, robuste et prêt pour la démonstration. Il couvre les besoins essentiels d’un système intelligent de gestion énergétique :

- API accessible ;
- IA exploitable ;
- données synthétiques prêtes ;
- mode local fiable ;
- tests de validation en place.

C’est une base saine, claire et professionnelle pour continuer le développement du produit.
