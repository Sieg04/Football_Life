# FOOTBALL LIFE

## PHASE 17 — REAL FOOTBALL WORLD & COMPETITION ENGINE

**Specification Version:** 1.0
**Project:** Football Life
**Phase:** 17
**Phase Name:** Real Football World & Competition Engine
**Status:** Design Specification
**Primary Objective:** Transform the existing career simulation from an event-driven progression system into a coherent football career simulation based on real football structures, competitions, matches, seasons, statistics, international football, injuries, trophies, and awards.

---

# 1. PHASE OBJECTIVE

Phase 17 introduces the football-world and competition layer required for Football Life to produce believable, complete football careers.

The current system can already:

* create a player;
* create a career session;
* advance seasons;
* generate events;
* record career history;
* generate narrative;
* generate scripts;
* generate presentation data;
* display the career visually;
* generate replay/content structures.

However, the first real career test revealed a fundamental limitation:

> The career currently does not contain enough football information to feel like a real football career.

Examples of missing or insufficient information include:

* goals;
* assists;
* competition participation;
* league positions;
* match results;
* European campaigns;
* domestic cups;
* international football;
* injuries;
* trophies;
* seasonal statistical summaries;
* meaningful match history.

Phase 17 addresses this problem.

The objective is **not** to create a Football Manager clone.

Football Life should remain:

> **A player-focused football career simulator and story-generation engine.**

The simulation should generate enough football context to make the protagonist's career believable and narratively interesting without simulating every tactical or managerial detail.

---

# 2. CORE DESIGN PRINCIPLE

The central principle of Phase 17 is:

> **Simulate the football world around the protagonist, not every detail of the football world.**

The engine should answer:

* Where does the player play?
* What competition is he playing in?
* How many matches does he play?
* How does he perform?
* Does his club win?
* Does he suffer injuries?
* Does he get selected internationally?
* Does he transfer?
* Does he win trophies?
* How does his career evolve?

The engine does NOT need to answer:

* exact tactical formations for every club;
* every player's complete career;
* every substitution in every match;
* detailed club finances;
* transfer negotiations between every club;
* real-time tactical decisions;
* individual player AI for the entire football world.

---

# 3. PHASE 17 SCOPE

## 3.1 Included

Phase 17 includes:

1. Real football-world data structures.
2. Countries.
3. National teams.
4. Leagues.
5. Clubs.
6. Competitions.
7. Competition seasons.
8. Competition participation.
9. League tables.
10. Fixtures.
11. Match simulation.
12. Player match performance.
13. Seasonal statistics.
14. Domestic cups.
15. Continental competitions.
16. International competitions.
17. International call-ups.
18. Injuries and missed matches.
19. Trophies.
20. Awards.
21. Season summaries.
22. Career statistical aggregation.
23. Integration with the existing Career Engine.
24. Integration with Phase 9 career history.
25. Integration with Phase 10 narrative generation.
26. Integration with Phase 12 presentation.
27. Integration with Phase 13 UI.
28. Integration with Phase 14 career sessions.
29. Integration with Phase 16 replay/content systems.

---

# 4. EXPLICIT NON-GOALS

Phase 17 MUST NOT introduce:

* tactical match control;
* real-time match simulation;
* 3D matches;
* Football Manager-style club management;
* detailed club finances;
* staff management;
* training-session management;
* youth academy management;
* scouting systems;
* fully simulated careers for thousands of players;
* online multiplayer;
* cloud infrastructure;
* external APIs required at runtime;
* automatic video generation;
* AI-generated match commentary;
* LLM dependency;
* betting mechanics.

The protagonist remains the primary simulation target.

---

# 5. REAL-WORLD FOOTBALL DATA STRATEGY

Football Life should support real football structures while keeping the simulator manageable.

The system should use a curated dataset rather than attempting to reproduce the entire global football ecosystem.

## 5.1 Tier 1 — Major European Football

The initial real-world dataset SHOULD prioritize:

### England

* Premier League
* Championship
* FA Cup
* EFL Cup

### Spain

* LaLiga
* Segunda División
* Copa del Rey
* Supercopa

### Germany

* Bundesliga
* 2. Bundesliga
* DFB-Pokal

### Italy

* Serie A
* Serie B
* Coppa Italia
* Supercoppa Italiana

### France

* Ligue 1
* Ligue 2
* Coupe de France

---

# 6. CONTINENTAL COMPETITIONS

The simulation should support the major UEFA club competitions:

* UEFA Champions League
* UEFA Europa League
* UEFA Conference League

The system should allow a club's qualification for these competitions to affect the protagonist's season.

Example:

```text
FC Barcelona

LaLiga:
1st

Champions League:
Winner

Copa del Rey:
Quarter-final
```

---

# 7. ADDITIONAL FOOTBALL MARKETS

The data model should allow expansion into:

* Portugal
* Netherlands
* Belgium
* Turkey
* Austria
* Switzerland
* Greece
* Poland
* Brazil
* Argentina
* Mexico
* United States
* Japan
* Saudi Arabia
* South Korea
* other countries later.

Phase 17 does not require exhaustive coverage of all of them.

The architecture MUST NOT hardcode the initial five countries as permanent limits.

---

# 8. DATA MODEL

The existing football-world models from previous phases should be reused where possible.

Phase 17 should extend rather than duplicate existing concepts.

The system should introduce or extend concepts equivalent to:

```text
Country
NationalTeam
League
Club
Competition
CompetitionSeason
CompetitionParticipant
Fixture
Match
PlayerMatchPerformance
SeasonStatistics
CompetitionStatistics
LeagueStanding
Injury
InternationalCallUp
Trophy
Award
SeasonSummary
```

Exact naming should follow the existing project conventions.

---

# 9. COUNTRY

A country should contain enough information to support:

* player nationality;
* national team;
* leagues;
* competitions;
* international tournaments.

Example:

```text
Spain

Code: ESP
Region: Europe
National Team: Spain
```

Country identity must be deterministic.

---

# 10. NATIONAL TEAM

A national team represents the international career destination of a player.

Example:

```text
Spain

FIFA/World ranking:
...

Confederation:
UEFA
```

The simulation does not need to simulate the entire national-team squad.

Only the protagonist's involvement must be meaningfully simulated.

---

# 11. LEAGUE

A league represents a domestic league competition.

Example:

```text
LaLiga

Country:
Spain

Tier:
1

Clubs:
20
```

The league should contain enough information to determine:

* number of clubs;
* matches per season;
* points system;
* promotion/relegation behavior;
* continental qualification;
* season duration.

---

# 12. CLUB

Clubs should have:

* deterministic ID;
* name;
* country;
* league;
* prestige;
* strength;
* reputation;
* continental eligibility;
* domestic competition participation.

Existing Phase 2 club data should remain the foundation.

---

# 13. COMPETITION

Competitions should support:

```text
CompetitionType
```

with values such as:

* LEAGUE
* DOMESTIC_CUP
* DOMESTIC_SUPERCUP
* CONTINENTAL_CLUB
* INTERNATIONAL
* INTERNATIONAL_QUALIFIER

Competitions should also contain:

* name;
* country/region;
* competition type;
* format;
* prestige;
* rules.

---

# 14. COMPETITION SEASON

A competition season represents a concrete edition.

Example:

```text
LaLiga
2036/37
```

The season should be deterministic from:

* competition;
* season;
* career seed.

---

# 15. FIXTURES

A fixture represents a scheduled match.

Example:

```text
Barcelona vs Sevilla
LaLiga
Matchday 18
2036/37
```

A fixture should contain:

* home club;
* away club;
* competition;
* round/matchday;
* date or deterministic ordering;
* result after simulation.

---

# 16. MATCH SIMULATION

Matches should be simulated statistically rather than tactically.

The engine should determine:

* winner;
* draw;
* goals;
* approximate match importance;
* protagonist participation;
* protagonist performance.

The result must be deterministic.

---

# 17. MATCH RESULT

A match result should include:

```text
home_score
away_score
winner
competition
round
```

Optional data may include:

```text
attendance
```

but this is not required for Phase 17.

---

# 18. PLAYER MATCH PERFORMANCE

The protagonist's match performance should include:

* appeared;
* starter;
* minutes;
* goals;
* assists;
* rating;
* yellow cards;
* red cards;
* injury;
* position.

Example:

```text
Adrian Martínez

90 minutes
2 goals
1 assist
8.9 rating
```

This is one of the most important additions of Phase 17.

---

# 19. PLAYER PARTICIPATION

The engine must determine whether the protagonist plays each fixture.

Participation should depend on factors such as:

* OVR;
* club status;
* form;
* fitness;
* injury;
* age;
* position;
* manager/context;
* competition importance.

The exact formula should be configurable.

---

# 20. GOALS AND ASSISTS

Goals and assists must be generated as real seasonal statistics.

They should NOT simply be assigned after the season.

They must originate from simulated match participation.

For example:

```text
38 appearances
22 starts

17 goals
9 assists
```

The total should equal the sum of individual match performances.

---

# 21. PLAYER FORM

Player form should influence:

* starting probability;
* match performance;
* goals;
* assists;
* event probability;
* transfer interest;
* awards.

Form should remain bounded and deterministic.

---

# 22. PLAYER RATING

The player should receive a match rating.

A rating may depend on:

* position;
* minutes;
* goals;
* assists;
* defensive contribution;
* match result;
* competition importance.

The engine should avoid producing unrealistic rating distributions.

---

# 23. INJURIES

Phase 17 introduces actual match-impacting injuries.

An injury should contain:

* type;
* severity;
* duration;
* start date/season;
* expected recovery;
* matches missed.

Example:

```text
HAMSTRING_INJURY

Severity:
Moderate

Duration:
5 weeks

Matches missed:
6
```

Injuries must affect availability.

---

# 24. INJURY TYPES

Initial configurable categories:

```text
MINOR
MODERATE
MAJOR
SEASON_ENDING
```

Examples:

* muscle injury;
* hamstring;
* ankle;
* knee;
* concussion;
* fatigue;
* illness.

The engine should remain extensible.

---

# 25. DOMESTIC LEAGUE SIMULATION

For the protagonist's club, the engine should simulate the full league season.

The league should produce:

* matches played;
* wins;
* draws;
* losses;
* goals for;
* goals against;
* points;
* final position.

Example:

```text
LaLiga 2036/37

1. Real Madrid       87 pts
2. Barcelona         84 pts
3. Atlético Madrid   76 pts
```

The protagonist's club position must be available to the narrative and presentation layers.

---

# 26. OTHER CLUBS

Other clubs do not need full player-level simulation.

They can be represented through deterministic club strength and fixture outcomes.

This is a critical scope constraint.

Football Life simulates:

> **the world around the player**

rather than:

> **every footballer in the world.**

---

# 27. DOMESTIC CUPS

The protagonist's club should participate in relevant domestic cup competitions.

The system should simulate:

* round;
* opponent;
* result;
* progression;
* elimination;
* final;
* trophy.

Example:

```text
Copa del Rey

Round of 16
Quarter-final
Semi-final
Final

Winner
```

---

# 28. CONTINENTAL QUALIFICATION

League performance should determine continental participation where applicable.

Example:

```text
LaLiga:

1st–4th:
Champions League

5th:
Europa League

6th:
Conference League
```

Exact qualification rules should be configuration-driven.

---

# 29. CONTINENTAL COMPETITIONS

If qualified, the protagonist's club should receive an additional competition schedule.

The system should support:

* group/league phase where applicable;
* knockout rounds;
* qualification;
* elimination;
* final;
* winner.

The exact modern competition format should be configuration-driven rather than hardcoded.

---

# 30. INTERNATIONAL FOOTBALL

International football is mandatory for Phase 17.

The protagonist may be:

```text
NOT_SELECTED
PRESELECTED
CALLED_UP
BENCH
STARTER
INTERNATIONAL_PLAYER
```

Selection probability should depend on:

* nationality;
* OVR;
* age;
* form;
* position;
* reputation;
* national-team strength;
* international experience.

---

# 31. INTERNATIONAL MATCHES

When selected, the player may participate in:

* friendlies;
* qualifiers;
* Nations League-style competitions;
* continental tournaments;
* World Cup.

The engine should record:

* caps;
* goals;
* assists;
* minutes;
* tournaments;
* results.

---

# 32. INTERNATIONAL TOURNAMENTS

The architecture should support major competitions such as:

* FIFA World Cup;
* UEFA European Championship;
* Copa América;
* Africa Cup of Nations;
* AFC Asian Cup;
* CONCACAF Gold Cup.

Not every tournament must be populated initially.

The architecture must allow them.

---

# 33. INTERNATIONAL CALL-UP EVENTS

A first national-team call-up should become a career milestone.

Example:

```text
INTERNATIONAL DEBUT

Spain
2031

Age:
21
```

This should feed Phase 9, Phase 10 and Phase 12.

---

# 34. TROPHIES

The system should record trophies explicitly.

Examples:

```text
LaLiga
Champions League
Copa del Rey
Europa League
World Cup
European Championship
```

A trophy should contain:

* competition;
* season;
* club/national team;
* winner;
* player involvement.

---

# 35. AWARDS

Phase 17 should introduce basic player awards.

Examples:

* Player of the Month;
* Young Player of the Season;
* League Player of the Season;
* Golden Boot;
* Team of the Season;
* Player of the Year.

Ballon d'Or-style awards may be represented as a later extension if the existing data supports it.

---

# 36. AWARD ELIGIBILITY

Awards should use deterministic calculations based on:

* goals;
* assists;
* appearances;
* average rating;
* trophies;
* competition importance;
* age;
* reputation.

The system must not simply award the protagonist automatically.

---

# 37. SEASON STATISTICS

Every completed season must generate a persistent statistical snapshot.

Example:

```text
2036/37

Club:
Barcelona

Appearances:
41

Starts:
32

Minutes:
2,941

Goals:
24

Assists:
11

Average Rating:
7.84

Yellow Cards:
3

Red Cards:
0

Injuries:
1

Trophies:
2
```

---

# 38. COMPETITION STATISTICS

Statistics must also be available by competition.

Example:

```text
LaLiga

28 appearances
18 goals
8 assists
7.9 rating

Champions League

10 appearances
5 goals
3 assists
8.2 rating
```

This is required for the UI and narrative system.

---

# 39. CAREER AGGREGATION

The engine must maintain cumulative career totals.

Example:

```text
Career

412 appearances
231 goals
104 assists

8 league titles
3 Champions League
1 World Cup
```

Career totals must always be derivable from seasonal records.

No duplicated source of truth should exist.

---

# 40. SEASON SUMMARY

Every season must produce a structured summary.

Example:

```text
SeasonSummary

season
club
appearances
goals
assists
average_rating
league_position
cup_progress
continental_progress
international_stats
injuries
trophies
awards
```

This summary becomes one of the main inputs for later phases.

---

# 41. CAREER EVENTS

Football achievements and setbacks should produce career events.

Examples:

```text
FIRST_GOAL
FIRST_START
FIRST_ASSIST
INTERNATIONAL_DEBUT
FIRST_TROPHY
CHAMPIONS_LEAGUE_DEBUT
CHAMPIONS_LEAGUE_WINNER
TOP_SCORER
MAJOR_INJURY
COMEBACK
TRANSFER
CAREER_BEST_SEASON
```

These events should integrate with the existing Event Engine.

---

# 42. EVENT VARIETY

Phase 17 should specifically address the problem discovered during the first real test:

> The player should not repeatedly experience only transfer-related events.

Football events should have multiple sources:

```text
MATCH
SEASON
COMPETITION
INTERNATIONAL
INJURY
PERFORMANCE
ACHIEVEMENT
TRANSFER
AWARD
CAREER_MILESTONE
```

---

# 43. TRANSFER INTEGRATION

Phase 17 does not replace the Transfer Engine.

It provides the football context required by it.

Transfer interest may be affected by:

* recent goals;
* assists;
* average rating;
* age;
* OVR;
* club prestige;
* competition performance;
* trophies;
* international reputation.

---

# 44. CAREER ENGINE INTEGRATION

Phase 14's `CareerSessionEngine` should remain the primary session orchestrator.

Phase 17 should provide football simulation capabilities to it.

Conceptually:

```text
CareerSessionEngine
        ↓
Season Simulation
        ↓
Competition Engine
        ↓
Match Simulation
        ↓
Player Performance
        ↓
Season Statistics
        ↓
Career History
        ↓
Events
        ↓
Narrative
        ↓
Presentation
```

---

# 45. PHASE 17 ENGINE ARCHITECTURE

Suggested modules:

```text
backend/app/football/
    competition_domain.py
    competition_engine.py
    match_domain.py
    match_engine.py
    season_domain.py
    season_engine.py
    statistics_domain.py
    statistics_engine.py
    international_domain.py
    international_engine.py
    injury_domain.py
    injury_engine.py
    award_domain.py
    award_engine.py
```

The exact structure may be adapted to the existing architecture.

The implementation MUST avoid unnecessary duplication of existing Phase 2 and Phase 8–16 concepts.

---

# 46. CONFIGURATION

Football rules must be configuration-driven.

Possible files:

```text
backend/data/rules/competitions.json
backend/data/rules/matches.json
backend/data/rules/international.json
backend/data/rules/injuries.json
backend/data/rules/awards.json
```

Configuration should contain:

* league formats;
* competition formats;
* qualification rules;
* match probability parameters;
* injury probabilities;
* award weighting;
* international selection rules.

Rules MUST NOT be scattered through Python constants when they can reasonably be configuration.

---

# 47. DETERMINISM

All simulation must be deterministic.

Given:

```text
career_seed
player_identity
club
season
competition
match
```

the same simulation MUST produce the same result.

Forbidden sources of nondeterminism include:

```text
random without seeded RNG
uuid4
datetime.now()
time.time()
hash()
unordered iteration
external live APIs
```

SHA-256-derived deterministic seeds should continue to be used.

---

# 48. ORDERING

All collections that affect serialized or observable results must have deterministic ordering.

Examples:

* fixtures;
* matches;
* competitions;
* statistics;
* awards;
* trophies;
* events.

---

# 49. IMMUTABILITY

Domain objects should remain immutable wherever consistent with the existing architecture.

Prefer:

```python
@dataclass(frozen=True)
```

and:

```text
tuple
MappingProxyType
```

for nested structures.

Simulation functions should return new state rather than mutating existing domain objects.

---

# 50. ATOMICITY

Failed simulations must not partially modify career state.

For example:

```text
simulate season
    ↓
error
    ↓
original career remains unchanged
```

This requirement is especially important because Phase 17 feeds the Career Session Engine.

---

# 51. ACTIVE CAREER SAFETY

Active careers MUST NOT be incorrectly marked as retired.

Examples of forbidden behavior:

```text
"retired"
"final season"
"career ended"
```

unless the career actually has a retirement state.

Existing Phase 8–16 safeguards must remain intact.

---

# 52. DATA GROUNDING

All generated statistics must originate from simulation state.

The engine MUST NOT invent:

* goals;
* assists;
* trophies;
* injuries;
* international appearances;
* competition participation.

If the data does not exist, it must be represented as:

```text
0
empty
not qualified
not selected
```

rather than fabricated.

---

# 53. MATCH SIMULATION BALANCE

The match engine should produce plausible football results.

It should avoid:

* excessive 8–0 results;
* impossible goal rates;
* unrealistic player statistics;
* identical scores every season;
* deterministic-looking repetition.

The exact distribution should be controlled through configurable probabilities.

---

# 54. PLAYER STATISTICS BALANCE

Statistics should scale with:

* position;
* OVR;
* minutes;
* competition;
* club strength;
* age;
* form.

For example:

A goalkeeper should not naturally generate striker-like goal totals.

A striker should have higher goal probability.

A midfielder should have higher assist probability.

A defender should have lower scoring probability but may contribute through defensive performance.

---

# 55. POSITIONAL PROFILES

The system should define configurable positional profiles.

Examples:

```text
GK
CB
LB
RB
DM
CM
AM
LW
RW
ST
```

Each profile should influence:

* goal probability;
* assist probability;
* rating;
* match impact.

The implementation should reuse existing player-position definitions whenever possible.

---

# 56. SEASON FLOW

A normal season should conceptually follow:

```text
Season Start
    ↓
Competition Qualification
    ↓
Fixture Generation
    ↓
Match Simulation
    ↓
Player Performance
    ↓
Injury Checks
    ↓
International Windows
    ↓
Domestic Cup
    ↓
Continental Matches
    ↓
Season Completion
    ↓
Awards
    ↓
Trophies
    ↓
Season Summary
    ↓
Career Update
```

The exact implementation may interleave competitions.

---

# 57. CAREER ADVANCEMENT

When the user presses:

> ADVANCE CAREER

the system should simulate the next meaningful career period.

The current UX should remain simple.

The user should not have to manually simulate:

```text
Match 1
Match 2
Match 3
...
Match 40
```

unless a later phase intentionally introduces optional match-by-match viewing.

The default experience remains season-oriented.

---

# 58. SEASON COMPLETION UI DATA

At minimum, the backend should provide enough information for the UI to display:

```text
SEASON 2036/37

41
APPEARANCES

24
GOALS

11
ASSISTS

7.9
RATING

OVR
83 → 86

LaLiga
2nd

Champions League
Winner

Copa del Rey
Quarter-final

Spain
7 caps
3 goals

TROPHIES
2
```

This directly addresses the issues discovered during the first real test.

---

# 59. PRESENTATION INTEGRATION

Phase 17 must provide richer data to Phase 12.

The existing presentation system should be able to display:

* season statistics;
* competition statistics;
* club history;
* trophies;
* injuries;
* international career;
* awards;
* important matches;
* season summaries.

Phase 17 should not redesign the Phase 12 presentation architecture unnecessarily.

---

# 60. NARRATIVE INTEGRATION

Phase 10 should receive meaningful football facts.

Examples:

```text
"Adrian scored 24 goals in his breakout season."

"Barcelona won the Champions League."

"Adrian made his Spain debut."

"An ankle injury ruled him out for six weeks."

"His performances earned him the league's Player of the Season award."
```

The narrative engine must remain responsible for turning facts into narrative.

Phase 17 provides the facts.

---

# 61. REPLAY INTEGRATION

Phase 16 should be able to identify important moments from Phase 17.

Examples:

```text
First professional goal
Hat-trick
Champions League goal
Cup final
International debut
Major injury
Comeback
Title-winning match
Career-high season
```

These should become candidate replay moments.

---

# 62. CONTENT CREATION VALUE

Phase 17 should deliberately create data that is useful for manual video recording.

A career should naturally generate moments such as:

```text
"FIRST PROFESSIONAL GOAL"

"FIRST SPAIN CALL-UP"

"CHAMPIONS LEAGUE FINAL"

"MAJOR INJURY"

"COMEBACK"

"TRANSFER TO REAL MADRID"

"BALLON D'OR"

"RETIREMENT"
```

The application does not automatically create the video.

It creates the material for the user to record.

---

# 63. REAL-WORLD DATA VERSIONING

Real football data changes over time.

The application should therefore treat the curated football dataset as versioned static data.

Example:

```text
football_world_version:
1.0
```

A career should record the dataset version used to create it.

This ensures reproducibility.

---

# 64. EXTERNAL DATA

External football APIs may be used during development or data preparation if desired.

However:

> **Runtime simulation MUST NOT depend on external network access.**

Football Life remains a local-first application.

---

# 65. DATABASE / PERSISTENCE

Phase 17 should not introduce a mandatory database architecture if the current simulator remains session/in-memory based.

Persistent storage may be introduced later.

The simulation domain must remain independent from infrastructure.

---

# 66. API

Phase 17 should expose only endpoints required by the existing application.

Possible endpoints include:

```text
GET /football/countries
GET /football/leagues
GET /football/leagues/{league_id}/clubs
GET /football/competitions
GET /career/{career_id}/season/{season}
GET /career/{career_id}/matches
GET /career/{career_id}/statistics
GET /career/{career_id}/competitions
GET /career/{career_id}/international
```

Exact API design should follow existing FastAPI conventions.

---

# 67. CAREER CREATION UX

Phase 17 should improve the career creation flow.

The player should NOT have to manually type a starting club.

Instead:

```text
COUNTRY
    ↓
LEAGUE
    ↓
CLUB
```

Example:

```text
Country
[ Spain ▼ ]

League
[ LaLiga ▼ ]

Starting Club
[ FC Barcelona ▼ ]
```

The available leagues MUST depend on the selected country.

The available clubs MUST depend on the selected league.

Nationality should also use a selectable list.

This directly addresses an issue discovered during the first real test.

---

# 68. INVALID SELECTIONS

The system must reject:

* club not belonging to selected league;
* league not belonging to selected country;
* invalid nationality;
* unavailable competition;
* invalid club IDs.

Validation should happen both:

* frontend;
* backend.

Backend validation is authoritative.

---

# 69. TESTING REQUIREMENTS

Phase 17 requires comprehensive tests.

At minimum:

## Domain

* construction;
* validation;
* immutability;
* invalid values.

## Match Engine

* deterministic results;
* valid score ranges;
* player participation;
* goals;
* assists;
* ratings.

## Competition Engine

* league scheduling;
* standings;
* cups;
* continental qualification;
* progression.

## Statistics

* aggregation;
* seasonal totals;
* career totals;
* competition totals.

## International

* selection;
* call-ups;
* matches;
* tournament participation.

## Injuries

* generation;
* duration;
* availability;
* recovery.

## Awards

* eligibility;
* deterministic winner selection.

---

# 70. DETERMINISM TESTS

The audit suite MUST include:

```text
single-process determinism
100x repeated execution
cross-process determinism
end-to-end determinism
```

Example:

```text
simulate_same_career(seed)
100 times
→ identical output
```

---

# 71. REGRESSION TESTS

All existing tests from Phases 8–16 must continue to pass.

Phase 17 must not modify previous behavior unless explicitly required for integration.

Target:

```text
Phase 8 regression: PASS
Phase 9 regression: PASS
Phase 10 regression: PASS
Phase 11 regression: PASS
Phase 12 regression: PASS
Phase 13 regression: PASS
Phase 14 regression: PASS
Phase 15 regression: PASS
Phase 16 regression: PASS
```

---

# 72. SECURITY

Phase 17 must not introduce:

* `eval`;
* `exec`;
* dynamic code execution;
* unsafe deserialization;
* arbitrary file execution;
* exposed credentials;
* unnecessary network access.

External data must be validated before entering the simulation domain.

---

# 73. PERFORMANCE

The simulator must remain fast enough for interactive use.

A complete season should not require an unreasonable amount of time.

The target is:

> **A full season simulation should complete in interactive time, preferably well below one second for the protagonist-focused simulation.**

Performance should be measured rather than assumed.

---

# 74. PHASE BOUNDARIES

Phase 17 owns:

```text
football world
competitions
matches
season statistics
international football
injuries
trophies
awards
```

Phase 17 does NOT own:

```text
narrative writing
script writing
UI presentation design
automatic video generation
content rendering
```

Those responsibilities remain in the appropriate phases.

---

# 75. SOURCE OF TRUTH

The following hierarchy should be respected:

```text
Football World
      ↓
Competition
      ↓
Match
      ↓
Player Performance
      ↓
Season Statistics
      ↓
Career History
      ↓
Events
      ↓
Narrative
      ↓
Script
      ↓
Presentation
      ↓
Replay / Content
```

No downstream layer should fabricate football facts.

---

# 76. CAREER DATA EXAMPLE

After Phase 17, a career should be capable of producing a structure conceptually equivalent to:

```text
CAREER
Adrian Martínez
Spain
ST

2028/29
Club: Valencia
Apps: 18
Goals: 4
Assists: 2
League: 11th

2029/30
Club: Valencia
Apps: 32
Goals: 14
Assists: 7
League: 6th

2030/31
Club: Atlético Madrid
Apps: 39
Goals: 21
Assists: 10
League: 2nd
Copa del Rey: Winner

2031/32
Club: Atlético Madrid
Apps: 45
Goals: 27
Assists: 12
League: Winner
Champions League: Semi-final
Spain: 8 caps
Spain: 3 goals

2032/33
Club: Atlético Madrid
Apps: 48
Goals: 31
Assists: 15
League: Winner
Champions League: Winner
Spain: World Cup
World Cup: Quarter-final

...
```

The exact numbers are illustrative only.

---

# 77. FIRST REAL CAREER TEST

Phase 17 should be considered successful only when a complete career simulation can produce a believable sequence such as:

```text
Youth / Lower Level
        ↓
Professional Debut
        ↓
First Goals
        ↓
Breakout Season
        ↓
Transfer
        ↓
European Football
        ↓
International Debut
        ↓
Major Trophy
        ↓
Peak
        ↓
Injury / Setback
        ↓
Comeback
        ↓
Late Career
        ↓
Retirement
```

The exact trajectory should vary between careers.

---

# 78. VARIABILITY

Different seeds should produce meaningfully different careers.

The engine must avoid:

```text
same club progression
same goals
same injuries
same trophies
same international trajectory
```

for every player.

At the same time, randomness must remain plausible and deterministic.

---

# 79. BALANCE PRINCIPLE

The simulator should favor believable careers rather than extreme careers.

Most careers should NOT become:

```text
18 years old → Real Madrid
20 years old → 50 goals
21 years old → Champions League
22 years old → Ballon d'Or
```

Exceptional careers should exist, but they should be exceptional.

---

# 80. EXTREME CAREERS

The engine should still allow:

* wonderkids;
* late bloomers;
* journeymen;
* injury-plagued careers;
* one-club legends;
* international stars;
* cult heroes;
* players who never reach elite level.

This variability is important for narrative generation.

---

# 81. IMPLEMENTATION ORDER

Implementation should proceed incrementally.

Recommended order:

### Step 1

Audit existing Phase 2 football-world models.

### Step 2

Implement competition domain.

### Step 3

Implement competition configuration.

### Step 4

Implement fixtures.

### Step 5

Implement match simulation.

### Step 6

Implement player match performance.

### Step 7

Implement season statistics.

### Step 8

Implement league standings.

### Step 9

Implement domestic cups.

### Step 10

Implement continental competitions.

### Step 11

Implement injuries.

### Step 12

Implement international football.

### Step 13

Implement trophies.

### Step 14

Implement awards.

### Step 15

Integrate with CareerSessionEngine.

### Step 16

Integrate with Event Engine.

### Step 17

Integrate with Career History.

### Step 18

Integrate with Narrative/Presentation/Replay.

### Step 19

Update career creation selectors.

### Step 20

Perform full career simulation tests.

---

# 82. IMPLEMENTATION RULE

DO NOT BUILD THE ENTIRE SYSTEM IN ONE PASS.

Each subsystem must be:

1. implemented;
2. tested;
3. audited;
4. integrated;
5. regression-tested.

Only then should the next subsystem be added.

---

# 83. REQUIRED DELIVERABLES

At the end of Phase 17, the repository should contain:

### Backend

* competition domain;
* competition engine;
* match domain;
* match engine;
* season simulation;
* statistics engine;
* international system;
* injury system;
* trophy system;
* award system;
* configuration files;
* API integration where required.

### Frontend

* country selector;
* league selector;
* club selector;
* nationality selector;
* season statistics display;
* competition display;
* international career display;
* injury display;
* trophy/award display.

### Tests

* unit tests;
* integration tests;
* determinism audits;
* immutability audits;
* atomicity audits;
* security audits;
* regression tests.

---

# 84. SUCCESS CRITERIA

Phase 17 is considered complete only if:

### Football World

* [ ] Countries are selectable.
* [ ] Nationalities are selectable.
* [ ] Leagues are selectable by country.
* [ ] Clubs are selectable by league.
* [ ] Real-world football structures are represented.

### Matches

* [ ] Matches are generated.
* [ ] Results are deterministic.
* [ ] Player participation is simulated.
* [ ] Goals are recorded.
* [ ] Assists are recorded.
* [ ] Match ratings are recorded.

### Competitions

* [ ] League seasons work.
* [ ] League standings work.
* [ ] Domestic cups work.
* [ ] Continental qualification works.
* [ ] Continental competitions work.
* [ ] Competition progression works.

### Player Career

* [ ] Seasonal statistics exist.
* [ ] Career statistics exist.
* [ ] Injuries affect participation.
* [ ] Transfers interact with club context.
* [ ] International call-ups exist.
* [ ] International statistics exist.
* [ ] Trophies are recorded.
* [ ] Awards are recorded.

### Integration

* [ ] Career Engine uses competition simulation.
* [ ] Event Engine receives meaningful football events.
* [ ] Career History records football statistics.
* [ ] Narrative Engine receives grounded football facts.
* [ ] Presentation receives seasonal/competition data.
* [ ] Replay receives meaningful career moments.

### Quality

* [ ] Deterministic.
* [ ] Immutable.
* [ ] Atomic.
* [ ] Secure.
* [ ] No fabricated statistics.
* [ ] No regression in Phases 8–16.
* [ ] Interactive performance acceptable.

---

# 85. PHASE 17 FINAL VALIDATION

Before declaring Phase 17 complete, perform:

```text
1. Full backend test suite
2. Phase 8 regression
3. Phase 9 regression
4. Phase 10 regression
5. Phase 11 regression
6. Phase 12 regression
7. Phase 13 regression
8. Phase 14 regression
9. Phase 15 regression
10. Phase 16 regression
11. Phase 17 unit tests
12. Phase 17 audit tests
13. 100x determinism test
14. Cross-process determinism
15. Immutability audit
16. Atomicity audit
17. Security audit
18. Angular tests
19. Angular production build
20. Full career simulation
21. Manual UI verification
22. Git status/diff verification
23. Code review
```

---

# 86. FINAL PRODUCT TEST

The most important test is no longer:

> "Does the code pass?"

It is:

> **"Can I create a player, choose a real country → league → club, simulate an entire career, and look back at that career and genuinely feel that a football career happened?"**

A successful Phase 17 should produce careers where the user can answer:

* Where did I play?
* How many matches did I play?
* How many goals did I score?
* How many assists did I make?
* What competitions did I play?
* Where did my team finish?
* What trophies did I win?
* Did I play in Europe?
* Did I play for my national team?
* Did I suffer injuries?
* What were my best seasons?
* What were my biggest matches?
* Which clubs did I represent?
* How did my career evolve?

If the answer to these questions is consistently available and grounded in simulation data, Phase 17 has achieved its objective.

---

# 87. FINAL RECOMMENDATION

Phase 17 should be treated as a **major simulation-depth phase**, not merely another UI phase.

The goal is to make Football Life's generated careers:

> **Statistically believable.**
>
> **Structurally coherent.**
>
> **Narratively rich.**
>
> **Visually presentable.**
>
> **Interesting enough to record as content.**

The simulator should remain simple to operate:

```text
CREATE CAREER
      ↓
ADVANCE CAREER
      ↓
EXPERIENCE THE SEASON
      ↓
MAKE IMPORTANT DECISIONS
      ↓
SEE WHAT HAPPENED
      ↓
ADVANCE AGAIN
```

The complexity belongs inside the simulation engine.

The user experience should remain simple.

---

# 88. PHASE 17 COMPLETION STATE

When all requirements are satisfied:

```text
PHASE 17
REAL FOOTBALL WORLD & COMPETITION ENGINE

STATUS:
READY FOR FINAL AUDIT
```

Only after the Phase 17 audit passes should the project proceed to Phase 18.

---

## END OF PHASE 17 DESIGN SPECIFICATION
