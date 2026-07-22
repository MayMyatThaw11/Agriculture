from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CropRequirement(Base):
    __tablename__ = "crop_requirements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    crop_id: Mapped[str] = mapped_column(ForeignKey("crop_profiles.id"), index=True)
    factor: Mapped[str] = mapped_column(String(50), nullable=False)
    minimum_value: Mapped[float | None] = mapped_column(Float)
    maximum_value: Mapped[float | None] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(30), nullable=False)
    weight: Mapped[float] = mapped_column(Float, default=1, nullable=False)
    criticality: Mapped[str] = mapped_column(String(30), default="important", nullable=False)
    source_reference: Mapped[str] = mapped_column(String(255), nullable=False)
