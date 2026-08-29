<div align="center">

# ⚡ NouanKanyAI
### Plateforme Intelligente de Gestion & d'Optimisation Énergétique Industrielle

**La solution SaaS & IA de nouvelle génération qui transforme la facture d'électricité en avantage compétitif pour l'Afrique.**

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI_0.115+-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js_15-000000?style=for-the-badge&logo=next.js)](https://nextjs.org)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python)](https://python.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=for-the-badge&logo=typescript)](https://www.typescriptlang.org)
[![XGBoost](https://img.shields.io/badge/ML-XGBoost_v2.0-FF6600?style=for-the-badge)](https://xgboost.readthedocs.io)
[![Gemini](https://img.shields.io/badge/AI-Google_Gemini-4285F4?style=for-the-badge&logo=google)](https://ai.google.dev)
[![Multi--Agents](https://img.shields.io/badge/AI_Architecture-Multi--Agent_Blackboard-8A2BE2?style=for-the-badge)]()
[![Tests](https://img.shields.io/badge/Tests-166_Passed-success?style=for-the-badge&logo=pytest)](https://pytest.org)

</div>

---

## 🎯 Qu'est-ce que NouanKanyAI ?

**NouanKanyAI** est une plateforme SaaS complète et intelligente conçue pour superviser, prédire, réguler et optimiser la consommation électrique des industries, hôtels, restaurants, bâtiments tertiaires et grands ménages en **Côte d'Ivoire** et en Afrique subsaharienne.

Elle articule des technologies de pointe :
- 📊 **Monitoring IoT & Télémétrie en temps réel** : acquisition haute fréquence (puissance kW, température, vibrations, pression).
- 🧠 **Sous-système ML v2 (XGBoost + Isolation Forest)** : prévisions de charge à horizon $t+1\text{h}$, détection multi-paramétrique d'anomalies et observabilité $p50/p95/p99$.
- 🤖 **AI Gateway & Copilot Industriel (Google Gemini)** : assistant conversationnel connecté aux services métiers via un système de **Tool Calling** normalisé.
- 📚 **Moteur RAG Industriel Avancé** : recherche documentaire hybride (vectorielle + BM25) sur 8 collections (ISO 50001, guides ADEME, IoT, audits).
- 🧩 **Architecture Multi-Agents (Blackboard)** : orchestration collaborative de 10 agents spécialisés (Énergie, Prévision, Anomalies, Carbone, etc.).
- 📑 **Générateur Automatique de Rapports Multi-Formats** : édition automatisée de rapports d'audit et de performance en **PDF, DOCX, XLSX et PPTX**.
- 💰 **Calcul dynamique des gains (Tarifs CIE Côte d'Ivoire)** & modèle économique **Gain-Share** (10% de commission sur les économies réelles constatées).

---

## ✨ Fonctionnalités & Capacités du Système

### 1. 🏠 Interface Utilisateur & Dashboard Next.js 15
- **Page d'Accueil Premium** : design sombre futuriste, carrousel d'illustrations 3D, effet *glassmorphism*, animations micro-interactives et authentification Supabase Auth.
- **Tableau de Bord Énergétique** : puissance active globale, courbe de charge journalière dynamique, appareils les plus énergivores actualisés toutes les 5s.
- **Pilotage & Régulation Actionnable** :
  - *Coupure d'urgence* : pilotage de relais intelligents ON/OFF.
  - *Mode Éco dynamique* : réduction instantanée de 35% de la puissance appelée sans rupture de production.
- **Gestion du Parc d'Équipements** : inventaire complet, télémétrie capteurs (kW, °C, Hz, bar) et simulateur d'anomalies pour tests de résilience.
- **Facturation Gain-Share & Paiement Mobile** : répartition 90% client / 10% commission, intégration Mobile Money (Wave, Orange, MTN, Moov).

---

### 2. 🧠 Sous-système Machine Learning v2 & Inférence Temps Réel
- **Architecture de Modèles Découplée (`app/ml/`)** :
  - `ModelLoader` & `RegistryManager` : chargement sécurisé avec vérification d'intégrité (hash SHA-256) et manifeste de déploiement.
  - `FeatureValidator` : validation stricte via `feature_schema.json`, détection et rejet immédiat des `NaN`, `Inf` et valeurs hors bornes.
  - `PredictionEngine` / `ForecastingService` : régression XGBoost v2.0.0 avec calcul automatique des lags ($t-1$, $t-24$) et moyennes mobiles.
  - `AnomalyDetectionService` : détection d'isolation forest avec classification par sévérité métier (*Normale*, *Faible*, *Modérée*, *Critique*).
- **Observabilité MLOps & Audit Trail** :
  - Métriques d'inférence en temps réel : percentiles de latence ($p50$, $p95$, $p99$), débit RPM, taux d'anomalies.
  - Journal d'audit cryptographique : traçabilité de chaque inférence avec UUID unique et empreinte numérique.
  - Diagnostics de santé `/api/v1/ml/health` et rechargement à chaud des modèles `/api/v1/ml/reload`.

---

### 3. 🤖 Couche GenAI & Copilot Industriel (`app/ai/`)
- **AIGateway Centralisée** : pont robuste avec Google Gemini (Flash / Pro), gestion des quotas, calcul de latences et mode simulation hors-ligne.
- **Mémoire Conversationnelle Multi-Niveaux** :
  - Mémoire courte de session active (buffer glissant).
  - Mémoire longue persistante avec isolation multi-tenant (par organisation, site et utilisateur).
  - Résumé automatique périodique du contexte pour optimiser les tokens LLM.
- **Constructeur de Prompts Dynamique (Jinja2 & YAML)** :
  - Personas configurables (*Energy Manager*, *Directeur d'usine*, *Technicien de maintenance*).
  - Adaptations contextuelles selon la typologie du bâtiment (*Industrie*, *Hôtel*, *Restaurant*, *Tertiaire*, *Grand ménage*).
  - Intégration automatique de la grille tarifaire CIE, de l'historique de consommation et des prévisions ML.
- **Système de Tool Calling Normalisé (10 Outils Métier)** :
  1. `predict_consumption` : Inférence prévisionnelle de consommation.
  2. `detect_anomaly` : Analyse de conformité et détection d'anomalies.
  3. `get_energy_history` : Récupération des historiques de consommation.
  4. `compare_periods` : Analyse comparative de consommation entre deux plages.
  5. `get_sensor_status` : Diagnostic temps réel des capteurs IoT.
  6. `get_equipment_details` : Fiche technique et état d'un équipement.
  7. `get_building_metrics` : KPIs consolidés du bâtiment.
  8. `generate_report` : Déclenchement de génération de rapport énergétique.
  9. `get_weather` : Données météo locales (température, humidité).
  10. `get_electricity_tariffs` : Grille tarifaire officielle CIE.

---

### 4. 📚 Moteur RAG Industriel Avancé
- **8 Collections Documentaires** : *Documentation NouanKanyAI, Norme ISO 50001, Manuels Fabricants, Rapports Énergétiques, Guides ADEME, FAQ, Rapports d'Audit, Documentation IoT*.
- **Découpage & Vectorisation Intelligente** : chunking avec conservation du contexte, calcul d'embeddings (Gemini `text-embedding-004` & adaptateur déterministe).
- **Recherche Hybride & Reranking** : combinaison de similarité vectorielle cosinus et recherche lexicale BM25, reranker sémantique avec boost de proximité.
- **Traçabilité & Performance** : citations précises des sources (documents, pages, sections) et cache de requêtes LRU avec TTL.

---

### 5. 📑 Générateur de Rapports Énergétiques Multi-Formats (`app/reports/`)
- **6 Typologies de Rapports** : *Journalier, Hebdomadaire, Mensuel, Audit Énergétique, Rapport d'Anomalies, Rapport de Performance*.
- **Exports Multi-Formats** :
  - 📄 **PDF** (ReportLab) : mise en page soignée, tableaux stylisés, graphiques vectoriels, KPIs et recommandations IA.
  - 📝 **DOCX** (python-docx) : document éditable complet avec charte graphique industrielle.
  - 📊 **XLSX** (openpyxl) : tableur avec feuilles dédiées aux séries temporelles, synthèses et formules de calcul.
  - 📽️ **PPTX** (python-pptx) : diaporama exécutif pour présentations de direction.
- **Graphiques Automatiques Intégrés** : courbes de charge 24h, répartition par tranche tarifaire CIE, consommation comparative par machine (Matplotlib).

---

### 6. 🧩 Architecture Multi-Agents Collaborative (`app/ai/multiagent/`)
- **Pattern Blackboard Partagé** : bus de données centralisé thread-safe permettant aux agents de publier et de consommer des faits partagés.
- **Orchestrateur Central** : routage dynamique des requêtes utilisateur selon 4 modes d'exécution (*Single, Séquentiel, Parallèle, Consensus*).
- **10 Agents Spécialisés Définis** :
  - ⚡ `Energy Agent` : surveillance globale et analyse des flux.
  - 📈 `Forecast Agent` : projections et anticipation des pics.
  - 🚨 `Anomaly Agent` : corrélation d'alarmes et diagnostic de panne.
  - 🔧 `Maintenance Agent` : recommandations prédictives sur les machines.
  - 💡 `Optimization Agent` : suggestions d'économies et d'efficacité.
  - 📋 `Reporting Agent` : synthèse et génération de rapports.
  - 💵 `Cost Saving Agent` : arbitrage tarifaire CIE et suivi du Gain-Share.
  - 🌿 `Carbon Agent` : calcul de l'empreinte carbone et émissions de CO₂.
  - 📡 `IoT Agent` : gestion du réseau de capteurs et passerelles.
  - 🛡️ `Administrator Agent` : gouvernance, santé des modèles et sécurité.

---

## 🏗️ Architecture du Projet

```
NouanKanyAI/
│
├── frontend/                               ← Application Web Next.js 15 (App Router)
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx                    ← Page d'accueil avec hero 3D & auth
│   │   │   ├── globals.css                 ← Design system (glassmorphism, dark mode)
│   │   │   └── dashboard/
│   │   │       ├── page.tsx                ← Tableau de bord principal temps réel
│   │   │       ├── layout.tsx              ← Sidebar, header & navigation
│   │   │       ├── appareils/              ← Gestion des machines & simulation
│   │   │       ├── predictions/            ← Copilot IA, chat & recommandations
│   │   │       ├── facturation/            ← Économies CIE, Mobile Money & audit
│   │   │       ├── sites/                  ← Supervision multi-sites
│   │   │       └── admin/                  ← Console d'administration MLOps
│   │   ├── components/                     ← Composants UI réutilisables
│   │   ├── hooks/
│   │   │   └── use-ml.ts                   ← Hooks React (usePrediction, useAnomaly, useMLHealth, etc.)
│   │   └── lib/
│   │       ├── ml-api.ts                   ← Client API TypeScript typé
│   │       └── supabase.ts                 ← Configuration client Supabase
│   └── public/                             ← Assets & illustrations 3D
│
├── backend/                                ← Backend API Python FastAPI
│   ├── main.py                             ← Point d'entrée ASGI & routes principales
│   ├── app/
│   │   ├── api/v1/ml/                      ← Routes REST ML versionnées (/predict, /detect-anomaly, /health, /metrics)
│   │   ├── ml/                             ← Moteur ML v2 (Loader, Registry, Validators, Engine, Monitoring, Audit)
│   │   ├── ai/                             ← Couche GenAI & Copilot Industriel
│   │   │   ├── gateway.py                  ← AIGateway Gemini avec fallbacks
│   │   │   ├── assistant.py                ← IndustrialCopilot
│   │   │   ├── memory.py                   ← Mémoire conversationnelle multi-tenant
│   │   │   ├── prompt_builder.py           ← Prompt builder dynamique Jinja2/YAML
│   │   │   ├── tools.py                    ← Système de 10 outils métier
│   │   │   ├── document_processor.py       ← Collections & smart chunking
│   │   │   ├── vector_store.py             ← Moteur de recherche vectorielle & BM25
│   │   │   ├── reranker.py                 ← Reranking sémantique
│   │   │   ├── query_cache.py              ← Cache LRU RAG
│   │   │   ├── citations.py                ← Formatage des citations de sources
│   │   │   ├── templates/                  ← Templates YAML/Jinja2 (personas, bâtiments)
│   │   │   └── multiagent/                 ← Infrastructure Multi-Agents (Blackboard, Orchestrator, 10 agents)
│   │   └── reports/                        ← Moteur de Rapports Énergétiques
│   │       ├── generator.py                ← Orchestrateur de génération
│   │       ├── charts.py                   ← Générateur de graphiques Matplotlib
│   │       ├── service.py                  ← Service de persistance et export
│   │       └── exporters/                  ← Exportateurs (PDF, DOCX, XLSX, PPTX)
│   ├── artifacts/                          ← Modèles sérialisés, schémas JSON et model cards
│   │   ├── forecasting/                    ← XGBoost model, feature schema, deployment manifest
│   │   ├── anomaly/                        ← Isolation Forest model, schemas
│   │   └── registry/                       ← Registre global des modèles
│   ├── data/                               ← Grille tarifaire CIE & données synthétiques
│   └── tests/                              ← Suite de tests automatisés (166 tests)
│       ├── ml/                             ← Tests unitaires, intégration et performances ML
│       ├── ai/                             ← Tests AI Gateway, RAG, Outils, Mémoire, Multi-Agents
│       └── reports/                        ← Tests génération PDF, DOCX, XLSX, PPTX
│
├── pytest.ini                              ← Configuration des tests backend
└── requirements.txt                        ← Dépendances Python globales
```

---

## 🛠️ Stack Technologique Détaillée

### Frontend
| Technologie | Version | Rôle & Usage |
|---|---|---|
| **Next.js** | 15.0+ | Framework React avec App Router et Server Components |
| **TypeScript** | 5.0+ | Typage statique strict sur l'ensemble des modules |
| **Recharts** | 2.13+ | Visualisation interactive (Courbes de charge, Barres, Camemberts) |
| **Lucide React** | Latest | Bibliothèque d'icônes vectorielles |
| **Supabase JS** | 2.45+ | Authentification JWT et synchronisation temps réel |
| **Vanilla CSS** | — | Design system haute performance (Glassmorphism, animations GPU) |

### Backend & Machine Learning
| Technologie | Version | Rôle & Usage |
|---|---|---|
| **Python** | 3.12 | Environnement d'exécution moderne |
| **FastAPI** | 0.115+ | Framework API REST asynchrone haute performance |
| **Pydantic** | v2.9+ | Validation stricte des schémas et sérialisation |
| **XGBoost** | 2.0+ | Modèle de régression pour la prévision de charge |
| **Scikit-learn** | 1.5+ | Modèle Isolation Forest pour la détection d'anomalies |
| **Pandas / NumPy** | 2.0+ | Manipulation vectorielle des séries temporelles |
| **Joblib** | 1.4+ | Sérialisation et chargement des artefacts ML |

### Intelligence Artificielle Générative & RAG
| Composant | Technologie / Approche | Rôle & Usage |
|---|---|---|
| **LLM Provider** | Google Gemini (Flash / Pro) | Moteur de raisonnement conversationnel et vision |
| **Embeddings** | Gemini `text-embedding-004` / Mock | Vectorisation sémantique des documents |
| **Recherche Documentaire** | Hybride (Cosinus + BM25) | Recherche multi-critères sur les bases documentaires |
| **Templates** | Jinja2 + YAML | Personas dynamiques et adaptateurs multi-fournisseurs |
| **Multi-Agents** | Pattern Blackboard + Orchestrateur | Collaboration distribuée de 10 agents experts |

### Moteur de Rapports
| Format | Librairie | Spécificités |
|---|---|---|
| **PDF** | ReportLab | Mise en page vectorielle, tableaux haute fidélité, graphiques intégrés |
| **DOCX** | python-docx | Rapports éditables sous Microsoft Word |
| **XLSX** | openpyxl | Tableurs avec onglets analytiques et formules |
| **PPTX** | python-pptx | Présentations de synthèse pour comités de direction |
| **Graphiques** | Matplotlib | Rendu des courbes de charge, camemberts tarifaires et histogrammes |

---

## ⚡ Grille Tarifaire CIE (Côte d'Ivoire) Intégrée

NouanKanyAI intègre nativement la tarification officielle de la **Compagnie Ivoirienne d'Électricité (CIE)** pour calculer au centime près les coûts et gains :

| Tranche Tarifaire | Plage de Consommation | Tarif Unitaire (FCFA / kWh) |
|---|---|---|
| **Sociale** | 0 – 80 kWh | **36 FCFA** |
| **Domestique** | 81 – 150 kWh | **46 FCFA** |
| **Non Domestique** | 151 – 500 kWh | **68 FCFA** |
| **Professionnelle / Industrielle** | > 500 kWh | **96 FCFA** |

---

## 🚀 Installation & Démarrage Rapide

### 1. Prérequis
- **Python 3.12+**
- **Node.js 18+** et **npm**
- Clé API **Google Gemini** (sur [Google AI Studio](https://aistudio.google.com))
- Projet **Supabase** (gratuit sur [supabase.com](https://supabase.com))

---

### 2. Configuration de l'environnement Backend

1. **Naviguer dans le dossier backend et configurer le fichier `.env`** :
   ```bash
   cd NouanKanyAI/backend
   cp .env.example .env
   ```

2. **Renseigner les clés dans `backend/.env`** :
   ```env
   GEMINI_API_KEY=votre_cle_gemini
   SUPABASE_URL=https://votre-projet.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=votre_cle_service_role
   ```

3. **Installer les dépendances Python** :
   ```bash
   pip install -r requirements.txt
   ```

4. **Lancer la suite de tests automatisés** :
   ```bash
   pytest
   # Résultat attendu : 166 passed
   ```

5. **Démarrer le serveur API FastAPI** :
   ```bash
   python main.py
   # API accessible sur : http://localhost:8000
   # Swagger / OpenAPI : http://localhost:8000/docs
   ```

---

### 3. Configuration & Démarrage du Frontend

1. **Naviguer dans le dossier frontend et installer les modules** :
   ```bash
   cd ../frontend
   npm install
   ```

2. **Lancer le serveur de développement Next.js** :
   ```bash
   npm run dev
   # Interface disponible sur : http://localhost:3000
   ```

---

## 🧪 Validation & Couverture des Tests

La plateforme dispose d'une suite exhaustive de tests automatisés couvrant tous les niveaux de l'architecture :

```bash
pytest backend/tests/ -v
```

- **Tests ML (`backend/tests/ml/`)** : validation des artefacts, intégrité des manifestes, chargement `ModelLoader`, hot-reload `ModelManager`, validation des bornes et `NaN` `FeatureValidator`, calculs de latence `PredictionEngine`, métriques $p50/p95/p99$ et tests de charge sous 50ms.
- **Tests AI & RAG (`backend/tests/ai/`)** : centralisation `AIGateway`, formatage dynamique `PromptBuilder`, isolation de la mémoire multi-tenant, exécution des 10 outils métier, recherche hybride RAG et orchestrateur multi-agents.
- **Tests Rapports (`backend/tests/reports/`)** : génération de graphiques Matplotlib et exports binaires intègres en PDF, DOCX, XLSX et PPTX.
- **Tests API FastAPI (`backend/tests/test_ml_api.py`)** : endpoints `/predict`, `/detect-anomaly`, `/health`, `/metrics` et conformité des codes de retour HTTP.

---

## 📄 Licence

Ce projet est distribué sous licence **MIT**.

<div align="center">

---

**Développé avec passion pour l'efficacité énergétique industrielle | NouanKanyAI © 2026**

*Optimisez votre énergie. Maximisez vos économies.*

</div>
