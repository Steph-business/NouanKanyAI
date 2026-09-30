"""Port de génération de rapports sans dépendance aux formats d'export."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class GeneratedReport:
    """Contenu d'un rapport produit, avec son nom et son type MIME."""

    filename: str
    content: bytes
    media_type: str


class ReportService(ABC):
    """Contrat d'accès à un générateur de rapport concret."""

    @abstractmethod
    async def generate(
        self, report_type: str, export_format: str, site_name: str, building_type: str
    ) -> GeneratedReport:
        """Produit un rapport pour un site et un format demandés."""
        raise NotImplementedError
