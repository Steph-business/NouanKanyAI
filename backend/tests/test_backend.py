from fastapi.testclient import TestClient

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
