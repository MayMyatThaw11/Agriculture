"""Observation validation belongs here; the HTTP layer only maps errors."""

from datetime import UTC, timedelta

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import Device, Field, Observation, utcnow
from app.schemas import ObservationCreate
from app.services import recompute_assessment


def ingest_observation(session: Session, data: ObservationCreate) -> Observation:
    if session.scalar(select(Observation).where(Observation.event_id == data.event_id)):
        raise HTTPException(
            status_code=409, detail={"code": "duplicate_event", "message": "Observation event was already processed"}
        )
    field = session.get(Field, data.field_id)
    device = session.get(Device, data.device_id)
    if not field:
        raise HTTPException(status_code=404, detail={"code": "field_not_found", "message": "Field not found"})
    if not device or device.field_id != field.id:
        raise HTTPException(
            status_code=404, detail={"code": "device_not_found", "message": "Device not found for field"}
        )
    observed_at = data.observed_at or utcnow()
    if observed_at.tzinfo is None:
        observed_at = observed_at.replace(tzinfo=UTC)
    if observed_at > utcnow() + timedelta(minutes=5):
        raise HTTPException(
            status_code=422,
            detail={"code": "future_timestamp", "message": "Observation timestamp is too far in the future"},
        )
    observation = Observation(
        **data.model_dump(exclude={"observed_at"}), observed_at=observed_at, received_at=utcnow(), quality="good"
    )
    session.add(observation)
    device.last_seen_at = utcnow()
    session.commit()
    session.refresh(observation)
    recompute_assessment(session, field, source_mode=data.source_mode)
    return observation
