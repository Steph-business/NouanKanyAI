"""
backend/tests/ai/test_multi_agent.py — Tests unitaires et d'intégration pour l'architecture Multi-Agents et l'orchestrateur central.
"""

import pytest
from app.ai.multiagent import (
    MultiAgentOrchestrator,
    SharedAgentBlackboard,
    AgentTask,
    AgentResult,
    AgentType,
    ExecutionMode,
    TaskPriority,
    EnergyAgent,
    ForecastAgent,
    AnomalyAgent,
    MaintenanceAgent,
    OptimizationAgent,
    ReportingAgent,
    CostSavingAgent,
    CarbonAgent,
    IoTAgent,
    AdministratorAgent,
)


class TestMultiAgentSuite:
    """Suite de tests pour la collaboration multi-agents et l'orchestration."""

    @pytest.fixture(autouse=True)
    def setup_orchestrator(self):
        self.orchestrator = MultiAgentOrchestrator.create_default_orchestrator()
        self.blackboard = self.orchestrator.blackboard

    def test_all_ten_specialized_agents_registered(self):
        """Vérifie que les 10 agents spécialisés requis sont bien instanciés et enregistrés."""
        agents = self.orchestrator.list_agents()
        assert len(agents) == 10

        expected_types = [
            AgentType.ENERGY,
            AgentType.FORECAST,
            AgentType.ANOMALY,
            AgentType.MAINTENANCE,
            AgentType.OPTIMIZATION,
            AgentType.REPORTING,
            AgentType.COST_SAVING,
            AgentType.CARBON,
            AgentType.IOT,
            AgentType.ADMINISTRATOR,
        ]
        registered_types = [a.agent_type for a in agents]
        for exp in expected_types:
            assert exp in registered_types, f"Agent manquant : {exp}"
            agent = self.orchestrator.get_agent(exp)
            assert agent is not None
            assert len(agent.capabilities) >= 5
            assert len(agent.description) > 10

    def test_shared_agent_blackboard_operations(self):
        """Vérifie le fonctionnement du bus d'échange partagé (Blackboard)."""
        bb = SharedAgentBlackboard(initial_state={"voltage_v": 400.0})
        assert bb.get_value("voltage_v") == 400.0

        bb.set_value("temperature_c", 68.5, author=AgentType.IOT)
        assert bb.get_value("temperature_c") == 68.5

        bb.set_agent_output(AgentType.ENERGY, {"load_kw": 120.0})
        out = bb.get_agent_output(AgentType.ENERGY)
        assert out["load_kw"] == 120.0

        snap = bb.get_snapshot()
        assert snap["state"]["temperature_c"] == 68.5
        assert snap["event_count"] >= 1

    def test_semantic_task_routing(self):
        """Vérifie le routage sémantique automatique des requêtes vers les agents compétents."""
        # Tâche 1 : Prévision
        t_forecast = AgentTask(query="Quelle est la prévision de consommation à t+1 heure ?")
        routed_1 = self.orchestrator.route_task(t_forecast)
        assert len(routed_1) >= 1
        assert routed_1[0].agent_type == AgentType.FORECAST

        # Tâche 2 : Maintenance
        t_maint = AgentTask(query="Planifier la maintenance prédictive et vérifier les vibrations des roulements.")
        routed_2 = self.orchestrator.route_task(t_maint)
        assert any(a.agent_type == AgentType.MAINTENANCE for a in routed_2)

        # Tâche 3 : Facturation FCFA
        t_cost = AgentTask(query="Calculer les économies en FCFA et le tarif CIE.")
        routed_3 = self.orchestrator.route_task(t_cost)
        assert any(a.agent_type == AgentType.COST_SAVING for a in routed_3)

        # Tâche 4 : Carbone
        t_carb = AgentTask(query="Bilan des émissions de CO2 et empreinte carbone.")
        routed_4 = self.orchestrator.route_task(t_carb)
        assert any(a.agent_type == AgentType.CARBON for a in routed_4)

    def test_single_agent_execution_mode(self):
        """Vérifie l'exécution ciblée d'un seul agent."""
        task = AgentTask(
            query="Inspecter la connectivité IoT",
            target_agents=[AgentType.IOT],
            execution_mode=ExecutionMode.SINGLE,
        )
        response = self.orchestrator.execute_task(task)

        assert response.task_id == task.task_id
        assert len(response.participating_agents) == 1
        assert response.participating_agents[0] == AgentType.IOT
        assert "iot_agent" in response.agent_results
        assert response.agent_results["iot_agent"].success is True

    def test_sequential_pipeline_execution_mode(self):
        """Vérifie l'exécution en cascade avec partage de contexte."""
        task = AgentTask(
            query="Optimiser la charge et calculer les économies",
            target_agents=[AgentType.ENERGY, AgentType.OPTIMIZATION, AgentType.COST_SAVING],
            execution_mode=ExecutionMode.SEQUENTIAL_PIPELINE,
            context_data={"total_power_kw": 145.0, "subscribed_limit_kw": 250.0},
        )
        response = self.orchestrator.execute_task(task)

        assert response.execution_mode == ExecutionMode.SEQUENTIAL_PIPELINE
        assert len(response.participating_agents) == 3
        assert "energy_agent" in response.agent_results
        assert "optimization_agent" in response.agent_results
        assert "cost_saving_agent" in response.agent_results
        assert "Diagnostic Multi-Agents" in response.combined_summary

    def test_parallel_fanout_and_consensus_synthesis(self):
        """Vérifie l'exécution parallèle avec synthèse collective."""
        task = AgentTask(
            query="Diagnostic complet de l'usine : puissance, prévision, anomalie, maintenance et carbone",
            target_agents=[
                AgentType.ENERGY,
                AgentType.FORECAST,
                AgentType.ANOMALY,
                AgentType.MAINTENANCE,
                AgentType.CARBON,
            ],
            execution_mode=ExecutionMode.CONSENSUS_SYNTHESIS,
        )
        response = self.orchestrator.execute_task(task)

        assert response.execution_mode == ExecutionMode.CONSENSUS_SYNTHESIS
        assert len(response.participating_agents) == 5
        assert len(response.agent_results) == 5
        assert response.total_latency_ms >= 0.0
        assert "Observations des Agents Experts" in response.combined_summary
        assert "Plan d'Action Collectif" in response.combined_summary

    def test_agent_error_resilience(self):
        """Vérifie que l'orchestrateur gère les erreurs isolées sans bloquer la réponse collective."""
        class FailingAgent(EnergyAgent):
            @property
            def agent_type(self) -> AgentType:
                return AgentType.ENERGY

            def process(self, task: AgentTask, blackboard: SharedAgentBlackboard) -> AgentResult:
                raise RuntimeError("Panne de communication simulée")

        orch = MultiAgentOrchestrator()
        orch.register_agent(FailingAgent())
        orch.register_agent(CostSavingAgent())

        task = AgentTask(
            query="Analyser la situation",
            target_agents=[AgentType.ENERGY, AgentType.COST_SAVING],
            execution_mode=ExecutionMode.PARALLEL_FANOUT,
        )
        response = orch.execute_task(task)

        assert "energy_agent" in response.agent_results
        assert response.agent_results["energy_agent"].success is False
        assert "Panne de communication" in str(response.agent_results["energy_agent"].error)

        assert "cost_saving_agent" in response.agent_results
        assert response.agent_results["cost_saving_agent"].success is True
