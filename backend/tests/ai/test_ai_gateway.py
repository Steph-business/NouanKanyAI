"""
backend/tests/ai/test_ai_gateway.py — Tests unitaires et d'intégration pour l'AI Gateway et l'assistant Copilot.
"""

import pytest
from app.ai import (
    AIGateway,
    IndustrialCopilot,
    PromptBuilder,
    IndustrialContextBuilder,
    ConversationManager,
    ToolRegistry,
    CalculateEnergyCostTool,
    MockEmbedder,
    GeminiEmbedder,
    InMemoryRetriever,
    ConversationBufferMemory,
    SummaryMemory,
    IndustrialRAGPipeline,
    DocumentChunk,
    ChatMessage,
    MessageRole,
    AIResponse,
)


class TestAIGatewaySuite:
    """Suite de tests pour la passerelle IA centrale."""

    def test_gateway_simulation_mode_nominal(self):
        """Vérifie le mode simulation de secours en l'absence de clé API."""
        gateway = AIGateway(api_key="")
        assert gateway.is_simulation_mode is True

        response = gateway.generate_text("Quel est l'état du compresseur A ?")
        assert isinstance(response, AIResponse)
        assert len(response.content) > 0
        assert "NouanKanyAI Copilot" in response.content
        assert response.latency_ms >= 0.0
        assert response.finish_reason == "STOP"

    def test_prompt_builder_structure(self):
        """Vérifie l'assemblage des directives système et des prompts enrichis."""
        builder = PromptBuilder()
        system_inst = builder.build_system_instruction(
            additional_guidelines=["Toujours proposer un plan d'effacement."],
            custom_context="Usine de conditionnement d'Abidjan.",
        )
        assert "NouanKanyAI Copilot" in system_inst
        assert "Toujours proposer un plan d'effacement" in system_inst
        assert "Abidjan" in system_inst

        user_prompt = builder.format_user_prompt(
            query="Comment réduire la facture en pointe ?",
            industrial_context="Machine 1: 45 kW",
            rag_context="Guide CIE 2026",
        )
        assert "[CONTEXTE INDUSTRIEL TEMPS RÉEL]" in user_prompt
        assert "Machine 1: 45 kW" in user_prompt
        assert "[DOCUMENTATION TECHNIQUE & PROCÉDURES]" in user_prompt
        assert "Guide CIE 2026" in user_prompt
        assert "[REQUÊTE DE L'UTILISATEUR]" in user_prompt

    def test_conversation_manager_sessions(self):
        """Vérifie la gestion et la persistance des sessions et de l'historique."""
        mgr = ConversationManager(max_messages_per_session=4)
        session = mgr.get_or_create_session("sess-001")
        assert session.session_id == "sess-001"

        mgr.add_message("sess-001", MessageRole.USER, "Message 1")
        mgr.add_message("sess-001", MessageRole.ASSISTANT, "Réponse 1")
        mgr.add_message("sess-001", MessageRole.USER, "Message 2")
        mgr.add_message("sess-001", MessageRole.ASSISTANT, "Réponse 2")
        mgr.add_message("sess-001", MessageRole.USER, "Message 3 (élagage)")

        history = mgr.get_history("sess-001")
        assert len(history) == 4
        assert history[-1].content == "Message 3 (élagage)"

        assert mgr.clear_session("sess-001") is True
        assert len(mgr.get_history("sess-001")) == 0

    def test_industrial_context_builder(self):
        """Vérifie le formatage des informations d'équipements, d'alertes et de tarif CIE."""
        builder = IndustrialContextBuilder()
        machines = [
            {"name": "Compresseur C1", "status": "running", "power_kw": 35.5, "temperature_c": 65.0, "vibration_hz": 12.0}
        ]
        alerts = [
            {"severity": "warning", "message": "Pic de vibration", "timestamp": "14h30"}
        ]
        ctx = builder.build_full_context(machines=machines, alerts=alerts, current_hour=20)
        
        assert "HEURE DE POINTE" in ctx
        assert "145.00 FCFA" in ctx
        assert "Compresseur C1" in ctx
        assert "Pic de vibration" in ctx

    def test_tool_registry_and_execution(self):
        """Vérifie l'enregistrement et l'exécution d'un outil métier."""
        registry = ToolRegistry()
        tool = CalculateEnergyCostTool()
        registry.register(tool)

        assert registry.get("calculate_energy_cost") is not None
        schemas = registry.get_gemini_schemas()
        assert len(schemas) == 1
        assert schemas[0]["name"] == "calculate_energy_cost"

        # Exécution de l'outil pour 100 kWh à 20h (heure de pointe CIE = 145 FCFA/kWh)
        result = registry.execute_tool("calculate_energy_cost", energy_kwh=100.0, hour=20)
        assert result["total_cost_fcfa"] == 14500.0
        assert result["tariff_name"] == "Heure de Pointe"

    def test_embeddings_and_retriever(self):
        """Vérifie le fonctionnement du calcul d'embeddings et de la recherche documentaire."""
        embedder = MockEmbedder(dimension=64)
        vec = embedder.embed_text("Optimisation énergétique")
        assert len(vec) == 64

        gemini_embedder = GeminiEmbedder()
        assert gemini_embedder.dimension == 768

        retriever = InMemoryRetriever()
        chunk1 = DocumentChunk(
            document_id="doc-1",
            content="Procédure d'effacement des compresseurs en période de pointe.",
            metadata={"category": "procedure"},
        )
        chunk2 = DocumentChunk(
            document_id="doc-2",
            content="Spécifications techniques de la presse hydraulique P1.",
            metadata={"category": "manual"},
        )
        retriever.add_document(chunk1)
        retriever.add_document(chunk2)

        results = retriever.retrieve("effacement compresseurs", top_k=1)
        assert len(results) == 1
        assert results[0].document_id == "doc-1"

    def test_memory_implementations(self):
        """Vérifie les implémentations de mémoire conversationnelle."""
        buffer_mem = ConversationBufferMemory(max_turns=2)
        buffer_mem.save_context("User 1", "AI 1")
        buffer_mem.save_context("User 2", "AI 2")
        vars_dict = buffer_mem.load_memory_variables()
        assert len(vars_dict["history"]) == 4

        summary_mem = SummaryMemory()
        summary_mem.save_context("Comment marche le four ?", "Le four consomme 120 kW.")
        summary_vars = summary_mem.load_memory_variables()
        assert "four" in summary_vars["summary"]

    def test_rag_pipeline_execution(self):
        """Vérifie le cycle complet du pipeline RAG."""
        gateway = AIGateway(api_key="")
        retriever = InMemoryRetriever()
        retriever.add_document(
            DocumentChunk(document_id="doc-energy", content="Tarif CIE Heures de Pointe = 145 FCFA/kWh")
        )
        pipeline = IndustrialRAGPipeline(gateway=gateway, retriever=retriever)
        response = pipeline.run("Quel est le tarif de pointe ?")
        assert isinstance(response, AIResponse)
        assert len(response.content) > 0

    def test_copilot_end_to_end_ask(self):
        """Vérifie l'orchestration complète du Copilot industriel."""
        copilot = IndustrialCopilot()
        machines = [
            {"name": "Presse 1", "status": "running", "power_kw": 50.0, "temperature_c": 70.0, "vibration_hz": 8.0}
        ]
        alerts = []
        response = copilot.ask(
            query="Faut-il délester la Presse 1 maintenant ?",
            session_id="test-session-123",
            machines=machines,
            alerts=alerts,
            current_hour=20,
            use_tools=True,
        )
        assert isinstance(response, AIResponse)
        assert response.model_name is not None
        assert response.latency_ms >= 0.0

        # Vérifier que la session a bien sauvegardé les messages
        history = copilot.conversation_manager.get_history("test-session-123")
        assert len(history) == 2
        assert history[0].role == MessageRole.USER
        assert history[1].role == MessageRole.ASSISTANT
