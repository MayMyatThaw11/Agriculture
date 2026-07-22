from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class FieldContext(Base):
    __tablename__ = "field_context_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    field_id: Mapped[str] = mapped_column(ForeignKey("fields.id"), index=True)
    soil_type: Mapped[str] = mapped_column(String(100), nullable=False)
    soil_ph: Mapped[float] = mapped_column(Float, nullable=False)
    temperature_baseline: Mapped[float] = mapped_column(Float, nullable=False)
    rainfall_baseline: Mapped[float] = mapped_column(Float, nullable=False)
    elevation_meters: Mapped[float] = mapped_column(Float, nullable=False)
    source_name: Mapped[str] = mapped_column(String(100), nullable=False)
    source_reference: Mapped[str] = mapped_column(String(255), nullable=False)
    quality: Mapped[str] = mapped_column(String(30), default="seeded", nullable=False)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
