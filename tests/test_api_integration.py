"""FastAPI integration checks for the supported service and legacy entry point."""
import os
os.environ.setdefault("AUDIT_SECRET_KEY", "test-integration-key-not-for-production")

from fastapi.testclient import TestClient
from agents.api import app
from glomerulonephritis_classifier_agent.server import create_app


def test_main_http_api_end_to_end():
    client = TestClient(app)
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "HEALTHY"
    response = client.post("/api/audit", json={
        "task_id": "TEST-100", "target_identifier": "SYN-100",
        "primary_metric": 28, "secondary_metric": 2,
        "status_descriptor": "NOMINAL", "is_critical_flag": False
    })
    assert response.status_code == 200, response.text
    assert response.json()["overall_urgency"] == "ELEVATED_RISK"
    metrics = client.get("/metrics/prometheus")
    assert metrics.status_code == 200
    assert "system_tasks_total" in metrics.text
    assert "text/plain" in metrics.headers["content-type"]
    assert client.get("/api/audit/logs").json()["verified"] is True


def test_nested_phi_is_rejected_by_http_api():
    client = TestClient(app)
    response = client.post("/api/audit", json={
        "task_id": "TEST-200", "target_identifier": "SYN-200",
        "primary_metric": 5, "attributes": {"note": "MRN-994827"}
    })
    assert response.status_code == 422
    assert "994827" not in response.text


def test_legacy_http_api_health_and_audit():
    app2 = create_app()
    assert app2 is not None
    client = TestClient(app2)
    assert client.get("/health").status_code == 200
    response = client.post("/api/audit", json={
        "case_id": "TEST-300", "patient_synthetic_id": "SYN-300",
        "primary_metric": 2, "secondary_metric": 1, "status_flag": "NORMAL"
    })
    assert response.status_code == 200, response.text
    assert response.json()["overall_status"] == "CONCORDANT_NORMAL"
