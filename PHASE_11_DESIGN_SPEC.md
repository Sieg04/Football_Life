# FOOTBALL LIFE

## PHASE 11 — STORY SCRIPT & NARRATIVE PRESENTATION ENGINE

**Version:** 1.0
**Project:** Football Life
**Phase:** 11
**Type:** Deterministic narrative presentation and script assembly engine
**Primary platform:** Desktop/local web application
**Development assistant:** Jules

---

# 1. PHASE OBJECTIVE

Phase 11 transforms the structured narrative produced by Phase 10 into a **complete presentation-ready story structure and narration script** suitable for downstream voice/video generation.

Phase 11 does **not** simulate football.

It does **not** determine what happened.

It does **not** create new career facts.

It does **not** decide the player's career.

Those responsibilities belong to previous phases.

Phase 11 takes:

```text
NarrativeStory
```

and transforms it into:

```text
StoryScript
```

containing deterministic narration segments, scene/presentation instructions, pacing information, transitions, hooks, and closing structure.

The output must be usable by future presentation systems without requiring the narrative engine to be modified.

---

# 2. ARCHITECTURE

The complete pipeline becomes:

```text
PHASE 8
Event Simulation
    ↓
Event Resolution
    ↓
Effect Application
    ↓
PHASE 9
Career History
    ↓
PHASE 10
Narrative Structure
    ↓
NarrativeStory
    ↓
PHASE 11
Story Script & Presentation
    ↓
StoryScript
    ↓
FUTURE PHASES
Voice Generation
Visual Generation
Video Assembly
Publishing
```

Phase responsibilities:

```text
8E = CHANGE STATE

9 = RECORD + INTERPRET CAREER

10 = STRUCTURE STORY

11 = PRESENT STRUCTURED STORY

Future = GENERATE VOICE / VISUALS / VIDEO
```

---

# 3. CORE PRINCIPLE

Phase 11 is a **presentation layer over factual narrative structure**.

It may transform:

```text
facts
↓
structured narrative information
↓
natural-language narration
```

but may never transform:

```text
absence of facts
↓
invented facts
```

Narration may improve:

* wording;
* rhythm;
* transitions;
* emphasis;
* dramatic presentation;
* sentence structure;
* chronology;
* pacing.

Narration may NOT invent:

* events;
* statistics;
* trophies;
* transfers;
* injuries;
* relationships;
* motivations;
* dialogue;
* quotes;
* thoughts;
* emotions;
* causal explanations;
* places;
* dates;
* records.

Unless explicitly present in the source `NarrativeStory` / `CareerRecord`.

---

# 4. NON-GOALS

Phase 11 must NOT implement:

* football simulation;
* event generation;
* probability calculation;
* effect application;
* career history recording;
* narrative premise detection;
* narrative act detection;
* narrative beat detection;
* narrative conflict detection;
* narrative climax detection;
* database persistence;
* SQLAlchemy;
* SQLite;
* Alembic;
* FastAPI;
* Angular;
* external APIs;
* OpenAI API;
* LLM calls;
* voice generation;
* text-to-speech;
* image generation;
* video generation;
* video editing;
* TikTok publishing.

Phase 11 must remain a deterministic local domain engine.

---

# 5. INPUT

The primary input is:

```text
NarrativeStory
```

Phase 11 may access the underlying `CareerRecord` only when explicitly required for factual rendering and traceability.

The preferred data flow is:

```text
NarrativeStory
    ↓
StoryScript
```

not:

```text
CareerRecord
    ↓
StoryScript
```

Phase 10 remains responsible for narrative selection and structure.

---

# 6. OUTPUT

The primary output is:

```text
StoryScript
```

The script should contain:

```text
StoryScript
├── metadata
├── title
├── hook
├── introduction
├── sections
├── transitions
├── climax
├── resolution
├── closing
├── estimated_duration
├── word_count
└── traceability metadata
```

The output must remain structured rather than being only one large text string.

---

# 7. DOMAIN PRIMITIVES

Implement the required Phase 11 domain models in:

```text
backend/app/event/script_domain.py
```

Required models:

```text
StoryScript
ScriptSection
ScriptSegment
ScriptTransition
ScriptHook
ScriptClosing
ScriptMetadata
ScriptSourceReference
ScriptBuildResult
```

All domain models must follow existing project conventions.

Use:

```python
@dataclass(frozen=True)
```

where appropriate.

Nested collections must be immutable.

---

# 8. ENUMS

Implement appropriate enums including:

```text
ScriptSectionType
ScriptSegmentType
TransitionType
HookType
ClosingType
NarrationTone
NarrationPacing
ScriptDensity
ScriptErrorCode
```

The exact enum values must follow the Phase 11 implementation requirements and configuration.

Recommended section types:

```text
HOOK
INTRODUCTION
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
CLOSING
```

A section must only exist when supported by the incoming `NarrativeStory`.

---

# 9. SCRIPT SEGMENTS

A `ScriptSegment` represents the smallest independently renderable narration unit.

It should contain information such as:

```text
id
sequence
segment_type
text
source references
estimated word count
estimated duration
pacing
importance
```

Every factual segment must remain traceable to its source narrative component.

Example:

```text
ScriptSegment
    ↓
NarrativeBeat
    ↓
CareerEvent / Milestone / TurningPoint
```

---

# 10. SCRIPT SOURCE REFERENCES

Implement explicit traceability.

A script segment may reference:

```text
source_story_ids
source_act_ids
source_beat_ids
source_thread_ids
source_conflict_ids
source_event_ids
source_milestone_ids
source_turning_point_ids
source_seed_ids
```

Not every field must be populated.

Only relevant source references should be included.

No script segment containing factual claims should be completely untraceable.

---

# 11. HOOK ENGINE

Implement deterministic hook generation.

Supported hook strategies may include:

```text
ORIGIN_HOOK
COLD_OPEN
MAJOR_ACHIEVEMENT
CAREER_CONTRAST
CRISIS
COMEBACK
RIVALRY
MYSTERY
LEGACY
```

The hook must be based on actual narrative material.

Example conceptual transformation:

```text
NarrativeBeat:
"Player wins first major trophy."

↓
Hook:

"Before anyone knew his name, he was already changing his career."
```

The wording may be dramatic, but the underlying fact must remain supported.

Do NOT invent:

```text
"He had one chance left."
"He was rejected by every club."
"Nobody believed in him."
```

unless those facts exist in the source data.

---

# 12. HOOK SELECTION

The hook engine must:

1. inspect available narrative material;
2. rank possible hook candidates;
3. select the strongest deterministic candidate;
4. generate a presentation-safe narration segment;
5. preserve source references.

If insufficient material exists:

```text
NO_HOOK
```

may be returned or a minimal chronological opening may be used according to configuration.

---

# 13. INTRODUCTION

The introduction should establish:

```text
who
what career
where the story begins
```

using only available facts.

It may include:

* player identity;
* position;
* nationality if available;
* starting club;
* age/year where available;
* career context.

It must not infer missing biographical information.

---

# 14. NARRATIVE SECTION ASSEMBLY

Transform each `NarrativeAct` into one or more script sections.

Example:

```text
NarrativeAct
    ↓
ScriptSection
    ↓
ScriptSegments
```

The script engine must preserve the ordering established by Phase 10.

Phase 11 must NOT reorder major narrative events unless explicitly required by an opening/hook strategy.

---

# 15. SEGMENT GENERATION

For every narrative beat:

1. identify the factual source;
2. determine its narrative function;
3. render a concise narration;
4. assign pacing;
5. estimate words;
6. estimate duration;
7. attach source references.

The engine must never silently drop critical beats unless density rules explicitly allow compression.

---

# 16. NARRATION STYLE

Phase 11 should support deterministic narration styles.

Recommended styles:

```text
DOCUMENTARY
CINEMATIC
DRAMATIC
MINIMAL
FAST_PACED
REFLECTIVE
```

Style affects:

* sentence length;
* transition frequency;
* emphasis;
* pacing;
* amount of connective language.

Style must NOT alter factual content.

---

# 17. NARRATION TONE

Recommended tones:

```text
NEUTRAL
DRAMATIC
INSPIRATIONAL
DARK
REFLECTIVE
TRIUMPHANT
TENSE
```

Tone controls presentation only.

Tone must never introduce unsupported psychological claims.

For example:

Allowed:

```text
"The season marked a turning point in his career."
```

if supported by Phase 10.

Not allowed:

```text
"He felt completely broken."
```

unless explicitly supported.

---

# 18. TRANSITIONS

Implement deterministic transitions between sections.

Examples of transition functions:

```text
TIME_ADVANCE
CAUSE
CONTRAST
ESCALATION
TURNING_POINT
RECOVERY
PEAK
RESOLUTION
```

Transitions must not introduce new factual claims.

They may establish structural relationships already present in Phase 10.

---

# 19. TRANSITION SAFETY

Do not convert chronological proximity into causality.

Bad:

```text
"He transferred clubs, and that caused his downfall."
```

unless causal information exists.

Safe:

```text
"His next chapter began at a new club."
```

The engine must distinguish:

```text
SEQUENCE
```

from:

```text
CAUSALITY
```

---

# 20. CLIMAX RENDERING

The Phase 10 climax must become the script's narrative peak.

The climax should receive:

* increased narrative emphasis;
* appropriate pacing;
* dedicated segment(s);
* source references.

The engine must not replace the Phase 10 climax with a different event.

---

# 21. RESOLUTION RENDERING

The script resolution must follow the Phase 10 resolution.

Examples:

```text
TRIUMPH
LEGACY
RETIREMENT
DECLINE
UNRESOLVED
ONGOING
COMEBACK
```

Active careers must not receive final retirement language.

For active careers:

```text
"The story is still being written."
```

may be used as presentation language.

But:

```text
"His career ended here."
```

must never be produced unless retirement is supported.

---

# 22. CLOSING ENGINE

Implement deterministic closing strategies:

```text
LEGACY
ONGOING
RETIREMENT
TRIUMPH
REFLECTION
OPEN_ENDED
```

The closing should summarize the established narrative without adding new facts.

---

# 23. WORD COUNT

Every `ScriptSegment` should expose deterministic word count.

The total script must expose:

```text
word_count
```

Word counting must use a deterministic rule.

Recommended:

```text
split on whitespace
```

No language model tokenization.

---

# 24. DURATION ESTIMATION

Phase 11 may estimate narration duration using:

```text
word_count
words_per_minute
```

Configuration should define default narration speed.

Example:

```text
150 words/minute
```

The result should expose:

```text
estimated_duration_seconds
```

This is an estimate only.

Phase 11 must NOT generate audio.

---

# 25. TARGET DURATION

Support:

```text
target_duration_seconds
```

The engine should attempt to produce a script close to the target using:

* segment selection;
* compression;
* expansion through supported connective language;
* density;
* pacing.

It must never invent facts simply to reach a duration.

If insufficient factual material exists:

```text
actual_duration < target_duration
```

is acceptable.

Factual correctness has priority over duration.

---

# 26. SCRIPT DENSITY

Support:

```text
COMPACT
STANDARD
DETAILED
COMPLETE
```

Density controls:

```text
number of beats included
transition frequency
description verbosity
section depth
```

Density must never create new facts.

---

# 27. PACING

Implement deterministic pacing:

```text
SLOW
MODERATE
FAST
VERY_FAST
```

Pacing may depend on:

* narrative importance;
* act type;
* beat type;
* climax;
* conflict;
* target duration.

Recommended:

```text
origin → moderate
rise → moderate/fast
conflict → fast
crisis → slow/moderate
climax → slow/moderate
resolution → slow
```

These are presentation rules only.

---

# 28. WORD BUDGET

The engine should calculate a deterministic word budget.

Example:

```text
target_duration_seconds
×
words_per_minute / 60
```

The word budget must be used to prioritize segments.

Priority order should favor:

```text
climax
turning points
major milestones
major conflicts
high-significance events
resolution
opening
```

Low-priority material may be compressed or omitted according to density.

---

# 29. MATERIAL COMPRESSION

When the target duration is too short:

Prefer:

```text
remove redundant beats
compress repeated information
reduce transitions
merge adjacent related segments
remove low-significance events
```

Never:

```text
invent facts
change event meaning
change chronology
remove the climax
remove essential resolution information
```

---

# 30. MATERIAL EXPANSION

When target duration allows more content:

Prefer:

```text
include additional supported beats
include additional milestones
include relevant relationship material
include additional turning points
include additional contextual transitions
```

Do NOT invent narrative details.

---

# 31. FACTUAL GROUNDING

Every factual statement generated by Phase 11 must be derived from:

```text
NarrativeStory
```

and ultimately traceable to:

```text
CareerRecord
```

The engine must not introduce unsupported facts through templates.

Templates must be designed so that missing fields result in omission rather than invention.

---

# 32. TEMPLATE SAFETY

Templates must support optional fields.

For example:

```text
"{player_name} joined {club_name} in {season}."
```

If `season` is unavailable:

DO NOT produce:

```text
"{player_name} joined {club_name} that season."
```

unless chronology supports it.

Instead use:

```text
"{player_name} joined {club_name}."
```

Templates must degrade safely.

---

# 33. NO HALLUCINATION INVARIANT

The following invariant must always hold:

```text
Every factual claim in StoryScript
    ↓
has source reference
    ↓
source exists in NarrativeStory/CareerRecord
```

A validation function must detect violations.

---

# 34. SCRIPT COHERENCE VALIDATION

Implement:

```text
validate_script_coherence(...)
```

It must verify:

* section ordering;
* segment ordering;
* unique IDs;
* valid source references;
* chronology;
* climax inclusion;
* resolution consistency;
* active/retired consistency;
* word count;
* duration;
* density constraints;
* no unsupported references.

---

# 35. ACTIVE CAREER SAFETY

Explicitly test:

```text
active career
```

must never produce:

```text
retirement
career ended
final chapter
last season
former player
```

unless those facts are explicitly supported.

---

# 36. RETIREMENT SAFETY

Explicitly test:

```text
retirement event
```

and:

```text
retirement milestone
```

including cases where one collection is empty.

Retirement detection must work independently for events and milestones.

---

# 37. EMPTY CAREER

For an empty CareerRecord/NarrativeStory:

The engine must:

* return a typed failure or minimal valid script according to specification;
* never fabricate a career;
* never fabricate a player history;
* never fabricate achievements.

---

# 38. SHORT CAREER

For very short careers:

* avoid forcing a standard five-act structure;
* avoid fabricated conflict;
* avoid fabricated climax;
* produce a concise script;
* preserve factual grounding.

---

# 39. SERIALIZATION

Extend:

```text
to_json_bytes()
```

to support all Phase 11 objects.

Serialization must be:

```text
UTF-8
deterministic
stable
sorted
```

Equivalent inputs must produce equivalent bytes.

---

# 40. DETERMINISM

Phase 11 must be completely deterministic.

Forbidden:

```text
random
random.random()
hash()
uuid.uuid4()
timestamps
process IDs
memory addresses
unordered nondeterministic iteration
```

Use SHA-256 for deterministic identifiers where necessary.

Given identical:

```text
NarrativeStory
configuration
density
style
tone
target_duration
```

the output must be identical.

---

# 41. IMMUTABILITY

Phase 11 must never mutate:

```text
NarrativeStory
StoryPremise
NarrativeProtagonist
NarrativeAct
NarrativeBeat
NarrativeConflict
NarrativeThread
CareerRecord
```

All input structures must remain unchanged.

---

# 42. ATOMICITY

Script generation must be atomic.

If any validation or rendering step fails:

```text
no partial successful StoryScript
input remains unchanged
typed error/result returned
```

---

# 43. CONFIGURATION

Create:

```text
backend/data/rules/script.json
```

for central presentation rules.

Configuration may include:

```text
default_words_per_minute
density weights
hook priorities
transition priorities
segment priorities
tone parameters
pacing parameters
duration tolerances
```

Do not bury large rule tables in Python.

---

# 44. API DESIGN

Implement the core engine in:

```text
backend/app/event/script_engine.py
```

Expected processing functions include:

```text
build_script_metadata
generate_story_hook
build_script_introduction
build_script_sections
build_script_segments
build_script_transitions
render_script_climax
render_script_resolution
generate_script_closing
calculate_script_word_count
estimate_script_duration
validate_script_coherence
build_story_script
```

Additional helper functions may be added when justified.

---

# 45. ORCHESTRATION

The main function should conceptually perform:

```text
build_story_script(...)
    ↓
validate input
    ↓
select hook
    ↓
build introduction
    ↓
build sections
    ↓
build segments
    ↓
build transitions
    ↓
render climax
    ↓
render resolution
    ↓
generate closing
    ↓
calculate words
    ↓
estimate duration
    ↓
validate coherence
    ↓
return StoryScript
```

No stage may mutate the input.

---

# 46. EXPORTS

Update:

```text
backend/app/event/__init__.py
```

to expose all public Phase 11 domain models and processing functions.

Do not remove existing Phase 8, 9, or 10 exports.

---

# 47. TEST SUITE

Create:

```text
backend/tests/test_event_phase11.py
```

and, if necessary:

```text
backend/tests/test_event_11_audit.py
```

Tests must cover at minimum:

### Domain

* construction;
* validation;
* immutability;
* nested immutability;
* invalid values.

### Hook

* cold open;
* major achievement;
* comeback;
* rivalry;
* crisis;
* legacy;
* fallback;
* deterministic selection.

### Introduction

* player identity;
* available metadata;
* missing metadata;
* safe omission.

### Sections

* ordering;
* act mapping;
* unsupported acts;
* short careers;
* long careers.

### Segments

* generation;
* ordering;
* source references;
* word count;
* deterministic IDs.

### Transitions

* time transitions;
* contrast;
* escalation;
* recovery;
* resolution;
* no unsupported causality.

### Climax

* correct Phase 10 climax preserved;
* source traceability;
* deterministic rendering.

### Resolution

* active;
* retired;
* decline;
* comeback;
* ongoing.

### Closing

* legacy;
* ongoing;
* retirement;
* open-ended.

### Density

* COMPACT;
* STANDARD;
* DETAILED;
* COMPLETE.

### Duration

* target duration;
* short target;
* long target;
* insufficient material.

### Factual grounding

Explicitly verify that unsupported facts cannot be generated.

### Template safety

Verify missing fields do not produce fabricated information.

### Immutability

Verify Phase 10 and Phase 9 inputs remain unchanged.

### Atomicity

Force rendering/validation failures and verify no partial result is returned.

### Determinism

Run:

```text
1x
10x
100x
```

and compare serialized output.

### Cross-process

Run identical input in independent Python processes.

### Replay

Build the same script repeatedly and compare:

```text
script_a == script_b
serialized_a == serialized_b
```

---

# 48. END-TO-END TEST

Create an integration test:

```text
Phase 8
    ↓
Phase 9
    ↓
Phase 10
    ↓
Phase 11
```

Verify:

```text
Event Resolution
    ↓
Effect Application
    ↓
Career History
    ↓
NarrativeStory
    ↓
StoryScript
```

The test must use real domain objects where practical.

---

# 49. REGRESSION TESTS

Run:

```bash
pytest
```

and verify:

```text
Phase 8A
Phase 8B
Phase 8C
Phase 8D
Phase 8E
Phase 8F
Phase 9
Phase 10
Phase 11
Integration
Full suite
```

No previous phase may regress.

---

# 50. SECURITY AUDIT

Search Phase 11 for:

```text
eval(
exec(
compile(
random.
uuid.uuid4
hash(
datetime.now
time.time
```

Also inspect imports for:

```text
requests
httpx
urllib
FastAPI
SQLAlchemy
```

There must be no external network dependency.

---

# 51. DIFF AUDIT

Before completion:

```bash
git status
git diff --stat
git diff
```

Every modified file must be classified:

```text
EXPECTED
NECESSARY
UNRELATED
```

Do not leave unrelated modifications.

---

# 52. FINAL IMPLEMENTATION REPORT

Jules must return a report containing:

1. Implementation status
2. Domain models
3. Script engine functions
4. Hook engine
5. Introduction
6. Section assembly
7. Segment generation
8. Transition engine
9. Climax rendering
10. Resolution rendering
11. Closing engine
12. Word counting
13. Duration estimation
14. Density handling
15. Target duration handling
16. Factual grounding
17. Template safety
18. Traceability
19. Determinism
20. Cross-process determinism
21. Immutability
22. Atomicity
23. Serialization
24. Configuration
25. Phase 8 → 9 → 10 → 11 integration
26. Regression results
27. Test results
28. Files changed
29. Code review findings
30. Remaining limitations

Report exact test counts.

The final recommendation must be exactly one of:

```text
READY FOR PHASE 11 AUDIT
```

or:

```text
PHASE 11 REQUIRES FIXES
```

Do not claim readiness if any required invariant has not been verified.

---

# 53. ARCHITECTURAL INVARIANTS

The following invariants are mandatory:

```text
I1:
Phase 11 never changes simulation state.

I2:
Phase 11 never modifies CareerRecord or NarrativeStory.

I3:
Phase 11 never invents factual information.

I4:
Every factual script segment is traceable to source data.

I5:
Phase 11 never changes the Phase 10 narrative structure.

I6:
Phase 11 may change presentation wording but not factual meaning.

I7:
Active careers cannot be presented as completed careers.

I8:
Retirement detection works when events or milestones are individually absent.

I9:
Identical inputs always produce identical scripts.

I10:
Different Python processes produce identical serialized output.

I11:
Script generation is atomic.

I12:
Serialization is deterministic.

I13:
No external APIs are required.

I14:
No persistence dependency exists inside the narrative/script engine.

I15:
Future voice/video systems can consume StoryScript without modifying Phase 11.
```

---

# 54. FINAL PIPELINE

After Phase 11 the architecture must be:

```text
┌──────────────────────────┐
│       PHASE 8            │
│     Event Engine         │
└────────────┬─────────────┘
             ↓
┌──────────────────────────┐
│       PHASE 9            │
│    Career History        │
└────────────┬─────────────┘
             ↓
┌──────────────────────────┐
│       PHASE 10           │
│   Narrative Structure    │
└────────────┬─────────────┘
             ↓
      NarrativeStory
             ↓
┌──────────────────────────┐
│       PHASE 11           │
│ Story Script Engine      │
└────────────┬─────────────┘
             ↓
        StoryScript
             ↓
┌──────────────────────────┐
│      FUTURE PHASE        │
│    Voice Generation      │
│    Visual Generation     │
│    Video Assembly        │
└──────────────────────────┘
```

Phase 11 is considered complete only when:

```text
Phase 8 → Phase 9 → Phase 10 → Phase 11
```

works deterministically, immutably, atomically, factually, and with complete traceability.
