from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Observation(Base):
    __tablename__ = "sensor_observations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_id: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    device_id: Mapped[str] = mapped_column(ForeignKey("sensor_devices.id"), index=True)
    field_id: Mapped[str] = mapped_column(ForeignKey("fields.id"), index=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    temperature_c: Mapped[float] = mapped_column(Float, nullable=False)
    humidity_percent: Mapped[float] = mapped_column(Float, nullable=False)
    soil_moisture_percent: Mapped[float] = mapped_column(Float, nullable=False)
    soil_ph: Mapped[float] = mapped_column(Float, nullable=False)
    light_percent: Mapped[float] = mapped_column(Float, nullable=False)
    source_mode: Mapped[str] = mapped_column(String(30), default="simulated", nullable=False)
    quality: Mapped[str] = mapped_column(String(30), default="good", nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
