from fastapi.testclient import TestClient

import backend.main as main
from backend.main import app


def test_root_endpoint():
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["message"] == "NouanKanyAI API is running"


def test_machines_endpoint_returns_data():
    with TestClient(app) as client:
        response = client.get("/api/machines")
        assert response.status_code == 200
        payload = response.json()
        assert isinstance(payload, list)
        assert len(payload) > 0
        machine = payload[0]
        assert "machine_id" in machine
        assert "status" in machine


def test_structured_router_machines_endpoint_returns_data():
    with TestClient(app) as client:
        response = client.get("/api/v1/machines")
        assert response.status_code == 200
        payload = response.json()
        assert isinstance(payload, list)
        assert len(payload) > 0
        machine = payload[0]
        assert "machine_id" in machine
        assert "status" in machine
        assert "nom" in machine


def test_facturation_falls_back_when_supabase_fails(monkeypatch):
    class BrokenSupabase:
        def table(self, *_args, **_kwargs):
            raise RuntimeError("simulated outage")

    monkeypatch.setattr(main, "supabase", BrokenSupabase())

    with TestClient(app) as client:
        response = client.get("/api/facturation")
        assert response.status_code == 200
        payload = response.json()
        assert "grossSavings" in payload
        assert payload["auditTrail"] == []
        assert payload["invoices"] == []


def test_predict_uses_fallback_when_model_unavailable(monkeypatch):
    monkeypatch.setattr(main, "xgb_data", None)
    monkeypatch.setattr(main, "iso_data", None)
    monkeypatch.setattr(main, "load_models", lambda: None)

    with TestClient(app) as client:
        response = client.post(
            "/api/predict",
            json={
                "machine_id": "M-001",
                "temperature_c": 30.0,
                "vibration_hz": 6.0,
                "pressure_bar": 2.0,
                "hours_ahead": 3,
            },
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["machine_id"] == "M-001"
        assert payload["mode"] == "fallback"
        assert len(payload["predictions"]) == 3


def test_media_analysis_reports_unsupported_format_without_crashing():
    with TestClient(app) as client:
        response = client.post(
            "/api/machines/M-001/analyze-media",
            files={"file": ("report.pdf", b"%PDF-1.4", "application/pdf")},
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "UNSUPPORTED_FORMAT"


def test_simulate_machine_uses_demo_when_supabase_unavailable():
    with TestClient(app) as client:
        response = client.post("/api/machines/CLIM-001/simulate")
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "success"
        assert payload["mode"] == "demo"
