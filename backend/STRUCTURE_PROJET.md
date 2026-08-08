# Structure du backend NouanKanyAI

## Vue d’ensemble

Le backend a été restructuré pour offrir une organisation claire, professionnelle et évolutive.

## Arborescence retenue

```text
backend/
├── main.py                  # Point d’entrée principal de l’API
├── requirements.txt         # Dépendances Python
├── .env                     # Configuration locale
├── .env.example             # Exemple de configuration
├──
├── app/
│   ├── __init__.py
│   ├── core/
│   │   └── __init__.py
│   ├── api/
│   │   └── __init__.py
│   └── services/
│       └── __init__.py
│
├── ml/
│   ├── generate_data.py
│   ├── train_xgboost.py
│   ├── train_anomaly.py
│   ├── recommendation_engine.py
│   ├── data/
│   └── models/
│
├── data/
│   ├── synthetic_data.py
│   └── cie_tariffs.json
│
└── tests/
    └── test_backend.py
```

## Règles de structure

- main.py : point d’entrée unique de l’API
- app/ : encapsule la logique applicative
- core/ : utilitaires partagés
- api/ : endpoints et routes
- services/ : logique métier et traitements
- ml/ : modèles et scripts d’intelligence artificielle
- tests/ : validation technique

## Objectif

Cette structure permet :
- de mieux séparer les responsabilités ;
- d’évoluer vers une architecture plus propre ;
- d’éviter la confusion entre les dossiers dupliqués ;
- de préparer le projet pour une mise en production plus sérieuse.
