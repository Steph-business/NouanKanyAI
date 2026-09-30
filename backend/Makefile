.PHONY: help setup dev test lint format clean

VENV_PYTHON = .venv/Scripts/python.exe
PYTHON ?= $(VENV_PYTHON)
BOOTSTRAP_PYTHON ?= python
LINT_IMPORTS = .venv/Scripts/lint-imports.exe

help: ## Affiche les commandes disponibles
	@$(PYTHON) -c "print('help    Affiche les commandes disponibles\nsetup   Crée le venv et installe les dépendances\ndev     Lance FastAPI\ntest    Lance pytest\nlint    Lance Ruff, mypy et lint-imports\nformat  Formate le code avec Ruff\nclean   Supprime les caches générés')"

setup: ## Crée le venv et installe les dépendances
	$(BOOTSTRAP_PYTHON) -m venv .venv
	$(VENV_PYTHON) -m pip install -r requirements.txt -r requirements-dev.txt
	$(VENV_PYTHON) -m pre_commit install

dev: ## Lance le serveur en mode développement
	$(PYTHON) main.py

test: ## Lance les tests backend avec couverture
	$(PYTHON) -m pytest -v

lint: ## Vérifie le style, le typage et les frontières d'import
	$(PYTHON) -m ruff check app/
	$(PYTHON) -m mypy app/
	$(LINT_IMPORTS)

format: ## Formate et corrige les imports Python
	$(PYTHON) -m ruff format app/
	$(PYTHON) -m ruff check --fix app/

clean: ## Supprime les caches Python et de couverture générés
	$(PYTHON) -c "import pathlib, shutil; roots=['.pytest_cache','.mypy_cache','.ruff_cache','htmlcov']; [shutil.rmtree(p, ignore_errors=True) for p in roots]; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('app').rglob('__pycache__')]; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('tests').rglob('__pycache__')]"
