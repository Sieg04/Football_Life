# FOOTBALL LIFE — PHASE 12 DESIGN SPEC

## Career Presentation & Visual Experience

**Version:** 1.0
**Project:** Football Life
**Phase:** 12
**Status:** Design Specification
**Primary Responsibility:** Transform the completed career, narrative, and script domain data into a deterministic, immutable, presentation-ready career experience model.

---

# 1. PURPOSE

Phase 12 introduces the **Career Presentation & Visual Experience Layer**.

Its purpose is to transform the outputs of Phases 8–11 into a structured presentation model suitable for rendering by the Football Life user interface.

Phase 12 does **not** simulate football, create career facts, generate new narrative information, generate media, or render videos.

Its responsibility is strictly:

```text
Existing Football Life Data
        ↓
Presentation Model
        ↓
Frontend/UI
```

The presentation layer must make the generated career:

* visually understandable;
* chronologically coherent;
* statistically readable;
* narratively accessible;
* emotionally engaging;
* suitable for screen recording;
* deterministic;
* immutable;
* fully traceable to source data.

---

# 2. ARCHITECTURAL POSITION

The complete pipeline is:

```text
PHASE 8
Event Simulation & Resolution
        ↓
PHASE 9
Career History & Narrative Foundation
        ↓
PHASE 10
Narrative Engine & Story Assembly
        ↓
PHASE 11
Story Script & Narrative Presentation
        ↓
PHASE 12
Career Presentation & Visual Experience
        ↓
PHASE 13
Simulation Interface & Career Interaction
        ↓
PHASE 14
UX, Visual Identity & Polish
        ↓
PHASE 15
Content / Export Utilities
```

Phase responsibilities:

```text
8  = WHAT HAPPENS
9  = WHAT HAPPENED TO THE PLAYER
10 = WHAT IS THE STORY
11 = HOW IS THE STORY WRITTEN
12 = HOW IS THE INFORMATION PRESENTED
13 = HOW DOES THE USER INTERACT WITH IT
14 = HOW IS THE EXPERIENCE POLISHED
15 = OPTIONAL CONTENT/EXPORT UTILITIES
```

---

# 3. CORE PRINCIPLE

The most important Phase 12 invariant is:

```text
PHASE 12 PRESENTS INFORMATION.
PHASE 12 DOES NOT CREATE INFORMATION.
```

Every displayed fact must originate from an existing domain object.

Phase 12 must never invent:

* statistics;
* achievements;
* transfers;
* clubs;
* competitions;
* injuries;
* relationships;
* milestones;
* turning points;
* narrative events;
* dates;
* seasons;
* trophies;
* career outcomes.

---

# 4. SCOPE

Phase 12 is responsible for creating a presentation-ready model containing:

* player identity;
* career overview;
* career statistics;
* club history;
* season summaries;
* career timeline;
* important events;
* milestones;
* turning points;
* relationships;
* career arc;
* narrative story;
* story script;
* presentation sections;
* visual emphasis metadata;
* source references.

Phase 12 may determine **how existing information should be visually prioritized**.

Phase 12 may NOT determine new football facts.

---

# 5. NON-GOALS

Phase 12 must NOT implement:

* Angular components;
* HTML templates;
* CSS;
* frontend routing;
* browser state management;
* FastAPI endpoints;
* database persistence;
* SQLAlchemy models;
* simulation rules;
* event generation;
* probability calculation;
* effect application;
* career history recording;
* narrative generation;
* script generation;
* image generation;
* video generation;
* voice generation;
* TTS;
* video rendering;
* external AI APIs;
* external network calls.

The domain layer must remain independent of UI infrastructure.

---

# 6. INPUTS

Phase 12 consumes existing domain outputs.

Primary inputs:

```text
CareerRecord
NarrativeStory
StoryScript
```

Optional supporting data may include existing immutable player/world domain objects when explicitly required by the specification.

Phase 12 must not modify these inputs.

---

# 7. OUTPUT

The primary Phase 12 output is:

```text
CareerPresentation
```

which represents the complete presentation-ready view of a player's career.

Conceptually:

```text
CareerPresentation
│
├── PlayerPresentation
├── CareerOverview
├── CareerStatistics
├── ClubTimeline
├── SeasonSummaries
├── CareerTimeline
├── CareerHighlights
├── CareerArcPresentation
├── RelationshipPresentation
├── NarrativePresentation
├── ScriptPresentation
└── PresentationMetadata
```

---

# 8. DOMAIN PRIMITIVES

All Phase 12 domain objects must be immutable frozen dataclasses.

Required objects:

```text
CareerPresentation
PlayerPresentation
CareerOverview
CareerStatistics
ClubPresentation
SeasonPresentation
TimelineEntry
CareerHighlight
CareerArcPresentation
RelationshipPresentation
NarrativePresentation
ScriptPresentation
PresentationMetadata
PresentationSourceReference
PresentationBuildResult
```

Supporting enums should include, where required:

```text
PresentationSectionType
TimelineEntryType
HighlightType
StatCategory
CareerStatus
VisualPriority
PresentationDensity
PresentationErrorCode
```

The exact enum values must follow this specification and existing domain semantics.

---

# 9. IMMUTABILITY

Every Phase 12 domain object must be immutable.

Required:

```python
@dataclass(frozen=True)
```

Nested collections must also be immutable.

Use:

```text
tuple
MappingProxyType
immutable nested domain objects
```

Do not expose mutable lists or dictionaries inside presentation objects.

The following must be impossible:

```python
presentation.timeline.append(...)
presentation.statistics.goals = ...
presentation.metadata["x"] = ...
```

---

# 10. PLAYER PRESENTATION

`PlayerPresentation` represents the identity information displayed to the user.

It may contain:

```text
player_id
name
first_name
last_name
age
nationality
position
overall_rating
potential
current_club
career_status
```

Only fields actually available from source data may be populated.

Missing information must remain missing.

Do not invent defaults such as:

```text
unknown nationality → Spain
unknown position → ST
missing club → Free Agent
```

unless explicitly supported by the source model.

---

# 11. CAREER OVERVIEW

`CareerOverview` provides a compact summary.

Possible fields:

```text
career_start
career_end
years_active
clubs_count
matches
goals
assists
trophies
milestones
turning_points
peak_rating
peak_club
career_arc
```

All values must be derived from source data.

No statistics may be inferred from unrelated fields.

For example:

```text
number of events ≠ number of matches
number of milestones ≠ number of trophies
```

unless the source explicitly defines that relationship.

---

# 12. CAREER STATISTICS

`CareerStatistics` groups existing career statistics for presentation.

Possible categories:

```text
appearances
goals
assists
clean_sheets
minutes
average_rating
trophies
awards
```

Only statistics actually available in the source data should be presented.

Missing statistics should be represented explicitly rather than fabricated.

---

# 13. CLUB PRESENTATION

Each `ClubPresentation` represents a real club association already present in the career data.

Possible fields:

```text
club_id
club_name
country
start_date
end_date
season_count
appearances
goals
assists
trophies
role
importance
```

Phase 12 must not infer a transfer unless a source career event explicitly records one.

---

# 14. SEASON PRESENTATION

`SeasonPresentation` provides a readable representation of each season.

Possible fields:

```text
season_id
season_label
club_id
club_name
appearances
goals
assists
average_rating
trophies
important_events
milestones
turning_points
```

Ordering must be deterministic.

Preferred ordering:

```text
chronological ascending
```

unless the UI explicitly requests descending order.

---

# 15. CAREER TIMELINE

`TimelineEntry` provides a chronological representation of the player's career.

Each entry should contain:

```text
timeline_id
date_or_season
entry_type
title
summary
importance
source_reference
```

Possible entry types:

```text
EVENT
MILESTONE
TURNING_POINT
TRANSFER
TROPHY
BREAKTHROUGH
SETBACK
RECOVERY
CAREER_ARC_CHANGE
```

Only types supported by source data may be generated.

---

# 16. TIMELINE ORDERING

Timeline ordering must be deterministic.

Primary ordering:

```text
chronological date
```

Secondary ordering:

```text
source event sequence
```

Tertiary ordering:

```text
stable deterministic ID
```

Never depend on:

```text
set iteration order
dict iteration from unstable sources
memory addresses
hash()
```

---

# 17. CAREER HIGHLIGHTS

`CareerHighlight` represents information that deserves stronger visual emphasis.

Highlights may be derived from:

```text
high-significance events
milestones
turning points
career arc transitions
important achievements
narrative climax
```

A highlight is a **presentation classification**, not a new fact.

Example:

```text
Existing fact:
"Player won first major trophy."

Presentation:
HighlightType.FIRST_MAJOR_TROPHY
```

The presentation layer must not create:

```text
"Greatest moment of his career"
```

unless that interpretation is already supported by Phase 9/10 data.

---

# 18. VISUAL PRIORITY

Presentation elements may have a priority:

```text
CRITICAL
HIGH
MEDIUM
LOW
```

Priority determines visual emphasis only.

It must never alter factual content.

Priority may be derived deterministically from:

```text
EventSignificance
MilestoneType
TurningPointType
CareerArc
NarrativeSeed priority
NarrativeBeat importance
```

---

# 19. CAREER ARC PRESENTATION

`CareerArcPresentation` exposes the career arc generated by Phase 9.

It may contain:

```text
arc_id
arc_type
status
start_reference
end_reference
phases
current_phase
history
```

The presentation layer must not modify the arc.

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
ADVERSITY
    ↓
RECOVERY
```

must remain semantically identical to the Phase 9 source.

---

# 20. RELATIONSHIP PRESENTATION

`RelationshipPresentation` exposes important career relationships.

Possible fields:

```text
relationship_id
target_entity_id
target_entity_name
relationship_type
status
strength
start_reference
end_reference
```

The relationship must originate from `CareerRecord`.

Phase 12 must not invent:

```text
friendship
rivalry
mentorship
conflict
```

---

# 21. NARRATIVE PRESENTATION

`NarrativePresentation` wraps the Phase 10 `NarrativeStory`.

Possible fields:

```text
story_id
premise
theme
acts
beats
threads
conflicts
opening
climax
resolution
```

Phase 12 may reorganize these for display.

It must not alter the semantic narrative.

---

# 22. SCRIPT PRESENTATION

`ScriptPresentation` wraps the Phase 11 `StoryScript`.

Possible fields:

```text
script_id
hook
introduction
sections
segments
transitions
climax
resolution
closing
word_count
estimated_duration
```

The original script must remain unchanged.

Phase 12 is only responsible for deciding how the script is displayed.

---

# 23. PRESENTATION SECTIONS

The complete presentation should support sections such as:

```text
PLAYER
OVERVIEW
CAREER
STATISTICS
TIMELINE
HIGHLIGHTS
RELATIONSHIPS
CAREER ARC
STORY
SCRIPT
```

Not every presentation must contain every section.

Sections may be omitted when the source contains no meaningful data.

The system must avoid empty visual sections.

---

# 24. PRESENTATION DENSITY

Support:

```text
COMPACT
STANDARD
DETAILED
COMPLETE
```

Density affects:

* number of timeline entries shown;
* number of highlights;
* amount of secondary statistics;
* narrative detail;
* visual emphasis.

Density must NOT affect:

* factual correctness;
* source data;
* narrative semantics;
* deterministic ordering.

For example:

```text
COMPACT:
Top career moments

STANDARD:
Top moments + key statistics

DETAILED:
Expanded timeline + statistics

COMPLETE:
All relevant presentation data
```

---

# 25. EMPTY DATA HANDLING

The engine must gracefully support:

```text
empty career
career with one event
career with no milestones
career with no turning points
career with no relationships
career with no narrative conflicts
career with minimal story
```

Do not create placeholder facts.

For example, do not generate:

```text
"No trophies yet"
```

unless the UI presentation layer explicitly chooses to render such a state.

The domain should represent the absence of trophies.

---

# 26. ACTIVE CAREER SAFETY

Active careers must remain active.

Phase 12 must not display unsupported final-career language.

For active players:

```text
current career
ongoing career
currently playing
```

may be displayed only when supported by source data.

Never convert an active player into:

```text
retired player
former player
career completed
final chapter
career ended
```

unless supported by Phase 9/10/11 data.

---

# 27. RETIRED CAREER PRESENTATION

Retirement may be presented only when supported by source data.

Valid sources include:

```text
retirement event
retirement milestone
career resolution indicating retirement
```

Phase 12 must rely on the established Phase 9/10 retirement semantics.

---

# 28. FACTUAL GROUNDING

Every presentation object containing factual information must have a source path.

Conceptually:

```text
Presentation
    ↓
NarrativeStory / StoryScript / CareerRecord
    ↓
source IDs
```

No presentation element may become an orphaned fact.

Examples:

```text
TimelineEntry
    → source_event_id

Highlight
    → source_milestone_id

CareerArcPresentation
    → source_arc_id

ScriptPresentation
    → source_script_id
```

---

# 29. TRACEABILITY

Required source references:

```text
PresentationSourceReference
```

may contain:

```text
career_record_id
event_ids
milestone_ids
turning_point_ids
relationship_ids
arc_ids
story_id
act_ids
beat_ids
thread_ids
conflict_ids
seed_ids
script_id
segment_ids
```

Only relevant IDs need to be populated.

All IDs must point to actual source objects.

---

# 30. TRACEABILITY VALIDATION

`validate_career_presentation()` must verify:

1. every source event exists;
2. every source milestone exists;
3. every source turning point exists;
4. every source relationship exists;
5. every source arc exists;
6. every story reference exists;
7. every script reference exists;
8. no orphaned reference is present.

Invalid references must produce a typed Phase 12 error.

---

# 31. PRESENTATION METADATA

`PresentationMetadata` may contain:

```text
presentation_id
player_id
created_from_story_id
created_from_script_id
density
section_order
version
```

Do not use real timestamps.

If a timestamp is required by a future infrastructure layer, it must remain outside the deterministic domain model.

---

# 32. DETERMINISTIC IDENTIFIERS

Phase 12 identifiers must be deterministic.

Use:

```text
SHA-256
```

or another cryptographic deterministic derivation already established by previous phases.

IDs should be derived from stable inputs such as:

```text
player_id
career_record_id
story_id
script_id
source_id
presentation type
```

Never use:

```text
uuid.uuid4()
random
hash()
process ID
memory address
current timestamp
```

---

# 33. PRESENTATION ENGINE

Create:

```text
backend/app/event/presentation_engine.py
```

Required functions:

```text
build_player_presentation
build_career_overview
build_career_statistics
build_club_presentations
build_season_presentations
build_career_timeline
build_career_highlights
build_career_arc_presentation
build_relationship_presentations
build_narrative_presentation
build_script_presentation
build_presentation_metadata
validate_career_presentation
build_career_presentation
```

All functions must be:

* deterministic;
* pure;
* side-effect free;
* immutable;
* independently testable.

---

# 34. ORCHESTRATION

`build_career_presentation()` must orchestrate:

```text
CareerRecord
      +
NarrativeStory
      +
StoryScript
      ↓
Player Presentation
      ↓
Career Overview
      ↓
Statistics
      ↓
Clubs
      ↓
Seasons
      ↓
Timeline
      ↓
Highlights
      ↓
Career Arc
      ↓
Relationships
      ↓
Narrative
      ↓
Script
      ↓
Metadata
      ↓
Validation
      ↓
CareerPresentation
```

If validation fails, the operation must fail atomically.

---

# 35. ATOMICITY

Presentation construction must be atomic.

If any required stage fails:

```text
no partial presentation
```

must be returned as a successful result.

Use a typed error/result model.

Inputs must remain untouched.

---

# 36. INPUT IMMUTABILITY

Before building the presentation, capture the logical state of:

```text
CareerRecord
NarrativeStory
StoryScript
```

After processing, verify they are unchanged.

Phase 12 must never mutate:

```text
events
milestones
turning points
relationships
career arcs
narrative acts
narrative beats
script segments
```

---

# 37. SERIALIZATION

Extend:

```text
backend/app/event/domain.py
```

so all Phase 12 objects serialize through:

```text
to_json_bytes()
```

Requirements:

```text
UTF-8
stable ordering
sort_keys=True
byte deterministic
```

Repeated serialization must produce identical bytes.

---

# 38. CONFIGURATION

Create:

```text
backend/data/rules/presentation.json
```

Centralize presentation rules such as:

```text
default density
maximum timeline items
maximum highlights
section priorities
visual priority weights
stat display rules
timeline display limits
```

Configuration must affect presentation prioritization only.

It must never create facts.

---

# 39. CONFIGURATION SAFETY

Invalid configuration must produce a typed error.

Do not silently fall back to arbitrary values.

Configuration parsing must be deterministic.

---

# 40. SECURITY

Phase 12 must contain no:

```text
eval()
exec()
compile()
```

No dynamic code execution.

No external network calls.

No:

```text
requests
httpx
urllib
openai
```

No database dependency.

No:

```text
SQLAlchemy
SQLite sessions
Alembic
FastAPI
Angular
```

inside the domain/presentation engine.

---

# 41. PHASE BOUNDARIES

Strict responsibilities:

```text
Phase 8
Simulation state changes

Phase 9
Career history recording

Phase 10
Narrative structure

Phase 11
Narrative script

Phase 12
Presentation model
```

Phase 12 must NOT:

```text
simulate
record
narrate
rewrite
mutate
persist
render
```

It only presents.

---

# 42. FRONTEND SEPARATION

Phase 12 must remain independent of Angular.

The output should be consumable by a future UI.

Conceptually:

```text
Angular
   ↓
Presentation API / Adapter
   ↓
CareerPresentation
```

Phase 12 itself must not import Angular or frontend code.

---

# 43. VISUAL SEMANTICS

Phase 12 may provide metadata intended to guide UI rendering.

Examples:

```text
VisualPriority.HIGH
TimelineEntryType.TRANSFER
HighlightType.BREAKTHROUGH
PresentationSectionType.CAREER
```

These values describe presentation semantics.

They must not dictate implementation-specific CSS or components.

Do NOT introduce:

```text
<div>
class="hero-card"
CSS strings
HTML
pixel coordinates
browser APIs
```

---

# 44. SCREEN-RECORDING PRINCIPLE

The presentation model should support an attractive visual career experience suitable for screen recording.

The system should prioritize:

```text
clear hierarchy
important career moments
readable statistics
chronological progression
narrative accessibility
visual emphasis
```

However, Phase 12 does not implement the actual recording system.

---

# 45. NARRATIVE / DATA CONSISTENCY

The following must remain consistent:

```text
CareerRecord
      ↕
NarrativeStory
      ↕
StoryScript
      ↕
CareerPresentation
```

Phase 12 must not present information contradicting the narrative layers.

Examples of invalid behavior:

```text
CareerRecord says active
Presentation says retired

CareerRecord has no trophy
Presentation shows trophy

NarrativeStory climax = event A
Presentation labels unrelated event B as climax
```

Such inconsistencies must fail validation.

---

# 46. CLIMAX PRESERVATION

The Phase 10 climax must remain the presentation climax.

If the story contains:

```text
climax_id
```

Phase 12 must preserve that identity.

The UI may emphasize it visually but must not replace it.

---

# 47. SCRIPT PRESERVATION

Phase 11 script semantics must remain unchanged.

Phase 12 may group:

```text
hook
introduction
sections
climax
resolution
closing
```

for display.

It may not rewrite the script.

---

# 48. PRESENTATION ORDER

Default section ordering:

```text
PLAYER
OVERVIEW
CAREER
STATISTICS
TIMELINE
HIGHLIGHTS
CAREER ARC
RELATIONSHIPS
STORY
SCRIPT
```

Ordering must be configurable through deterministic rules.

---

# 49. ERROR MODEL

Create:

```text
PresentationErrorCode
PresentationProcessingException
```

Potential error codes:

```text
INVALID_INPUT
MISSING_SOURCE
INVALID_REFERENCE
INVALID_CONFIGURATION
INCONSISTENT_DATA
IMMUTABILITY_VIOLATION
INVALID_DENSITY
INVALID_PRESENTATION
```

Errors must be explicit and typed.

Do not silently swallow errors.

---

# 50. PUBLIC EXPORTS

Update:

```text
backend/app/event/__init__.py
```

to expose all public Phase 12:

* domain objects;
* enums;
* errors;
* engine functions.

Do not remove existing Phase 8–11 exports.

---

# 51. TESTING REQUIREMENTS

Create:

```text
backend/tests/test_event_phase12.py
backend/tests/test_event_12_audit.py
```

Tests must cover:

### Domain

```text
domain construction
validation
immutability
nested immutability
```

### Presentation

```text
player presentation
career overview
statistics
clubs
seasons
timeline
highlights
career arc
relationships
narrative
script
metadata
```

### Edge cases

```text
empty career
one-event career
missing milestones
missing relationships
missing turning points
active career
retired career
minimal narrative
minimal script
```

### Safety

```text
factual grounding
traceability
climax preservation
script preservation
career/narrative consistency
```

### Determinism

```text
100x repeated execution
cross-process execution
byte-identical serialization
```

### Atomicity

```text
invalid source
invalid reference
invalid configuration
pipeline failure
```

### Integration

```text
Phase 8 → 9 → 10 → 11 → 12
```

---

# 52. DETERMINISM TEST

Run the complete presentation pipeline at least:

```text
100 times
```

with identical inputs.

Compare:

```text
CareerPresentation
```

and:

```text
to_json_bytes(CareerPresentation)
```

Every output must be identical.

---

# 53. CROSS-PROCESS TEST

Execute presentation generation in multiple independent Python processes.

Compare serialized bytes.

Expected:

```text
byte-for-byte identical
```

---

# 54. REGRESSION TESTING

Phase 12 must not break:

```text
Phase 8
Phase 9
Phase 10
Phase 11
```

All previous tests must continue to pass.

---

# 55. END-TO-END TEST

At least one test must execute:

```text
Phase 8
   ↓
Phase 9
   ↓
Phase 10
   ↓
Phase 11
   ↓
Phase 12
```

using real domain objects.

The resulting:

```text
CareerPresentation
```

must contain coherent:

```text
career
timeline
narrative
script
```

information.

---

# 56. SERIALIZATION AUDIT

Verify serialization for:

```text
CareerPresentation
PlayerPresentation
CareerOverview
CareerStatistics
ClubPresentation
SeasonPresentation
TimelineEntry
CareerHighlight
CareerArcPresentation
RelationshipPresentation
NarrativePresentation
ScriptPresentation
PresentationMetadata
PresentationSourceReference
PresentationBuildResult
```

No object may produce non-deterministic JSON.

---

# 57. SECURITY AUDIT

Search the entire Phase 12 implementation for:

```text
random
random.random
hash(
uuid.uuid4
datetime.now
datetime.utcnow
time.time
eval(
exec(
compile(
```

Any use affecting output is a failure.

Search imports for:

```text
requests
httpx
urllib
openai
SQLAlchemy
FastAPI
Angular
```

No external dependency may be introduced.

---

# 58. GIT SCOPE

Inspect:

```bash
git status
git diff --stat
git diff
```

Every changed file must be classified:

```text
EXPECTED
NECESSARY
UNRELATED
```

No unrelated modifications are permitted.

---

# 59. ACCEPTANCE CRITERIA

Phase 12 is complete only if:

```text
[ ] All required domain objects implemented
[ ] All required enums implemented
[ ] All required errors implemented
[ ] All domain objects immutable
[ ] Nested collections immutable
[ ] Player presentation implemented
[ ] Career overview implemented
[ ] Statistics presentation implemented
[ ] Club presentation implemented
[ ] Season presentation implemented
[ ] Timeline implemented
[ ] Highlights implemented
[ ] Career arc presentation implemented
[ ] Relationships implemented
[ ] Narrative presentation implemented
[ ] Script presentation implemented
[ ] Metadata implemented
[ ] Factual grounding enforced
[ ] Traceability enforced
[ ] Active career safety enforced
[ ] Retirement consistency enforced
[ ] Climax preservation enforced
[ ] Script preservation enforced
[ ] Density support implemented
[ ] Empty data handled safely
[ ] Atomicity enforced
[ ] Deterministic IDs implemented
[ ] 100x determinism verified
[ ] Cross-process determinism verified
[ ] Serialization verified
[ ] Configuration implemented
[ ] Security constraints verified
[ ] Phase boundaries verified
[ ] Phase 8 regression passes
[ ] Phase 9 regression passes
[ ] Phase 10 regression passes
[ ] Phase 11 regression passes
[ ] End-to-end 8→9→10→11→12 passes
[ ] No unrelated files changed
```

---

# 60. DEFINITION OF DONE

Phase 12 is considered complete only when:

```text
CareerRecord
      ↓
NarrativeStory
      ↓
StoryScript
      ↓
CareerPresentation
```

produces a complete, deterministic, immutable and traceable presentation model.

The presentation model must contain enough structured information for a future frontend to render:

```text
Player Profile
Career Overview
Statistics
Club History
Season History
Career Timeline
Highlights
Career Arc
Relationships
Story
Script
```

without requiring the frontend to reconstruct or infer career facts.

---

# 61. IMPORTANT ARCHITECTURAL RULE

The frontend should be a renderer of presentation data, not a second narrative engine.

Therefore:

```text
BAD:

Frontend
    ↓
"figure out what happened"
    ↓
display something

GOOD:

Phase 12
    ↓
decides what existing information is presented
    ↓
Frontend
    ↓
renders it
```

This prevents business/narrative logic from leaking into the UI.

---

# 62. FINAL TARGET ARCHITECTURE

After Phase 12:

```text
                  FOOTBALL LIFE

                  SIMULATION
                      │
                      ▼
                 EVENT ENGINE
                      │
                      ▼
                 CAREER RECORD
                      │
             ┌────────┴────────┐
             ▼                 ▼
       NARRATIVE ENGINE     CAREER DATA
             │                 │
             ▼                 │
       NARRATIVE STORY         │
             │                 │
             ▼                 │
        STORY SCRIPT           │
             │                 │
             └────────┬────────┘
                      ▼
             PRESENTATION ENGINE
                      │
                      ▼
             CAREER PRESENTATION
                      │
                      ▼
                FUTURE FRONTEND
                      │
                      ▼
             VISUAL FOOTBALL LIFE
```

---

# 63. PHASE 12 PHILOSOPHY

The fundamental principle of Phase 12 is:

> **Make the career easy to understand, easy to explore, and visually compelling without changing what actually happened.**

Football Life should feel like a football career documentary interface.

The simulator creates the career.

The event engine creates what happens.

The career engine remembers it.

The narrative engine understands it.

The script engine tells it.

**Phase 12 presents it.**
