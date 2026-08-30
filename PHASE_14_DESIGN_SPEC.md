# FOOTBALL LIFE

## PHASE 14 — CAREER EXPERIENCE & SIMULATION INTERFACE

### Complete Design Specification

**Version:** 1.0
**Project:** Football Life
**Phase:** 14
**Primary Goal:** Transform Football Life from a collection of simulation/presentation engines into an interactive career experience.

---

# 1. PHASE OBJECTIVE

Phase 14 introduces the interactive career experience layer.

The user must be able to:

1. Start a career.
2. Enter a career dashboard.
3. Advance the simulation.
4. Experience significant career events.
5. Resolve decisions when required.
6. Observe changes in the player's career.
7. Navigate the accumulated career history.
8. Access Phase 13 presentation views.
9. Complete a career.
10. Use the interface comfortably for manual screen recording.

Phase 14 is **not** a video-generation system.

The user remains responsible for recording and editing the final content.

---

# 2. PRODUCT PHILOSOPHY

Phase 14 must follow these principles.

## 2.1 Simulation First

The primary action of the application is advancing the player's career.

## 2.2 Visual First

Important information should be understandable visually without requiring large amounts of text.

## 2.3 Minimal Friction

The user should be able to advance the career with very few interactions.

## 2.4 Narrative Emergence

The application must not fabricate stories.

Narrative output must emerge from actual simulation results.

```text
Simulation
    ↓
Events
    ↓
Decisions
    ↓
Career State
    ↓
Career History
    ↓
Narrative
    ↓
Presentation
```

## 2.5 Recording Friendly

The interface must be visually attractive and easy to capture using screen-recording software.

---

# 3. PHASE BOUNDARIES

Phase 14 must consume existing phase functionality.

It must not duplicate or replace previous phase responsibilities.

```text
Phase 8
Event Simulation & Resolution
        ↓
Phase 9
Career History
        ↓
Phase 10
Narrative Structure
        ↓
Phase 11
Story Script
        ↓
Phase 12
Visual Presentation Data
        ↓
Phase 13
Career Viewer
        ↓
Phase 14
Interactive Career Experience
```

Responsibilities:

| Phase | Responsibility                                                       |
| ----- | -------------------------------------------------------------------- |
| 8     | Simulation events, conditions, probability, resolution and decisions |
| 9     | Career history and career-state recording                            |
| 10    | Narrative structure                                                  |
| 11    | Script/presentation narration                                        |
| 12    | Presentation data                                                    |
| 13    | Static/interactively browsable career presentation                   |
| 14    | Interactive career progression and user interaction                  |

Phase 14 must **orchestrate** existing systems rather than reimplement them.

---

# 4. CORE USER FLOW

The primary user flow is:

```text
HOME
  ↓
NEW CAREER
  ↓
PLAYER SETUP
  ↓
CAREER DASHBOARD
  ↓
ADVANCE
  ↓
SIMULATION
  ↓
EVENT
  ↓
DECISION?
  ├── YES → DECISION UI
  │             ↓
  │          USER CHOICE
  │             ↓
  └──────── STATE UPDATE
                ↓
        CAREER UPDATE
                ↓
          DASHBOARD
                ↓
             ADVANCE
```

Secondary navigation:

```text
CAREER
├── Dashboard
├── Profile
├── Timeline
├── Stats
├── Clubs
├── Achievements
├── Story
└── Script
```

---

# 5. CAREER SESSION

Phase 14 introduces the concept of a career session.

Suggested location:

```text
backend/app/career/domain.py
```

## 5.1 CareerSession

`CareerSession` represents the interactive state of an active career.

Required conceptual fields:

```text
career_id
player_id
current_season
current_date_or_simulation_position
status
career_state
pending_events
pending_decision
last_processed_event
```

The exact representation must reuse existing project models wherever possible.

## 5.2 CareerSessionStatus

Required statuses:

```text
SETUP
ACTIVE
EVENT_PENDING
DECISION_PENDING
PAUSED
COMPLETED
FAILED
```

The domain object must be immutable.

Nested collections must use immutable structures where appropriate.

---

# 6. CAREER STATE

Phase 14 must expose the current career state without creating an unnecessary duplicate `Player` model.

The state should allow the UI to display:

* player identity
* age
* position
* club
* overall rating
* relevant attributes
* salary
* market value
* season statistics
* career statistics
* reputation
* relationships
* contract information
* current season
* career progression

Existing domain objects should be reused.

Do not create duplicate versions of Phase 8–13 domain models.

---

# 7. CAREER CREATION

Phase 14 introduces a simple career creation flow.

Required UI:

```text
START YOUR CAREER

PLAYER NAME

POSITION

[ ST ] [ LW ] [ CM ] [ CB ]

STARTING CLUB

[ SELECT CLUB ]

[ START CAREER ]
```

The implementation must use capabilities already available in the project.

Do not build a complex character creator.

Do not introduce unnecessary player-generation infrastructure.

If player generation is not yet available, use the simplest valid mechanism already supported by the existing simulation.

---

# 8. CAREER CREATION DOMAIN

The implementation may introduce a lightweight creation request/model if required.

Possible conceptual fields:

```text
player_id or generated player
starting_club
initial configuration
seed
```

The implementation must remain deterministic.

---

# 9. CAREER DASHBOARD

The dashboard is the primary screen of Phase 14.

It should provide an immediate understanding of:

* who the player is
* where the player plays
* current overall
* current season
* recent performance
* latest important event
* career progression
* primary action

Conceptual layout:

```text
┌──────────────────────────────────────────────┐
│ FOOTBALL LIFE                     2026/27    │
├──────────────────────────────────────────────┤
│                                              │
│ PLAYER                                       │
│                                              │
│ [AVATAR]    PLAYER NAME                      │
│             21 YEARS                         │
│             ST / LW                          │
│                                              │
│             82 OVR                           │
│                                              │
├──────────────────────────────────────────────┤
│ CLUB                 CURRENT SEASON          │
│ Example FC           2026/27                 │
│                                              │
│ Matches   Goals   Assists   Rating            │
│   18       11       6       7.8               │
│                                              │
├──────────────────────────────────────────────┤
│ LATEST MOMENT                                 │
│                                              │
│ First professional goal                      │
│                                              │
│ [ VIEW EVENT ]                               │
│                                              │
├──────────────────────────────────────────────┤
│                                              │
│             [ ADVANCE CAREER ]               │
│                                              │
└──────────────────────────────────────────────┘
```

The primary action must be visually dominant:

```text
ADVANCE CAREER
```

---

# 10. ADVANCE CAREER

The user must be able to progress the career using one primary action.

```text
POST /career/{career_id}/advance
```

The endpoint/application service must orchestrate the existing simulation pipeline.

Conceptual flow:

```text
ADVANCE
   ↓
Determine simulation progression
   ↓
Phase 8 event generation/resolution
   ↓
Decision required?
   ↓
Phase 8F decision
   ↓
Phase 8E effect application
   ↓
Phase 9 career recording
   ↓
Milestones
   ↓
Relationships
   ↓
Turning points
   ↓
Career arcs
   ↓
Narrative seeds
   ↓
Phase 10 narrative update
   ↓
Phase 11 script update
   ↓
Phase 12 presentation update
   ↓
Return updated career state
```

Phase 14 must not reproduce these algorithms.

---

# 11. ADVANCE RESULT

Introduce a domain representation such as:

```text
CareerAdvanceResult
```

It should communicate:

* previous state
* resulting state
* processed events
* newly generated notifications
* pending decision, if any
* career status
* whether progression succeeded

The exact structure must follow existing project conventions.

---

# 12. SIMULATION STOP CONDITIONS

The simulation must stop when user interaction is required.

Example:

```text
ADVANCE
   ↓
EVENT
   ↓
DECISION_REQUIRED
```

The career must enter:

```text
DECISION_PENDING
```

and further advancement must be rejected until the decision is resolved.

---

# 13. DECISION EXPERIENCE

When Phase 8F produces a decision, the UI must present the existing `Decision` and `DecisionOption` objects.

Example:

```text
┌─────────────────────────────────────┐
│             DECISION                │
│                                     │
│ Your manager has offered you        │
│ a new contract.                     │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ SIGN THE CONTRACT               │ │
│ │ Secure your future              │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ WAIT FOR BETTER OFFER            │ │
│ │ Risk everything for more         │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

Rules:

* Options must originate from Phase 8F.
* Angular must not invent decision options.
* Invalid choices must be rejected.
* The simulation must not continue while a decision is pending.
* Successful decision resolution must flow through Phase 8E.
* Phase 14 must not mutate simulation state directly.

---

# 14. DECISION API

Required endpoint:

```text
POST /career/{career_id}/decision
```

Request:

```text
career_id
decision_id
option_id
```

Response:

```text
updated CareerSession
+
CareerAdvanceResult or equivalent result
```

The exact transport schema may be adapted to existing FastAPI conventions.

---

# 15. EVENT EXPERIENCE

Important events should receive visual treatment.

Relevant event categories may include:

```text
NORMAL_EVENT
IMPORTANT_EVENT
MILESTONE
TURNING_POINT
DECISION
TRANSFER
INJURY
TROPHY
BREAKTHROUGH
SETBACK
```

The frontend must derive the event type from actual source data.

It must not invent events.

---

# 16. EVENT OVERLAY

Important events may appear as an overlay.

Example:

```text
┌─────────────────────────────────────┐
│                                     │
│              72'                    │
│                                     │
│          ★ CAREER MOMENT ★          │
│                                     │
│       FIRST PROFESSIONAL GOAL       │
│                                     │
│       The stadium erupted...        │
│                                     │
│             CONTINUE                │
│                                     │
└─────────────────────────────────────┘
```

Requirements:

* visually prominent
* easy to dismiss
* keyboard accessible
* no unnecessary modal nesting
* compatible with recording mode

---

# 17. CAREER NOTIFICATIONS

Introduce a lightweight notification system.

Examples:

```text
NEW MILESTONE
TRANSFER INTEREST
RELATIONSHIP CHANGED
OVERALL INCREASED
NEW TROPHY
TURNING POINT
NEW DECISION
```

Notifications should only be generated from real state changes.

Avoid building a complex notification infrastructure.

---

# 18. PLAYER EVOLUTION

The dashboard should communicate meaningful changes.

Example:

```text
OVR

74 ── 76 ── 79 ── 82 ── 84
              ↑
        BREAKTHROUGH
```

Attribute changes may be shown:

```text
PACE       81 → 84
SHOOTING   73 → 79
PASSING    68 → 74
```

Only display changes supported by actual simulation state.

---

# 19. CAREER ARC VISUALIZATION

Reuse Phase 9/12 career arc data.

Example:

```text
ACADEMY
   │
   ●──────────────
                  │
             BREAKTHROUGH
                  │
                  ●──────────────
                                 │
                           ESTABLISHMENT
```

The visualization must reflect the actual `CareerArc`.

---

# 20. CAREER NAVIGATION

Phase 13 navigation remains the main navigation system.

Required destinations:

```text
/career
/profile
/timeline
/stats
/clubs
/achievements
/story
/script
```

The dashboard remains the central interactive view.

---

# 21. PHASE 13 INTEGRATION

Phase 14 must reuse Phase 13 components.

Do not duplicate:

* player profile
* timeline
* statistics
* clubs
* achievements
* story
* script

The intended relationship is:

```text
CareerSession
      ↓
CareerPresentation
      ↓
Phase 13 Components
```

When the career advances, the presentation data must reflect the new state.

---

# 22. CAREER COMPLETION

When the simulation reaches its natural endpoint:

```text
CAREER COMPLETE
```

Display a final summary:

```text
CAREER SUMMARY

Career span
Clubs
Matches
Goals
Assists
Trophies
Peak OVR
Peak market value
Major milestones

[ VIEW CAREER ]

[ VIEW STORY ]

[ VIEW SCRIPT ]
```

The user must be able to navigate into the existing Phase 13 presentation views.

---

# 23. RECORDING MODE

Phase 14 must provide a dedicated visual mode for manual screen recording.

This does **not** mean automated video recording.

## Recording Mode Goals

* minimize UI noise
* emphasize important information
* improve composition
* enlarge important values
* reduce unnecessary controls
* provide cinematic transitions
* work well at 16:9
* make event overlays visually strong

Possible toggle:

```text
NORMAL MODE
RECORDING MODE
```

Recording mode must never alter simulation logic.

---

# 24. RECORDING MODE LAYOUT

Primary target:

```text
1920 × 1080
```

Secondary:

```text
1366 × 768
1280 × 720
```

Important content should remain inside a safe visual area.

Avoid critical information touching screen edges.

---

# 25. VISUAL DIRECTION

Phase 14 must preserve the Phase 13 visual identity.

Core qualities:

```text
DARK
CINEMATIC
SPORT
TECHNICAL
MODERN
MINIMAL
```

Phase 14 should add controlled motion:

* stat counters
* event reveals
* subtle transitions
* timeline movement
* career progression animations
* decision emphasis

Avoid:

* excessive gradients
* generic SaaS dashboard aesthetics
* excessive glassmorphism
* constant animations
* excessive particle effects
* visual clutter

The desired feeling is:

```text
Football Career Simulation
        ×
Sports Broadcast
        ×
Football Analytics
```

---

# 26. BRANDING

The existing Football Life logo remains the primary brand asset:

```text
fl_logo.png
```

The existing Phase 13 design system must be reused.

Do not create a second visual identity.

---

# 27. FRONTEND STATE MANAGEMENT

There must be a single source of truth for the active career.

The frontend state must represent:

```text
Current Career
Current Player
Current Season
Current Simulation State
Pending Decision
Latest Event
Latest Notifications
Recording Mode
```

Avoid duplicated career state between components.

A centralized service/store is recommended.

---

# 28. LOADING STATES

The UI must provide clear loading feedback during:

* career creation
* advance
* decision submission
* presentation refresh

The interface must prevent duplicate submissions while a request is processing.

---

# 29. ERROR HANDLING

Minimum conceptual error codes:

```text
CAREER_NOT_FOUND
INVALID_STATE
SIMULATION_ERROR
DECISION_REQUIRED
INVALID_DECISION
CAREER_COMPLETED
INVALID_PLAYER
```

Errors must not crash the UI.

They must produce human-readable feedback.

---

# 30. BACKEND ARCHITECTURE

Recommended structure:

```text
backend/app/career/
├── __init__.py
├── domain.py
├── engine.py
├── service.py
└── exceptions.py
```

## domain.py

Career session domain primitives.

## engine.py

Career progression orchestration.

## service.py

Application/service layer.

## exceptions.py

Phase 14 exceptions.

The implementation may adapt this structure if the existing project architecture has an established equivalent.

---

# 31. API ROUTER

Recommended:

```text
backend/app/api/career.py
```

Endpoints:

```text
POST /career
GET  /career/{career_id}
POST /career/{career_id}/advance
POST /career/{career_id}/decision
POST /career/{career_id}/pause
GET  /career/{career_id}/events
GET  /career/{career_id}/presentation
```

Not every endpoint must contain complex business logic.

The router must delegate to the career service.

---

# 32. API RESPONSIBILITIES

The API layer must:

* validate request data
* call application services
* map domain errors to HTTP responses
* serialize domain results
* never contain simulation algorithms

FastAPI must remain outside the simulation domain.

---

# 33. PAUSE

A lightweight pause mechanism may be implemented.

```text
POST /career/{career_id}/pause
```

Pausing must only affect session state.

It must not mutate career history or simulation facts.

---

# 34. PERSISTENCE

Phase 14 must **not introduce a new persistent database architecture**.

Initial implementation may keep career sessions in application memory if compatible with the existing application.

Do not introduce:

```text
PostgreSQL
Redis
Authentication
Accounts
Cloud Saves
```

unless an existing project requirement makes one strictly necessary.

Persistence can be designed in a future phase.

---

# 35. DETERMINISM

Determinism is mandatory.

Given:

```text
same initial career
+
same seed
+
same sequence of user decisions
```

the result must be identical.

Do not introduce:

```text
random.random()
random.choice()
hash()
uuid.uuid4()
datetime.now()
time.time()
```

or equivalent nondeterministic mechanisms.

Use the deterministic mechanisms already established in Phase 8.

---

# 36. ATOMICITY

Career progression must be atomic.

If processing fails:

```text
previous state
    ↓
ERROR
    ↓
previous state remains unchanged
```

A failed advance must not leave partial updates in:

* player state
* career history
* relationships
* milestones
* turning points
* career arcs
* narrative
* presentation

Where possible, reuse existing atomic processing guarantees from Phases 8–12.

---

# 37. IMMUTABILITY

Phase 14 domain objects must be immutable.

Do not mutate:

```text
CareerRecord
CareerEvent
CareerMilestone
CareerRelationship
CareerTurningPoint
CareerArc
NarrativeSeed
NarrativeStory
StoryScript
CareerPresentation
```

directly.

All state transitions must occur through the appropriate domain/application layer.

---

# 38. SECURITY

Do not introduce:

```text
eval
exec
compile
new Function
unsafe HTML injection
dynamic code execution
```

No arbitrary code execution.

No external network calls are required for Phase 14.

---

# 39. PERFORMANCE

Target:

```text
Career advance:
< 500 ms target
```

for normal local simulations.

The implementation should avoid unnecessary duplicate rebuilding of:

* narrative
* script
* presentation

when no relevant source data changed.

Performance optimizations must not compromise determinism.

---

# 40. ACCESSIBILITY

The interface must support:

* keyboard navigation
* visible focus states
* semantic buttons
* accessible labels
* sufficient text contrast
* decision options accessible without mouse
* modal/overlay focus handling
* reduced-motion preference where practical

Recording mode must not remove accessibility from interactive controls.

---

# 41. RESPONSIVE DESIGN

Desktop is the primary target.

Priority:

```text
1920 × 1080
1366 × 768
1280 × 720
```

Mobile should remain functionally usable but is not the main target of Phase 14.

---

# 42. FRONTEND COMPONENTS

Recommended new components:

```text
career-dashboard/
career-create/
career-event/
career-decision/
career-notification/
career-recording-mode/
```

Reuse existing Phase 13 components whenever possible.

---

# 43. CAREER DASHBOARD COMPONENT

Responsibilities:

* current player
* current club
* season
* OVR
* key metrics
* latest event
* career progression
* advance button

It must not contain simulation logic.

---

# 44. CAREER EVENT COMPONENT

Responsibilities:

* display event
* display event importance
* display source-derived text/data
* allow continuation

It must not generate events.

---

# 45. CAREER DECISION COMPONENT

Responsibilities:

* display decision
* display options
* submit selected option
* prevent invalid selections
* handle loading/error state

It must not calculate outcomes.

---

# 46. CAREER NOTIFICATION COMPONENT

Responsibilities:

* display recent meaningful changes
* allow dismissal where appropriate
* avoid visual clutter

---

# 47. CAREER CREATE COMPONENT

Responsibilities:

* gather minimal career setup data
* validate inputs
* submit career creation
* transition into active career

---

# 48. RECORDING MODE COMPONENT

Responsibilities:

* toggle recording-friendly UI
* hide unnecessary controls
* expose cinematic layout
* preserve all simulation functionality

---

# 49. TESTING — BACKEND

Create:

```text
backend/tests/test_career_phase14.py
backend/tests/test_career_14_audit.py
```

Tests must cover:

### Domain

* construction
* validation
* immutability

### Career Creation

* valid creation
* invalid creation

### Progression

* advance
* state transition
* event processing

### Decisions

* pending decision
* invalid option
* valid option
* blocked advancement while decision pending

### Completion

* completed career
* advancement after completion rejected

### Atomicity

* failed advance preserves previous state
* failed decision preserves previous state

### Determinism

* repeated execution
* 100x repeated execution
* cross-process execution

### Integration

```text
Phase 8
→ Phase 9
→ Phase 10
→ Phase 11
→ Phase 12
→ Phase 13
→ Phase 14
```

---

# 50. TESTING — FRONTEND

Tests must cover:

* career creation
* dashboard rendering
* advance button
* loading state
* event display
* decision display
* decision submission
* notifications
* navigation
* recording mode
* error states
* completion state

---

# 51. END-TO-END TEST

At least one complete integration test must execute:

```text
CREATE CAREER
      ↓
CAREER DASHBOARD
      ↓
ADVANCE
      ↓
SIMULATION
      ↓
EVENT
      ↓
CAREER HISTORY
      ↓
NARRATIVE
      ↓
SCRIPT
      ↓
PRESENTATION
      ↓
UPDATED UI
```

A decision path must also be tested:

```text
ADVANCE
   ↓
DECISION_REQUIRED
   ↓
SELECT OPTION
   ↓
EFFECT
   ↓
CAREER UPDATE
```

---

# 52. VISUAL VERIFICATION

Before Phase 14 is considered complete:

1. Start the backend.
2. Start the Angular application.
3. Create a career.
4. Enter the dashboard.
5. Advance the career several times.
6. Trigger an event.
7. Trigger a decision.
8. Resolve the decision.
9. Verify updated statistics.
10. Open Timeline.
11. Open Story.
12. Open Script.
13. Enable Recording Mode.
14. Capture screenshots at 1920×1080.

Visual verification must confirm:

* no broken layouts
* no overflowing text
* no console-breaking errors
* no navigation failures
* consistent branding
* visually coherent transitions
* readable typography
* recording-friendly composition

---

# 53. FILES EXPECTED

Backend:

```text
backend/app/career/__init__.py
backend/app/career/domain.py
backend/app/career/engine.py
backend/app/career/service.py
backend/app/career/exceptions.py
backend/app/api/career.py
backend/tests/test_career_phase14.py
backend/tests/test_career_14_audit.py
```

Frontend:

```text
frontend/football-life/src/app/career/career-dashboard/
frontend/football-life/src/app/career/career-create/
frontend/football-life/src/app/career/career-event/
frontend/football-life/src/app/career/career-decision/
frontend/football-life/src/app/career/career-notification/
frontend/football-life/src/app/career/career-recording-mode/
```

Potentially modified:

```text
backend/app/main.py
frontend/football-life/src/app/app.routes.ts
frontend/football-life/src/app/core/services/
frontend/football-life/src/styles.scss
```

Only modify existing files when necessary.

---

# 54. EXPLICIT NON-GOALS

Phase 14 must NOT implement:

* automatic video generation
* video editing
* voice synthesis
* AI narration
* automatic TikTok generation
* social media publishing
* authentication
* user accounts
* cloud persistence
* multiplayer
* online football data APIs
* advanced character creator
* advanced tactical UI
* 3D player models
* rendered football matches
* replay systems
* real-time multiplayer simulation

These are explicitly outside Phase 14.

---

# 55. ANTI-OVERENGINEERING RULE

This rule is mandatory.

If a proposed implementation introduces significant infrastructure that is not required for:

1. career progression,
2. user interaction,
3. visual feedback,
4. recording usability,

do not implement it in Phase 14.

Prefer:

```text
simple
deterministic
local
reusable
```

over:

```text
distributed
persistent
complex
over-engineered
```

---

# 56. DEFINITION OF DONE

Phase 14 is complete only when all of the following are true:

```text
[ ] User can create a career
[ ] User can enter the career dashboard
[ ] User can advance the career
[ ] Simulation progresses correctly
[ ] Events appear visually
[ ] Important events receive enhanced presentation
[ ] Decisions pause progression
[ ] User can resolve decisions
[ ] Decision effects are applied through Phase 8E
[ ] Career history updates through Phase 9
[ ] Narrative updates through Phase 10
[ ] Script updates through Phase 11
[ ] Presentation updates through Phase 12
[ ] Phase 13 views remain functional
[ ] Career completion works
[ ] Recording Mode works
[ ] Desktop layout is polished
[ ] Keyboard accessibility works
[ ] Error states work
[ ] Atomicity passes
[ ] Immutability passes
[ ] Determinism passes
[ ] Security audit passes
[ ] Backend tests pass
[ ] Frontend tests pass
[ ] Production Angular build passes
[ ] End-to-end integration passes
[ ] Visual browser verification passes
```

---

# 57. FINAL ARCHITECTURE

After Phase 14:

```text
                         FOOTBALL LIFE
                              │
                              ▼
                     CAREER EXPERIENCE
                              │
             ┌────────────────┴────────────────┐
             │                                 │
             ▼                                 ▼
        SIMULATION                            UI
             │                                 │
             ▼                                 ▼
        Phase 8–9                         Phase 13–14
             │                                 │
             ▼                                 │
       CAREER HISTORY                          │
             │                                 │
             ▼                                 │
       NARRATIVE ENGINE                        │
             │                                 │
             ▼                                 │
        SCRIPT ENGINE                          │
             │                                 │
             ▼                                 │
      PRESENTATION DATA ───────────────────────┘
```

The complete interactive loop becomes:

```text
CREATE PLAYER
      ↓
START CAREER
      ↓
SIMULATE
      ↓
EVENT
      ↓
DECISION
      ↓
CONSEQUENCE
      ↓
CAREER EVOLUTION
      ↓
NEW EVENTS
      ↓
NEW MILESTONES
      ↓
NEW STORY
      ↓
NEW PRESENTATION
      ↓
CAREER COMPLETE
```

---

# 58. PRODUCT OUTCOME

The intended product experience after Phase 14 is:

> **Football Life is a deterministic football career simulator where the user can follow a player's career, make meaningful decisions, watch the player's career evolve, and visually explore the story that emerges from the simulation.**

The application is not a video editor.

The application is the **world and career experience** from which the user can create their own recorded content.

---

# 59. IMPLEMENTATION PRIORITY

Jules must implement Phase 14 in this order:

```text
1. Career session/domain
        ↓
2. Career service
        ↓
3. Career progression orchestration
        ↓
4. Career API
        ↓
5. Career creation UI
        ↓
6. Career dashboard
        ↓
7. Event UI
        ↓
8. Decision UI
        ↓
9. Phase 13 integration
        ↓
10. Notifications
        ↓
11. Recording Mode
        ↓
12. Accessibility
        ↓
13. Tests
        ↓
14. End-to-end verification
        ↓
15. Visual verification
```

Do not implement later steps before the core career loop works.

---

# 60. FINAL CONSTRAINT

The most important requirement of Phase 14 is:

> **Make Football Life feel like a career simulator, not like a collection of technical systems.**

The user should be able to open the application, create a player, press **ADVANCE CAREER**, encounter events and decisions, see consequences, and progressively discover an interesting football career.

Everything else is secondary.
