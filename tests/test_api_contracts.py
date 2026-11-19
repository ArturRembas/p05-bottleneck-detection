cat << 'EOF' > tests/test_api_contracts.py
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_openapi_specification_version():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["openapi"] == "3.1.0"
    assert "/api/v1/analyses/{analysis_id}/bottlenecks" in schema["paths"]
    assert "/api/v1/analyses/{analysis_id}/kpis" in schema["paths"]

def test_upload_rejects_unsupported_format():
    files = {"file": ("test.txt", b"dummy content", "text/plain")}
    response = client.post("/api/v1/analyses", files=files)
    assert response.status_code == 415
    assert response.json()["code"] == "UNSUPPORTED_LOG_FORMAT"

def test_endpoints_return_501_not_mocked_data():
    response = client.get("/api/v1/analyses/run-demo-001/bottlenecks")
    assert response.status_code == 501
    assert response.json()["code"] == "ANALYSIS_REPOSITORY_NOT_IMPLEMENTED"

def test_approval_rejects_without_implementation():
    payload = {
        "candidate_id": "cand-01",
        "countermeasure_id": "cm-01",
        "workstation": "CNC_Milling",
        "action": "Add resource"
    }
    response = client.post("/api/v1/analyses/run-demo-001/countermeasures/approve", json=payload)
    assert response.status_code == 501
    assert response.json()["code"] == "APPROVAL_SERVICE_NOT_IMPLEMENTED"
EOF
