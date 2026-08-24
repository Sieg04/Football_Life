````markdown
# FOOTBALL LIFE — DEVELOPMENT RULES FOR GITHUB COPILOT

## 1. Source of truth

Before making changes, always read:

`PROJECT_SPEC.md`

`PROJECT_SPEC.md` is the canonical source of truth for:

- Product vision
- Functional requirements
- Game systems
- Architecture
- Visual direction
- MVP scope
- Roadmap
- Future features

This file (`reglas.instructions.md`) is ONLY the source of truth for development behavior and coding rules.

Do not duplicate the complete project specification here.

---

## 2. Incremental development

### CRITICAL RULE

> DO NOT BUILD THE ENTIRE SYSTEM IN ONE PASS.

Football Life must be developed phase by phase.

Never attempt to implement the complete simulator in a single response, command or coding session.

The development process must follow:

```text
PLAN
 ↓
IMPLEMENT
 ↓
TEST
 ↓
VERIFY
 ↓
FIX
 ↓
NEXT PHASE
````

Each phase must leave the project in a working state.

Do not automatically continue to the next phase.

---

## 3. Before modifying code

Before making changes:

1. Inspect the existing project structure.
2. Read the relevant sections of `PROJECT_SPEC.md`.
3. Inspect existing implementations related to the requested change.
4. Identify dependencies between the requested change and existing systems.
5. Explain briefly what will be implemented.
6. Implement only the requested scope.

Do not modify unrelated code.

---

## 4. Phase boundaries

Never implement functionality from a future phase unless explicitly requested.

For example:

If working on the player engine, do NOT automatically implement:

* Transfers
* Injuries
* Narrative engine
* Community voting
* TikTok integration
* Presentation mode

Respect the roadmap defined in `PROJECT_SPEC.md`.

---

## 5. Architecture boundaries

The project must maintain a strict separation between:

```text
Frontend
    ↓
API
    ↓
Application Services
    ↓
Simulation Engine
    ↓
Persistence
```

### Frontend responsibilities

The frontend is responsible for:

* UI
* User interaction
* Presentation
* Animation
* Data visualization
* Frontend-specific state

The frontend must NOT contain core football simulation rules.

### API responsibilities

The API is responsible for:

* HTTP
* Request validation
* Response serialization
* Routing
* Calling application services

### Application Service responsibilities

Application services are responsible for:

* Orchestrating use cases
* Coordinating simulation and persistence
* Converting between API/domain/persistence representations where necessary

### Simulation Engine responsibilities

The Simulation Engine is responsible for:

* Football rules
* Probabilities
* Player development
* Matches
* Transfers
* Events
* Career progression
* Relationships
* Narrative calculations

### Persistence responsibilities

Persistence is responsible for:

* Saving
* Loading
* Database access
* Repositories
* Transactions

---

## 6. Simulation Engine independence

The Simulation Engine MUST NOT depend on:

* Angular
* TypeScript
* FastAPI
* HTTP
* SQLAlchemy
* SQLite
* REST
* Frontend components

The simulation engine should eventually be executable directly from Python without starting FastAPI.

Preferred conceptual flow:

```python
result = simulation_engine.simulate(
    career_state,
    rules,
    seed
)
```

The engine should return structured domain results.

Persistence should happen outside the core simulation engine.

Preferred architecture:

```text
FastAPI
   ↓
Application Service
   ↓
Simulation Engine
   ↓
Simulation Result
   ↓
Application Service
   ↓
Persistence
```

The Simulation Engine must not directly write to the database.

---

## 7. Deterministic simulation

Football Life requires reproducible careers.

Every career must have a seed.

The simulation must eventually satisfy:

```text
same seed
+
same initial state
+
same rules version
=
same result
```

Do not introduce uncontrolled randomness.

Avoid direct scattered calls to global random functions.

Use a centralized deterministic RNG abstraction.

The RNG implementation should make it possible to:

* Reproduce a career
* Debug unexpected outcomes
* Compare different rule versions
* Create future community branches
* Run automated balance tests

---

## 8. Data-driven game rules

Game rules should be configurable whenever practical.

Examples:

```text
data/rules/
data/events/
```

Do not hardcode large collections of:

* Events
* Probabilities
* Position weightings
* Development coefficients
* Transfer rules
* Injury probabilities
* Narrative weights

inside business logic.

However, do not over-engineer configuration systems before they are needed.

Use simple structured data first.

---

## 9. Code quality

Prefer:

* Simple code
* Small functions
* Clear names
* Strong typing
* Explicit dependencies
* Testable components
* Minimal abstractions
* Easy-to-read business logic

Avoid:

* Premature abstraction
* Giant classes
* God objects
* Circular dependencies
* Unnecessary design patterns
* Unnecessary third-party libraries
* Over-engineered frameworks

Do not create abstractions merely because they may become useful in the distant future.

---

## 10. No fake implementations

Do not create implementations that pretend to provide functionality that has not actually been built.

Avoid examples such as:

```python
def simulate_career():
    return {"status": "success"}
```

unless the task explicitly requires a temporary prototype.

Do not hardcode fake simulation results in production logic.

Do not create empty future engines merely to make the folder structure look complete.

Create systems when their phase begins.

---

## 11. Testing

Important domain logic must have automated tests.

At minimum, test:

* Player calculations
* Overall calculation
* Position weighting
* Development
* Aging
* Match calculations
* Playing time
* Transfers
* Event conditions
* Decision resolution
* Narrative calculations
* Deterministic RNG

Whenever a bug is fixed, add a regression test when appropriate.

Tests should focus especially on domain rules rather than only API endpoints.

---

## 12. Verification

After implementing a phase:

1. Run the relevant tests.
2. Start the backend if applicable.
3. Start the frontend if applicable.
4. Verify the requested functionality manually when practical.
5. Fix errors before reporting completion.

Do not claim that something works without verifying it.

If something could not be tested, explicitly state that.

---

## 13. Dependencies

Do not introduce a dependency unless:

* It solves a real problem.
* It is compatible with the current architecture.
* The benefit justifies the added complexity.
* The functionality cannot reasonably be achieved with the current stack.

Prefer the existing stack defined in `PROJECT_SPEC.md`.

Do not add libraries simply for convenience.

---

## 14. Database rules

Database access must remain outside the core Simulation Engine.

Use:

```text
SQLAlchemy
Alembic
SQLite
```

according to the project specification.

Do not put database queries directly inside simulation algorithms.

Prefer:

```text
API
 ↓
Application Service
 ↓
Repository / Persistence
```

where appropriate.

The Simulation Engine should operate on domain state and return domain results.

---

## 15. API rules

The frontend communicates with the backend through HTTP/REST.

Do not put business rules inside Angular components.

Do not make the frontend calculate:

* Player overall
* Development
* Transfer probability
* Match results
* Event probabilities
* Career outcomes
* Narrative importance

Those calculations belong to backend/domain logic.

The API should expose data and operations, not duplicate the simulation engine.

---

## 16. Frontend rules

The frontend should focus on:

* Presentation
* UX
* Animation
* Interaction
* Data visualization

Avoid creating a generic admin-dashboard appearance.

Follow the visual direction in `PROJECT_SPEC.md`.

Do not prioritize visual polish over simulation functionality during early phases.

Do not build the final presentation mode before the underlying career data and narrative systems exist.

---

## 17. MVP discipline

Do not implement future features simply because the architecture can support them.

Future features include:

* TikTok integration
* Comment scraping
* Community voting
* Public careers
* Multiplayer
* AI narration
* Automatic video generation
* Community branches

Keep the MVP focused.

If a future feature is encountered during implementation, document it rather than implementing it automatically.

---

## 18. Future community architecture

The architecture should remain compatible with:

```text
Decision
    ↓
Automatic resolution
```

and eventually:

```text
Decision
    ↓
Community Vote
    ↓
Selected Option
```

The Simulation Engine should not care where a decision option came from.

The input to the simulation should simply be a selected decision option.

Do NOT implement the community system unless explicitly requested.

---

## 19. Development communication

Before a significant implementation:

Briefly explain:

* What will be changed.
* Why it is needed.
* Which files/modules are affected.
* Which phase the change belongs to.

After implementation, report:

* What was implemented.
* Files created.
* Files modified.
* Tests added.
* Tests executed.
* Problems discovered.
* Remaining issues.
* Recommended next step.

Do not continue automatically to the next major phase.

---

## 20. Refactoring policy

Refactor when:

* It clearly improves maintainability.
* It fixes architectural coupling.
* It removes duplication that is already causing problems.
* It is necessary for the requested feature.
* The existing architecture prevents correct implementation.

Do not perform large refactors simply because a different architecture might theoretically be better.

Avoid unrelated cleanup during feature implementation.

---

## 21. Error handling

Do not silently swallow errors.

Use clear error messages.

Do not hide failures behind generic success responses.

When an error is caused by the implementation, fix it rather than masking it.

Do not use broad exception handling unless there is a clear reason.

---

## 22. Documentation

Update documentation when:

* Architecture changes
* Public APIs change
* Setup changes
* Important development decisions are made
* A new development phase is completed

Keep `PROJECT_SPEC.md` focused on the product specification.

Keep this file focused on development behavior.

Do not duplicate the entire project specification here.

---

## 23. Project priority

The project's priority is:

```text
1. Simulation quality
2. Career variety
3. Narrative quality
4. Data integrity
5. Maintainability
6. Performance
7. Visual quality
8. Future extensibility
```

Do not sacrifice simulation quality for visual polish.

Do not sacrifice maintainability for unnecessary complexity.

---

## 24. Simulation quality principles

The simulator should prioritize:

```text
Believability
+
Unpredictability
+
Career variety
+
Narrative potential
```

Do not optimize every player toward becoming a superstar.

The simulator must allow:

* Failure
* Mediocrity
* Early decline
* Injuries
* Bad transfers
* Missed potential
* Unexpected success
* Late blooming
* Club loyalty
* Journeyman careers
* Legendary careers

Randomness should create uncertainty without producing nonsense.

---

## 25. Narrative quality principles

The narrative engine must derive stories from the simulation.

Do not artificially create events simply to fit a story template.

A career without major drama should remain relatively simple.

A career with major turning points should receive more narrative attention.

The simulator should distinguish between:

```text
Normal events
Important events
Major career events
Historic events
```

The final story should prioritize the latter categories.

---

## 26. Simulation speed

The simulator will eventually need to generate complete careers quickly.

The architecture should allow normal matches and low-value events to be aggregated where appropriate.

Do not optimize prematurely.

However, avoid designs that require expensive database operations for every insignificant simulated action.

The long-term goal is to support:

```text
Single career simulation
```

and eventually:

```text
Hundreds or thousands of careers for balance testing
```

---

## 27. Future balance testing

Once the basic simulator works, it should be possible to run many careers automatically.

The system should eventually support statistics such as:

```text
average_peak_overall
average_final_overall
average_career_length
average_transfers
average_injuries
average_goals
average_trophies
average_market_value
average_retirement_age
percentage_reaching_potential
percentage_winning_major_titles
```

This should be used to balance the simulation.

---

## 28. No premature visual development

The final product should be visually polished.

However:

During early phases, prioritize:

```text
Architecture
 ↓
Domain
 ↓
Simulation
 ↓
Narrative
 ↓
UI
 ↓
Visual polish
 ↓
Presentation mode
```

Do not spend significant development time on animations or visual details before the underlying career systems work.

---

## 29. No premature community development

Community interaction is a future feature.

Do not implement:

* TikTok API
* Comment parsing
* Voting
* Followers
* Public accounts
* Public careers

until explicitly requested.

Keep the data model compatible with future branching decisions.

---

## 30. Phase discipline

The phases defined in `PROJECT_SPEC.md` are ordered deliberately.

Do not skip ahead without reason.

Do not combine multiple major phases into one implementation request unless explicitly authorized.

For example:

```text
Phase 3 Player Engine
```

should not silently include:

```text
Phase 7 Transfer Engine
```

even if the transfer system would technically benefit from knowing about player attributes.

Build the dependency first, then move to the next phase.

---

## 31. First implementation phase

The first implementation phase is deliberately small.

Implement only:

* FastAPI
* Angular
* SQLite
* SQLAlchemy
* Alembic
* Centralized configuration
* Health endpoint
* Basic API shell
* Basic frontend shell
* Basic frontend → backend communication
* Basic automated tests

Do NOT implement:

* Player simulation
* Match simulation
* Development
* Transfers
* Injuries
* Events
* Relationships
* Narrative
* Career progression
* TikTok presentation
* Community features

The goal is to prove that the application architecture works before building game logic.

---

## 32. First phase verification

Phase 1 is complete only when:

```text
Angular starts
+
FastAPI starts
+
SQLite connection works
+
Alembic works
+
/health works
+
Angular can communicate with FastAPI
+
Tests pass
```

Do not proceed to Phase 2 automatically.

---

## 33. Major architectural changes

If a requested feature appears to require:

* Rewriting a subsystem
* Changing the database architecture
* Changing the frontend framework
* Replacing the simulation architecture
* Adding a major external service

Stop and explain:

1. Why the current architecture is insufficient.
2. What alternatives exist.
3. What the consequences would be.
4. Which option you recommend.

Do not perform major architectural changes silently.

---

## 34. Working style

Prefer a collaborative development process.

For substantial tasks:

```text
Understand
 ↓
Explain
 ↓
Implement
 ↓
Test
 ↓
Review
 ↓
Continue
```

Do not assume that a larger implementation is automatically better.

---

## 35. Final rules

When uncertain:

1. Check `PROJECT_SPEC.md`.
2. Check the current architecture.
3. Check the current development phase.
4. Prefer the simplest solution consistent with the specification.
5. Do not invent new systems without justification.
6. Do not implement future features automatically.
7. Do not rewrite unrelated code.

Most importantly:

> Build Football Life incrementally.

> Keep the Simulation Engine independent.

> Keep the project working after every phase.

> Test important domain logic.

> Do not build the entire system in one pass.

```
```
