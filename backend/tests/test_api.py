import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_list_rules(client):
    response = client.get("/api/rules")
    assert response.status_code == 200
    data = response.json()
    assert "metadata" in data
    assert data["metadata"]["version"] == "2026.2"
    assert len(data["rules"]) > 10

def test_auth_and_scan_flow(client):
    # Register
    email = "testuser@example.com"
    pwd = "SecurePassword@123"
    reg_resp = client.post("/api/auth/register", json={
        "email": email,
        "password": pwd,
        "full_name": "Test Inspector",
        "role": "INSPECTOR"
    })
    assert reg_resp.status_code in [201, 400] # 400 if already created in previous run

    # Login
    login_resp = client.post("/api/auth/login", json={
        "email": email,
        "password": pwd
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Post Demo Scan
    scan_resp = client.post("/api/scans", data={"demoPreset": "demoA"}, headers=headers)
    assert scan_resp.status_code == 201
    scan_data = scan_resp.json()
    assert scan_data["overallStatus"] == "COMPLIANT"
    assert "summary" in scan_data
    scan_id = scan_data["id"]

    # Get Scan Details
    detail_resp = client.get(f"/api/scans/{scan_id}")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["id"] == scan_id

    # List Scans
    list_resp = client.get("/api/scans", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1

    # Admin Dashboard
    admin_resp = client.get("/api/admin/dashboard")
    assert admin_resp.status_code == 200
    admin_data = admin_resp.json()
    assert admin_data["totalScans"] >= 1
    assert "neutralNotice" in admin_data
