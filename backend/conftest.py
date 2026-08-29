"""
backend/conftest.py — Configuration pytest et fixtures partagées pour les tests du backend et ML.
"""

import sys
from pathlib import Path

# Ajouter backend et la racine au sys.path
backend_dir = Path(__file__).resolve().parent
project_root = backend_dir.parent

if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
