````markdown
# FOOTBALL LIFE — JULES DEVELOPMENT INSTRUCTIONS

## 1. Source of truth

Before making any changes, always read:

1. `PROJECT_SPEC.md`
2. `.github/instructions/reglas.instructions.md`

`PROJECT_SPEC.md` defines what Football Life should be.

`.github/instructions/reglas.instructions.md` defines how the project must be developed.

These documents are complementary and must not be treated as interchangeable.

---

## 2. Incremental development

### CRITICAL

DO NOT BUILD THE ENTIRE SYSTEM IN ONE PASS.

Football Life is developed phase by phase.

For every requested phase:

```text
READ
 ↓
ANALYZE
 ↓
PLAN
 ↓
IMPLEMENT
 ↓
TEST
 ↓
VERIFY
 ↓
REPORT
````

Never implement future phases automatically.

Never combine multiple major phases unless explicitly requested.

---

## 3. Jules workflow

Before modifying code:

1. Read the relevant project specification.
2. Inspect the current repository state.
3. Inspect existing implementations.
4. Identify dependencies.
5. Create a concise implementation plan.
6. Stop and wait for approval if the task is a major architectural or phase-level change.

For an explicitly approved implementation task:

1. Implement only the approved scope.
2. Run relevant tests.
3. Run regression tests.
4. Verify the application.
5. Report all changes and results.
6. Do not continue into future phases.

---

## 4. Pull request discipline

Each major phase or architectural refactor should be isolated in its own branch/PR.

A PR should contain:

* Only the requested phase.
* Tests for the implemented behavior.
* Required migrations/configuration.
* No unrelated cleanup.
* No future systems.

Do not mix:

```text
Phase 4
+
Phase 5
```

in one PR.

---

## 5. Architecture

The project must maintain:

```text
Angular
   ↓
FastAPI
   ↓
Application Services
   ↓
Domain
   ↓
Persistence
```

The Simulation Engine and domain logic must remain independent of:

* Angular
* FastAPI
* HTTP
* SQLAlchemy
* SQLite
* REST

Pure business calculations should be testable without infrastructure.

---

## 6. Simulation Engine independence

Never put football simulation rules into:

* Angular components
* FastAPI routes
* SQLAlchemy models
* Database repositories

The Simulation Engine must operate on structured domain state.

Preferred flow:

```text
API
 ↓
Application Service
 ↓
Simulation / Domain
 ↓
Domain Result
 ↓
Application Service
 ↓
Persistence
```

---

## 7. Determinism

The project requires deterministic simulation.

Whenever randomness is used:

```text
seed
+
same initial state
+
same rules version
=
same result
```

Use a centralized RNG abstraction.

Do not scatter uncontrolled random calls throughout the codebase.

---

## 8. Data-driven rules

Prefer configuration files for:

* Attribute weights
* Position weights
* Role definitions
* Development profiles
* Development coefficients
* Event probabilities
* Trait definitions

Do not hardcode large rule collections into business logic.

---

## 9. No fake functionality

Do not create fake implementations merely to satisfy future architecture.

Do not create:

```python
return {"status": "implemented"}
```

for systems that are not implemented.

Do not create empty placeholder engines for future phases unless explicitly requested for an architectural reason.

---

## 10. Player domain

Football Life must have a single fundamental `Player` model.

Generic world player:

```text
Player
+
ClubMembership
```

Career protagonist:

```text
Player
+
Career
```

Do not create:

```text
GenericSquadPlayer
CareerPlayer
```

as independent football models.

---

## 11. Current Ability vs OVR

Always preserve the distinction:

```text
Current Ability
=
general football quality
```

```text
OVR
=
effectiveness in a particular position
```

Changing position must not mutate the underlying attributes.

---

## 12. Career Engine

The Career Engine must eventually simulate:

```text
Season
 ↓
State
 ↓
Performance
 ↓
Development
 ↓
World evolution
 ↓
Next season
```

Development must not simply be:

```text
OVR + fixed amount
```

It must depend on contextual factors defined in `PROJECT_SPEC.md`.

---

## 13. Phase discipline

When implementing a phase:

DO NOT implement systems belonging to later phases.

For example, while implementing Phase 4:

Do not implement:

* Match Engine
* Transfers
* Contracts
* Injuries
* Narrative
* Community
* TikTok presentation

unless explicitly included in the approved task.

---

## 14. Testing

Run:

1. New tests.
2. Relevant subsystem tests.
3. Full regression suite.

A change is not complete if it breaks previously working functionality.

For simulation systems, also test:

* Determinism
* Distribution sanity
* Boundary values
* Reproducibility

---

## 15. Migrations

When database schema changes are required:

1. Create a proper Alembic migration.
2. Verify upgrade behavior.
3. Verify the application against the new schema.
4. Document destructive migrations.

Never silently destroy persistent data unless the specification explicitly allows rebuilding generated seed data.

---

## 16. Balance changes

When adjusting simulation probabilities or distributions:

Do not optimize against a single seed.

Use:

* Multiple seeds
* Statistical distributions
* Broad range assertions
* Regression checks

Avoid fragile tests that require exact random outputs unless determinism itself is being tested.

---

## 17. Performance

Do not prematurely optimize.

However:

* Avoid unnecessary database queries inside simulation loops.
* Avoid repeated expensive calculations when values can be cached.
* Keep pure simulation calculations lightweight.
* Preserve the ability to run many careers for balance testing.

---

## 18. Documentation

Update documentation when:

* Architecture changes
* Public API changes
* New phases are completed
* Important simulation rules change

Do not rewrite `PROJECT_SPEC.md` unless explicitly requested.

---

## 19. Reporting

At the end of an implementation task report:

### Implemented

What changed.

### Files

Created, modified and removed files.

### Tests

Tests added and tests executed.

### Verification

Builds, migrations, seed checks and runtime verification.

### Issues

Known warnings, limitations or concerns.

### Next step

Only the next logical phase or review step.

Do not continue automatically.

---

## 20. Final rule

Football Life is a simulation project first and a UI project second.

Prioritize:

```text
Simulation quality
↓
Career variety
↓
Narrative potential
↓
Data integrity
↓
Maintainability
↓
Visual quality
```

Most importantly:

> Implement only the approved scope.

> Keep the domain independent.

> Keep every phase reproducible.

> Test before declaring completion.

````

