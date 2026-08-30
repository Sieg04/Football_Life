# PHASE 16 — CAREER REPLAY & CONTENT CAPTURE

**Project:** Football Life
**Phase:** 16
**Status:** Design Specification
**Depends on:** Phases 8–15
**Primary platform:** Desktop / Local Web Application
**Implementation assistant:** Jules

---

# 1. PURPOSE

Phase 16 introduces the **Career Replay & Content Capture Layer**.

The purpose of this phase is to transform an already simulated Football Life career into a convenient, visually attractive sequence of moments and scenes that the user can manually record.

Football Life is **not** becoming a video editor or automatic video generator.

The user remains responsible for:

* simulating the career;
* deciding what moments are interesting;
* controlling the storytelling;
* recording the screen;
* narrating the story;
* editing the final video.

Football Life provides the visual interface and tooling required to make this process easy.

The central product principle is:

> **Football Life does not create the video. Football Life creates a career worth recording and provides the tools to tell its story.**

---

# 2. PRODUCT GOAL

Phase 16 should enable this workflow:

```text
Simulate Career
      ↓
Complete / Pause Career
      ↓
Open CONTENT MODE
      ↓
Review Career Moments
      ↓
Select Interesting Moments
      ↓
Build Content Story
      ↓
Arrange Scenes
      ↓
Preview Scene
      ↓
Enter Capture View
      ↓
Record Screen Manually
```

The phase must integrate with existing Phase 12–15 presentation infrastructure instead of duplicating career information.

---

# 3. SCOPE

Phase 16 includes:

* career replay representation;
* replay seasons;
* replay moments;
* automatic identification of potentially interesting moments;
* manual scene selection;
* content story construction;
* scene ordering;
* scene preview;
* capture frames;
* cinematic capture view;
* recording-mode integration;
* keyboard navigation;
* content-oriented visual presentation;
* backend replay API;
* Angular replay/content UI;
* deterministic processing;
* immutable domain structures;
* factual grounding;
* complete audit testing.

---

# 4. EXPLICIT NON-GOALS

Phase 16 MUST NOT implement:

* automatic video rendering;
* MP4 generation;
* video editing;
* video trimming;
* automatic voice generation;
* text-to-speech;
* AI narration;
* automatic music generation;
* automatic music synchronization;
* TikTok API integration;
* YouTube API integration;
* social media publishing;
* OBS integration;
* screen recording APIs;
* external video-processing libraries;
* external network services;
* generative AI;
* automatic scene video generation;
* automatic image generation.

The capture view only prepares the browser interface for **manual screen recording**.

---

# 5. ARCHITECTURAL POSITION

The complete pipeline becomes:

```text
Phase 8
Event Simulation
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
Career Presentation
      ↓
Phase 13
Career Viewer
      ↓
Phase 14
Interactive Career
      ↓
Phase 15
Visual / UX Refinement
      ↓
Phase 16
Career Replay & Content Capture
```

Phase 16 consumes existing outputs.

It must not replace or duplicate:

* event simulation;
* career recording;
* narrative generation;
* script generation;
* presentation generation.

---

# 6. CORE PRINCIPLE: TIMELINE ≠ STORY

The existing career timeline represents chronological reality.

The Phase 16 content story represents the user's desired storytelling order.

Therefore:

```text
Career Timeline
    =
Chronological Order

Content Story
    =
Storytelling Order
```

A scene may therefore appear in a different order from its chronological position.

Example:

```text
01 — CLIMAX
02 — FIVE YEARS EARLIER
03 — BEGINNING
04 — BREAKTHROUGH
05 — TRANSFER
06 — FALL
07 — COMEBACK
08 — LEGACY
```

The underlying career data remains unchanged.

---

# 7. BACKEND MODULE STRUCTURE

Create:

```text
backend/app/event/replay_domain.py
backend/app/event/replay_engine.py
backend/app/api/replay.py
backend/data/rules/replay.json
```

Tests:

```text
backend/tests/test_event_phase16.py
backend/tests/test_event_16_audit.py
backend/tests/test_api_replay.py
```

Do not modify unrelated phase modules unless strictly required for integration.

---

# 8. DOMAIN ENUMS

Implement the following enums.

## 8.1 ReplayMomentType

```text
CAREER_START
DEBUT
GOAL_MILESTONE
STAT_MILESTONE
TRANSFER
ACHIEVEMENT
CONFLICT
TURNING_POINT
BREAKTHROUGH
COMEBACK
CAREER_PEAK
CAREER_END
SEASON
OTHER
```

---

## 8.2 SceneType

```text
INTRO
CAREER_MOMENT
SEASON
TRANSFER
ACHIEVEMENT
CONFLICT
TURNING_POINT
CLIMAX
ENDING
STAT_CARD
```

---

## 8.3 ScenePriority

```text
LOW
MEDIUM
HIGH
CRITICAL
```

---

## 8.4 CapturePresetType

```text
CINEMATIC
MATCHDAY
DOCUMENTARY
PROFILE
```

---

## 8.5 ReplayErrorCode

At minimum:

```text
INVALID_SOURCE
INVALID_MOMENT
INVALID_SCENE
DUPLICATE_SCENE
INVALID_ORDER
EMPTY_CONTENT_STORY
INVALID_CAPTURE_FRAME
INVALID_REFERENCE
INCONSISTENT_STATE
```

Additional codes may be added when justified by implementation.

---

# 9. DOMAIN MODELS

All Phase 16 domain objects MUST be immutable.

Use:

```python
@dataclass(frozen=True)
```

Collections must use:

* tuples;
* immutable mappings such as `MappingProxyType`.

No mutable lists or dictionaries may escape through public domain objects.

---

# 10. CareerReplay

`CareerReplay` represents the replayable representation of a career.

Required conceptual fields:

```text
replay_id
career_id
player_id
player_name
career_status
seasons
moments
source_story_id
source_script_id
source_presentation_id
```

Additional fields may be included if required by the specification.

The replay must retain traceability to the source career.

---

# 11. ReplaySeason

Represents a season in the career replay.

Required information:

```text
season_id
season_label
season_index
club_id
club_name
appearances
goals
assists
trophies
ovr
moment_ids
source_references
```

Values must come directly from existing career/presentation data.

---

# 12. ReplayMoment

Represents an important career moment.

Required information:

```text
moment_id
moment_type
title
description
season_id
priority
visual_priority
source_event_ids
source_milestone_ids
source_turning_point_ids
source_seed_ids
```

A `ReplayMoment` MUST NOT invent facts.

If there is no source data supporting a moment, the moment must not be generated.

---

# 13. ContentScene

Represents a moment selected for the user's content story.

Required conceptual fields:

```text
scene_id
scene_type
title
subtitle
description
order_index
priority
moment_id
season_id
source_references
script_segment_ids
presentation_references
```

A scene is a presentation object.

It does not modify the career.

---

# 14. ContentStory

Represents the user's selected sequence of scenes.

Required conceptual fields:

```text
content_story_id
career_id
title
scenes
total_scenes
estimated_duration_seconds
source_story_id
source_script_id
```

The `scenes` collection must be immutable.

Scene order is explicitly part of the content story.

---

# 15. CapturePreset

Represents visual capture configuration.

Required fields:

```text
preset_id
preset_type
width
height
show_navigation
show_controls
show_branding
show_statistics
show_player_identity
show_season
```

The default capture resolution is:

```text
1920 × 1080
```

No actual screen recording is performed by this object.

---

# 16. CaptureFrame

Represents the information required to render a selected scene in capture mode.

Required conceptual fields:

```text
frame_id
scene_id
preset
player_name
club_name
season
headline
subheadline
statistics
visual_priority
```

It must contain only presentation information.

---

# 17. ReplayBuildResult

Represents replay processing output.

It should expose:

```text
success
replay
errors
warnings
```

The result must be immutable.

---

# 18. CONTENT STORY BUILD RESULT

If the implementation requires a separate result for content-story creation, implement:

```text
ContentStoryBuildResult
```

with:

```text
success
content_story
errors
warnings
```

It must remain immutable.

---

# 19. REPLAY ENGINE

Create:

```text
backend/app/event/replay_engine.py
```

The engine must be deterministic and side-effect free.

---

# 20. REQUIRED ENGINE FUNCTIONS

Implement at minimum:

```python
build_career_replay()
identify_replay_moments()
build_replay_seasons()
build_content_scene()
build_content_story()
reorder_content_scenes()
build_capture_frame()
validate_content_story()
validate_career_replay()
```

A top-level orchestration function should be provided:

```python
build_replay()
```

or an equivalent clearly documented orchestration API.

---

# 21. build_career_replay()

Input:

```text
CareerRecord
NarrativeStory
StoryScript
CareerPresentation
```

The function must construct a deterministic `CareerReplay`.

It must:

1. validate all sources;
2. extract seasons;
3. identify replay moments;
4. establish traceability;
5. produce deterministic IDs;
6. return an immutable result.

It must not mutate any input.

---

# 22. build_replay_seasons()

Extract season information from existing career/presentation data.

Season ordering must be chronological.

Use explicit stable sorting keys.

Never rely on:

```python
set
hash()
dictionary iteration without ordering guarantees
```

for output ordering.

---

# 23. identify_replay_moments()

Identify potentially interesting moments based exclusively on source data.

Potential candidates include:

```text
career start
debut
major goals
statistical milestones
transfers
trophies
conflicts
turning points
breakthroughs
comebacks
career peak
career ending
```

A moment must only exist when its source data supports it.

---

# 24. MOMENT PRIORITY

Priority should be derived from source significance.

Suggested conceptual ranking:

```text
CRITICAL
    career climax
    major turning point
    major achievement
    major transfer

HIGH
    breakthrough
    important milestone
    significant conflict

MEDIUM
    notable season
    ordinary milestone

LOW
    informational moment
```

The exact thresholds must be controlled by:

```text
backend/data/rules/replay.json
```

Do not hardcode large rule tables in Python.

---

# 25. Content Scene Creation

A selected replay moment can be converted into a `ContentScene`.

The scene must preserve:

```text
moment_id
source IDs
season
career references
script references
presentation references
```

No source information may be lost.

---

# 26. Scene Selection

The user can manually select moments.

The backend must support creating a content story from selected moments.

Duplicate moments must not produce duplicate scenes unless explicitly supported by the design.

Default behavior:

```text
same moment → one scene
```

---

# 27. Scene Ordering

The user must be able to reorder scenes.

Example:

```text
Original:

01 Debut
02 First Goal
03 Transfer
04 Trophy
05 Injury
06 Comeback

User order:

01 Transfer
02 Debut
03 First Goal
04 Injury
05 Comeback
06 Trophy
```

The career itself is unaffected.

`order_index` must be recalculated deterministically.

---

# 28. Atomic Reordering

`reorder_content_scenes()` must be atomic.

If:

* a scene ID does not exist;
* a duplicate scene ID exists in the requested order;
* a scene is missing;
* the requested order is invalid;

then the operation must fail without modifying the original content story.

---

# 29. Content Story Duration

Estimated duration may be calculated from associated script segments.

Use existing Phase 11 script metadata whenever available.

Do not generate new narration.

Do not silently invent word counts.

If no script duration is available, the duration may be marked unavailable or calculated only from explicitly supported source information.

---

# 30. Phase 11 Integration

Scenes may reference:

```text
StoryScript
ScriptSection
ScriptSegment
ScriptHook
ScriptClosing
```

This allows the user to see which narration corresponds to a scene.

Example:

```text
SCENE 04
TRANSFER

Narration:

"The move changed everything."

Source:
Script Segment #17
```

The application must not synthesize unsupported facts.

---

# 31. Phase 12/13 Integration

Phase 16 must reuse:

```text
CareerPresentation
```

and existing Phase 13 presentation concepts.

Do not duplicate:

* player statistics;
* club history;
* achievements;
* relationships;
* career arcs;
* narrative data.

Phase 16 is a composition layer.

---

# 32. ACTIVE VS RETIRED CAREERS

Phase 16 must preserve the safety rules established in previous phases.

For active careers:

```text
do not imply retirement
do not imply career completion
do not display unsupported ending scenes
```

For retired/completed careers:

```text
career ending
legacy
final season
career conclusion
```

may be presented when source data supports them.

---

# 33. FACTUAL GROUNDING

Every replay moment and scene must be traceable to source information.

At minimum, traceability should support:

```text
event IDs
milestone IDs
turning point IDs
seed IDs
act IDs
beat IDs
script segment IDs
presentation references
```

Not every scene needs every reference.

But every factual claim must have an appropriate source.

---

# 34. DETERMINISM

Phase 16 MUST be deterministic.

Forbidden:

```python
random
uuid.uuid4()
datetime.now()
time.time()
hash()
```

IDs must be derived using deterministic hashing.

Recommended:

```text
SHA-256
```

Example conceptual identity:

```text
career_id
+
moment_type
+
source_id
```

Output ordering must also be deterministic.

---

# 35. CROSS-PROCESS DETERMINISM

The same career input must produce byte-identical output across:

* repeated executions;
* separate Python processes;
* rebuilds.

Audit tests must verify this.

---

# 36. IMMUTABILITY

Phase 16 must not mutate:

```text
CareerRecord
CareerEvent
CareerMilestone
CareerTurningPoint
NarrativeStory
StoryScript
CareerPresentation
```

Mutation attempts on Phase 16 domain objects must fail.

Nested collections must also be immutable.

---

# 37. ATOMICITY

All public transformation operations must be atomic.

On invalid input:

```text
no partial output
no source mutation
typed exception/result
```

must be produced.

---

# 38. CONFIGURATION

Create:

```text
backend/data/rules/replay.json
```

Configuration should contain:

```json
{
  "version": 1,
  "moment_priority": {},
  "duration": {},
  "capture": {},
  "limits": {},
  "presets": {}
}
```

The exact schema may be expanded where necessary.

Configuration must be validated on load.

Invalid configuration must fail explicitly.

---

# 39. API

Create:

```text
backend/app/api/replay.py
```

Register it in:

```text
backend/app/main.py
```

Only modify `main.py` as required for router registration.

---

# 40. REQUIRED API ENDPOINTS

## GET replay

```http
GET /career/{career_id}/replay
```

Returns the replay representation.

---

## GET moments

```http
GET /career/{career_id}/replay/moments
```

Returns identified replay moments.

Optional filtering may include:

```text
priority
type
season
```

Filtering must not modify source data.

---

## POST content story

```http
POST /career/{career_id}/content-story
```

Creates a content story from selected moment IDs.

---

## GET content story

```http
GET /career/{career_id}/content-story
```

Returns the current content story representation.

If persistence does not exist, an in-memory session-scoped implementation is acceptable.

---

## PUT content story order

```http
PUT /career/{career_id}/content-story/order
```

Reorders scenes.

Invalid orders must return an appropriate HTTP error.

---

## GET capture frame

```http
GET /career/{career_id}/capture/{scene_id}
```

Returns the capture-frame data required by the frontend.

---

# 41. API SAFETY

The API must:

* validate IDs;
* validate payloads;
* reject invalid scene references;
* return appropriate HTTP status codes;
* avoid exposing internal exceptions;
* avoid mutating source career records;
* avoid arbitrary file access;
* avoid dynamic code execution.

---

# 42. FRONTEND STRUCTURE

Create:

```text
frontend/football-life/src/app/career/career-replay/
frontend/football-life/src/app/career/career-moments/
frontend/football-life/src/app/career/content-story/
frontend/football-life/src/app/career/content-scene/
frontend/football-life/src/app/career/capture-view/
frontend/football-life/src/app/career/scene-controls/
```

Exact component decomposition may be adjusted if Angular architecture benefits from consolidation.

Do not create unnecessary abstractions.

---

# 43. FRONTEND SERVICE

Create:

```text
frontend/football-life/src/app/core/services/replay.service.ts
```

Responsibilities:

* load replay;
* load moments;
* create content story;
* load content story;
* reorder scenes;
* load capture frames;
* expose reactive state where useful;
* handle API errors;
* provide safe fallback behavior where appropriate.

The service must not contain career simulation logic.

---

# 44. CONTENT ROUTE

Add:

```text
/career/content
```

or an equivalent nested route under the active career.

The preferred route is:

```text
/career/content
```

The route should be accessible from the Phase 13/14 career shell.

---

# 45. CONTENT MODE

The Content section should clearly communicate that the user is preparing material for recording.

Suggested header:

```text
CONTENT MODE
```

Possible supporting text:

```text
Build your story. Pick the moments worth recording.
```

The visual identity must remain consistent with Football Life.

---

# 46. CAREER REPLAY VIEW

The replay screen should show:

```text
Career
Season list
Timeline
Moments
Moment priority
Club
Statistics
```

The user should be able to move through the career chronologically.

---

# 47. MOMENTS VIEW

Show automatically identified moments as visual cards.

Example:

```text
┌──────────────────────────────┐
│ ★ HIGH                      │
│                              │
│ FIRST PROFESSIONAL GOAL      │
│ 2026/27                      │
│ FC Barcelona                │
│                              │
│ [ ADD TO STORY ]             │
└──────────────────────────────┘
```

Important moments should have stronger visual emphasis.

---

# 48. MOMENT FILTERING

Provide simple filtering:

```text
ALL
CRITICAL
HIGH
MEDIUM
LOW
```

Optional:

```text
ALL TYPES
TRANSFERS
ACHIEVEMENTS
TURNING POINTS
CLIMAX
```

Do not create overly complex filtering systems.

---

# 49. CONTENT STORY BOARD

The storyboard is the user's selected sequence.

Example:

```text
MY STORY

01  THE BEGINNING
02  FIRST BREAKTHROUGH
03  THE TRANSFER
04  THE FALL
05  THE COMEBACK
06  THE PEAK
```

Each scene should support:

```text
Preview
Remove
Move up
Move down
```

Drag-and-drop may be implemented if it remains simple and reliable, but is not mandatory.

---

# 50. SCENE PREVIEW

Selecting a scene should display:

```text
Scene title
Season
Club
OVR
Statistics
Narrative information
Script text if available
Source information where useful
```

The preview should resemble the final capture view.

---

# 51. CAPTURE VIEW

The capture view is the visual centerpiece of Phase 16.

Target:

```text
1920 × 1080
```

The view should prioritize:

* player identity;
* club;
* season;
* OVR;
* relevant statistics;
* scene title;
* major visual accent;
* Football Life branding.

---

# 52. CAPTURE VIEW PRINCIPLES

The capture view must be:

```text
cinematic
minimal
high contrast
clean
readable
recording-friendly
```

Avoid:

* excessive UI;
* sidebars;
* tiny text;
* unnecessary controls;
* debugging information;
* excessive animation.

---

# 53. CAPTURE PRESETS

## CINEMATIC

Default.

Focus:

```text
large typography
player identity
dramatic spacing
minimal UI
storytelling
```

---

## MATCHDAY

Focus:

```text
club
season
statistics
match-like information
```

---

## DOCUMENTARY

Focus:

```text
large text
story information
timeline
narrative
minimal statistics
```

---

## PROFILE

Focus:

```text
player
OVR
club
career statistics
identity
```

---

# 54. DEFAULT PRESET

The default preset must be:

```text
CINEMATIC
```

Default dimensions:

```text
1920 × 1080
```

---

# 55. CAPTURE CONTROLS

Controls should be visually unobtrusive.

Suggested controls:

```text
← Previous
→ Next
SPACE Hide UI
ESC Exit Capture
R Recording Mode
```

Keyboard shortcuts must not trigger browser-destructive behavior.

---

# 56. HIDDEN UI

When the user activates:

```text
HIDE UI
```

all non-essential controls must disappear.

The scene content remains visible.

The application should then provide a clean surface suitable for screen recording.

---

# 57. RECORDING MODE

Phase 15's Recording Mode must be reused.

Phase 16 extends it rather than replacing it.

The flow becomes:

```text
Content Story
      ↓
Select Scene
      ↓
Preview
      ↓
Capture
      ↓
Recording Mode
      ↓
1920 × 1080
```

No actual recording API is required.

---

# 58. RESPONSIVE BEHAVIOR

The application is primarily intended for desktop recording.

Desktop is the priority.

Still ensure:

* no layout overflow at normal desktop resolutions;
* acceptable behavior at smaller widths;
* no broken navigation;
* usable keyboard controls.

The canonical recording viewport is:

```text
1920 × 1080
```

---

# 59. VISUAL IDENTITY

Phase 16 must maintain the Football Life visual language established in Phases 13–15.

Use:

```text
dark cinematic foundation
strong contrast
Football Life accent color
Barlow Condensed for display typography
DM Sans for supporting text
```

Reuse existing design tokens from:

```text
frontend/football-life/src/styles.scss
```

Do not introduce a second independent design system.

---

# 60. LOGO

Use the existing Football Life logo:

```text
frontend/football-life/public/assets/fl_logo.png
```

Do not generate a replacement logo.

The logo should be used selectively.

Capture mode must avoid oversized branding that competes with the player/story content.

---

# 61. ANIMATION

Animation should remain restrained.

Use animation for:

* scene transitions;
* card appearance;
* priority emphasis;
* capture-mode transitions.

Avoid:

* constant movement;
* excessive particle effects;
* distracting looping animation.

Respect:

```css
prefers-reduced-motion
```

---

# 62. ACCESSIBILITY

The frontend must support:

* keyboard navigation;
* visible focus states;
* semantic buttons;
* accessible labels;
* sufficient text contrast;
* logical heading hierarchy;
* reduced motion preferences.

Capture controls must have accessible names.

---

# 63. PERFORMANCE

Phase 16 must remain lightweight.

Avoid:

* unnecessary polling;
* large third-party libraries;
* video-processing libraries;
* canvas-heavy rendering;
* uncontrolled animations.

Replay generation should remain fast for normal career sizes.

---

# 64. SECURITY

Forbidden:

```text
eval
exec
new Function
dynamic code execution
unsafe HTML interpolation
external network calls
hardcoded credentials
```

No user-provided text may be interpreted as executable code.

Angular templates must use normal Angular escaping/binding.

---

# 65. SERIALIZATION

Extend:

```text
backend/app/event/domain.py
```

only if required to support Phase 16 serialization.

`to_json_bytes()` must support all Phase 16 domain objects.

Requirements:

```text
UTF-8
sorted keys
stable serialization
deterministic bytes
```

Existing Phase 8–15 serialization behavior must remain unchanged.

---

# 66. EXPORTS

Update:

```text
backend/app/event/__init__.py
```

to expose Phase 16 public:

* domain models;
* enums;
* exceptions;
* engine functions.

Do not remove or alter existing public exports.

---

# 67. TESTING

Create:

```text
backend/tests/test_event_phase16.py
backend/tests/test_event_16_audit.py
backend/tests/test_api_replay.py
```

Frontend tests must cover the Phase 16 components and service.

---

# 68. DOMAIN TESTS

Test:

* valid construction;
* invalid construction;
* enum validation;
* immutable fields;
* immutable nested collections;
* invalid references;
* empty replay;
* active career;
* retired career;
* invalid scene;
* duplicate scenes.

---

# 69. REPLAY TESTS

Test:

* season extraction;
* chronological ordering;
* moment detection;
* priority assignment;
* source traceability;
* deterministic IDs;
* missing source data;
* sparse careers;
* active careers;
* completed careers.

---

# 70. CONTENT STORY TESTS

Test:

* scene creation;
* scene selection;
* duplicate prevention;
* scene ordering;
* reordering;
* invalid order;
* empty story;
* atomicity;
* immutable output.

---

# 71. CAPTURE TESTS

Test:

* capture frame generation;
* each capture preset;
* default 1920×1080 resolution;
* scene references;
* active career safety;
* missing statistics;
* missing script data.

---

# 72. DETERMINISM AUDIT

At least:

```text
100 repeated builds
```

must produce identical results.

Also verify:

```text
cross-process determinism
```

using a separate Python process.

---

# 73. IMMUTABILITY AUDIT

Take snapshots of:

```text
CareerRecord
NarrativeStory
StoryScript
CareerPresentation
```

before replay generation.

Verify byte/value equality afterward.

---

# 74. SECURITY AUDIT

Search Phase 16 code for:

```text
eval
exec
compile
new Function
random
uuid4
datetime.now
time.time
requests
```

Any legitimate occurrence must be reviewed.

No unsafe dynamic behavior may be introduced.

---

# 75. REGRESSION TESTING

The full existing test suite must continue passing.

At minimum verify:

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
```

No earlier phase behavior may regress.

---

# 76. FRONTEND TESTING

Run:

```bash
npx ng test --watch=false --browsers=ChromeHeadless
```

All relevant tests must pass.

---

# 77. ANGULAR BUILD

Run:

```bash
npm run build
```

Production build must complete successfully with no errors.

---

# 78. VISUAL VERIFICATION

Use browser/Playwright verification.

At minimum inspect:

```text
Content Mode
Replay
Moments
Content Story
Scene Preview
Capture View
1920×1080 Recording Mode
```

Capture screenshots for visual inspection.

Verify:

* no clipping;
* no overflow;
* typography;
* logo;
* contrast;
* scene hierarchy;
* responsive behavior;
* hidden UI mode.

---

# 79. GIT HYGIENE

Before completion:

```bash
git status
git diff --stat
```

Verify:

* only expected Phase 16 files changed;
* no generated logs;
* no screenshots accidentally committed;
* no build artifacts;
* no temporary files;
* no credentials;
* no debug output.

Do not commit:

```text
*.log
dist/
coverage/
temporary screenshots
browser recordings
```

unless explicitly required by the repository.

---

# 80. PHASE BOUNDARIES

Phase 16:

```text
READS:
Phase 8
Phase 9
Phase 10
Phase 11
Phase 12
Phase 13
Phase 14
Phase 15

CREATES:
Replay
Moments
Content Story
Capture Frames
Content UI

MUST NOT MODIFY:
Simulation rules
Career history semantics
Narrative generation semantics
Script generation semantics
Presentation semantics
```

Any modification outside these boundaries requires explicit justification.

---

# 81. ACCEPTANCE CRITERIA

Phase 16 is complete only when all of the following are true.

### Backend

```text
CareerReplay implemented
ReplaySeason implemented
ReplayMoment implemented
ContentScene implemented
ContentStory implemented
CapturePreset implemented
CaptureFrame implemented
ReplayBuildResult implemented
```

### Engine

```text
Replay generation works
Moment detection works
Scene creation works
Scene ordering works
Capture frame generation works
Validation works
```

### API

```text
Replay endpoint works
Moments endpoint works
Content Story creation works
Content Story retrieval works
Scene ordering endpoint works
Capture frame endpoint works
```

### Frontend

```text
Replay view works
Moments view works
Content Story board works
Scene preview works
Capture View works
Recording Mode integration works
Keyboard navigation works
```

### Integrity

```text
Determinism PASS
Immutability PASS
Atomicity PASS
Factual grounding PASS
Traceability PASS
Security PASS
Phase boundaries PASS
```

### Build

```text
Backend tests PASS
Frontend tests PASS
Angular build PASS
Visual verification PASS
```

---

# 82. FINAL USER EXPERIENCE

The finished experience should feel like:

```text
CAREER
   ↓
CONTENT
   ↓
"Your career has a story."
   ↓
CAREER MOMENTS
   ↓
Select moments
   ↓
MY STORY
   ↓
Arrange scenes
   ↓
Preview
   ↓
CAPTURE
   ↓
CINEMATIC 1920×1080 VIEW
   ↓
User manually records screen
```

The application should make the user feel that they are preparing a **sports documentary about their generated football career**, not operating a video editor.

---

# 83. DESIGN PHILOSOPHY

The visual and functional philosophy of Phase 16 is:

> **Less software, more story.**

The application should disappear when recording starts.

The career should become the focus.

The interface should communicate:

```text
Football
Career
Drama
Progression
Identity
Memory
Legacy
```

without overwhelming the user.

---

# 84. IMPLEMENTATION CONSTRAINTS FOR JULES

Jules must:

1. Read `PHASE_16_DESIGN_SPEC.md` completely before modifying code.
2. Inspect existing Phases 8–15 before implementation.
3. Reuse existing domain models and presentation structures wherever possible.
4. Avoid duplicating existing career/narrative/presentation logic.
5. Avoid introducing external dependencies unless absolutely necessary.
6. Preserve all existing tests.
7. Preserve deterministic behavior.
8. Preserve immutability.
9. Preserve phase boundaries.
10. Implement only the scope defined in this specification.
11. Not implement automatic video generation.
12. Not implement external social-media integrations.
13. Not implement screen recording APIs.
14. Not modify previous phase semantics merely to simplify Phase 16.
15. Add tests for every new public behavior.
16. Perform backend and frontend verification before completion.
17. Perform Playwright visual verification.
18. Review `git diff` and remove unrelated artifacts before declaring completion.

---

# 85. DEFINITION OF DONE

Phase 16 is DONE when:

```text
[✓] Replay domain implemented
[✓] Replay engine implemented
[✓] Moment identification implemented
[✓] Content Story implemented
[✓] Scene ordering implemented
[✓] Capture Frame implemented
[✓] Replay API implemented
[✓] Angular Replay UI implemented
[✓] Content Story UI implemented
[✓] Capture View implemented
[✓] Recording Mode integrated
[✓] Keyboard controls implemented
[✓] Existing visual identity preserved
[✓] Factual grounding verified
[✓] Traceability verified
[✓] Determinism verified
[✓] Immutability verified
[✓] Atomicity verified
[✓] Security verified
[✓] Phase boundaries verified
[✓] Backend tests pass
[✓] Frontend tests pass
[✓] Angular production build passes
[✓] Playwright visual verification passes
[✓] Git hygiene verified
```

---

# 86. FINAL AUDIT REQUIREMENTS

The final Phase 16 audit must report:

```text
Overall Status

Product Purpose Verification

Backend Verification

API Verification

Frontend Verification

Replay Verification

Content Story Verification

Capture Mode Verification

Determinism

Immutability

Atomicity

Factual Grounding

Traceability

Serialization

Security

Phase Boundary Verification

Backend Tests

Frontend Tests

Angular Build

Visual Verification

Git Hygiene

Critical Findings

Non-Blocking Findings

Files Changed

Final Recommendation
```

The final recommendation must be one of:

```text
READY FOR NEXT PHASE
```

or:

```text
NOT READY
```

depending on actual verification results.

---

# 87. FINAL PRINCIPLE

Phase 16 must not turn Football Life into a video-production application.

It should instead complete the original product vision:

> **Generate a football career, experience it, discover its story, and make it easy for the user to tell that story visually.**

The user's creativity remains the final layer.

Football Life provides the world, the career, the story, and the stage.

The user presses record.
