from typing import Any

from sqlalchemy.orm import Session

from app.db import Assessment, CropProfile, Field, utcnow
from app.services import current_context, current_observation
from app.services.alerting import create_alert_for_assessment
from app.services.suitability import score_crop


def recompute_assessment(
    session: Session,
    field: Field,
    *,
    source_mode: str = "seeded",
) -> tuple[Assessment, Any, Any]:
    crop_id = field.selected_crop_id or "maize"
    crop = session.get(CropProfile, crop_id)
    context = current_context(session, field.id)
    observation = current_observation(session, field.id)
    if not crop or not context:
        raise ValueError("Field is missing a crop profile or context")

    values: dict[str, float] = {
        "temperature_c": observation.temperature_c if observation else context.temperature_baseline,
        "humidity_percent": observation.humidity_percent if observation else 70,
        "soil_moisture_percent": observation.soil_moisture_percent if observation else 65,
        "soil_ph": observation.soil_ph if observation else context.soil_ph,
        "light_percent": observation.light_percent if observation else 60,
        "rainfall_mm": context.rainfall_baseline,
    }
    result = score_crop(values, crop.requirements)
    assessment = Assessment(
        field_id=field.id,
        crop_id=crop.id,
        observation_id=observation.id if observation else None,
        status=result["status"],
        health_score=result["health_score"],
        primary_risk=result["primary_risk"],
        recommendation=result["recommendation"],
        evidence=result["evidence"],
        confidence=result["confidence"],
        decision_mode="rules",
        updated_at=utcnow(),
    )
    session.add(assessment)
    session.flush()
    alert, delivery = create_alert_for_assessment(session, field=field, assessment=assessment)
    session.commit()
    session.refresh(assessment)
    return assessment, alert, delivery
