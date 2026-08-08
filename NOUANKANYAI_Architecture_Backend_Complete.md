# NOUANKANYAI - ARCHITECTURE BACKEND PROFESSIONNELLE
## Guide de mise en place pour Lead Backend (Cote d'Ivoire)

---

## 1. PHILOSOPHIE ARCHITECTURALE

### Pattern : Clean Architecture / Hexagonale (adapte)
Separation stricte :
- **Domain** : Entites metier pures (Machine, Consommation, Facture)
- **Application** : Use cases (CalculerEconomies, DetecterAnomalie, GenererRecommandation)
- **Infrastructure** : Acces donnees, ML, API externes (Supabase, Gemini, CIE)
- **Interface** : FastAPI routers, DTOs, middlewares

Pourquoi ? En Afrique, les equipes sont petites. Le Clean Architecture permet :
- De changer Supabase par PostgreSQL auto-heberge si necessaire
- De swapper XGBoost par LightGBM sans toucher l'API
- De tester independamment le metier

---

## 2. STRUCTURE DES DOSSIERS CIBLE

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Point d'entree FastAPI
│   ├── config.py                  # Settings Pydantic (env vars)
│   ├── dependencies.py            # Injection de dependances
│   │
│   ├── domain/                    # Coeur metier (aucune dependance externe)
│   │   ├── __init__.py
│   │   ├── entities/
│   │   │   ├── machine.py         # dataclass Machine
│   │   │   ├── sensor_reading.py  # dataclass SensorReading
│   │   │   ├── invoice.py         # dataclass Invoice
│   │   │   └── recommendation.py  # dataclass Recommendation
│   │   ├── repositories/
│   │   │   ├── machine_repo.py    # Interface (ABC)
│   │   │   ├── sensor_repo.py     # Interface (ABC)
│   │   │   └── invoice_repo.py    # Interface (ABC)
│   │   └── services/
│   │       ├── cie_calculator.py      # Grille tarifaire CIE
│   │       ├── gain_share_calculator.py # Commission 10%
│   │       └── anomaly_detector.py    # Interface abstraite ML
│   │
│   ├── application/               # Use cases
│   │   ├── __init__.py
│   │   ├── machines/
│   │   │   ├── create_machine.py
│   │   │   ├── list_machines.py
│   │   │   └── simulate_anomaly.py
│   │   ├── predictions/
│   │   │   └── predict_consumption.py
│   │   ├── billing/
│   │   │   ├── calculate_savings.py
│   │   │   └── generate_invoice.py
│   │   ├── recommendations/
│   │   │   └── generate_recommendations.py
│   │   └── chat/
│   │       └── process_chat.py
│   │
│   ├── infrastructure/            # Acces techniques
│   │   ├── __init__.py
│   │   ├── db/
│   │   │   ├── supabase_client.py
│   │   │   └── migrations/        # SQL files
│   │   ├── ml/
│   │   │   ├── models/            # .pkl files
│   │   │   ├── xgboost_predictor.py
│   │   │   ├── isolation_forest_detector.py
│   │   │   └── recommendation_engine.py
│   │   ├── external/
│   │   │   ├── gemini_client.py
│   │   │   └── cie_tariffs.json
│   │   └── persistence/
│   │       ├── machine_repository.py    # Implementation Supabase
│   │       ├── sensor_repository.py     # Implementation Supabase
│   │       └── invoice_repository.py    # Implementation Supabase
│   │
│   └── interface/                 # API HTTP
│       ├── __init__.py
│       ├── routers/
│       │   ├── __init__.py
│       │   ├── machines.py
│       │   ├── predictions.py
│       │   ├── billing.py
│       │   ├── recommendations.py
│       │   ├── chat.py
│       │   └── admin.py
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── machine.py         # Pydantic DTOs
│       │   ├── prediction.py
│       │   ├── billing.py
│       │   └── chat.py
│       └── middleware/
│           ├── auth.py            # JWT verification
│           ├── rate_limit.py      # SlowAPI
│           └── logging.py         # Request ID
│
├── tests/
│   ├── __init__.py
│   ├── unit/                      # Tests unitaires (domain)
│   ├── integration/               # Tests API + DB
│   └── fixtures/                  # Donnees de test
│
├── scripts/
│   ├── generate_data.py
│   ├── train_xgboost.py
│   ├── train_anomaly.py
│   └── seed_database.py
│
├── notebooks/                     # Exploration ML
│   └── eda_consumption.ipynb
│
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── .env.example
├── .env
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
├── alembic.ini                    # Migrations DB
└── README.md
```

---

## 3. STACK TECHNIQUE COMPLETE

### Core
| Tech | Version | Role |
|------|---------|------|
| Python | 3.11+ | Langage |
| FastAPI | 0.110+ | Framework API |
| Uvicorn | 0.27+ | Serveur ASGI |
| Pydantic | 2.6+ | Validation + Settings |
| Pydantic-Settings | 2.2+ | Gestion .env |

### Base de donnees & Cache
| Tech | Version | Role |
|------|---------|------|
| Supabase-py | 2.4+ | Client PostgreSQL |
| SQLAlchemy | 2.0+ | ORM (optionnel, pour migrations) |
| Alembic | 1.13+ | Migrations schema |
| psycopg2-binary | 2.9+ | Driver PostgreSQL |
| Redis | 7.x | Cache predictions + rate limiting |

### Machine Learning
| Tech | Version | Role |
|------|---------|------|
| XGBoost | 2.0+ | Prediction consommation |
| Scikit-learn | 1.4+ | Isolation Forest + preprocessing |
| Pandas | 2.2+ | Data manipulation |
| NumPy | 1.26+ | Calculs numeriques |
| Joblib | 1.3+ | Serialisation modeles |

### IA & Chatbot
| Tech | Version | Role |
|------|---------|------|
| Google Generative AI | 0.7+ | Client Gemini Flash |

### Securite & Performance
| Tech | Version | Role |
|------|---------|------|
| python-jose | 3.3+ | JWT tokens |
| passlib | 1.7+ | Hashing |
| slowapi | 0.1+ | Rate limiting |
| python-multipart | 0.0.9 | Upload fichiers |

### Tests & Qualite
| Tech | Version | Role |
|------|---------|------|
| pytest | 8.0+ | Tests |
| pytest-asyncio | 0.23+ | Tests async |
| httpx | 0.27+ | Client HTTP test |
| coverage | 7.4+ | Couverture code |
| black | 24.x | Formatage |
| ruff | 0.3+ | Linting |
| mypy | 1.9+ | Typage statique |

### Monitoring & Logging
| Tech | Version | Role |
|------|---------|------|
| structlog | 24.x | Logging structure JSON |
| prometheus-client | 0.20+ | Metriques |
| sentry-sdk | 1.40+ | Error tracking |

---

## 4. FICHIER requirements.txt PRODUCTION

```
# Core
fastapi==0.110.0
uvicorn[standard]==0.27.1
pydantic==2.6.4
pydantic-settings==2.2.1
python-dotenv==1.0.1

# Database
supabase==2.4.0
sqlalchemy==2.0.28
alembic==1.13.1
psycopg2-binary==2.9.9

# Cache
redis==5.0.3

# ML / Data Science
xgboost==2.0.3
scikit-learn==1.4.1
pandas==2.2.1
numpy==1.26.4
joblib==1.3.2

# AI / LLM
google-generativeai==0.7.0

# Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
slowapi==0.1.9
python-multipart==0.0.9

# Monitoring / Logging
structlog==24.1.0
prometheus-client==0.20.0
sentry-sdk[fastapi]==1.40.6

# Utils
httpx==0.27.0
python-dateutil==2.9.0
```

---

## 5. FICHIER requirements-dev.txt

```
-r requirements.txt

# Testing
pytest==8.1.1
pytest-asyncio==0.23.5
pytest-cov==4.1.0
factory-boy==3.3.0

# Quality
black==24.3.0
ruff==0.3.4
mypy==1.9.0
pre-commit==3.6.2

# Dev tools
ipython==8.22.2
jupyter==1.0.0
```

---

## 6. CONFIGURATION PYDANTIC (config.py)

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API
    APP_NAME: str = "NouanKanyAI API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Supabase
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str
    SUPABASE_ANON_KEY: str

    # Google Gemini
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # Redis (optionnel)
    REDIS_URL: str = "redis://localhost:6379/0"

    # ML
    MODELS_PATH: str = "./app/infrastructure/ml/models"

    # CIE
    CIE_TARIFFS_PATH: str = "./app/infrastructure/external/cie_tariffs.json"

    # Commission NouanKanyAI
    COMMISSION_RATE: float = 0.10  # 10%

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

---

## 7. POINT D'ENTREE FASTAPI (main.py)

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.interface.routers import machines, predictions, billing, recommendations, chat, admin
from app.infrastructure.db.supabase_client import init_supabase
import structlog

logger = structlog.get_logger()
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting NouanKanyAI Backend", version=settings.APP_VERSION)
    await init_supabase()
    yield
    # Shutdown
    logger.info("Shutting down")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API de gestion energetique intelligente - Cote d'Ivoire",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS - A restreindre en production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://votre-domaine.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(machines.router, prefix=settings.API_V1_PREFIX, tags=["machines"])
app.include_router(predictions.router, prefix=settings.API_V1_PREFIX, tags=["predictions"])
app.include_router(billing.router, prefix=settings.API_V1_PREFIX, tags=["billing"])
app.include_router(recommendations.router, prefix=settings.API_V1_PREFIX, tags=["recommendations"])
app.include_router(chat.router, prefix=settings.API_V1_PREFIX, tags=["chat"])
app.include_router(admin.router, prefix=settings.API_V1_PREFIX, tags=["admin"])

@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "region": "CIV",
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "nouankanyai-backend"}
```

---

## 8. AUTHENTIFICATION JWT (middleware/auth.py)

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from app.config import get_settings

security = HTTPBearer()
settings = get_settings()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

async def get_current_user(token_data: dict = Depends(verify_token)) -> dict:
    return token_data
```

Note : Le token JWT vient du frontend (Supabase Auth). Vous verifiez juste la signature avec le meme SECRET_KEY.

---

## 9. CALCULATEUR CIE (domain/services/cie_calculator.py)

```python
import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class CIETranche:
    name: str
    min_kwh: float
    max_kwh: float
    price_per_kwh: float  # FCFA

class CIECalculator:
    TRANCHES: List[CIETranche] = [
        CIETranche("Sociale", 0, 80, 36.0),
        CIETranche("Domestique", 81, 150, 46.0),
        CIETranche("Non Domestique", 151, 500, 68.0),
        CIETranche("Professionnelle", 501, float('inf'), 96.0),
    ]

    def calculate_bill(self, total_kwh: float) -> dict:
        detail = []
        remaining = total_kwh
        total_amount = 0.0

        for tranche in self.TRANCHES:
            if remaining <= 0:
                break

            tranche_kwh = min(remaining, tranche.max_kwh - tranche.min_kwh + 1)
            tranche_amount = tranche_kwh * tranche.price_per_kwh

            detail.append({
                "tranche": tranche.name,
                "kwh": tranche_kwh,
                "price_per_kwh": tranche.price_per_kwh,
                "amount": tranche_amount,
            })

            total_amount += tranche_amount
            remaining -= tranche_kwh

        return {
            "total_kwh": total_kwh,
            "total_amount_fcfa": round(total_amount, 2),
            "detail_by_tranche": detail,
            "currency": "XOF",
        }

    def estimate_monthly_bill(self, average_daily_kwh: float) -> dict:
        monthly_kwh = average_daily_kwh * 30
        return self.calculate_bill(monthly_kwh)

    def detect_tranche_risk(self, current_monthly_kwh: float, projected_kwh: float) -> dict:
        current_tranche = self._get_tranche(current_monthly_kwh)
        projected_tranche = self._get_tranche(projected_kwh)

        risk = {
            "risk_detected": current_tranche != projected_tranche,
            "current_tranche": current_tranche,
            "projected_tranche": projected_tranche,
            "days_until_threshold": None,
        }

        if current_tranche != projected_tranche:
            threshold = self._get_threshold(projected_tranche)
            daily_rate = current_monthly_kwh / 30
            remaining = threshold - current_monthly_kwh
            if daily_rate > 0:
                risk["days_until_threshold"] = max(0, int(remaining / daily_rate))

        return risk

    def _get_tranche(self, kwh: float) -> str:
        for t in self.TRANCHES:
            if t.min_kwh <= kwh <= t.max_kwh:
                return t.name
        return "Professionnelle"

    def _get_threshold(self, tranche_name: str) -> float:
        for t in self.TRANCHES:
            if t.name == tranche_name:
                return t.min_kwh
        return 501.0
```

---

## 10. GAIN-SHARE CALCULATOR (domain/services/gain_share_calculator.py)

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class GainShareResult:
    raw_savings_fcfa: float
    commission_rate: float
    commission_fcfa: float
    client_net_savings_fcfa: float
    confidence_score: float

class GainShareCalculator:
    def __init__(self, commission_rate: float = 0.10):
        self.commission_rate = commission_rate

    def calculate(
        self,
        baseline_consumption_kwh: float,
        optimized_consumption_kwh: float,
        cie_calculator,
        confidence_score: float = 0.85,
    ) -> GainShareResult:
        baseline_bill = cie_calculator.calculate_bill(baseline_consumption_kwh)
        optimized_bill = cie_calculator.calculate_bill(optimized_consumption_kwh)

        raw_savings = baseline_bill["total_amount_fcfa"] - optimized_bill["total_amount_fcfa"]

        if raw_savings <= 0:
            return GainShareResult(
                raw_savings_fcfa=0.0,
                commission_rate=self.commission_rate,
                commission_fcfa=0.0,
                client_net_savings_fcfa=0.0,
                confidence_score=confidence_score,
            )

        commission = raw_savings * self.commission_rate
        client_net = raw_savings - commission

        return GainShareResult(
            raw_savings_fcfa=round(raw_savings, 2),
            commission_rate=self.commission_rate,
            commission_fcfa=round(commission, 2),
            client_net_savings_fcfa=round(client_net, 2),
            confidence_score=confidence_score,
        )
```

---

## 11. ROUTER MACHINES (interface/routers/machines.py)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.interface.schemas.machine import MachineCreate, MachineResponse
from app.interface.middleware.auth import get_current_user
from app.infrastructure.persistence.machine_repository import SupabaseMachineRepository

router = APIRouter(prefix="/machines")

@router.get("/", response_model=List[MachineResponse])
async def list_machines(
    current_user: dict = Depends(get_current_user),
    repo: SupabaseMachineRepository = Depends(),
):
    user_id = current_user.get("sub")
    machines = await repo.get_by_user_id(user_id)
    return machines

@router.post("/", response_model=MachineResponse, status_code=status.HTTP_201_CREATED)
async def create_machine(
    machine: MachineCreate,
    current_user: dict = Depends(get_current_user),
    repo: SupabaseMachineRepository = Depends(),
):
    user_id = current_user.get("sub")
    created = await repo.create(machine.dict(), user_id)
    return created

@router.post("/{machine_id}/simulate")
async def simulate_anomaly(
    machine_id: str,
    current_user: dict = Depends(get_current_user),
):
    return {"status": "anomaly_triggered", "machine_id": machine_id}
```

---

## 12. SCHEMAS PYDANTIC (interface/schemas/machine.py)

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class MachineStatus(str, Enum):
    ACTIVE = "active"
    ALERT = "alert"
    OFFLINE = "offline"

class MachineCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, example="Clim Hall Principal")
    power_rating_kw: float = Field(..., gt=0, example=5.5)
    quantity: int = Field(default=1, ge=1)
    location: Optional[str] = Field(None, example="Rez-de-chaussee")
    priority: str = Field(default="medium", example="high")

class MachineResponse(BaseModel):
    id: str
    name: str
    power_rating_kw: float
    quantity: int
    status: MachineStatus
    location: Optional[str]
    priority: str
    current_power_kw: Optional[float]
    current_temperature_c: Optional[float]
    current_vibration_hz: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True
```

---

## 13. DOCKERFILE PRODUCTION

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Installation des dependances systeme
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application
COPY app/ ./app/
COPY scripts/ ./scripts/

# Modeles ML (si presents)
COPY app/infrastructure/ml/models/ ./app/infrastructure/ml/models/

# Non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

---

## 14. DOCKER-COMPOSE (developpement local)

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./app:/app/app
      - ./scripts:/app/scripts
    depends_on:
      - redis
      - db
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: nouankanyai
      POSTGRES_PASSWORD: devpassword
      POSTGRES_DB: nouankanyai_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## 15. PYTEST CONFIGURATION (pytest.ini)

```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    unit: Tests unitaires rapides
    integration: Tests necessitant la base de donnees
    slow: Tests lents (ML, entrainement)
```

---

## 16. PRE-COMMIT CONFIG (.pre-commit-config.yaml)

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 24.3.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.4
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.9.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

---

## 17. CHECKLIST DE MISE EN PLACE (Etapes concretes)

### Etape 0 : Prerequis
- [ ] Python 3.11+ installe
- [ ] Docker + Docker Compose installes
- [ ] Compte Supabase cree (projet configure)
- [ ] Cle API Gemini obtenue
- [ ] Git configure

### Etape 1 : Structure initiale
```bash
mkdir -p backend/{app/{domain/{entities,repositories,services},application/{machines,predictions,billing,recommendations,chat},infrastructure/{db,ml/models,external,persistence},interface/{routers,schemas,middleware}},tests/{unit,integration,fixtures},scripts,notebooks,docker}
```

### Etape 2 : Environnement virtuel
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Etape 3 : Variables d'environnement
```bash
cp .env.example .env
# Editer .env avec vos vraies cles
```

### Etape 4 : Base de donnees Supabase
- Creer les tables : machines, sensor_metrics, sites, audit_logs, invoices, predictions_history
- Activer Row Level Security (RLS) sur chaque table
- Creer les policies : user_id = auth.uid()

### Etape 5 : Generation des donnees & Entrainement ML
```bash
python scripts/generate_data.py
python scripts/train_xgboost.py
python scripts/train_anomaly.py
```

### Etape 6 : Lancement local
```bash
# Avec Docker
 docker-compose up --build

# Ou directement
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Etape 7 : Tests
```bash
pytest tests/unit/ -v
pytest tests/integration/ -v --cov=app --cov-report=html
```

### Etape 8 : Pre-commit
```bash
pre-commit install
pre-commit run --all-files
```

### Etape 9 : Deploiement Render
- Creer un Blueprint render.yaml
- Configurer les variables d'environnement sur Render
- Deployer

---

## 18. BONNES PRATIQUES CRITIQUES

### A. Securite
1. Jamais de cle API en dur dans le code
2. Jamais committer le fichier .env
3. Toujours valider le JWT Supabase cote backend
4. Row Level Security active sur TOUTES les tables Supabase
5. Rate limiting : 100 req/min par IP, 1000 req/min par user
6. Sanitiser toutes les entrees

### B. Performance
1. Cache Redis pour les predictions XGBoost (TTL 5 minutes)
2. Pagination sur tous les endpoints list (default 20, max 100)
3. Async partout : FastAPI est async, Supabase-py est async
4. Lazy loading des modeles ML : chargez les .pkl au startup
5. Connection pooling : Supabase gere ca, mais verifier les limites

### C. Monitoring
1. Structured logging (JSON) pour Render/Datadog
2. Health check endpoint /health utilise par Render
3. Sentry pour le tracking d'erreurs
4. Prometheus metrics : nombre de predictions, temps de reponse, taux d'erreur

### D. ML Ops (minimaliste mais propre)
1. Versionner les modeles .pkl avec Git LFS
2. Logger les metriques d'entrainement (R2, MAPE)
3. Stocker les predictions vs realite pour mesurer le drift
4. Endpoint /api/v1/admin/retrain protege (admin uniquement)

### E. Contexte Ivoirien
1. Devise : toujours XOF/FCFA, jamais USD en interne
2. Fuseau horaire : Africa/Abidjan (UTC+0)
3. Langue : API en francais, codes d'erreur en francais
4. Grille CIE : versionner le JSON des tarifs (ils changent ~1x/an)
5. Reseau : prevoir un mode "offline" ou cache agressif

---

## 19. SCHEMA DE BASE DE DONNEES SUPABASE (SQL)

```sql
-- Table : machines
CREATE TABLE machines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    site_id UUID REFERENCES sites(id),
    name TEXT NOT NULL,
    power_rating_kw FLOAT NOT NULL,
    quantity INTEGER DEFAULT 1,
    location TEXT,
    priority TEXT DEFAULT 'medium',
    status TEXT DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table : sensor_metrics (partitionnable par date)
CREATE TABLE sensor_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    machine_id UUID REFERENCES machines(id) ON DELETE CASCADE,
    power_kw FLOAT,
    temperature_c FLOAT,
    vibration_hz FLOAT,
    pressure_bar FLOAT,
    recorded_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index pour performance
CREATE INDEX idx_sensor_metrics_machine_time ON sensor_metrics(machine_id, recorded_at DESC);

-- Table : sites
CREATE TABLE sites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    address TEXT,
    city TEXT,
    country TEXT DEFAULT 'CI',
    cie_account_number TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table : audit_logs (append-only)
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    action TEXT NOT NULL,
    entity_type TEXT,
    entity_id UUID,
    ref_hash TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table : invoices
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id),
    site_id UUID REFERENCES sites(id),
    month DATE NOT NULL,
    baseline_consumption_kwh FLOAT,
    optimized_consumption_kwh FLOAT,
    raw_savings_fcfa FLOAT,
    commission_fcfa FLOAT,
    client_net_savings_fcfa FLOAT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table : predictions_history (pour drift monitoring)
CREATE TABLE predictions_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    machine_id UUID REFERENCES machines(id),
    predicted_value FLOAT,
    actual_value FLOAT,
    horizon_hours INTEGER,
    model_version TEXT,
    mape_error FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Row Level Security (CRITIQUE)
ALTER TABLE machines ENABLE ROW LEVEL SECURITY;
ALTER TABLE sensor_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE sites ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can only see their own machines" ON machines
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can only see their own sites" ON sites
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can only see their own invoices" ON invoices
    FOR ALL USING (auth.uid() = user_id);
```

---

## 20. RENDER BLUEPRINT (render.yaml)

```yaml
services:
  - type: web
    name: nouankanyai-api
    runtime: docker
    plan: standard
    branch: main
    dockerfilePath: ./docker/Dockerfile
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_SERVICE_ROLE_KEY
        sync: false
      - key: GEMINI_API_KEY
        sync: false
      - key: SECRET_KEY
        generateValue: true
    healthCheckPath: /health
    autoDeploy: true

  - type: redis
    name: nouankanyai-redis
    plan: starter
    ipAllowList: []
```

---

## 21. PLAN DE TESTS

### Tests Unitaires (domain)
- test_cie_calculator.py : Verifier chaque tranche, cas limites (80, 81, 150, 151, 500, 501 kWh)
- test_gain_share_calculator.py : Verifier 10%, cas sans economie
- test_anomaly_detector.py : Mock du modele Isolation Forest

### Tests d'Integration (API + DB)
- test_machines_api.py : CRUD complet avec auth
- test_predictions_api.py : Verifier que XGBoost retourne un float
- test_billing_api.py : Verifier le calcul CIE + commission

### Tests de Charge (optionnel)
```bash
locust -f locustfile.py --host=http://localhost:8000
```

---

## 22. ROADMAP BACKEND (12 semaines)

| Semaine | Objectif | Livrable |
|---------|----------|----------|
| 1-2 | Architecture + Setup | Structure clean, Docker, CI |
| 3-4 | Auth + CRUD machines | JWT, RLS, tests unitaires |
| 5-6 | ML Pipeline | XGBoost + Isolation Forest integres |
| 7-8 | CIE + Billing | Calculateur tarifaire, Gain-Share, factures |
| 9-10 | Chatbot + Recommandations | Gemini integration, moteur de regles |
| 11 | Admin + Monitoring | Dashboard MLOps, Sentry, metriques |
| 12 | Optimisation + Deploiement | Cache Redis, load testing, Render |

---

Document genere pour NouanKanyAI - Lead Backend - Cote d'Ivoire
Version 1.0 - 2026
