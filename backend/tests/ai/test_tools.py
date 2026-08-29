"""
backend/tests/ai/test_tools.py — Tests unitaires et d'intégration pour le sous-système de Tool Calling (10 outils métier).
"""

import pytest
from app.ai import (
    ToolRegistry,
    BaseTool,
    ToolResult,
    PredictConsumptionTool,
    DetectAnomalyTool,
    GetEnergyHistoryTool,
    ComparePeriodsTool,
    GetSensorStatusTool,
    GetEquipmentDetailsTool,
    GetBuildingMetricsTool,
    GenerateReportTool,
    GetWeatherTool,
    GetElectricityTariffsTool,
    IndustrialCopilot,
)
from app.ai.exceptions import ToolExecutionError


class TestToolCallingSuite:
    """Suite de tests pour les outils métiers et le Function Calling."""

    @pytest.fixture(autouse=True)
    def setup_registry(self):
        self.registry = ToolRegistry.create_default_registry()

    def test_default_registry_contains_all_10_tools(self):
        """Vérifie que le registre par défaut initialise et contient l'intégralité des 10 outils requis."""
        tools = self.registry.list_tools()
        assert len(tools) == 10
        tool_names = [t.name for t in tools]

        expected = [
            "predict_consumption",
            "detect_anomaly",
            "get_energy_history",
            "compare_periods",
            "get_sensor_status",
            "get_equipment_details",
            "get_building_metrics",
            "generate_report",
            "get_weather",
            "get_electricity_tariffs",
        ]
        for name in expected:
            assert name in tool_names, f"Outil manquant : {name}"

    def test_predict_consumption_tool(self):
        """Vérifie l'exécution normalisée de l'outil predict_consumption."""
        tool = self.registry.get("predict_consumption")
        assert tool is not None

        result = tool.run(power_kw=45.0, temperature_c=30.0, hour=14)
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert result.data["predicted_power_kw"] > 0
        assert result.data["estimated_cost_fcfa"] > 0
        assert result.data["currency"] == "FCFA"
        assert result.execution_time_ms >= 0.0

    def test_detect_anomaly_tool(self):
        """Vérifie l'exécution normalisée de l'outil detect_anomaly."""
        tool = self.registry.get("detect_anomaly")
        assert tool is not None

        # Cas 1: Nominal
        res_normal = tool.run(power_kw=30.0, temperature_c=32.0, vibration_hz=3.0, pressure_bar=1.5)
        assert res_normal.success is True
        assert "is_anomaly" in res_normal.data
        assert "severity" in res_normal.data

        # Cas 2: Dérive extrême
        res_extreme = tool.run(power_kw=320.0, temperature_c=105.0, vibration_hz=85.0, pressure_bar=8.0)
        assert res_extreme.success is True
        assert res_extreme.data["is_anomaly"] is True
        assert res_extreme.data["severity"] in ["modérée", "critique"]

    def test_get_energy_history_tool(self):
        """Vérifie l'outil get_energy_history sur différentes périodes."""
        tool = self.registry.get("get_energy_history")
        assert tool is not None

        res_today = tool.run(period="today")
        assert res_today.success is True
        assert res_today.data["total_consumption_kwh"] > 0
        assert res_today.data["total_cost_fcfa"] > 0

        res_7d = tool.run(period="last_7_days", machine_id="compresseur_1")
        assert res_7d.success is True
        assert res_7d.data["period"] == "last_7_days"

    def test_compare_periods_tool(self):
        """Vérifie l'outil compare_periods."""
        tool = self.registry.get("compare_periods")
        assert tool is not None

        res = tool.run(period_1="last_week", period_2="this_week")
        assert res.success is True
        assert "consumption_period_1_kwh" in res.data
        assert "consumption_period_2_kwh" in res.data
        assert "delta_kwh" in res.data
        assert "delta_percentage" in res.data

    def test_get_sensor_status_tool(self):
        """Vérifie l'outil get_sensor_status."""
        tool = self.registry.get("get_sensor_status")
        assert tool is not None

        res = tool.run(machine_id="Four 1")
        assert res.success is True
        assert "sensors" in res.data
        assert len(res.data["sensors"]) >= 3
        assert res.data["gateway_status"] == "ONLINE"

    def test_get_equipment_details_tool(self):
        """Vérifie l'outil get_equipment_details."""
        tool = self.registry.get("get_equipment_details")
        assert tool is not None

        res = tool.run(equipment_id="compresseur_c1")
        assert res.success is True
        assert res.data["nominal_power_kw"] == 45.0
        assert "status" in res.data

    def test_get_building_metrics_tool(self):
        """Vérifie l'outil get_building_metrics."""
        tool = self.registry.get("get_building_metrics")
        assert tool is not None

        res = tool.run(building_id="usine_nord")
        assert res.success is True
        assert res.data["subscribed_power_limit_kw"] == 250.0
        assert res.data["power_factor_cos_phi"] >= 0.9

    def test_generate_report_tool(self):
        """Vérifie l'outil generate_report."""
        tool = self.registry.get("generate_report")
        assert tool is not None

        res = tool.run(report_type="daily", building_id="site_principal")
        assert res.success is True
        assert "report_id" in res.data
        assert "summary" in res.data
        assert len(res.data["top_recommendations"]) > 0

    def test_get_weather_tool(self):
        """Vérifie l'outil get_weather."""
        tool = self.registry.get("get_weather")
        assert tool is not None

        res = tool.run(location="Abidjan")
        assert res.success is True
        assert res.data["location"] == "Abidjan"
        assert "temperature_c" in res.data
        assert "cdd_cooling_impact" in res.data

    def test_get_electricity_tariffs_tool(self):
        """Vérifie l'outil get_electricity_tariffs."""
        tool = self.registry.get("get_electricity_tariffs")
        assert tool is not None

        # Heure de pointe (20h)
        res_peak = tool.run(contract_type="MT_INDUSTRIEL", hour=20)
        assert res_peak.success is True
        assert res_peak.data["active_tariff_band"] == "Heure de Pointe"
        assert res_peak.data["active_rate_fcfa_kwh"] == 145.0

        # Heure pleine (14h)
        res_standard = tool.run(hour=14)
        assert res_standard.data["active_tariff_band"] == "Heure Pleine"
        assert res_standard.data["active_rate_fcfa_kwh"] == 85.0

    def test_multi_provider_schema_export(self):
        """Vérifie l'export des schémas Function Calling pour Gemini, OpenAI et Anthropic."""
        gemini_schemas = self.registry.get_gemini_schemas()
        assert len(gemini_schemas) == 10
        assert "name" in gemini_schemas[0]
        assert "parameters" in gemini_schemas[0]

        openai_schemas = self.registry.get_openai_schemas()
        assert len(openai_schemas) == 10
        assert openai_schemas[0]["type"] == "function"
        assert "function" in openai_schemas[0]

        anthropic_schemas = self.registry.get_anthropic_schemas()
        assert len(anthropic_schemas) == 10
        assert "input_schema" in anthropic_schemas[0]

    def test_error_handling_unknown_tool(self):
        """Vérifie la robustesse en cas d'appel d'un outil inexistant."""
        with pytest.raises(ToolExecutionError):
            self.registry.execute_tool("unknown_tool_xyz", param=123)

        normalized_res = self.registry.execute_tool_normalized("unknown_tool_xyz")
        assert normalized_res.success is False
        assert normalized_res.error is not None

    def test_copilot_tool_registry_integration(self):
        """Vérifie que le Copilot initialise automatiquement les 10 outils et les expose."""
        copilot = IndustrialCopilot()
        tools = copilot.tool_registry.list_tools()
        assert len(tools) == 10
