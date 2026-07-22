from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class APIModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


class HealthResponse(APIModel):
    status: Literal["ok"]
    service_name: str
    version: str
    environment: str


class FieldCreate(APIModel):
    name: str = Field(min_length=1, max_length=160)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    area_hectares: float | None = Field(default=None, gt=0, le=100000)
    region_label: str = Field(min_length=1, max_length=160)
    crop_id: str | None = None


class FieldResponse(FieldCreate):
    id: str
    selected_crop_id: str | None = None
    is_demo: bool
    status: str
    created_at: datetime
    current_status: str | None = None


class ContextResponse(APIModel):
    id: int
    field_id: str
    soil_type: str
    soil_ph: float
    temperature_baseline: float
    rainfall_baseline: float
    elevation_meters: float
    source_name: str
    source_reference: str
    quality: str
    retrieved_at: datetime


class CropResponse(APIModel):
    id: str
    name: str
    variety: str | None
    export_use_case: str
    profile_version: str
    source_type: str
    source_reference: str
    requirements: dict[str, Any]


class CropSelectionRequest(APIModel):
    crop_id: str
    season_label: str = Field(default="2026-main", min_length=1, max_length=50)


class ObservationCreate(APIModel):
    event_id: str = Field(min_length=1, max_length=120)
    device_id: str
    field_id: str
    observed_at: datetime | None = None
    temperature_c: float = Field(ge=-40, le=70)
    humidity_percent: float = Field(ge=0, le=100)
    soil_moisture_percent: float = Field(ge=0, le=100)
    soil_ph: float = Field(ge=0, le=14)
    light_percent: float = Field(ge=0, le=100)
    source_mode: Literal["live", "simulated", "manual", "replay"] = "simulated"


class ObservationResponse(ObservationCreate):
    id: int
    quality: str
    received_at: datetime


class Evidence(APIModel):
    factor: str
    observed_value: float
    minimum: float | None
    maximum: float | None
    unit: str
    in_range: bool
    source: str


class AssessmentResponse(APIModel):
    id: int
    field_id: str
    crop_id: str
    status: Literal["healthy", "warning", "critical"]
    health_score: int = Field(ge=0, le=100)
    primary_risk: str
    recommendation: str
    evidence: list[Evidence]
    confidence: Literal["high", "medium", "low", "unknown"]
    mode: Literal["live", "simulated", "seeded", "replay", "degraded"]
    updated_at: datetime


class AlertResponse(APIModel):
    id: int
    field_id: str
    assessment_id: int
    severity: Literal["warning", "critical"]
    risk_type: str
    message: str
    status: str
    opened_at: datetime


class NotificationResponse(APIModel):
    id: int
    alert_id: int
    channel: str
    destination_ref: str
    delivery_key: str
    status: str
    attempt_count: int
    last_error_code: str | None
    sent_at: datetime | None


class GrowthEventResponse(APIModel):
    event_date: str
    growth_stage: str
    health_index: int
    intervention: str | None
    risk_marker: str | None


class GrowthSimulationResponse(APIModel):
    id: int
    field_id: str
    crop_id: str
    scenario_type: str
    seed: str
    is_illustrative: bool
    events: list[GrowthEventResponse]


class GrowthStartRequest(APIModel):
    scenario: Literal["healthy", "dry-soil", "heat-stress"] = "healthy"


class DemoResetRequest(APIModel):
    scenario: Literal["healthy", "dry-soil", "heat-stress"] = "healthy"


class WeatherRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    language: Literal["en", "my"] = "en"


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=30)
    language: Literal["en", "my"] = "en"


class CropExplanationRequest(BaseModel):
    soil_pH: float = Field(ge=0, le=14)
    rainfall_mm: float = Field(ge=0, le=5000)
    temperature_c: float = Field(ge=-40, le=70)
    crop: str = Field(min_length=1, max_length=100)
    language: Literal["en", "my"] = "en"


class HealthUpdateCreate(APIModel):
    township: str = Field(min_length=1, max_length=100)
    crop_type: str = Field(min_length=1, max_length=100)
    health_status: str = Field(min_length=1, max_length=50)
    disease_details: str | None = None
    reported_by: str = Field(min_length=1, max_length=100)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)


class HealthUpdateResponse(HealthUpdateCreate):
    id: int
    reported_at: datetime
