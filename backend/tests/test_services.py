"""Service-layer tests: ingestion, correlation, RCA, and remediation lifecycle."""

import pytest

from app.models.enums import ActionType, AlertSeverity, IncidentStatus, RemediationStatus
from app.models.schemas.alert import AlertIngest
from app.services.alert_service import AlertService
from app.services.incident_service import IncidentService
from app.services.remediation_service import RemediationService


def _alert(**kw) -> AlertIngest:
    base = {
        "service": "checkout-api",
        "severity": AlertSeverity.CRITICAL,
        "metric": "api_latency_p95",
        "value": 2500,
        "threshold": 1000,
        "labels": {"env": "production"},
    }
    base.update(kw)
    return AlertIngest(**base)


@pytest.mark.asyncio
async def test_ingest_creates_incident_with_rca(db_session):
    alert, incident_id, created = await AlertService(db_session).ingest(_alert())
    await db_session.commit()
    assert created is True

    incident = await IncidentService(db_session).get(incident_id)
    assert incident.confidence is not None
    assert incident.recommended_action["action_type"] == ActionType.ROLLBACK.value
    assert incident.status == IncidentStatus.AWAITING_APPROVAL.value


@pytest.mark.asyncio
async def test_alerts_correlate_to_same_incident(db_session):
    svc = AlertService(db_session)
    _, inc1, created1 = await svc.ingest(_alert(alert_id="c1"))
    await db_session.commit()
    _, inc2, created2 = await svc.ingest(
        _alert(alert_id="c2", metric="error_rate", value=0.05, threshold=0.01)
    )
    await db_session.commit()
    assert created1 is True and created2 is False
    assert inc1 == inc2


@pytest.mark.asyncio
async def test_remediation_auto_proposed_and_approved(db_session):
    _, incident_id, _ = await AlertService(db_session).ingest(_alert())
    await db_session.commit()

    rem_svc = RemediationService(db_session)
    rems = await rem_svc.list(incident_id=incident_id)
    assert len(rems) == 1
    assert rems[0].status == RemediationStatus.PENDING_APPROVAL.value

    approved = await rem_svc.approve(rems[0].remediation_id, actor="operator")
    await db_session.commit()
    assert approved.status == RemediationStatus.SUCCEEDED.value
    assert approved.result["success"] is True


@pytest.mark.asyncio
async def test_remediation_reject(db_session):
    _, incident_id, _ = await AlertService(db_session).ingest(_alert())
    await db_session.commit()
    rem_svc = RemediationService(db_session)
    rem = (await rem_svc.list(incident_id=incident_id))[0]
    rejected = await rem_svc.reject(rem.remediation_id, actor="operator", reason="false positive")
    await db_session.commit()
    assert rejected.status == RemediationStatus.REJECTED.value
    assert rejected.rejection_reason == "false positive"
