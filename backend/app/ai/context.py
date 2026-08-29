"""
app/ai/context.py — Constructeur de contexte industriel temps réel pour le Copilot.

Formate et injecte les données d'équipements industriels (état de fonctionnement,
puissance active, température, alertes actives, tranches tarifaires CIE) dans le prompt du LLM.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class IndustrialContextBuilder:
    """
    Assembleur de contexte opérationnel industriel pour l'assistant IA.
    """

    @staticmethod
    def format_machines_context(machines: List[Dict[str, Any]]) -> str:
        """
        Formate la liste des équipements et leur état télémétrique.

        :param machines: Liste de dictionnaires d'équipements.
        :return: Bloc textuel formaté.
        """
        if not machines:
            return "Aucun équipement renseigné dans le système."

        lines = ["#### État des Équipements de Production :"]
        for m in machines:
            name = m.get("name", m.get("id", "Machine"))
            status = m.get("status", "inconnu")
            power = m.get("power_kw", m.get("current_power_kw", "N/A"))
            temp = m.get("temperature_c", "N/A")
            vibr = m.get("vibration_hz", "N/A")
            lines.append(
                f"- **{name}** : Statut={status} | Puissance={power} kW | "
                f"Temp={temp}°C | Vibration={vibr} Hz"
            )
        return "\n".join(lines)

    @staticmethod
    def format_alerts_context(alerts: List[Dict[str, Any]]) -> str:
        """
        Formate les alertes actives et dérives détectées.

        :param alerts: Liste des alertes récentes.
        :return: Bloc textuel des alertes.
        """
        if not alerts:
            return "Aucune alerte active signalée (fonctionnement normal)."

        lines = ["#### Alertes et Anomalies Récentes :"]
        for a in alerts:
            sev = a.get("severity", "info").upper()
            msg = a.get("message", a.get("description", "Alerte"))
            time_str = a.get("timestamp", "récent")
            lines.append(f"- [{sev}] {msg} ({time_str})")
        return "\n".join(lines)

    @staticmethod
    def format_tariff_context(
        current_hour: Optional[int] = None,
        base_rate_fcfa: float = 85.0,
        peak_rate_fcfa: float = 145.0,
        off_peak_rate_fcfa: float = 55.0,
    ) -> str:
        """
        Formate la situation tarifaire CIE actuelle.

        :param current_hour: Heure actuelle (0-23).
        :param base_rate_fcfa: Tarif heures pleines.
        :param peak_rate_fcfa: Tarif heures de pointe (19h-23h).
        :param off_peak_rate_fcfa: Tarif heures creuses (23h-07h).
        :return: Synthèse tarifaire.
        """
        hour = current_hour if current_hour is not None else datetime.now(timezone.utc).hour
        is_peak = (19 <= hour <= 23)
        is_off_peak = (hour < 7 or hour >= 23)

        if is_peak:
            current_band = "HEURE DE POINTE (19h-23h)"
            active_price = peak_rate_fcfa
        elif is_off_peak:
            current_band = "HEURE CREUSE (23h-07h)"
            active_price = off_peak_rate_fcfa
        else:
            current_band = "HEURE PLEINE (07h-19h)"
            active_price = base_rate_fcfa

        return (
            f"#### Grille Tarifaire CIE Actuelle (Heure {hour:02d}h00) :\n"
            f"- **Tranche en cours** : {current_band}\n"
            f"- **Tarif actif** : {active_price:.2f} FCFA / kWh\n"
            f"- Grille de référence : Heures Pleines ({base_rate_fcfa} FCFA), "
            f"Heures de Pointe ({peak_rate_fcfa} FCFA), Heures Creuses ({off_peak_rate_fcfa} FCFA)."
        )

    def build_full_context(
        self,
        machines: Optional[List[Dict[str, Any]]] = None,
        alerts: Optional[List[Dict[str, Any]]] = None,
        current_hour: Optional[int] = None,
        custom_notes: Optional[str] = None,
    ) -> str:
        """
        Construit l'intégralité du bloc de contexte industriel temps réel.

        :param machines: Données des machines.
        :param alerts: Données des alertes.
        :param current_hour: Heure d'analyse.
        :param custom_notes: Notes d'exploitation additionnelles.
        :return: Texte complet du contexte industriel.
        """
        blocks = [
            self.format_tariff_context(current_hour=current_hour),
            self.format_machines_context(machines or []),
            self.format_alerts_context(alerts or []),
        ]
        if custom_notes:
            blocks.append(f"#### Notes de Poste :\n{custom_notes}")

        return "\n\n".join(blocks)
