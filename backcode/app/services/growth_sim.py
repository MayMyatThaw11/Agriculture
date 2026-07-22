from datetime import UTC, date, datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db import Alert, Assessment, Field, GrowthEvent, GrowthSimulation, Notification, Observation

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
STAGES = [
    "Germination",
    "Germination",
    "Vegetative",
    "Vegetative",
    "Flowering",
    "Flowering",
    "Fruiting",
    "Fruiting",
    "Grain filling",
    "Grain filling",
    "Harvest",
    "Harvest",
]


def _build_scenario(
    session: Session, *, field_id: str, crop_id: str, scenario_type: str, seed: str, stressed: bool
) -> GrowthSimulation:
    simulation = GrowthSimulation(
        field_id=field_id, crop_id=crop_id, scenario_type=scenario_type, seed=seed, is_illustrative=True
    )
    session.add(simulation)
    session.flush()
    year = datetime.now(UTC).year
    for index, (_month, stage) in enumerate(zip(MONTHS, STAGES, strict=True)):
        recovery = 10 if scenario_type == "iot_guided" and stressed and index >= 3 else 0
        degradation = 3 * max(0, index - 2) if scenario_type == "normal_control" and stressed else 0
        health = max(25, min(98, 86 - (12 if stressed else 0) + recovery - degradation))
        session.add(
            GrowthEvent(
                simulation_id=simulation.id,
                event_date=str(date(year, index + 1, 15)),
                growth_stage=stage,
                health_index=health,
                intervention=("Irrigation alert acted on; moisture recovered." if recovery else None),
                risk_marker=(
                    "dry-soil" if stressed and index == 2 else "heat-stress" if stressed and index == 3 else None
                ),
            )
        )
    return simulation


def start_growth_replay(session: Session, field: Field, scenario: str = "healthy") -> list[GrowthSimulation]:
    for simulation in session.scalars(select(GrowthSimulation).where(GrowthSimulation.field_id == field.id)).all():
        session.execute(delete(GrowthEvent).where(GrowthEvent.simulation_id == simulation.id))
    session.execute(delete(GrowthSimulation).where(GrowthSimulation.field_id == field.id))
    stressed = scenario != "healthy"
    result = [
        _build_scenario(
            session,
            field_id=field.id,
            crop_id=field.selected_crop_id or "maize",
            scenario_type="iot_guided",
            seed=f"{scenario}-guided-v2",
            stressed=stressed,
        ),
        _build_scenario(
            session,
            field_id=field.id,
            crop_id=field.selected_crop_id or "maize",
            scenario_type="normal_control",
            seed=f"{scenario}-control-v2",
            stressed=stressed,
        ),
    ]
    session.commit()
    return result


def ensure_simulations(session: Session, field_id: str, crop_id: str) -> list[GrowthSimulation]:
    existing = list(session.scalars(select(GrowthSimulation).where(GrowthSimulation.field_id == field_id)).all())
    if existing:
        return existing
    field = session.get(Field, field_id)
    return start_growth_replay(session, field, "healthy") if field else []


def reset_demo_data(session: Session, field: Field, scenario: str = "healthy") -> list[GrowthSimulation]:
    simulation_ids = [
        item.id for item in session.scalars(select(GrowthSimulation).where(GrowthSimulation.field_id == field.id)).all()
    ]
    for simulation_id in simulation_ids:
        session.execute(delete(GrowthEvent).where(GrowthEvent.simulation_id == simulation_id))
    session.execute(delete(GrowthSimulation).where(GrowthSimulation.field_id == field.id))
    alert_ids = [item.id for item in session.scalars(select(Alert).where(Alert.field_id == field.id)).all()]
    for alert_id in alert_ids:
        session.execute(delete(Notification).where(Notification.alert_id == alert_id))
    session.execute(delete(Alert).where(Alert.field_id == field.id))
    session.execute(delete(Assessment).where(Assessment.field_id == field.id))
    session.execute(delete(Observation).where(Observation.field_id == field.id))
    session.commit()
    return start_growth_replay(session, field, scenario)
