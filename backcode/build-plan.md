# AgroGuard implementation build plan

This is the completed Phase 1–6 execution plan for the current repository. Each phase has an observable exit condition and a fallback.

## Phase 1 — foundation

- Create the React/FastAPI boundary and `/health` probes.
- Configure environment-backed database, CORS, LLM, weather, and Telegram settings.
- Keep secrets out of source control.
- Exit: backend starts locally and OpenAPI loads.

## Phase 2 — field and crop context

- Seed one Ayeyarwady demo field, one simulated device, one maize profile, and one context snapshot.
- Return field coordinates, selected crop, pH, baseline temperature, rainfall, source, and quality.
- Exit: `GET /api/fields` and `/context` show a stable seeded field without external providers.

## Phase 3 — observation and assessment

- Validate sensor ranges and future timestamps.
- Make `event_id` idempotent.
- Score crop fit with weighted ranges and return status, score, risk, recommendation, evidence, confidence, and mode.
- Exit: healthy input remains healthy; dry soil and heat stress produce deterministic warning/critical output.

## Phase 4 — alerts and Telegram

- Store alerts and delivery attempts separately.
- Add warning/critical transition handling, risk fingerprint, and one-hour cooldown.
- Add acknowledge and resolve lifecycle actions.
- Send a formatted Telegram message when configured; preserve the in-app alert on absent credentials or delivery failure.
- Exit: one risk produces one alert; repeated readings produce a suppressed delivery, not Telegram spam.

## Phase 5 — growth comparison

- Start a replay with `healthy`, `dry-soil`, or `heat-stress` scenario.
- Generate twelve monthly events across germination, vegetative, flowering, fruiting, and harvest stages.
- Let the IoT-guided path recover after intervention and let normal-control degrade when intervention is missed.
- Mark both paths illustrative.
- Exit: timeline endpoint returns two comparable 12-event simulations.

## Phase 6 — migration, seed, and integration

- Apply migration `0002_add_core_domain_tables.py` to a fresh PostgreSQL/Supabase database.
- Keep SQLite startup fallback for the local demo.
- Make dashboard stats reflect fields, assessments, observations, active alerts, and current field assessments.
- Add `/api` aliases for the current frontend and retain `/api/v1` as the stable contract.
- Add VS Code Ruff formatter settings and repeatable pytest coverage.
- Exit: select field → ingest reading → assessment → alert → growth comparison → reset and replay.

## Verification checklist

- [x] Health and OpenAPI endpoints.
- [x] Seeded field, maize profile, context, and simulated device.
- [x] Observation validation and duplicate protection.
- [x] Explainable assessment and recommendation.
- [x] Alert cooldown and notification delivery tracking.
- [x] Acknowledge and resolve lifecycle routes.
- [x] Twelve-month guided/control growth replay.
- [x] Demo reset without deleting non-demo health reports.
- [x] Migration, environment template, formatter settings, and tests.
