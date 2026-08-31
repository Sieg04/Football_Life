# FOOTBALL LIFE

# PHASE 18 — CAREER REALISM, PROGRESSION & DECISION DEPTH

**Project:** Football Life
**Phase:** 18
**Title:** Career Realism, Progression & Decision Depth
**Status:** Design Specification
**Depends on:** Phases 8–17
**Primary goal:** Transform the existing simulation into a coherent, believable football career experience.

---

# 1. PHASE OBJECTIVE

Phase 18 is a **career realism and simulation-depth phase**.

The previous phases established:

* Event generation
* Career state
* Narrative generation
* Script generation
* Visual presentation
* Interactive career sessions
* Replay/content capture
* Real football world data
* Competition and match simulation
* Injuries
* International football
* Awards
* Statistics
* Career creation

However, functional testing revealed an important problem:

> The simulator technically produces career data, but the resulting career does not yet consistently feel like a believable football career.

Examples of current weaknesses include:

* Starting clubs do not sufficiently influence career difficulty.
* Starting player quality is not sufficiently calibrated to the club context.
* Competition for playing time is not properly represented.
* Transfer offers lack meaningful club/market context.
* Transfer events do not provide enough information or meaningful choices.
* Season results are not sufficiently visible to the user.
* Goals, assists, appearances and competition results are not consistently surfaced throughout the career UI.
* Event variety is too limited.
* Events are not sufficiently conditioned by the player's actual career situation.
* The user cannot meaningfully react to some important career situations.
* Career progression can feel disconnected from the player's actual performances.

Phase 18 addresses these issues.

---

# 2. PRODUCT PRINCIPLE

Football Life should behave like a **career simulation**, not merely a sequence of random events.

The system should establish the following relationship:

```text
Football World
      ↓
Starting Context
      ↓
Player Profile
      ↓
Club Environment
      ↓
Playing Time
      ↓
Performance
      ↓
Reputation
      ↓
Career Progression
      ↓
Transfer Market
      ↓
Career Decisions
      ↓
New Environment
      ↓
New Career Context
```

Every major career outcome should be explainable by the player's previous state and the football environment.

---

# 3. IMPORTANT PRODUCT BOUNDARY

Phase 18 must **NOT** turn Football Life into a full Football Manager clone.

The application does not need:

* Tactical match controls
* Formation editing
* Manual substitutions
* Detailed training schedules
* Full club management
* Transfer negotiations with dozens of parameters
* Real-time match gameplay
* Financial management
* Contract micromanagement
* Scouting screens
* Staff management
* Multiplayer

The goal is:

> **A believable player career simulation that is visually engaging and fun to manually record.**

The simulator performs the complex calculations.

The user interacts with important career decisions.

---

# 4. PRIMARY EXPERIENCE

A typical career should now look like:

```text
CREATE PLAYER
      ↓
SELECT NATIONALITY
      ↓
SELECT COUNTRY
      ↓
SELECT LEAGUE
      ↓
SELECT CLUB
      ↓
SYSTEM CALIBRATES STARTING CONTEXT
      ↓
CAREER BEGINS
      ↓
SEASON SIMULATION
      ↓
MATCHES
      ↓
PERFORMANCES
      ↓
PLAYING TIME
      ↓
EVENTS
      ↓
INTERNATIONAL FOOTBALL
      ↓
INJURIES
      ↓
COMPETITIONS
      ↓
SEASON SUMMARY
      ↓
REPUTATION UPDATE
      ↓
TRANSFER MARKET
      ↓
CAREER DECISION
      ↓
NEXT SEASON
```

---

# 5. DESIGN GOALS

Phase 18 must achieve the following:

1. Starting clubs matter.
2. Starting leagues matter.
3. Starting countries matter.
4. Starting player quality is contextual.
5. Playing time is contextual.
6. Performance affects progression.
7. Performance affects reputation.
8. Reputation affects transfer interest.
9. Transfer offers contain meaningful information.
10. The user can choose between offers.
11. Seasons have complete summaries.
12. Competitions are visible.
13. Domestic and international football are visible.
14. Events have significantly greater variety.
15. Events are conditionally generated.
16. Career decisions have consequences.
17. The dashboard remains synchronized.
18. Phase 13/16 presentation receives the new information.
19. Existing determinism remains intact.
20. Existing phases remain backward compatible.

---

# 6. NON-GOALS

Phase 18 must NOT implement:

* Real-time match simulation UI
* Tactical management
* Club management
* Manual match intervention
* Financial accounting
* Full contract negotiation simulator
* Online functionality
* Authentication
* Cloud persistence
* Social networking
* Automatic video generation
* AI-generated video
* TikTok API integration
* Real-money systems

---

# 7. FOOTBALL WORLD CONTEXT

Phase 17 introduced curated real football structures.

Phase 18 must use these structures as the source of truth.

The simulator must not invent arbitrary leagues or clubs when an appropriate real-world entity already exists in the curated dataset.

The existing world data remains authoritative for:

* Countries
* National teams
* Leagues
* Clubs
* Competitions
* Club strength
* League strength
* Competition tiers

---

# 8. CLUB CONTEXT MODEL

Create a deterministic club context layer.

Suggested model:

```text
ClubContext
```

The model should include:

* club_id
* club_name
* country_id
* league_id
* club_prestige
* squad_quality
* squad_depth
* youth_development
* player_visibility
* domestic_competition_level
* international_competition_level
* expected_player_quality
* expected_starting_ovr
* competition_for_minutes
* transfer_market_strength

All values must be deterministic.

---

# 9. CLUB PRESTIGE

Club prestige should be derived from existing football-world data where possible.

Example conceptual scale:

```text
0–20   Local
21–40  Low
41–60  Established
61–75  Major
76–90  Elite
91–100 Global Elite
```

Prestige must influence:

* starting player calibration
* expectations
* playing time
* transfer visibility
* transfer destinations
* salary
* event probability
* international visibility

Prestige must NOT directly guarantee success.

---

# 10. LEAGUE STRENGTH

Every league should have a deterministic strength rating.

Example:

```text
LeagueStrength = 0–100
```

The strength should be derived from:

* curated league tier
* competition quality
* club strength distribution
* international reputation

League strength influences:

* starting OVR
* player expectations
* playing time
* reputation gain
* transfer market exposure
* quality of offers

---

# 11. COUNTRY FOOTBALL CONTEXT

Country context should influence:

* league availability
* club availability
* national-team competitiveness
* international visibility
* reputation growth

Country should NOT directly determine player quality.

Nationality and starting club are independent choices.

---

# 12. CAREER CREATION

Career creation must use structured selectors.

The required flow is:

```text
Nationality
    ↓
Country
    ↓
League
    ↓
Club
```

Country selection must be a dropdown.

League selection must be a dropdown populated from the selected country.

Club selection must be a dropdown populated from the selected league.

The user must never need to manually type a club ID or club name.

---

# 13. CAREER CREATION VALIDATION

The backend must validate:

* nationality exists
* country exists
* league exists
* club exists
* league belongs to country
* club belongs to league
* requested starting context is compatible

Invalid combinations must be rejected.

Example:

```text
Spain
  ↓
Premier League
```

must be rejected.

Likewise:

```text
Spain
  ↓
La Liga
  ↓
Manchester City
```

must be rejected.

---

# 14. STARTING PLAYER CALIBRATION

Starting player quality must depend on the football context.

The system should no longer generate exactly the same quality distribution regardless of starting club.

Conceptual formula:

```text
StartingOVR =
BaseTalent
+ LeagueContextModifier
+ ClubContextModifier
+ YouthContextModifier
+ CareerSeedVariance
```

The final result must be clamped to valid OVR bounds.

---

# 15. IMPORTANT BALANCE RULE

Starting at a stronger club does NOT simply mean:

```text
strong club = easier career
```

Instead:

```text
strong club
    ↓
higher starting quality
+
higher expectations
+
higher competition
+
greater visibility
+
better development infrastructure
```

While:

```text
weak club
    ↓
lower starting quality
+
lower expectations
+
more playing opportunities
+
lower visibility
+
potentially slower reputation growth
```

This creates different career archetypes.

---

# 16. EXAMPLE STARTING CONTEXTS

## Elite Academy

Example:

```text
Real Madrid
Barcelona
Manchester City
Bayern Munich
PSG
```

Possible characteristics:

```text
Starting OVR: higher
Potential: higher
Competition: very high
Minutes: difficult
Visibility: very high
Expectations: very high
Transfer market: high
```

## Mid-Level Club

```text
Established European club
```

Characteristics:

```text
Starting OVR: medium
Competition: medium
Minutes: moderate
Visibility: moderate
Expectations: moderate
```

## Lower-Tier League

Characteristics:

```text
Starting OVR: lower
Competition: lower
Minutes: easier
Visibility: lower
Expectations: lower
```

These are not hardcoded careers.

They are contextual probabilities.

---

# 17. PLAYER REPUTATION

Introduce a career reputation layer.

Suggested model:

```text
CareerReputation
```

Possible fields:

* domestic_reputation
* international_reputation
* club_reputation
* league_reputation
* media_visibility
* market_value_reputation

All values should remain deterministic.

---

# 18. REPUTATION CALCULATION

Reputation should be influenced by:

```text
Performance
+
Playing Time
+
Competition Strength
+
Goals
+
Assists
+
Awards
+
Trophies
+
International Performances
+
Age
+
Consistency
+
Club Visibility
```

Poor performance must also affect reputation.

Reputation must not increase automatically simply because seasons pass.

---

# 19. PLAYING TIME ENGINE

Create a deterministic playing-time calculation system.

Possible output:

```text
PlayingTimeResult
```

Including:

* expected_role
* expected_minutes
* expected_starts
* competition_level
* confidence_level
* selection_probability

---

# 20. PLAYING TIME FACTORS

Playing time must consider:

### Player

* OVR
* position
* age
* form
* reputation
* recent performances
* injury status

### Club

* squad quality
* squad depth
* competition
* tactical fit

### Context

* domestic competition
* European competition
* important matches
* injuries to teammates
* manager confidence

---

# 21. PLAYING ROLE

Possible roles:

```text
Youth Prospect
Bench Player
Rotation Player
Squad Player
Regular Starter
Key Player
Star Player
```

The role should be dynamic.

A player can move:

```text
Bench
→ Rotation
→ Starter
→ Key Player
```

or:

```text
Starter
→ Rotation
→ Bench
```

depending on performance.

---

# 22. POSITIONAL COMPETITION

Playing time should be calculated against the player's position.

For example:

```text
Player: ST
Club:
  ST #1 OVR 88
  ST #2 OVR 84
  Player OVR 76
```

The player should face significant competition.

If:

```text
Player OVR 84
ST #1 OVR 85
ST #2 injured
```

the player's playing time should increase.

This creates believable opportunities.

---

# 23. PERFORMANCE SYSTEM

Each simulated season must generate player-level statistics.

At minimum:

* appearances
* starts
* minutes
* goals
* assists
* average rating
* clean sheets where positionally relevant
* cards where relevant
* injuries
* competition appearances

The existing Phase 17 engines should remain the foundation.

Phase 18 should improve how their results affect career progression.

---

# 24. POSITION-AWARE STATISTICS

Statistics must be interpreted according to position.

For example:

### Striker

Goals and assists have high importance.

### Midfielder

Goals, assists, chances created and rating matter.

### Defender

Defensive contribution, clean sheets and rating matter.

### Goalkeeper

Clean sheets, saves, goals conceded and rating matter.

The system must avoid evaluating every player purely by goals.

---

# 25. SEASON PERFORMANCE SCORE

Introduce a normalized seasonal performance score.

Conceptual:

```text
SeasonPerformance =
Performance
+ PlayingTime
+ Consistency
+ CompetitionStrength
+ Awards
+ InternationalPerformance
```

This value drives progression and reputation.

---

# 26. PLAYER DEVELOPMENT

Player development should depend on:

* age
* potential
* season performance
* playing time
* club development environment
* injuries
* consistency
* professionalism/personality where available

The system must avoid automatic linear OVR growth.

---

# 27. DEVELOPMENT ARCHETYPES

Possible trajectories:

```text
Early Wonderkid
Late Bloomer
Steady Development
Rapid Breakthrough
Inconsistent Talent
Perpetual Prospect
Declining Star
Elite Career
```

These should emerge from simulation rather than being directly assigned.

---

# 28. CAREER MARKET VALUE

Market value should reflect:

* OVR
* age
* potential
* performance
* reputation
* club
* league
* international status
* contract context

Market value should be deterministic.

It must not be the only factor used for transfers.

---

# 29. TRANSFER MARKET ENGINE

Create a deterministic transfer market subsystem.

Suggested output:

```text
TransferMarketResult
```

Containing:

* interested clubs
* available offers
* transfer probability
* offer quality
* salary
* contract length
* squad role
* club prestige
* league
* competition
* transfer fee

---

# 30. TRANSFER INTEREST

Transfer interest should be influenced by:

```text
Player Quality
+
Recent Performance
+
Age
+
Potential
+
Reputation
+
Current Club
+
League
+
International Status
+
Market Value
```

---

# 31. STARTING CLUB EFFECT ON TRANSFERS

Starting context must matter.

Example:

A player beginning at Real Madrid with high quality and high reputation may attract:

```text
Manchester City
Bayern Munich
PSG
Liverpool
Barcelona
```

while a player beginning in a lower-tier league might initially attract:

```text
Mid-table clubs
Higher-tier domestic clubs
Lower-tier European clubs
```

However, exceptional performance must allow a player from a lower-tier league to rapidly increase their market.

The system must allow:

```text
Small Club
   ↓
Breakout Season
   ↓
High Reputation
   ↓
Elite Transfer
```

---

# 32. TRANSFER OFFER QUALITY

Offer quality should be based on compatibility.

A club should not make an unrealistic offer simply because the player has a high OVR.

Consider:

* club prestige
* league strength
* squad position
* available role
* financial capacity
* player reputation
* current club
* market value

---

# 33. TRANSFER OFFER OBJECT

Create an immutable object such as:

```text
TransferOffer
```

Fields:

* offer_id
* club_id
* club_name
* league_id
* league_name
* transfer_fee
* weekly_salary
* contract_years
* squad_role
* expected_ovr
* competition_level
* European_competition
* offer_score

---

# 34. TRANSFER DECISION UI

Transfer offers must no longer appear as a simple event message.

They must display meaningful information.

Example:

```text
TRANSFER OFFER

ARSENAL

Premier League

Transfer Fee
€42M

Salary
€145K / week

Contract
4 Years

Squad Role
Rotation Player

European Football
Champions League

--------------------------------

ACCEPT

REJECT

VIEW CLUB
```

---

# 35. MULTIPLE OFFERS

The system should support multiple offers where appropriate.

Example:

```text
Offer A
Manchester United
€55M
Starter

Offer B
Arsenal
€42M
Rotation

Offer C
Inter
€35M
Key Player
```

The user chooses.

---

# 36. TRANSFER DECISION CONSEQUENCES

Accepting an offer must:

* change club
* change league
* update contract
* update salary
* update squad context
* update playing-time competition
* update reputation context
* create a career event
* create timeline entry
* update presentation
* affect future transfer market

Rejecting an offer must:

* preserve club
* preserve contract
* create an appropriate event
* potentially affect future market opportunities

---

# 37. LOAN SYSTEM

Where appropriate, support loan offers.

A loan should include:

* destination club
* league
* expected role
* duration
* salary responsibility
* development opportunity

Example:

```text
LOAN OFFER

Real Sociedad

Expected Role:
Regular Starter

Duration:
1 Season

Development:
High

European Football:
Yes
```

The user can:

```text
ACCEPT
REJECT
```

---

# 38. CONTRACT EVENTS

Expand contract-related events.

Possible events:

```text
Contract Extension
Contract Negotiation
Contract Expiring
Transfer Interest
Transfer Offer
Loan Offer
Renewal Rejected
Player Requests Transfer
```

---

# 39. SEASON SUMMARY

Every completed season must generate a complete season summary.

Minimum information:

```text
Season
Club
League
Appearances
Starts
Minutes
Goals
Assists
Average Rating
Domestic Position
Domestic Cup Result
European Competition Result
International Caps
International Goals
Trophies
Awards
Injuries
OVR Start
OVR End
Market Value
```

---

# 40. SEASON SUMMARY UI

After advancing a season, the user should see a dedicated season result.

Example:

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2027 / 28

REAL MADRID

LA LIGA

2ND PLACE

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

31 MATCHES
17 STARTS
9 GOALS
7 ASSISTS
7.3 RATING

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CHAMPIONS LEAGUE
Quarter-Final

COPA DEL REY
WINNER

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INTERNATIONAL

6 CAPS
2 GOALS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OVR
72 → 76

MARKET VALUE
€18M → €31M

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

This information must be available after every season.

---

# 41. COMPETITION RESULTS

The user must be able to see how every relevant competition ended.

At minimum:

### Domestic League

* final position
* points
* wins
* draws
* losses
* goals for
* goals against

### Domestic Cup

* progression
* elimination stage
* winner

### European Competition

Where applicable:

* competition
* stage reached
* result

### International

* caps
* goals
* tournament participation
* tournament stage

---

# 42. CAREER STATISTICS

Career statistics must aggregate:

```text
Total Matches
Total Starts
Total Minutes
Total Goals
Total Assists
Total International Caps
Total International Goals
Total Trophies
Total Awards
Average Rating
```

Statistics must update immediately after season completion.

---

# 43. EVENT ENGINE 2.0

Phase 18 must significantly increase event diversity.

Events must become **context-aware**.

Events should not simply be randomly selected from a flat list.

---

# 44. EVENT CATEGORIES

At minimum:

## Career

* First Team Debut
* Breakthrough
* Starting XI Opportunity
* Starting XI Promotion
* Losing Starting Place
* Manager Confidence
* Contract Renewal
* Transfer Interest
* Transfer Offer
* Loan Offer
* Return From Loan

## Performance

* Hat-Trick
* Match Winner
* Goal Streak
* Assist Streak
* Man of the Match
* Career-Best Performance
* Breakout Month
* Goal Drought
* Poor Form
* Career-Best Season

## Club

* New Manager
* Tactical Change
* Squad Competition
* Major Signing
* Teammate Injury
* European Qualification
* Title Race
* Relegation Battle

## International

* First Call-Up
* International Debut
* Starting International Match
* Tournament Selection
* International Goal
* Dropped From Squad
* Major Tournament

## Injury

* Minor Injury
* Moderate Injury
* Major Injury
* Season-Ending Injury
* Recovery
* Return To Training
* Return To Competition

## Transfer

* Scout Interest
* Transfer Rumour
* Formal Offer
* Multiple Offers
* Loan Offer
* Contract Extension
* Transfer Request

## Achievement

* Trophy
* Award
* Record
* Personal Milestone

---

# 45. EVENT CONDITIONS

Every event should define conditions.

Example:

```text
Hat-Trick
requires:
  goals_in_match >= 3
```

Example:

```text
First International Call-Up
requires:
  international_caps == 0
  AND international_eligibility == true
  AND ovr >= threshold
```

Example:

```text
Transfer Offer
requires:
  market_interest >= threshold
```

Events must not appear when their prerequisites are impossible.

---

# 46. EVENT FREQUENCY

Events must be controlled by:

* season frequency
* importance
* player state
* recent events
* event cooldown
* event category
* probability modifiers

Avoid repetitive events.

The same event category should not dominate every career.

---

# 47. EVENT COOLDOWNS

Important event types should have cooldowns.

Example:

```text
Transfer Offer:
minimum cooldown = 1 season
```

The exact values must be configurable in JSON.

---

# 48. EVENT MEMORY

The simulator must remember relevant previous events.

Example:

If:

```text
Player rejected Arsenal
```

the next season should not immediately generate:

```text
Arsenal offer
```

unless a legitimate new context exists.

Similarly:

```text
Player suffered major injury
```

should affect:

* playing time
* form
* performance
* transfer interest

during recovery.

---

# 49. CAREER DECISIONS

Important events must create actual decisions.

Possible decisions:

```text
Transfer Offer
Loan Offer
Contract Renewal
Transfer Request
National Team Choice
Career Development Choice
```

Decision options must be meaningful.

---

# 50. DECISION STRUCTURE

A decision should contain:

```text
Decision
├── Situation
├── Context
├── Options
├── Consequences
└── Resolution
```

Consequences must be applied through the existing Phase 8 decision/effect systems.

---

# 51. DECISION PRESENTATION

Decision overlays should display:

* event title
* description
* current club
* player role
* relevant statistics
* offer details
* available options
* consequences where appropriate

The UI must never force the user to guess what an option means.

---

# 52. CAREER DASHBOARD

The dashboard must become the primary career control center.

It should show at minimum:

```text
PLAYER
OVR
AGE
POSITION
CLUB
CURRENT SEASON

SEASON STATS
Matches
Goals
Assists
Rating

CAREER TOTALS
Matches
Goals
Assists
Trophies

CURRENT FORM

MARKET VALUE

CURRENT ROLE

NEXT IMPORTANT EVENT
```

---

# 53. SEASON STATUS

The dashboard must clearly indicate:

```text
2028/29

Season:
ACTIVE
```

or:

```text
Season:
COMPLETED
```

When a season completes, the season summary must be immediately available.

---

# 54. CAREER HISTORY

The user must be able to browse previous seasons.

Example:

```text
2026/27
Real Madrid
18 apps
4 goals
2 assists

2027/28
Real Madrid
31 apps
9 goals
7 assists

2028/29
Arsenal
36 apps
15 goals
11 assists
```

---

# 55. CLUB HISTORY

Club history must show:

* club
* seasons
* appearances
* goals
* assists
* trophies
* transfer fee
* role

---

# 56. INTERNATIONAL HISTORY

International history must show:

* country
* caps
* goals
* tournaments
* tournament results
* debut season

---

# 57. CAREER ARC

The existing Phase 12/13 career arc must use the improved data.

Possible trajectory:

```text
ACADEMY
   ↓
DEBUT
   ↓
BREAKTHROUGH
   ↓
ESTABLISHED
   ↓
STAR
   ↓
ELITE
   ↓
DECLINE
   ↓
RETIREMENT
```

This must be derived from actual career data.

---

# 58. PRESENTATION INTEGRATION

Phase 18 must update the Phase 12/13 presentation layer.

New presentation data must include:

* complete season summaries
* competition results
* player statistics
* transfer offers
* club history
* international history
* awards
* injuries
* reputation
* market value
* career milestones

Phase 12 remains responsible for pure presentation models.

Phase 13 remains responsible for visual presentation.

Phase 16 remains responsible for replay/content capture.

---

# 59. REPLAY INTEGRATION

Phase 16 replay generation must be able to use Phase 18 information.

Replay moments may include:

```text
First Goal
First Trophy
Breakout Season
Major Transfer
International Debut
Major Injury
Career-Best Season
Record
Major Award
```

---

# 60. REAL FOOTBALL DATA USAGE

Phase 18 should use the curated football world introduced in Phase 17.

Priority should be given to:

1. Real clubs
2. Real leagues
3. Real competitions
4. Real national teams
5. Real competition structures

The simulation may generate fictional:

* player names
* player careers
* statistics
* transfers
* events

The football world itself should remain grounded in curated real entities.

---

# 61. RULE CONFIGURATION

Create or extend configuration files under:

```text
backend/data/rules/
```

Suggested:

```text
career_context.json
progression.json
playing_time.json
reputation.json
transfers.json
events.json
season_summary.json
```

Rules must be externalized where practical.

Avoid scattering balance constants throughout Python code.

---

# 62. DETERMINISM

Phase 18 must preserve deterministic simulation.

For identical:

```text
seed
+
player
+
career state
+
football world
```

the result must be identical.

This includes:

* starting OVR
* playing time
* match statistics
* transfers
* events
* reputation
* progression
* season summaries
* decisions

---

# 63. CROSS-PROCESS DETERMINISM

The same career must produce the same result across independent Python processes.

Do NOT rely on:

* Python's randomized hash()
* unordered iteration
* memory addresses
* timestamps
* random UUIDs
* system-specific ordering

Use the existing deterministic seed/hash architecture.

---

# 64. IMMUTABILITY

Domain objects introduced by Phase 18 must be immutable where appropriate.

Use:

```text
@dataclass(frozen=True)
```

and immutable collections.

No engine function should mutate input career state in place.

---

# 65. ATOMICITY

Every major career operation must be atomic.

Examples:

```text
advance_season()
resolve_transfer()
resolve_loan()
resolve_contract()
apply_event()
```

If an operation fails:

```text
career state before operation
==
career state after failed operation
```

No partial state updates are allowed.

---

# 66. ERROR HANDLING

Introduce typed errors for:

* invalid club
* invalid league
* invalid country
* invalid transfer offer
* invalid decision
* unavailable offer
* invalid career state
* invalid season state
* missing required data

Do not expose internal stack traces through API responses.

---

# 67. API REQUIREMENTS

The backend must expose sufficient endpoints for the frontend.

Existing endpoints must remain compatible.

Possible additions:

```text
GET /football/career/{id}/season/{season}
GET /football/career/{id}/history
GET /football/career/{id}/transfers
GET /football/career/{id}/offers
POST /football/career/{id}/transfer
GET /football/career/{id}/reputation
```

Exact endpoint structure may be adapted to the existing architecture.

Avoid duplicate APIs where an existing endpoint can provide the information.

---

# 68. FRONTEND REQUIREMENTS

The frontend must integrate the new data without replacing the existing visual system.

Existing:

* Career Shell
* Career Dashboard
* Career Hub
* Player Profile
* Timeline
* Stats
* Clubs
* Achievements
* Story
* Script
* Replay
* Content Mode
* Recording Mode

must remain functional.

---

# 69. CAREER CREATION UI

Career creation must visually present:

```text
NATIONALITY
[ Select ]

STARTING COUNTRY
[ Select ]

LEAGUE
[ Select ]

STARTING CLUB
[ Select ]
```

Dropdowns should support loading states.

Example:

```text
Select country first
```

League and club selectors should remain disabled until their parent selection is valid.

---

# 70. TRANSFER UI

Create a visually strong transfer offer interface.

Recommended structure:

```text
TRANSFER MARKET

┌───────────────────────────────┐
│ ARSENAL                       │
│ Premier League               │
│                               │
│ €42M TRANSFER FEE             │
│ €145K / WEEK                  │
│ 4 YEARS                       │
│                               │
│ ROLE: ROTATION                │
│ CHAMPIONS LEAGUE              │
│                               │
│ [ ACCEPT ]    [ REJECT ]      │
└───────────────────────────────┘
```

The design should fit the existing Football Life dark cinematic identity.

---

# 71. SEASON RESULT UI

Season completion should produce a strong visual transition.

Recommended:

```text
SEASON COMPLETE

2028 / 29

━━━━━━━━━━━━━━━━━━

CLUB
ARSENAL

LEAGUE
3RD

PLAYER

38 APPEARANCES
21 GOALS
13 ASSISTS
7.8 RATING

━━━━━━━━━━━━━━━━━━

CHAMPIONS LEAGUE
SEMI-FINAL

FA CUP
WINNER

━━━━━━━━━━━━━━━━━━

OVR
79 → 83

━━━━━━━━━━━━━━━━━━

[ VIEW SEASON ]
[ CONTINUE CAREER ]
```

---

# 72. EVENT UI

Events should communicate information, not raw engine structures.

Never display:

```text
FORM_CHANGE
CURRENT_ABILITY +81.60000000001
```

Instead display:

```text
FORM IMPROVEMENT

Your recent performances have improved your form.

CURRENT OVR
82

FORM
Excellent

[ CONTINUE ]
```

Raw internal enum names must never be presented to the user.

---

# 73. DATA FORMATTING

All presentation values must be formatted.

Examples:

```text
83.60000000001
```

becomes:

```text
83.6
```

or:

```text
84
```

depending on UI context.

Currency:

```text
74000000
```

becomes:

```text
€74M
```

Salary:

```text
180000
```

becomes:

```text
€180K / week
```

---

# 74. ACCESSIBILITY

New UI components must include:

* semantic buttons
* labels
* keyboard navigation
* visible focus states
* sufficient contrast
* accessible dialog behavior
* appropriate ARIA attributes where required
* reduced motion support

---

# 75. RESPONSIVE DESIGN

Desktop remains the primary platform.

Required support:

```text
1280×720
1920×1080
2560×1440
```

The recording experience should prioritize:

```text
1920×1080
```

---

# 76. RECORDING MODE

Existing recording mode must remain functional.

Phase 18 should improve recording readability where required.

Recording mode should clearly expose:

* player identity
* season
* OVR
* club
* statistics
* events
* decisions
* season results

Do not automatically generate video files.

---

# 77. PERFORMANCE

The simulation should remain lightweight.

Phase 18 must avoid unnecessary:

* network calls
* repeated calculations
* database queries
* expensive rendering
* duplicate presentation generation

The frontend should request only necessary information.

---

# 78. SECURITY

Phase 18 must not introduce:

* eval
* exec
* dynamic code execution
* unsafe HTML rendering
* unvalidated identifiers
* arbitrary file access
* credentials
* secrets

API inputs must be validated.

---

# 79. TESTING STRATEGY

Phase 18 requires several levels of testing.

## Domain Tests

Test:

* context creation
* reputation
* progression
* playing time
* transfer offers
* season summaries

## Engine Tests

Test:

* deterministic output
* contextual calculations
* edge cases
* impossible transfers
* event conditions

## API Tests

Test:

* valid requests
* invalid requests
* missing career
* transfer resolution
* season history

## Frontend Tests

Test:

* selectors
* dashboard updates
* season summary
* transfer modal
* decision flow
* recording mode

---

# 80. DETERMINISM TESTING

Minimum:

```text
10x repeated execution
100x repeated execution
cross-process execution
```

must produce identical outputs.

Critical systems:

```text
Starting Context
Starting OVR
Playing Time
Season Stats
Progression
Reputation
Transfer Offers
Events
Season Summary
Career Presentation
```

---

# 81. REGRESSION TESTING

All previous phases must remain passing.

Minimum required:

```text
Phase 8
Phase 9
Phase 10
Phase 11
Phase 12
Phase 13
Phase 14
Phase 15
Phase 16
Phase 17
```

No regression is acceptable without explicit justification.

---

# 82. REAL CAREER TEST MATRIX

At least six deterministic careers must be simulated.

## Career A — Elite Academy

```text
Real Madrid
```

Expected:

* high starting OVR
* high competition
* difficult early minutes
* high market visibility

## Career B — Elite Academy

```text
Barcelona
```

Expected similar contextual difficulty but different deterministic outcomes.

## Career C — Mid-Level Club

```text
Established European club
```

Expected:

* moderate competition
* regular opportunities
* moderate market visibility

## Career D — Lower-Tier League

```text
Second-tier / lower-strength league club
```

Expected:

* lower starting OVR
* easier minutes
* lower initial visibility

## Career E — Breakout

A seed that produces:

```text
low/mid-level start
→ exceptional season
→ reputation increase
→ elite transfer interest
```

## Career F — Difficult Career

A seed producing:

```text
poor form
+
limited minutes
+
injury
+
reduced market interest
```

These are validation scenarios, not guaranteed user-facing scripts.

---

# 83. EXPECTED CAREER VARIETY

The simulator should be capable of producing different trajectories.

Examples:

### Wonderkid

```text
Academy
→ Debut
→ Breakthrough
→ Starter
→ Elite Club
→ International Star
```

### Late Bloomer

```text
Lower League
→ Regular Starter
→ Breakout
→ Major Transfer
→ Elite Career
```

### Failed Prospect

```text
Elite Academy
→ Limited Minutes
→ Loans
→ Decline
→ Mid-Level Career
```

### Injury Career

```text
Breakthrough
→ Major Injury
→ Recovery
→ Reduced Form
→ Comeback
```

### Journeyman

```text
Club A
→ Club B
→ Club C
→ Club D
→ International Career
```

---

# 84. IMPORTANT BALANCE REQUIREMENT

No single career path should dominate.

The simulator should not systematically produce:

```text
OVR increase every season
+
transfer every 3 seasons
+
international call-up
```

That would feel scripted.

Career outcomes must emerge from:

```text
seed
+
player
+
context
+
performance
+
events
+
decisions
```

---

# 85. EVENT VARIETY VALIDATION

A multi-season simulation must demonstrate more than the current three dominant event types.

The validation suite should explicitly verify the possibility of:

* performance events
* breakthrough events
* injury events
* international events
* club events
* transfer events
* contract events
* achievement events
* contextual events

The exact distribution should remain configurable.

---

# 86. SEASON COMPLETION CONTRACT

Every successful `advance_season()` operation must produce enough information to construct:

```text
SeasonSummary
```

without reconstructing data from incomplete event payloads.

The season summary must be a first-class domain result.

---

# 87. DATA GROUNDING

Every displayed career fact must originate from:

```text
Career State
+
Football World
+
Simulation Results
+
Resolved Decisions
```

The presentation layer must never invent:

* goals
* assists
* trophies
* transfers
* club history
* injuries
* international appearances
* competition results

---

# 88. NO FAKE PRESENTATION DATA

Mock/fallback data may exist for development/sample screens only.

Production career views must prioritize actual career state.

The frontend must not silently replace missing real data with fabricated statistics.

---

# 89. SERIALIZATION

All Phase 18 domain objects must support deterministic serialization where required.

Serialization must use:

```text
UTF-8
sorted keys
stable ordering
```

The existing `to_json_bytes()` architecture should be extended rather than replaced.

---

# 90. PHASE BOUNDARIES

Phase 18 must respect:

### Phase 8

Event conditions, probability and decisions remain authoritative.

### Phase 9

Career domain remains authoritative for career records.

### Phase 10

Narrative remains authoritative for story generation.

### Phase 11

Script generation remains authoritative for presentation scripts.

### Phase 12

Presentation domain remains authoritative for presentation data structures.

### Phase 13

Visual career presentation remains authoritative for information display.

### Phase 14

Career session lifecycle remains authoritative for interactive career state.

### Phase 15

Visual refinement and recording experience remain authoritative for design consistency.

### Phase 16

Replay and content capture remain authoritative for replay/capture functionality.

### Phase 17

Football world and competition engines remain authoritative for real football structures and match/competition simulation.

Phase 18 orchestrates and enriches these systems.

It must not duplicate their responsibilities.

---

# 91. ARCHITECTURAL PRINCIPLE

The preferred architecture is:

```text
Football World
      ↓
Competition Engine
      ↓
Match Engine
      ↓
Player Statistics
      ↓
Career Context
      ↓
Playing Time
      ↓
Performance
      ↓
Progression
      ↓
Reputation
      ↓
Transfer Market
      ↓
Events / Decisions
      ↓
Career State
      ↓
Presentation
      ↓
Replay / Content
```

Avoid creating circular dependencies.

---

# 92. IMPLEMENTATION ORDER

Jules should implement Phase 18 in controlled steps.

Do NOT build everything in one pass.

Recommended sequence:

## Step 1

Career Context Domain

## Step 2

Starting Player Calibration

## Step 3

Playing Time Engine

## Step 4

Performance & Progression

## Step 5

Reputation

## Step 6

Transfer Market

## Step 7

Transfer / Loan Decisions

## Step 8

Season Summary

## Step 9

Event Engine 2.0

## Step 10

Career Dashboard synchronization

## Step 11

Career Creation selectors

## Step 12

Presentation integration

## Step 13

Replay integration

## Step 14

Frontend visual improvements

## Step 15

Full testing and audit

---

# 93. IMPLEMENTATION SAFETY

At every step:

1. Read the existing implementation.
2. Identify the authoritative domain.
3. Reuse existing types.
4. Avoid duplicating logic.
5. Avoid breaking previous phases.
6. Add tests before or alongside implementation.
7. Run targeted tests.
8. Run regression tests.
9. Only then continue.

---

# 94. FILE STRUCTURE

Suggested backend structure:

```text
backend/app/
├── career/
│   ├── domain.py
│   ├── engine.py
│   ├── service.py
│   ├── context.py
│   ├── progression.py
│   ├── reputation.py
│   └── transfer.py
│
├── football/
│   ├── match_engine.py
│   ├── competition_engine.py
│   ├── statistics_engine.py
│   ├── injury_engine.py
│   ├── international_engine.py
│   └── award_engine.py
│
└── event/
    ├── conditions.py
    ├── probability.py
    ├── career_engine.py
    ├── presentation_engine.py
    └── replay_engine.py
```

Exact organization may be adapted to existing architecture.

---

# 95. FRONTEND STRUCTURE

Suggested:

```text
frontend/football-life/src/app/career/

├── career-create/
├── career-dashboard/
├── career-season-summary/
├── career-transfer/
├── career-decision/
├── career-event/
├── career-notification/
├── career-recording-mode/
├── career-shell/
├── career-timeline/
├── career-clubs/
├── career-achievements/
├── career-story/
├── career-script/
└── capture-view/
```

---

# 96. ACCEPTANCE CRITERIA

Phase 18 is complete only when:

### Career Creation

* [ ] Nationality is selectable.
* [ ] Country is selectable.
* [ ] League is filtered by country.
* [ ] Club is filtered by league.
* [ ] Invalid combinations are rejected.

### Starting Context

* [ ] Club prestige affects starting context.
* [ ] League strength affects starting context.
* [ ] Starting OVR is contextual.
* [ ] Competition for minutes is contextual.

### Playing Time

* [ ] Squad quality affects minutes.
* [ ] Position affects minutes.
* [ ] Player OVR affects minutes.
* [ ] Form affects minutes.
* [ ] Injuries can create opportunities.

### Statistics

* [ ] Matches are recorded.
* [ ] Starts are recorded.
* [ ] Minutes are recorded.
* [ ] Goals are recorded.
* [ ] Assists are recorded.
* [ ] Ratings are recorded.
* [ ] Competition statistics are recorded.

### Progression

* [ ] Performance affects progression.
* [ ] Age affects progression.
* [ ] Potential affects progression.
* [ ] Playing time affects progression.
* [ ] Injuries can affect progression.

### Reputation

* [ ] Performance affects reputation.
* [ ] Competition strength affects reputation.
* [ ] International football affects reputation.
* [ ] Reputation affects transfer market.

### Transfers

* [ ] Transfer interest is contextual.
* [ ] Offers contain detailed information.
* [ ] Multiple offers are supported where appropriate.
* [ ] User can accept/reject.
* [ ] Accepted offers change club state.
* [ ] Rejected offers preserve club state.
* [ ] Loan offers are supported where appropriate.

### Seasons

* [ ] Every completed season has a summary.
* [ ] League result is visible.
* [ ] Cup result is visible.
* [ ] European result is visible where applicable.
* [ ] Player statistics are visible.
* [ ] International statistics are visible.
* [ ] Trophies are visible.
* [ ] OVR progression is visible.
* [ ] Market value is visible.

### Events

* [ ] Event variety is substantially increased.
* [ ] Events are conditional.
* [ ] Event cooldowns exist.
* [ ] Event history is respected.
* [ ] Raw engine keys are never displayed.

### Presentation

* [ ] Dashboard updates immediately.
* [ ] Career history updates.
* [ ] Club history updates.
* [ ] Statistics update.
* [ ] Timeline updates.
* [ ] Replay receives important moments.

### Technical

* [ ] Deterministic.
* [ ] Cross-process deterministic.
* [ ] Immutable.
* [ ] Atomic.
* [ ] Secure.
* [ ] Serialized deterministically.
* [ ] Previous phases remain compatible.

---

# 97. REQUIRED TEST TARGET

Before Phase 18 is considered complete:

```text
Phase 18 unit tests:
PASS

Phase 18 integration tests:
PASS

Phase 18 audit tests:
PASS

Phase 17 regression:
PASS

Phase 16 regression:
PASS

Phase 15 regression:
PASS

Phase 14 regression:
PASS

Phase 13 regression:
PASS

Phase 12 regression:
PASS

Phase 11 regression:
PASS

Phase 10 regression:
PASS

Phase 9 regression:
PASS

Phase 8 regression:
PASS
```

Frontend:

```text
Angular unit tests:
PASS

Production build:
PASS
```

---

# 98. REAL-WORLD MANUAL TEST

At least one complete career must be manually tested through the application.

The tester should:

1. Open Football Life.
2. Create a player.
3. Select nationality.
4. Select country.
5. Select league.
6. Select club.
7. Start career.
8. Advance season.
9. Inspect match statistics.
10. Inspect league result.
11. Inspect cup result.
12. Inspect European competition if applicable.
13. Inspect international career.
14. Inspect injuries/events.
15. Inspect player development.
16. Inspect reputation.
17. Inspect transfer interest.
18. Receive a transfer offer if generated.
19. Inspect offer details.
20. Accept/reject an offer where available.
21. Continue career.
22. Verify club history.
23. Verify career statistics.
24. Verify season history.
25. Verify timeline.
26. Verify presentation.
27. Verify recording mode.

---

# 99. FINAL AUDIT REQUIREMENTS

Before declaring Phase 18 complete, produce a final audit containing:

## Overall Status

```text
PASS / FAIL
```

## Product Purpose Verification

Confirm that Football Life now produces a believable player career experience.

## Starting Context

Confirm:

* country
* league
* club
* prestige
* difficulty
* starting OVR

## Playing Time

Confirm contextual playing time.

## Statistics

Confirm:

* appearances
* starts
* minutes
* goals
* assists
* ratings

## Competitions

Confirm:

* league
* cups
* European competitions
* international competitions

## Progression

Confirm OVR and development behavior.

## Reputation

Confirm reputation behavior.

## Transfers

Confirm contextual transfer offers and decisions.

## Events

Confirm event variety and conditional behavior.

## Season Summary

Confirm complete season results.

## Presentation

Confirm dashboard and all career views update.

## Determinism

```text
single-process:
PASS

100x repeated:
PASS

cross-process:
PASS

end-to-end:
PASS
```

## Immutability

```text
PASS
```

## Atomicity

```text
PASS
```

## Serialization

```text
PASS
```

## Security

```text
PASS
```

## Phase Boundaries

```text
Phase 8:
PASS

Phase 9:
PASS

Phase 10:
PASS

Phase 11:
PASS

Phase 12:
PASS

Phase 13:
PASS

Phase 14:
PASS

Phase 15:
PASS

Phase 16:
PASS

Phase 17:
PASS

Phase 18:
PASS
```

## Tests

Provide exact execution results.

## Files Changed

List all expected and necessary files.

## Critical Findings

```text
None
```

or enumerate all blockers.

## Non-Blocking Findings

List minor issues.

## Final Recommendation

Only use:

```text
READY FOR PHASE 19
```

when all acceptance criteria pass.

---

# 100. FINAL PRODUCT VISION AFTER PHASE 18

After Phase 18, Football Life should no longer feel like:

```text
CLICK
↓
RANDOM EVENT
↓
OVR +1
↓
CLICK
↓
RANDOM EVENT
```

It should feel like:

```text
I STARTED AT REAL MADRID
        ↓
I WAS A HIGH-QUALITY ACADEMY PLAYER
        ↓
BUT THE SQUAD WAS STACKED
        ↓
I STRUGGLED FOR MINUTES
        ↓
I GOT MY CHANCE AFTER AN INJURY
        ↓
I SCORED 8 GOALS
        ↓
MY OVR INCREASED
        ↓
MY REPUTATION GREW
        ↓
I RECEIVED OFFERS
        ↓
ARSENAL OFFERED €42M
        ↓
I HAD TO CHOOSE
        ↓
I MOVED TO ARSENAL
        ↓
BECAME A STARTER
        ↓
PLAYED CHAMPIONS LEAGUE
        ↓
MADE MY NATIONAL TEAM DEBUT
        ↓
WON A TROPHY
        ↓
BECAME AN ELITE PLAYER
```

The important difference is that the story should emerge from the simulation.

The system should not write a predetermined story.

---

# 101. PHASE 18 SUCCESS DEFINITION

Phase 18 succeeds when a user can start two players in two different football environments and immediately feel that they are beginning **different careers**.

A player starting at:

```text
Real Madrid
```

should feel different from one starting at:

```text
a second-tier Turkish club
```

without either path being inherently scripted.

Likewise, two players starting at the same club should still be able to develop differently because of:

```text
seed
+
performance
+
playing time
+
events
+
injuries
+
decisions
+
market opportunities
```

The final objective is:

> **Football Life should generate careers worth watching.**

The user should be able to press **ADVANCE CAREER**, wait for the season to unfold, and genuinely wonder:

> **"¿Qué le ha pasado esta temporada?"**

That is the core product test for Phase 18.
