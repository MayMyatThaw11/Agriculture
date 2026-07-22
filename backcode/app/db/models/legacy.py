from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class HealthUpdate(Base):
    __tablename__ = "health_updates"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    township: Mapped[str] = mapped_column(String(100), nullable=False)
    crop_type: Mapped[str] = mapped_column(String(100), nullable=False)
    health_status: Mapped[str] = mapped_column(String(50), nullable=False)
    disease_details: Mapped[str | None] = mapped_column(Text)
    reported_by: Mapped[str] = mapped_column(String(100), nullable=False)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    reported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class Region(Base):
    __tablename__ = "regions"
    pcode: Mapped[str] = mapped_column(String(10), primary_key=True)
    name_en: Mapped[str] = mapped_column(String(100), nullable=False)
    name_my: Mapped[str] = mapped_column(String(100), nullable=False)


class NDVI(Base):
    __tablename__ = "ndvi_measurements"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    region_pcode: Mapped[str] = mapped_column(String(10), index=True)
    label: Mapped[str] = mapped_column(String(20), nullable=False)
    vim: Mapped[float] = mapped_column(Float, nullable=False)
    viq: Mapped[float] = mapped_column(Float, nullable=False)
