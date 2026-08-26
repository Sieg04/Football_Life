# Football Life — PROJECT SPEC

**Version:** 1.5
**Status:** Approved Architecture Specification
**Project:** Football Life
**Primary Goal:** Deterministic football career simulation with emergent player development, competition, performance and career trajectories.

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

The project is designed around independent simulation domains that communicate through explicit domain objects.

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

Attributes are integer-like values constrained to:

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

```python
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

Current baseline:

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

Current approved thresholds include:

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

Approved defaults:

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

Repeat goals apply diminishing return:

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

```text 1.0–10.0
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

Phase 6 exists because the current Match Engine can simulate individual matches but does not yet own:

* fixture sequencing
* competition progression
* standings
* form tables
* season lifecycle
* tournament progression

Phase 6 creates that layer.

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
Season Performance
        ↓
Career Engine
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

The domain must define:

```text
CompetitionType
CompetitionFormat
CompetitionStageType
Competition
CompetitionSeason
CompetitionParticipant
```

Competition types include:

```text
LEAGUE
DOMESTIC_CUP
EUROPEAN
INTERNATIONAL
```

Formats must be configurable.

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

Competition definitions must be data-driven.

---

# 57. COMPETITION SEASON

A CompetitionSeason represents one competition instance in a given football season.

```text
id
competition_id
season_label
start_date
end_date
participants
stages
status
winner_id
```

---

# 58. COMPETITION PARTICIPANT

Participant object:

```text
club_id
competition_season_id
seed
status
```

Participant status may include:

```text
ACTIVE
ELIMINATED
CHAMPION
```

---

# 59. COMPETITION STAGES

Examples:

```text
REGULAR_SEASON
GROUP_STAGE
LEAGUE_PHASE
ROUND_OF_32
ROUND_OF_16
QUARTER_FINAL
SEMI_FINAL
FINAL
```

Stage definitions must be configurable.

---

# 60. FIXTURE DOMAIN

Fixture contains:

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
status
match_id
```

---

# 61. FIXTURE GENERATION

Fixture generation must be deterministic.

Input:

```text
competition participants
competition format
season seed
```

Output:

```text
ordered fixture list
```

Identical inputs must produce identical fixtures.

---

# 62. LEAGUE FIXTURE GENERATION

Standard league scheduling should support:

* home/away balancing
* round-robin scheduling
* fixed participant count
* deterministic round ordering
* no duplicate pairing in the same half-season
* configurable number of rounds

For a standard double round-robin:

```text
matches_per_club =
2 × (participant_count - 1)
```

---

# 63. HOME / AWAY BALANCE

Fixture generation should minimize:

```text
consecutive home matches
consecutive away matches
```

Subject to the configured competition format.

---

# 64. COMPETITION IMPORTANCE

Fixture importance is generated from context.

Inputs may include:

```text
competition importance
stage importance
league position
title race proximity
relegation race proximity
rivalry factor
knockout status
```

Phase 6 may calculate contextual match importance.

Phase 6 must not duplicate Match Engine resolution.

---

# 65. STANDINGS

League standings must maintain:

```text
played
wins
draws
losses
goals_for
goals_against
goal_difference
points
```

Standard points:

```text
win  = 3
draw = 1
loss = 0
```

---

# 66. STANDINGS ORDER

Default ordering:

```text
points DESC
goal_difference DESC
goals_for DESC
deterministic_tiebreak
```

Competition-specific ordering can override this through configuration.

---

# 67. STANDINGS UPDATE

After every completed league fixture:

```text
MatchResult
 ↓
Validate
 ↓
Update home club
Update away club
 ↓
Recompute ranking
```

Standings must be deterministic.

---

# 68. FORM ENGINE

Recent form tracks previous results.

Default form window:

```text
last 5 matches
```

Form can include:

```text
wins
draws
losses
goals_for
goals_against
points
```

Form is exposed to Match Engine context.

---

# 69. SEASON ORCHESTRATOR

The Season Orchestrator executes a competition season.

Conceptual flow:

```text
initialize competition season
        ↓
generate fixtures
        ↓
for fixture:
    create MatchContext
    select lineups
    resolve match
    generate performances
    aggregate results
    update standings
    update form
        ↓
competition complete
        ↓
determine winner
```

---

# 70. MATCH ENGINE BOUNDARY

Phase 6 must call:

```text
Match Engine
```

It must not reproduce:

* xG formulas
* Poisson sampling
* lineup selection
* player rating formulas
* development formulas

---

# 71. SEASON PERFORMANCE BOUNDARY

Phase 6 produces match results and season context.

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
aging
decline
```

---

# 72. COMPETITION PROGRESSION

For knockout competitions:

```text
Stage
 ↓
Generate pairings
 ↓
Play fixtures
 ↓
Determine winners
 ↓
Generate next stage
```

Knockout ties may be:

```text
single_leg
two_leg
```

according to configuration.

---

# 73. DRAW HANDLING

If a competition requires a winner and the match ends drawn:

Phase 6 may invoke competition-specific resolution:

```text
extra_time
penalties
replay
```

This must be a Competition rule, not hardcoded into Match Engine.

---

# 74. CUP COMPETITIONS

Cup rules must support:

* single elimination
* optional two-leg rounds
* configured replays
* configured home/away rules
* configured extra time
* configured penalties

---

# 75. EUROPEAN COMPETITIONS

The initial implementation does not need to reproduce real-world competition formats exactly.

The system should support generic configurable forms such as:

```text
league phase
qualification stage
knockout rounds
```

Exact real-world scheduling is not required in Phase 6.

---

# 76. INTERNATIONAL COMPETITIONS

International competitions use the same competition abstractions.

However, international squad selection is outside Phase 6.

Phase 6 can operate on provided participants.

---

# 77. SEASON STATE

The Season Engine should maintain:

```text
season_label
current_date
current_fixture_index
competition_states
completed_competitions
```

---

# 78. GLOBAL SEASON ORCHESTRATION

A future WorldSeason runner can coordinate:

```text
league fixtures
cup fixtures
European fixtures
international fixtures
```

without changing Match Engine formulas.

---

# 79. MATCH IMPORTANCE FROM STANDINGS

Phase 6 may derive contextual importance.

Examples:

```text
title deciding match
relegation battle
European qualification
cup final
semi-final
dead-rubber
```

This modifies MatchContext.

It does not modify Match Resolution mathematics directly.

---

# 80. PLAYER CONTEXT

Competition results may indirectly affect:

```text
player form
player reputation
career evaluation
future selection
```

but Phase 6 must not implement transfer or narrative systems.

---

# 81. PHASE 6 DOMAIN STRUCTURE

Recommended:

```text
backend/app/competition/
├── __init__.py
├── domain.py
├── formats.py
├── fixtures.py
├── standings.py
├── form.py
└── season.py
```

Core engine remains pure.

---

# 82. PHASE 6 PERSISTENCE

Persistence belongs outside the pure competition engine.

Potential tables:

```text
competitions
competition_seasons
competition_participants
competition_stages
fixtures
standings
```

Existing tables should be reused where appropriate.

No duplication of:

```text
clubs
players
managers
matches
```

---

# 83. PHASE 6 REPOSITORIES

Possible repository layer:

```text
CompetitionRepository
FixtureRepository
StandingRepository
SeasonRepository
```

Repositories translate between domain and SQLAlchemy.

---

# 84. PHASE 6 CONFIGURATION

Recommended configuration:

```text
backend/data/rules/competitions.json
backend/data/rules/competition_formats.json
```

Configuration should contain:

* point systems
* stage structures
* participant counts
* round counts
* knockout rules
* importance levels
* tie-breaking rules

---

# 85. PHASE 6 TESTING

Phase 6 must include unit tests for:

## Competition Domain

* valid Competition
* valid CompetitionSeason
* stage validation
* participant validation

## Fixtures

* deterministic generation
* no duplicate pairings
* home/away balance
* correct round count
* correct participant count

## Standings

* points
* goals
* goal difference
* ranking
* tie-breaks

## Form

* last five results
* deterministic ordering
* points calculation

## Knockouts

* stage progression
* winner advancement
* elimination

## Season Orchestration

* complete league season
* complete cup
* complete competition
* correct final standings
* correct winner

---

# 86. PHASE 6 DETERMINISM TESTS

Tests must verify:

```text
same competition seed
+
same participants
+
same rules
=
identical fixture list
```

and:

```text
same fixture seed
=
identical season result
```

Cross-process determinism must be verified.

---

# 87. PHASE 6 STATISTICAL AUDITS

Large audits should measure:

```text
home/away balance
fixture distribution
points distribution
wins/draws/losses
goals
standings concentration
```

No competitive balance correction should be hardcoded without empirical evidence.

---

# 88. PHASE 6 ACCEPTANCE CRITERIA

Phase 6 is complete when:

* a league can generate a complete fixture list
* all fixtures resolve through Match Engine
* standings update correctly
* form updates correctly
* a winner is determined
* match importance can be derived contextually
* complete season results are deterministic
* Phase 1–5 tests remain green
* no infrastructure leaks into pure competition domain

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
Media
International player selection
Presentation Mode
Full real-world fixture replication
Advanced tactical AI
```

---

# 90. PHASE 7 — TRANSFER & CONTRACT ENGINE

Deferred.

Phase 7 will eventually depend on:

* competition performance
* player reputation
* club attractiveness
* squad needs
* contract state
* market value

Phase 7 must not be implemented during Phase 6.

---

# 91. PHASE 8 — INJURY & AVAILABILITY ENGINE

Deferred.

Potential inputs:

```text fatigue
minutes
physical profile
match load
```

No persistent injury simulation is part of Phase 6.

---

# 92. PHASE 9 — CLUB & MANAGER ECOSYSTEM

Deferred.

Potential systems:

```text manager changes
club objectives
club philosophy
youth academy
board expectations
```

---

# 93. PHASE 10 — CAREER EVENTS & NARRATIVE

Deferred.

Potential systems:

```text events
relationships
media
morale
career decisions
```

---

# 94. PHASE 11 — INTERNATIONAL CAREER

Deferred.

Potential systems:

```text national selection
international tournaments
national team reputation
```

---

# 95. PHASE 12 — PRESENTATION

Deferred.

Presentation must consume simulation results.

Presentation must not alter simulation logic.

---

# 96. TEST POLICY

Every phase must preserve all previous tests.

Full regression command:

```bash
PYTHONPATH=backend python3 -m pytest backend/tests
```

No phase is considered complete with failing previous tests.

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
6. regression suite

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

# 102. FINAL ARCHITECTURAL RULE

The simulation must always preserve this dependency direction:

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

Future systems may consume information from earlier systems, but must not duplicate their internal rules.

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

**END OF PROJECT SPEC v1.5**
