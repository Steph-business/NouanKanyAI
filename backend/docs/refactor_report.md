# Rapport de refactoring — NouanKanyAI

**État :** phases 0 à 9 réalisées ; phase 10 exécutée. La suite a collecté 166 tests : 165 passent et un test de latence ML échoue sous le seuil par défaut sur l'environnement courant.

## Résumé

Le backend a commencé sa migration depuis une organisation centrée sur `main.py`, `app/api/`, `app/interface/` et `app/ml/` vers les couches `domain`, `application`, `infrastructure` et `presentation`. La configuration est centralisée dans `app/config/settings.py`, les services et dépôts sont assemblés dans `app/config/container.py`, et `main.py` sert de point d'entrée ASGI compatible.

Les chemins historiques sont encore présents et utilisés : `app/presentation/legacy_app.py` conserve les routes et comportements historiques, tandis que certains modules sous `app/api/`, `app/interface/` et `app/ml/` restent des points de compatibilité ou sont encore utilisés directement. La migration n'est donc pas complète. Les contrats HTTP et les artefacts ML doivent rester inchangés lors des phases restantes.

## Structure avant / après

| Avant (inventaire phase 0) | Après (audit phase 10) |
|---|---|
| 69 fichiers Python sous `app/` | 154 fichiers Python sous `app/` |
| Entrée principale concentrée dans `main.py` | `main.py` délègue à `presentation/legacy_app.py` |
| Modules `api/`, `interface/`, `ml/`, `ai/` | Ces modules coexistent avec `domain/`, `application/`, `infrastructure/`, `presentation/` et `config/` |
| Routes historiques et versionnées répertoriées dans `docs/endpoints_inventory.md` | Routes versionnées dédiées, routes historiques conservées dans `legacy_app.py`, nouveaux endpoints de rapport et santé |

Comptage actuel des nouveaux espaces Python : `domain/` 20 fichiers, `application/` 16, `infrastructure/` 22, `presentation/` 23, `config/` 4. Ces nombres comptent les fichiers Python, y compris les `__init__.py`.

## Changements livrés

- Configuration typée Pydantic Settings et configuration de logs.
- Déclaration de Jinja2 et PyYAML, requis par les modules IA utilisés pendant la collecte des tests.
- Entités, objets valeur, événements, exceptions et interfaces de dépôts du domaine.
- Ports, DTO, services et use cases applicatifs.
- Adaptateurs Supabase, ML, LLM, notifications, rapports et dépôts de démonstration.
- Routeurs, schémas, middlewares et handlers HTTP dans Presentation, avec chemins de compatibilité.
- Container d'injection, documentation des quatre couches, ADR, guide de contribution et outillage développeur.
- Audit de structure après migration dans `docs/audit_after.txt`.
- Rétablissement du comportement d'import historique de `backend.main`, afin que les anciens appels et monkeypatchs continuent de cibler les symboles legacy.
- Typage des réponses JSON aux frontières des dépôts Supabase et déclaration explicite de l'état d'initialisation du container.

## Inventaire des fichiers modifiés et créés

L'audit Git au moment de la phase 10 indique 16 chemins modifiés et environ 100 chemins non suivis ajoutés (les répertoires de couches, configuration, documentation et outillage). Ce relevé inclut aussi des fichiers préexistants modifiés dans l'espace de travail, notamment `.env`, `.env.example`, `frontend/package-lock.json` et un fichier de cache Python. Ils ne sont pas attribués au refactoring sans comparaison avec leur historique. Aucun fichier suivi n'a été supprimé pendant les phases observées.

Pour produire un décompte exact par fichier, consulter `git status --short` et comparer à la branche de départ ; le dépôt n'a pas été commité par phase et certains changements préexistaient à cette phase.

## Validation de la phase 10

| Vérification | Résultat observé |
|---|---|
| `python -m pytest -q -o addopts='' --basetemp=.pytest_tmp_all_nocov` | **166 passed** en 56,67 s, sans couverture. Trois avertissements de dépréciation tiers. Les erreurs Temp Windows ont été évitées en plaçant `basetemp` dans le backend. |
| `python -m pytest -q --basetemp=.pytest_tmp_final` (configuration du projet, avec `pytest-cov`) | **165 passed, 1 failed**. Le test `test_anomaly_detection_latency_under_threshold` mesure 583 ms contre un seuil de 250 ms sous instrumentation. Le même groupe de performance passe sans couverture (**3/3**). |
| `python -m ruff check app/` | **Échec** : 1 336 problèmes restent sur l'ensemble du code après correction automatique limitée aux nouvelles couches. Le périmètre des nouvelles couches conserve 29 problèmes, principalement lignes longues, motifs FastAPI `Depends` et quelques règles de nommage ; le legacy comporte la majorité des problèmes. |
| `python -m mypy app/` (mypy 1.19.1) | **Échec** : 58 erreurs sur 153 fichiers. Elles incluent des stubs tiers absents et des erreurs dans le code historique (AI, ML, rapports), ainsi que des types à préciser à la frontière JSON des nouveaux adaptateurs Supabase et le typage des handlers d'exception. |
| `python -m lint_imports` | **Réussi** : 139 fichiers, contrat Clean Architecture conservé, aucun contrat cassé. |
| Import de l'application, `GET /docs`, `GET /openapi.json` via TestClient | **Réussi** : import réussi, `/docs` retourne 200, OpenAPI retourne 200. 30 routes sont enregistrées dans `app.routes` (routes intégrées FastAPI comprises). |
| Imports interdits dans `domain/` | **Aucune occurrence** de Pydantic, FastAPI, Supabase ou XGBoost dans le code Python du domaine. |
| Lectures directes `os.getenv` / `os.environ` dans `app/` | **Aucune occurrence dans le code** ; la seule correspondance de recherche était un exemple négatif dans le README Presentation. |
| Démarrage serveur et appels manuels des endpoints métier | **Non validés** dans cette phase ; le test de client vérifie la disponibilité de la documentation OpenAPI uniquement. |

Les 166 tests annoncés passent sans couverture. L'exécution standard avec `pytest-cov` fait échouer uniquement le test SLO d'anomalie : l'instrumentation augmente la durée mesurée au-delà de 250 ms (583 ms au dernier passage), tandis que le groupe de performance passe sans couverture. Le seuil n'a pas été augmenté pour masquer ce résultat. Les dépendances runtime et outils ont été installés dans `backend/venv`; cet environnement local n'est pas suivi par Git.

## Points d'amélioration

1. Adapter l'exécution du test SLO pour mesurer la latence sans instrumentation de couverture, puis garder les tests fonctionnels sous couverture afin que `make test` soit vert sans relâcher le seuil de 250 ms.
2. Résoudre les 29 problèmes Ruff des nouvelles couches et les erreurs mypy des adapters et handlers, puis planifier séparément le nettoyage du code historique.
3. Rejouer la suite complète après correction du SLO et comparer les contrats HTTP de toutes les routes à l'inventaire initial et aux tests frontend.
4. Migrer progressivement les handlers encore dans `legacy_app.py` vers les routes fines et use cases, sans retirer les chemins de compatibilité avant vérification des consommateurs.
5. Mettre à jour `docs/endpoints_inventory.md` en indiquant clairement le statut avant/après de chaque endpoint et les routes réellement montées.
6. Étendre les tests d'intégration des adaptateurs et du container, puis comparer les changements au commit de départ ; aucun commit atomique par phase n'a été créé.

