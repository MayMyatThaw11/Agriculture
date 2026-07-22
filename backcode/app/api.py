import json
from collections.abc import Iterator
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db import (
    NDVI,
    Alert,
    Assessment,
    CropProfile,
    Field,
    FieldContext,
    GrowthEvent,
    HealthUpdate,
    Notification,
    Observation,
    Region,
    get_db,
    utcnow,
)
from app.schemas import (
    AlertResponse,
    AssessmentResponse,
    ChatRequest,
    ContextResponse,
    CropExplanationRequest,
    CropResponse,
    CropSelectionRequest,
    DemoResetRequest,
    FieldCreate,
    FieldResponse,
    GrowthEventResponse,
    GrowthSimulationResponse,
    GrowthStartRequest,
    HealthResponse,
    HealthUpdateCreate,
    HealthUpdateResponse,
    NotificationResponse,
    ObservationCreate,
    ObservationResponse,
    WeatherRequest,
)
from app.services import (
    current_context,
    current_observation,
    ensure_simulations,
    recompute_assessment,
    reset_demo_data,
    serialize_field,
    start_growth_replay,
)
from app.services.alerting import acknowledge_alert as acknowledge_alert_service
from app.services.alerting import resolve_alert as resolve_alert_service
from app.services.observation import ingest_observation

router = APIRouter()
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE = 8 * 1024 * 1024


def get_field_or_404(session: Session, field_id: str) -> Field:
    field = session.get(Field, field_id)
    if not field:
        raise HTTPException(status_code=404, detail={"code": "field_not_found", "message": "Field not found"})
    return field


def assessment_dict(assessment: Assessment, observation: Observation | None = None) -> dict[str, Any]:
    mode = observation.source_mode if observation else "seeded"
    if mode == "manual":
        mode = "simulated"
    return {
        "id": assessment.id,
        "field_id": assessment.field_id,
        "crop_id": assessment.crop_id,
        "status": assessment.status,
        "health_score": assessment.health_score,
        "primary_risk": assessment.primary_risk,
        "recommendation": assessment.recommendation,
        "evidence": assessment.evidence,
        "confidence": assessment.confidence,
        "mode": mode,
        "updated_at": assessment.updated_at,
    }


@router.get("/health", response_model=HealthResponse, tags=["system"])
def api_health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok", service_name=settings.app_name, version=settings.app_version, environment=settings.environment
    )


@router.get("/fields", response_model=list[FieldResponse], tags=["fields"])
def list_fields(session: Session = Depends(get_db)) -> list[dict[str, Any]]:
    result = []
    for field in session.scalars(select(Field).where(Field.status == "active").order_by(Field.created_at)).all():
        latest = session.scalar(
            select(Assessment).where(Assessment.field_id == field.id).order_by(Assessment.updated_at.desc())
        )
        result.append(serialize_field(field, latest.status if latest else None))
    return result


@router.post("/fields", response_model=FieldResponse, status_code=status.HTTP_201_CREATED, tags=["fields"])
def create_field(data: FieldCreate, session: Session = Depends(get_db)) -> dict[str, Any]:
    if data.crop_id and not session.get(CropProfile, data.crop_id):
        raise HTTPException(status_code=404, detail={"code": "crop_not_found", "message": "Crop profile not found"})
    field = Field(
        id=f"field-{uuid4().hex[:12]}",
        name=data.name,
        latitude=data.latitude,
        longitude=data.longitude,
        area_hectares=data.area_hectares,
        region_label=data.region_label,
        selected_crop_id=data.crop_id or "maize",
        is_demo=False,
    )
    session.add(field)
    session.add(
        FieldContext(
            field_id=field.id,
            soil_type="Unknown",
            soil_ph=6.5,
            temperature_baseline=28,
            rainfall_baseline=120,
            elevation_meters=0,
            source_name="AgroGuard fallback context",
            source_reference="demo://fallback",
            quality="estimated",
        )
    )
    session.commit()
    session.refresh(field)
    return serialize_field(field)


@router.get("/fields/{field_id}", response_model=FieldResponse, tags=["fields"])
def get_field(field_id: str, session: Session = Depends(get_db)) -> dict[str, Any]:
    field = get_field_or_404(session, field_id)
    latest = session.scalar(
        select(Assessment).where(Assessment.field_id == field.id).order_by(Assessment.updated_at.desc())
    )
    return serialize_field(field, latest.status if latest else None)


@router.get("/fields/{field_id}/context", response_model=ContextResponse, tags=["fields"])
def get_context(field_id: str, session: Session = Depends(get_db)) -> FieldContext:
    get_field_or_404(session, field_id)
    context = current_context(session, field_id)
    if not context:
        raise HTTPException(status_code=404, detail={"code": "context_not_found", "message": "Field context not found"})
    return context


@router.post("/fields/{field_id}/context/refresh", response_model=ContextResponse, tags=["fields"])
def refresh_context(field_id: str, session: Session = Depends(get_db)) -> FieldContext:
    field = get_field_or_404(session, field_id)
    previous = current_context(session, field_id)
    context = FieldContext(
        field_id=field.id,
        soil_type=previous.soil_type if previous else "Unknown",
        soil_ph=previous.soil_ph if previous else 6.5,
        temperature_baseline=previous.temperature_baseline if previous else 28,
        rainfall_baseline=previous.rainfall_baseline if previous else 120,
        elevation_meters=previous.elevation_meters if previous else 0,
        source_name="AgroGuard fallback provider",
        source_reference="demo://fallback-refresh",
        quality="estimated",
        retrieved_at=utcnow(),
    )
    session.add(context)
    session.commit()
    session.refresh(context)
    return context


@router.get("/crops", response_model=list[CropResponse], tags=["crops"])
def list_crops(session: Session = Depends(get_db)) -> list[CropProfile]:
    return list(session.scalars(select(CropProfile).order_by(CropProfile.name)).all())


@router.get("/crops/{crop_id}", response_model=CropResponse, tags=["crops"])
def get_crop(crop_id: str, session: Session = Depends(get_db)) -> CropProfile:
    crop = session.get(CropProfile, crop_id)
    if not crop:
        raise HTTPException(status_code=404, detail={"code": "crop_not_found", "message": "Crop profile not found"})
    return crop


@router.post("/fields/{field_id}/crop-selection", response_model=FieldResponse, tags=["crops"])
def select_crop(field_id: str, data: CropSelectionRequest, session: Session = Depends(get_db)) -> dict[str, Any]:
    field = get_field_or_404(session, field_id)
    if not session.get(CropProfile, data.crop_id):
        raise HTTPException(status_code=404, detail={"code": "crop_not_found", "message": "Crop profile not found"})
    field.selected_crop_id = data.crop_id
    session.commit()
    session.refresh(field)
    return serialize_field(field)


@router.post(
    "/observations", response_model=ObservationResponse, status_code=status.HTTP_201_CREATED, tags=["observations"]
)
def create_observation(data: ObservationCreate, session: Session = Depends(get_db)) -> Observation:
    return ingest_observation(session, data)


@router.get("/fields/{field_id}/observations", response_model=list[ObservationResponse], tags=["observations"])
def list_observations(
    field_id: str, limit: int = Query(50, ge=1, le=200), session: Session = Depends(get_db)
) -> list[Observation]:
    get_field_or_404(session, field_id)
    return list(
        session.scalars(
            select(Observation)
            .where(Observation.field_id == field_id)
            .order_by(Observation.observed_at.desc())
            .limit(limit)
        ).all()
    )


@router.get("/fields/{field_id}/assessment", response_model=AssessmentResponse, tags=["assessments"])
def get_assessment(field_id: str, session: Session = Depends(get_db)) -> dict[str, Any]:
    field = get_field_or_404(session, field_id)
    assessment = session.scalar(
        select(Assessment).where(Assessment.field_id == field_id).order_by(Assessment.updated_at.desc())
    )
    if not assessment:
        assessment, _, _ = recompute_assessment(session, field)
    return assessment_dict(assessment, current_observation(session, field_id))


@router.post("/fields/{field_id}/assessment/recompute", response_model=AssessmentResponse, tags=["assessments"])
def recompute(field_id: str, session: Session = Depends(get_db)) -> dict[str, Any]:
    field = get_field_or_404(session, field_id)
    assessment, _, _ = recompute_assessment(session, field)
    return assessment_dict(assessment, current_observation(session, field_id))


@router.get("/alerts", response_model=list[AlertResponse], tags=["alerts"])
def list_alerts(
    field_id: str | None = None,
    alert_status: str | None = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=200),
    session: Session = Depends(get_db),
) -> list[Alert]:
    query: Select[Any] = select(Alert).order_by(Alert.opened_at.desc()).limit(limit)
    if field_id:
        query = query.where(Alert.field_id == field_id)
    if alert_status:
        query = query.where(Alert.status == alert_status)
    return list(session.scalars(query).all())


@router.get("/fields/{field_id}/alerts", response_model=list[AlertResponse], tags=["alerts"])
def field_alerts(
    field_id: str, limit: int = Query(50, ge=1, le=200), session: Session = Depends(get_db)
) -> list[Alert]:
    get_field_or_404(session, field_id)
    return list(
        session.scalars(
            select(Alert).where(Alert.field_id == field_id).order_by(Alert.opened_at.desc()).limit(limit)
        ).all()
    )


@router.api_route(
    "/alerts/{alert_id}/acknowledge", methods=["POST", "PATCH"], response_model=AlertResponse, tags=["alerts"]
)
def acknowledge_alert(alert_id: int, session: Session = Depends(get_db)) -> Alert:
    alert = acknowledge_alert_service(session, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail={"code": "alert_not_found", "message": "Alert not found"})
    return alert


@router.patch("/alerts/{alert_id}/resolve", response_model=AlertResponse, tags=["alerts"])
def resolve_alert(alert_id: int, session: Session = Depends(get_db)) -> Alert:
    alert = resolve_alert_service(session, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail={"code": "alert_not_found", "message": "Alert not found"})
    return alert


@router.get("/notifications", response_model=list[NotificationResponse], tags=["notifications"])
def list_notifications(limit: int = Query(50, ge=1, le=200), session: Session = Depends(get_db)) -> list[Notification]:
    return list(session.scalars(select(Notification).order_by(Notification.id.desc()).limit(limit)).all())


@router.get(
    "/fields/{field_id}/growth-simulations", response_model=list[GrowthSimulationResponse], tags=["simulations"]
)
def list_simulations(field_id: str, session: Session = Depends(get_db)) -> list[dict[str, Any]]:
    field = get_field_or_404(session, field_id)
    simulations = ensure_simulations(session, field.id, field.selected_crop_id or "maize")
    result = []
    for simulation in simulations:
        events = [
            GrowthEventResponse.model_validate(event).model_dump()
            for event in session.scalars(
                select(GrowthEvent).where(GrowthEvent.simulation_id == simulation.id).order_by(GrowthEvent.event_date)
            ).all()
        ]
        result.append(
            {
                "id": simulation.id,
                "field_id": simulation.field_id,
                "crop_id": simulation.crop_id,
                "scenario_type": simulation.scenario_type,
                "seed": simulation.seed,
                "is_illustrative": simulation.is_illustrative,
                "events": events,
            }
        )
    return result


@router.post(
    "/fields/{field_id}/growth-simulations/replay", response_model=list[GrowthSimulationResponse], tags=["simulations"]
)
def replay_simulations(field_id: str, session: Session = Depends(get_db)) -> list[dict[str, Any]]:
    field = get_field_or_404(session, field_id)
    return list_simulations(field.id, session)


@router.post("/fields/{field_id}/growth/start", response_model=list[GrowthSimulationResponse], tags=["simulations"])
def start_growth(field_id: str, data: GrowthStartRequest, session: Session = Depends(get_db)) -> list[dict[str, Any]]:
    field = get_field_or_404(session, field_id)
    start_growth_replay(session, field, data.scenario)
    return list_simulations(field.id, session)


@router.get("/fields/{field_id}/growth/timeline", response_model=list[GrowthSimulationResponse], tags=["simulations"])
def growth_timeline(field_id: str, session: Session = Depends(get_db)) -> list[dict[str, Any]]:
    return list_simulations(field_id, session)


@router.get("/demo-scenarios", tags=["demo"])
def demo_scenarios() -> list[dict[str, str]]:
    return [
        {"id": "healthy", "label": "Healthy baseline"},
        {"id": "dry-soil", "label": "Dry soil critical"},
        {"id": "heat-stress", "label": "Heat stress warning"},
    ]


@router.post("/demo-scenarios/{scenario_id}/reset", tags=["demo"])
def reset_demo_scenario(scenario_id: str, session: Session = Depends(get_db)) -> dict[str, Any]:
    if scenario_id not in {"healthy", "dry-soil", "heat-stress"}:
        raise HTTPException(
            status_code=404, detail={"code": "scenario_not_found", "message": "Demo scenario not found"}
        )
    return reset_demo(DemoResetRequest(scenario=scenario_id), session)


@router.post("/demo/reset", tags=["demo"])
def reset_demo(data: DemoResetRequest, session: Session = Depends(get_db)) -> dict[str, Any]:
    field = get_field_or_404(session, "demo-field")
    reset_demo_data(session, field, data.scenario)
    if data.scenario == "dry-soil":
        ingest_observation(
            session,
            ObservationCreate(
                event_id=f"demo-reset-dry-{uuid4().hex}",
                device_id="demo-device",
                field_id=field.id,
                source_mode="replay",
                soil_moisture_percent=12,
                temperature_c=30,
                humidity_percent=68,
                soil_ph=6.4,
                light_percent=60,
            ),
        )
    elif data.scenario == "heat-stress":
        ingest_observation(
            session,
            ObservationCreate(
                event_id=f"demo-reset-heat-{uuid4().hex}",
                device_id="demo-device",
                field_id=field.id,
                source_mode="replay",
                soil_moisture_percent=62,
                temperature_c=42,
                humidity_percent=55,
                soil_ph=6.4,
                light_percent=75,
            ),
        )
    assessment = AssessmentResponse.model_validate(get_assessment(field.id, session)).model_dump(by_alias=True)
    timeline = [
        GrowthSimulationResponse.model_validate(item).model_dump(by_alias=True)
        for item in list_simulations(field.id, session)
    ]
    return {
        "scenarioId": data.scenario,
        "message": "Demo data cleared and re-seeded without deleting non-demo records",
        "assessment": assessment,
        "timeline": timeline,
    }


# Compatibility routes used by the current React screens.
@router.get("/regions", tags=["legacy"])
def regions(session: Session = Depends(get_db)) -> list[dict[str, str]]:
    return [
        {"pcode": item.pcode, "name_en": item.name_en, "name_my": item.name_my}
        for item in session.scalars(select(Region).order_by(Region.name_en)).all()
    ]


@router.get("/ndvi/{pcode}", tags=["legacy"])
def ndvi(pcode: str, session: Session = Depends(get_db)) -> dict[str, list[Any]]:
    rows = session.scalars(select(NDVI).where(NDVI.region_pcode == pcode).order_by(NDVI.id)).all()
    if not rows:
        raise HTTPException(status_code=404, detail="No NDVI data found for region")
    return {"labels": [row.label for row in rows], "vim": [row.vim for row in rows], "viq": [row.viq for row in rows]}


@router.get("/dashboard/stats", tags=["legacy"])
def dashboard_stats(session: Session = Depends(get_db)) -> dict[str, Any]:
    fields = list(session.scalars(select(Field).where(Field.status == "active").order_by(Field.name)).all())
    assessment_count = session.scalar(select(func.count(Assessment.id))) or 0
    observation_count = session.scalar(select(func.count(Observation.id))) or 0
    active_alerts = session.scalar(select(func.count(Alert.id)).where(Alert.status == "open")) or 0
    statuses = []
    for field in fields:
        assessment = session.scalar(
            select(Assessment).where(Assessment.field_id == field.id).order_by(Assessment.updated_at.desc())
        )
        statuses.append(
            {
                "fieldId": field.id,
                "fieldName": field.name,
                "status": assessment.status if assessment else "healthy",
                "healthScore": assessment.health_score if assessment else None,
                "recommendation": assessment.recommendation if assessment else "No assessment yet",
                "primaryRisk": assessment.primary_risk if assessment else "none",
            }
        )
    return {
        "overview": {"townships": len(fields), "records": assessment_count, "yield": "demo", "rainfall": "seeded"},
        "totalFields": len(fields),
        "totalAssessments": assessment_count,
        "totalObservations": observation_count,
        "activeAlerts": active_alerts,
        "fieldStatuses": statuses,
        "cropDistribution": [{"crop": "Maize", "percent": 100 if fields else 0}],
        "yieldByCrop": [{"crop": "Maize", "yield": 0}],
    }


@router.post(
    "/health-updates", response_model=HealthUpdateResponse, status_code=status.HTTP_201_CREATED, tags=["legacy"]
)
def create_health_update(data: HealthUpdateCreate, session: Session = Depends(get_db)) -> HealthUpdate:
    item = HealthUpdate(**data.model_dump())
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.get("/health-updates", tags=["legacy"])
def health_updates(
    skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200), session: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    return [
        health_update_dict(item)
        for item in session.scalars(
            select(HealthUpdate).order_by(HealthUpdate.reported_at.desc()).offset(skip).limit(limit)
        ).all()
    ]


@router.put("/health-updates/{update_id}", tags=["legacy"])
def update_health_update(
    update_id: int, data: HealthUpdateCreate, session: Session = Depends(get_db)
) -> dict[str, Any]:
    item = session.get(HealthUpdate, update_id)
    if not item:
        raise HTTPException(status_code=404, detail="Health update not found")
    for key, value in data.model_dump().items():
        setattr(item, key, value)
    session.commit()
    session.refresh(item)
    return health_update_dict(item)


@router.delete("/health-updates/{update_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["legacy"])
def delete_health_update(update_id: int, session: Session = Depends(get_db)) -> None:
    item = session.get(HealthUpdate, update_id)
    if not item:
        raise HTTPException(status_code=404, detail="Health update not found")
    session.delete(item)
    session.commit()


def health_update_dict(item: HealthUpdate) -> dict[str, Any]:
    return {
        "id": item.id,
        "township": item.township,
        "crop_type": item.crop_type,
        "health_status": item.health_status,
        "disease_details": item.disease_details,
        "reported_by": item.reported_by,
        "latitude": item.latitude,
        "longitude": item.longitude,
        "reported_at": item.reported_at,
    }


@router.post("/location-weather", tags=["legacy"])
def location_weather(data: WeatherRequest) -> dict[str, Any]:
    return {
        "region": {
            "name_en": "Myanmar demo region",
            "name_my": "မြန်မာနိုင်ငံ ဒေသ",
        },
        "current": {"temperature_c": 28.0, "rainfall_7d_mm": 120.0, "humidity_pct": 70, "soil_pH_estimate": 6.5},
        "advisories": [
            {
                "severity": "info",
                "icon": "✓",
                "title_en": "Favorable Conditions",
                "title_my": "သင့်တော်သော အခြေအနေများ",
                "message_en": "Seeded satellite fallback data is being used for this location.",
                "message_my": "ဤနေရာအတွက် ခန့်မှန်းဒေတာကို အသုံးပြုနေပါသည်။",
            }
        ],
    }


@router.post("/disease-detect", tags=["legacy"])
async def disease_detect(file: UploadFile = File(...)) -> dict[str, Any]:
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        return {
            "plantName": "",
            "scientificName": "",
            "healthStatus": "Invalid file type. Please upload JPG, PNG, or WEBP.",
            "healthScore": 0,
            "detectedDisease": "",
            "confidenceScore": 0,
            "diseaseSeverity": "",
            "estimatedAffectedArea": "",
            "visibleSymptoms": [],
            "possibleCauses": [],
            "treatmentRecommendations": ["Upload a valid image file."],
            "preventionRecommendations": [],
        }
    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        return {
            "plantName": "",
            "scientificName": "",
            "healthStatus": "File too large. Maximum size is 8 MB.",
            "healthScore": 0,
            "detectedDisease": "",
            "confidenceScore": 0,
            "diseaseSeverity": "",
            "estimatedAffectedArea": "",
            "visibleSymptoms": [],
            "possibleCauses": [],
            "treatmentRecommendations": ["Choose a smaller image."],
            "preventionRecommendations": [],
        }
    return {
        "plantName": "Plant specimen",
        "scientificName": "Species identification unavailable",
        "healthStatus": "Analysis complete — deterministic fallback; no disease model configured",
        "healthScore": 50,
        "detectedDisease": "Unidentified",
        "confidenceScore": 0,
        "diseaseSeverity": "Unknown",
        "estimatedAffectedArea": "Not estimated",
        "visibleSymptoms": ["A trained image model is not configured."],
        "possibleCauses": ["Disease detection requires a validated crop-specific model."],
        "treatmentRecommendations": [
            "Consult a local agricultural extension officer before treatment.",
            "Continue monitoring and isolate visibly affected leaves.",
        ],
        "preventionRecommendations": [
            "Practice crop rotation.",
            "Maintain field hygiene.",
            "Monitor plants regularly.",
        ],
    }


def sse(chunks: list[str]) -> StreamingResponse:
    def stream() -> Iterator[str]:
        for chunk in chunks:
            yield f"data: {json.dumps({'content': chunk, 'done': False})}\n\n"
        yield 'data: {"content": "", "done": true}\n\n'

    return StreamingResponse(stream(), media_type="text/event-stream")


@router.post("/chat", tags=["legacy"])
def chat(data: ChatRequest) -> StreamingResponse:
    last = data.messages[-1].content
    prefix = "မင်္ဂလာပါ။ " if data.language == "my" else "Hello. "
    return sse(
        [
            prefix,
            "I am AgroGuard's local fallback assistant. ",
            f"For your question, start by checking the field readings and the recommendation rule: {last}",
        ]
    )


@router.post("/crop-explanation", tags=["legacy"])
def crop_explanation(data: CropExplanationRequest) -> StreamingResponse:
    text = f"{data.crop} is being evaluated with pH {data.soil_pH:.1f}, rainfall {data.rainfall_mm:.0f} mm, and temperature {data.temperature_c:.1f}°C. This explanation uses transparent demo rules; confirm decisions with local agronomy advice."
    return sse([text])
