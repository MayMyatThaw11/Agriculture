# AgroGuard backend

This is the FastAPI backend for the agriculture dashboard. It implements the demo decision loop described in `context-kit`:

`field -> context -> crop -> sensor reading -> assessment -> alert -> growth replay`

The Phase 4–6 implementation also provides alert acknowledgement/resolution,
Telegram delivery tracking with a one-hour cooldown, a 12-month guided versus
normal-control replay, a safe demo reset, and real dashboard assessment data.

The default database is a local SQLite file (`backcode/agroguard.db`) so the demo can run without PostgreSQL. Set `AGROGUARD_DATABASE_URL` to a PostgreSQL SQLAlchemy URL for a deployed environment.

## Run locally

```powershell
cd backcode
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Format and lint Python with the repository VS Code settings or directly:

```powershell
python -m ruff format app tests migrations
python -m ruff check app tests migrations
```

Open `http://127.0.0.1:8000/docs` for the API contract.

Apply the PostgreSQL/Supabase schema with:

```powershell
python -m alembic upgrade head
```

The React app can use the API with:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
VITE_ENABLE_API=true
```

## Key demo calls

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/fields
Invoke-RestMethod http://127.0.0.1:8000/api/v1/fields/demo-field/assessment
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/v1/observations -ContentType application/json -Body (@{
  eventId = "demo-dry-1"; deviceId = "demo-device"; fieldId = "demo-field"; sourceMode = "simulated";
  soilMoisturePercent = 12; temperatureC = 30; humidityPercent = 68; soilPh = 6.4; lightPercent = 60
} | ConvertTo-Json)
Invoke-RestMethod http://127.0.0.1:8000/api/v1/alerts
Invoke-RestMethod http://127.0.0.1:8000/api/fields/demo-field/growth/timeline
Invoke-RestMethod -Method Patch -Uri http://127.0.0.1:8000/api/alerts/1/acknowledge
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/demo/reset -ContentType application/json -Body '{"scenario":"healthy"}'
```

Telegram delivery is adapter-based. Without credentials the backend keeps the alert and records a safe `suppressed` delivery instead of failing the assessment.
