"""End-to-end API tests covering the full incident lifecycle and RBAC."""

import pytest

ALERT = {
    "alert_id": "api-001",
    "service": "checkout-api",
    "severity": "critical",
    "metric": "api_latency_p95",
    "value": 2500,
    "threshold": 1000,
    "labels": {"env": "production"},
}


@pytest.mark.asyncio
async def test_health_ok(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_endpoints_require_auth(client):
    assert (await client.get("/api/v1/incidents/")).status_code == 401
    assert (await client.post("/api/v1/alerts/ingest", json=ALERT)).status_code == 401


@pytest.mark.asyncio
async def test_login_returns_token(client):
    resp = await client.post(
        "/api/v1/auth/login", json={"username": "admin", "password": "admin123"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["role"] == "admin"
    assert body["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_bad_login_rejected(client):
    resp = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "wrong"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_full_incident_flow(client, operator_headers):
    # 1. Ingest alert -> incident + RCA
    resp = await client.post("/api/v1/alerts/ingest", json=ALERT, headers=operator_headers)
    assert resp.status_code == 201
    incident_id = resp.json()["incident_id"]
    assert resp.json()["incident_created"] is True

    # 2. Incident has RCA + recommended rollback
    detail = (await client.get(f"/api/v1/incidents/{incident_id}", headers=operator_headers)).json()
    assert detail["status"] == "awaiting_approval"
    assert detail["recommended_action"]["action_type"] == "rollback"
    assert detail["confidence"] > 0.5
    assert len(detail["alerts"]) == 1

    # 3. A remediation is pending approval
    rems = (
        await client.get(
            "/api/v1/remediation/", params={"incident_id": incident_id}, headers=operator_headers
        )
    ).json()
    assert len(rems) == 1 and rems[0]["status"] == "pending_approval"

    # 4. Approve -> executed successfully (HITL)
    approve = await client.post(
        f"/api/v1/remediation/{rems[0]['remediation_id']}/approve", headers=operator_headers
    )
    assert approve.status_code == 200
    assert approve.json()["status"] == "succeeded"

    # 5. Stats reflect the activity
    stats = (await client.get("/api/v1/stats/summary", headers=operator_headers)).json()
    assert stats["incidents"]["total"] == 1
    assert stats["remediations"]["succeeded"] == 1


@pytest.mark.asyncio
async def test_rbac_viewer_cannot_ingest(client, viewer_headers):
    resp = await client.post("/api/v1/alerts/ingest", json=ALERT, headers=viewer_headers)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_viewer_can_read(client, viewer_headers):
    assert (await client.get("/api/v1/incidents/", headers=viewer_headers)).status_code == 200


@pytest.mark.asyncio
async def test_knowledge_search_endpoint(client, viewer_headers):
    resp = await client.post(
        "/api/v1/knowledge/search",
        json={"query": "rollback deployment latency", "top_k": 3},
        headers=viewer_headers,
    )
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


@pytest.mark.asyncio
async def test_integrations_status_admin_only(client, viewer_headers, admin_headers):
    # Viewers cannot see integration status.
    assert (
        await client.get("/api/v1/integrations/status", headers=viewer_headers)
    ).status_code == 403
    # Admins get a per-integration health report (mock mode in tests).
    resp = await client.get("/api/v1/integrations/status", headers=admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["mock_mode"] is True
    names = {i["name"] for i in body["integrations"]}
    assert {"slack", "kubernetes", "prometheus"}.issubset(names)
