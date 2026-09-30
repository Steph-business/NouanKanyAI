# Contribuer à NouanKanyAI

## Démarrage en quelques minutes

Depuis le dossier `backend`, avec Python 3.12 ou supérieur :

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-dev.txt
if (!(Test-Path .env)) { Copy-Item .env.example .env }
.\.venv\Scripts\python.exe main.py
```

Le serveur écoute sur `http://localhost:8000`; sa documentation OpenAPI est disponible sur `/docs`. Renseigner les intégrations externes dans `.env` seulement si nécessaire; sans Supabase, le backend sélectionne les dépôts de démonstration.

Si GNU Make est installé, les raccourcis sont `make setup`, `make dev`, `make test` et `make lint`.

## Où placer le code ?

| Type | Emplacement |
|---|---|
| Entité, règle et objet valeur | `app/domain/` |
| Use case, DTO et port | `app/application/` |
| Adaptateur Supabase, ML, LLM, rapport ou notification | `app/infrastructure/` |
| Route FastAPI, schéma HTTP et middleware | `app/presentation/` |
| Configuration validée et composition root | `app/config/` |

`app/presentation/legacy_app.py` est une zone de compatibilité pendant la migration. Une nouvelle fonctionnalité doit utiliser les couches et le container au lieu d'y ajouter un handler métier.

## Conventions

- Branches : `feat/`, `fix/`, `refactor/`, `docs/`.
- Commits : Conventional Commits, par exemple `refactor(application): add invoice use case`.
- Code et noms de modules en anglais; docstrings et documentation destinées à l'équipe en français.
- Ajouter des types aux interfaces publiques et éviter `Any` hors des frontières SDK dynamiques justifiées.
- Ne jamais committer `.env`, clés privées ou secrets client.

## Vérifications

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check app/
.\.venv\Scripts\python.exe -m mypy app/
.\.venv\Scripts\lint-imports.exe
```

Les suites d'export ont besoin des dépendances de `requirements.txt`, et les outils de développement de `requirements-dev.txt`.

## Checklist de revue

- [ ] Les tests couvrent les règles et scénarios ajoutés.
- [ ] Les routes et schémas HTTP conservent les contrats clients convenus.
- [ ] Les nouvelles décisions d'architecture ont un ADR.
- [ ] Les modules publics ont des docstrings et types utiles.
- [ ] Ruff, mypy et import-linter passent dans un environnement complet.
- [ ] Les changements ne modifient ni artefacts ML ni secrets sans demande explicite.

