"""Create AgroGuard core domain tables and seed the demo field.

This migration is intentionally self-contained for the standalone backcode
folder. It can be applied to a new PostgreSQL/Supabase database, while the
application startup keeps a SQLite-only compatibility check for local demos.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "crop_profiles",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("variety", sa.String(100)),
        sa.Column("export_use_case", sa.Text(), nullable=False),
        sa.Column("profile_version", sa.String(30), nullable=False),
        sa.Column("source_type", sa.String(40), nullable=False),
        sa.Column("source_reference", sa.String(255), nullable=False),
        sa.Column("requirements", sa.JSON(), nullable=False),
    )
    op.create_table(
        "crop_requirements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("crop_id", sa.String(64), sa.ForeignKey("crop_profiles.id"), nullable=False),
        sa.Column("factor", sa.String(50), nullable=False),
        sa.Column("minimum_value", sa.Float()),
        sa.Column("maximum_value", sa.Float()),
        sa.Column("unit", sa.String(30), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column("criticality", sa.String(30), nullable=False),
        sa.Column("source_reference", sa.String(255), nullable=False),
    )
    op.create_table(
        "fields",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("area_hectares", sa.Float()),
        sa.Column("region_label", sa.String(160), nullable=False),
        sa.Column("selected_crop_id", sa.String(64), sa.ForeignKey("crop_profiles.id")),
        sa.Column("is_demo", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("status", sa.String(30), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "field_context_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("field_id", sa.String(64), sa.ForeignKey("fields.id"), nullable=False),
        sa.Column("soil_type", sa.String(100), nullable=False),
        sa.Column("soil_ph", sa.Float(), nullable=False),
        sa.Column("temperature_baseline", sa.Float(), nullable=False),
        sa.Column("rainfall_baseline", sa.Float(), nullable=False),
        sa.Column("elevation_meters", sa.Float(), nullable=False),
        sa.Column("source_name", sa.String(100), nullable=False),
        sa.Column("source_reference", sa.String(255), nullable=False),
        sa.Column("quality", sa.String(30), nullable=False),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "sensor_devices",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("field_id", sa.String(64), sa.ForeignKey("fields.id"), nullable=False),
        sa.Column("device_key", sa.String(120), nullable=False, unique=True),
        sa.Column("transport", sa.String(30), nullable=False),
        sa.Column("is_simulated", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "sensor_observations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_id", sa.String(120), nullable=False, unique=True),
        sa.Column("device_id", sa.String(64), sa.ForeignKey("sensor_devices.id"), nullable=False),
        sa.Column("field_id", sa.String(64), sa.ForeignKey("fields.id"), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("temperature_c", sa.Float(), nullable=False),
        sa.Column("humidity_percent", sa.Float(), nullable=False),
        sa.Column("soil_moisture_percent", sa.Float(), nullable=False),
        sa.Column("soil_ph", sa.Float(), nullable=False),
        sa.Column("light_percent", sa.Float(), nullable=False),
        sa.Column("source_mode", sa.String(30), nullable=False),
        sa.Column("quality", sa.String(30), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "assessments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("field_id", sa.String(64), sa.ForeignKey("fields.id"), nullable=False),
        sa.Column("crop_id", sa.String(64), sa.ForeignKey("crop_profiles.id"), nullable=False),
        sa.Column("observation_id", sa.Integer(), sa.ForeignKey("sensor_observations.id")),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("health_score", sa.Integer(), nullable=False),
        sa.Column("primary_risk", sa.String(100), nullable=False),
        sa.Column("recommendation", sa.Text(), nullable=False),
        sa.Column("confidence", sa.String(20), nullable=False),
        sa.Column("decision_mode", sa.String(30), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("field_id", sa.String(64), sa.ForeignKey("fields.id"), nullable=False),
        sa.Column("assessment_id", sa.Integer(), sa.ForeignKey("assessments.id"), nullable=False),
        sa.Column("fingerprint", sa.String(200), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("risk_type", sa.String(100), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True)),
        sa.Column("resolved_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "notification_deliveries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("alert_id", sa.Integer(), sa.ForeignKey("alerts.id"), nullable=False),
        sa.Column("channel", sa.String(30), nullable=False),
        sa.Column("destination_ref", sa.String(120), nullable=False),
        sa.Column("delivery_key", sa.String(220), nullable=False, unique=True),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column("last_error_code", sa.String(80)),
        sa.Column("sent_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "growth_simulations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("field_id", sa.String(64), sa.ForeignKey("fields.id"), nullable=False),
        sa.Column("crop_id", sa.String(64), sa.ForeignKey("crop_profiles.id"), nullable=False),
        sa.Column("scenario_type", sa.String(30), nullable=False),
        sa.Column("seed", sa.String(80), nullable=False),
        sa.Column("is_illustrative", sa.Boolean(), nullable=False),
    )
    op.create_table(
        "growth_simulation_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("simulation_id", sa.Integer(), sa.ForeignKey("growth_simulations.id"), nullable=False),
        sa.Column("event_date", sa.String(10), nullable=False),
        sa.Column("growth_stage", sa.String(40), nullable=False),
        sa.Column("health_index", sa.Integer(), nullable=False),
        sa.Column("intervention", sa.Text()),
        sa.Column("risk_marker", sa.String(100)),
    )
    op.get_bind().exec_driver_sql("""INSERT INTO crop_profiles (id, name, variety, export_use_case, profile_version, source_type, source_reference, requirements)
        VALUES ('maize', 'Maize', 'Export-quality field maize', 'Primary demo crop for explainable field readiness and export quality.', 'demo-1', 'demo_assumption', 'AgroGuard demo assumption',
        '{"temperature_c":{"minimum":18,"maximum":32,"unit":"C","weight":1.2,"label":"temperature"},"humidity_percent":{"minimum":45,"maximum":85,"unit":"%","weight":0.8,"label":"humidity"},"soil_moisture_percent":{"minimum":35,"maximum":75,"unit":"%","weight":1.5,"label":"soil moisture"},"soil_ph":{"minimum":5.5,"maximum":7.5,"unit":"pH","weight":1.2,"label":"soil pH"},"light_percent":{"minimum":50,"maximum":95,"unit":"%","weight":0.7,"label":"light"},"rainfall_mm":{"minimum":80,"maximum":250,"unit":"mm / 7 days","weight":0.7,"label":"rainfall"}}')""")
    op.execute(
        sa.text(
            "INSERT INTO fields (id, name, latitude, longitude, area_hectares, region_label, selected_crop_id, is_demo, status) VALUES ('demo-field', 'Ayeyarwady Demo Field', 16.8713, 96.1994, 2.4, 'Ayeyarwady Region', 'maize', true, 'active')"
        )
    )
    op.execute(
        sa.text(
            "INSERT INTO field_context_snapshots (field_id, soil_type, soil_ph, temperature_baseline, rainfall_baseline, elevation_meters, source_name, source_reference, quality) VALUES ('demo-field', 'Alluvial loam', 6.4, 29, 165, 12, 'AgroGuard seeded context', 'demo://ayeyeyarwady-field/context-v1', 'seeded')"
        )
    )
    op.execute(
        sa.text(
            "INSERT INTO sensor_devices (id, field_id, device_key, transport, is_simulated, status) VALUES ('demo-device', 'demo-field', 'wokwi-demo-device', 'wokwi', true, 'active')"
        )
    )


def downgrade() -> None:
    for table in (
        "growth_simulation_events",
        "growth_simulations",
        "notification_deliveries",
        "alerts",
        "assessments",
        "sensor_observations",
        "sensor_devices",
        "field_context_snapshots",
        "fields",
        "crop_requirements",
        "crop_profiles",
    ):
        op.drop_table(table)
