"""
backend/tests/ai/test_dynamic_prompt.py — Tests unitaires pour le constructeur dynamique de prompts Jinja2/YAML.
"""

import pytest
from app.ai import (
    PromptBuilder,
    PromptContext,
    UserRole,
    BuildingType,
    MLContext,
    ChatMessage,
    MessageRole,
    DocumentChunk,
)


class TestDynamicPromptBuilderSuite:
    """Suite de tests pour le constructeur dynamique de prompts."""

    def test_yaml_config_loading_and_supported_lists(self):
        """Vérifie le chargement des configurations YAML de rôles et de bâtiments."""
        builder = PromptBuilder()
        roles = builder.get_supported_roles()
        assert len(roles) >= 5
        assert "energy_manager" in roles
        assert "plant_director" in roles
        assert "hotel_manager" in roles

        buildings = builder.get_supported_building_types()
        assert len(buildings) >= 4
        assert "industry" in buildings
        assert "hotel" in buildings
        assert "restaurant" in buildings
        assert "tertiaire" in buildings

    def test_system_prompt_generation_by_role_and_building(self):
        """Vérifie l'adaptation de l'instruction système selon le rôle et la typologie du site."""
        builder = PromptBuilder()

        # Test 1: Energy Manager dans l'Industrie
        ctx_industry = PromptContext(
            query="Comment optimiser ?",
            role=UserRole.ENERGY_MANAGER,
            building_type=BuildingType.INDUSTRY,
            language="fr",
            currency="FCFA",
        )
        sys_inst_1 = builder.build_system_instruction(context=ctx_industry)
        assert "Responsable Énergie" in sys_inst_1
        assert "Site Industriel" in sys_inst_1
        assert "19h-23h" in sys_inst_1
        assert "FCFA" in sys_inst_1

        # Test 2: Directeur d'Hôtel
        ctx_hotel = PromptContext(
            query="Comment réduire la facture des chambres ?",
            role=UserRole.HOTEL_MANAGER,
            building_type=BuildingType.HOTEL,
            language="fr",
        )
        sys_inst_2 = builder.build_system_instruction(context=ctx_hotel)
        assert "Complexe Hôtelier" in sys_inst_2
        assert "Hôtel" in sys_inst_2

        # Test 3: Restaurant
        ctx_resto = PromptContext(
            query="Gérer le froid",
            role=UserRole.RESTAURANT_OWNER,
            building_type=BuildingType.RESTAURANT,
        )
        sys_inst_3 = builder.build_system_instruction(context=ctx_resto)
        assert "Restaurant" in sys_inst_3

        # Test 4: Grand Ménage
        ctx_house = PromptContext(
            query="Mon climatiseur",
            role=UserRole.HOUSEHOLD_HEAD,
            building_type=BuildingType.GRAND_MENAGE,
        )
        sys_inst_4 = builder.build_system_instruction(context=ctx_house)
        assert "Grand Ménage" in sys_inst_4

    def test_user_prompt_with_ml_and_rag_context(self):
        """Vérifie l'injection des prévisions ML, anomalies et extraits documentaires."""
        builder = PromptBuilder()
        ml = MLContext(
            predicted_power_kw=82.45,
            forecasting_unit="kW",
            is_anomaly=True,
            anomaly_severity="critique",
            anomaly_probability=0.88,
        )
        rag_chunks = [
            DocumentChunk(
                document_id="guide-cie",
                content="En période de pointe (19h-23h), délester les compresseurs non prioritaires.",
                metadata={"source": "Guide CIE 2026"},
            )
        ]
        user_prompt = builder.format_user_prompt(
            query="Que faire face à cette alerte ?",
            industrial_context="Compresseur C1: 45 kW, Temp: 92°C",
            memory_context="Préférence: alerte > 100 kW",
            rag_context=rag_chunks,
            ml_context=ml,
        )

        assert "82.45 kW" in user_prompt
        assert "ANOMALIE DÉTECTÉE" in user_prompt
        assert "CRITIQUE" in user_prompt
        assert "88.0%" in user_prompt or "88%" in user_prompt
        assert "Guide CIE 2026" in user_prompt
        assert "Compresseur C1" in user_prompt
        assert "Préférence: alerte > 100 kW" in user_prompt

    def test_multi_provider_formatting(self):
        """Vérifie l'export adapté aux formats Gemini, OpenAI, Anthropic et Raw."""
        builder = PromptBuilder()
        messages = [
            ChatMessage(role=MessageRole.USER, content="Question utilisateur 1"),
            ChatMessage(role=MessageRole.ASSISTANT, content="Réponse assistant 1"),
            ChatMessage(role=MessageRole.USER, content="Question utilisateur 2"),
        ]
        system_inst = "Directive système test"

        # Format Gemini
        gemini_payload = builder.format_for_provider(messages, system_inst, provider="gemini")
        assert "contents" in gemini_payload
        assert len(gemini_payload["contents"]) == 3
        assert gemini_payload["contents"][0]["role"] == "user"
        assert gemini_payload["contents"][1]["role"] == "model"
        assert "systemInstruction" in gemini_payload

        # Format OpenAI
        openai_payload = builder.format_for_provider(messages, system_inst, provider="openai")
        assert "messages" in openai_payload
        assert len(openai_payload["messages"]) == 4
        assert openai_payload["messages"][0]["role"] == "system"
        assert openai_payload["messages"][1]["role"] == "user"
        assert openai_payload["messages"][2]["role"] == "assistant"

        # Format Anthropic
        anthropic_payload = builder.format_for_provider(messages, system_inst, provider="anthropic")
        assert "system" in anthropic_payload
        assert "messages" in anthropic_payload
        assert len(anthropic_payload["messages"]) == 3

        # Format Raw Text
        raw_payload = builder.format_for_provider(messages, system_inst, provider="raw_text")
        assert "[SYSTEM]" in raw_payload["prompt"]
        assert "[USER]" in raw_payload["prompt"]
        assert "[ASSISTANT]" in raw_payload["prompt"]

    def test_build_from_prompt_context_end_to_end(self):
        """Vérifie la méthode intégrée build_from_prompt_context."""
        builder = PromptBuilder()
        ctx = PromptContext(
            query="Analyser la facture",
            role=UserRole.PLANT_DIRECTOR,
            building_type=BuildingType.INDUSTRY,
            energy_context="Puissance active: 120 kW",
            additional_instructions=["Proposer un échéancier d'investissement solaire."],
        )
        sys_inst, chat_msgs = builder.build_from_prompt_context(ctx)

        assert "Directeur d'Usine" in sys_inst
        assert "investissement solaire" in sys_inst
        assert len(chat_msgs) == 1
        assert "Puissance active: 120 kW" in chat_msgs[0].content

    def test_custom_in_memory_template_registration(self):
        """Vérifie l'enregistrement et le rendu d'un template personnalisé en mémoire."""
        builder = PromptBuilder()
        custom_tpl = "Custom Prompt: {{ query | upper }} (Budget: {{ budget_fcfa | fcfa }})"
        builder.register_template("custom_alert.jinja2", custom_tpl)

        rendered = builder._jinja_env.get_template("custom_alert.jinja2").render(
            query="Alerte surchauffe", budget_fcfa=50000.0
        )
        assert "Custom Prompt: ALERTE SURCHAUFFE" in rendered
        assert "50 000 FCFA" in rendered
