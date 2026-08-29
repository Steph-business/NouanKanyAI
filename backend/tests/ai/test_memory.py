"""
backend/tests/ai/test_memory.py — Tests unitaires et d'intégration pour le sous-système de mémoire conversationnelle.
"""

import pytest
from app.ai import (
    ConversationMemoryManager,
    ConversationBufferMemory,
    SummaryMemory,
    UserPreferences,
    RecommendationRecord,
    ConfirmedActionRecord,
    LongTermEntityMemory,
    IndustrialCopilot,
    AIResponse,
)


class TestConversationMemorySuite:
    """Suite de tests pour la mémoire multi-niveaux et multi-tenant."""

    def test_entity_key_generation(self):
        """Vérifie la génération standardisée des clés hiérarchiques."""
        key = ConversationMemoryManager.build_entity_key(
            org_id="cie_industry", building_id="usine_nord", user_id="ing_koffi"
        )
        assert key == "cie_industry:usine_nord:ing_koffi"

        default_key = ConversationMemoryManager.build_entity_key()
        assert default_key == "default_org:default_building:default_user"

    def test_short_term_and_long_term_creation(self):
        """Vérifie la création et l'isolation des mémoires courtes et longues."""
        manager = ConversationMemoryManager(short_term_max_messages=6)
        
        short = manager.get_or_create_short_term("sess-1", user_id="user-1", org_id="org-1")
        assert short.session_id == "sess-1"
        assert len(short.messages) == 0

        long_mem = manager.get_or_create_long_term(org_id="org-1", building_id="bldg-1", user_id="user-1")
        assert isinstance(long_mem, LongTermEntityMemory)
        assert long_mem.org_id == "org-1"
        assert len(long_mem.tracked_equipments) == 0

    def test_add_turn_and_auto_summarization(self):
        """Vérifie l'enregistrement des tours et le déclenchement automatique du résumé."""
        manager = ConversationMemoryManager(short_term_max_messages=4)
        session_id = "session-overflow"
        org_id = "org-test"
        user_id = "user-test"

        # Tour 1 (2 messages)
        manager.add_turn(session_id, "Quel est l'état du Compresseur 1 ?", "Il fonctionne à 35 kW.", org_id=org_id, user_id=user_id)
        # Tour 2 (2 messages -> total 4 messages)
        manager.add_turn(session_id, "Faut-il couper le Four 2 ?", "Non, la température est stable.", org_id=org_id, user_id=user_id)

        short = manager.get_or_create_short_term(session_id)
        assert len(short.messages) == 4

        # Tour 3 (2 messages -> dépassement de 4 -> déclenchement du résumé)
        manager.add_turn(session_id, "Combien coûte l'heure de pointe ?", "Le tarif est de 145 FCFA/kWh.", org_id=org_id, user_id=user_id)

        assert len(short.messages) <= 4
        long_mem = manager.get_or_create_long_term(org_id=org_id, user_id=user_id)
        assert len(long_mem.conversation_summaries) >= 1
        assert "Échanges précédents" in long_mem.conversation_summaries[0]

    def test_user_preferences_update(self):
        """Vérifie la mise à jour des préférences opérationnelles."""
        manager = ConversationMemoryManager()
        prefs = UserPreferences(
            currency="FCFA",
            energy_alert_threshold_kw=150.0,
            preferred_tariff_schedule="CIE_INDUSTRIEL",
            auto_delestage_allowed=True,
        )
        manager.update_preferences(prefs, org_id="org_ci", user_id="op_1")

        long_mem = manager.get_or_create_long_term(org_id="org_ci", user_id="op_1")
        assert long_mem.preferences.energy_alert_threshold_kw == 150.0
        assert long_mem.preferences.preferred_tariff_schedule == "CIE_INDUSTRIEL"
        assert long_mem.preferences.auto_delestage_allowed is True

    def test_tracked_equipments_lifecycle(self):
        """Vérifie l'ajout, le dédoublonnage et le retrait d'équipements suivis."""
        manager = ConversationMemoryManager()
        org = "agro_ci"
        bldg = "hangar_a"

        equipments = manager.add_tracked_equipment(["Compresseur C1", "Four F2", "Compresseur C1"], org_id=org, building_id=bldg)
        assert len(equipments) == 2
        assert "Compresseur C1" in equipments
        assert "Four F2" in equipments

        # Retrait
        removed = manager.remove_tracked_equipment("Four F2", org_id=org, building_id=bldg)
        assert removed is True
        assert "Four F2" not in manager.get_or_create_long_term(org_id=org, building_id=bldg).tracked_equipments

    def test_recommendation_and_action_confirmation(self):
        """Vérifie l'enregistrement des recommandations et le calcul cumulatif des économies réelles."""
        manager = ConversationMemoryManager()
        org = "cimenterie"
        user = "directeur_prod"

        # Enregistrement d'une recommandation
        rec = manager.record_recommendation(
            title="Délestage Broyeur 1",
            description="Arrêt pendant la pointe CIE 19h-23h",
            target_machine="Broyeur B1",
            estimated_savings_fcfa=58000.0,
            estimated_savings_kwh=400.0,
            org_id=org,
            user_id=user,
        )
        assert rec.estimated_savings_fcfa == 58000.0

        # Confirmation d'action
        act = manager.confirm_action(
            action_type="shed_load",
            user_id=user,
            machine_id="Broyeur B1",
            details={"hour": 19, "duration_h": 4},
            realized_savings_fcfa=58000.0,
            realized_savings_kwh=400.0,
            org_id=org,
        )
        assert act.realized_savings_fcfa == 58000.0

        long_mem = manager.get_or_create_long_term(org_id=org, user_id=user)
        assert long_mem.cumulative_savings_fcfa == 58000.0
        assert long_mem.cumulative_savings_kwh == 400.0
        assert len(long_mem.confirmed_actions) == 1

    def test_relevant_context_formatting_for_prompt(self):
        """Vérifie la production du bloc Markdown de mémoire pour le PromptBuilder."""
        manager = ConversationMemoryManager()
        org = "usine_abidjan"
        user = "chef_equipe"

        manager.add_tracked_equipment(["Ligne d'Extrusion E1"], org_id=org, user_id=user)
        manager.confirm_action(
            action_type="eco_mode",
            user_id=user,
            machine_id="Ligne d'Extrusion E1",
            realized_savings_fcfa=25000.0,
            realized_savings_kwh=180.0,
            org_id=org,
        )

        prompt_ctx = manager.get_relevant_context_for_prompt(org_id=org, user_id=user)
        assert "[MÉMOIRE & HISTORIQUE DU SITE]" in prompt_ctx
        assert "Ligne d'Extrusion E1" in prompt_ctx
        assert "25,000 FCFA" in prompt_ctx

    def test_copilot_memory_integration(self):
        """Vérifie que le Copilot utilise la mémoire pour enrichir ses réponses."""
        manager = ConversationMemoryManager()
        org = "site_zone4"
        user = "ing_amadou"

        manager.add_tracked_equipment(["Presse P100"], org_id=org, user_id=user)
        copilot = IndustrialCopilot(memory_manager=manager)

        res = copilot.ask(
            query="Quel équipement dois-je surveiller en priorité ?",
            session_id="session-mem-1",
            org_id=org,
            user_id=user,
        )
        assert isinstance(res, AIResponse)
        assert len(res.content) > 0

        # Vérifier que le tour a été enregistré dans le manager
        short = manager.get_or_create_short_term("session-mem-1")
        assert len(short.messages) == 2
