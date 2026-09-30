# Couche Infrastructure

## Rôle

L'infrastructure implémente les ports applicatifs et domaine avec les bibliothèques concrètes du projet : Supabase, les modèles ML, Gemini, les notifications et les formats de rapports.

## Ce qu'on peut y mettre

- Adaptateurs qui implémentent les interfaces des couches internes.
- Conversion entre les lignes Supabase et les entités du domaine.
- Appels réseau, SDK, accès aux modèles joblib et écritures de fichiers.
- Adaptateurs simulés utilisés par les tests.

## Ce qu'on ne doit jamais y mettre

- Décisions de routage HTTP ou schémas FastAPI.
- Règles métier qui doivent rester dans domain/application.
- Dépendances vers `presentation/`.
- Imports de routeurs pour appeler une fonctionnalité applicative.

## Exemples

### Fabriquer un dépôt Supabase

```python
client = create_supabase_client()
machines = SupabaseMachineRepository(client)
```

### Assembler les modèles existants

```python
forecast = XGBoostAdapter(model_manager, reading_repository)
anomaly = IsolationForestAdapter(model_manager)
ml_service = CombinedMLAdapter(forecast, anomaly)
```

### Tester sans modèle réel

```python
ml_service = MockMLAdapter(predictions=[42.0, 43.0])
llm_service = MockLLMAdapter("Réponse simulée")
```

## Erreurs courantes

- Réécrire une logique ML déjà disponible plutôt que l'envelopper.
- Créer un client Supabase au moment de l'import d'un module.
- Laisser les objets SDK ou les modèles Pydantic traverser vers domain.
- Bloquer la boucle asynchrone avec les appels synchrones du SDK. Les adaptateurs ML, Gemini, rapports et dépôts Supabase déportent leurs appels synchrones dans un thread.
- Interpréter les bornes min/max d'une projection comme un intervalle de confiance calibré.

## Adaptateurs présents

- `persistence/supabase/` : client différé et dépôts machine/mesures.
- `ml/` : adaptateurs XGBoost et Isolation Forest, composite et mock.
- `llm/` : gateway Gemini et mock.
- `notifications/` : WhatsApp Cloud API et console.
- `reports/` : adaptateur du service historique et raccourcis PDF/XLSX.
