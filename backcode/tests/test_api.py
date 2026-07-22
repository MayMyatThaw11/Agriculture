import os
from uuid import uuid4

os.environ["AGROGUARD_DATABASE_URL"] = "sqlite:///./test-agroguard.db"

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_demo_vertical_slice() -> None:
    transport = ASGITransport(app=app)
    async with app.router.lifespan_context(app):
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            assert (await client.get("/health")).json() == {"status": "ok"}
            reset = await client.post("/api/demo/reset", json={"scenario": "healthy"})
            assert reset.status_code == 200
            fields = await client.get("/api/v1/fields")
            assert fields.status_code == 200
            assert fields.json()[0]["id"] == "demo-field"

            baseline = await client.get("/api/v1/fields/demo-field/assessment")
            assert baseline.status_code == 200
            assert baseline.json()["status"] == "healthy"

            reading = await client.post(
                "/api/v1/observations",
                json={
                    "eventId": f"test-dry-observation-{uuid4().hex}",
                    "deviceId": "demo-device",
                    "fieldId": "demo-field",
                    "temperatureC": 30,
                    "humidityPercent": 68,
                    "soilMoisturePercent": 10,
                    "soilPh": 6.4,
                    "lightPercent": 60,
                    "sourceMode": "simulated",
                },
            )
            assert reading.status_code == 201
            assessment = await client.get("/api/v1/fields/demo-field/assessment")
            assert assessment.json()["status"] == "critical"
            alerts = await client.get("/api/v1/alerts", params={"fieldId": "demo-field"})
            assert alerts.status_code == 200
            assert any(alert["severity"] == "critical" for alert in alerts.json())


@pytest.mark.asyncio
async def test_observation_is_idempotent() -> None:
    transport = ASGITransport(app=app)
    async with app.router.lifespan_context(app):
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            payload = {
                "eventId": f"same-event-{uuid4().hex}",
                "deviceId": "demo-device",
                "fieldId": "demo-field",
                "temperatureC": 29,
                "humidityPercent": 68,
                "soilMoisturePercent": 65,
                "soilPh": 6.4,
                "lightPercent": 60,
                "sourceMode": "simulated",
            }
            assert (await client.post("/api/v1/observations", json=payload)).status_code == 201
            assert (await client.post("/api/v1/observations", json=payload)).status_code == 409


@pytest.mark.asyncio
async def test_alert_lifecycle_and_growth_replay() -> None:
    transport = ASGITransport(app=app)
    async with app.router.lifespan_context(app):
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            reset = await client.post("/api/demo/reset", json={"scenario": "dry-soil"})
            assert reset.status_code == 200
            assert reset.json()["assessment"]["status"] == "critical"

            alerts = await client.get("/api/fields/demo-field/alerts")
            assert alerts.status_code == 200 and alerts.json()
            alert_id = alerts.json()[0]["id"]
            acknowledged = await client.patch(f"/api/alerts/{alert_id}/acknowledge")
            assert acknowledged.status_code == 200
            assert acknowledged.json()["status"] == "acknowledged"
            resolved = await client.patch(f"/api/alerts/{alert_id}/resolve")
            assert resolved.status_code == 200
            assert resolved.json()["status"] == "resolved"

            replay = await client.post("/api/fields/demo-field/growth/start", json={"scenario": "dry-soil"})
            assert replay.status_code == 200
            assert len(replay.json()) == 2
            assert all(item["isIllustrative"] and len(item["events"]) == 12 for item in replay.json())
