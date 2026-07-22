from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    field_id: Mapped[str] = mapped_column(ForeignKey("fields.id"), index=True)
    crop_id: Mapped[str] = mapped_column(ForeignKey("crop_profiles.id"))
    observation_id: Mapped[int | None] = mapped_column(ForeignKey("sensor_observations.id"))
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    health_score: Mapped[int] = mapped_column(Integer, nullable=False)
    primary_risk: Mapped[str] = mapped_column(String(100), nullable=False)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[str] = mapped_column(String(20), nullable=False)
    decision_mode: Mapped[str] = mapped_column(String(30), default="rules", nullable=False)
    evidence: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
