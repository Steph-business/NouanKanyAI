"""
app/reports/exporters/base.py — Interface de base pour les exportateurs de rapports.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
from app.reports.models import EnergyReportData


class BaseReportExporter(ABC):
    """
    Interface abstraite pour tous les convertisseurs de format de rapport.
    """

    @abstractmethod
    def export(
        self,
        report_data: EnergyReportData,
        chart_images: Optional[Dict[str, bytes]] = None,
    ) -> bytes:
        """
        Génère le flux binaire du document (PDF, DOCX, XLSX, PPTX).

        :param report_data: Données métier du rapport.
        :param chart_images: Dictionnaire des graphiques pré-générés (PNG en octets).
        :return: Données binaires du fichier.
        """
        pass
