# FOOTBALL LIFE

## PHASE 10 — NARRATIVE ENGINE & STORY ASSEMBLY

### Design Specification

**Version:** 1.0
**Project:** Football Life
**Phase:** 10
**Status:** Design Specification
**Primary responsibility:** Transform structured career history into a deterministic, factually grounded narrative structure suitable for future script and video generation.

---

# 1. PHASE 10 OBJECTIVE

Phase 10 introduces the **Narrative Engine & Story Assembly**.

Its responsibility is to transform the structured career information produced by Phase 9 into a coherent narrative representation.

The engine must identify:

* the player's origin;
* the beginning of the journey;
* important developments;
* conflicts;
* setbacks;
* breakthroughs;
* achievements;
* relationships;
* turning points;
* peak moments;
* decline or resolution;
* legacy.

The output is a **structured story**, not yet a final video script.

---

# 2. CORE TRANSFORMATION

The architecture is:

```text
PHASE 8
Simulation
"What happened?"
        ↓
PHASE 9
Career History
"What did it mean?"
        ↓
PHASE 10
Narrative Engine
"How should the career be structured as a story?"
        ↓
FUTURE PHASE
Script / Voice / Video
"How should the story be presented?"
```

---

# 3. FUNDAMENTAL PRINCIPLE

Phase 10 must transform facts into narrative structure without fabricating facts.

It may determine:

```text
importance
sequence
focus
contrast
pacing
dramatic structure
character emphasis
story arcs
```

It must NOT fabricate:

```text
events
quotes
thoughts
private conversations
motivations
relationships
injuries
transfers
achievements
statistics
```

unless those facts exist in the underlying simulation history.

---

# 4. PHASE BOUNDARY

Phase 10 MUST NOT:

* modify simulation state;
* apply effects;
* calculate probabilities;
* resolve events;
* create new simulation events;
* persist directly to the database;
* call FastAPI;
* call Angular;
* call external APIs;
* call an LLM;
* generate audio;
* generate video;
* render images;
* publish social media content.

Phase 10 is a pure narrative transformation layer.

---

# 5. INPUTS

Phase 10 consumes:

```text
CareerRecord
CareerEvent
CareerMilestone
CareerRelationship
CareerTurningPoint
CareerArc
NarrativeSeed
```

Optional contextual information may include:

```text
PlayerState
Club information
Competition information
Season information
Career statistics
```

Existing domain objects must be reused.

Do not duplicate Phase 9 models.

---

# 6. OUTPUT

The primary output is:

```text
NarrativeStory
```

The story contains structured sections and narrative beats.

Suggested structure:

```text
NarrativeStory
├── story_id
├── player_id
├── title_context
├── premise
├── protagonist
├── timeline
├── acts
├── narrative_beats
├── featured_events
├── featured_relationships
├── featured_milestones
├── featured_turning_points
├── featured_arcs
├── ending
├── themes
└── metadata
```

All domain objects must be immutable.

---

# 7. NARRATIVE STORY

`NarrativeStory` represents the complete structured narrative of the player's career.

It should not contain final prose paragraphs.

Instead it describes:

```text
what should be mentioned
when it should appear
why it matters
which facts support it
```

---

# 8. STORY PREMISE

A `StoryPremise` represents the central narrative concept.

Example conceptual structure:

```text
StoryPremise
├── premise_type
├── primary_arc
├── central_conflict
├── protagonist_goal
├── resolution_type
└── supporting_facts
```

The premise must remain factually grounded.

Possible premise types:

```text
RISE
COMEBACK
UNDERDOG
TRIUMPH
TRAGEDY
REDEMPTION
RIVALRY
LOYALTY
JOURNEY
LEGACY
```

The engine may select the most appropriate type based on structured career data.

---

# 9. PROTAGONIST PROFILE

The narrative engine may create a structured protagonist representation.

Example:

```text
NarrativeProtagonist
├── player_id
├── position
├── origin
├── career_stage
├── key_traits
├── important_clubs
├── important_relationships
└── defining_events
```

Traits must be based on simulation data.

Do not invent psychological characteristics without supporting data.

---

# 10. NARRATIVE ACTS

The story should be divided into narrative acts.

Initial model:

```text
ACT 1 — ORIGIN
ACT 2 — RISE
ACT 3 — CONFLICT
ACT 4 — BREAKTHROUGH
ACT 5 — PEAK
ACT 6 — RESOLUTION
```

Not every career requires every act.

Short careers may contain fewer acts.

Long careers may contain more detailed sections.

---

# 11. ACT TYPES

Define:

```text
ORIGIN
SETUP
RISE
CONFLICT
CRISIS
BREAKTHROUGH
PEAK
FALL
RECOVERY
RESOLUTION
LEGACY
```

Acts must be determined from career history.

---

# 12. NARRATIVE BEATS

A `NarrativeBeat` represents a single storytelling unit.

Suggested structure:

```text
NarrativeBeat
├── beat_id
├── beat_type
├── sequence
├── importance
├── source_event_ids
├── source_milestone_ids
├── source_turning_point_ids
├── source_seed_ids
├── emotional_direction
├── narrative_function
└── factual_context
```

No prose is required at this stage.

---

# 13. NARRATIVE BEAT TYPES

Initial types:

```text
INTRODUCTION
ORIGIN
FIRST_CHANCE
EARLY_SUCCESS
SETBACK
CONFLICT
RIVAL_APPEARANCE
BREAKTHROUGH
MAJOR_ACHIEVEMENT
CRISIS
COMEBACK
CLIMAX
PEAK
DECLINE
FINAL_CHAPTER
LEGACY
```

---

# 14. NARRATIVE FUNCTION

Each beat may have a narrative function:

```text
SETUP
ESCALATION
CONTRAST
CONFLICT
TRANSITION
PAYOFF
CLIMAX
RESOLUTION
REFLECTION
```

This allows future script generation to understand why the beat exists.

---

# 15. EMOTIONAL DIRECTION

Phase 10 may represent emotional direction as structured metadata.

Suggested values:

```text
NEUTRAL
POSITIVE
NEGATIVE
TENSION
HOPE
TRIUMPH
LOSS
UNCERTAINTY
RELIEF
BITTERSWEET
```

This does not represent the player's actual feelings.

It represents the intended narrative tone of the event sequence.

This distinction must remain explicit.

---

# 16. FACTUAL CONTEXT

Every important narrative beat must reference its source facts.

Example:

```text
NarrativeBeat
    ↓
source_event_ids
source_milestone_ids
source_turning_point_ids
source_seed_ids
```

This creates traceability.

Future narrative generation must be able to answer:

> "Which simulation facts produced this narrative statement?"

---

# 17. STORY SELECTION

Not every career event should appear in the final story.

Phase 10 must select relevant material.

Selection factors include:

```text
event significance
milestone significance
turning-point importance
arc importance
narrative seed priority
rarity
career impact
relationship importance
chronological relevance
```

The selection must be deterministic.

---

# 18. STORY DENSITY

Introduce configurable narrative density.

Possible values:

```text
COMPACT
STANDARD
DETAILED
COMPLETE
```

Example:

```text
COMPACT
≈ only major career events

STANDARD
≈ major events + important context

DETAILED
≈ major events + secondary developments

COMPLETE
≈ complete structured career history
```

No prose generation occurs.

---

# 19. STORY LENGTH TARGET

The engine may support a target narrative duration.

Example:

```text
target_duration_seconds
```

This is metadata only.

Phase 10 may use it to select an appropriate number of beats.

It must not generate the final spoken script.

---

# 20. NARRATIVE WEIGHT

Every selected narrative component should have a deterministic weight.

Conceptually:

```text
narrative_weight =
    significance
  + milestone_importance
  + turning_point_importance
  + arc_importance
  + seed_priority
  + contextual_importance
```

Weights must be bounded and deterministic.

---

# 21. CENTRAL CONFLICT

A story may contain one or more conflicts.

Represent:

```text
NarrativeConflict
├── conflict_id
├── conflict_type
├── source_events
├── start_sequence
├── end_sequence
├── intensity
└── resolution_status
```

Possible conflict types:

```text
SPORTING
CAREER
TRANSFER
COMPETITIVE
RELATIONSHIP
PERFORMANCE
INJURY
STATUS
INTERNATIONAL
```

Only create conflicts supported by career history.

---

# 22. CONFLICT LIFECYCLE

Conflicts may follow:

```text
INTRODUCED
ESCALATING
PEAK
RESOLVED
UNRESOLVED
ABANDONED
```

This gives future narrative systems a structured dramatic trajectory.

---

# 23. RELATIONSHIP NARRATIVES

Important relationships may become narrative threads.

Examples:

```text
MENTOR
RIVAL
MANAGER
TEAMMATE
CLUB
NATIONAL_TEAM
```

A relationship should only become a major narrative thread if it has sufficient narrative importance.

---

# 24. RIVALRY NARRATIVES

A rivalry should be represented through multiple supporting facts where possible.

Example:

```text
Rivalry
    ↓
first encounter
    ↓
competitive escalation
    ↓
major confrontation
    ↓
resolution / continuation
```

The engine must not invent verbal confrontation or personal hatred.

---

# 25. CAREER ARC INTEGRATION

Phase 10 consumes Phase 9 career arcs.

For each arc:

```text
CareerArc
    ↓
relevant events
    ↓
relevant milestones
    ↓
turning points
    ↓
narrative beats
```

Career arcs should form the backbone of the narrative structure.

---

# 26. TURNING POINT INTEGRATION

Turning points should receive higher narrative priority.

A turning point may produce:

```text
setup beat
turning-point beat
consequence beat
```

where the supporting events exist.

---

# 27. MILESTONE INTEGRATION

Important milestones can act as narrative anchors.

Examples:

```text
FIRST_GOAL
FIRST_TEAM_DEBUT
FIRST_TROPHY
MAJOR_AWARD
MAJOR_TRANSFER
RECORD
CAREER_PEAK
RETIREMENT
```

Not every milestone must appear.

Selection depends on narrative importance and target density.

---

# 28. STORY OPENING

The story opening should be represented structurally.

Possible opening strategies:

```text
CHRONOLOGICAL_ORIGIN
COLD_OPEN
MAJOR_ACHIEVEMENT
CAREER_CONTRAST
MYSTERY
RIVALRY
CRISIS
```

A cold open may reference a major later event before returning to the beginning.

However, all referenced facts must exist.

---

# 29. COLD OPEN

If supported, a cold open should identify:

```text
opening_event
follow_up_origin
```

Example structure:

```text
Major Event
    ↓
"How did he get here?"
    ↓
Origin
```

No actual prose is generated.

---

# 30. STORY CLIMAX

The engine should identify a climax candidate.

Potential candidates:

```text
major trophy
career-defining performance
major transfer
record
comeback
rivalry resolution
career peak
international breakthrough
```

The climax must be derived from narrative weights.

---

# 31. STORY RESOLUTION

The resolution should represent how the career currently ends.

Possible resolution types:

```text
TRIUMPH
LEGACY
RETIREMENT
DECLINE
UNRESOLVED
ONGOING
COMEBACK
```

For active players:

```text
ONGOING
```

may be the correct result.

The engine must not pretend the career has ended when simulation history shows it is ongoing.

---

# 32. LEGACY

Legacy information may include:

```text
major achievements
records
clubs
international impact
career arc
important relationships
historical significance
```

Legacy should be structured metadata.

Do not generate subjective claims such as "one of the greatest ever" unless the simulation explicitly supports such classification.

---

# 33. THEMES

The engine may derive recurring narrative themes.

Possible themes:

```text
PERSEVERANCE
AMBITION
LOYALTY
RIVALRY
RECOVERY
ADVERSITY
SUCCESS
SACRIFICE
CHANGE
LEGACY
```

Themes must be derived from repeated structured patterns.

Do not infer unsupported psychological traits.

---

# 34. NARRATIVE COHERENCE

The final story should satisfy:

```text
chronological coherence
causal coherence
character continuity
fact consistency
arc continuity
relationship continuity
```

A later event should not contradict earlier established facts.

---

# 35. CAUSAL LINKS

Where supported, narrative beats may reference causal relationships.

Example:

```text
Event A
   ↓
state change
   ↓
Event B
```

The engine may record:

```text
caused_by
consequence_of
enabled_by
followed_by
```

Only use explicit simulation relationships where available.

Do not invent causality merely because events occurred near each other.

---

# 36. NARRATIVE THREADS

A `NarrativeThread` may connect multiple beats around a shared subject.

Examples:

```text
CAREER_RISE
RIVALRY
CLUB_LOYALTY
INTERNATIONAL_CAREER
RECOVERY
PERFORMANCE
TRANSFER_JOURNEY
```

A thread contains:

```text
thread_id
thread_type
beat_ids
start_sequence
end_sequence
importance
status
```

---

# 37. THREAD PRIORITIZATION

Not every thread should appear in a short narrative.

Rank threads using deterministic:

```text
importance
duration
event count
turning points
milestones
narrative weight
```

---

# 38. NARRATIVE PACING

Phase 10 should model pacing structurally.

Suggested pacing values:

```text
SLOW
MODERATE
FAST
CLIMACTIC
REFLECTIVE
```

Pacing may be assigned to beats or acts.

It represents future presentation rhythm.

It does not generate timing or audio.

---

# 39. CONTRAST

Strong narratives often require contrast.

The engine may identify structured contrasts:

```text
success → failure
failure → recovery
unknown → famous
academy → superstar
club loyalty → transfer
injury → comeback
rivalry → reconciliation
```

Contrast must be based on real career transitions.

---

# 40. REPETITION CONTROL

The narrative engine must avoid repeatedly selecting the same information.

For example:

```text
same event
same milestone
same achievement
same relationship
```

should not produce redundant narrative beats unless intentionally serving different narrative functions.

---

# 41. STORY DEDUPLICATION

Every narrative component must have a deterministic identity.

Do not use random UUIDs.

Recommended:

```text
SHA-256
```

derived from stable source identifiers.

---

# 42. DETERMINISM

Given identical:

```text
CareerRecord
configuration
target density
target duration
```

Phase 10 must produce identical:

```text
NarrativeStory
NarrativeActs
NarrativeBeats
NarrativeThreads
NarrativeConflicts
```

No uncontrolled randomness.

---

# 43. CROSS-PROCESS DETERMINISM

Where practical, verify:

```text
single process
100 repeated runs
cross-process execution
```

using deterministic serialization.

Avoid:

```text
random
hash()
uuid.uuid4()
timestamps
process IDs
memory addresses
unordered iteration
```

---

# 44. IMMUTABILITY

All narrative domain objects must be immutable.

Processing:

```text
CareerRecord
    ↓
NarrativeStory
```

must not mutate the CareerRecord.

Nested collections must also be protected.

---

# 45. ATOMICITY

If narrative construction fails:

```text
CareerRecord
```

must remain unchanged.

No partially constructed narrative should be returned as a successful result.

---

# 46. REPLAYABILITY

The same CareerRecord must always produce the same NarrativeStory.

Conceptually:

```text
CareerRecord
    ↓
Narrative Engine
    ↓
Story A

same CareerRecord
    ↓
Narrative Engine
    ↓
Story B
```

must satisfy:

```text
A == B
```

including serialized output.

---

# 47. CONFIGURATION

Narrative configuration should be centralized.

Possible configuration:

```text
data/rules/narrative.json
```

Potential values:

```text
significance weights
beat weights
act thresholds
thread thresholds
theme thresholds
story density
target durations
opening strategy weights
climax thresholds
```

Do not hard-code large collections of narrative rules inside Python.

Use existing project configuration conventions where appropriate.

---

# 48. NO LLM DEPENDENCY

Phase 10 must remain fully functional without:

```text
OpenAI
LLM APIs
internet
external AI services
```

The engine must produce a complete structured narrative using deterministic local logic.

An LLM may be introduced in a future phase as a presentation layer.

---

# 49. NO PROSE REQUIREMENT

Phase 10 may optionally contain short structured labels.

However, the primary output must remain machine-readable.

Avoid generating large natural-language paragraphs.

Future script generation will consume the structured story.

---

# 50. SERIALIZATION

All Phase 10 domain objects must support deterministic JSON serialization through existing project conventions.

At minimum:

```text
NarrativeStory
StoryPremise
NarrativeProtagonist
NarrativeAct
NarrativeBeat
NarrativeConflict
NarrativeThread
```

must serialize deterministically.

---

# 51. PUBLIC API

Expose intended Phase 10 APIs through the appropriate `app.event` domain package.

Potential functions:

```python
build_narrative_story(...)
select_narrative_events(...)
build_narrative_acts(...)
build_narrative_beats(...)
build_narrative_threads(...)
identify_narrative_conflicts(...)
select_story_opening(...)
identify_story_climax(...)
build_story_resolution(...)
```

Exact naming should follow repository conventions.

---

# 52. COMPLETE PIPELINE

Provide a high-level orchestration function:

```python
build_narrative_story(
    career_record,
    configuration=None,
    target_duration_seconds=None,
    density=STANDARD,
) -> NarrativeStory
```

The orchestration should:

```text
validate input
    ↓
analyze career
    ↓
select relevant material
    ↓
identify premise
    ↓
build acts
    ↓
build beats
    ↓
build threads
    ↓
identify conflicts
    ↓
select opening
    ↓
select climax
    ↓
build resolution
    ↓
derive themes
    ↓
validate coherence
    ↓
return immutable NarrativeStory
```

---

# 53. VALIDATION

The final story must validate:

```text
all source references exist
beat order is valid
act order is valid
no duplicate IDs
no contradictory source references
opening exists where required
resolution exists
climax exists when sufficient data exists
all referenced events belong to CareerRecord
```

---

# 54. EMPTY CAREER

An empty career record must be handled explicitly.

Possible result:

```text
EMPTY_STORY
```

or a valid minimal `NarrativeStory`.

Do not fabricate an origin story.

---

# 55. SHORT CAREERS

The engine must handle careers with very little data.

Example:

```text
debut
few events
retirement
```

The story should contain only supported material.

Do not force missing acts.

---

# 56. LONG CAREERS

Long careers must be compressible.

The engine must avoid producing thousands of narrative beats when the target density is compact.

Selection must prioritize:

```text
turning points
major milestones
high-significance events
important relationships
career arc transitions
```

---

# 57. ACTIVE CAREERS

For active players:

```text
resolution_type = ONGOING
```

unless the data explicitly indicates retirement or career completion.

The engine must not invent an ending.

---

# 58. FAILED NARRATIVE BUILD

If required input validation fails:

```text
NarrativeBuildResult
success = False
error = explicit typed error
story = None
```

or the project's established error convention.

Do not silently produce incomplete narratives.

---

# 59. ERROR HANDLING

Potential error codes:

```text
INVALID_CAREER_RECORD
INVALID_EVENT_REFERENCE
INVALID_MILESTONE_REFERENCE
INVALID_TURNING_POINT_REFERENCE
INVALID_ARC_REFERENCE
INVALID_RELATIONSHIP_REFERENCE
INVALID_CONFIGURATION
EMPTY_INPUT
NARRATIVE_VALIDATION_ERROR
NARRATIVE_BUILD_ERROR
```

Errors must be explicit and deterministic.

---

# 60. TESTING STRATEGY

Create dedicated Phase 10 tests.

## Domain tests

Test:

```text
NarrativeStory
StoryPremise
NarrativeProtagonist
NarrativeAct
NarrativeBeat
NarrativeConflict
NarrativeThread
```

including validation and immutability.

---

# 61. STORY SELECTION TESTS

Test:

* event ranking;
* density modes;
* target duration;
* major event selection;
* deduplication;
* deterministic ranking.

---

# 62. ACT TESTS

Test:

* origin;
* rise;
* conflict;
* breakthrough;
* peak;
* resolution;
* missing acts;
* non-linear careers.

---

# 63. BEAT TESTS

Test:

* beat creation;
* ordering;
* source references;
* narrative functions;
* emotional direction;
* pacing;
* duplicate prevention.

---

# 64. THREAD TESTS

Test:

* thread creation;
* event grouping;
* relationship threads;
* rivalry threads;
* career threads;
* deterministic prioritization.

---

# 65. CONFLICT TESTS

Test:

* conflict creation;
* escalation;
* peak;
* resolution;
* unresolved conflict;
* deterministic conflict detection.

---

# 66. OPENING TESTS

Test:

```text
chronological opening
cold open
major achievement opening
career contrast opening
```

using deterministic selection.

---

# 67. CLIMAX TESTS

Test:

* trophy climax;
* breakthrough climax;
* comeback climax;
* record climax;
* peak performance climax;
* absence of sufficient climax data.

---

# 68. RESOLUTION TESTS

Test:

```text
retired player
active player
declining career
ongoing career
comeback career
```

---

# 69. FACTUAL GROUNDING TESTS

Verify that every narrative component references actual source data.

Explicitly test that Phase 10 cannot produce unsupported:

```text
events
relationships
achievements
quotes
motivations
statistics
```

---

# 70. IMMUTABILITY TESTS

Verify:

```text
CareerRecord unchanged
nested CareerRecord structures unchanged
Phase 9 objects unchanged
```

after narrative generation.

---

# 71. DETERMINISM TESTS

Run:

```text
1x
10x
100x
```

with identical inputs.

Verify byte-identical serialized outputs.

Where practical, verify independent process execution.

---

# 72. REPLAY / REBUILD TESTS

Build a story from a CareerRecord.

Build it again from the exact same CareerRecord.

Verify:

```text
Story A == Story B
```

and serialized outputs are identical.

---

# 73. END-TO-END TEST

At least one integration test must execute:

```text
Phase 8
    ↓
Phase 9
    ↓
Phase 10
```

using real domain objects.

Expected:

```text
Simulation
    ↓
Event Resolution
    ↓
Effect Application
    ↓
Career History
    ↓
Narrative Story
```

Do not replace real intermediate objects with unrelated mocks if actual domain objects can be used.

---

# 74. PHASE 8 REGRESSION

All Phase 8 tests must continue passing.

Verify:

```text
8A
8B
8C
8D
8E
8F
```

---

# 75. PHASE 9 REGRESSION

All Phase 9 tests must continue passing.

Verify:

```text
Career History
Milestones
Relationships
Turning Points
Career Arcs
Narrative Seeds
```

remain unchanged.

---

# 76. FULL TEST SUITE

Run:

```bash
pytest
```

and report exact results.

---

# 77. SECURITY

Phase 10 must not execute arbitrary code.

Do NOT use:

```text
eval
exec
compile
```

Do not dynamically execute narrative rules.

All narrative selection must use deterministic local logic.

---

# 78. PERFORMANCE

Phase 10 must remain lightweight enough for local simulation.

Prefer:

```text
O(n)
O(n log n)
```

style processing where practical.

Avoid repeatedly scanning the entire career history unnecessarily.

---

# 79. PERSISTENCE BOUNDARY

No direct dependency on:

```text
SQLAlchemy
SQLite
Alembic
database sessions
```

Phase 10 should operate entirely on in-memory domain objects.

---

# 80. API / FRONTEND BOUNDARY

No dependency on:

```text
FastAPI
Angular
HTTP
frontend state
```

The narrative engine must function independently.

---

# 81. PHASE RESPONSIBILITY MODEL

The final architecture must remain:

```text
8A
Event Domain
    ↓
8B
Candidate Generation
    ↓
8C
Conditions & Probability
    ↓
8D
Resolution
    ↓
8F
Decision
    ↓
8E
Effect Application
    ↓
Simulation State
    ↓
9
Career History
    ↓
10
Narrative Structure
    ↓
Future
Script / Voice / Video
```

The responsibilities are:

```text
8E = CHANGE STATE

9 = RECORD + INTERPRET CAREER

10 = STRUCTURE STORY

Future = PRESENT STORY
```

---

# 82. NON-GOALS

Do NOT implement:

```text
LLM generation
natural-language script generation
voice generation
text-to-speech
video generation
image generation
TikTok API
social media publishing
database persistence
frontend UI
```

---

# 83. IMPLEMENTATION ORDER

Recommended order:

```text
1. Domain primitives
2. NarrativeStory
3. Story selection
4. Premise detection
5. Protagonist structure
6. Act construction
7. Beat construction
8. Thread construction
9. Conflict construction
10. Opening selection
11. Climax selection
12. Resolution construction
13. Theme detection
14. Coherence validation
15. Density / duration support
16. Serialization
17. Integration tests
18. Regression tests
19. Full audit
```

---

# 84. FINAL INVARIANTS

Phase 10 must guarantee:

```text
DETERMINISTIC
```

```text
IMMUTABLE
```

```text
ATOMIC
```

```text
FACTUALLY GROUNDED
```

```text
REPLAYABLE
```

```text
TRACEABLE
```

```text
PHASE-BOUNDARY SAFE
```

---

# 85. DEFINITION OF DONE

Phase 10 is complete only when:

* all required narrative domain models exist;
* CareerRecord can be transformed into NarrativeStory;
* narrative selection is deterministic;
* story density works;
* target duration metadata is supported;
* premise detection works;
* acts are generated;
* beats are generated;
* threads are generated;
* conflicts are detected;
* opening is selected;
* climax is selected;
* resolution is generated;
* themes are derived;
* source traceability is preserved;
* duplicate information is controlled;
* factual grounding is enforced;
* immutable inputs are preserved;
* processing is atomic;
* serialization is deterministic;
* replay produces identical output;
* cross-process determinism is verified where practical;
* Phase 8 regression passes;
* Phase 9 regression passes;
* Phase 8 → 9 → 10 integration passes;
* full test suite passes;
* no LLM or external AI dependency exists;
* no database/API/frontend coupling exists;
* no final prose or video generation exists.

---

# 86. FINAL REPORT REQUIREMENTS

When implementation is complete, report:

## Implementation Status

```text
COMPLETE
```

or:

```text
BLOCKED
```

## Implemented

List all Phase 10 domain primitives and processing functions.

## Narrative Pipeline

Explain:

```text
CareerRecord
    ↓
NarrativeStory
    ↓
Acts
    ↓
Beats
    ↓
Threads
    ↓
Conflict
    ↓
Opening
    ↓
Climax
    ↓
Resolution
```

## Phase Boundaries

Confirm:

```text
8E = state application
9 = career history / interpretation
10 = narrative structure
```

## Tests

Report:

```text
Phase 10:
X passed / Y failed

Phase 9 regression:
X passed / Y failed

Phase 8 regression:
X passed / Y failed

Integration:
X passed / Y failed

Full suite:
X passed / Y failed
```

## Determinism

Report:

```text
single-process
repeated execution
cross-process
rebuild/replay
end-to-end
```

## Immutability

```text
PASS / FAIL
```

## Atomicity

```text
PASS / FAIL
```

## Factual Grounding

```text
PASS / FAIL
```

## Traceability

```text
PASS / FAIL
```

## Serialization

```text
PASS / FAIL
```

## Files Changed

List every modified or created file.

Classify:

```text
EXPECTED
NECESSARY
UNRELATED
```

## Findings

List remaining concerns.

## Final Recommendation

Choose:

```text
READY FOR PHASE 10 AUDIT
```

or:

```text
PHASE 10 REQUIRES FIXES
```

---

# 87. FINAL ARCHITECTURAL VISION

Football Life must ultimately preserve this pipeline:

```text
┌─────────────────────────────────────────────┐
│                 SIMULATION                  │
│                                             │
│  8A → 8B → 8C → 8D → 8F → 8E              │
│                                             │
│             WHAT HAPPENED?                  │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│              CAREER HISTORY                 │
│                                             │
│  Events → Milestones → Relationships        │
│          → Turning Points → Arcs             │
│          → Narrative Seeds                  │
│                                             │
│             WHAT DID IT MEAN?               │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│             NARRATIVE ENGINE                │
│                                             │
│  Premise → Acts → Beats → Threads           │
│          → Conflict → Climax → Resolution   │
│                                             │
│          HOW SHOULD IT BE TOLD?             │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│              FUTURE PHASES                  │
│                                             │
│      Script → Voice → Visuals → Video       │
│                                             │
│             HOW DO WE PRESENT IT?           │
└─────────────────────────────────────────────┘
```

The separation between **simulation**, **career interpretation**, **narrative structure**, and **final presentation** is a core architectural invariant of Football Life.
