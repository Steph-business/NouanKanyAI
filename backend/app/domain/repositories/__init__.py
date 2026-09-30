"""Contrats abstraits de persistance requis par le domaine."""

from app.domain.repositories.machine_repository import MachineRepository
from app.domain.repositories.reading_repository import ReadingRepository

__all__ = ["MachineRepository", "ReadingRepository"]
