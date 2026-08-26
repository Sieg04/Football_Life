# Football Life — PROJECT SPEC

**Version:** 1.5
**Status:** Approved Architecture Specification
**Project:** Football Life
**Primary Goal:** Deterministic football career simulation with emergent player development, competition, match performance and career trajectories.

---

# 1. PROJECT VISION

Football Life is a deterministic football career simulation in which a football player evolves through:

```text
Football World
      ↓
Player
      ↓
Career
      ↓
Competition
      ↓
Match
      ↓
Performance
      ↓
Season
      ↓
Development
      ↓
Next Season
```

The project is designed around independent simulation domains communicating through explicit domain objects.

The system must support:

* deterministic simulation
* reproducible career trajectories
* emergent player development
* contextual match performance
* realistic squad selection
* competition progression
* configurable football rules
* data-driven balancing
* infrastructure-independent simulation logic

The simulation core must never depend directly on:

* FastAPI
* HTTP
* Angular
* SQLAlchemy
* SQLite
* REST
* presentation code

---

# 2. CORE ARCHITECTURAL PRINCIPLES

## 2.1 Domain Independence

Simulation domains contain pure Python objects and calculation functions.

```text
API
 ↓
Application Services
 ↓
Domain Engines
 ↓
Repositories
 ↓
Database
```

Never:

```text
Domain Engine
 ↓
SQLAlchemy
```

Never:

```text
Domain Engine
 ↓
FastAPI
```

---

## 2.2 Determinism

All simulation randomness must use isolated seeded RNG instances.

Never use:

```python
hash(...)
```

Use SHA-256 derived seeds:

```python
seed_material = f"{seed}:{entity_id}:{stage}"
digest = hashlib.sha256(seed_material.encode("utf-8")).hexdigest()
seed_int = int(digest[:16], 16)
rng = random.Random(seed_int)
```

Identical inputs and identical seeds must produce byte-for-byte equivalent serialized outputs across processes.

---

## 2.3 Data-Driven Rules

Balancing constants should be stored in:

```text
backend/data/rules/
```

Examples:

```text
world.json
player_attributes.json
player_development.json
player_roles.json
player_traits.json
player_archetypes.json
career_archetypes.json
competitions.json
competition_formats.json
```

New configurable systems should prefer JSON configuration over hardcoded constants.

---

# 3. DOMAIN STRUCTURE

The project is divided into:

```text
World Domain
Player Domain
Career Domain
Match Domain
Competition Domain
Transfer Domain
Injury Domain
Narrative Domain
Presentation Domain
```

Only approved phases may implement their corresponding domain.

---

# 4. PHASE MAP

```text
Phase 1   Foundation
Phase 2   Football World
Phase 3   Player Engine
Phase 3.1 Player Generation & Balance Refinement
Phase 4   Career Engine
Phase 4.1B Career Archetype Classifier
Phase 5   Match Engine
Phase 6   Competition & Season Engine
Phase 7   Transfer & Contract Engine
Phase 8   Injury & Availability Engine
Phase 9   Club & Manager Ecosystem
Phase 10  Career Events & Narrative
Phase 11  International Career
Phase 12  Presentation / UI
```

---

# 5. PHASE 1 — FOUNDATION

Phase 1 established the backend foundation.

Responsibilities:

* application structure
* database configuration
* SQLAlchemy foundation
* Alembic
* testing infrastructure
* configuration loading
* health checks

The domain engines remain independent from this infrastructure.

---

# 6. PHASE 2 — FOOTBALL WORLD

Phase 2 created the initial football world.

## 6.1 World Entities

```text
Country
League
Club
Manager
Competition
Player
ClubMembership
```

The seed world contains:

* 5 countries
* 5 leagues
* 20 clubs
* 20 managers
* 16 competitions
* 800 generated players
* 800 initial club memberships

---

## 6.2 Club Strength

Club strength is derived from:

* squad quality
* squad depth
* manager quality
* club attributes
* initial world data

Strength calculations remain deterministic.

---

## 6.3 Generic World Players

Generic players are real `Player` domain objects.

They are not a separate football model.

```text
Player
 +
ClubMembership
```

The protagonist also uses:

```text
Player
 +
Career
```

---

# 7. PHASE 3 — PLAYER ENGINE

The Player Engine defines the universal football player.

## 7.1 Player Structure

```text
Player
├── Identity
├── Attributes
├── Positions
├── Current Ability
├── Potential
├── Development Rate
├── Development Profile
├── Role Familiarity
├── Traits
├── Personality
└── Player State
```

---

# 8. INTERNAL PLAYER ATTRIBUTES

Attributes are constrained to:

```text
1–100
```

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

## Goalkeeping

```text
diving
handling
kicking
reflexes
speed
goalkeeper_positioning
```

---

# 9. VISIBLE ATTRIBUTE GROUPS

Visible groups are derived values.

They are not independently stored attributes.

```text
PAC
SHO
PAS
DRI
DEF
PHY
MENTAL
```

Group calculations use configurable weights from:

```text
player_attributes.json
```

---

# 10. CURRENT ABILITY

Current Ability is the player's general football quality.

Formula:

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

Current Ability is position-independent.

---

# 11. POSITION OVR

OVR represents effectiveness in a specific position.

The same attributes can produce different OVRs:

```text
ST 87
CAM 83
CM 76
```

Position changes the evaluation weights, not the attributes.

Goalkeepers use a dedicated goalkeeper calculation.

---

# 12. POTENTIAL

Potential represents theoretical maximum ability.

Constraint:

```text
potential >= current_ability
```

Potential is not a guarantee.

Progression depends on:

* age
* development rate
* development profile
* playing time
* performance
* environment
* professionalism
* player state
* deterministic randomness

---

# 13. DEVELOPMENT RATE

```text
0–30    Very Slow
31–50   Slow
51–70   Normal
71–85   Fast
86–100  Exceptional
```

Development Rate does not directly represent annual CA growth.

---

# 14. DEVELOPMENT PROFILE

Profiles describe the direction of growth.

Examples:

```text
BALANCED
FINISHER
PLAYMAKER
ATHLETIC
DEFENSIVE
TECHNICAL
CREATIVE
PHYSICAL
LATE_BLOOMER
```

Profile coefficients are configured through:

```text
player_development.json
```

---

# 15. ROLE FAMILIARITY

Role Familiarity describes experience and comfort in a role.

It affects:

* role effectiveness
* role fit
* lineup selection
* match performance

It does not directly mutate base attributes.

---

# 16. ROLE ATTRIBUTE FIT

```text
ATTRIBUTE_FIT =
Σ(group_rating × role_weight)
```

Role weights are configurable.

---

# 17. ROLE EFFECTIVENESS

```text
ROLE_EFFECTIVENESS =
    ATTRIBUTE_FIT × 0.70
  + ROLE_FAMILIARITY × 0.30
```

Role Effectiveness does not replace OVR.

---

# 18. TRAITS / PLAYSTYLES

Traits are contextual.

Examples:

```text
FINESSE_SHOT
RAPID
AERIAL
LEADER
CREATIVE
BIG_GAME_PLAYER
COMPOSED
LONG_BALL
```

Traits:

* do not provide flat OVR bonuses
* do not globally alter Current Ability
* activate only in relevant simulation contexts

---

# 19. PERSONALITY

Personality attributes:

```text
ambition
loyalty
professionalism
ego
temper
leadership
sociability
```

Personality is data during Phase 3.

Behavioral consequences are implemented later.

---

# 20. PLAYER STATE

Player State:

```text
confidence
morale
form
fitness
fatigue
happiness
reputation
```

All use:

```text
0–100
```

Player State is temporary state, not permanent football ability.

---

# 21. PHASE 3.1 — PLAYER GENERATION

Generic player generation includes:

* positional archetypes
* attribute specialization
* potential distribution
* secondary positions
* traits
* goalkeeper specialization
* position-specific OVR
* archetype persistence

Generic players must not all have identical attribute distributions.

---

# 22. PHASE 4 — CAREER ENGINE

Phase 4 converts Player into an evolving career.

```text
Player
 ↓
Career
 ↓
Season
 ↓
Development
 ↓
Next Season
```

---

# 23. CAREER DOMAIN

```text
Career
Season
SeasonSnapshot
CareerPhase
SeasonalPlayingTimeInput
SeasonalPerformanceInput
SeasonalEnvironmentInput
```

Career stores:

* player
* current club
* start date
* current season
* career phase
* peak ability
* peak OVR
* peak age
* peak position
* peak club
* season history
* snapshots
* deterministic seed

---

# 24. CAREER PHASES

Strict age-first hierarchy:

```text
YOUTH        <18
EARLY_PRO    18–20
DEVELOPMENT  21–23
PRIME        24–28
LATE_PRIME   29–31
DECLINE      32–34
VETERAN      35+
```

---

# 25. DEVELOPMENT BUDGET

Formula:

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

Current calibrated:

```text
BASE_RATE = 4.0
```

---

# 26. POTENTIAL FACTOR

Baseline:

```text
potential_gap =
max(0, potential - current_ability)
```

The potential conversion curve remains data-driven through:

```text
player_development.json
```

---

# 27. AGE FACTOR

Configured baseline:

```text
16–18  = 1.40
19–21  = 1.25
22–24  = 1.10
25–27  = 0.85
28–30  = 0.60
31–33  = 0.35
34+    = 0.10
```

The active season uses the player's starting age.

---

# 28. TWO-STAGE DEVELOPMENT

Stage 1:

```text
Development Budget
        ↓
PAC / SHO / PAS / DRI / DEF / PHY / MENTAL
```

weighted by Development Profile.

Stage 2:

```text
Group Budget
        ↓
Internal Attributes
```

Stage 2 uses normalized internal attribute weights so that group budget represents average internal group growth.

---

# 29. SOFT CAPS

```text
<80   = 1.00
80–89 = 0.85
90–94 = 0.60
95–97 = 0.30
98+   = 0.10
```

---

# 30. DECLINE

Physical decline dominates technical decline.

Physical:

```text
acceleration
sprint_speed
agility
stamina
jumping
reactions
```

Technical decline is weaker.

Mental decline is zero or near-zero.

Veteran players can therefore evolve toward:

```text
lower pace
+
retained intelligence
+
retained passing
+
retained composure
```

---

# 31. PHASE 4.1B — CAREER ARCHETYPE CLASSIFIER

Career archetypes are multi-label.

Tags:

```text
LONG_PRIME
WONDERKID
FAILED_WONDERKID
SUPERSTAR
LATE_BLOOMER
EARLY_DECLINER
SOLID_PRO
```

The classifier produces:

```text
tags
+
evidence
```

Rules are data-driven through:

```text
career_archetypes.json
```

Approved thresholds include:

```text
WONDERKID:
starting_age <= 17
starting_ca >= 78.36
potential >= 87.23

FAILED_WONDERKID:
starting_age <= 17
potential >= 87.23
potential_realization <= 82%

SUPERSTAR:
peak_ovr >= 88

LONG_PRIME:
peak_age >= 27
seasons_within_98_pct >= 19

LATE_BLOOMER:
peak_age >= 28
post_age_24_ca_growth >= 1.5

EARLY_DECLINER:
peak_age <= 29
peak_to_final_ca_decline >= 3
```

---

# 32. PHASE 5 — MATCH ENGINE

Phase 5 creates the football performance loop.

```text
Lineup
 ↓
Match Resolution
 ↓
Player Performance
 ↓
Season Aggregation
 ↓
Career Engine
```

---

# 33. MATCH DOMAIN

Main objects:

```text
SimulationMode
CompetitionType
MatchEventType
MatchContext
PlayerMatchPerformance
MatchEvent
MatchResult
```

Simulation modes:

```text
FAST
DETAILED
```

---

# 34. MATCH CONTEXT

MatchContext contains:

```text
match_id
home_club_id
away_club_id
competition_type
competition_importance
home_advantage_points
match_importance
rivalry_factor
seed
simulation_mode
```

Validation is strict.

---

# 35. LINEUP ENGINE

Supported formations:

```text
4-3-3
4-2-3-1
4-4-2
3-5-2
3-4-3
4-1-4-1
```

Selection uses:

```text
OVR
+
Role Effectiveness
+
Form
+
Fitness
+
Manager preference
```

---

# 36. EFFECTIVE TEAM STRENGTH

```text
effective_strength =
    XI_quality × 0.65
  + club_strength × 0.15
  + manager_quality × 0.05
  + tactical_fit × 0.05
  + form_factor × 0.05
  + fitness_factor × 0.05
```

XI Quality:

```text
GK = 10%
DEF = 30%
MID = 30%
ATT = 30%
```

---

# 37. MODEL D — MINUTES ALLOCATION

Model D solves the zero-minute feedback loop.

## Youth Bonus

```text
youth_bonus =
    (manager.youth_preference / 100)
  × max(0, (22 - age) / 5)
  × ((100 - competition_importance) / 100)
  × MAX_YOUTH_BONUS
```

Defaults:

```text
Starter bonus = 3
Bench bonus = 12
```

## Rotation Bonus

```text
rotation_bonus =
    (manager.rotation / 100)
  × ((100 - competition_importance) / 100)
  × (1 - min(season_minutes, 3000) / 3000)
  × MAX_ROTATION_BONUS
```

Default:

```text
MAX_ROTATION_BONUS = 10
```

The system never guarantees youth minutes.

---

# 38. SUBSTITUTE PRIORITY

```text
sub_priority_score =
    OVR × 0.40
  + role_effectiveness × 0.20
  + form × 0.15
  + fitness × 0.15
  + youth_bonus
  + rotation_bonus
```

Substitution candidates use seeded weighted stochastic selection.

Requirements:

* no duplicate candidate
* max configured substitutions
* high importance favors strongest options
* low importance increases rotation/youth opportunity
* deterministic result for identical seeds

---

# 39. MATCH RESOLUTION

Goals are generated directly from Poisson distributions.

```text
goals ~ Poisson(xG)
```

No independent W/D/L sampling is used.

---

# 40. XG FORMULA

Current calibrated exponent:

```text
1.10
```

Conceptually:

```text
home_xG =
1.35
× (home_strength / away_strength)^1.10
× variance_modifier
```

Away:

```text
away_xG =
1.15
× (away_strength / home_strength)^1.10
× variance_modifier
```

Clamp:

```text
0.15 ≤ xG ≤ 4.50
```

---

# 41. POISSON SAMPLING

Deterministic Knuth sampling uses SHA-256 seeded `random.Random`.

---

# 42. MATCH PERFORMANCE

Performance engine calculates:

* latent influence
* attacking chances
* shots
* shots on target
* goals
* assists
* defensive actions
* saves
* minutes
* substitutions
* contextual ratings

---

# 43. GOAL DISTRIBUTION

Current positional priorities:

```text
ST            1.35
LW / RW       1.10
CAM / AM      1.00
LM / RM       0.85
CM            0.70
DM            0.45
CB / LB / RB  0.20
GK            0.01
```

Goal assignment uses seeded weighted stochastic sampling.

Repeat goals apply diminishing returns:

```text
0.70^k
```

---

# 44. ASSISTS

Assist priorities favor:

```text
CAM / AM
LW / RW
LM / RM
CM
DM
ST
FB / WB
CB
GK
```

Self-assists are impossible.

---

# 45. MATCH RATINGS

Match rating is contextual.

Examples:

```text
ST  → goals, shots, conversion
CAM → key passes, assists, progression
CB  → tackles, interceptions, clearances
GK  → saves, goals prevented
```

Clamp:

```text
1.0–10.0
```

---

# 46. SEASON AGGREGATION

SeasonPerformance aggregates:

```text
appearances
starts
substitute_appearances
minutes_played
goals
assists
shots
shots_on_target
key_passes
tackles
interceptions
clearances
clean_sheets
average_rating
performance_factor
playing_time_factor
```

---

# 47. PERFORMANCE FACTOR

```text
performance_factor =
clamp(
    1 + (average_rating - 6.8) / 10,
    0.80,
    1.20
)
```

---

# 48. PLAYING TIME FACTOR

```text
0–300      = 0.30
301–750    = 0.55
751–1400   = 0.80
1401–2200  = 1.00
2201–3000  = 1.05
3000+      = 1.00
```

---

# 49. PHASE 5F — CAREER INTEGRATION

Match output flows into Career Engine:

```text
Match
 ↓
PlayerMatchPerformance
 ↓
SeasonPerformance
 ↓
Seasonal Performance Input
 ↓
Career Engine
 ↓
Development
```

The Match Engine never duplicates development calculations.

---

# 50. FAST VS DETAILED

Fast Mode provides:

* score
* xG
* essential statistics
* summary player outputs

Detailed Mode provides:

* micro-events
* chance logs
* detailed performance
* substitutions
* event metadata

Both use the same core resolution semantics.

---

# 51. PHASE 5 VALIDATION

Phase 5 must maintain:

* exact score/action invariants
* deterministic seeds
* no infrastructure coupling
* no development logic duplication
* bounded ratings
* bounded xG
* plausible football distributions

---

# 52. PHASE 6 — COMPETITION & SEASON ENGINE

Phase 6 introduces the competition structure that connects individual matches into complete football seasons.

Phase 6 exists because the Match Engine can simulate individual matches but does not own:

* fixture sequencing
* competition progression
* standings
* form tables
* season lifecycle

Phase 6 creates this layer.

---

# 53. PHASE 6 ARCHITECTURE

```text
Competition Domain
        ↓
Competition Season
        ↓
Fixture Generator
        ↓
Match Engine
        ↓
Match Results
        ↓
Standings
        ↓
Form
        ↓
Season Progression
        ↓
Career Context
```

---

# 54. PHASE 6 RESPONSIBILITIES

Phase 6 owns:

```text
Competition
CompetitionSeason
CompetitionStage
CompetitionParticipant
Fixture
FixtureRound
Standing
FormRecord
SeasonCompetitionResult
SeasonSimulation
```

Phase 6 does not own:

```text
transfers
contracts
injuries
relationships
narrative
economy
presentation
```

---

# 55. COMPETITION DOMAIN

The domain defines:

```text
CompetitionType
CompetitionFormat
CompetitionStageType
CompetitionSeasonStatus
Competition
CompetitionSeason
CompetitionParticipant
CompetitionStage
```

Competition types:

```text
LEAGUE
DOMESTIC_CUP
EUROPEAN
INTERNATIONAL
```

Formats:

```text
ROUND_ROBIN
SINGLE_ELIMINATION
TWO_LEG_ELIMINATION
LEAGUE_PHASE
```

---

# 56. COMPETITION

A Competition contains:

```text
id
name
competition_type
country_id
importance
level
format
participant_count
rules
```

Validation:

* non-empty ID
* non-empty name
* importance `0–100`
* level positive
* participant count >= 2

Competition rules must be data-driven.

---

# 57. COMPETITION SEASON

A CompetitionSeason represents one competition instance in one football season.

```text
id
competition_id
season_label
start_date
end_date
participants
stages
current_stage_index
status
winner_id
seed
```

Status:

```text
NOT_STARTED
ACTIVE
COMPLETED
```

Validation must ensure:

* valid dates
* at least two participants
* unique participant clubs
* participant season IDs match
* unique stage IDs
* stage season IDs match
* non-empty seed

---

# 58. COMPETITION PARTICIPANT

```text
competition_season_id
club_id
seed
```

Validation:

* valid season ID
* positive club ID
* non-empty seed

No database lookup is performed in the domain.

---

# 59. COMPETITION STAGE

```text
id
competition_season_id
stage_type
stage_number
participant_club_ids
completed
```

Validation:

* non-empty ID
* valid season ID
* stage number >= 1
* at least two participant clubs
* no duplicate participant clubs

Stage progression is implemented later in 6D.

---

# 60. FIXTURE DOMAIN

A Fixture contains:

```text
fixture_id
competition_season_id
stage_id
round_number
home_club_id
away_club_id
scheduled_date
match_importance
competition_importance
rivalry_factor
status
match_id
```

Status initially:

```text
SCHEDULED
PLAYED
```

Future states may include:

```text
POSTPONED
CANCELLED
```

---

# 61. FIXTURE & CALENDAR ENGINE

Stage 6B owns deterministic fixture generation.

Inputs:

```text
participants
competition format
rules
start date
season seed
```

Outputs:

```text
ordered fixtures
```

Identical inputs must always generate identical fixtures.

---

# 62. ROUND-ROBIN FIXTURE GENERATION

For a standard double round-robin:

```text
matches_per_club =
2 × (participant_count - 1)
```

For 20 clubs:

```text
38 matches per club
380 total matches
```

Requirements:

* every pairing exactly twice
* one home match
* one away match
* deterministic round ordering

---

# 63. ODD PARTICIPANT COUNTS

Odd participant counts must be supported using a temporary bye slot.

The bye:

* is never persisted as a club
* does not create a fixture
* does not affect standings

---

# 64. HOME / AWAY BALANCE

Fixture generation should minimize:

* excessive consecutive home matches
* excessive consecutive away matches

Exact scheduling optimization must remain deterministic.

---

# 65. CALENDAR DATES

Default league interval:

```text
7 days
```

Cup and European intervals are configurable.

Phase 6 does not attempt to reproduce real-world fixture calendars.

---

# 66. MATCH IMPORTANCE

Phase 6 calculates contextual importance from:

```text
competition importance
stage importance
rivalry factor
standings context
```

Initial baseline examples:

```text
League         50
Domestic Cup   55
European       70
Final          95
```

Clamp:

```text
0–100
```

---

# 67. STANDINGS ENGINE

StandingEntry:

```text
club_id
played
wins
draws
losses
goals_for
goals_against
goal_difference
points
```

Default points:

```text
win  = 3
draw = 1
loss = 0
```

---

# 68. STANDINGS UPDATE

Input:

```text
MatchResult
```

Output:

```text
updated standings
```

Update:

1. played
2. goals
3. result
4. goal difference
5. points
6. ranking

---

# 69. STANDINGS ORDER

Default:

```text
points DESC
goal_difference DESC
goals_for DESC
deterministic_tiebreak
```

Default deterministic tiebreak may use `club_id` until competition-specific head-to-head rules exist.

---

# 70. FORM ENGINE

Track recent completed matches.

Default window:

```text
5 matches
```

Form stores:

```text
wins
draws
losses
goals_for
goals_against
points
results
```

Results:

```text
W
D
L
```

Form can be passed to Match Engine as context.

Phase 6 must not duplicate Match Engine form calculations.

---

# 71. COMPETITION PROGRESSION

Phase 6D handles stage progression.

## League

```text
fixture completed
↓
standings updated
↓
next fixture
```

Competition is complete when all fixtures are played.

Winner:

```text
rank 1
```

---

# 72. SINGLE ELIMINATION

Example:

```text
16 teams
 ↓
Round of 16
 ↓
Quarter-final
 ↓
Semi-final
 ↓
Final
```

Winners advance.

Eliminated teams stop participating.

---

# 73. TWO-LEG TIES

Two-leg competitions aggregate:

```text
Leg 1
+
Leg 2
↓
Aggregate Score
↓
Winner
```

Initial defaults:

* no away-goals rule
* extra time configurable
* penalties configurable
* replay configurable

---

# 74. DRAW RESOLUTION

When a competition requires a winner:

```text
DRAW_ALLOWED
EXTRA_TIME
PENALTIES
REPLAY
```

These are Competition rules.

Match Engine remains responsible only for normal match resolution.

---

# 75. CUP COMPETITIONS

Cup rules may support:

* single elimination
* two-leg rounds
* replays
* home/away rules
* extra time
* penalties

Exact rules are data-driven.

---

# 76. EUROPEAN COMPETITIONS

Initial Phase 6 does not need to reproduce real-world UEFA formats exactly.

Generic support is sufficient for:

```text
league phase
qualification
knockout
```

Real-world fixture replication is explicitly out of scope.

---

# 77. SEASON ORCHESTRATOR

Phase 6E performs a complete competition season.

Conceptual flow:

```text
Initialize Competition Season
        ↓
Generate Fixtures
        ↓
For each fixture:
    Create MatchContext
    Select Lineups
    Resolve Match
    Generate Player Performances
    Aggregate Results
    Update Standings
    Update Form
        ↓
Competition Complete
        ↓
Determine Winner
```

---

# 78. MATCH ENGINE BOUNDARY

Phase 6 calls Match Engine.

Phase 6 must not duplicate:

* xG formulas
* Poisson sampling
* lineup selection
* role effectiveness
* player ratings
* goal allocation
* player development

---

# 79. SEASON PERFORMANCE BOUNDARY

Phase 5E remains responsible for:

```text
SeasonPerformance
performance_factor
playing_time_factor
```

Phase 4 remains responsible for:

```text
development budget
attribute growth
age curve
decline
```

---

# 80. GLOBAL SEASON STATE

The future global season runner should be able to track:

```text
season_label
current_date
current_fixture_index
competition_states
completed_competitions
```

This may coordinate multiple competitions.

---

# 81. PHASE 6 DOMAIN STRUCTURE

Recommended:

```text
backend/app/competition/
├── __init__.py
├── domain.py
├── fixtures.py
├── calendar.py
├── standings.py
├── form.py
├── progression.py
├── season.py
└── orchestrator.py
```

All core calculations remain pure.

---

# 82. PHASE 6 PERSISTENCE

Persistence is external to the pure engine.

Potential models:

```text
CompetitionModel
CompetitionSeasonModel
CompetitionParticipantModel
CompetitionStageModel
FixtureModel
StandingModel
```

Existing models should be reused where appropriate.

Do not duplicate:

```text
ClubModel
PlayerModel
ManagerModel
MatchModel
```

---

# 83. PHASE 6 REPOSITORIES

Potential repository layer:

```text
CompetitionRepository
CompetitionSeasonRepository
FixtureRepository
StandingRepository
```

Repositories perform:

* domain ↔ ORM mapping
* load
* save
* transactional persistence

Repositories must not contain simulation formulas.

---

# 84. PHASE 6 CONFIGURATION

Recommended files:

```text
backend/data/rules/competitions.json
backend/data/rules/competition_formats.json
```

Configuration includes:

* point systems
* participant counts
* round counts
* home/away rules
* stage structures
* knockout rules
* importance levels
* tie-break rules
* calendar intervals

---

# 85. PHASE 6 TESTING

## 85.1 6A Competition Domain

Tests:

* valid Competition
* invalid Competition
* valid Participant
* invalid Participant
* valid Stage
* duplicate stage participants
* valid CompetitionSeason
* invalid dates
* duplicate clubs
* mismatched season IDs
* enum values
* immutable equality
* zero infrastructure imports

Target:

```text
20–30 tests
```

---

## 85.2 6B Fixtures

Tests:

* deterministic round-robin
* 20-team 380 fixture validation
* every pairing exactly twice
* home/away balance
* odd participant handling
* round count
* date progression

---

## 85.3 6C Standings and Form

Tests:

* points
* goals
* goal difference
* rankings
* tie-breaks
* five-match form window
* deterministic ordering
* input-order independence

---

## 85.4 6D Progression

Tests:

* knockout advancement
* elimination
* bracket integrity
* two-leg aggregate
* draw resolution
* winner determination
* deterministic progression

---

## 85.5 6E Season Orchestrator

Tests:

* complete league
* complete cup
* Match Engine integration
* standings progression
* form progression
* season winner
* deterministic full-season replay
* Phase 4/5 regression

---

# 86. PHASE 6 STATISTICAL AUDITS

## Audit A — Fixture Audit

100 competitions.

Measure:

* duplicated pairings
* home/away balance
* consecutive home/away streaks
* fixture coverage
* rounds

## Audit B — League Audit

100 complete league seasons.

Measure:

* winner distribution
* points distribution
* wins/draws/losses
* goals
* table concentration

## Audit C — Full Season Audit

100 complete world seasons.

Measure:

* total fixtures
* total goals
* average points
* champion diversity
* form distribution
* player minutes
* player performance
* development impact

---

# 87. PHASE 6 DETERMINISM

Must verify:

```text
same participants
+
same rules
+
same season seed
=
same fixtures
+
same match contexts
+
same results
+
same standings
+
same winner
```

Cross-process determinism is mandatory.

---

# 88. PHASE 6 ACCEPTANCE CRITERIA

Phase 6 is complete when:

```text
[ ] Competition domain validated
[ ] Fixtures deterministic
[ ] No duplicate fixtures
[ ] Home/away balanced
[ ] Standings mathematically correct
[ ] Form correctly maintained
[ ] Knockout progression correct
[ ] Complete league season works
[ ] Complete cup season works
[ ] Match Engine integration works
[ ] Career Engine integration remains intact
[ ] Cross-process deterministic
[ ] No infrastructure leaks in pure domain
[ ] All previous tests remain green
```

---

# 89. PHASE 6 NON-GOALS

Do not implement:

```text
Transfers
Contracts
Persistent Injuries
Relationships
Narrative
Economy
Sponsorship
Board System
International Player Selection
Media System
Presentation Mode
Advanced Tactical AI
Full Real-World Fixture Replication
```

---

# 90. PHASE 7 — TRANSFER & CONTRACT ENGINE

Deferred.

Phase 7 will depend on:

* competition performance
* player reputation
* club attractiveness
* squad needs
* contract status
* market value
* playing time

Phase 7 must not be implemented during Phase 6.

---

# 91. PHASE 8 — INJURY & AVAILABILITY ENGINE

Deferred.

Potential inputs:

* fatigue
* minutes
* physical profile
* match load

No persistent injury simulation belongs to Phase 6.

---

# 92. PHASE 9 — CLUB & MANAGER ECOSYSTEM

Deferred.

Potential systems:

* manager changes
* club objectives
* club philosophy
* youth academy
* board expectations

---

# 93. PHASE 10 — CAREER EVENTS & NARRATIVE

Deferred.

Potential systems:

* relationships
* media
* morale events
* career decisions
* narrative events

---

# 94. PHASE 11 — INTERNATIONAL CAREER

Deferred.

Potential systems:

* national selection
* international tournaments
* national team reputation

---

# 95. PHASE 12 — PRESENTATION

Deferred.

Presentation must consume simulation results.

Presentation must never alter simulation logic.

---

# 96. TEST POLICY

Every phase must preserve all previous tests.

Full regression command:

```bash
PYTHONPATH=backend python3 -m pytest backend/tests
```

No phase is complete with failing previous tests.

---

# 97. AUDIT POLICY

Large Monte Carlo audits should be staged:

```text
10
 ↓
100
 ↓
500
 ↓
1000+
```

Never begin with a massive audit before verifying a single deterministic pipeline.

---

# 98. VALIDATION POLICY

For every engine:

1. unit tests
2. deterministic tests
3. structural independence tests
4. targeted behavioral audit
5. larger statistical audit
6. full regression suite

---

# 99. FAILURE DEBUGGING POLICY

When an audit fails:

```text
single entity
 ↓
single season
 ↓
small population
 ↓
large population
```

Do not immediately modify formulas.

First identify:

* exact exception
* exact input
* exact function
* exact domain state

---

# 100. CURRENT APPROVED PROJECT STATUS

```text
Phase 1        COMPLETE
Phase 2        COMPLETE
Phase 3        COMPLETE
Phase 3.1      COMPLETE
Phase 4        COMPLETE
Phase 4.1B     COMPLETE
Phase 5        COMPLETE
Model D        COMPLETE
Phase 6        APPROVED / NOT IMPLEMENTED
Phase 7        DEFERRED
Phase 8        DEFERRED
Phase 9        DEFERRED
Phase 10       DEFERRED
Phase 11       DEFERRED
Phase 12       DEFERRED
```

---

# 101. NEXT IMPLEMENTATION TARGET

The next implementation target is:

```text
PHASE 6 — COMPETITION & SEASON ENGINE
```

Recommended implementation order:

```text
6A Competition Domain
        ↓
6B Fixture & Calendar Engine
        ↓
6C Standings & Form Engine
        ↓
6D Competition Progression
        ↓
6E Season Orchestrator
```

Each sub-stage must be implemented and audited independently.

---

# 102. FIRST IMPLEMENTATION TASK

The immediate implementation target is:

```text
PHASE 6A — COMPETITION DOMAIN
```

Only create:

```text
backend/app/competition/__init__.py
backend/app/competition/domain.py
backend/tests/test_competition_domain.py
```

unless a minimal pure configuration adjustment is strictly necessary.

Do not implement:

* fixture generation
* calendar generation
* standings
* form engine
* progression
* season orchestration
* Match Engine integration
* Career Engine integration
* persistence
* SQLAlchemy
* Alembic
* repositories

Stop after 6A.

---

# 103. FINAL ARCHITECTURAL RULE

The simulation must preserve this dependency direction:

```text
World
 ↓
Player
 ↓
Career
 ↓
Competition
 ↓
Match
 ↓
Performance
 ↓
Season Aggregation
 ↓
Development
```

Future systems may consume information from earlier systems but must not duplicate their internal rules.

The ultimate goal is a deterministic, modular football world where careers emerge from the interaction between:

```text
player ability
+
player state
+
manager decisions
+
competition context
+
match performance
+
development
+
season progression
```

rather than from scripted career outcomes.

---

**END OF PROJECT SPEC v1.5**
