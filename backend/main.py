"""Point d'entrée ASGI conservé pour `python main.py` et `uvicorn main:app`."""

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.presentation import legacy_app
from app.config.settings import settings

app = legacy_app.app
__all__ = ["app"]

# Preserve historical `backend.main` monkeypatch/import behavior for existing tests and callers.
if __name__ != "__main__":
    sys.modules[__name__] = legacy_app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
