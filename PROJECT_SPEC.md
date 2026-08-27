# FOOTBALL LIFE
## Complete Project Specification

**Version:** 1.6  
**Project:** Football Life  
**Type:** Local football career simulator + narrative/story generator  
**Primary platform:** Desktop/local web application  
**Development assistant:** Jules  
**Initial objective:** Generate fictional football careers that can be presented as engaging 5–6 minute vertical TikTok videos.

---

# 1. PROJECT VISION

Football Life is a local football career simulator designed primarily as a **story-generation engine**.

The objective is not to reproduce Football Manager in miniature.

The objective is to generate believable, unpredictable and emotionally interesting football careers containing:

- believable football development
- career breakthroughs
- failures
- stalled careers
- transfers
- injuries in future phases
- rivalries
- titles
- comebacks
- unexpected outcomes
- memorable endings

A complete career should eventually be presentable as a single approximately **5–6 minute vertical video**.

The most important output is therefore not:

> "What is this player's overall rating?"

but:

> **"What happened during this player's life?"**

---

# 2. CORE PRODUCT PHILOSOPHY

## 2.1 Story > raw simulation detail

The simulator should prioritize meaningful football careers rather than tactical complexity.

A career like:

```text
16 — Academy player
18 — Professional debut
20 — Major transfer
22 — Superstar
23 — Major setback
25 — Career decline
28 — Comeback
30 — Champions League
34 — Retirement
```

is more valuable than an extremely detailed simulation that produces boring results.

## 2.2 Every career should be different

Variation should come from:

- Player attributes
- Potential
- Development Rate
- Development Profile
- Personality
- Club context
- Manager
- Playing time
- Match performance
- Form
- Fitness
- Future injuries
- Transfers
- Relationships
- Randomness
- World evolution

## 2.3 Failure must be possible

The simulation must allow:

- poor careers
- failed wonderkids
- bench careers
- bad transfers
- early decline
- journeyman careers
- players who never reach potential
- clubs that decline
- clubs that unexpectedly become dominant

## 2.4 Randomness must create uncertainty, not nonsense

Random events should stay inside plausible football contexts.

## 2.5 Presentation is part of the product

The application must eventually look good enough that its UI can be directly recorded for social media.

---

# 3. MAIN USE CASE

Typical workflow:

```text
Create player
      ↓
Start career
      ↓
Simulate career
      ↓
Review seasons
      ↓
Review key events
      ↓
Generate story
      ↓
Presentation mode
      ↓
Record video
      ↓
Edit externally
      ↓
Publish
```

---

# 4. FUTURE COMMUNITY CONCEPT

The first version does **not** include community interaction.

Long-term concept:

```text
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
```

Future community features may influence:

- club selection
- transfer decisions
- career choices
- personal decisions
- rivalries
- important events

---

# 5. MVP GOALS

The eventual MVP should allow the user to:

1. Create a fictional player.
2. Select nationality.
3. Select position.
4. Select starting club.
5. Generate attributes.
6. Generate personality.
7. Start a career.
8. Simulate seasons.
9. Simulate matches.
10. Track player performance.
11. Develop attributes.
12. Experience injuries in later phases.
13. Receive transfers in later phases.
14. Sign contracts in later phases.
15. Play international football in later phases.
16. Experience important events.
17. Track relationships.
18. Win trophies.
19. Win individual awards.
20. Retire.
21. Calculate legacy.
22. Detect career archetypes.
23. Generate a complete career timeline.
24. Generate a 5–6 minute story.
25. Present the story visually.
26. Enter vertical 9:16 presentation mode.

---

# 6. EXPLICIT NON-GOALS FOR INITIAL MVP

Do NOT implement initially:

- user accounts
- authentication
- cloud deployment
- public API
- TikTok API
- TikTok comment scraping
- community voting
- multiplayer
- public career pages
- mobile application
- 3D matches
- tactical real-time simulation
- complete real-world player database
- complete real-world squad database
- complex accounting/finances
- mandatory LLM integration
- automatic video generation

---

# 7. DEVELOPMENT PHILOSOPHY

## CRITICAL RULE

> **DO NOT BUILD THE ENTIRE SYSTEM IN ONE PASS.**

Development process:

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
REVIEW
 ↓
NEXT PHASE
```

Every major phase must leave the project in a working state.

Do not automatically continue to future phases.

---

# 8. DEVELOPMENT PHASES

## Phase 0 — Planning

- repository
- documentation
- architecture
- development rules

## Phase 1 — Foundation

Implement:

- FastAPI
- Angular
- SQLite
- SQLAlchemy
- Alembic
- configuration
- health endpoint
- API shell
- Angular shell
- Angular → FastAPI communication
- tests

No football simulation.

## Phase 2 — Football World

Implement:

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
- initial world seed
- generic squad generation
- shared Player domain
- ClubMembership

Do NOT implement:

- player development
- Match Engine
- transfers
- injuries
- narrative

## Phase 3 — Player Engine

Implement:

- internal attributes
- PAC / SHO / PAS / DRI / DEF / PHY
- MENTAL
- Current Ability
- position-specific OVR
- Potential
- Development Rate
- Development Profiles
- Role Familiarity
- Role Attribute Fit
- Role Effectiveness
- Traits / PlayStyles
- Personality
- Player State
- aging baseline
- deterministic generation
- player validation
- persistence

## Phase 3.1 — Player Generation & Balance Refinement

Implement:

- position-based archetypes
- squad distributions
- positional specialization
- secondary positions
- expanded role coverage
- variable trait counts
- trait compatibility
- improved potential distribution
- goalkeeper-specific OVR
- intra-club player variance
- statistical seed validation

## Phase 4 — Career Engine

Implement:

- Career
- Season
- SeasonSnapshot
- season progression
- development budget
- seasonal development
- internal attribute changes
- Current Ability recalculation
- OVR recalculation
- age progression
- Career Phase
- peak tracking
- seasonal snapshots
- deterministic career simulation

## Phase 4.1B — Career Archetype Classifier

Implement:

- multi-label career trajectory classifier
- evidence output
- configurable rules
- WONDERKID
- FAILED_WONDERKID
- SUPERSTAR
- LONG_PRIME
- LATE_BLOOMER
- EARLY_DECLINER
- SOLID_PRO fallback

## Phase 5 — Match Engine

Phase 5 is divided into:

```text
5A — Match Domain
5B — Lineup + Team Strength
5C — Match Resolution
5D — Player Performance
5E — Season Aggregation
5F — Career Integration
```

The Match Engine introduces the football-performance loop without implementing future transfer, injury, narrative or community systems.

## Phase 6 — Competition Engine

Phase 6 is the completed **Competition Engine**. It is responsible for defining,
generating, simulating, aggregating, and progressing football competitions while
remaining independent of infrastructure.

The Competition Engine is divided into:

```text
6A — Competition Domain
6B — Fixture & Calendar Engine
6C — Standings & Form Engine
6D — Competition Progression Engine
6E-A — Generic Season Orchestrator
6E-B — Match Engine Integration
6E-C — Standings & Form Integration
6E-D — Progression Integration
6E-E — Full Season / Multi-Competition Orchestrator
```

### Phase 6A — Competition Domain

Implemented:

- Competition
- CompetitionParticipant
- CompetitionStage
- CompetitionSeason
- CompetitionType integration
- CompetitionFormat
- CompetitionStageType
- CompetitionSeasonStatus
- immutable competition rules
- domain validation
- participant/stage consistency
- completed-season winner validation

### Phase 6B — Fixture & Calendar Engine

Implemented:

- Fixture
- FixtureStatus
- deterministic fixture seeds
- round-robin generation
- odd-team BYE handling
- single-elimination fixture generation
- two-leg elimination fixture generation
- calendar/window validation
- deterministic fixture ordering
- match importance calculation

Round-robin generation uses a deterministic Berger/circle construction.
No BYE fixture is exposed as a real match.

### Phase 6C — Standings & Form Engine

Implemented:

- PointsRule
- StandingEntry
- StandingsTable
- standings initialization
- match-result application
- deterministic ranking
- rank lookup
- FormRecord
- rolling form windows
- form-table construction
- form points
- form rate
- form goal difference

Standings and form operations are pure functions and must not mutate their inputs.

### Phase 6D — Competition Progression Engine

Implemented:

- ProgressionResult
- TieBreakResult
- round-robin completion/qualification
- aggregate scoring
- two-leg tie resolution
- knockout-stage progression
- stage advancement
- next-stage participant construction
- final winner resolution

Progression logic remains separate from orchestration and Match Engine execution.

### Phase 6E-A — Generic Season Orchestrator

Implemented a generic deterministic FixtureExecutor boundary for executing an ordered
set of fixtures without coupling the generic orchestrator to Match Engine internals.

Responsibilities:

- deterministic fixture ordering
- exactly-once fixture execution
- completed-fixture accounting
- execution result validation
- failure propagation
- no persistence

### Phase 6E-B — Match Engine Integration

Connects competition fixtures to the frozen Phase 5 Match Engine through the
FixtureExecutor boundary.

Responsibilities:

- Fixture → MatchContext adaptation
- injected participant resolution
- Phase 5 Match Engine invocation
- MatchResult identity validation
- deterministic seed propagation
- FAST/DETAILED execution where supported

Phase 6E-B must not duplicate Match Engine formulas or modify Phase 5.

### Phase 6E-C — Standings & Form Integration

Consumes MatchResults produced by Phase 6E-B and updates an immutable competition
season state through the existing Phase 6C engines.

Responsibilities:

- immutable CompetitionSeasonState
- standings updates
- form updates
- processed-match tracking
- duplicate-result protection
- ranking/form access

### Phase 6E-D — Progression Integration

Consumes competition state and MatchResults and delegates stage decisions to Phase 6D.

Responsibilities:

- progression state
- round-robin advancement
- knockout advancement
- next-stage resolution
- champion resolution
- stage completion validation

### Phase 6E-E — Full Season / Multi-Competition Orchestrator

Coordinates complete competition seasons and multiple competitions by composing:

```text
6B Fixture Generation
        ↓
6E-B Match Execution
        ↓
6E-C Standings / Form
        ↓
6E-D Progression
        ↓
Next Stage
        ↓
Competition Completion
```

It also coordinates independent competition states and deterministic calendar
execution across multiple competitions where required by the simulation.

The orchestrator must never duplicate:

- fixture-generation algorithms
- Match Engine formulas
- standings calculations
- form calculations
- progression rules

### Phase 6 Acceptance Criteria

Phase 6 is complete only when the following are true:

```text
Competition domain valid
+
Fixtures deterministic
+
Standings correct
+
Form correct
+
Progression correct
+
Match Engine integrated
+
Full competition season works
+
Multi-competition coordination works
+
Deterministic replay works
+
Cross-process determinism works
+
Phase 5 remains frozen
```

Phase 6 is now considered **FROZEN** before Phase 7 begins.

## Phase 7 — Transfer Engine

Phase 7 introduces the deterministic player-transfer layer.

Its responsibility is to create plausible movement of players between clubs at
season/transfer-window boundaries while preserving the responsibilities of the
Player, Career, Match, and Competition engines.

Core flow:

```text
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
```

The transfer system must create **believable movement**, not random movement.

### Phase 7 Internal Stages

Phase 7 is developed incrementally:

```text
7A — Market Value & Contract State
7B — Club Needs & Player Fit
7C — Transfer Market & Offer Generation
7D — Player / Club Decision Resolution
7E — Transfer Application & Next-Season Integration
```

Do not implement all five subphases in one pass.

### Phase 7 Explicit Non-Goals

Do NOT initially implement:

- injuries
- relationships
- media
- narrative generation
- community decisions
- agent simulation
- real-time negotiations
- multiplayer transfer market
- mandatory LLM decisions
- loans
- advanced release-clause behavior
- complex financial accounting
- UI/API changes

These remain future systems.

---

### Phase 7A — Market Value & Contract State

Objective:

Create the economic and contractual state required for later transfer decisions.

#### Market Value

Market value is a derived football-market signal.

Relevant inputs may include:

```text
current ability
OVR
potential
age
development trajectory
form
playing time
performance
position scarcity
contract duration
club level
competition exposure
```

Market value is not intended to reproduce exact real-world transfer fees.

The target is:

```text
relative plausibility
+
internal consistency
+
determinism
```

Potential must matter more for younger players than for established veterans with
the same current ability.

#### Contract State

Conceptual fields:

```text
contract_start
contract_end
contract_years_remaining
wage_band
release_clause (optional)
```

Initial contract status:

```text
ACTIVE
EXPIRING_SOON
EXPIRED
```

Suggested contract-pressure interpretation:

```text
3+ years → low transfer pressure
2 years  → normal
1 year   → elevated availability
<1 year  → high availability
expired  → free-agent pathway
```

All values must be configurable.

---

### Phase 7B — Club Needs & Player Fit

Objective:

Determine which clubs genuinely need which players.

#### Squad Analysis

Each club should evaluate:

```text
squad size
position depth
starter quality
backup quality
age distribution
potential distribution
role coverage
formation needs
recent departures
```

#### Position Need

Conceptual:

```text
position_need =
    lack_of_depth
  + starter_quality_gap
  + age_risk
  + role_gap
  + squad_balance
```

The result must remain bounded and configurable.

#### Player Fit

A potential target may be evaluated from:

```text
player OVR
role effectiveness
primary position
secondary positions
manager preference
formation suitability
age
development potential
playing-time opportunity
club level compatibility
```

Conceptual:

```text
fit_score =
    quality_fit
  + role_fit
  + tactical_fit
  + age_fit
  + squad_need_fit
```

Do not duplicate tactical formulas from Phase 5.

#### Club Attractiveness

Use existing club-world information:

```text
prestige
league strength
competition participation
manager quality
facilities
squad quality
recent success
financial capability
```

Do not create a second club-strength system.

---

### Phase 7C — Transfer Market & Offer Generation

Objective:

Generate transfer candidates and offers.

#### TransferCandidate

Conceptual immutable structure:

```text
player_id
selling_club_id
buying_club_id
market_value
fit_score
interest_score
priority_score
```

#### TransferOffer

Conceptual immutable structure:

```text
id
player_id
selling_club_id
buying_club_id
transfer_fee
wage_offer
contract_years
structured_reason
seed
```

Structured reasons may include:

```text
DEPTH
STARTING_ROLE
YOUTH_INVESTMENT
STAR_REPLACEMENT
CONTRACT_EXPIRY
VALUE_OPPORTUNITY
```

Do not generate narrative prose.

#### Offer Preconditions

A club should generate meaningful interest when:

```text
club_need high
+
player_fit high
+
player_available
+
club_attractiveness sufficient
+
financial capability sufficient
```

The model should naturally avoid nonsensical transfers.

#### Transfer Windows

Initial conceptual windows:

```text
SUMMER_WINDOW
WINTER_WINDOW
```

Dates must be configuration-driven.

Transfers outside a valid window are invalid.

---

### Phase 7D — Player / Club Decision Resolution

An offer is not automatically a transfer.

#### Player Decision

Player evaluation may consider:

```text
sporting role
expected playing time
club attractiveness
competition level
career trajectory
contract quality
wage
current club situation
age
development opportunity
```

#### Club Decision

Selling club may consider:

```text
player importance
squad depth
player age
replacement availability
offer fee
contract status
```

Key players and high-potential young players should generally be more difficult
to sell without a sufficiently strong offer.

#### Deterministic Decision

Decision resolution may use deterministic seeded randomness:

```text
decision_score
      ↓
SHA-256 derived RNG
      ↓
accept / reject
```

Randomness is a controlled uncertainty layer, not a replacement for the decision model.

---

### Phase 7E — Transfer Application & Next-Season Integration

Objective:

Apply accepted transfers to the Football World.

#### TransferResult

Conceptual immutable structure:

```text
transfer_id
player_id
from_club_id
to_club_id
fee
accepted
completed
```

#### Membership Transition

The transition is:

```text
Player
   ↓
ClubMembership
   ↓
new ClubMembership
```

The Player identity must never be recreated.

Player remains the single football identity source.

Historical club memberships remain available for career history.

#### Contract Transition

On completed transfer:

```text
old contract → closed
new contract → active
```

There must never be two active contracts for the same player.

#### Squad Integration

After a completed transfer:

```text
selling club loses player
buying club gains player
```

A player cannot belong to two active squads simultaneously.

---

### Phase 7 Global Transfer Rules

1. Only eligible players may transfer.
2. Buying and selling clubs must differ.
3. Transfers must occur inside configured windows.
4. One player may complete at most one transfer per window.
5. A club may not purchase the same player twice in one window.
6. Completed transfers must update membership atomically.
7. Historical membership data must remain intact.
8. All decisions must be deterministic.
9. Invalid states must raise explicit errors.
10. Transfer logic must not modify previous-season results.

---

### Transfer Fee Model

A transfer fee should be related to market value.

Conceptually:

```text
transfer_fee =
    market_value
    × negotiation_factor
    × urgency_factor
    × contract_factor
```

All factors must be bounded and configurable.

No requirement exists to reproduce real-world fee distributions exactly.

---

### Free Transfers

When:

```text
contract expired
```

the player may enter:

```text
FREE_AGENT_MARKET
```

No transfer fee is required.

The player may still evaluate available offers.

---

### Youth Transfers

Young high-potential players should not automatically transfer.

An academy club may retain a player when:

```text
age low
+
potential high
+
facilities strong
+
reasonable path to playing time
```

This should emerge from the model rather than from scripted wonderkid behavior.

---

### Star Player Protection

High-value stars should normally require stronger transfer pressure:

```text
very strong offer
OR
player wants to leave
OR
club sporting decline
OR
contract pressure
```

No narrative scripting is required.

---

### Multi-Offer Resolution

A player may receive several offers.

At most one can be accepted.

Suggested deterministic ranking:

```text
player_preference_score DESC
sporting_fit DESC
playing_time_opportunity DESC
club_attractiveness DESC
offer_quality DESC
club_id ASC
```

The final result must remain deterministic.

---

### Transfer Chains

Prevent:

```text
Player A → Club B
and then
Player A → Club C
```

within the same transfer window.

A completed transfer locks the player for that window.

---

### Out of Scope

Initial Phase 7 does not implement:

```text
LOANS
AGENTS
ADVANCED RELEASE CLAUSES
COMPLEX NEGOTIATIONS
```

These may be added in later phases.

---

### Transfer Decision Explainability

The engine must expose structured evidence where useful.

Example:

```text
interest_score = 78.4
need_score = 86.0
player_fit = 81.7
playing_time_projection = 74.0
financial_feasibility = 69.0
```

No free-form prose is required.

---

### Desired Feedback Loops

Transfers should allow these emergent loops.

#### Playing-Time Loop

```text
high OVR
+
low playing time
        ↓
transfer interest
        ↓
better opportunity
        ↓
transfer
        ↓
more minutes
        ↓
future development
```

#### Squad-Balance Loop

```text
player departure
        ↓
position shortage
        ↓
club need
        ↓
market search
        ↓
recruitment
```

#### Promotion / Relegation Context

Promotion or relegation itself belongs to the Competition system.

Transfer Engine consumes the resulting world state.

Promoted clubs may become more attractive and acquire stronger targets.
Relegated clubs may become less attractive and lose players.

---

### Data Ownership

```text
Player Engine
→ player attributes / OVR / potential

Career Engine
→ career trajectory / development

Competition Engine
→ competitions / matches / standings / progression

Transfer Engine
→ market / offers / decisions / membership transitions
```

No cross-ownership.

---

### Persistence Boundary

Pure Transfer Engine logic must remain infrastructure-independent.

Future persistence adapters may store:

```text
contracts
transfer offers
completed transfers
membership history
market snapshots
```

The transfer calculations themselves must work without SQLite.

---

### Recommended Package Structure

Only create files as required by each subphase.

Possible final structure:

```text
backend/app/transfer/
├── __init__.py
├── domain.py
├── market.py
├── needs.py
├── fit.py
├── offers.py
├── decisions.py
└── application.py
```

This is a recommendation, not a requirement to create everything at once.

---

### Deterministic Randomness

Phase 7 follows the global deterministic rule:

```text
same seed
+
same initial state
+
same rules version
=
same transfer results
```

Preferred derivation:

```text
season seed
   ↓
transfer window seed
   ↓
player / club pair seed
   ↓
offer / decision seed
```

Use stable SHA-256 derivation.

Do not use Python's built-in `hash()` for simulation seeds.

---

### Phase 7A Acceptance Criteria

7A is complete when:

```text
MarketValue exists
+
ContractState exists
+
contract expiry works
+
values are deterministic
+
distribution audit passes
+
Phase 5 regression passes
+
Phase 6 regression passes
+
no infrastructure leakage
```

---

### Phase 7B Acceptance Criteria

7B is complete when:

```text
ClubNeed exists
+
PlayerFit exists
+
position deficiencies are detectable
+
manager preference influences fit
+
club attractiveness influences fit
+
deterministic output
```

---

### Phase 7C Acceptance Criteria

7C is complete when:

```text
candidates generate
+
offers generate
+
transfer windows are respected
+
multiple offers are supported
+
duplicate transfers are prevented
+
ordering is deterministic
```

---

### Phase 7D Acceptance Criteria

7D is complete when:

```text
player decisions work
+
club decisions work
+
accept/reject is deterministic
+
multiple offers resolve correctly
+
impossible transfers are rejected
```

---

### Phase 7E Acceptance Criteria

7E is complete when:

```text
completed transfers update membership
+
old club loses player
+
new club gains player
+
contracts transition correctly
+
history remains intact
+
duplicate memberships are impossible
+
next-season lineup uses new club
```

---

### Global Phase 7 Acceptance

The complete flow becomes:

```text
Season N
   ↓
Competition Completion
   ↓
Transfer Window
   ↓
Market Generation
   ↓
Offers
   ↓
Decisions
   ↓
Transfers
   ↓
Season N+1
```

This is the first phase that introduces meaningful **club mobility** into the long-term
career simulation.

---

### Phase 7 Balance Audits

Once the complete phase exists, evaluate large samples.

Recommended minimum:

```text
500 careers
```

Preferred:

```text
1,000 careers
```

Measure distributions of:

```text
average transfers
median transfers
transfers by age
transfers by OVR
transfers by position
free transfers
high-value transfers
club movement
elite-club concentration
playing-time changes
development changes
```

Analyze distributions and percentiles, not only averages.

---

### Phase 7 Transfer Concentration Audit

Verify elite clubs do not acquire every high-potential player.

Desired:

```text
talent moves
+
club differentiation remains
+
competition remains meaningful
```

Undesired:

```text
all elite talent → top clubs
```

---

### Phase 7 Market Activity Audit

Avoid both extremes:

```text
0 transfers every season
```

and:

```text
almost every player transfers every season
```

The target is believable transfer activity.

---

### Phase 7 Career Feedback Audit

Eventually measure:

```text
low playing time
→ transfer probability
```

and:

```text
transfer
→ minutes change
→ performance change
→ development change
```

The transfer system should influence careers without completely dominating them.

---

### Phase 7 Determinism Audit

For identical:

```text
world state
player state
club state
season
transfer window
seed
rules version
```

the engine must reproduce:

```text
identical market
identical offers
identical decisions
identical completed transfers
identical final memberships
```

Cross-process byte-for-byte deterministic reproduction is required for final Phase 7 acceptance.

---

### Phase 7 Definition of Done

Phase 7 is complete only when:

```text
7A Market Value & Contracts
+
7B Club Needs & Player Fit
+
7C Market & Offers
+
7D Decision Resolution
+
7E Transfer Application
```

all pass:

```text
unit tests
integration tests
determinism tests
cross-process tests
invariant tests
large-scale balance audits
```

and:

```text
Phase 5 remains frozen
Phase 6 remains frozen
no infrastructure leakage
no duplicated simulation formulas
```

## Phase 8 — Event Engine

Implement later:

- data-driven events
- conditions
- probabilities
- effects
- decisions

## Phase 9 — Narrative Engine

Implement later:

- timeline
- story beats
- career arcs
- legacy score
- narrative generation

## Phase 10 — Frontend

Implement later:

- player creation
- career dashboard
- season view
- match view
- timeline
- statistics
- transfers
- retirement
- story screen

## Phase 11 — Visual Polish

Implement later:

- dark theme
- typography
- animations
- player cards
- trophy presentation
- timeline animations
- microinteractions

## Phase 12 — TikTok Presentation Mode

Implement later:

- 9:16 layout
- 1080×1920 target
- scene system
- recording-friendly presentation

## Phase 13 — Simulation Balance

Run hundreds or thousands of complete careers and tune:

- career length
- peak overall
- final overall
- match performance
- transfers
- injuries
- goals
- trophies
- retirement age
- potential attainment
- late bloomers
- failures

---

# 9. TECHNOLOGY STACK

## Backend

```text
Python 3.12+
FastAPI
Pydantic
SQLAlchemy
Alembic
SQLite
Pytest
```

## Frontend

```text
Angular
TypeScript
SCSS
RxJS
Angular Router
Standalone Components
```

---

# 10. HIGH-LEVEL ARCHITECTURE

```text
Angular
   │
   │ REST
   ▼
FastAPI
   │
   ▼
Application Services
   │
   ├───────────────┐
   ▼               ▼
Simulation      Persistence
Engine          Layer
   │               │
   ▼               ▼
Domain         SQLAlchemy
Results           │
                  ▼
                SQLite
```

The domain and simulation engine must remain independent of infrastructure.

---

# 11. SIMULATION ENGINE INDEPENDENCE

The Simulation Engine MUST NOT depend on:

- Angular
- TypeScript
- FastAPI
- HTTP
- SQLAlchemy
- SQLite
- REST

Pure business calculations must be testable without infrastructure.

Persistence adapters may use SQLAlchemy.

---

# 12. DETERMINISTIC RANDOMNESS

Every major simulation operation must support a seed.

Requirement:

```text
same seed
+
same initial state
+
same rules version
=
same result
```

Use stable hashing such as SHA-256.

Do NOT use Python's built-in `hash()` to derive simulation seeds.

Preferred pattern:

```python
seed_material = f"{career_seed}:{entity_id}:{step_number}"
seed_hash = sha256(seed_material.encode("utf-8")).hexdigest()
seed_int = int(seed_hash[:16], 16)
rng = random.Random(seed_int)
```

---

# 13. DATA-DRIVEN RULES

Suggested:

```text
backend/data/
├── rules/
│   ├── world.json
│   ├── player_attributes.json
│   ├── player_development.json
│   ├── player_roles.json
│   ├── player_traits.json
│   ├── player_archetypes.json
│   ├── career_archetypes.json
│   ├── match.json
│   ├── lineup.json
│   ├── competitions.json
│   └── narrative.json
```

Large collections of rules should be configurable rather than hardcoded.

---

# 14. FOOTBALL WORLD

Core entities:

```text
Country
League
Club
Manager
Competition
Player
ClubMembership
```

The same Player domain is used for generic players and future protagonists.

---

# 15. EXTERNAL DATA PHILOSOPHY

External rankings are initial references, not immutable truths.

Suggested references:

```text
Opta  → club/league current strength reference
UEFA  → European club coefficient reference
IFFHS → historical league strength reference
FIFA  → national team strength reference
Manual/Generated → prestige, academy, facilities, financial inputs
```

After simulation begins, internal simulation rules become the source of truth.

---

# 16. DATA SOURCE METADATA

Important external data can retain:

```text
data_source
source_date
source_name
source_value
normalized_value
```

Possible source IDs:

```text
OPTA
UEFA
IFFHS
FIFA
MANUAL
GENERATED
```

---

# 17. CLUB SYSTEM

Each club contains conceptually:

```text
id
name
country
league_id
manager_id
current_strength
prestige
financial_power
academy_quality
facilities
fan_pressure
squad_depth
uefa_coefficient_raw
uefa_coefficient_normalized
domestic_reputation
international_reputation
momentum
```

Values are primarily 0–100 except raw coefficients and momentum.

---

# 18. CLUB CURRENT STRENGTH

Suggested structure:

```text
CURRENT_STRENGTH =
    SQUAD_BASE           × 0.75
  + MANAGER_QUALITY      × 0.05
  + SQUAD_DEPTH          × 0.10
  + FACILITIES           × 0.03
  + MOMENTUM_NORMALIZED  × 0.07
```

Clamp to 1–100.

Prestige does not directly enter current sporting strength.

---

# 19. CLUB SQUAD LINES

```text
Attack
Midfield
Defense
Goalkeeper
```

These are derived from current Player/ClubMembership data.

---

# 20. CLUB PRESTIGE

Suggested:

```text
PRESTIGE =
    historical_success × 0.35
  + european_history   × 0.25
  + domestic_history   × 0.15
  + global_reputation  × 0.15
  + fanbase            × 0.10
```

Prestige changes slowly over time.

---

# 21. CLUB FINANCIAL POWER

```text
FINANCIAL_POWER =
    revenue             × 0.35
  + ownership_capacity  × 0.20
  + league_money        × 0.20
  + european_income     × 0.15
  + commercial_power    × 0.10
```

This is not a full accounting simulator.

---

# 22. CLUB ACADEMY

Academy quality influences youth-player probability distributions, not exact deterministic ratings.

Conceptual model:

```text
ACADEMY_QUALITY =
    academy_reputation   × 0.40
  + facilities           × 0.25
  + youth_investment     × 0.20
  + country_youth_factor × 0.15
```

---

# 23. CLUB FACILITIES

```text
FACILITIES =
    training_facilities × 0.60
  + medical_facilities  × 0.20
  + youth_facilities    × 0.20
```

Development modifier baseline:

```text
development_modifier =
1 + ((facilities - 50) / 500)
```

---

# 24. LEAGUE SYSTEM

Each league contains conceptually:

```text
id
name
country
tier
current_strength
prestige
financial_strength
european_performance
global_reputation
```

Suggested league strength:

```text
LEAGUE_STRENGTH =
    top_4_average        × 0.35
  + top_8_average        × 0.25
  + middle_average       × 0.20
  + bottom_average       × 0.10
  + european_performance × 0.10
```

---

# 25. COUNTRY / NATIONAL TEAM

Countries may contain:

```text
id
name
fifa_rank
fifa_points
national_strength
```

FIFA data is the initial reference for national strength.

---

# 26. MANAGER SYSTEM

Managers contain conceptually:

```text
id
name
tactical_quality
player_development
game_management
rotation
adaptability
tactical_style
youth_preference
discipline
```

Manager quality:

```text
MANAGER_QUALITY =
    tactical_quality   × 0.30
  + player_development × 0.25
  + game_management    × 0.20
  + rotation           × 0.10
  + adaptability       × 0.15
```

---

# 27. PLAYER DOMAIN

There is exactly one fundamental football `Player` entity.

```text
Generic world player
└── Player + ClubMembership

Career protagonist
└── Player + Career
```

Do not create separate football models for generic and career players.

---

# 28. PLAYER IDENTITY

```text
id
name
surname
nationality
birth_date
height
weight
preferred_foot
primary_position
secondary_positions
```

---

# 29. INTERNAL PLAYER ATTRIBUTES

## Pace

```text
acceleration
sprint_speed
```

## Shooting

```text
finishing
shot_power
long_shots
volleys
penalties
```

## Passing

```text
vision
short_passing
long_passing
crossing
curve
```

## Dribbling

```text
agility
balance
ball_control
dribblling
reactions
```

## Defending

```text
defensive_awareness
standing_tackle
interceptions
heading
```

## Physical

```text
strength
stamina
jumping
aggression
```

## Mental

```text
decision_making
composure
creativity
positioning
concentration
work_rate
leadership
```

All internal attributes use 1–100.

---

# 30. VISIBLE ATTRIBUTE GROUPS

```text
PAC
SHO
PAS
DRI
DEF
PHY
```

MENTAL is derived separately.

The visible groups are derived from internal attributes and should not be duplicated as independent stored values when avoidable.

---

# 31. MENTAL

```text
MENTAL =
    decision_making × 0.20
  + composure       × 0.15
  + creativity      × 0.15
  + positioning     × 0.15
  + concentration   × 0.15
  + work_rate       × 0.10
  + leadership      × 0.10
```

---

# 32. CURRENT ABILITY

```text
CURRENT_ABILITY =
    PAC    × 0.15
  + SHO    × 0.15
  + PAS    × 0.15
  + DRI    × 0.15
  + DEF    × 0.15
  + PHY    × 0.15
  + MENTAL × 0.10
```

Clamp to 1–100.

---

# 33. POSITION-SPECIFIC OVR

Current Ability is general quality.

OVR is position-specific effectiveness.

Changing evaluated position must not mutate internal attributes.

Starting examples:

### ST

```text
SHO 35
PAC 20
DRI 20
PHY 10
PAS 10
MENTAL 5
```

### LW/RW

```text
DRI 25
PAC 25
SHO 20
PAS 15
PHY 10
MENTAL 5
```

### CAM/AM

```text
PAS 25
DRI 20
MENTAL 20
SHO 15
PAC 10
PHY 10
```

### CM

```text
PAS 25
DRI 20
MENTAL 20
DEF 15
PHY 10
SHO 10
```

### DM

```text
DEF 25
PAS 25
MENTAL 20
PHY 15
DRI 10
SHO 5
```

### CB

```text
DEF 35
PHY 25
MENTAL 15
PAS 15
PAC 10
```

### LB/RB

```text
DEF 25
PAC 20
PHY 15
PAS 15
DRI 15
MENTAL 10
```

---

# 34. GOALKEEPER ATTRIBUTES

Goalkeepers:

```text
diving
handling
kicking
reflexes
speed
goalkeeper_positioning
```

GK uses a dedicated OVR calculation.

---

# 35. PLAYER ARCHETYPES

Generation archetypes include:

```text
BALANCED
FINISHER
TARGET
PLAYMAKER
BOX_TO_BOX
BALL_PLAYING
STOPPER
SHOT_STOPPER
SWEEPER_KEEPER
```

These describe generation tendencies and are not career archetypes.

---

# 36. ROLE SYSTEM

Role definitions contain:

- id
- compatible_positions
- attribute_weights

Examples:

```text
ADVANCED_FORWARD
POACHER
FALSE_9
TARGET_FORWARD
WINGER
PLAYMAKER
BALL_WINNER
CENTRE_BACK
SWEEPER_KEEPER
TRADITIONAL_KEEPER
FULL_BACK
WING_BACK
INVERTED_FULL_BACK
```

---

# 37. ROLE ATTRIBUTE FIT

```text
ATTRIBUTE_FIT =
Σ(attribute_group × role_weight)
```

---

# 38. ROLE FAMILIARITY

Range:

```text
0–100
```

Initial targets:

```text
Primary role      80–95
Secondary role    55–80
Unnatural role    20–50
```

Role familiarity does not directly mutate base attributes.

---

# 39. ROLE EFFECTIVENESS

```text
ROLE_EFFECTIVENESS =
    ATTRIBUTE_FIT    × 0.70
  + ROLE_FAMILIARITY × 0.30
```

Do not directly multiply OVR by familiarity.

---

# 40. TRAITS / PLAYSTYLES

Configurable IDs include:

```text
FINESSE_SHOT
POWER_SHOT
FIRST_TOUCH
LONG_BALL
SET_PIECE
RAPID
STRONG
AERIAL
ENDURANCE
BIG_GAME_PLAYER
LEADER
COMPOSED
CREATIVE
CLUTCH
```

Initial variable distribution:

```text
0 traits → ~35%
1 trait  → ~40%
2 traits → ~20%
3 traits → ~5%
```

Traits are contextual behaviors, not universal OVR bonuses.

---

# 41. PERSONALITY

```text
ambition
loyalty
professionalism
ego
temper
leadership
sociability
```

Range: 0–100.

Personality consequences are implemented only in later phases.

---

# 42. POTENTIAL

Rule:

```text
potential >= current_ability
```

Potential is a theoretical ceiling, not a guarantee.

Potential 95+ must be rare and 100 exceptional.

---

# 43. DEVELOPMENT RATE

Range: 0–100.

```text
0–30    Very slow
31–50   Slow
51–70   Normal
71–85   Fast
86–100  Exceptional
```

Development Rate is not annual growth.

---

# 44. DEVELOPMENT PROFILES

Profiles:

```text
BALANCED
TECHNICAL
PHYSICAL
CREATIVE
DEFENSIVE
FINISHER
PLAYMAKER
ATHLETIC
LATE_BLOOMER
```

They determine development direction rather than fixed yearly bonuses.

---

# 45. PLAYER STATE

```text
confidence
morale
form
fitness
fatigue
happiness
reputation
```

Range 0–100.

Phase 3 initializes and validates state. Later systems evolve it.

---

# 46. CLUB MEMBERSHIP

```text
ClubMembership
├── player_id
├── club_id
├── role
├── start_date
└── end_date
```

Role belongs to membership, not Player identity.

---

# 47. CAREER DOMAIN

Career contains professional history.

Conceptually:

```text
Career
├── player_id
├── start_date
├── end_date
├── current_season
├── seasons
├── snapshots
├── events
├── transfers
├── injuries
├── awards
├── titles
├── international_career
├── timeline
└── narrative
```

Only the parts assigned to each phase may be implemented.

---

# 48. PHASE 4 CAREER ENGINE

Phase 4 transforms a static Player into a progressing career.

```text
Career
 ↓
Season Start
 ↓
Development
 ↓
Season End
 ↓
Snapshot
 ↓
Next Season
```

---

# 49. DEVELOPMENT BUDGET

```text
DEVELOPMENT_BUDGET =
    BASE_RATE
  × POTENTIAL_FACTOR
  × AGE_FACTOR
  × DEVELOPMENT_RATE_FACTOR
  × PLAYING_TIME_FACTOR
  × ENVIRONMENT_FACTOR
  × PROFESSIONALISM_FACTOR
  × PERFORMANCE_FACTOR
  × PLAYER_STATE_FACTOR
  × RANDOM_FACTOR
```

Current calibrated baseline:

```text
BASE_RATE = 4.0
```

---

# 50. POTENTIAL FACTOR

Initial Phase 4 model:

```text
potential_gap = potential - current_ability
potential_factor = clamp(potential_gap / 30.0, 0, 1)
```

Keep configurable.

---

# 51. AGE FACTOR

Baseline:

```text
16–18 → 1.40
19–21 → 1.25
22–24 → 1.10
25–27 → 0.85
28–30 → 0.60
31–33 → 0.35
34+   → 0.10
```

The season beginning at age N uses the age-N factor.

---

# 52. PLAYING TIME FACTOR

Phase 4 neutral baseline:

```text
0–300       → 0.30
301–750     → 0.55
751–1400    → 0.80
1401–2200   → 1.00
2201–3000   → 1.05
3000+       → 1.00
```

Phase 5 replaces the neutral minutes input with actual match-derived minutes.

---

# 53. ENVIRONMENT FACTOR

Conceptually based on:

- facilities
- manager.player_development

Use small contextual modifiers so environment matters without dominating development.

---

# 54. PROFESSIONALISM FACTOR

Baseline:

```text
low professionalism     → ~0.92
average                  → ~1.00
high                     → ~1.08
```

---

# 55. PERFORMANCE FACTOR

Phase 4 neutral baseline:

```text
average_rating = 6.8
performance_factor = 1.0
```

Formula:

```text
performance_factor = 1.0 + ((average_rating - 6.8) / 10.0)
```

Phase 5 provides actual seasonal average rating.

---

# 56. PLAYER STATE FACTOR

Use a small aggregate of relevant state values.

Phase 4 baseline remains simple.

Later phases can make state dynamic.

---

# 57. RANDOM FACTOR

Initial baseline:

```text
0.85–1.15
```

Must be deterministic through seeded RNG.

---

# 58. TWO-STAGE DEVELOPMENT ALLOCATION

Stage 1:

```text
Development Budget
        ↓
PAC / SHO / PAS / DRI / DEF / PHY / MENTAL
```

Stage 2:

```text
Group Budget
        ↓
Internal attribute multipliers
        ↓
Normalized internal deltas
        ↓
Soft caps
```

Important semantic rule:

> A Group Budget represents intended weighted-average growth of that visible group, not the sum of raw sub-attribute points.

The normalized internal deltas must preserve the calculation-weighted group average.

---

# 59. INTERNAL ATTRIBUTE SOFT CAPS

Baseline development resistance:

```text
<80     ×1.00
80–89   ×0.85
90–94   ×0.60
95–97   ×0.30
98+     ×0.10
```

Soft caps are not hard caps.

---

# 60. DECLINE

Decline operates directly on internal attributes.

Category priority:

```text
Physical > Technical > Mental
```

Physical attributes decline faster.

Technical attributes decline slowly.

Mental attributes normally remain stable or decline very slowly.

The system should allow a veteran to transform rather than simply collapse.

---

# 61. CAREER PHASE

Age-first phase hierarchy:

```text
YOUTH       <18
EARLY_PRO   18–20
DEVELOPMENT 21–23
PRIME       24–28
LATE_PRIME  29–31
DECLINE     32–34
VETERAN     35+
```

---

# 62. PEAK TRACKING

Track:

```text
peak_current_ability
peak_ovr
peak_age
peak_position
peak_club
```

Whenever a new peak is reached, update peak information.

---

# 63. SEASON SNAPSHOT

A season snapshot preserves enough data for debugging, replay, narrative and analysis.

Example:

```json
{
  "season": "2029/30",
  "age": 20,
  "club_id": "arsenal",
  "starting_ability": 71,
  "ending_ability": 75,
  "starting_ovr": 72,
  "ending_ovr": 76,
  "minutes": 1820,
  "development_budget": 2.4,
  "development_summary": {
    "shooting": 1.2,
    "dribbling": 0.7,
    "mental": 0.5
  }
}
```

---

# 64. PHASE 4 DETERMINISM

Given:

```text
career seed
+
player seed/state
+
world state
+
rules version
```

the same career must produce the same seasonal state, development and snapshots.

---

# 65. CAREER ARCHETYPE CLASSIFIER

Phase 4.1B uses a pure multi-label classifier.

Supported tags:

```text
WONDERKID
FAILED_WONDERKID
SUPERSTAR
LONG_PRIME
LATE_BLOOMER
EARLY_DECLINER
SOLID_PRO
```

Multiple major tags can coexist.

`SOLID_PRO` is a fallback only when no major archetype is detected.

---

# 66. CAREER ARCHETYPE RULES

Current empirical configuration:

```text
WONDERKID:
    starting_age <= 17
    AND starting_ca >= P80 threshold
    AND potential >= P80 threshold

FAILED_WONDERKID:
    starting_age <= 17
    AND potential >= P85 threshold
    AND potential_realization_pct <= 82

SUPERSTAR:
    peak_ovr >= 88

LONG_PRIME:
    peak_age >= 27
    AND seasons_within_98_percent_of_peak >= 19

LATE_BLOOMER:
    peak_age >= 28
    AND post_age_24_ca_growth >= 1.5

EARLY_DECLINER:
    peak_age <= 29
    AND peak_to_final_ca_decline >= 3.0
```

Thresholds are configurable.

The classifier must not modify simulation outcomes.

---

# 67. PHASE 5 — MATCH ENGINE OVERVIEW

Phase 5 introduces the match-performance loop.

Core flow:

```text
Player
+
Club
+
Role
+
State
+
Opponent
+
MatchContext
        ↓
Match Engine
        ↓
Match Result
+
Minutes
+
Goals
+
Assists
+
Player Ratings
        ↓
Season Performance
        ↓
Career Engine
        ↓
Development
```

Phase 5 must remain separate from Career Engine.

The Match Engine produces football performance.

The Career Engine interprets that performance for development.

---

# 68. PHASE 5 INTERNAL STAGES

Phase 5 is developed incrementally:

```text
5A — Match Domain
5B — Lineup + Team Strength
5C — Match Resolution
5D — Player Performance
5E — Season Aggregation
5F — Career Integration
```

Never implement all five subphases in one pass unless explicitly requested.

---

# 69. PHASE 5A — MATCH DOMAIN

Create pure domain objects for:

```text
MatchContext
MatchResult
PlayerMatchPerformance
MatchEvent
```

## MatchContext

Minimum conceptual fields:

```text
competition
competition_importance
home_club
away_club
home_advantage
match_importance
rivalry_factor
seed
```

No persistent injuries or future transfer state are required.

## MatchResult

Minimum fields:

```text
home_score
away_score
home_xg
away_xg
possession
shots
shots_on_target
player_performances
events
```

## PlayerMatchPerformance

Minimum fields:

```text
player_id
minutes
rating
goals
assists
shots
shots_on_target
key_passes
tackles
interceptions
clearances
role
position
match_influence
```

## MatchEvent

Possible events:

```text
goal
assist
yellow_card
red_card
substitution
missed_chance
big_save
key_pass
great_defensive_action
```

Persistent injuries remain outside Phase 5.

---

# 70. PHASE 5B — LINEUP ENGINE

The Lineup Engine selects the XI using:

```text
OVR
+
Role Effectiveness
+
Form
+
Fitness
+
Manager Preference
+
Rotation
```

Starting conceptual selection score:

```text
selection_score =
    OVR                × 0.50
  + role_effectiveness × 0.20
  + form               × 0.10
  + fitness            × 0.10
  + manager_preference × 0.10
```

Values are configurable.

---

# 71. FORMATION PRESETS

Initial formation presets may include:

```text
4-3-3
4-2-3-1
4-4-2
3-5-2
3-4-3
4-1-4-1
```

Formation is configuration, not a full tactical AI system.

Managers may prefer formations/styles.

---

# 72. TACTICAL STYLES

Initial manager styles may include:

```text
ATTACKING
BALANCED
POSSESSION
COUNTER
DEFENSIVE
YOUTH
```

Styles modify context modestly.

They must not dominate player quality.

---

# 73. TACTICAL FIT

Tactical Fit is influenced by:

- correct position
- Role Familiarity
- manager style
- formation suitability

Scale:

```text
0–100
```

High tactical fit should provide a moderate advantage.

---

# 74. XI QUALITY

Conceptual baseline:

```text
XI Quality = weighted average of starting XI effectiveness
```

Suggested line weights:

```text
GK      10%
DEF     30%
MID     30%
ATT     30%
```

Configuration may later refine these.

---

# 75. EFFECTIVE TEAM STRENGTH

Initial model:

```text
effective_team_strength =
    XI_quality          × 0.65
  + club_strength       × 0.15
  + manager_quality     × 0.05
  + tactical_fit        × 0.05
  + form_factor         × 0.05
  + fitness_factor      × 0.05
```

The weights are initial calibration values and must remain configurable.

---

# 76. HOME ADVANTAGE

Initial baseline:

```text
home_advantage = +3 strength points
```

Home advantage modifies probability rather than guaranteeing victory.

---

# 77. MATCH WIN PROBABILITY

A continuous probability function should be used.

Conceptual:

```text
strength_difference =
    home_effective_strength
  - away_effective_strength
  + home_advantage
```

Then:

```text
win_bias =
    1 / (1 + exp(-strength_difference / scale))
```

The scale parameter is configurable.

Strong teams should be favored, not guaranteed to win.

---

# 78. EXPECTED GOALS

The engine uses expected goals as an intermediate abstraction.

Conceptual:

```text
home_xG =
    base_home_xG
  × home_attack_factor
  × away_defensive_factor

away_xG =
    base_away_xG
  × away_attack_factor
  × home_defensive_factor
```

The exact formulas and baselines are configurable and must be calibrated statistically.

---

# 79. GOAL GENERATION

Final goals may be sampled from a suitable discrete distribution, initially Poisson or another transparent alternative.

Requirements:

- low-score outcomes should be common
- high-score outliers should be possible
- strong teams should generally generate higher xG
- upsets must remain possible

The same match seed must reproduce the same result.

---

# 80. ATTACK FACTOR

Attack factor should be influenced by:

```text
attack quality
midfield quality
role effectiveness
form
fitness
```

Do not base attacking output on OVR alone.

---

# 81. DEFENSIVE FACTOR

Defensive factor should be influenced by:

```text
defense quality
goalkeeper quality
midfield protection
tactical fit
form
fitness
```

Goalkeepers use their dedicated attributes and GK OVR.

---

# 82. MATCH VARIANCE

The engine must include deterministic controlled variance.

Variance may influence:

- chance creation
- finishing
- goalkeeper saves
- player performance
- match outcome

Variance must not erase team quality completely.

---

# 83. POSSESSION

Possession may be derived from:

```text
midfield quality
+
tactical style
+
tactical fit
+
match variance
```

Do not simulate every possession event.

---

# 84. CHANCE GENERATION

The engine should derive:

```text
shots
shots_on_target
big_chances
```

from xG and configured chance-distribution rules.

---

# 85. PLAYER CHANCE DISTRIBUTION

Offensive chances are distributed based on:

```text
position
OVR
Role Effectiveness
SHO
PAC
DRI
PAS
MENTAL
Form
Fitness
```

A player with strong attacking characteristics should generally receive more relevant opportunities.

---

# 86. PLAYER CHANCE SHARE

Conceptually:

```text
chance_share_i =
    attacking_contribution_i
    /
    Σ attacking_contribution
```

Then:

```text
Σ chance_share = 1
```

Example distribution:

```text
ST   32%
LW   22%
RW   18%
CAM  15%
CM    8%
Other 5%
```

Actual values must emerge from lineups and player profiles.

---

# 87. GOAL CONVERSION

Goal conversion for an individual chance may depend on:

```text
finishing
shot_power
composure
positioning
role
chance_quality
goalkeeper
```

Do not add universal OVR bonuses.

---

# 88. ASSISTS

Assist generation should use:

```text
vision
short_passing
long_passing
crossing
creativity
role
chance creation
```

Playmakers should generally generate more assists than defensive players with similar overall quality.

---

# 89. DEFENSIVE CONTRIBUTIONS

Structured defensive statistics may include:

```text
tackles
interceptions
clearances
recoveries
blocks
```

These do not require per-action simulation.

They can be generated statistically from the player context.

---

# 90. PLAYER MATCH INFLUENCE

Conceptual inputs:

```text
OVR
Role Effectiveness
Form
Fitness
Attributes
Traits
Player State
Match variance
```

Match influence should be a latent value used to derive performance statistics and rating.

---

# 91. TRAITS IN MATCH ENGINE

Traits gain contextual effects in Phase 5.

Examples:

```text
FINESSE_SHOT
→ improved finesse-shot conversion in applicable chances

RAPID
→ improved transition/space situations

AERIAL
→ improved aerial duel/chance performance

CREATIVE
→ improved chance creation

BIG_GAME_PLAYER
→ small bonus in high-importance matches

COMPOSED
→ improved performance under pressure

LEADER
→ small contextual team effect
```

Traits must never provide flat universal OVR increases.

---

# 92. PLAYER STATE IN MATCH ENGINE

State can modestly affect match effectiveness:

```text
confidence
morale
form
fitness
fatigue
happiness
reputation
```

Do not allow state factors to overpower actual football ability.

---

# 93. MATCH RATING

Base rating:

```text
6.0
```

Possible modifiers include:

```text
goal
assist
key_pass
big_chance_created
defensive_actions
major_mistake
team_result
minutes
```

Illustrative starting values:

```text
Goal               +0.90
Assist             +0.60
Key pass           +0.08
Big chance created +0.12
Tackle             +0.03
Interception       +0.03
Major mistake      -0.40
```

All values must be configurable and statistically calibrated.

---

# 94. ROLE-CONTEXTUAL RATING

The importance of statistics depends on role/position.

Examples:

- goals matter heavily for forwards
- chance creation matters heavily for playmakers
- tackles/interceptions matter more for defenders
- saves matter heavily for goalkeepers

A single universal rating formula is not required if role-specific contribution weights are configured cleanly.

---

# 95. MINUTES

Match Engine produces actual minutes:

```text
0
1–15
16–30
31–60
61–75
76–89
90
```

Minutes depend on:

```text
starter status
fitness
form
manager rotation
match importance
substitution logic
```

---

# 96. SUBSTITUTIONS

Initial simplified substitution logic may use:

```text
low stamina
poor performance
match state
manager style
match importance
```

Examples:

```text
Poor performance late
→ higher substitution probability

Winning late
→ increased defensive substitution probability

Losing late
→ increased attacking substitution probability
```

Do not build advanced tactical AI.

---

# 97. MATCH IMPORTANCE

Scale:

```text
0–100
```

Suggested references:

```text
League normal            40
League rivalry           60
Domestic cup             55
European group           65
European knockout        80
Semi-final               90
Final                   100
```

Values are configurable.

---

# 98. COMPETITION CONTEXT

Phase 5 may use a minimal competition context:

```text
league
 domestic cup
european
international
```

Each match should know:

```text
competition type
importance
home/away
```

Full realistic scheduling remains outside early Phase 5 if not required.

---

# 99. SEASON SCHEDULING BASELINE

Initial approximate match counts:

```text
League          ~34–38
Domestic Cup     0–8
European         0–15
International    0–12
```

These are configurable ranges, not hardcoded real-world schedules.

---

# 100. SEASON PERFORMANCE AGGREGATION

Aggregate individual match results into:

```text
SeasonPerformance
```

Suggested fields:

```text
appearances
starts
substitute_appearances
minutes
goals
assists
average_rating
shots
shots_on_target
key_passes
defensive_actions
clean_sheets
```

The aggregation layer remains pure domain logic.

---

# 101. PERFORMANCE FACTOR INTEGRATION

Convert season average rating into the Career Engine's Performance Factor.

Initial formula:

```text
performance_factor =
    clamp(
        1.0 + ((average_rating - 6.8) / 10.0),
        0.80,
        1.20
    )
```

Examples:

```text
6.0 → 0.92
6.8 → 1.00
7.5 → 1.07
8.2 → 1.14
```

The Match Engine produces the rating; Career Engine consumes the aggregated factor.

---

# 102. PLAYING TIME INTEGRATION

The Match Engine's season minutes replace the Phase 4 neutral value.

Career Engine then evaluates:

```text
0–300       → 0.30
301–750     → 0.55
751–1400    → 0.80
1401–2200   → 1.00
2201–3000   → 1.05
3000+       → 1.00
```

---

# 103. CAREER FEEDBACK LOOP

The complete feedback loop becomes:

```text
Player
  ↓
Lineup Selection
  ↓
Match
  ↓
Minutes / Performance
  ↓
Season Aggregation
  ↓
Performance Factor
  +
Playing Time Factor
  ↓
Career Engine
  ↓
Development
  ↓
Player Attributes
  ↓
OVR
  ↓
Future Lineup Selection
```

This is the central gameplay loop.

---

# 104. BREAKTHROUGH LOOP

A young player may naturally enter a positive feedback loop:

```text
high OVR/fit
↓
higher selection probability
↓
more minutes
↓
better development opportunity
↓
attributes increase
↓
OVR increases
↓
more selection probability
```

This should emerge from the systems rather than be scripted.

---

# 105. STAGNATION LOOP

Likewise:

```text
low OVR / poor fit
↓
bench
↓
low minutes
↓
slow development
↓
stagnation
```

This should naturally support failed wonderkid careers.

---

# 106. MATCH VARIANCE PRINCIPLE

A strong team should not always win.

A player with OVR 85 should not always obtain a 7.3 rating.

A player with OVR 75 should occasionally have an outstanding match.

The same deterministic seed must reproduce those surprises.

---

# 107. MATCH RESULT ACCEPTANCE CRITERIA

After Phase 5 resolution is implemented, large statistical samples should be evaluated.

At minimum:

```text
100,000 matches
```

Measure:

- average goals per match
- home advantage
- draw percentage
- upset frequency
- shots
- shots on target
- xG distribution
- player rating distribution
- goal distribution
- assist distribution
```

The goal is plausibility, not exact replication of real-world statistics.

---

# 108. CAREER ACCEPTANCE CRITERIA WITH MATCH ENGINE

Run approximately:

```text
1,000 careers
```

Compare:

```text
CAREER ENGINE WITHOUT MATCH ENGINE
vs
CAREER ENGINE + MATCH ENGINE
```

The integrated system should produce meaningful differences in:

- minutes
- performance
- development
- potential realization
- peak age
- peak OVR
- career archetypes

---

# 109. PHASE 5A ACCEPTANCE TEST

Must support:

```text
Create MatchContext
↓
Create MatchResult
↓
Create PlayerMatchPerformance
↓
Create MatchEvents
```

All domain objects must remain infrastructure-independent.

---

# 110. PHASE 5B ACCEPTANCE TEST

Must support:

```text
Select XI
↓
Choose formation
↓
Calculate Role Effectiveness
↓
Calculate Tactical Fit
↓
Calculate XI Quality
↓
Calculate Effective Team Strength
```

---

# 111. PHASE 5C ACCEPTANCE TEST

Must support:

```text
Team Strength
↓
Home Advantage
↓
Win Probability
↓
xG
↓
Score
```

Upsets must be possible.

---

# 112. PHASE 5D ACCEPTANCE TEST

Must support:

```text
Lineup
↓
Player opportunities
↓
Goals / assists
↓
Defensive contributions
↓
Minutes
↓
Match Rating
```

---

# 113. PHASE 5E ACCEPTANCE TEST

Must support:

```text
Match performances
↓
Season aggregation
↓
Minutes
↓
Goals
↓
Assists
↓
Average rating
↓
Performance Factor
```

---

# 114. PHASE 5F ACCEPTANCE TEST

Must support:

```text
Season Performance
↓
Performance Factor
+
Playing Time Factor
↓
Career Engine
↓
Development
↓
Next Season
```

No duplication of Career Engine development logic.

---

# 115. PHASE 5 EXPLICIT NON-GOALS

Do NOT implement in Phase 5:

- transfers
- contracts
- persistent injuries
- relationship engine
- narrative generation
- community decisions
- TikTok integration
- presentation mode
- advanced tactical AI
- full accounting simulation
- mandatory LLM integration
- complete real-world fixtures database

---

# 116. PERSISTENCE PRINCIPLES

Persistence models remain separate from domain objects.

Match persistence should only be introduced where needed for:

- debugging
- career history
- season statistics
- reproducibility

Do not persist every simulated micro-action unless a later requirement justifies it.

Prefer storing structured match results and meaningful player performance summaries.

---

# 117. DATABASE DIRECTION

Conceptual future relationships:

```text
Career
  ↓
Season
  ↓
SeasonPerformance
  ↓
Match
  ↓
PlayerMatchPerformance
```

Foreign keys and indexes should be explicit.

Player remains the single football identity source.

---

# 118. TESTING REQUIREMENTS

## World

Test:

- club calculations
- league calculations
- normalization
- deterministic seed
- manager quality
- momentum

## Player

Test:

- attribute ranges
- visible groups
- mental calculation
- Current Ability
- position OVR
- roles
- traits
- personality
- state
- development
- deterministic generation

## Career

Test:

- initialization
- age progression
- development budget
- potential factor
- age factor
- development rate
- playing time
- environment
- professionalism
- performance factor
- state factor
- deterministic RNG
- stage-two allocation
- soft caps
- decline
- peak tracking
- snapshots

## Archetypes

Test:

- multi-label classification
- configurable thresholds
- evidence output
- fallback behavior

## Match

Test:

- MatchContext
- lineups
- tactical fit
- XI quality
- team strength
- home advantage
- win probabilities
- xG
- score generation
- deterministic variance
- minutes
- goals
- assists
- defensive contributions
- player ratings
- trait effects

## Season

Test:

- match aggregation
- minutes
- appearances
- starts
- goals
- assists
- average rating
- performance factor
- playing-time factor

## Integration

Test:

```text
Match
↓
Season Performance
↓
Career Engine
↓
Development
```

---

# 119. BALANCE TESTING

Do not optimize a simulation from a single seed.

Use:

- hundreds of matches
- thousands of matches
- thousands of careers when practical
- distributions
- percentiles
- controlled experiments
- matched-player comparisons

Avoid fragile tests requiring exact random outputs unless testing determinism.

---

# 120. DEBUGGER REQUIREMENTS

A useful internal developer/debug view should eventually expose:

```text
career seed
current season
player
club
current position
role
CA
OVR
potential
development rate
profile
form
fitness
confidence
club strength
match importance
team strength
xG
minutes
match rating
season performance
development budget
peak data
```

---

# 121. PRESENTATION MODE

Target:

```text
1080 × 1920
9:16
```

Keyboard navigation can later support:

```text
SPACE → next scene
LEFT  → previous scene
RIGHT → next scene
ESC   → exit
```

---

# 122. NARRATIVE ENGINE FUTURE

Narrative should eventually identify:

- breakthroughs
- failures
- title wins
- major performances
- records
- transfers
- injuries
- rivalries
- comebacks
- retirement

Phase 5 may expose `narrative_importance` as structured metadata, but must not generate prose narrative.

---

# 123. CAREER ARC FUTURE

Possible future arcs:

```text
RISE_TO_GLORY
FALL_FROM_GRACE
REDEMPTION
WONDERKID
ONE_CLUB_LEGEND
JOURNEYMAN
MERCENARY
LATE_BLOOMER
TRAGEDY
GOAT
CULT_HERO
```

These are future narrative concepts, not Phase 5 simulation rules.

---

# 124. LEGACY FUTURE

At retirement, a future Legacy System may use:

```text
titles
goals
assists
appearances
individual_awards
international_career
records
longevity
club_impact
narrative_significance
```

---

# 125. STORY GENERATION FUTURE

Target final story duration:

```text
5–6 minutes
```

Possible structure:

```text
HOOK
ORIGIN
RISE
BREAKTHROUGH
TURNING_POINT
PRIME
CRISIS
COMEBACK
ENDING
LEGACY
CTA
```

---

# 126. UI PHILOSOPHY

Target aesthetic:

> Football Manager × modern sports analytics × premium sports editorial design.

Avoid:

- generic admin dashboard
- spreadsheet-heavy UI
- excessive neon
- rainbow gradients
- cheap gaming aesthetics
- excessive glassmorphism

---

# 127. VISUAL LANGUAGE

Default:

```text
Dark
```

Suggested palette:

```text
Background: #08090B
Surface:    #111318
Elevated:   #181B21
Border:     #272B33
Text:       #F5F5F5
Secondary:  #8E949F
```

Accent:

```text
muted football green / lime
```

---

# 128. TESTING DEFINITION OF DONE

A feature is complete only when:

```text
Code exists
+
Tests exist
+
Application runs
+
Feature works
+
No obvious regression
```

For simulation systems:

```text
Feature works
+
Repeated simulations produce believable distributions
+
Deterministic reproduction works
```

---

# 129. PHASE 1 ACCEPTANCE TEST

```text
Angular starts
+
FastAPI starts
+
SQLite works
+
SQLAlchemy works
+
Alembic works
+
/health works
+
Angular communicates with FastAPI
+
Tests pass
```

---

# 130. PHASE 2 ACCEPTANCE TEST

```text
World Seed
 ↓
Countries
 ↓
Leagues
 ↓
Clubs
 ↓
Managers
 ↓
Competitions
 ↓
Players
 ↓
ClubMemberships
 ↓
Club Ratings
 ↓
League Ratings
```

World seed must be reproducible.

---

# 131. PHASE 3 ACCEPTANCE TEST

```text
Create Player
 ↓
Generate Internal Attributes
 ↓
Generate visible groups
 ↓
Calculate MENTAL
 ↓
Calculate Current Ability
 ↓
Calculate Position OVR
 ↓
Assign Potential
 ↓
Assign Development Rate
 ↓
Assign Development Profile
 ↓
Generate Role Familiarity
 ↓
Calculate Role Effectiveness
 ↓
Assign Traits
 ↓
Generate Personality
 ↓
Initialize Player State
 ↓
Persist Player
```

---

# 132. PHASE 3.1 ACCEPTANCE TEST

The generated world must contain:

- multiple player archetypes
- positional specialization
- secondary positions
- variable trait counts
- realistic potential distribution
- dedicated GK OVR
- meaningful intra-club variance
- deterministic outputs

---

# 133. PHASE 4 ACCEPTANCE TEST

```text
Create Career
 ↓
Initialize Season
 ↓
Calculate Development Budget
 ↓
Allocate by profile
 ↓
Modify internal attributes
 ↓
Recalculate CA
 ↓
Recalculate OVR
 ↓
Update age
 ↓
Update Career Phase
 ↓
Track peak
 ↓
Create Snapshot
 ↓
Advance season
```

---

# 134. PHASE 4.1B ACCEPTANCE TEST

The classifier must:

- support multiple tags
- produce evidence
- use configurable thresholds
- leave simulation unchanged
- provide useful fallback behavior

---

# 135. PHASE 5 ACCEPTANCE TEST

The full match loop must eventually support:

```text
Player + Club + Opponent + Context
 ↓
Lineup
 ↓
Team Strength
 ↓
Match Resolution
 ↓
Player Performance
 ↓
Minutes / Goals / Assists / Rating
 ↓
Season Aggregation
 ↓
Performance Factor
 ↓
Playing Time Factor
 ↓
Career Engine
 ↓
Development
 ↓
Next Season
```

---

# 136. PHASE 5 BALANCE TARGETS

Phase 5 is not expected to reproduce real-world football exactly.

It should instead produce broadly plausible distributions for:

- goals per match
- home advantage
- draws
- scorelines
- xG
- shots
- player ratings
- minutes
- goals per player
- assists per player
- clean sheets
- upset rate

The exact targets should be defined through statistical audits after implementation.

---

# 137. MATCH ENGINE DESIGN PRINCIPLES

1. Strong teams are favored, not guaranteed.
2. OVR matters, but does not determine everything.
3. Role Effectiveness matters.
4. Form and Fitness matter.
5. Traits create contextual behavior.
6. Match variance creates surprises.
7. Player rating emerges from performance.
8. Minutes are generated by selection and substitutions.
9. Season Performance emerges from matches.
10. Career Engine consumes aggregated seasonal inputs.
11. Match Engine never directly modifies Career development.
12. Deterministic randomness is mandatory.

---

# 138. MATCH ENGINE PHASE ORDER

The recommended order is:

```text
5A Match Domain
 ↓
5B Lineup + Team Strength
 ↓
5C Match Resolution
 ↓
5D Player Performance
 ↓
5E Season Aggregation
 ↓
5F Career Integration
```

Each stage must be independently testable.

---

# 139. PERSISTENCE RULES FOR MATCHES

Do not store every simulated micro-action unless required.

Prefer storing:

```text
Match
PlayerMatchPerformance
SeasonPerformance
```

over every individual possession/chance object.

Use structured event storage only where it adds future narrative/debugging value.

---

# 140. CAREER SIMULATION BALANCE

When enough systems exist, run large samples and collect:

```text
average_peak_overall
average_final_overall
average_career_length
average_transfers
average_injuries
average_goals
average_assists
average_trophies
average_market_value
average_retirement_age
percentage_reaching_potential
percentage_winning_major_titles
percentage_late_bloomers
percentage_failed_wonderkids
percentage_long_primes
```

Analyze distributions, not only averages.

---

# 141. JULES IMPLEMENTATION RULE

Before implementing any phase:

1. Read `PROJECT_SPEC.md`.
2. Read `.github/instructions/reglas.instructions.md`.
3. Read `AGENTS.md`.
4. Inspect current repository state.
5. Produce an implementation plan for major phase work.
6. Wait for approval when requested.
7. Implement only approved scope.
8. Run tests.
9. Run regression tests.
10. Verify deterministic behavior.
11. Report results.
12. Stop.

Do not continue automatically to a future phase.

---

# 142. JULES PULL REQUEST DISCIPLINE

Each major phase or architectural refactor should use its own branch and pull request.

A PR must contain:

- only requested scope
- required tests
- required migrations
- required configuration
- no unrelated refactors
- no future-phase implementation

---

# 143. DOCUMENTATION RULE

Update documentation when:

- architecture changes
- API contracts change
- a major phase is completed
- important simulation rules change

Do not silently rewrite the specification during implementation.

---

# 144. FINAL PRODUCT STRATEGY

TikTok is initially the distribution channel.

Football Life is the underlying simulation product.

The simulator should remain useful independently of social media.

---

# 145. FINAL PRODUCT VISION

The complete long-term loop:

```text
PLAYER
   ↓
CAREER
   ↓
MATCHES
   ↓
STORY
   ↓
VIDEO
   ↓
AUDIENCE
   ↓
COMMENTS
   ↓
COMMUNITY DECISIONS
   ↓
NEW CAREER
```

The current core loop is:

```text
PLAYER
   ↓
CAREER
   ↓
MATCHES
   ↓
PERFORMANCE
   ↓
DEVELOPMENT
```

---

# 146. FINAL DESIGN PRINCIPLE

Football Life should always answer:

> **Would someone watch the entire 5–6 minute career because they genuinely want to know how it ends?**

The simulator must target:

```text
BELIEVABLE
     +
UNPREDICTABLE
     +
EMOTIONAL
     +
DYNAMIC WORLD
     +
MEANINGFUL PLAYER EVOLUTION
     +
MEANINGFUL MATCH PERFORMANCE
     +
VISUALLY ATTRACTIVE
     =
FOOTBALL LIFE
```

The simulation must not become:

```text
statistically accurate but boring
```

nor:

```text
chaotic but implausible
```

The goal is believable unpredictability that naturally creates stories.
