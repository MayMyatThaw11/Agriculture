from sqlalchemy import inspect, select, text
from sqlalchemy.orm import Session

from app.db import (
    NDVI,
    Base,
    CropProfile,
    CropRequirement,
    Device,
    Field,
    FieldContext,
    GrowthSimulation,
    Region,
    engine,
)
from app.services import ensure_simulations

REGIONS = [
    ("MMR001", "Sagaing Region", "စစ်ကိုင်းတိုင်းဒေသကြီး"),
    ("MMR002", "Bago Region", "ပဲခူးတိုင်းဒေသကြီး"),
    ("MMR003", "Magway Region", "မကွေးတိုင်းဒေသကြီး"),
    ("MMR004", "Mandalay Region", "မန္တလေးတိုင်းဒေသကြီး"),
    ("MMR005", "Tanintharyi Region", "တနင်္သာရီတိုင်းဒေသကြီး"),
    ("MMR006", "Ayeyarwady Region", "ဧရာဝတီတိုင်းဒေသကြီး"),
    ("MMR007", "Kachin State", "ကချင်ပြည်နယ်"),
    ("MMR008", "Kayah State", "ကယားပြည်နယ်"),
    ("MMR009", "Kayin State", "ကရင်ပြည်နယ်"),
    ("MMR010", "Chin State", "ချင်းပြည်နယ်"),
    ("MMR011", "Mon State", "မွန်ပြည်နယ်"),
    ("MMR012", "Rakhine State", "ရခိုင်ပြည်နယ်"),
    ("MMR013", "Shan State (North)", "ရှမ်းပြည်နယ် (မြောက်ပိုင်း)"),
    ("MMR014", "Yangon Region", "ရန်ကုန်တိုင်းဒေသကြီး"),
    ("MMR015", "Nay Pyi Taw", "နေပြည်တော်"),
    ("MMR016", "Shan State (South)", "ရှမ်းပြည်နယ် (တောင်ပိုင်း)"),
    ("MMR017", "Shan State (East)", "ရှမ်းပြည်နယ် (အရှေ့ပိုင်း)"),
    ("MMR018", "Bago Region (East)", "ပဲခူးတိုင်းဒေသကြီး (အရှေ့ပိုင်း)"),
]


def init_database() -> None:
    Base.metadata.create_all(engine)
    # Keep a previously-created local SQLite demo database usable after the
    # alert lifecycle gained an explicit resolved_at timestamp. Production
    # deployments should apply the Alembic migration instead.
    if engine.url.get_backend_name() == "sqlite":
        with engine.begin() as connection:
            columns = {column["name"] for column in inspect(connection).get_columns("alerts")}
            if "resolved_at" not in columns:
                connection.execute(text("ALTER TABLE alerts ADD COLUMN resolved_at DATETIME"))
    with Session(engine) as session:
        if not session.get(CropProfile, "maize"):
            session.add(
                CropProfile(
                    id="maize",
                    name="Maize",
                    variety="Export-quality field maize",
                    export_use_case="Primary demo crop for explainable field readiness and export quality.",
                    requirements={
                        "temperature_c": {
                            "minimum": 20,
                            "maximum": 35,
                            "unit": "°C",
                            "weight": 1.2,
                            "label": "temperature",
                        },
                        "humidity_percent": {
                            "minimum": 50,
                            "maximum": 90,
                            "unit": "%",
                            "weight": 0.8,
                            "label": "humidity",
                        },
                        "soil_moisture_percent": {
                            "minimum": 45,
                            "maximum": 85,
                            "unit": "%",
                            "weight": 1.5,
                            "label": "soil moisture",
                        },
                        "soil_ph": {"minimum": 5.5, "maximum": 7.5, "unit": "pH", "weight": 1.2, "label": "soil pH"},
                        "light_percent": {"minimum": 40, "maximum": 90, "unit": "%", "weight": 0.7, "label": "light"},
                        "rainfall_mm": {
                            "minimum": 100,
                            "maximum": 300,
                            "unit": "mm / 7 days",
                            "weight": 0.7,
                            "label": "rainfall",
                        },
                    },
                )
            )
        if not session.get(Field, "demo-field"):
            session.add(
                Field(
                    id="demo-field",
                    name="Ayeyarwady Demo Field",
                    latitude=16.8713,
                    longitude=96.1994,
                    area_hectares=2.4,
                    region_label="Ayeyarwady Region",
                    selected_crop_id="maize",
                    is_demo=True,
                )
            )
        else:
            demo_field = session.get(Field, "demo-field")
            if demo_field:
                demo_field.selected_crop_id = "maize"
        if not session.scalar(select(CropRequirement).where(CropRequirement.crop_id == "maize")):
            maize = session.get(CropProfile, "maize")
            for factor, requirement in (maize.requirements if maize else {}).items():
                session.add(
                    CropRequirement(
                        crop_id="maize",
                        factor=factor,
                        minimum_value=requirement.get("minimum"),
                        maximum_value=requirement.get("maximum"),
                        unit=requirement.get("unit", ""),
                        weight=requirement.get("weight", 1),
                        criticality="important",
                        source_reference="AgroGuard demo assumption",
                    )
                )
        for simulation in session.scalars(
            select(GrowthSimulation).where(GrowthSimulation.field_id == "demo-field")
        ).all():
            simulation.crop_id = "maize"
        if not session.get(FieldContext, 1):
            session.add(
                FieldContext(
                    field_id="demo-field",
                    soil_type="Alluvial loam",
                    soil_ph=6.4,
                    temperature_baseline=29.0,
                    rainfall_baseline=165.0,
                    elevation_meters=12.0,
                    source_name="AgroGuard seeded context",
                    source_reference="demo://ayeyeyarwady-field/context-v1",
                    quality="seeded",
                )
            )
        if not session.get(Device, "demo-device"):
            session.add(
                Device(
                    id="demo-device",
                    field_id="demo-field",
                    device_key="wokwi-demo-device",
                    transport="wokwi",
                    is_simulated=True,
                    status="active",
                )
            )
        for pcode, name_en, name_my in REGIONS:
            if not session.get(Region, pcode):
                session.add(Region(pcode=pcode, name_en=name_en, name_my=name_my))
        if not session.scalar(select(NDVI).where(NDVI.region_pcode == "MMR001")):
            for label, vim, viq in [
                ("Jan", 0.42, 72),
                ("Feb", 0.48, 75),
                ("Mar", 0.55, 79),
                ("Apr", 0.62, 83),
                ("May", 0.68, 87),
                ("Jun", 0.71, 90),
            ]:
                session.add(NDVI(region_pcode="MMR001", label=label, vim=vim, viq=viq))
        session.commit()
        ensure_simulations(session, "demo-field", "maize")
