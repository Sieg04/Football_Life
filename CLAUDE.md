# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

Football Life is a football career **simulation and narrative-generation engine**: it generates believable
fictional football careers (progression, setbacks, transfers, injuries, trophies, decline, retirement) that
are eventually presented as ~5–6 minute vertical (9:16) videos. It is not a Football-Manager clone — realism
is in service of producing a *believable story*, not simulation detail for its own sake. See `PROJECT_SPEC.md`
for the full product spec and roadmap, and `FOOTBALL_LIFE_CLAUDE_PROJECT_CONTEXT.md` for a longer narrative
write-up of the product philosophy. Per-phase feature specs live in `PHASE_*_DESIGN_SPEC.md` at the repo root.

Stack: **FastAPI + SQLAlchemy + Alembic + SQLite** backend, **Angular** frontend, talking over REST/JSON.

## Commands

### Backend (from `backend/`)

```bash
# Install deps (use the repo venv's python)
../venv/Scripts/python.exe -m pip install -r requirements.txt

# Run the API (http://localhost:8000)
../venv/Scripts/python.exe -m uvicorn app.main:app --reload

# Run all tests
../venv/Scripts/python.exe -m pytest

# Run a single test file / test
../venv/Scripts/python.exe -m pytest tests/test_career_engine.py
../venv/Scripts/python.exe -m pytest tests/test_career_engine.py::test_some_case -v

# Migrations (Alembic)
../venv/Scripts/python.exe -m alembic upgrade head
../venv/Scripts/python.exe -m alembic revision -m "description" --autogenerate

# Seed the database from data/world.json
../venv/Scripts/python.exe scripts/seed_database.py
```

`pytest.ini` sets `pythonpath = .`, so tests import `app.*` directly — run pytest from `backend/`.
A `venv/` already exists at the repo root; there's also a root-level `python3.bat`/`python3.cmd` shim.

### Frontend (from `frontend/football-life/`)

```bash
npm install
ng serve        # dev server on http://localhost:4200, proxies to backend via CORS
ng build
ng test          # Karma/Jasmine unit tests
```

## Architecture

Strict layered flow, enforced by convention (see `.github/instructions/reglas.instructions.md` and
`AGENTS.md` for the full rules both Copilot and other agents are expected to follow):

```
Angular (frontend/)
   ↓ HTTP/REST
FastAPI routers (backend/app/api/*.py)
   ↓
Application Services (backend/app/<domain>/service.py)
   ↓
Simulation Engine / Domain (backend/app/<domain>/engine.py, domain.py)
   ↓
Persistence (SQLAlchemy models/repositories, Alembic migrations)
```

**The Simulation Engine must stay independent of FastAPI/HTTP/SQLAlchemy/SQLite/Angular.** Domain logic should
be callable and testable as plain Python without spinning up the web stack. Database access happens in
services/repositories, never inside engine/domain code.

### Backend module layout (`backend/app/`)

Each subsystem is its own package with a consistent internal split:
- `domain.py` — dataclasses/models representing pure domain state (no framework deps)
- `engine.py` — the actual simulation/business logic operating on domain state
- `service.py` — application-service orchestration (session state, calling engine + persistence)
- `repository.py` — persistence access, where present

Subsystems: `career/` (career sessions, archetypes, reputation, transfers-in-career), `competition/`
(fixtures, standings, form, season orchestration), `event/` (event/decision/narrative/presentation/replay/script
engines — several parallel engines under one package), `football/` (match/injury/award/international/statistics
engines), `match/` (lineup, performance, resolution, aggregation), `player/` (generation, engine), `transfer/`
(market, offers, contracts, decisions), `world/` (world generation/seeding/calculations), `models/`
(SQLAlchemy ORM models: `base.py`, `career.py`, `competition.py`, `world.py`), `api/` (FastAPI routers, one per
subsystem, wired up in `main.py`), `core/` (`config.py` settings via pydantic-settings + `.env`, `database.py`).

Config is centralized in `app/core/config.py` (`Settings`, cached via `get_settings()`); DB URL, CORS origins,
etc. come from `.env` there.

### Frontend layout (`frontend/football-life/src/app/`)

Angular 19, standalone components (no NgModules). `career/` holds one component folder per screen/widget
(career-dashboard, career-timeline, career-transfer, career-decision, career-script, capture-view/
career-recording-mode for the video-capture presentation flow, etc.). `core/services/` holds the HTTP client
services (`career-session.service.ts`, `presentation.service.ts`, `replay.service.ts`) and `core/models/` the
matching TypeScript interfaces for API payloads. The frontend must not contain simulation/business rules
(overall calculation, development, transfer/event probabilities) — those stay server-side; the frontend only
consumes results.

### Data-driven rules

Game rules that would otherwise be large hardcoded tables live as JSON under `backend/data/rules/`
(`player_attributes.json`, `player_development.json`, `player_traits.json`, `player_roles.json`,
`career_archetypes.json`, `transfers.json`, `events.json`, `narrative.json`, `presentation.json`, `replay.json`,
`script.json`, `season_transition.json`), loaded at runtime rather than embedded in engine code. World data
(clubs/leagues) is `backend/data/world.json`, consumed by `world/seed.py` / `scripts/seed_database.py`.

## Development process rules (important — read before large changes)

This repo is developed **phase by phase**, and there is an explicit, detailed rulebook the team expects any
agent (Claude, Copilot, Jules) to follow: `.github/instructions/reglas.instructions.md` (canonical, in
English) and `AGENTS.md` (equivalent, written for Jules). Key points distilled from both:

- **Don't build multiple phases at once.** Implement only the requested/approved scope; do not silently pull
  in functionality from a later phase (e.g. don't add transfer logic while implementing the player engine).
  `PROJECT_SPEC.md` defines the phase roadmap.
- **No fake/placeholder implementations.** Don't return stub success responses (`{"status": "implemented"}`)
  or build empty "future" engines to make the folder structure look complete — build a system when its phase
  actually begins.
- **Determinism matters.** Careers should eventually be reproducible from `seed + initial state + rules
  version`. Avoid scattering raw `random` calls through simulation code; route through a centralized RNG
  abstraction.
- **Single `Player` model.** There is one fundamental `Player`; a generic world player is `Player +
  ClubMembership`, a career protagonist is `Player + Career`. Don't fork into separate
  `GenericSquadPlayer`/`CareerPlayer` domain models.
- **Current Ability vs OVR are distinct.** Current Ability is general football quality; OVR is
  position-specific effectiveness. Changing a player's position must not mutate underlying attributes.
- **Testing priority is domain logic over API surface** — player calculations, overall/position weighting,
  development, aging, match calculations, transfers, event conditions/decision resolution, deterministic RNG.
  When fixing a bug, add a regression test. For simulation/balance work, assert on distributions across
  multiple seeds rather than exact outputs from one seed.
- **Migrations:** schema changes go through a proper Alembic revision; never silently destroy persistent data.
- Priority ordering when trading off decisions: simulation quality → career variety → narrative quality → data
  integrity → maintainability → performance → visual quality → future extensibility.
