# AgroGuard backend architecture

## Scope

This document describes the implemented Phase 4–6 backend in `backcode`. It is a demo-first modular monolith: one FastAPI process, one relational database, and explicit service boundaries. The system is intentionally small enough to run locally while keeping the field decision loop testable.

```text
field + crop context
        |
        v
normalized observation -> assessment/rule evidence -> alert lifecycle -> Telegram delivery
                                                       |
                                                       v
                                             12-month growth replay
```

## Runtime components

| Component | Responsibility | Fallback |
|---|---|---|
| FastAPI API | Validation, versioned routes, response contracts | `/api` aliases remain compatible with the current React client |
| SQLAlchemy persistence | Fields, crop profiles, contexts, devices, observations, assessments, alerts, deliveries, simulations | SQLite for local demo; PostgreSQL/Supabase URL for deployment |
| Suitability service | Pure, explainable range scoring and recommendation | Rules always available; no model key required |
| Assessment service | Combines baseline context and latest reading, stores evidence, raises alert intent | Seeded context and deterministic rules |
| Alerting service | Warning/critical transition, fingerprint, one-hour cooldown, lifecycle state | In-app alert remains visible if Telegram is unavailable |
| Telegram adapter | Formats and sends field/risk/recommendation messages | `suppressed` when credentials are absent; `failed` on provider error |
| Growth simulation service | Healthy, dry-soil, and heat-stress replays for guided/control comparison | Deterministic 12-month illustrative timeline |
| Seed/reset service | Keeps one demo field and simulated device repeatable | Reset only removes dynamic demo rows, not user health reports |

## API surface

The documented contract is `/api/v1`; the same routes are mounted at `/api` for the existing frontend.

| Route | Purpose |
|---|---|
| `GET /fields`, `GET /fields/{id}`, `GET /fields/{id}/context` | Load the selected field and baseline evidence |
| `GET /crops`, `POST /fields/{id}/crop-selection` | Load and select the active crop profile |
| `POST /observations` | Validate and ingest a normalized sensor event idempotently |
| `GET/POST /fields/{id}/assessment...` | Read or recompute current status and recommendation |
| `GET /fields/{id}/alerts` | Show field alerts in the dashboard |
| `PATCH /alerts/{id}/acknowledge`, `PATCH /alerts/{id}/resolve` | Move alert lifecycle state |
| `POST /fields/{id}/growth/start`, `GET /fields/{id}/growth/timeline` | Start and read illustrative comparison replays |
| `POST /demo/reset` | Clear dynamic demo rows and re-seed a scenario |

Legacy dashboard, weather, NDVI, disease, chat, crop explanation, and health-update routes are retained so existing React screens do not break.

## Alert flow

1. Observation ingestion stores the event and recomputes assessment.
2. A warning or critical assessment calls `services/alerting.py`.
3. The service searches for the same field/risk in the previous hour.
4. A new risk creates an in-app alert and a Telegram delivery row.
5. A repeated risk creates a `suppressed` delivery row and does not create another alert.
6. Telegram credentials are read only from settings. Failures become `failed` delivery state, never a failed assessment.

## Data modes and honesty

The response exposes `mode` and evidence source. Seeded, simulated, replay, and estimated values are not presented as measured farm truth. Growth indices are always returned with `isIllustrative=true`; they are a storytelling comparison, not a yield forecast.

## Migration and deployment

`migrations/versions/0002_add_core_domain_tables.py` creates the Phase 6 core tables and seeds the demo maize field. Run:

```powershell
cd backcode
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

For a local no-setup run, application startup creates the SQLite schema and applies the small `resolved_at` compatibility alteration. Use PostgreSQL/Supabase plus Alembic for shared environments.
