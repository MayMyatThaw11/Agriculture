from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class GrowthSimulation(Base):
    __tablename__ = "growth_simulations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    field_id: Mapped[str] = mapped_column(ForeignKey("fields.id"), index=True)
    crop_id: Mapped[str] = mapped_column(ForeignKey("crop_profiles.id"))
    scenario_type: Mapped[str] = mapped_column(String(30), nullable=False)
    seed: Mapped[str] = mapped_column(String(80), nullable=False)
    is_illustrative: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
