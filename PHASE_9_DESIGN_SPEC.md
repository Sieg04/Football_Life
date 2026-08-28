# FOOTBALL LIFE

## PHASE 9 — CAREER HISTORY & NARRATIVE FOUNDATION

### Design Specification

**Version:** 1.0
**Project:** Football Life
**Phase:** 9
**Status:** Design Specification
**Primary responsibility:** Convert simulation events and state transitions into a deterministic, structured career history and narrative foundation.

---

# 1. PHASE 9 OBJECTIVE

Phase 9 introduces the **Career History & Narrative Foundation Engine**.

Its responsibility is to transform the structured results produced by the simulation and Phase 8 Event Engine into a persistent, deterministic representation of the player's career history.

Phase 9 does **NOT** generate natural-language storytelling.

It creates the structured information that future narrative systems can consume.

The fundamental transformation is:

```text
PHASE 8
Structured Simulation Events
        ↓
PHASE 9
Career History
        ↓
Career Significance
        ↓
Milestones
        ↓
Relationships
        ↓
Turning Points
        ↓
Career Arcs
        ↓
Narrative Seeds
```

---

# 2. CORE PRINCIPLE

Phase 9 must answer:

> "What does what happened mean for this player's career?"

Phase 8 answers:

```text
WHAT HAPPENED?
```

Phase 9 answers:

```text
WHAT DID IT MEAN?
```

Future narrative phases will answer:

```text
HOW SHOULD IT BE TOLD?
```

Therefore:

```text
8 = Event Simulation
9 = Career Interpretation
10+ = Narrative Generation
```

---

# 3. PHASE BOUNDARY

Phase 9 MUST NOT:

* generate prose;
* generate dialogue;
* generate narration;
* generate TikTok scripts;
* call an LLM;
* produce final storytelling;
* render video;
* access frontend state;
* directly modify simulation state;
* directly apply effects;
* recalculate event probability;
* re-resolve events.

Phase 9 is a **read/interpret/record layer** over simulation results.

---

# 4. INPUTS

Phase 9 consumes structured simulation information.

Primary inputs include:

```text
EventResult
EventResolution
DecisionResult
EffectApplicationResult
Simulation State
Player State
Season / Date
Club
Competition
Country
Career Context
```

The exact types must reuse existing domain models wherever possible.

Phase 9 must not create duplicate versions of Phase 8 domain objects.

---

# 5. OUTPUTS

Phase 9 produces structured career information.

Core concepts:

```text
CareerRecord
CareerEvent
CareerMilestone
CareerRelationship
CareerTurningPoint
CareerArc
NarrativeSeed
```

The exact implementation must follow existing project conventions for:

* immutable dataclasses;
* enums;
* validation;
* serialization;
* deterministic identifiers;
* public exports.

---

# 6. CAREER RECORD

`CareerRecord` represents the structured history of one player's career.

Conceptually:

```python
CareerRecord(
    player_id,
    events,
    milestones,
    relationships,
    turning_points,
    arcs,
    narrative_seeds
)
```

The record must be immutable from the perspective of the domain layer.

Updates must return a new record rather than mutating the existing instance.

---

# 7. CAREER EVENT

A `CareerEvent` represents a significant simulation event recorded in the player's career history.

Suggested structure:

```text
CareerEvent
├── event_id
├── source_event_id
├── player_id
├── season
├── date / sequence
├── event_type
├── category
├── significance
├── summary_data
├── state_changes
├── participants
├── clubs
├── competitions
└── tags
```

The object must contain structured data rather than generated prose.

---

# 8. EVENT CATEGORIES

Phase 9 should support extensible event categorization.

Initial categories may include:

```text
TRANSFER
CONTRACT
DEBUT
APPEARANCE
GOAL
ASSIST
INJURY
RECOVERY
FORM_CHANGE
PERFORMANCE
AWARD
TROPHY
PROMOTION
RELEGATION
INTERNATIONAL
RELATIONSHIP
RIVALRY
CONTROVERSY
DECISION
BREAKTHROUGH
SETBACK
RETIREMENT
OTHER
```

Do not over-specialize the engine for every possible football scenario.

Categories should remain extensible.

---

# 9. EVENT SIGNIFICANCE

Not every simulation event should have equal narrative importance.

Introduce a deterministic significance model.

Suggested levels:

```text
TRIVIAL
MINOR
MODERATE
MAJOR
CRITICAL
LEGENDARY
```

Significance must be derived from structured inputs.

It must NOT use:

```text
randomness
LLM judgement
subjective prose analysis
timestamps
```

---

# 10. SIGNIFICANCE FACTORS

Possible deterministic factors include:

```text
sporting impact
career impact
financial impact
reputation impact
relationship impact
competition importance
club importance
rarity
state change magnitude
milestone proximity
career stage
```

The exact formula should remain deterministic and configurable.

Example conceptual model:

```text
significance =
    sporting_weight
  + career_weight
  + reputation_weight
  + relationship_weight
  + rarity_weight
  + context_weight
```

The implementation must define explicit bounds.

---

# 11. EVENT DEDUPLICATION

Phase 9 must avoid recording the same underlying event multiple times.

Every recorded event must have a deterministic identity.

Possible identity:

```text
source_event_id
+
player_id
+
sequence
```

or another deterministic composite defined during implementation.

Do NOT use:

```text
uuid.uuid4()
timestamp-based IDs
random IDs
```

for identity.

---

# 12. CAREER TIMELINE

Phase 9 must maintain a deterministic chronological timeline.

Events must be ordered using explicit fields.

Preferred ordering:

```text
season
date / simulation tick
sequence
event_id
```

Never rely on:

```text
Python set ordering
dictionary iteration assumptions
memory identity
```

for career chronology.

---

# 13. CAREER MILESTONES

A `CareerMilestone` represents an important achievement or threshold.

Examples:

```text
FIRST_TEAM_DEBUT
FIRST_GOAL
FIRST_ASSIST
FIRST_TRANSFER
FIRST_INTERNATIONAL_APPEARANCE
FIRST_TROPHY
FIRST_MAJOR_AWARD
100_APPEARANCES
50_GOALS
100_GOALS
CLUB_CAPTAINCY
NATIONAL_TEAM_CAPTAINCY
MAJOR_TRANSFER
RECORD_BROKEN
CAREER_BEST_SEASON
RETIREMENT
```

Milestones must be detected deterministically from career history and/or state transitions.

---

# 14. MILESTONE UNIQUENESS

Where a milestone is inherently unique, such as:

```text
FIRST_GOAL
FIRST_TROPHY
FIRST_INTERNATIONAL_APPEARANCE
```

it must not be emitted repeatedly.

Repeated achievements such as:

```text
100_GOALS
200_GOALS
```

may generate separate milestones where explicitly defined.

---

# 15. MILESTONE CONTEXT

Milestones should preserve structured context.

Example:

```text
CareerMilestone
├── milestone_type
├── season
├── event_id
├── club_id
├── competition_id
├── value
└── significance
```

Do not store narrative prose.

---

# 16. CAREER RELATIONSHIPS

Phase 9 introduces structured relationships between the player and other entities.

Possible relationship types:

```text
TEAMMATE
MANAGER
MENTOR
RIVAL
FRIEND
COMPETITOR
CLUB
NATIONAL_TEAM
```

The initial implementation should prioritize relationships directly supported by existing simulation data.

Do not invent relationship mechanics that the simulation cannot currently support.

---

# 17. RELATIONSHIP STATE

A relationship may contain:

```text
relationship_id
source_entity
target_entity
relationship_type
strength
status
start_sequence
last_updated_sequence
event_ids
```

Relationship strength must be deterministic.

Possible normalized range:

```text
[-1.0, 1.0]
```

where:

```text
-1.0 = strongly negative
 0.0 = neutral
+1.0 = strongly positive
```

---

# 18. RELATIONSHIP EVOLUTION

Relationships may evolve in response to relevant events.

Examples:

```text
successful collaboration
conflict
competition
betrayal
support
transfer
shared achievement
```

However, Phase 9 must only update relationships when the source event contains sufficient structured information.

Never infer unsupported relationships from arbitrary text.

---

# 19. RIVALRIES

A rivalry may be represented as a specialized relationship.

A rivalry can emerge when repeated competitive interactions satisfy deterministic thresholds.

Possible factors:

```text
frequency
competitive intensity
negative interaction score
importance
direct encounters
```

The exact formula must be deterministic.

Do not implement a complete social simulation in Phase 9.

---

# 20. CAREER TURNING POINTS

A `CareerTurningPoint` represents an event or sequence that materially changes the direction of the career.

Examples:

```text
BREAKTHROUGH
MAJOR_TRANSFER
SERIOUS_SETBACK
CAREER_RECOVERY
MAJOR_TROPHY
LOSS_OF_STARTING_POSITION
MANAGER_CHANGE
INTERNATIONAL_BREAKTHROUGH
CAREER_DECLINE
RETIREMENT_DECISION
```

Turning points must be derived from structured career information.

---

# 21. TURNING POINT DETECTION

A turning point may be triggered by:

```text
large state change
significant event
milestone
club change
role change
reputation change
performance trajectory change
relationship change
```

The detection algorithm must be deterministic.

Avoid subjective narrative interpretation.

---

# 22. CAREER ARCS

A `CareerArc` groups related events into a meaningful career period.

Examples:

```text
ACADEMY_RISE
BREAKTHROUGH
ESTABLISHMENT
PEAK
ADVERSITY
RECOVERY
DECLINE
LATE_CAREER
RETIREMENT
```

An arc contains structured information:

```text
CareerArc
├── arc_id
├── type
├── start_sequence
├── end_sequence
├── event_ids
├── milestones
├── turning_points
├── significance
└── status
```

---

# 23. ARC TRANSITIONS

Career arcs must evolve deterministically.

For example:

```text
ACADEMY_RISE
      ↓
BREAKTHROUGH
      ↓
ESTABLISHMENT
      ↓
PEAK
      ↓
DECLINE
      ↓
RETIREMENT
```

However, the engine must permit non-linear careers.

Examples:

```text
BREAKTHROUGH
    ↓
ADVERSITY
    ↓
RECOVERY
    ↓
PEAK
```

Do not force every player into the same career structure.

---

# 24. NARRATIVE SEEDS

A `NarrativeSeed` is the final abstraction produced by Phase 9 for future narrative systems.

It is NOT prose.

Example:

```text
NarrativeSeed
├── seed_id
├── seed_type
├── priority
├── event_ids
├── milestone_ids
├── relationship_ids
├── arc_id
├── emotional_direction
├── factual_context
└── narrative_weight
```

---

# 25. NARRATIVE SEED TYPES

Initial types may include:

```text
ORIGIN
BREAKTHROUGH
RIVALRY
TRIUMPH
FAILURE
COMEBACK
CONTROVERSY
TRANSFER
LOYALTY
BETRAYAL
REDEMPTION
PEAK
DECLINE
LEGACY
RETIREMENT
```

These represent narrative opportunities, not generated stories.

---

# 26. NARRATIVE SEED PRIORITY

Seeds must be ranked deterministically.

Possible priority levels:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

Priority should derive from:

```text
event significance
career impact
rarity
milestone importance
arc importance
relationship importance
```

No randomness.

---

# 27. FACTUAL INTEGRITY

This is a critical invariant.

Phase 9 must never create factual information that did not originate from simulation data.

For example, it must NOT invent:

```text
quotes
feelings
private conversations
motives
unrecorded relationships
unrecorded injuries
unrecorded conflicts
```

It may classify structured events, but cannot fabricate facts.

Future narrative systems may dramatize presentation while remaining grounded in the structured history.

---

# 28. STATE VS HISTORY

Phase 9 must distinguish between:

```text
CURRENT STATE
```

and:

```text
HISTORICAL RECORD
```

Example:

A player currently belongs to Club B.

The career history must still preserve:

```text
previously played for Club A
transferred to Club B
```

History must never be reconstructed solely from current state when the original event record is available.

---

# 29. IMMUTABILITY

Phase 9 domain objects must follow the same immutability principles established in Phase 8.

Processing a new event must return a new career record.

Conceptually:

```text
old_record
    +
new_event
    ↓
new_record
```

The original record remains unchanged.

---

# 30. ATOMICITY

If processing an event requires multiple derived updates:

```text
event
 ↓
career event
 ↓
milestone
 ↓
relationship
 ↓
turning point
 ↓
arc
 ↓
narrative seed
```

and processing fails, the original career record must remain unchanged.

No partial career history should be returned as successful.

---

# 31. DETERMINISM

Phase 9 must be completely deterministic.

Given:

```text
same career history
+
same event
+
same simulation state
```

the resulting:

```text
CareerRecord
CareerEvent
Milestones
Relationships
TurningPoints
CareerArcs
NarrativeSeeds
```

must be identical.

No uncontrolled randomness is permitted.

---

# 32. CROSS-PROCESS DETERMINISM

Where practical, verify Phase 9 in independent Python processes.

Serialized results must be identical.

Do not rely on:

```text
hash()
random.random()
UUID randomness
timestamps
process IDs
memory addresses
unordered iteration
```

for deterministic outputs.

---

# 33. SERIALIZATION

Extend the existing event-domain serialization conventions.

Phase 9 objects must serialize deterministically.

At minimum support:

```text
CareerRecord
CareerEvent
CareerMilestone
CareerRelationship
CareerTurningPoint
CareerArc
NarrativeSeed
```

Serialization must:

* preserve enum values;
* preserve nested structures;
* preserve ordering;
* avoid mutation;
* produce deterministic bytes.

---

# 34. PUBLIC API

Expose intended Phase 9 domain primitives through:

```text
backend/app/event/
```

or the appropriate domain module established by the repository architecture.

Do not expose implementation-only helpers.

Maintain clean public exports.

---

# 35. PROCESSING API

Introduce a pure processing API.

Conceptually:

```python
record_career_event(
    career_record,
    event_result,
    simulation_state,
) -> CareerRecord
```

and/or:

```python
process_career_event(...)
```

The exact naming may follow repository conventions.

The processing function must:

1. validate inputs;
2. create the historical event;
3. detect milestones;
4. update relationships;
5. detect turning points;
6. update career arcs;
7. generate narrative seeds;
8. return the new immutable record.

---

# 36. BATCH PROCESSING

Support deterministic processing of multiple historical events.

Conceptually:

```python
process_career_events(
    career_record,
    events,
    simulation_state,
) -> CareerRecord
```

Events must be processed in deterministic chronological order.

Processing the same event list twice must produce identical records.

---

# 37. IDEMPOTENCY

Processing the same source event twice must not duplicate it.

Example:

```text
record_career_event(record, event)
record_career_event(record_after_event, event)
```

must not create duplicate history entries.

This is critical for safe simulation replay.

---

# 38. REPLAYABILITY

Phase 9 should support rebuilding a career history from an ordered sequence of simulation events.

Conceptually:

```text
Initial CareerRecord
        ↓
Event 1
        ↓
Event 2
        ↓
Event 3
        ↓
...
        ↓
Final CareerRecord
```

Replaying the same event sequence must produce the same final result.

---

# 39. ERROR HANDLING

Introduce explicit typed errors where appropriate.

Potential categories:

```text
INVALID_CAREER_RECORD
INVALID_EVENT
INVALID_PLAYER
INVALID_SEQUENCE
DUPLICATE_EVENT
INVALID_CONTEXT
INVALID_RELATIONSHIP
INVALID_MILESTONE
PROCESSING_ERROR
```

Do not silently ignore malformed events.

---

# 40. MISSING DATA

Phase 9 must distinguish between:

```text
missing optional information
```

and:

```text
invalid required information
```

Optional missing information should not necessarily fail processing.

Required missing information must fail explicitly.

Never fabricate replacement values.

---

# 41. PERFORMANCE

Phase 9 must remain lightweight.

Avoid expensive global recomputation whenever possible.

Prefer incremental updates:

```text
new event
 ↓
update affected history
```

rather than rebuilding the entire career for every event.

However, replay functionality may legitimately rebuild the history from scratch.

---

# 42. CONFIGURATION

Thresholds and weights should not be scattered through code.

Where appropriate, use the project's existing rules/configuration architecture.

Potential configuration:

```text
data/rules/
```

Possible configurable values:

```text
significance weights
milestone thresholds
relationship thresholds
turning-point thresholds
arc transition thresholds
narrative seed priorities
```

Do not introduce configuration files unless the existing architecture supports them.

---

# 43. DATABASE / PERSISTENCE BOUNDARY

Phase 9 domain logic must remain independent from persistence.

Do NOT directly depend on:

```text
SQLAlchemy
SQLite
Alembic
database sessions
```

The career history engine should operate in memory.

Persistence can be added through a separate adapter layer later.

---

# 44. API / FRONTEND BOUNDARY

Phase 9 must remain independent of:

```text
FastAPI
Angular
HTTP requests
frontend state
```

It should be executable independently as a domain engine.

---

# 45. SECURITY

Phase 9 must contain no arbitrary code execution.

Do NOT use:

```text
eval
exec
compile
dynamic code execution
```

All classification and interpretation must remain deterministic and declarative.

---

# 46. TESTING STRATEGY

Create dedicated Phase 9 tests.

At minimum:

## Domain tests

Test:

```text
CareerRecord
CareerEvent
CareerMilestone
CareerRelationship
CareerTurningPoint
CareerArc
NarrativeSeed
```

including validation and immutability.

---

# 47. EVENT RECORDING TESTS

Test:

* first event;
* multiple events;
* chronological ordering;
* duplicate event;
* malformed event;
* missing optional data;
* missing required data.

---

# 48. MILESTONE TESTS

Test:

* first milestone;
* repeated unique milestone;
* threshold milestone;
* multiple milestones;
* deterministic milestone detection.

---

# 49. RELATIONSHIP TESTS

Test:

* relationship creation;
* relationship update;
* positive change;
* negative change;
* neutral interaction;
* deterministic strength;
* repeated event handling.

---

# 50. TURNING POINT TESTS

Test:

* significant state change;
* major event;
* milestone-triggered turning point;
* repeated processing;
* deterministic detection.

---

# 51. CAREER ARC TESTS

Test:

* initial arc;
* arc transition;
* non-linear progression;
* repeated events;
* deterministic arc state.

---

# 52. NARRATIVE SEED TESTS

Test:

* seed creation;
* seed priority;
* seed deduplication;
* association with events;
* association with milestones;
* association with arcs;
* deterministic ranking.

---

# 53. IMMUTABILITY TESTS

Verify:

```text
input CareerRecord unchanged
input EventResult unchanged
input State unchanged
```

after processing.

Nested structures must also remain untouched.

---

# 54. ATOMICITY TESTS

Create a scenario where processing fails halfway through.

Verify:

```text
original CareerRecord
      ↓
processing failure
      ↓
original CareerRecord unchanged
```

No partial history may escape as a successful result.

---

# 55. IDEMPOTENCY TESTS

Process the same event multiple times.

Verify:

```text
one source event
=
one historical event
```

and that milestones, relationships, arcs and narrative seeds are not duplicated incorrectly.

---

# 56. REPLAY TESTS

Given:

```text
Event 1
Event 2
Event 3
...
Event N
```

verify that:

```text
process sequentially
```

produces the same result as replaying the same sequence again from an empty record.

---

# 57. DETERMINISM TESTS

Run identical scenarios:

```text
1x
10x
100x
```

and verify identical serialized results.

Where practical:

```text
cross-process
```

determinism must also be verified.

---

# 58. SERIALIZATION TESTS

Verify deterministic JSON serialization.

Test:

```text
serialize
deserialize
serialize
```

where supported.

The result must remain semantically equivalent.

---

# 59. END-TO-END PHASE 8 → PHASE 9 TEST

At least one integration test must connect the real Phase 8 pipeline with Phase 9.

Expected:

```text
Phase 8
    ↓
Event Resolution
    ↓
Decision
    ↓
Effect Application
    ↓
State Transition
    ↓
Phase 9
    ↓
Career History
    ↓
Milestone / Turning Point / Narrative Seed
```

Do not construct fake intermediate objects if real Phase 8 domain objects can be used.

---

# 60. PHASE 8 REGRESSION

All existing Phase 8 tests must continue passing.

At minimum verify:

```text
8A
8B
8C
8D
8E
8F
```

No Phase 8 behavior may regress.

---

# 61. FULL TEST SUITE

Run:

```text
pytest
```

and report exact results.

---

# 62. RESPONSIBILITY MODEL

The final responsibility separation must remain:

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
Event Resolution
    ↓
8F
Decision Selection
    ↓
8E
Effect Application
    ↓
Simulation State
    ↓
9
Career History & Interpretation
    ↓
Narrative Seeds
    ↓
Future Narrative Engine
```

Important:

```text
8E changes STATE.
9 records and interprets HISTORY.
```

Phase 9 must never become another state mutation engine.

---

# 63. NON-GOALS

Do NOT implement:

```text
AI-generated narratives
LLM integration
natural-language generation
dialogue generation
voice generation
TikTok scripts
video generation
social media integration
career commentary text
```

Do NOT implement advanced social simulation unless explicitly supported by the existing domain.

Do NOT implement database persistence.

Do NOT implement frontend interfaces.

---

# 64. CODE QUALITY

Prefer:

* immutable domain models;
* pure functions;
* deterministic algorithms;
* explicit validation;
* small composable processors;
* existing project conventions;
* reusable structured data.

Avoid:

* global mutable state;
* hidden caches;
* uncontrolled randomness;
* excessive inheritance;
* dynamic execution;
* duplicated Phase 8 logic;
* unnecessary framework dependencies.

---

# 65. IMPLEMENTATION ORDER

Recommended implementation order:

```text
1. Domain primitives
2. CareerRecord
3. CareerEvent recording
4. Timeline ordering
5. Milestone detection
6. Relationship tracking
7. Turning-point detection
8. Career arcs
9. Narrative seeds
10. Incremental processing
11. Batch processing
12. Replay
13. Serialization
14. Integration tests
15. Full regression
```

Do not implement future narrative generation.

---

# 66. FINAL INVARIANTS

The implementation must guarantee:

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
IDEMPOTENT
```

```text
REPLAYABLE
```

```text
FACTUALLY GROUNDED
```

```text
PHASE-BOUNDARY SAFE
```

---

# 67. DEFINITION OF DONE

Phase 9 is complete only when:

* all domain models exist;
* career history can be built incrementally;
* historical events are deterministic;
* duplicate events are prevented;
* milestones are detected;
* relationships are tracked where supported;
* turning points are detected;
* career arcs are maintained;
* narrative seeds are generated;
* serialization works;
* immutability is verified;
* atomicity is verified;
* idempotency is verified;
* replayability is verified;
* cross-process determinism is verified where practical;
* at least one real Phase 8 → Phase 9 integration test exists;
* all Phase 8 tests pass;
* the full test suite passes;
* no database/frontend/API coupling exists;
* no narrative prose generation exists.

---

# 68. FINAL REPORT REQUIREMENTS

When implementation is complete, return:

## Implementation Status

```text
COMPLETE
```

or:

```text
BLOCKED
```

## Implemented

List every Phase 9 domain primitive and processing function.

## Integration

Explain exactly how Phase 8 feeds Phase 9.

## Phase Boundaries

Confirm that:

```text
8E = state application
9 = career history / interpretation
```

remain separate.

## Tests

Report:

```text
Phase 9:
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
replay
end-to-end
```

## Immutability

Report:

```text
PASS / FAIL
```

## Atomicity

Report:

```text
PASS / FAIL
```

## Idempotency

Report:

```text
PASS / FAIL
```

## Serialization

Report:

```text
PASS / FAIL
```

## Files Changed

List every modified or created file.

Classify each:

```text
EXPECTED
NECESSARY
UNRELATED
```

## Findings

List any remaining concerns.

## Final Recommendation

Choose:

```text
READY FOR PHASE 9 AUDIT
```

or:

```text
PHASE 9 REQUIRES FIXES
```

---

# 69. FINAL ARCHITECTURAL PRINCIPLE

Football Life must preserve the following separation:

```text
┌─────────────────────────────────────────────┐
│                SIMULATION                   │
│                                             │
│  8A → 8B → 8C → 8D → 8F → 8E              │
│                                             │
│          "WHAT HAPPENED?"                   │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│             CAREER HISTORY                  │
│                                             │
│  Events → Milestones → Relationships        │
│          → Turning Points → Arcs             │
│          → Narrative Seeds                  │
│                                             │
│          "WHAT DID IT MEAN?"                │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│              FUTURE PHASES                  │
│                                             │
│       Narrative → Script → Video            │
│                                             │
│          "HOW DO WE TELL IT?"               │
└─────────────────────────────────────────────┘
```

This separation is a core architectural invariant of Football Life and must not be violated.
