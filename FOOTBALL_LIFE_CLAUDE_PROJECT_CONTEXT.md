# FOOTBALL LIFE — PROJECT CONTEXT FOR CLAUDE

**Repository:** `Sieg04/Football_Life`  
**Current stable milestone:** Phase 14 — Career Experience & Simulation Interface  
**Primary stack:** Python, FastAPI, SQLAlchemy, Alembic, SQLite, Angular  
**Runtime model:** Local/local-web application  
**Primary purpose:** Generate believable fictional football careers that can become engaging 5–6 minute vertical 9:16 videos.

---

# 1. PROJECT OVERVIEW

Football Life is a **football career simulation and narrative-generation engine**.

The project is not intended to reproduce Football Manager in miniature.

Its central question is:

> **What happened during this player's life?**

The simulation should create believable careers with:

- progression
- setbacks
- breakthroughs
- failures
- transfers
- playing-time changes
- decisions
- events
- trophies
- rivalries
- comebacks
- unexpected outcomes
- memorable endings

The eventual career should be presentable as an engaging approximately 5–6 minute vertical video.

The simulator is the foundation. Narrative and presentation exist to expose the story created by the simulation.

---

# 2. PRODUCT PHILOSOPHY

## 2.1 Story over raw simulation detail

Football realism matters because it produces believable stories.

Do not add complexity merely for complexity's sake.

A career such as:

    16 — Academy
    18 — Professional debut
    20 — Breakthrough
    22 — Major transfer
    23 — Setback
    25 — Decline
    28 — Comeback
    30 — Major title
    34 — Retirement

is more valuable than a technically detailed simulation that produces a boring career.

---

## 2.2 Career variety is essential

Different careers should emerge naturally from:

- player attributes
- potential
- development rate
- development profile
- personality
- club context
- manager
- playing time
- match performance
- form
- fitness
- injuries
- transfers
- decisions
- events
- relationships
- randomness
- world evolution

The system should not make every career follow the same trajectory.

---

## 2.3 Failure must exist

The simulator must allow:

- failed wonderkids
- mediocre careers
- bench careers
- bad transfers
- early decline
- late bloomers
- journeymen
- players who never reach their potential
- players who become unexpectedly successful
- loyal one-club careers
- legendary careers
- careers interrupted by setbacks

Do not optimize every player toward becoming a superstar.

---

## 2.4 Randomness should create uncertainty, not nonsense

Random outcomes must remain plausible within football context.

Randomness should create:

- uncertainty
- variation
- unexpected events
- different career paths

but not:

- absurd outcomes
- arbitrary narrative events
- impossible player progression
- meaningless randomness

---

# 3. CORE CAREER PIPELINE

The long-term product flow is:

    Create Player
          ↓
    Start Career
          ↓
    Simulate Seasons
          ↓
    Matches / Performance
          ↓
    Development / World Evolution
          ↓
    Transfers / Events / Decisions
          ↓
    Career Timeline
          ↓
    Narrative
          ↓
    Script
          ↓
    Presentation Mode
          ↓
    Record Video
          ↓
    Edit Externally
          ↓
    Publish

The current system already implements a substantial portion of this pipeline.

---

# 4. CURRENT ARCHITECTURE

The intended architecture is:

    Angular
       ↓
    FastAPI
       ↓
    Application Services
       ↓
    Domain / Simulation Engine
       ↓
    Persistence

More explicitly:

    Frontend
        ↓
    HTTP / REST API
        ↓
    Application Services
        ↓
    Domain + Simulation Engines
        ↓
    Repositories / Persistence
        ↓
    SQLite

---

# 5. LAYER RESPONSIBILITIES

## 5.1 Frontend

Angular is responsible for:

- UI
- UX
- interaction
- visual presentation
- animations
- visualization
- client-side state

The frontend must NOT contain core football business rules.

It should not calculate:

- player OVR
- player development
- transfer probabilities
- match results
- event probabilities
- career outcomes
- narrative importance

Those calculations belong to backend/domain systems.

---

## 5.2 FastAPI

FastAPI is responsible for:

- HTTP
- routing
- request validation
- response serialization
- calling application services

FastAPI routes should not contain core football simulation formulas.

---

## 5.3 Application Services

Application services are responsible for:

- use-case orchestration
- coordinating domain engines
- coordinating persistence
- API/domain translation where necessary

They should compose existing systems rather than duplicate them.

---

## 5.4 Domain / Simulation

The domain layer owns football logic.

This includes:

- player calculations
- development
- matches
- competitions
- transfers
- events
- decisions
- career progression
- narrative calculations

The core simulation must remain independent of:

- Angular
- TypeScript
- FastAPI
- HTTP
- SQLAlchemy
- SQLite
- REST

---

## 5.5 Persistence

Persistence is responsible for:

- database access
- repositories
- saving/loading
- transactions
- migrations

The simulation engine should not directly write to the database.

Preferred architecture:

    API
      ↓
    Application Service
      ↓
    Domain / Simulation
      ↓
    Domain Result
      ↓
    Application Service
      ↓
    Persistence

---

# 6. CORE ENGINE PRINCIPLES

## 6.1 Determinism

Football Life requires reproducible simulation.

The fundamental rule is:

    same seed
    +
    same initial state
    +
    same rules version
    =
    same result

Randomness should be centralized through deterministic RNG mechanisms.

Avoid uncontrolled scattered calls to global random functions.

Determinism is important for:

- debugging
- testing
- balance analysis
- reproducing careers
- comparing rules
- future community branching
- regression testing

---

## 6.2 Data-driven rules

Prefer configuration for large rule collections.

Existing conventions include:

    data/rules/

Examples:

- position weights
- role definitions
- development profiles
- development coefficients
- event probabilities
- transfer parameters
- traits
- balance parameters

Do not hardcode large rule collections into business logic when structured configuration is appropriate.

---

## 6.3 Pure domain calculations

Important football calculations should be testable without infrastructure.

Pure calculations should generally:

- avoid persistence
- avoid HTTP
- avoid framework dependencies
- avoid unexpected mutation
- return explicit structured results

---

## 6.4 Immutability

Avoid unexpected mutation of:

- inputs
- domain state
- calculation results
- reusable objects

This is especially important in:

- standings
- form calculations
- probability calculations
- player calculations
- career snapshots
- simulation state transitions

---

## 6.5 No fake functionality

Never create fake production behavior simply to satisfy an interface.

Do not return fake success responses.

Do not hardcode fake career outcomes.

Do not create placeholder implementations pretending a subsystem is complete.

If something is not implemented, it must be clearly identified as such.

---

# 7. FUNDAMENTAL PLAYER MODEL

Football Life uses one fundamental `Player` identity.

World player:

    Player
    +
    ClubMembership

Career protagonist:

    Player
    +
    Career

Do NOT create parallel football identities such as:

    GenericSquadPlayer
    CareerPlayer

The same fundamental player model should be reused throughout the system.

---

# 8. CURRENT ABILITY VS OVR

This distinction is fundamental.

## Current Ability

Represents general football quality.

## OVR

Represents effectiveness in a specific position.

Conceptually:

    Current Ability
    =
    general football quality

    OVR
    =
    position-specific effectiveness

Changing position must not mutate the player's underlying attributes.

The player system includes concepts such as:

- PAC
- SHO
- PAS
- DRI
- DEF
- PHY
- MENTAL
- Current Ability
- position-specific OVR
- Potential
- Development Rate
- Development Profile
- Role Familiarity
- Role Attribute Fit
- Role Effectiveness
- Traits / PlayStyles
- Personality
- Player State
- aging

Goalkeepers have goalkeeper-specific OVR logic.

Player generation is deterministic and should respect:

- position
- archetype
- potential
- development profile
- role specialization
- secondary positions
- traits
- personality

---

# 9. FOOTBALL WORLD

The World layer contains concepts for:

- countries
- leagues
- clubs
- managers
- competitions
- external source metadata
- club attributes
- league attributes
- club strength
- league strength
- generic squads
- player membership

The project intentionally uses a compact generated football world instead of trying to reproduce every real-world player and squad.

Historical seed generation included:

- 5 countries
- 5 leagues
- 20 clubs
- 20 managers
- 16 competitions
- 800 generic players
- 25 source records

Role weights were moved into:

    data/rules/world.json

The world can use concepts such as:

- force / strength
- prestige
- momentum
- attractiveness

Do NOT introduce another competing club-strength model.

Reuse the existing world concepts.

---

# 10. CAREER ENGINE

The Career Engine models progression through seasons.

Conceptually:

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

Career concepts include:

- Career
- Season
- SeasonSnapshot
- season progression
- development
- attribute changes
- Current Ability recalculation
- OVR recalculation
- age progression
- Career Phase
- peak tracking
- seasonal snapshots
- deterministic simulation

Development must NOT simply be:

    OVR + fixed amount

Development should depend on the contextual systems defined in the project specifications.

---

# 11. CAREER ARCHETYPES

The career archetype classifier derives labels from the actual career trajectory.

Known archetypes include:

- `WONDERKID`
- `FAILED_WONDERKID`
- `SUPERSTAR`
- `LONG_PRIME`
- `LATE_BLOOMER`
- `EARLY_DECLINER`
- `SOLID_PRO`

The classifier should use actual evidence from the career.

Do not fabricate archetypes simply because they make a story more interesting.

---

# 12. MATCH ENGINE

The Match Engine provides the football performance loop.

Development was divided into:

    5A — Match Domain
    5B — Lineup + Team Strength
    5C — Match Resolution
    5D — Player Performance
    5E — Season Aggregation
    5F — Career Integration

The Match Engine is responsible for match resolution and player performance.

It should remain separate from:

- transfers
- injuries
- relationships
- narrative
- community

unless a later approved phase explicitly integrates those systems.

The Match Engine is the source of truth for match resolution.

Do not duplicate its formulas elsewhere.

---

# 13. COMPETITION ENGINE

Phase 6 introduced the Competition Engine.

Responsibilities include:

- competition definitions
- fixtures
- calendar
- standings
- form
- progression
- season orchestration
- multi-competition orchestration

Subphases:

    6A — Competition Domain
    6B — Fixture & Calendar Engine
    6C — Standings & Form Engine
    6D — Competition Progression Engine
    6E-A — Generic Season Orchestrator
    6E-B — Match Engine Integration
    6E-C — Standings/Form Integration
    6E-D — Progression Integration
    6E-E — Full Season / Multi-Competition Orchestrator

Important principles:

- deterministic fixtures
- deterministic standings
- deterministic form
- immutable standings/form calculations
- progression separated from orchestration
- Match Engine remains the source of match results
- orchestration composes existing engines
- no duplicated football formulas
- deterministic replay
- cross-process determinism

Phase 6 should be treated as a stable subsystem unless an explicit task requires modifying it.

---

# 14. TRANSFER ENGINE

Phase 7 introduced deterministic transfers.

Conceptual flow:

    Season Complete
          ↓
    Market Value
          ↓
    Club Needs
          ↓
    Player Fit
          ↓
    Transfer Interest
          ↓
    Transfer Offers
          ↓
    Player Decision
          ↓
    Club Decision
          ↓
    Transfer
          ↓
    New Club Membership
          ↓
    Next Season

The goal is believable player movement.

Transfers should not simply be random club changes.

---

## 14.1 Market value

Market value can depend on:

- Current Ability
- OVR
- Potential
- age
- development trajectory
- form
- playing time
- performance
- position scarcity
- contract duration
- club level
- competition exposure

---

## 14.2 Contract state

Conceptual contract information includes:

- contract_start
- contract_end
- contract_years_remaining
- wage
- release_clause

Contract state can include:

- ACTIVE
- EXPIRING_SOON
- EXPIRED

---

## 14.3 Club needs

Club recruitment needs can consider:

- squad size
- positional depth
- starter quality
- backup quality
- age distribution
- potential distribution
- role coverage
- formation needs
- departures

---

## 14.4 Player fit

Player fit can consider:

- OVR
- role effectiveness
- positions
- secondary positions
- manager preference
- formation
- age
- development
- playing-time opportunity
- club compatibility

Transfers must preserve career continuity and correct club membership.

---

# 15. EVENT ENGINE

The Event Engine provides deterministic, data-driven event evaluation.

Important concepts include:

- `EventCondition`
- `ConditionCompositionNode`
- `ConditionResult`
- `ConditionEvaluationResult`
- `ConditionOperator`
- `ConditionCompositionType`
- `evaluate_condition`
- `evaluate_composition`
- `evaluate_event_conditions`
- `ProbabilityModifier`
- `ProbabilityCalculationResult`
- `EventCandidate`
- `ProbabilityModifierType`
- `calculate_event_probability`

Conditions require strict type handling.

Missing attributes must have explicit handling.

Probability calculations must be bounded and deterministic.

Events should create plausible career consequences.

The Event Engine should not become a random narrative generator.

---

# 16. DECISION SYSTEM

The later Event Engine introduced decision-required flows.

Conceptually:

    Advance Career
          ↓
    Simulation
          ↓
    Decision Trigger?
       ↙       ↘
      No        Yes
      ↓          ↓
    Continue    Pause
                  ↓
            User Decision
                  ↓
            Resolve Decision
                  ↓
            Continue Career

The core simulation should not care who selected the decision.

Long-term the selection source could be:

    Automatic Logic

or:

    User

or:

    Community Vote

The simulation should simply receive the selected option.

---

# 17. PHASE 8 EVENT SYSTEM

Phase 8 was developed as a family of subsystems covering the event and decision pipeline.

The later architecture includes:

- condition evaluation
- probability calculation
- event candidate generation/selection
- decisions
- decision resolution
- career integration
- persistence integration

Phase 8 logic must not be duplicated by later phases.

---

# 18. PHASE 9 — CAREER DOMAIN

Phase 9 formalized the career domain layer.

It provides the foundation for:

- career state
- career progression
- seasonal state
- career snapshots
- career records
- event integration
- deterministic progression

When working on later career functionality, reuse this domain rather than creating parallel career models.

---

# 19. NARRATIVE ENGINE

The Narrative Engine derives stories from actual simulation state.

It must NOT fabricate drama.

If a career is quiet, the resulting story should be relatively quiet.

If the career contains major turning points, those should receive stronger narrative emphasis.

Useful event importance levels include:

    Normal
    Important
    Major Career Event
    Historic

The narrative should prioritize things such as:

- breakthroughs
- failures
- major transfers
- injuries
- comebacks
- rivalries
- titles
- records
- awards
- turning points
- retirement
- legacy

The narrative explains what happened.

It should not invent what happened.

---

# 20. SCRIPT & PRESENTATION

The long-term output is a story suitable for a 5–6 minute vertical video.

The system should eventually expose:

- player identity
- career progression
- important seasons
- statistics
- transfers
- trophies
- major events
- turning points
- narrative beats
- legacy

The application is intended to make recording easy.

Automatic video generation is NOT a core requirement.

The user can record the presentation manually and edit the video externally.

---

# 21. PHASE 14 — CAREER EXPERIENCE & SIMULATION INTERFACE

Phase 14 is the current stable career-experience milestone.

Important domain concepts:

- `CareerSession`
- `CareerSessionStatus`
- `CareerAdvanceResult`
- `CareerSetupRequest`
- `CareerSessionNotification`

Important backend components:

- `CareerSessionEngine`
- `CareerSessionService`

The Career Session Engine orchestrates:

- session creation
- season progression
- decision triggers
- decision resolution
- Phase 8E/8F integration
- presentation building

---

## 21.1 Phase 14 API

Current career endpoints:

    POST /career
    GET  /career/{id}
    POST /career/{id}/advance
    POST /career/{id}/decision
    POST /career/{id}/pause
    GET  /career/{id}/events
    GET  /career/{id}/presentation

These endpoints should be treated as part of the current career-session contract unless a deliberate API change is required.

---

## 21.2 Phase 14 frontend

The Angular career experience includes components for:

- career creation
- career dashboard
- career events
- career decisions
- career notifications
- recording mode

The Angular career-session service is:

    frontend/football-life/src/app/core/services/career-session.service.ts

Known components include:

    career-create
    career-dashboard
    career-event
    career-decision
    career-notification
    career-recording-mode

---

# 22. CURRENT VALIDATION BASELINE

The latest Phase 14 QA established the following baseline:

- 8-season career simulation executed successfully
- playing-time comparison validated
- transfer persistence validated
- decision resolution validated
- FastAPI TestClient career flow validated
- two-run seed determinism check completed
- full backend suite: **694/694 passed**
- Angular production build completed successfully
- Angular headless unit tests: **6/6 passed**
- pre-commit verification completed
- comprehensive career-flow QA audit completed
- final status: **READY**

This baseline must be preserved.

If current repository state differs from this description, inspect the repository and establish the actual state before changing anything.

---

# 23. PROJECT PHASE HISTORY

The project has been developed incrementally.

Current phase history:

    Phase 0  — Planning
    Phase 1  — Foundation
    Phase 2  — Football World
    Phase 3  — Player Engine
    Phase 3.1 — Player Generation & Balance Refinement
    Phase 4  — Career Engine
    Phase 4.1B — Career Archetype Classifier
    Phase 5  — Match Engine
    Phase 6  — Competition Engine
    Phase 7  — Transfer Engine
    Phase 8  — Event Engine
    Phase 9  — Career Domain
    Phase 10 — Narrative Engine
    Phase 11 — Script & Presentation
    Phase 12 — Presentation Engine
    Phase 13 — Presentation UI
    Phase 14 — Career Experience & Simulation Interface

The repository also contains design documents for future phases including:

    Phase 15
    Phase 16
    Phase 17
    Phase 18

IMPORTANT:

The existence of a phase design document does NOT mean the phase is implemented.

Always distinguish:

    Specified
        ↓
    Designed
        ↓
    Implemented
        ↓
    Tested
        ↓
    Runtime Verified

Inspect the actual code and tests before claiming implementation status.

---

# 24. IMPORTANT REPOSITORY DOCUMENTS

Important project files include:

    PROJECT_SPEC.md
    AGENTS.md
    .github/instructions/reglas.instructions.md

Relevant phase specifications include:

    PHASE_8E_DESIGN_SPEC.md
    PHASE_8F_DESIGN_SPEC.md
    PHASE_9_DESIGN_SPEC.md
    PHASE_10_DESIGN_SPEC.md
    PHASE_11_DESIGN_SPEC.md
    PHASE_12_DESIGN_SPEC.md
    PHASE_14_DESIGN_SPEC.md
    PHASE_15_DESIGN_SPEC.md
    PHASE_16_DESIGN_SPEC.md
    PHASE_17_DESIGN_SPEC.md
    PHASE_18_DESIGN_SPEC.md

---

# 25. SOURCE OF TRUTH

There are three important categories of documentation.

## Product specification

    PROJECT_SPEC.md

This is the primary product/design source of truth.

## Development rules

    AGENTS.md

and:

    .github/instructions/reglas.instructions.md

These define how development should be performed.

## This document

This file is a **Claude handoff/context document**.

It provides:

- project history
- architecture context
- design philosophy
- current baseline
- important constraints
- development expectations

It does NOT replace the official project specification.

Claude must still read the relevant official specification before implementing a feature.

---

# 26. DEVELOPMENT PHILOSOPHY

The project explicitly follows:

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
    REVIEW
      ↓
    NEXT PHASE

The project must NOT be built in one massive pass.

---

# 27. BEFORE MODIFYING CODE

Before implementing a significant change:

1. Read the relevant specification.
2. Read the development rules.
3. Inspect the repository.
4. Inspect the existing implementation.
5. Inspect related tests.
6. Identify dependencies.
7. Identify which subsystem owns the behavior.
8. Determine whether the requested feature already exists partially.
9. Determine whether another subsystem already provides the required calculation.
10. Plan the smallest correct implementation.

Do not start coding based only on the user's description if the repository contains relevant existing behavior.

---

# 28. PHASE DISCIPLINE

Never silently implement future functionality.

For example, a Player Engine task should not automatically introduce:

- transfers
- injuries
- relationships
- narrative
- community systems

unless explicitly requested.

Similarly, a UI task should not introduce backend business rules.

If a requested feature genuinely requires a cross-phase modification:

1. Explain why.
2. Identify the affected subsystem.
3. Explain the proposed change.
4. Keep the modification narrow.
5. Test the affected systems.

---

# 29. TESTING REQUIREMENTS

Every meaningful domain change should have automated tests.

Depending on the feature, test:

- unit behavior
- integration behavior
- API behavior
- frontend behavior
- regression behavior
- determinism
- invalid inputs
- missing attributes
- boundary values
- immutability
- multiple seeds
- distribution sanity
- cross-process determinism

For simulation balance, do not rely on one seed.

Prefer:

    many seeds
    +
    statistical assertions
    +
    sensible ranges

instead of fragile exact-output assertions.

Bug fixes should normally include a regression test.

---

# 30. DATABASE RULES

Persistence uses:

    SQLite
    SQLAlchemy
    Alembic

When a schema change is required:

1. Create a proper Alembic migration.
2. Verify upgrade behavior.
3. Verify the application against the new schema.
4. Preserve existing persistent data.
5. Do not silently destroy data.
6. Clearly document destructive behavior if it is genuinely unavoidable.

Never place database queries directly inside pure simulation calculations.

---

# 31. FRONTEND RULES

Angular is the presentation/client layer.

The frontend should request calculated results from the backend.

Do not move football business logic into Angular simply because it is convenient.

Avoid:

- duplicated formulas
- duplicate state models
- hardcoded football rules
- fake simulation results

The frontend should eventually support:

- career interaction
- career exploration
- visual storytelling
- recording
- vertical 9:16 presentation

The visual experience should feel like a football career story, not a generic enterprise dashboard.

---

# 32. MVP NON-GOALS

The initial project explicitly excludes:

- user accounts
- authentication
- cloud deployment
- public API
- TikTok API
- TikTok comment scraping
- community voting
- multiplayer
- public career pages
- mobile app
- 3D matches
- tactical real-time simulation
- complete real-world player database
- complete real-world squad database
- complex financial accounting
- mandatory LLM integration
- automatic video generation

These can become future features.

Do not implement them unless explicitly requested.

---

# 33. FUTURE COMMUNITY CONCEPT

The long-term community concept is:

    Follower
       ↓
    Comment
       ↓
    Career request
       ↓
    Simulation
       ↓
    Video
       ↓
    Community decision
       ↓
    Next event
       ↓
    Next video

Community interaction could eventually affect:

- club selection
- transfers
- career choices
- personal decisions
- rivalries
- important events

The core simulation should remain agnostic about who selected an option.

---

# 34. PERFORMANCE AND SCALE

The project should eventually support not only individual careers but also large numbers of simulations for testing and balancing.

Potential future workloads:

    Single career
        ↓
    Multiple careers
        ↓
    Hundreds of careers
        ↓
    Thousands of careers

Avoid unnecessary database operations inside simulation loops.

Keep pure simulation calculations lightweight.

Do not prematurely optimize.

But do not introduce architecture that unnecessarily makes large-scale simulation expensive.

Potential future balance metrics include:

- average peak overall
- average final overall
- average career length
- average transfers
- average injuries
- average goals
- average trophies
- average market value
- average retirement age
- percentage reaching potential
- percentage winning major titles

---

# 35. REFACTORING POLICY

Refactor when necessary for:

- correctness
- eliminating harmful duplication
- correcting architectural coupling
- materially improving maintainability

Do NOT:

- rewrite the architecture because another design looks cleaner
- perform unrelated cleanup
- introduce abstractions for hypothetical future features
- modify stable systems without justification
- replace working implementations merely because they were created by another AI

If a major architectural change appears necessary, stop and explain:

1. Why the current architecture is insufficient.
2. Possible alternatives.
3. Consequences of each.
4. Recommended approach.

Do not silently perform major architectural changes.

---

# 36. IMPORTANT DESIGN PRINCIPLES

## One responsibility per layer

    Frontend
        ↓
    Presentation

    API
        ↓
    Transport

    Application Services
        ↓
    Orchestration

    Domain / Simulation
        ↓
    Football logic

    Persistence
        ↓
    Storage

---

## Do not duplicate systems

If an existing subsystem already calculates something, reuse it.

Examples:

Do not create:

- a second club-strength formula
- a second Player identity model
- duplicate Match Engine formulas
- duplicate standings logic
- duplicate event probability logic
- duplicate transfer evaluation logic

---

## Prefer composition

Existing engines should be composed.

For example:

    Competition
        ↓
    Match Engine
        ↓
    Result
        ↓
    Standings
        ↓
    Progression

rather than copying Match Engine formulas into the Competition Engine.

---

# 37. NARRATIVE QUALITY PRINCIPLES

Narrative should emerge from simulation.

Do not create artificial drama simply because a story template expects it.

Good:

    Player struggled for two seasons,
    finally became a starter,
    transferred to a stronger club,
    then suffered a decline.

Bad:

    Player suddenly becomes a legend
    because the narrative needs a climax.

The narrative system must respect actual simulation data.

The story should reflect:

- causality
- progression
- setbacks
- context
- turning points
- consequences

The most important moments should receive the most narrative attention.

---

# 38. VISUAL PRODUCT DIRECTION

Football Life is intended to be used for content creation.

The presentation should work especially well in:

    9:16 vertical format

The user should be able to manually record the presentation.

Visual priorities:

- clear player identity
- strong career timeline
- statistics
- club changes
- trophies
- major events
- narrative highlights
- visually understandable progression
- recording-friendly presentation

Avoid unnecessary enterprise-style UI.

The visual layer should serve the story.

---

# 39. WHAT CLAUDE SHOULD DO WHEN TAKING OVER

Claude is taking over an existing project.

This is NOT a greenfield project.

Do not assume:

> "The previous implementation is wrong because another AI created it."

Also do not assume:

> "Everything must be correct because tests pass."

Use four sources of truth:

    Specification
    +
    Implementation
    +
    Tests
    +
    Runtime behavior

All four matter.

---

# 40. INITIAL REPOSITORY RECONNAISSANCE

When starting work on the repository, first establish:

### Repository state

Check:

- current branch
- working tree
- recent commits
- current files
- existing migrations
- tests
- frontend build state

### Specification state

Read:

- PROJECT_SPEC.md
- AGENTS.md
- .github/instructions/reglas.instructions.md
- relevant phase design specification

### Implementation state

Inspect:

- relevant backend modules
- relevant domain models
- application services
- API endpoints
- frontend components/services
- database models
- migrations

### Testing state

Inspect:

- relevant unit tests
- integration tests
- API tests
- frontend tests
- regression tests

### Runtime state

When relevant, verify:

- API behavior
- career creation
- season progression
- decision flow
- persistence
- transfers
- determinism
- frontend build

---

# 41. STATUS CLASSIFICATION

When evaluating a feature, explicitly distinguish:

    SPECIFIED
    The specification describes it.

    DESIGNED
    A design document exists.

    IMPLEMENTED
    Code exists.

    TESTED
    Automated tests cover it.

    RUNTIME VERIFIED
    Actual execution has confirmed it.

Do not collapse these categories into one.

For example:

    PHASE_17_DESIGN_SPEC.md exists

does NOT mean:

    Phase 17 is implemented.

---

# 42. CHANGE MANAGEMENT

Before changing an existing subsystem ask:

1. Is the behavior already implemented?
2. Is it already tested?
3. Is it part of a stable phase?
4. Is there another subsystem that owns this behavior?
5. Would this create duplicated logic?
6. Would this affect determinism?
7. Would this affect persistence?
8. Would this break an API contract?
9. Would this require a migration?
10. Can the change be isolated?

Prefer the smallest change that satisfies the specification.

---

# 43. REGRESSION PROTECTION

Existing working behavior is valuable.

When modifying a subsystem, protect:

- existing tests
- deterministic behavior
- existing API contracts
- database compatibility
- domain boundaries
- player identity
- transfer persistence
- event persistence
- career progression
- presentation contracts

If a test needs to change because the specification deliberately changed, explain why.

Do not modify tests simply to make an implementation pass.

---

# 44. REPORTING FORMAT

After implementation, report results in this structure:

    Implemented
    - What was changed.

    Files
    - Files created/modified.

    Tests
    - Tests added/modified.
    - Test results.

    Verification
    - Runtime/API/frontend verification.

    Issues
    - Known limitations or concerns.

    Next step
    - Only the next logical step.
    
Do not automatically start the next phase.

---

# 45. CURRENT PROJECT PRIORITY ORDER

The project's priorities are:

    1. Simulation quality
    2. Career variety
    3. Narrative quality
    4. Data integrity
    5. Maintainability
    6. Performance
    7. Visual quality
    8. Future extensibility

Do not sacrifice simulation quality for visual polish.

Do not sacrifice maintainability for unnecessary complexity.

---

# 46. THINGS CLAUDE MUST NOT DO

Never:

- rebuild Football Life from scratch
- replace the architecture without justification
- implement several future phases automatically
- duplicate existing domain logic
- put football simulation rules into Angular
- put football simulation rules directly into FastAPI routes
- put persistence inside pure simulation calculations
- introduce uncontrolled randomness
- hardcode fake career outcomes
- silently change stable behavior
- perform unrelated refactors
- assume a design document means implementation exists
- claim a feature is complete without testing
- modify tests merely to hide implementation failures
- introduce unnecessary dependencies
- break deterministic behavior without explicit justification
- create parallel models for concepts that already have a canonical model

---

# 47. WHEN A REQUEST IS AMBIGUOUS

If a requested change could reasonably belong to multiple phases or subsystems:

1. Inspect the current architecture.
2. Identify the canonical owner.
3. Explain the interpretation.
4. Implement the narrowest correct solution.

Do not invent a new subsystem just because the request is ambiguous.

---

# 48. WHEN A MAJOR ARCHITECTURAL PROBLEM IS FOUND

If Claude discovers that the existing architecture genuinely prevents correct implementation:

Do NOT immediately rewrite it.

Instead report:

    Problem
    Why the current architecture cannot support the requirement.

    Affected systems
    Which components are involved.

    Options
    Possible solutions.

    Recommendation
    Preferred approach and why.

    Impact
    Tests, migrations, APIs, frontend, determinism, etc.

Then wait for direction if the change is substantial.

---

# 49. CORE MENTAL MODEL

The easiest way to understand Football Life is:

    WORLD
      ↓
    PLAYER
      ↓
    CAREER
      ↓
    SEASON
      ↓
    COMPETITIONS
      ↓
    MATCHES
      ↓
    PERFORMANCE
      ↓
    DEVELOPMENT
      ↓
    TRANSFERS / EVENTS / DECISIONS
      ↓
    CAREER HISTORY
      ↓
    NARRATIVE
      ↓
    PRESENTATION

Each layer should have a clear responsibility.

---

# 50. THE MOST IMPORTANT RULE

> **Understand the existing system before changing it.**

Football Life has already gone through substantial incremental development and validation.

The current validated baseline is Phase 14.

The objective is to **continue from this state**, not restart the project.

When uncertain:

1. Check `PROJECT_SPEC.md`.
2. Check the relevant phase specification.
3. Inspect the actual implementation.
4. Inspect the tests.
5. Check architectural ownership.
6. Prefer the simplest solution consistent with the specification.
7. Preserve determinism.
8. Preserve domain independence.
9. Preserve existing working behavior.
10. Do not implement future phases automatically.
11. Do not perform unrelated refactors.
12. Test before declaring completion.
13. Clearly distinguish verified facts from assumptions.

---

# 51. FINAL HANDOFF SUMMARY

Football Life is:

> A local football career simulator whose primary purpose is to generate believable, varied and narratively interesting fictional football careers that can be presented as short-form vertical videos.

It is:

- simulation-first
- story-driven
- deterministic
- data-driven
- modular
- locally runnable
- progressively developed
- heavily tested
- designed for future extensibility

The current stable milestone is:

> **Phase 14 — Career Experience & Simulation Interface**

The latest known validation baseline is:

> **694/694 backend tests passed**  
> **6/6 Angular tests passed**  
> **Angular build passed**  
> **Career-flow runtime QA passed**  
> **Determinism verified**  
> **Transfer persistence verified**  
> **Decision flow verified**  
> **Phase 14 READY**

The job when continuing development is not to rebuild Football Life.

The job is to:

    understand
      ↓
    preserve
      ↓
    improve
      ↓
    test
      ↓
    verify

> **Build incrementally.**

> **Keep the domain independent.**

> **Preserve deterministic simulation.**

> **Protect existing working systems.**

> **Reuse existing subsystems.**

> **Do not duplicate business logic.**

> **Do not confuse design documents with implementation.**

> **Test before declaring anything complete.**

> **Never build the entire system in one pass.**