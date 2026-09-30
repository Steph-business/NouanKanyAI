# Inventaire des variables d'environnement

Les noms ci-dessous sont extraits des lectures de variables dans le backend, des configurations d'exemple et des références frontend/déploiement. Les valeurs secrètes ne sont volontairement pas reproduites.

## Variables lues dans le code Python backend

| Nom | Usage | Emplacement |
|---|---|---|
| `SUPABASE_URL` | URL du projet Supabase | `backend/main.py` |
| `SUPABASE_SERVICE_ROLE_KEY` | Client Supabase backend; également fallback actuel pour la clé admin ML | `backend/main.py`, `backend/app/api/deps.py` |
| `FRONTEND_URL` | Origine frontend autorisée par CORS | `backend/main.py` |
| `ALLOWED_ORIGINS` | Origines CORS additionnelles, séparées par virgules | `backend/main.py` |
| `GEMINI_API_KEY` | Appels Gemini, vision et embeddings | `backend/main.py`, `backend/app/ai/gateway.py`, `backend/app/ai/embeddings.py` |
| `ML_ADMIN_API_KEY` | Clé d'administration ML | `backend/app/api/deps.py` |
| `ADMIN_API_KEY` | Fallback de clé d'administration ML | `backend/app/api/deps.py` |
| `PORT` | Port du serveur lorsqu'il est lancé via `python main.py` | `backend/main.py` |
| `ML_MAX_LATENCY_MS` | Seuil de performance des tests ML seulement | `backend/tests/ml/test_performance.py` |

## Variables frontend

| Nom | Usage | Emplacement |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | URL publique de l'API FastAPI | `frontend/src/lib/api.ts`, `frontend/.env.example` |
| `NEXT_PUBLIC_SUPABASE_URL` | URL Supabase côté navigateur | `frontend/src/lib/supabase.ts`, `frontend/.env.example` |
| `SUPABASE_URL` | Fallback URL Supabase dans le client frontend | `frontend/src/lib/supabase.ts` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Clé publique anon Supabase | `frontend/src/lib/supabase.ts`, `frontend/.env.example` |
| `SUPABASE_ANON_KEY` | Fallback de la clé anon frontend | `frontend/src/lib/supabase.ts` |

## Variables déclarées dans les fichiers d'environnement et de déploiement

- `backend/.env.example` : `GEMINI_API_KEY`, `SUPABASE_ACCESS_TOKEN`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `FRONTEND_URL`.
- `frontend/.env.example` : `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`.
- `render.yaml` référence également `GEMINI_API_KEY`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_ACCESS_TOKEN`, `FRONTEND_URL`, `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_SUPABASE_URL` et `NEXT_PUBLIC_SUPABASE_ANON_KEY`.
- `SUPABASE_ACCESS_TOKEN` est configurée comme variable mais aucune lecture n'a été trouvée dans le code applicatif.
