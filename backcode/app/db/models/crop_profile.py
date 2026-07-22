from typing import Any

from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CropProfile(Base):
    __tablename__ = "crop_profiles"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    variety: Mapped[str | None] = mapped_column(String(100))
    export_use_case: Mapped[str] = mapped_column(Text, nullable=False)
    profile_version: Mapped[str] = mapped_column(String(30), default="demo-1", nullable=False)
    source_type: Mapped[str] = mapped_column(String(40), default="demo_assumption", nullable=False)
    source_reference: Mapped[str] = mapped_column(String(255), default="AgroGuard demo assumption", nullable=False)
    requirements: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
