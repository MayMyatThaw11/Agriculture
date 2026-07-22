"""Application services for the AgroGuard decision loop."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import Assessment, Field, FieldContext, Observation


def serialize_field(field: Field, current_status: str | None = None) -> dict:
    return {
        "id": field.id,
        "name": field.name,
        "latitude": field.latitude,
        "longitude": field.longitude,
        "area_hectares": field.area_hectares,
        "region_label": field.region_label,
        "crop_id": field.selected_crop_id,
        "selected_crop_id": field.selected_crop_id,
        "is_demo": field.is_demo,
        "status": field.status,
        "created_at": field.created_at,
        "current_status": current_status,
    }


def current_observation(session: Session, field_id: str) -> Observation | None:
    return session.scalar(
        select(Observation).where(Observation.field_id == field_id).order_by(Observation.observed_at.desc())
    )


def current_context(session: Session, field_id: str) -> FieldContext | None:
    return session.scalar(
        select(FieldContext).where(FieldContext.field_id == field_id).order_by(FieldContext.retrieved_at.desc())
    )


def latest_assessment(session: Session, field_id: str) -> Assessment | None:
    return session.scalar(
        select(Assessment).where(Assessment.field_id == field_id).order_by(Assessment.updated_at.desc())
    )


from app.services.assessment import recompute_assessment  # noqa: E402
from app.services.growth_sim import ensure_simulations, reset_demo_data, start_growth_replay  # noqa: E402

__all__ = [
    "current_context",
    "current_observation",
    "ensure_simulations",
    "latest_assessment",
    "recompute_assessment",
    "reset_demo_data",
    "serialize_field",
    "start_growth_replay",
]
