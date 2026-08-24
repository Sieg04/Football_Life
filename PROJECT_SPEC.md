# FOOTBALL LIFE
## Complete Project Specification

**Version:** 1.4  
**Project:** Football Life  
**Type:** Local football career simulator + narrative/story generator  
**Primary platform:** Desktop/local web application  
**Development assistant:** Jules  
**Initial objective:** Generate fictional football careers that can be presented as engaging 5–6 minute vertical TikTok videos.

---

# 1. PROJECT VISION

Football Life is a local football career simulator designed primarily as a **story-generation engine**.

The objective is not to reproduce Football Manager in miniature.

The objective is to generate:

- believable football careers
- unpredictable outcomes
- career variety
- important turning points
- emotional moments
- failures
- successes
- comebacks
- rivalries
- unexpected transfers
- memorable endings

A complete career should eventually be presentable as a single approximately **5–6 minute video**.

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
23 — ACL injury
25 — Career decline
28 — Comeback
30 — Champions League
34 — Retirement
```

is more valuable than an extremely detailed simulation that produces boring results.

---

## 2.2 Every career should be different

Two players with similar starting conditions should not necessarily experience the same career.

Variation should come from:

- Player attributes
- Potential
- Development Rate
- Development Profile
- Personality
- Club context
- Manager
- Playing time
- Form
- Injuries
- Transfers
- Relationships
- Randomness
- World evolution
- Decisions

---

## 2.3 Failure must be possible

The simulation must allow:

- Poor careers
- Injuries
- Failed wonderkids
- Bad transfers
- Early decline
- Long periods on the bench
- Journeyman careers
- Players who never reach potential
- Clubs that decline
- Clubs that unexpectedly become dominant

The game should not optimize every player toward becoming a superstar.

---

## 2.4 Randomness must create uncertainty, not nonsense

Random events should stay within plausible football contexts.

Bad:

```text
16-year-old player from a tiny amateur club
↓
Randomly transferred to Real Madrid
```

Better:

```text
Academy player
↓
Excellent youth performances
↓
Scouting attention
↓
Professional debut
↓
Breakthrough
↓
Major clubs become interested
↓
Transfer opportunity
```

---

## 2.5 Presentation is part of the product

The application must eventually look good enough that its UI can be directly recorded for social media.

The interface should not feel like a generic admin panel.

---

# 3. MAIN USE CASE

The initial user is the creator of a football/TikTok account.

Typical workflow:

```text
Create player
      ↓
Start career
      ↓
Simulate complete career
      ↓
Review timeline
      ↓
Review statistics
      ↓
Review key events
      ↓
Generate story
      ↓
Open presentation mode
      ↓
Record video
      ↓
Edit externally
      ↓
Publish
```

---

# 4. FUTURE COMMUNITY CONCEPT

The first version does NOT include community interaction.

The long-term concept is:

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

Future community features may allow followers to influence:

- Club selection
- Transfer decisions
- Contract decisions
- Career choices
- Personal decisions
- Rivalries
- Other important events

The architecture must support this later.

---

# 5. MVP GOALS

The MVP must eventually allow the user to:

1. Create a fictional player.
2. Select nationality.
3. Select position.
4. Select starting club.
5. Generate player attributes.
6. Generate personality.
7. Start a career.
8. Simulate seasons.
9. Simulate matches.
10. Track performance.
11. Develop attributes.
12. Experience injuries.
13. Receive transfers.
14. Sign contracts.
15. Play international football.
16. Experience important events.
17. Track relationships.
18. Win trophies.
19. Win individual awards.
20. Retire.
21. Calculate legacy.
22. Identify career archetype.
23. Generate a complete career timeline.
24. Generate a 5–6 minute story.
25. Present the story visually.
26. Enter vertical 9:16 presentation mode.

---

# 6. EXPLICIT NON-GOALS FOR MVP

Do NOT implement initially:

- User accounts
- Authentication
- Cloud deployment
- Public API
- TikTok API
- TikTok comment scraping
- Community voting
- Multiplayer
- Public career pages
- Mobile application
- 3D matches
- Tactical match simulation
- Complete real-world player database
- Full real-world squad database
- Complex accounting/finances
- Complex agent negotiations
- Mandatory LLM integration
- Automatic video generation

These may be developed later.

---

# 7. DEVELOPMENT PHILOSOPHY

## CRITICAL RULE

> **DO NOT BUILD THE ENTIRE SYSTEM IN ONE PASS.**

Football Life must be developed incrementally.

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

- Repository
- Documentation
- Architecture review
- Development rules

No gameplay implementation.

---

## Phase 1 — Foundation

Implement:

- FastAPI
- Angular
- SQLite
- SQLAlchemy
- Alembic
- Configuration
- Health endpoint
- Basic API shell
- Basic Angular shell
- Angular → FastAPI communication
- Basic tests

No football simulation.

---

## Phase 2 — Football World

Implement:

- Countries
- Leagues
- Clubs
- Managers
- Competitions
- External source metadata
- Club attributes
- League attributes
- Club strength
- League strength
- Initial world seed
- Generic squad generation
- Shared Player domain refactor
- ClubMembership
- Initial world tests

Do NOT implement:

- Player development
- Match engine
- Transfers
- Injuries
- Narrative engine

---

## Phase 3 — Player Engine

Implement:

- Player internal attribute system
- PAC / SHO / PAS / DRI / DEF / PHY
- MENTAL group
- Current Ability
- Position-specific OVR
- Potential
- Development Rate
- Development Profiles
- Role Familiarity
- Role Attribute Fit
- Role Effectiveness
- Traits / PlayStyles
- Personality data
- Player State
- Aging baseline
- Deterministic player generation
- Player attribute generation
- Player validation
- Player persistence

Do NOT implement yet:

- Full career progression
- Seasonal development loop
- Transfers
- Contracts
- Injuries
- Relationships
- Match engine
- Narrative
- Community
- TikTok presentation

---

## Phase 3.1 — Player Generation & Balance Refinement

Implement:

- Position-based archetypes
- Squad distribution
- Positional attribute specialization
- Secondary positions
- Expanded role coverage
- Variable trait counts
- Trait compatibility rules
- Improved potential distribution
- Goalkeeper-specific OVR
- Improved intra-club player variance
- Statistical seed validation

Phase 3.1 MUST preserve:

- Player Engine formulas
- Current Ability calculation
- OVR formulas
- Role Effectiveness formula
- Deterministic generation

The main purpose is to improve player generation, not redesign the Player Engine.

---

## Phase 4 — Career Engine

Implement:

- Career entity
- Career initialization
- Season entity/state
- Season progression
- Development budget
- Seasonal development
- Attribute changes
- Current Ability recalculation
- OVR recalculation
- Age progression
- Career phase
- Peak ability tracking
- Seasonal snapshots
- End-of-season state
- Deterministic career simulation

Do NOT implement yet:

- Full Match Engine
- Transfers
- Contracts
- Injuries
- Relationships
- Narrative
- Community
- TikTok presentation

---

## Phase 5 — Match Engine

Implement:

- Match results
- Team strength
- Playing time
- Player performance
- Goals
- Assists
- Ratings
- Competition outcomes
- Match importance
- Role impact
- Traits contextual effects

---

## Phase 6 — Career Depth

Implement:

- Form
- Fatigue
- Fitness
- Confidence
- Morale
- Injuries
- Relationships
- Manager interaction
- Dynamic role changes
- Position conversion
- Deeper seasonal state

---

## Phase 7 — Transfer Engine

Implement:

- Market value
- Club needs
- Transfer offers
- Contracts
- Transfer windows
- Club attractiveness
- Player fit
- Transfer decisions

---

## Phase 8 — Event Engine

Implement:

- Data-driven events
- Conditions
- Probabilities
- Effects
- Decisions
- Automatic resolution

---

## Phase 9 — Narrative Engine

Implement:

- Timeline
- Narrative importance
- Career arcs
- Legacy score
- Story beats
- Story generation

---

## Phase 10 — Frontend

Implement:

- Home
- Player creation
- Career dashboard
- Season view
- Event view
- Timeline
- Statistics
- Transfers
- Retirement
- Story screen

---

## Phase 11 — Visual Polish

Implement:

- Dark theme
- Typography
- Animations
- Player cards
- Trophy presentation
- Timeline animations
- Microinteractions
- Visual hierarchy

---

## Phase 12 — TikTok Presentation Mode

Implement:

- 9:16 layout
- 1080 × 1920 target
- Scene system
- Keyboard navigation
- Recording-friendly presentation
- Story progression

---

## Phase 13 — Simulation Balance

Run hundreds or thousands of careers.

Analyze:

- Career length
- Peak overall
- Final overall
- Transfers
- Injuries
- Goals
- Trophies
- Retirement age
- Potential attainment
- Major titles
- Narrative-event frequency
- Late bloomers
- One-club legends
- Career failures

Tune the simulation.

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

## Charts

Preferred:

```text
ApexCharts
```

Use another lightweight Angular-compatible chart library only if justified.

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

Preferred dependency direction:

```text
Frontend
    ↓
API
    ↓
Application Services
    ↓
Simulation Engine
    ↓
Simulation Result
    ↓
Application Services
    ↓
Persistence
```

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
- Frontend components

It should eventually be possible to execute the simulation directly from Python.

Conceptually:

```python
result = simulation_engine.simulate(
    career_state=career_state,
    world_state=world_state,
    rules=rules,
    seed=seed
)
```

The engine returns structured domain results.

It does not save directly to the database.

---

# 12. DETERMINISTIC RANDOMNESS

Every career must have a seed.

Example:

```text
FL-8F92-A21C
```

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

Use a centralized deterministic RNG abstraction.

Avoid uncontrolled calls to global random functions.

The seed system must support:

- Reproducing careers
- Debugging
- Snapshot recovery
- Balance testing
- Future community branching

---

# 13. DATA-DRIVEN RULES

Game rules should be configurable.

Suggested structure:

```text
backend/data/
├── rules/
│   ├── world.json
│   ├── player_attributes.json
│   ├── player_development.json
│   ├── player_roles.json
│   ├── player_traits.json
│   ├── player_archetypes.json
│   ├── career.json
│   ├── matches.json
│   ├── transfers.json
│   ├── injuries.json
│   └── narrative.json
│
└── events/
    ├── sport.json
    ├── transfers.json
    ├── injuries.json
    ├── media.json
    ├── relationships.json
    ├── personal.json
    └── chaos.json
```

Do not hardcode large collections of:

- Event definitions
- Attribute weights
- Position weights
- Role weights
- Development coefficients
- Probabilities
- Injury probabilities
- Transfer conditions
- Trait definitions
- Career development coefficients

inside Python business logic.

Do not over-engineer configuration systems before they are required.

---

# 14. FOOTBALL WORLD

Football World represents the environment in which careers take place.

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

The same `Player` domain is used for:

- Generic squad players
- Future career protagonists

A protagonist should not use a separate football-player model.

---

# 15. EXTERNAL DATA PHILOSOPHY

External rankings should be used as **initial references**, not immutable truths.

Recommended sources:

```text
Opta  → current club/league strength
UEFA  → European club coefficients
IFFHS → historical league strength
FIFA  → national team strength
Manual/generated → prestige, academy, facilities, finances
```

The external data creates the initial world.

After the simulation begins:

> **Internal simulation rules become the source of truth.**

---

# 16. DATA SOURCE METADATA

Important external values should retain:

```text
data_source
source_date
source_name
source_value
normalized_value
```

Potential source identifiers:

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

Each club should contain:

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

All internal values use 0–100 except:

```text
momentum: -100 → +100
```

and raw external coefficients.

---

# 18. CLUB RATING PRINCIPLE

Separate:

```text
Current Strength
```

from:

```text
Prestige
```

A club can have:

```text
Prestige = 99
Strength = 84
```

This is valid.

Historical importance should not automatically imply current sporting superiority.

---

# 19. CLUB CURRENT STRENGTH

Current strength represents how strong the first team is now.

Main components:

```text
Attack
Midfield
Defense
Goalkeeper
Squad Depth
Manager Quality
Facilities
Momentum
```

Formula:

```text
CURRENT_STRENGTH =
    SQUAD_BASE           × 0.75
  + MANAGER_QUALITY      × 0.05
  + SQUAD_DEPTH          × 0.10
  + FACILITIES           × 0.03
  + MOMENTUM_NORMALIZED  × 0.07
```

Clamp to:

```text
1–100
```

Prestige does NOT directly enter Current Strength.

---

# 20. CLUB SQUAD LINES

```text
Attack
Midfield
Defense
Goalkeeper
```

### Attack

```text
ATTACK =
weighted_average(
    forwards,
    wingers,
    attacking_midfielders
)
```

### Midfield

```text
MIDFIELD =
weighted_average(
    central_midfielders,
    defensive_midfielders,
    attacking_midfielders
)
```

### Defense

```text
DEFENSE =
weighted_average(
    center_backs,
    full_backs
)
```

### Goalkeeper

Goalkeepers use dedicated goalkeeper attributes.

---

# 21. PLAYER ROLE WEIGHTS FOR CLUB SQUADS

Current suggested values:

```text
STARTER   = 1.00
ROTATION  = 0.65
BACKUP    = 0.35
YOUTH     = 0.15
```

These values are configurable.

Example:

```text
ATTACK =
Σ(player_current_ability × role_weight)
/
Σ(role_weight)
```

The Player model does not own the squad role.

The role belongs to `ClubMembership`.

---

# 22. SQUAD BASE

Suggested:

```text
SQUAD_BASE =
    ATTACK     × 0.30
  + MIDFIELD  × 0.28
  + DEFENSE   × 0.27
  + GK        × 0.15
```

---

# 23. SQUAD DEPTH

Suggested:

```text
SQUAD_DEPTH =
    second_unit_strength × 0.60
  + third_unit_strength  × 0.25
  + positional_coverage  × 0.15
```

Normalize:

```text
0–100
```

---

# 24. GENERIC SQUAD GENERATION

The world initially contains generic players.

They are real `Player` domain objects.

Generation flow:

```text
Club target strength
        ↓
Squad distribution
        ↓
Primary position
        ↓
Player archetype
        ↓
Internal attributes
        ↓
Current Ability
        ↓
Potential
        ↓
Development Profile
        ↓
ClubMembership
```

Generic players may initially have limited identity/narrative information.

They must nevertheless share the same fundamental football-player model as the future protagonist.

---

# 25. PLAYER GENERATION AND CLUB DISTRIBUTION

Generic players should NOT simply be generated as:

```text
club_strength ± small_random_number
```

Instead, the club strength defines a **distribution target**.

A generated squad should contain:

- elite starters where appropriate
- strong rotation players
- competent backups
- lower-rated youth
- meaningful player-level variance

Strong clubs should generally have stronger squads.

However:

- weaker clubs may occasionally produce an exceptional player
- strong clubs may contain weaker squad members
- one player should not determine the entire club rating

---

# 26. POSITIONAL ARCHETYPES

Player generation must use position-specific archetypes.

Examples:

### ST FINISHER

```text
SHO high
PAC high
DRI high
PHY moderate/high
PAS moderate
DEF low
```

### ST TARGET

```text
SHO high
PHY very high
PAS moderate
DRI moderate
PAC lower
DEF low
```

### CM PLAYMAKER

```text
PAS very high
MENTAL very high
DRI high
SHO moderate
DEF moderate
PAC moderate
PHY moderate
```

### CB BALL PLAYING

```text
DEF very high
PHY high
PAS high
PAC moderate
DRI lower
SHO low
```

Archetypes must be configurable in:

```text
player_archetypes.json
```

---

# 27. PLAYER SECONDARY POSITIONS

Target approximate initial distribution:

```text
0 secondary positions → 45%
1 secondary position  → 40%
2 secondary positions → 15%
```

Secondary positions must respect compatibility rules.

Examples:

```text
LW ↔ RW
CM ↔ CAM
CM ↔ DM
CB ↔ DM
LB ↔ LWB
RB ↔ RWB
```

Do not generate implausible position conversions during initial world generation.

---

# 28. CLUB PRESTIGE

Prestige represents:

> How important and historically significant a club is.

Suggested formula:

```text
PRESTIGE =
    historical_success      × 0.35
  + european_history        × 0.25
  + domestic_history        × 0.15
  + global_reputation       × 0.15
  + fanbase                 × 0.10
```

All values normalized to 0–100.

---

# 29. PRESTIGE EVOLUTION

Prestige changes slowly.

Suggested impacts:

```text
Champions League title   +2.0
League title             +0.7
European final           +1.0
Major domestic cup       +0.4
Major relegation         -1.5
```

Values are configurable starting points.

Then:

```text
new_prestige =
old_prestige + seasonal_change
```

Clamp:

```text
0–100
```

Prestige should change over years rather than individual matches.

---

# 30. FINANCIAL POWER

Financial power represents a club's ability to spend.

Suggested model:

```text
FINANCIAL_POWER =
    revenue              × 0.35
  + ownership_capacity   × 0.20
  + league_money         × 0.20
  + european_income      × 0.15
  + commercial_power     × 0.10
```

All values:

```text
0–100
```

This is not a full accounting simulator.

---

# 31. FINANCIAL EVOLUTION

Conceptual seasonal change:

```text
financial_change =
    league_income
  + european_income
  + player_sales
  + sponsorship_growth
  - transfer_spending
  - wage_burden
  - poor_results_penalty
```

This belongs to later world simulation phases.

---

# 32. ACADEMY QUALITY

Suggested:

```text
ACADEMY_QUALITY =
    academy_reputation   × 0.40
  + facilities           × 0.25
  + youth_investment     × 0.20
  + country_youth_factor × 0.15
```

---

# 33. ACADEMY AS TALENT DISTRIBUTION

Academy quality changes the probability distribution of generated youth players.

It does NOT directly determine an exact player rating.

Exceptional RNG outcomes remain possible at smaller clubs.

---

# 34. FACILITIES

Suggested:

```text
FACILITIES =
    training_facilities × 0.60
  + medical_facilities  × 0.20
  + youth_facilities    × 0.20
```

Development modifier:

```text
development_modifier =
1 + ((facilities - 50) / 500)
```

Therefore:

```text
Facilities 100 → ×1.10
Facilities 50  → ×1.00
Facilities 0   → ×0.90
```

---

# 35. FAN PRESSURE

Suggested:

```text
FAN_PRESSURE =
    club_size       × 0.35
  + prestige        × 0.25
  + expectations    × 0.25
  + media_attention × 0.15
```

---

# 36. DOMESTIC REPUTATION

Suggested:

```text
DOMESTIC_REPUTATION =
    domestic_titles  × 0.40
  + league_success   × 0.30
  + fanbase          × 0.15
  + domestic_media  × 0.15
```

---

# 37. INTERNATIONAL REPUTATION

Suggested:

```text
INTERNATIONAL_REPUTATION =
    uefa_coefficient_normalized × 0.40
  + european_titles             × 0.25
  + european_appearances        × 0.15
  + global_reputation           × 0.20
```

---

# 38. UEFA COEFFICIENT

Store:

```text
uefa_coefficient_raw
uefa_coefficient_normalized
```

Normalization:

```text
UEFA_NORMALIZED =
100 ×
(
    club_uefa - dataset_min
)
/
(
    dataset_max - dataset_min
)
```

Clamp:

```text
0–100
```

---

# 39. CLUB MOMENTUM

Momentum represents current trajectory.

Scale:

```text
-100 → +100
```

Suggested formula:

```text
MOMENTUM =
    previous_momentum  × 0.55
  + result_momentum    × 0.25
  + trophy_momentum    × 0.10
  + transfer_momentum  × 0.05
  + financial_momentum × 0.05
```

Full momentum evolution belongs to later phases.

---

# 40. MOMENTUM NORMALIZATION

```text
MOMENTUM_NORMALIZED =
    (momentum + 100) / 2
```

Therefore:

```text
-100 → 0
0    → 50
+100 → 100
```

---

# 41. CLUB ATTRACTIVENESS

Suggested:

```text
CLUB_ATTRACTIVENESS =
    prestige                 × 0.30
  + current_strength         × 0.25
  + financial_power          × 0.15
  + league_strength          × 0.10
  + international_reputation × 0.10
  + facilities               × 0.05
  + momentum_normalized      × 0.05
```

Used later by the Transfer Engine.

---

# 42. LEAGUE SYSTEM

Each league contains:

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

---

# 43. LEAGUE STRENGTH

Suggested:

```text
LEAGUE_STRENGTH =
    top_4_average        × 0.35
  + top_8_average        × 0.25
  + middle_average       × 0.20
  + bottom_average       × 0.10
  + european_performance × 0.10
```

---

# 44. LEAGUE EVOLUTION

Each season:

```text
new_league_strength =
    current_strength × 0.70
  + newly_calculated_strength × 0.30
```

This belongs to future world simulation.

---

# 45. LEAGUE PRESTIGE

```text
LEAGUE_PRESTIGE =
    historical_success        × 0.30
  + european_success          × 0.25
  + star_power                × 0.15
  + domestic_competitiveness  × 0.15
  + global_attention          × 0.15
```

---

# 46. LEAGUE FINANCIAL STRENGTH

```text
LEAGUE_FINANCIAL_STRENGTH =
    broadcast_revenue × 0.35
  + club_finances     × 0.30
  + sponsorship       × 0.20
  + attendance        × 0.15
```

---

# 47. LEAGUE GLOBAL REPUTATION

```text
GLOBAL_REPUTATION =
    league_prestige        × 0.35
  + international_success  × 0.25
  + star_players           × 0.20
  + media_attention        × 0.20
```

---

# 48. COUNTRY / NATIONAL TEAM SYSTEM

Each country may contain:

```text
id
name
fifa_rank
fifa_points
national_strength
```

---

# 49. NATIONAL TEAM STRENGTH

FIFA data is the initial reference.

Conceptually:

```text
normalized_points =
(
    points - min_points
)
/
(
    max_points - min_points
)
```

Possible transformed model:

```text
national_strength =
100 × sqrt(normalized_points)
```

Then:

```text
clamp(0,100)
```

The exact transformation should remain configurable.

---

# 50. NATIONAL TEAM EVOLUTION

After international matches:

```text
new_strength =
old_strength × 0.90
+
performance_rating × 0.10
```

Major competition multipliers:

```text
World Cup             1.50
European Championship 1.30
Continental Cup       1.20
Friendly              0.30
```

---

# 51. MANAGER SYSTEM

Managers contain:

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

---

# 52. MANAGER QUALITY

```text
MANAGER_QUALITY =
    tactical_quality   × 0.30
  + player_development × 0.25
  + game_management    × 0.20
  + rotation           × 0.10
  + adaptability       × 0.15
```

---

# 53. COMPETITION SYSTEM

Each competition:

```text
id
name
type
country
tier
prestige
strength
```

Types:

```text
LEAGUE
DOMESTIC_CUP
EUROPEAN
INTERNATIONAL
```

---

# 54. COMPETITION PRESTIGE

Suggested:

```text
Champions League       100
Europa League           78
Conference League       62
Major domestic cup      75
League title            80
```

---

# 55. PLAYER DOMAIN — OVERVIEW

Football Life uses a single shared `Player` domain for:

- Generic squad players
- Career protagonists

A Player is the football identity.

A Career is the professional history.

Preferred:

```text
Player
   ↓
ClubMembership
   ↓
Club

Player
   ↓
Career
```

---

# 56. PLAYER IDENTITY

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

# 57. INTERNAL PLAYER ATTRIBUTES

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
dribbling
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

All internal attributes:

```text
1–100
```

---

# 58. TOP-LEVEL GROUPS

Visible groups:

```text
PAC
SHO
PAS
DRI
DEF
PHY
```

Internal:

```text
MENTAL
```

The visible groups are derived from internal attributes.

---

# 59. MENTAL

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

# 60. CURRENT ABILITY

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

Clamp:

```text
1–100
```

Do not introduce weakness penalties during Phase 3/3.1 unless explicitly approved.

---

# 61. POSITION-SPECIFIC OVR

Current Ability and OVR are separate.

Example:

```text
Current Ability = 84

ST OVR  = 87
CAM OVR = 83
CM OVR  = 76
```

Starting weights:

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

# 62. GOALKEEPER ATTRIBUTES

Goalkeepers:

```text
diving
handling
kicking
reflexes
speed
goalkeeper_positioning
```

GK uses a dedicated OVR formula.

At this stage, goalkeeper behavior is not yet part of the Match Engine.

---

# 63. PLAYER ARCHETYPES

Archetypes are configurable.

Examples:

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

Archetype affects initial attribute distributions.

Archetype is descriptive generation metadata.

It is not a career behavior system.

---

# 64. ROLE SYSTEM

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

# 65. ROLE ATTRIBUTE FIT

```text
ATTRIBUTE_FIT =
Σ(attribute_group × role_weight)
```

---

# 66. ROLE FAMILIARITY

Range:

```text
0–100
```

Initial target:

```text
Primary role      80–95
Secondary role    55–80
Unnatural role    20–50
```

Role familiarity does not alter base attributes.

---

# 67. ROLE EFFECTIVENESS

```text
ROLE_EFFECTIVENESS =
    ATTRIBUTE_FIT    × 0.70
  + ROLE_FAMILIARITY × 0.30
```

Do not multiply OVR directly by familiarity.

---

# 68. TRAITS / PLAYSTYLES

Phase 3/3.1 stores traits as configurable IDs.

Examples:

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

Traits should be compatible with player attributes where practical.

No match effects yet.

---

# 69. PERSONALITY

```text
ambition
loyalty
professionalism
ego
temper
leadership
sociability
```

Range:

```text
0–100
```

Phase 3 defines and persists personality data.

Behavioral consequences belong to later phases.

---

# 70. POTENTIAL

Rule:

```text
potential >= current_ability
```

Potential is a theoretical ceiling, not a guarantee.

The distribution must contain:

- low-ceiling players
- normal professionals
- strong prospects
- high-potential players
- rare wonderkids
- extremely rare generational talents

Potential 95+ must be rare.

Potential 100 must be exceptional.

---

# 71. DEVELOPMENT RATE

Range:

```text
0–100
```

Interpretation:

```text
0–30    Very slow
31–50   Slow
51–70   Normal
71–85   Fast
86–100  Exceptional
```

Development Rate is predisposition, not annual growth.

---

# 72. DEVELOPMENT PROFILES

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

Profiles modify development distribution.

Example:

### FINISHER

```text
PAC 1.05
SHO 1.30
PAS 1.00
DRI 1.10
DEF 0.90
PHY 1.00
MENTAL 1.05
```

### PLAYMAKER

```text
PAC 0.95
SHO 0.95
PAS 1.30
DRI 1.15
DEF 0.95
PHY 0.90
MENTAL 1.25
```

### ATHLETIC

```text
PAC 1.30
SHO 1.00
PAS 0.95
DRI 1.10
DEF 1.00
PHY 1.30
MENTAL 0.95
```

### DEFENSIVE

```text
PAC 1.00
SHO 0.85
PAS 1.00
DRI 0.90
DEF 1.30
PHY 1.20
MENTAL 1.10
```

### LATE_BLOOMER

Primarily modifies the timing/age curve rather than directly adding permanent attribute bonuses.

---

# 73. PLAYER STATE

Dynamic state:

```text
confidence
morale
form
fitness
fatigue
happiness
reputation
```

Range:

```text
0–100
```

Phase 3 initializes and validates it.

Later phases evolve it.

---

# 74. CLUB MEMBERSHIP

```text
ClubMembership
├── player_id
├── club_id
├── role
├── start_date
└── end_date
```

Role belongs to membership.

Player identity survives transfers.

---

# 75. CAREER DOMAIN

A Career contains the professional history of a Player.

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

Phase 4 implements only the initial Career and Season concepts.

---

# 76. PHASE 4 CAREER OBJECTIVE

Phase 4 transforms the static Player into a progressing football career.

The central loop is:

```text
Career
   ↓
Season Start
   ↓
Season State
   ↓
Development
   ↓
Season End
   ↓
Snapshot
   ↓
Next Season
```

The Match Engine does not yet exist in Phase 4.

Therefore performance must initially be represented by an abstract/configurable seasonal input rather than simulated matches.

---

# 77. PHASE 4 SEASON FLOW

Each season:

```text
Season initialization
        ↓
Age
        ↓
Career phase
        ↓
Club context
        ↓
Manager context
        ↓
Training environment
        ↓
Playing-time context
        ↓
Performance context
        ↓
Development calculation
        ↓
Attribute changes
        ↓
Current Ability recalculation
        ↓
OVR recalculation
        ↓
Player state update
        ↓
Peak tracking
        ↓
Season snapshot
        ↓
Next season
```

Do not implement transfers, injuries or matches yet.

---

# 78. DEVELOPMENT BUDGET

The central output of the yearly development system is:

```text
DEVELOPMENT_BUDGET
```

It represents:

> How much development opportunity the player receives during that season.

It is NOT directly equal to OVR growth.

Conceptual formula:

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

All major coefficients must be configurable.

---

# 79. BASE DEVELOPMENT RATE

The base development rate is configuration-driven.

A recommended initial abstraction:

```text
BASE_RATE = small seasonal budget
```

The exact numeric value must be tuned through balance testing.

Do not hardcode arbitrary OVR increases.

---

# 80. POTENTIAL FACTOR

Based on:

```text
potential_gap =
potential - current_ability
```

The potential factor must:

- be high when meaningful room exists
- decrease as current ability approaches potential
- reach approximately zero at the potential ceiling

The exact curve should be configurable.

A simple starting model:

```text
potential_factor =
clamp(
    potential_gap / max_gap,
    0,
    1
)
```

Use a smoothing function if required during balance testing.

---

# 81. AGE FACTOR

Starting baseline:

```text
16–18 → 1.40
19–21 → 1.25
22–24 → 1.10
25–27 → 0.85
28–30 → 0.60
31–33 → 0.35
34+   → 0.10
```

These values represent development opportunity.

They are not annual OVR changes.

---

# 82. PLAYING TIME FACTOR

Initial configurable baseline:

```text
0–300 minutes       → 0.30
301–750             → 0.55
751–1400            → 0.80
1401–2200           → 1.00
2201–3000           → 1.05
3000+               → 1.00
```

The purpose is to reward meaningful playing time without producing runaway growth from excessive minutes.

The full fatigue system belongs to later phases.

---

# 83. ENVIRONMENT FACTOR

Environment represents:

- Club facilities
- Training environment
- Manager development quality

A future baseline may use:

```text
environment_factor =
normalized combination of:
facilities
manager.player_development
```

Keep the modifier relatively small.

Environment should matter without determining a player's destiny.

---

# 84. PROFESSIONALISM FACTOR

Professionalism comes from Personality.

Use a small modifier rather than a huge multiplier.

Initial conceptual range:

```text
Low professionalism     → ~0.92
Average professionalism → ~1.00
High professionalism    → ~1.08
```

Do not let Personality dominate development.

---

# 85. PERFORMANCE FACTOR

Phase 4 does not have a Match Engine.

Therefore performance must initially be represented by an abstract seasonal performance input or neutral baseline.

The architecture must allow Phase 5 to replace this with actual match-derived performance.

Possible future input:

```text
season_rating
minutes
position_context
team_context
```

Do NOT implement the Match Engine inside Phase 4.

---

# 86. PLAYER STATE FACTOR

Player State may later influence development through:

- Confidence
- Morale
- Fitness
- Fatigue
- Happiness

Phase 4 should use only a simple configurable aggregate.

Do not build complex state evolution before Phase 6.

---

# 87. RANDOM FACTOR

Use deterministic RNG.

Initial range:

```text
0.85–1.15
```

The same seed must always produce the same outcome.

Randomness should create variation, not invalidate the broader career logic.

---

# 88. DEVELOPMENT PROFILE DISTRIBUTION

The Development Profile determines how the annual development budget is allocated.

Example:

```text
development_budget = 1.8
```

FINISHER might distribute it approximately toward:

```text
SHO
DRI
PAC
MENTAL
PHY
PAS
DEF
```

according to profile weights.

The result is a **budget distribution**, not fixed attribute increments.

---

# 89. ATTRIBUTE DISTRIBUTION

A development budget should be distributed across relevant attribute groups.

Example:

```text
1.8 budget
↓
SHO +0.8
DRI +0.4
PAC +0.3
MENTAL +0.2
PHY +0.1
```

The exact distribution is profile-driven and deterministic.

---

# 90. INTERNAL ATTRIBUTE DEVELOPMENT

Changing a visible group does not automatically add the same number to every internal attribute.

For example:

```text
SHO +0.8
```

may produce:

```text
finishing   +0.5
shot_power  +0.2
long_shots  +0.1
```

This preserves internal player identity.

The internal distribution is configuration-driven and may consider the player's existing strengths/weaknesses.

---

# 91. ATTRIBUTE SOFT CAPS

Attribute growth becomes increasingly difficult at very high values.

Initial conceptual multipliers:

```text
<80     ×1.00
80–89   ×0.85
90–94   ×0.60
95–97   ×0.30
98+     ×0.10
```

These are development resistance multipliers, not hard caps.

The goal is to make:

```text
98 → 99
```

meaningfully harder than:

```text
68 → 69
```

---

# 92. DECLINE

Decline should not simply subtract a fixed number from OVR every year.

As players age, decline should primarily affect vulnerable attributes.

Physical attributes should generally decline earlier:

```text
Pace
Acceleration
Agility
```

while many technical and mental attributes can remain stable longer:

```text
Passing
Vision
Composure
Decision Making
```

This allows natural player transformation.

Example:

```text
Age 27
RW
PAC 94
DRI 91

Age 34
CAM
PAC 76
DRI 90
PAS 88
MENTAL 92
```

The player has evolved rather than simply becoming worse.

---

# 93. DECLINE CURVE

Phase 4 should provide a decline function/configuration separate from the development curve.

A player's decline should generally become more important after their peak.

The exact curve must be configurable and tested statistically.

Do not force identical decline for every player.

---

# 94. CAREER PHASE

The player can have a derived career phase:

```text
YOUTH
EARLY_PRO
DEVELOPMENT
PRIME
LATE_PRIME
DECLINE
VETERAN
```

Career Phase is derived from:

- Age
- Current Ability
- Potential
- Development
- Career context

It is not simply an age label.

---

# 95. PEAK TRACKING

Career must track:

```text
peak_current_ability
peak_ovr
peak_age
peak_position
peak_club
```

Whenever the player reaches a new high:

```text
new_peak
```

should be stored.

This will later support narrative generation.

---

# 96. SEASON SNAPSHOT

Each completed season should produce a structured snapshot.

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

Snapshot should preserve enough information for:

- Debugging
- Career replay
- Narrative
- Balance analysis
- Future community branching

---

# 97. CAREER INITIALIZATION

Starting a career must establish:

```text
Player
↓
Starting Club
↓
Starting ClubMembership
↓
Starting Age
↓
Initial Season
↓
Initial Career Phase
↓
Initial Snapshot
```

The career should inherit the player's existing world seed and deterministic state.

---

# 98. CAREER SIMULATION DETERMINISM

Given:

```text
career seed
+
player seed
+
world state
+
rules version
```

the same career simulation must produce:

```text
same seasons
same development
same snapshots
same peak
same final state
```

---

# 99. PHASE 4 DOES NOT HAVE A MATCH ENGINE

This is a critical boundary.

Phase 4 must NOT calculate:

- Goals
- Assists
- Match ratings
- Opponent results
- League tables
- Cup results

Those belong to Phase 5.

Performance in Phase 4 must therefore use an abstract or neutral seasonal input.

---

# 100. PHASE 4 CAREER STATE

At the end of each season, preserve:

```text
age
club
position
role
current_ability
potential
development_rate
development_profile
attributes
player_state
career_phase
peak_data
season_snapshot
```

---

# 101. PHASE 4 ACCEPTANCE TEST

Phase 4 is complete when the system can:

```text
Create Career
     ↓
Start at configured age
     ↓
Advance one season
     ↓
Calculate development budget
     ↓
Apply development
     ↓
Recalculate attributes
     ↓
Recalculate Current Ability
     ↓
Recalculate OVR
     ↓
Update age
     ↓
Update career phase
     ↓
Track peak
     ↓
Create season snapshot
```

It must support repeated seasons.

It must remain deterministic.

It must not require the Match Engine.

---

# 102. PHASE 4 BALANCE TESTING

Before moving to Phase 5, run many isolated careers without matches.

Test:

- Development speed
- Potential realization
- Stagnation
- Late bloomers
- Early decline
- Peak age
- Attribute soft caps
- Club environment influence
- Professionalism influence
- Development profile influence

Do not judge final career realism until the Match Engine exists.

---

# 103. MATCH ENGINE

The match engine does not require full tactical simulation.

Inputs:

```text
team_strength
opponent_strength
home_advantage
form
fatigue
tactical_style
player_roles
player_form
player_traits
randomness
```

Outputs:

```text
score
winner
player_minutes
player_goals
player_assists
player_shots
player_key_passes
player_rating
```

---

# 104. INJURY ENGINE

Categories:

```text
minor
moderate
severe
career_threatening
```

Injury:

```text
type
duration
recurrence_probability
attribute_impact
narrative_importance
```

---

# 105. TRANSFER ENGINE

Transfer probability depends on:

```text
player_overall
potential
age
performance
reputation
contract
club_prestige
market_need
club_attractiveness
player_fit
```

---

# 106. RELATIONSHIPS

Supported:

```text
Player ↔ Manager
Player ↔ Club
Player ↔ Agent
Player ↔ Teammate
Player ↔ Rival
Player ↔ Fans
```

Range:

```text
-100 → +100
```

---

# 107. EVENT ENGINE

Events must be data-driven.

Categories:

```text
SPORT
TRANSFER
INJURY
PERSONAL
MEDIA
RELATIONSHIP
FINANCIAL
NATIONAL_TEAM
ACHIEVEMENT
CHAOS
```

Each event:

```text
id
category
weight
conditions
text
options
effects
narrative_importance
```

---

# 108. DECISION SYSTEM

MVP decisions are automatically resolved.

Future:

```text
Decision
   ↓
Community Vote
   ↓
Selected Option
   ↓
Simulation
```

---

# 109. NARRATIVE ENGINE

The narrative engine must identify:

- Turning points
- Emotional peaks
- Successes
- Failures
- Comebacks
- Rivalries
- Unexpected changes
- Major transfers
- Major injuries
- Historic matches
- Awards
- Records
- Retirement

---

# 110. CAREER ARC DETECTION

Possible archetypes:

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

Multiple arcs may coexist.

---

# 111. LEGACY SYSTEM

At retirement:

```text
legacy_score
```

Factors:

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

# 112. STORY GENERATION

Target:

```text
5–6 minutes
```

Suggested:

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

# 113. AI INTEGRATION

LLM integration is not mandatory for MVP.

Start with:

```text
Structured data
+
Templates
+
Narrative rules
```

Future:

```text
NarrativeProvider
```

---

# 114. UI PHILOSOPHY

Target aesthetic:

> Football Manager × modern sports analytics × premium sports editorial design.

Avoid:

- Generic admin dashboard
- Spreadsheet-heavy UI
- Excessive neon
- Rainbow gradients
- Excessive glassmorphism
- Cheap gaming aesthetics

---

# 115. VISUAL LANGUAGE

Default:

```text
Dark
```

Suggested palette:

```text
Background:      #08090B
Surface:         #111318
Elevated:        #181B21
Border:          #272B33
Primary text:    #F5F5F5
Secondary text:  #8E949F
```

Accent:

```text
Muted football green / lime
```

---

# 116. PRESENTATION MODE

Target:

```text
1080 × 1920
9:16
```

Keyboard:

```text
SPACE → next scene
LEFT  → previous scene
RIGHT → next scene
ESC   → exit
```

---

# 117. DEBUGGER

Internal developer view:

```text
Career seed
Current season
Player identity
Player attributes
Current ability
Overall by position
Potential
Development profile
Role
Form
Confidence
Club strength
Development budget
Development summary
Peak data
World ratings
```

---

# 118. BALANCE TESTING

Once enough systems exist, run hundreds or thousands of careers.

Collect:

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
percentage_late_bloomers
percentage_one_club_legends
percentage_failed_wonderkids
```

Analyze distributions, not only averages.

---

# 119. TESTING REQUIREMENTS

## World

Test:

- Club calculations
- League calculations
- External normalization
- Squad generation
- Deterministic seed
- Manager quality
- Momentum

## Player

Test:

- Player creation
- Internal attribute generation
- Attribute ranges
- PAC
- SHO
- PAS
- DRI
- DEF
- PHY
- MENTAL
- Current Ability
- Position OVR
- Role Fit
- Role Familiarity
- Role Effectiveness
- Potential
- Development Rate
- Development Profiles
- Traits
- Personality
- Player State
- Aging factor
- GK OVR
- Deterministic generation

## Career / Phase 4

Test:

- Career initialization
- Season initialization
- Age progression
- Career phase
- Potential factor
- Development budget
- Playing time factor
- Environment factor
- Professionalism factor
- Performance factor
- State factor
- Random factor
- Development profile distribution
- Internal attribute changes
- Current Ability recalculation
- OVR recalculation
- Peak tracking
- Season snapshot
- Career determinism

## Match

Test:

- Match result
- Player performance
- Minutes
- Role influence
- Trait influence

## Transfers

Test:

- Market value
- Club requirements
- Player fit
- Transfer generation

## Events

Test:

- Conditions
- Probability
- Effects
- Decision resolution

## Narrative

Test:

- Importance
- Arc detection
- Story generation
- Duration estimation

---

# 120. DEFINITION OF DONE

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
Repeated simulations produce believable results
+
Deterministic reproduction works
```

---

# 121. PHASE 1 ACCEPTANCE TEST

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

# 122. PHASE 2 ACCEPTANCE TEST

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
Club Memberships
    ↓
Club Ratings
    ↓
League Ratings
```

The world must be reproducible.

---

# 123. PHASE 3 ACCEPTANCE TEST

```text
Create Player
    ↓
Generate Internal Attributes
    ↓
Generate PAC / SHO / PAS / DRI / DEF / PHY
    ↓
Calculate MENTAL
    ↓
Calculate Current Ability
    ↓
Calculate Position-specific OVR
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

# 124. PHASE 3.1 ACCEPTANCE TEST

The world generation must produce:

- multiple player archetypes
- multiple positional profiles
- secondary positions
- 0–3 traits
- realistic potential distribution
- dedicated GK OVR
- meaningful intra-club variation
- deterministic output

---

# 125. PHASE 4 ACCEPTANCE TEST

The system must support:

```text
Create Career
     ↓
Initialize Season
     ↓
Age progression
     ↓
Calculate development budget
     ↓
Allocate development
     ↓
Modify internal attributes
     ↓
Recalculate Current Ability
     ↓
Recalculate OVR
     ↓
Update career phase
     ↓
Track peak
     ↓
Create snapshot
     ↓
Advance to next season
```

It must work repeatedly for many seasons.

It must not require the Match Engine.

---

# 126. PHASE 4 EXPLICIT NON-GOALS

Do NOT implement:

- Match simulation
- Transfers
- Contracts
- Injuries
- Relationships
- Narrative
- Awards
- Titles
- International career simulation
- Community decisions
- TikTok
- Presentation Mode

Phase 4 builds the career progression loop only.

---

# 127. IMPLEMENTATION RULE FOR JULES

Before implementing a phase:

1. Read `PROJECT_SPEC.md`.
2. Read `.github/instructions/reglas.instructions.md`.
3. Read `AGENTS.md`.
4. Inspect the current repository.
5. Identify the exact requested scope.
6. Produce a concise implementation plan.
7. Wait for approval for major phase changes.
8. Implement only the approved scope.
9. Run tests.
10. Verify the application.
11. Report results.
12. Stop.

Never automatically continue to the next phase.

---

# 128. JULES PULL REQUEST DISCIPLINE

Each major phase or refactor should use its own branch and pull request.

A PR must contain:

- Only the requested scope
- Tests for the implemented functionality
- Required migrations
- Required configuration
- No unrelated refactors
- No future-phase implementations

---

# 129. SIMULATION BALANCE PRINCIPLE

Do not optimize against one seed.

Balance must be evaluated using:

- multiple seeds
- statistical distributions
- broad range assertions
- regression tests
- long-run career simulations once available

Avoid brittle tests based on exact random outcomes unless determinism itself is being tested.

---

# 130. FINAL PRODUCT STRATEGY

TikTok is initially the distribution channel.

Football Life is the underlying product.

The simulator should remain useful independently of social media.

---

# 131. FINAL PRODUCT VISION

Football Life should ultimately feel like:

> **A football career RPG that happens to be a machine for creating stories.**

The complete long-term loop:

```text
PLAYER
   ↓
CAREER
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

But the MVP remains:

```text
PLAYER
   ↓
SIMULATE
   ↓
CAREER
   ↓
STORY
```

---

# 132. FINAL DESIGN PRINCIPLE

The simulator should always answer:

> **Would someone watch the entire 5–6 minute career because they genuinely want to know how it ends?**

If yes:

```text
Football Life is succeeding.
```

If the simulator produces statistically accurate but boring careers:

```text
It has failed.
```

If it produces beautiful screens but predictable careers:

```text
It has failed.
```

If it produces chaotic careers that make no sense:

```text
It has failed.
```

The target is:

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
VISUALLY ATTRACTIVE
     =
FOOTBALL LIFE
```