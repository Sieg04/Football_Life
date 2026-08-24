````markdown
# FOOTBALL LIFE
## Complete Project Specification

**Version:** 1.3  
**Project:** Football Life  
**Type:** Local football career simulator + narrative/story generator  
**Primary platform:** Desktop/local web application  
**Development assistant:** GitHub Copilot Free  
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

Football Life follows five principles.

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
````

is more valuable than an extremely detailed simulation that produces boring results.

---

## 2.2 Every career should be different

Two players with similar starting conditions should not necessarily experience the same career.

Variation should come from:

* Player attributes
* Potential
* Development Rate
* Development Profile
* Personality
* Club context
* Manager
* Playing time
* Form
* Injuries
* Transfers
* Relationships
* Randomness
* World evolution
* Decisions

---

## 2.3 Failure must be possible

The simulation must allow:

* Poor careers
* Injuries
* Failed wonderkids
* Bad transfers
* Early decline
* Long periods on the bench
* Journeyman careers
* Players who never reach potential
* Clubs that decline
* Clubs that unexpectedly become dominant

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

* Club selection
* Transfer decisions
* Contract decisions
* Career choices
* Personal decisions
* Rivalries
* Other important events

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

* User accounts
* Authentication
* Cloud deployment
* Public API
* TikTok API
* TikTok comment scraping
* Community voting
* Multiplayer
* Public career pages
* Mobile application
* 3D matches
* Tactical match simulation
* Complete real-world player database
* Full real-world squad database
* Complex accounting/finances
* Complex agent negotiations
* Mandatory LLM integration
* Automatic video generation

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

* Repository
* Documentation
* Architecture review
* Development rules

No gameplay implementation.

---

## Phase 1 — Foundation

Implement:

* FastAPI
* Angular
* SQLite
* SQLAlchemy
* Alembic
* Configuration
* Health endpoint
* Basic API shell
* Basic Angular shell
* Angular → FastAPI communication
* Basic tests

No football simulation.

---

## Phase 2 — Football World

Implement:

* Countries
* Leagues
* Clubs
* Managers
* Competitions
* External source metadata
* Club attributes
* League attributes
* Club strength
* League strength
* Initial world seed
* Generic squad generation
* Shared Player domain refactor
* ClubMembership
* Initial world tests

Do NOT implement:

* Player development
* Match engine
* Transfers
* Injuries
* Narrative engine

---

## Phase 3 — Player Engine

Implement:

* Player internal attribute system
* PAC / SHO / PAS / DRI / DEF / PHY
* MENTAL group
* Current Ability
* Position-specific OVR
* Potential
* Development Rate
* Development Profiles
* Role Familiarity
* Role Effectiveness
* Traits / PlayStyles
* Personality data
* Player State
* Aging baseline
* Deterministic player generation
* Player attribute generation
* Player validation
* Player persistence

Do NOT implement yet:

* Full career progression
* Seasonal development loop
* Transfers
* Contracts
* Injuries
* Relationships
* Match engine
* Narrative
* Community
* TikTok presentation

---

## Phase 4 — Basic Career Engine

Implement:

```text
Player
 ↓
Season
 ↓
Development
 ↓
Next Season
```

Allow careers to progress approximately from age 16 to retirement.

The Player Engine from Phase 3 provides the calculations used by this phase.

---

## Phase 5 — Match Engine

Implement:

* Match results
* Team strength
* Playing time
* Player performance
* Goals
* Assists
* Ratings
* Competition outcomes
* Match importance
* Role impact
* Traits contextual effects

---

## Phase 6 — Career Depth

Implement:

* Form
* Fatigue
* Fitness
* Confidence
* Morale
* Injuries
* Relationships
* Manager interaction
* Dynamic role changes
* Position conversion

---

## Phase 7 — Transfer Engine

Implement:

* Market value
* Club needs
* Transfer offers
* Contracts
* Transfer windows
* Club attractiveness
* Player fit
* Transfer decisions

---

## Phase 8 — Event Engine

Implement:

* Data-driven events
* Conditions
* Probabilities
* Effects
* Decisions
* Automatic resolution

---

## Phase 9 — Narrative Engine

Implement:

* Timeline
* Narrative importance
* Career arcs
* Legacy score
* Story beats
* Story generation

---

## Phase 10 — Frontend

Implement:

* Home
* Player creation
* Career dashboard
* Season view
* Event view
* Timeline
* Statistics
* Transfers
* Retirement
* Story screen

---

## Phase 11 — Visual Polish

Implement:

* Dark theme
* Typography
* Animations
* Player cards
* Trophy presentation
* Timeline animations
* Microinteractions
* Visual hierarchy

---

## Phase 12 — TikTok Presentation Mode

Implement:

* 9:16 layout
* 1080 × 1920 target
* Scene system
* Keyboard navigation
* Recording-friendly presentation
* Story progression

---

## Phase 13 — Simulation Balance

Run hundreds or thousands of careers.

Analyze:

* Career length
* Peak overall
* Final overall
* Transfers
* Injuries
* Goals
* Trophies
* Retirement age
* Potential attainment
* Major titles
* Narrative-event frequency
* Late bloomers
* One-club legends
* Career failures

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

* Angular
* TypeScript
* FastAPI
* HTTP
* SQLAlchemy
* SQLite
* REST
* Frontend components

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

* Reproducing careers
* Debugging
* Snapshot recovery
* Balance testing
* Future community branching

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

* Event definitions
* Attribute weights
* Position weights
* Role weights
* Development coefficients
* Probabilities
* Injury probabilities
* Transfer conditions
* Trait definitions

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

* Generic squad players
* Future career protagonists

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

```text
GK =
weighted_average(
    goalkeepers
)
```

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
Generate Player
        ↓
Generate attributes
        ↓
Calculate current ability
        ↓
Create ClubMembership
        ↓
Assign squad role
        ↓
Calculate squad strength
```

Generic players may initially have limited identity/narrative information.

They must nevertheless share the same fundamental football-player model as the future protagonist.

---

# 25. GENERIC PLAYER ATTRIBUTES

Generic players must have actual football attributes rather than only a single `rating`.

The generated attributes should produce a `current_ability` approximately consistent with the club-strength target.

This is necessary to preserve Phase 2 balance.

---

# 26. CLUB PRESTIGE

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

# 27. PRESTIGE EVOLUTION

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

# 28. FINANCIAL POWER

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

# 29. FINANCIAL EVOLUTION

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

This belongs to future world simulation phases.

---

# 30. ACADEMY QUALITY

Suggested:

```text
ACADEMY_QUALITY =
    academy_reputation   × 0.40
  + facilities           × 0.25
  + youth_investment     × 0.20
  + country_youth_factor × 0.15
```

---

# 31. ACADEMY AS TALENT DISTRIBUTION

Academy quality changes the probability distribution of generated youth players.

It does NOT directly determine an exact player rating.

Example:

```text
Academy Quality = 90
```

should increase the probability of:

```text
70–80 prospects
80–88 prospects
89+ exceptional prospects
```

Lower-quality academies should produce lower distributions.

Exceptional RNG outcomes must remain possible at small clubs.

---

# 32. FACILITIES

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

# 33. FAN PRESSURE

Suggested:

```text
FAN_PRESSURE =
    club_size       × 0.35
  + prestige        × 0.25
  + expectations    × 0.25
  + media_attention × 0.15
```

Higher pressure increases the probability of:

* Media criticism
* Manager pressure
* Player criticism
* Crisis events
* Board dissatisfaction

---

# 34. DOMESTIC REPUTATION

Suggested:

```text
DOMESTIC_REPUTATION =
    domestic_titles  × 0.40
  + league_success   × 0.30
  + fanbase          × 0.15
  + domestic_media  × 0.15
```

---

# 35. INTERNATIONAL REPUTATION

Suggested:

```text
INTERNATIONAL_REPUTATION =
    uefa_coefficient_normalized × 0.40
  + european_titles             × 0.25
  + european_appearances        × 0.15
  + global_reputation           × 0.20
```

---

# 36. UEFA COEFFICIENT

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

Keep raw value available for reference.

---

# 37. CLUB MOMENTUM

Momentum represents current trajectory.

Scale:

```text
-100 → +100
```

Examples:

```text
+85 = extraordinary positive momentum
0   = neutral
-70 = significant crisis
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

Full momentum evolution belongs to later simulation phases.

---

# 38. RESULT MOMENTUM

Conceptually:

```text
RESULT_MOMENTUM =
    actual_performance
    -
    expected_performance
```

Example:

```text
Expected position = 8
Actual position   = 3
```

produces positive momentum.

Example:

```text
Expected position = 3
Actual position   = 12
```

produces negative momentum.

Normalize to:

```text
-100 → +100
```

---

# 39. MOMENTUM NORMALIZATION

For formulas using a 0–100 value:

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

# 40. CLUB ATTRACTIVENESS

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

This will later influence transfers and player decisions.

---

# 41. LEAGUE SYSTEM

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

# 42. LEAGUE STRENGTH

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

# 43. LEAGUE STRENGTH INITIALIZATION

Initial value may use:

```text
Opta
+
IFFHS
+
external reference data
```

Normalize to:

```text
0–100
```

This becomes the initial target.

---

# 44. LEAGUE EVOLUTION

Each season:

```text
new_league_strength =
    current_strength × 0.70
  + newly_calculated_strength × 0.30
```

This should happen only once the world simulation exists.

---

# 45. LEAGUE PRESTIGE

Suggested:

```text
LEAGUE_PRESTIGE =
    historical_success        × 0.30
  + european_success          × 0.25
  + star_power                × 0.15
  + domestic_competitiveness  × 0.15
  + global_attention          × 0.15
```

Prestige evolves slowly.

---

# 46. LEAGUE FINANCIAL STRENGTH

Suggested:

```text
LEAGUE_FINANCIAL_STRENGTH =
    broadcast_revenue × 0.35
  + club_finances     × 0.30
  + sponsorship       × 0.20
  + attendance        × 0.15
```

---

# 47. LEAGUE GLOBAL REPUTATION

Suggested:

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

Major competitions can have stronger influence.

Suggested multipliers:

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

Suggested:

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

Suggested initial values:

```text
Champions League       100
Europa League           78
Conference League       62
Major domestic cup      75
League title            80
```

These are configurable.

---

# 55. COMPETITION STRENGTH

Separate:

```text
competition_prestige
```

from:

```text
competition_strength
```

Strength is based on the quality of participants.

Prestige represents importance and historical meaning.

---

# 56. WORLD EVOLUTION

The world must not remain static.

Eventually:

```text
Club Results
     ↓
Momentum
     ↓
Prestige / Finances / Reputation
     ↓
Club Strength
     ↓
League Strength
     ↓
Transfer Attractiveness
     ↓
Future Results
```

Changes must remain gradual.

---

# 57. PLAYER DOMAIN — OVERVIEW

Football Life uses a single shared `Player` domain for:

* Generic squad players
* Career protagonists

A Player is the football identity.

A Career is the professional history associated with that football identity.

Do NOT create:

```text
GenericSquadPlayer
CareerPlayer
```

as separate football models.

Preferred conceptual structure:

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

# 58. PLAYER IDENTITY

A Player contains:

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

# 59. PLAYER ATTRIBUTE PHILOSOPHY

The attribute system takes inspiration from established football-game systems such as EA SPORTS FC/FIFA and complementary ideas from PES/eFootball.

Do NOT attempt to reproduce proprietary formulas.

Use established football-game conventions as design references while implementing Football Life's own mathematical model.

The system must be understandable to viewers familiar with football games.

---

# 60. TOP-LEVEL PLAYER ATTRIBUTES

The player has six main visible attribute groups:

```text
PAC — Pace
SHO — Shooting
PAS — Passing
DRI — Dribbling
DEF — Defending
PHY — Physical
```

An additional internal group exists:

```text
MENTAL
```

MENTAL is used by the simulation and OVR calculations but does not need to appear as a seventh primary card stat.

---

# 61. INTERNAL PLAYER ATTRIBUTES

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

All internal attributes use:

```text
1–100
```

---

# 62. TOP-LEVEL GROUP CALCULATIONS

Top-level visible groups are derived from internal attributes.

They are NOT independent stored ratings.

## PAC

```text
PAC =
weighted_average(
    acceleration,
    sprint_speed
)
```

## SHO

```text
SHO =
weighted_average(
    finishing,
    shot_power,
    long_shots,
    volleys,
    penalties
)
```

## PAS

```text
PAS =
weighted_average(
    vision,
    short_passing,
    long_passing,
    crossing,
    curve
)
```

## DRI

```text
DRI =
weighted_average(
    agility,
    balance,
    ball_control,
    dribbling,
    reactions
)
```

## DEF

```text
DEF =
weighted_average(
    defensive_awareness,
    standing_tackle,
    interceptions,
    heading
)
```

## PHY

```text
PHY =
weighted_average(
    strength,
    stamina,
    jumping,
    aggression
)
```

Exact internal weights belong in:

```text
data/rules/player_attributes.json
```

---

# 63. MENTAL GROUP

MENTAL is calculated separately:

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

The weights should remain configurable.

---

# 64. CURRENT ABILITY

Current Ability represents:

> **The player's general football quality independent of one specific position.**

Initial model:

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

This is the initial baseline.

A future balance pass may introduce weakness penalties if extreme weaknesses make the linear model too forgiving.

The first implementation should remain simple and deterministic.

---

# 65. CURRENT ABILITY VS OVR

These concepts MUST remain separate.

```text
Current Ability
=
General football quality

OVR
=
Effectiveness in a specific position
```

Example:

```text
Current Ability = 84

ST OVR  = 87
CAM OVR = 83
CM OVR  = 76
```

Changing position does not mutate the internal attributes.

---

# 66. POSITION-SPECIFIC OVR

OVR is calculated from:

```text
PAC
SHO
PAS
DRI
DEF
PHY
MENTAL
```

using position-specific weights.

## ST

```text
SHO       35%
PAC       20%
DRI       20%
PHY       10%
PAS       10%
MENTAL     5%
```

## LW / RW

```text
DRI       25%
PAC       25%
SHO       20%
PAS       15%
PHY       10%
MENTAL     5%
```

## CAM / AM

```text
PAS       25%
DRI       20%
MENTAL    20%
SHO       15%
PAC       10%
PHY       10%
```

## CM

```text
PAS       25%
DRI       20%
MENTAL    20%
DEF       15%
PHY       10%
SHO       10%
```

## DM

```text
DEF       25%
PAS       25%
MENTAL    20%
PHY       15%
DRI       10%
SHO        5%
```

## CB

```text
DEF       35%
PHY       25%
MENTAL    15%
PAS       15%
PAC       10%
```

## LB / RB

```text
DEF       25%
PAC       20%
PHY       15%
PAS       15%
DRI       15%
MENTAL    10%
```

These are configurable starting values.

---

# 67. GOALKEEPER SUPPORT

Goalkeepers will eventually use goalkeeper-specific attributes:

```text
diving
handling
kicking
reflexes
speed
positioning
```

Goalkeeper OVR should have a dedicated calculation.

Unless required by the current Phase 3 implementation, the full goalkeeper subsystem may be deferred.

Do not allow GK-specific complexity to delay the rest of the Player Engine.

---

# 68. POSITION CHANGE

A player may change positions during their career.

Example:

```text
RW
↓
LW
↓
CAM
↓
CM
```

Changing position does NOT alter underlying attributes.

It changes:

* Primary position
* Secondary positions
* OVR
* Role familiarity
* Tactical fit

Later development can adapt to the new position.

Full position conversion belongs to the career/development phase.

---

# 69. POSITION OVR EXAMPLE

A player:

```text
PAC 88
SHO 74
PAS 61
DRI 83
DEF 32
PHY 70
MENTAL 82
```

might have:

```text
RW OVR = 81
CAM OVR = 77
ST OVR = 76
CM OVR = 68
```

The player attributes did not change.

Only the evaluation context changed.

---

# 70. POSITIONAL ROLES

Players have role-specific effectiveness.

Example:

```text
Advanced Forward
Poacher
False 9
Target Forward
```

The role rating depends on:

* Attribute suitability
* Position
* Traits
* Mental profile
* Role requirements

---

# 71. ROLE FAMILIARITY

Role familiarity uses:

```text
0–100
```

Example:

```text
Advanced Forward: 92
Poacher:           81
False 9:           48
Target Forward:    63
```

Role familiarity does NOT alter base attributes.

It represents how comfortable the player is performing a role.

---

# 72. ROLE ATTRIBUTE FIT

Each role has configurable attribute weights.

Example:

## Advanced Forward

```text
SHO       30%
PAC       20%
DRI       15%
MENTAL    15%
PHY       10%
PAS       10%
```

## Target Forward

```text
PHY       30%
SHO       25%
MENTAL    20%
PAS       10%
DRI       10%
PAC        5%
```

The role's `attribute_fit` is the weighted average using these requirements.

---

# 73. ROLE EFFECTIVENESS

Role effectiveness is separate from OVR.

Initial model:

```text
ROLE_EFFECTIVENESS =
    ATTRIBUTE_FIT    × 0.70
  + ROLE_FAMILIARITY × 0.30
```

Example:

```text
Attribute Fit: 88
Familiarity:   60

Role Effectiveness =
88 × 0.70 + 60 × 0.30
= 79.6
```

Do NOT multiply OVR directly by familiarity.

This prevents extreme or unintuitive rating collapses.

---

# 74. ROLE FAMILIARITY GENERATION

Initial role familiarity depends on:

* Primary position
* Secondary positions
* Attributes
* Development Profile
* Controlled randomness

Suggested baseline:

```text
Primary role      → 80–95
Secondary role    → 55–80
Unnatural role    → 20–50
```

Exact ranges are configurable.

Generation must be deterministic.

---

# 75. TRAITS / PLAYSTYLES

Phase 3 should define and store player traits.

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

Phase 3 does NOT apply match effects.

Future:

```text
Trait
↓
Match Engine behavior
↓
Narrative context
```

Traits should initially be represented by stable IDs and configuration.

---

# 76. TRAIT PRINCIPLE

Traits should not simply be universal numerical buffs.

Example:

```text
BIG_GAME_PLAYER
```

should eventually influence performance in high-importance matches rather than every match.

Example:

```text
RAPID
```

should eventually influence situations where acceleration or speed matters.

Trait behaviour belongs to later phases.

---

# 77. PERSONALITY

Players contain:

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

Possible derived descriptors:

```text
AMBICIOUS
LOYAL
MERCENARY
PROFESSIONAL
HOT_HEAD
LEADER
COMPETITIVE
INTROVERT
PARTY_ANIMAL
```

Phase 3 should create and validate personality data.

Phase 3 should NOT yet implement behavioural consequences.

Later systems may use personality for:

* Development
* Transfers
* Relationships
* Media
* Decisions
* Loyalty
* Confidence

---

# 78. POTENTIAL

Potential represents the theoretical ceiling.

Rule:

```text
potential >= current_ability
```

for initial player generation.

Example:

```text
Current Ability = 62
Potential = 87
```

Potential does not guarantee reaching 87.

The player's career outcome depends on future circumstances.

---

# 79. POTENTIAL GENERATION

Potential gap:

```text
potential_gap =
potential - current_ability
```

Initial generation should use configurable ranges.

Typical range:

```text
5–30 points
```

Players should not all have huge potential.

The distribution should contain:

* Normal professionals
* High-potential players
* Wonderkids
* Low-ceiling players
* Late bloomers

---

# 80. DEVELOPMENT RATE

Development Rate:

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

Development Rate represents predisposition toward improvement.

It does not directly equal annual rating growth.

---

# 81. DEVELOPMENT PROFILES

Profiles determine which attribute groups receive stronger development weighting.

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

---

# 82. DEVELOPMENT PROFILE — FINISHER

Example multipliers:

```text
PAC       1.05
SHO       1.30
PAS       1.00
DRI       1.10
DEF       0.90
PHY       1.00
MENTAL    1.05
```

These are starting values.

---

# 83. DEVELOPMENT PROFILE — PLAYMAKER

Example:

```text
PAC       0.95
SHO       0.95
PAS       1.30
DRI       1.15
DEF       0.95
PHY       0.90
MENTAL    1.25
```

---

# 84. DEVELOPMENT PROFILE — ATHLETIC

Example:

```text
PAC       1.30
SHO       1.00
PAS       0.95
DRI       1.10
DEF       1.00
PHY       1.30
MENTAL    0.95
```

---

# 85. DEVELOPMENT PROFILE — DEFENSIVE

Example:

```text
PAC       1.00
SHO       0.85
PAS       1.00
DRI       0.90
DEF       1.30
PHY       1.20
MENTAL    1.10
```

---

# 86. DEVELOPMENT PROFILE — LATE BLOOMER

Late Bloomer primarily modifies the age/development curve rather than forcing a specific attribute specialization.

Its purpose is:

> Allow meaningful development to occur later than the typical player.

It should not simply give permanent bonuses to all attributes.

---

# 87. DEVELOPMENT PROFILE EVOLUTION

A player's development profile may change during their career.

Example:

```text
Explosive winger
↓
Loss of pace
↓
Improved passing
↓
Improved decision-making
↓
Converted to CAM
↓
Creative playmaker
```

Full profile evolution belongs to future career/development systems.

Phase 3 only needs:

* Profile data
* Profile coefficients
* Profile validation
* Profile-aware development calculations

---

# 88. AGING BASELINE

Phase 3 defines an age factor but does not simulate complete career progression.

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

These values represent development opportunity.

They are NOT direct annual OVR changes.

They remain configurable.

---

# 89. DEVELOPMENT MODEL

Conceptually:

```text
DEVELOPMENT_DELTA =
    POTENTIAL_GAP
  × AGE_FACTOR
  × DEVELOPMENT_RATE_FACTOR
  × DEVELOPMENT_PROFILE_FACTOR
  × PLAYING_TIME_FACTOR
  × PERFORMANCE_FACTOR
  × ENVIRONMENT_FACTOR
  × PROFESSIONALISM_FACTOR
  × INJURY_FACTOR
  × RANDOMNESS
```

Phase 3 should prepare the pure calculation structure.

The actual season loop belongs to Phase 4.

---

# 90. PLAYER STATE

Player State is separate from permanent attributes.

Contains:

```text
confidence
morale
form
fitness
fatigue
happiness
reputation
```

All:

```text
0–100
```

Phase 3 should:

* Define the state
* Validate ranges
* Provide defaults
* Persist the state

It should NOT yet implement complex state evolution.

---

# 91. PLAYER DOMAIN SUMMARY

```text
PLAYER
│
├── Identity
│
├── Internal Attributes
│   ├── Pace
│   ├── Shooting
│   ├── Passing
│   ├── Dribbling
│   ├── Defending
│   ├── Physical
│   └── Mental
│
├── Visible Groups
│   ├── PAC
│   ├── SHO
│   ├── PAS
│   ├── DRI
│   ├── DEF
│   └── PHY
│
├── Current Ability
├── Potential
├── Development Rate
├── Development Profile
├── Role Familiarity
├── Traits
├── Personality
│
└── Player State
    ├── Form
    ├── Fitness
    ├── Fatigue
    ├── Morale
    ├── Confidence
    ├── Happiness
    └── Reputation
```

---

# 92. PLAYER / CAREER SEPARATION

The Player represents:

> **Who the footballer is.**

The Career represents:

> **What happened to the footballer.**

Therefore:

```text
Player
   ↓
Career
   ├── Seasons
   ├── Events
   ├── Transfers
   ├── Injuries
   ├── Awards
   ├── Titles
   ├── International career
   ├── Timeline
   └── Narrative
```

The Career must not duplicate the Player's football attributes.

---

# 93. CLUB MEMBERSHIP

```text
ClubMembership
├── player_id
├── club_id
├── role
├── start_date
└── end_date
```

Role belongs to membership.

The Player identity survives transfers.

---

# 94. MATCH ENGINE

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

# 95. MATCH IMPORTANCE

## NORMAL

Aggregate simulation.

## IMPORTANT

Can create player-specific moments.

## LEGENDARY

Examples:

* Champions League final
* World Cup final
* Major derby
* Decisive title match
* Historic record opportunity

Legendary matches receive high narrative importance.

---

# 96. SEASON ENGINE

Season flow:

```text
Pre-season
↓
League
↓
Domestic cup
↓
European competition
↓
International fixtures
↓
Season evaluation
↓
Awards
↓
Development
↓
World evolution
↓
Transfers
↓
Next season
```

---

# 97. INJURY ENGINE

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

Do not generate injuries solely for storytelling.

---

# 98. TRANSFER ENGINE

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

# 99. CONTRACT SYSTEM

Contract:

```text
salary
duration
release_clause
role
bonuses
```

Roles:

```text
YOUTH
ROTATION
BACKUP
STARTER
KEY_PLAYER
STAR
```

---

# 100. RELATIONSHIPS

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

Relationships evolve through:

* Performance
* Playing time
* Transfers
* Events
* Personality
* Conflicts
* Team success

---

# 101. RIVALRIES

Rivalries may arise from:

* Competition for a position
* Repeated important encounters
* Personality conflicts
* Media controversy
* Historic matches

Possible consequences:

* Media events
* Conflict
* Performance changes
* Historic matches
* Narrative moments

Do not force rivalries artificially.

---

# 102. NATIONAL TEAM

Selection depends on:

```text
nationality
overall
form
reputation
position competition
manager preference
```

Track:

```text
caps
goals
assists
tournaments
titles
```

---

# 103. EVENT ENGINE

Events must be data-driven.

Suggested categories:

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

# 104. DECISION SYSTEM

MVP decisions are automatically resolved.

Decision resolution considers:

```text
personality
current_state
relationships
career_goals
club_situation
randomness
```

The simulation accepts a selected option.

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

# 105. CAREER

A `Career` represents the professional story of a `Player`.

Conceptually:

```text
Player
   ↓
Career
   ├── Seasons
   ├── Events
   ├── Transfers
   ├── Injuries
   ├── Awards
   ├── Titles
   ├── International career
   ├── Timeline
   └── Narrative
```

The Player is the football identity.

The Career is the history.

---

# 106. CAREER SNAPSHOTS

Important states should be saveable.

```text
career_id
season
date
player_state
club_state
relationships
contracts
events
world_state
```

Snapshots enable:

* Resume
* Reproduce
* Debug
* Duplicate
* Future community branching

---

# 107. CAREER TIMELINE

Example:

```text
16 — Academy debut
17 — Professional debut
18 — First goal
19 — Major transfer
21 — ACL injury
23 — Champions League
25 — Ballon d'Or
28 — Decline
31 — Return to childhood club
33 — Europa League
35 — Retirement
```

Each event:

```text
date
type
title
description
importance
emotional_impact
career_impact
```

---

# 108. NARRATIVE IMPORTANCE

Every major event gets:

```text
1–10
```

Example:

```text
Normal match        1
Good performance    2
First goal          4
Debut               5
First title         6
Transfer            7
Major injury        8
Major final         9
Ballon d'Or        10
Retirement         10
```

---

# 109. NARRATIVE ENGINE

The narrative engine must identify:

* Turning points
* Emotional peaks
* Successes
* Failures
* Comebacks
* Rivalries
* Unexpected changes
* Major transfers
* Major injuries
* Historic matches
* Awards
* Records
* Retirement

It must NOT simply list every season.

Boring periods should be compressed.

Important periods should receive more narrative space.

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

Example:

```text
WONDERKID
    ↓
FALL_FROM_GRACE
    ↓
REDEMPTION
```

The archetype must emerge from the actual career.

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

Score:

```text
0–100
```

Example:

```text
91 / 100

THE REDEMPTION
```

---

# 112. STORY GENERATION

Target duration:

```text
5–6 minutes
```

Suggested structure:

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

Not every career needs every section.

---

# 113. STORY OUTPUT

Example:

```json
{
  "title": "The Career Nobody Saw Coming",
  "arc": "REDEMPTION",
  "estimated_duration_seconds": 342,
  "segments": [
    {
      "type": "HOOK",
      "duration": 15,
      "text": "..."
    },
    {
      "type": "ORIGIN",
      "duration": 30,
      "text": "..."
    }
  ]
}
```

This can later support:

* Text-to-speech
* AI narration
* Subtitles
* Automatic video generation
* External editing

---

# 114. STORY LENGTH RULES

Do not narrate every season individually.

Compress low-importance periods.

Give more time to:

* Debut
* Breakthrough
* Major transfers
* Injuries
* Rivalries
* Finals
* Awards
* Records
* Crises
* Comebacks
* Retirement

---

# 115. AI INTEGRATION

LLM integration is NOT mandatory for MVP.

Start with:

```text
Structured data
+
Templates
+
Narrative rules
```

Future abstraction:

```text
NarrativeProvider
```

Potential implementations:

```text
TemplateNarrativeProvider
LLMNarrativeProvider
```

Simulation must never depend directly on an LLM.

---

# 116. UI PHILOSOPHY

Target aesthetic:

> Football Manager × modern sports analytics × premium sports editorial design.

Avoid:

* Generic admin dashboard
* Spreadsheet-heavy UI
* Excessive neon
* Rainbow gradients
* Excessive glassmorphism
* Cheap gaming aesthetics

---

# 117. VISUAL LANGUAGE

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

# 118. TYPOGRAPHY

Primary:

```text
Inter
```

Display:

```text
Bebas Neue
Oswald
Archivo Narrow
```

Display typography should be used for:

* Player names
* Large numbers
* Headlines
* Seasons
* Results
* Milestones

---

# 119. HOME SCREEN

Hero:

```text
FOOTBALL LIFE

Build a player.
Simulate a life.
Tell the story.

[ START CAREER ]
```

Below:

```text
Recent Careers
```

Use visually rich cards.

---

# 120. PLAYER CREATION

Do not create a generic CRUD form.

Use an interactive player card.

Main inputs:

```text
Name
Surname
Nationality
Position
Age
Starting Club
```

Optional:

```text
Preferred Foot
Height
Starting Ability
Potential
Personality
```

---

# 121. PLAYER CARD

Target visual:

```text
┌─────────────────────────────┐
│      DIEGO SANTOS           │
│      ST · SPAIN · 18        │
│                             │
│          OVR 74             │
│                             │
│ PAC 82    SHO 76            │
│ PAS 58    DRI 79            │
│ DEF 32    PHY 71            │
│                             │
│ POTENTIAL 91                │
│                             │
│ Advanced Forward ★★★        │
└─────────────────────────────┘
```

The UI displays high-level information.

The engine retains detailed internal attributes.

---

# 122. CAREER DASHBOARD

Display:

```text
Player name
Age
Club
Nationality
Position
Overall
Market value
Goals
Assists
Trophies
Current season
```

Also:

```text
Form
Confidence
Morale
Manager relationship
```

Include:

```text
MOMENT OF THE SEASON
```

---

# 123. TIMELINE UI

Visual timeline:

```text
16       19        23        27        31        35
●────────●─────────●─────────●─────────●─────────●
         ↑                   ↑
      Transfer             UCL
```

Important events should be visually larger.

---

# 124. PLAYER STATISTICS

Recommended charts:

* Overall progression
* Attribute progression
* Goals per season
* Assists per season
* Market value
* Club history
* Trophies
* International career

---

# 125. RETIREMENT SCREEN

Example:

```text
CAREER COMPLETE

PLAYER NAME

Age 16 → 35

Matches
Goals
Assists
Titles
Awards

LEGACY SCORE

91 / 100

THE REDEMPTION
```

Show major career moments.

---

# 126. PRESENTATION MODE

Presentation Mode is an MVP requirement.

Target:

```text
1080 × 1920
9:16
```

Hide standard navigation.

Keyboard:

```text
SPACE → next scene
LEFT  → previous scene
RIGHT → next scene
ESC   → exit
```

The presentation should feel like a sports documentary.

---

# 127. PRESENTATION SCENES

Possible scenes:

```text
01 PLAYER INTRO
02 ORIGIN
03 EARLY CAREER
04 BREAKTHROUGH
05 MAJOR TRANSFER
06 PRIME
07 CRISIS
08 COMEBACK
09 FINAL YEARS
10 RETIREMENT
11 LEGACY
```

Scenes are dynamic.

If no crisis exists:

> Do not invent one.

---

# 128. PRESENTATION ANIMATIONS

Use subtle animations:

* Player card entrance
* Number counters
* Club badge transitions
* Trophy reveals
* Timeline progression
* Legacy score count-up
* Event reveals
* Season transitions

Avoid excessive motion.

---

# 129. RESPONSIVE REQUIREMENTS

Normal application:

```text
Minimum target: 1280 × 720
```

Presentation:

```text
1080 × 1920
```

Mobile browser support is not required for MVP.

---

# 130. CAREER GENERATION UX

Flow:

```text
CREATE PLAYER
      ↓
GENERATE WORLD STATE
      ↓
START CAREER
      ↓
SIMULATE
```

Show progress:

```text
Simulating career...

Season 2028/29 ✓
Season 2029/30 ✓
Season 2030/31 ✓
Season 2031/32...
```

---

# 131. DEBUGGER

Internal developer/debug view should show:

```text
Career seed
Current season
Player identity
Player attributes
Current ability
Overall by position
Potential
Development profile
Current role
Form
Confidence
Club strength
Manager relationship
Transfer offers
Events
Decisions
RNG outcomes
World ratings
```

The debugger does not need visual polish.

---

# 132. DATA QUALITY

External values should store:

```text
source
source_date
raw_value
normalized_value
```

The external ranking is the initial world state, not an immutable truth.

---

# 133. BALANCE TESTING

Once the simulator works, run hundreds or thousands of careers.

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

Analyze distributions rather than only averages.

---

# 134. CAREER VARIETY

Possible outcomes:

```text
Superstar
Solid professional
Journeyman
Cult hero
One-club legend
Wonderkid failure
Late bloomer
Injury tragedy
International legend
Domestic legend
European superstar
Career interrupted
Unexpected comeback
```

---

# 135. WORLD VARIETY

Possible club/world outcomes:

```text
Historic giant dominance
Emerging club dynasty
League decline
League resurgence
Financial crisis
Unexpected European success
Academy golden generation
Club rebuild
Managerial golden era
Unexpected powerhouse
```

---

# 136. PERFORMANCE VS PRESTIGE

Always distinguish:

```text
CURRENT_STRENGTH
PRESTIGE
FINANCIAL_POWER
MOMENTUM
```

Example:

```text
Real Madrid
Strength: 86
Prestige: 99
Finances: 97
Momentum: -20
```

This is valid.

---

# 137. PLAYER DATA MODEL SUMMARY

```text
PLAYER
│
├── Identity
│
├── Internal Attributes
│   ├── Pace
│   ├── Shooting
│   ├── Passing
│   ├── Dribbling
│   ├── Defending
│   ├── Physical
│   └── Mental
│
├── Visible Groups
│   ├── PAC
│   ├── SHO
│   ├── PAS
│   ├── DRI
│   ├── DEF
│   └── PHY
│
├── Current Ability
├── Potential
├── Development Rate
├── Development Profile
├── Role Familiarity
├── Role Effectiveness
├── Traits
├── Personality
│
└── Player State
    ├── Form
    ├── Fitness
    ├── Fatigue
    ├── Morale
    ├── Confidence
    ├── Happiness
    └── Reputation
```

---

# 138. CLUB MEMBERSHIP MODEL

```text
ClubMembership
├── player_id
├── club_id
├── role
├── start_date
└── end_date
```

Role belongs to membership.

The Player identity survives transfers.

---

# 139. CAREER MODEL

```text
Career
├── Player
├── Seasons
├── Events
├── Transfers
├── Injuries
├── Awards
├── Titles
├── International Career
├── Timeline
└── Narrative
```

---

# 140. FUTURE COMMUNITY ARCHITECTURE

Do NOT implement during MVP.

Future:

```text
Career
   ↓
Decision
   ↓
CommunityDecision
   ↓
Votes
   ↓
WinningOption
   ↓
CareerSnapshot
```

The Simulation Engine should not care whether a decision came from:

```text
Automatic
User
Community
```

It should receive a selected option.

---

# 141. FUTURE AI AND MEDIA

Potential:

```text
AI Story Writer
AI Voice Narration
AI Player Portraits
AI Club Graphics
Automatic Video Generation
Automatic Subtitles
```

---

# 142. TESTING REQUIREMENTS

## World

Test:

* Club calculations
* League calculations
* External normalization
* Squad generation
* Deterministic seed
* Manager quality
* Momentum

## Player

Test:

* Player creation
* Internal attribute generation
* Attribute ranges
* PAC calculation
* SHO calculation
* PAS calculation
* DRI calculation
* DEF calculation
* PHY calculation
* MENTAL calculation
* Current Ability calculation
* Position-specific OVR
* OVR changes between positions
* Current Ability separated from OVR
* Potential generation
* Potential >= Current Ability
* Development Rate generation
* Development Profile assignment
* Role Familiarity generation
* Role Effectiveness
* Traits
* Personality
* Player State
* Aging factor
* Deterministic generation
* Persistence

## Match

Test:

* Match result
* Player performance
* Minutes
* Role influence
* Trait influence

## Transfers

Test:

* Market value
* Club requirements
* Player fit
* Transfer generation

## Events

Test:

* Conditions
* Probability
* Effects
* Decision resolution

## Narrative

Test:

* Importance
* Arc detection
* Story generation
* Duration estimation

## Determinism

Critical:

```text
same_seed_same_result
```

---

# 143. DEFINITION OF DONE

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
```

---

# 144. PHASE 1 ACCEPTANCE TEST

Phase 1 complete when:

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

# 145. PHASE 2 ACCEPTANCE TEST

Phase 2 complete when:

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

It must not yet simulate a complete player career.

---

# 146. PHASE 3 ACCEPTANCE TEST

Phase 3 complete when:

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

The system must support different outcomes for players with similar potential.

Potential must not guarantee the final career outcome.

Changing position must change OVR without mutating internal attributes.

---

# 147. PHASE 3 EXPLICIT NON-GOALS

Phase 3 must NOT implement:

* Full season simulation
* Long-term development loop
* Match engine
* Transfer engine
* Contract engine
* Injury engine
* Relationships
* Career timeline
* Narrative engine
* Community decisions
* TikTok presentation
* Automatic video generation

Phase 3 builds the Player Engine only.

---

# 148. PHASE 3 CONFIGURATION

Phase 3 should use at least:

```text
backend/data/rules/player_attributes.json
backend/data/rules/player_development.json
backend/data/rules/player_roles.json
backend/data/rules/player_traits.json
```

These should contain:

### player_attributes.json

* Internal attribute group weights
* PAC weights
* SHO weights
* PAS weights
* DRI weights
* DEF weights
* PHY weights
* MENTAL weights
* Position OVR weights

### player_development.json

* Development Rate ranges
* Development Profile coefficients
* Age factors
* Potential gap ranges

### player_roles.json

* Role definitions
* Role attribute weights
* Familiarity generation ranges

### player_traits.json

* Trait identifiers
* Trait categories
* Future effect metadata

---

# 149. PHASE 3 DOMAIN BOUNDARY

Phase 3 domain logic should remain independent of:

```text
FastAPI
Angular
HTTP
SQLAlchemy
SQLite
REST
```

The pure Player calculations should be testable without:

* Web server
* Database
* Frontend
* HTTP request

---

# 150. PLAYER GENERATION REQUIREMENTS

Player generation must be deterministic.

Given:

```text
seed
+
position
+
initial conditions
```

the same generated player should have the same:

* Internal attributes
* PAC
* SHO
* PAS
* DRI
* DEF
* PHY
* MENTAL
* Current Ability
* Potential
* Development Rate
* Development Profile
* Role Familiarity
* Traits
* Personality
* Initial State

---

# 151. PLAYER GENERATION VARIETY

Generated players should not all look statistically identical.

The generator must be capable of producing:

```text
Technical player
Physical player
Creative player
Defensive player
Finisher
Playmaker
Athlete
Balanced player
High-potential wonderkid
Low-ceiling professional
Late bloomer
```

The distributions should be configurable.

---

# 152. PLAYER GENERATION EXAMPLE

Example player:

```text
DIEGO SANTOS
Age: 18
Position: ST

PAC 82
SHO 76
PAS 58
DRI 79
DEF 32
PHY 71
MENTAL 74

Current Ability: 71
Potential: 88
Development Rate: 82

Development Profile:
FINISHER

Advanced Forward:
88
Poacher:
84
False 9:
61
Target Forward:
67
```

This is an example only.

The actual numbers must come from deterministic generation.

---

# 153. DEVELOPMENT PHILOSOPHY

The Player Engine should support careers such as:

## Superstar

```text
16 → 61
18 → 71
21 → 83
24 → 90
28 → 94
31 → 91
35 → 82
```

## Solid Professional

```text
16 → 63
18 → 67
21 → 70
25 → 73
29 → 72
33 → 68
```

## Late Bloomer

```text
16 → 55
18 → 59
21 → 62
23 → 68
25 → 76
28 → 84
31 → 87
```

## Failed Wonderkid

```text
16 → 68
18 → 73
21 → 74
23 → 72
26 → 69
```

These examples demonstrate the desired variety.

---

# 154. CURRENT ABILITY / POTENTIAL RELATIONSHIP

A player should generally satisfy:

```text
current_ability <= potential
```

for initial generation.

During a career, if circumstances cause unexpected improvement beyond the current potential estimate, the potential system may later be adjusted by a future progression/reassessment mechanism.

Phase 3 does not implement potential reevaluation.

---

# 155. NO GUARANTEED POTENTIAL REALIZATION

Potential is not destiny.

The final career outcome depends on:

```text
Potential
+
Development Rate
+
Age
+
Profile
+
Playing Time
+
Performance
+
Environment
+
Professionalism
+
Fitness
+
Injuries
+
Decisions
+
Randomness
```

---

# 156. FINAL PRODUCT STRATEGY

TikTok is initially the distribution channel.

Football Life is the underlying product.

The simulator should remain useful independently of social media.

---

# 157. FINAL PRODUCT VISION

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

# 158. FINAL DESIGN PRINCIPLE

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

```
```
