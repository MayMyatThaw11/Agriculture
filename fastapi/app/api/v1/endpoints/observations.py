from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.field import Field
from app.db.models.sensor_device import SensorDevice
from app.db.models.sensor_observation import SensorObservation
from app.db.session import get_db_session
from app.schemas.sensor_observation import (
    IngestObservationRequest,
    ObservationResponse,
    SimulateObservationRequest,
)
from app.services.assessment import recompute_assessment
from app.services.observation import (
    simulate_scenario,
    validate_observation,
)

router = APIRouter(tags=["observations"])


async def _save_observation(
    request: IngestObservationRequest,
    session: AsyncSession,
) -> ObservationResponse:
    device = await session.get(SensorDevice, request.device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    existing = await session.execute(
        select(SensorObservation).where(
            SensorObservation.event_id == request.event_id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Observation with event_id '{request.event_id}' already exists",
        )

    validate_observation(request)

    observation = SensorObservation(
        device_id=request.device_id,
        event_id=request.event_id,
        temperature=request.temperature,
        humidity=request.humidity,
        soil_moisture=request.soil_moisture,
        ph=request.ph,
        light=request.light,
        recorded_at=request.recorded_at or datetime.now(UTC),
    )
    session.add(observation)

    device.last_seen_at = datetime.now(UTC)
    device.is_stale = False

    await session.commit()
    await session.refresh(observation)

    field = await session.get(Field, device.field_id)
    if field:
        await recompute_assessment(session, field)

    return ObservationResponse(
        id=observation.id,
        device_id=observation.device_id,
        event_id=observation.event_id,
        temperature=observation.temperature,
        humidity=observation.humidity,
        soil_moisture=observation.soil_moisture,
        ph=observation.ph,
        light=observation.light,
        recorded_at=observation.recorded_at,
    )


@router.post(
    "/observations/ingest",
    response_model=ObservationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Accept normalized sensor readings from a device",
)
async def ingest_observation(
    request: IngestObservationRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
):
    return await _save_observation(request, session)


@router.post(
    "/observations/simulate",
    response_model=ObservationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a simulated observation for manual scenario testing",
)
async def simulate_observation(
    request: SimulateObservationRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
):
    device = await session.get(SensorDevice, request.device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    simulated = simulate_scenario(device, request.scenario)
    return await _save_observation(simulated, session)
