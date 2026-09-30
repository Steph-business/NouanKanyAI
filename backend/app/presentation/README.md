# Couche Presentation

## Rôle

Presentation traduit les protocoles externes en commandes applicatives et sérialise les résultats. Les routes définissent les contrats HTTP, tandis que les dépendances fournissent les services nécessaires.

## Ce qu'on peut y mettre

- Routeurs FastAPI et schémas Pydantic d'entrée/sortie.
- Middlewares de requête et de corrélation.
- Traduction des exceptions métier en réponses HTTP.
- Adaptateurs de compatibilité temporaires pendant la migration.

## Ce qu'on ne doit jamais y mettre

- Calcul métier important ou algorithmes ML.
- Accès directs à Supabase, aux fichiers ou aux APIs tierces.
- Modèles métier Pydantic partagés avec le domaine.
- Configuration brute via `os.getenv`.

## Exemples

### Déclarer une route avec un contrat

```python
@router.post("/chat")
def chat(payload: ChatRequest) -> dict[str, str]:
    return {"reply": payload.message, "status": "ok"}
```

### Ajouter un identifiant de corrélation

```python
app.add_middleware(RequestIdMiddleware)
```

### Traduire une erreur métier

```python
app.add_exception_handler(MachineNotFoundError, machine_not_found_handler)
```

## Erreurs courantes

- Modifier un chemin ou un schéma sans maintenir le contrat du frontend.
- Instancier les fournisseurs techniques directement dans les handlers.
- Déclarer la même route deux fois dans des routeurs différents.
- Retourner les entités du domaine comme contrat HTTP sans mapping.

## Migration en cours

- Les routes versionnées existantes vivent maintenant dans `api/v1/routes/`.
- `app/api/v1/ml/router.py`, `app/schemas/ml.py` et `app/interface/routers/` restent des chemins de compatibilité.
- `POST /api/v1/reports` ajoute un export de fichier via le use case; la dépendance est fournie par `app.config.container`.
- Le chat conserve actuellement sa réponse de démonstration, en attendant le raccordement au Copilot applicatif.
- `legacy_app.py` conserve les handlers legacy et leur accès direct aux services jusqu'à une migration ultérieure; `main.py` reste leur point d'entrée de compatibilité.
