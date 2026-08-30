# PHASE 15 — Product Polish, UX & Recording Experience

**Version:** 1.0
**Project:** Football Life
**Phase:** 15
**Type:** Product polish, UX refinement, visual experience and recording workflow
**Primary platform:** Desktop/local web application
**Development assistant:** Jules

---

# 1. PHASE OBJECTIVE

Phase 15 transforms the existing Football Life application from a functionally complete prototype into a **polished, visually coherent and recording-friendly product**.

The objective is **not** to introduce another simulation subsystem.

The objective is to improve the experience surrounding the already existing systems:

```text
Phase 8
Simulation
    ↓
Phase 9
Career History
    ↓
Phase 10
Narrative Structure
    ↓
Phase 11
Script
    ↓
Phase 12
Presentation
    ↓
Phase 13
Career Viewer
    ↓
Phase 14
Interactive Career Experience
    ↓
Phase 15
Product Polish + Recording Experience
```

Football Life should feel like a cohesive football career simulation interface rather than a collection of independently implemented screens.

---

# 2. PRODUCT PRINCIPLE

The application does **not** need to automatically create the final TikTok video.

The intended workflow is:

```text
User
  ↓
Creates player
  ↓
Starts career
  ↓
Advances career manually
  ↓
Experiences events
  ↓
Makes decisions
  ↓
Observes player evolution
  ↓
Explores career presentation
  ↓
Activates Recording Mode
  ↓
Records the application manually
  ↓
Edits footage externally
  ↓
Publishes content
```

Therefore:

> Football Life is the simulation and visual presentation tool. The user is the director.

Phase 15 must reinforce this philosophy.

---

# 3. SCOPE

Phase 15 includes:

* visual polish;
* UX refinement;
* navigation consistency;
* animation and transitions;
* improved career progression feedback;
* improved event presentation;
* improved decision presentation;
* improved statistics presentation;
* improved career timeline presentation;
* improved Recording Mode;
* screen-recording-friendly layouts;
* loading and empty states;
* error states;
* responsive desktop layouts;
* accessibility improvements;
* visual consistency;
* removal of obvious prototype-like UI behavior.

Phase 15 does **not** include:

* automatic video generation;
* video rendering;
* AI video generation;
* automatic narration;
* automatic voice generation;
* external video APIs;
* social media APIs;
* cloud persistence;
* multiplayer;
* online accounts;
* authentication;
* new simulation mechanics;
* new probability systems;
* new career-generation mechanics.

---

# 4. EXISTING ARCHITECTURE

Phase 15 must build on the existing architecture.

Expected stack:

```text
Frontend
Angular

Backend
FastAPI

Simulation
Existing Phase 8 engines

Career History
Phase 9

Narrative
Phase 10

Script
Phase 11

Presentation
Phase 12

Career Viewer
Phase 13

Interactive Career Session
Phase 14
```

Phase 15 must not replace these systems.

---

# 5. PHASE BOUNDARY

Phase 15 is primarily a **frontend/product layer**.

The backend should only be modified when strictly necessary to expose information already available to the existing systems.

The following must remain unchanged in behavior:

* Phase 8 simulation;
* Phase 9 career recording;
* Phase 10 narrative generation;
* Phase 11 script generation;
* Phase 12 presentation generation;
* Phase 13 presentation structures;
* Phase 14 career session mechanics.

No existing simulation formulas may be rewritten for visual reasons.

No Phase 8–14 domain model may be modified unless explicitly required for compatibility and proven non-breaking.

---

# 6. VISUAL DIRECTION

Football Life should use a distinctive visual identity rather than looking like a generic football management application.

The visual language should combine:

* football broadcast graphics;
* modern sports interfaces;
* cinematic career presentation;
* dark UI;
* strong typography;
* subtle technical/simulation aesthetics.

The existing Football Life logo must remain the primary brand asset.

Expected asset:

```text
frontend/football-life/public/assets/fl_logo.png
```

---

# 7. VISUAL CHARACTER

The interface should communicate:

```text
SPORT
+
CAREER
+
SIMULATION
+
CINEMATIC PRESENTATION
```

The visual style should feel:

* premium;
* dark;
* modern;
* slightly futuristic;
* athletic;
* cinematic;
* information-dense but readable.

Avoid:

* generic Bootstrap dashboards;
* excessive gradients;
* excessive glassmorphism;
* excessive rounded cards;
* childish football graphics;
* unnecessary neon effects;
* visually noisy backgrounds;
* excessive animations.

---

# 8. DESIGN SYSTEM

Central design tokens must remain in:

```text
frontend/football-life/src/styles.scss
```

Avoid scattering arbitrary colors throughout individual components.

At minimum define tokens for:

```text
--fl-bg
--fl-surface
--fl-surface-elevated
--fl-surface-hover
--fl-border
--fl-text
--fl-text-muted
--fl-text-subtle

--fl-accent
--fl-accent-soft

--fl-success
--fl-warning
--fl-danger
--fl-info

--fl-radius-sm
--fl-radius-md
--fl-radius-lg

--fl-shadow-sm
--fl-shadow-md
--fl-shadow-lg

--fl-transition-fast
--fl-transition-normal
```

Exact values may be chosen by implementation as long as the visual system remains coherent.

---

# 9. TYPOGRAPHY

Maintain the established typography direction:

### Display / sports typography

```text
Barlow Condensed
```

Use for:

* player names;
* OVR;
* major numbers;
* section titles;
* career milestones;
* large statistics.

### Interface typography

```text
DM Sans
```

Use for:

* descriptions;
* buttons;
* metadata;
* navigation;
* secondary information.

Typography must establish hierarchy rather than relying exclusively on font size.

---

# 10. GLOBAL UI PRINCIPLES

Every major screen should contain a clear hierarchy:

```text
Context
    ↓
Primary information
    ↓
Secondary information
    ↓
Actions
```

Avoid presenting all information with equal visual weight.

Important information must visually dominate.

Examples:

```text
87 OVR
€74M
FC BARCELONA
12 GOALS
```

should be immediately visible.

Less important metadata should remain visually subordinate.

---

# 11. NAVIGATION POLISH

The existing Phase 13/14 navigation must be refined.

Primary career navigation should provide access to:

```text
Dashboard
Profile
Timeline
Stats
Clubs
Achievements
Story
Script
```

During an active career, navigation should feel like one cohesive application rather than separate routes.

The active route must have a clearly visible state.

Navigation should:

* remain predictable;
* preserve career context;
* avoid unnecessary page reloads;
* provide clear transitions;
* work with keyboard navigation.

---

# 12. CAREER DASHBOARD

The Career Dashboard becomes the central gameplay screen.

It should visually prioritize:

```text
PLAYER
CURRENT SEASON
OVR
CURRENT CLUB
KEY STATS
CAREER STATUS
ADVANCE CAREER
```

Example structure:

```text
┌──────────────────────────────────────────────┐
│ FL LOGO                  2028/29   ACTIVE    │
├──────────────────────────────────────────────┤
│                                              │
│          ADRIAN MARTÍNEZ                     │
│          FC BARCELONA                        │
│                                              │
│              87                             │
│             OVR                             │
│                                              │
│  MATCHES    GOALS    ASSISTS    TROPHIES     │
│    28         12         5          2        │
│                                              │
│           [ ADVANCE CAREER ]                 │
│                                              │
└──────────────────────────────────────────────┘
```

The `ADVANCE CAREER` action should be the most visually important interactive control.

---

# 13. ADVANCE CAREER FEEDBACK

Advancing the career must feel meaningful.

After an advance operation, visually communicate relevant changes.

Potential changes:

```text
+1 OVR
+€5M value
+3 goals
New club
New milestone
New relationship
New event
Decision required
```

Do not fabricate changes.

Only display information actually returned by the career session/presentation data.

Where possible, use short animations:

```text
OLD VALUE
   ↓
transition
   ↓
NEW VALUE
```

Example:

```text
84 OVR
   ↓
85 OVR
```

Animation must not change underlying values.

---

# 14. EVENT PRESENTATION

Career events should receive stronger visual treatment.

Important events should feel like moments rather than ordinary notifications.

Event hierarchy:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

Critical events may use:

* stronger typography;
* larger presentation area;
* subtle entrance animation;
* accent treatment;
* temporary focus;
* optional sound-ready visual structure.

No audio implementation is required.

---

# 15. EVENT OVERLAY

The event overlay should contain:

```text
EVENT CATEGORY
TITLE
DESCRIPTION
SEASON / DATE
IMPACT
CONTINUE
```

The event should remain readable while recording.

Avoid tiny modal dialogs.

For high-priority events, use a cinematic composition.

---

# 16. DECISION PRESENTATION

Decision screens must feel like meaningful career choices.

Structure:

```text
DECISION
────────────

Situation

[ Option A ]
description
potential context

[ Option B ]
description
potential context

[ Option C ]
description
potential context
```

The interface must clearly communicate:

```text
A DECISION IS REQUIRED
```

while preventing accidental advancement.

The user must understand what action is expected.

---

# 17. DECISION FEEDBACK

After selecting an option, provide concise visual confirmation.

Example:

```text
DECISION RESOLVED

You chose:
"Stay at the club"

Career impact:
Contract situation updated
```

Only display effects that are actually produced by the underlying simulation.

---

# 18. PLAYER PROFILE

The Player Profile should be visually closer to a premium football player card/profile than a database form.

Prioritize:

```text
Player identity
Position
Nationality
Age
Club
OVR
Contract
Salary
Career relationships
```

Use visual grouping rather than long lists.

---

# 19. STATISTICS VIEW

The statistics view should communicate career progression visually.

Include:

* career totals;
* season statistics;
* goals;
* assists;
* appearances;
* trophies;
* progression.

Where appropriate, use:

* bars;
* progress indicators;
* large numerical values;
* compact tables.

Do not introduce chart libraries unless already available or strictly necessary.

Prefer lightweight CSS/SVG visualizations.

---

# 20. CLUB HISTORY

Club history should communicate the player's journey.

Example:

```text
ACADEMY
   ↓
CLUB A
   ↓
CLUB B
   ↓
CLUB C
   ↓
CURRENT CLUB
```

Transfers should be visually recognizable.

The current club should receive stronger emphasis.

---

# 21. ACHIEVEMENTS

Achievements should feel rewarding.

Important trophies or milestones should receive:

* visual prominence;
* clear labels;
* date/season;
* competition information;
* priority hierarchy.

Empty states must be intentional.

Do not display fake trophies or placeholder achievements as if they were real.

---

# 22. CAREER ARC

The career arc should visually communicate progression.

Possible representation:

```text
ACADEMY
   ↓
RISE
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

Only phases actually present in the source career data should be displayed.

---

# 23. CAREER TIMELINE

The timeline should become one of the strongest visual components.

Important events should stand out.

Suggested hierarchy:

```text
YEAR
│
├── Transfer
│
├── Breakthrough
│
├── Trophy
│
├── Injury / setback
│
├── Major decision
│
└── Career milestone
```

The timeline must remain readable during screen recording.

---

# 24. STORY VIEW

The Story view should feel cinematic.

Use:

* large typography;
* strong act hierarchy;
* beat cards;
* narrative progression;
* restrained animation.

Example:

```text
ACT I
THE BEGINNING

ACT II
THE BREAKTHROUGH

ACT III
THE TEST

ACT IV
THE LEGACY
```

Actual labels must come from Phase 10 data.

Do not invent narrative facts.

---

# 25. SCRIPT VIEW

The script view should be useful for the user's manual content creation workflow.

Display:

```text
TITLE
HOOK
INTRO
ACTS
SEGMENTS
CLIMAX
RESOLUTION
CLOSING
```

Also display metadata such as:

```text
WORD COUNT
ESTIMATED DURATION
DENSITY
TONE
PACING
```

The script should be easily readable while recording or preparing a video.

---

# 26. RECORDING MODE

Recording Mode is one of the most important Phase 15 features.

The objective is to provide a clean composition specifically designed for screen recording.

Default desktop recording target:

```text
1920 × 1080
```

The recording interface should minimize:

* unnecessary navigation;
* browser-like visual clutter;
* excessive UI controls;
* irrelevant metadata.

It should maximize:

* player identity;
* career context;
* important statistics;
* events;
* decisions;
* narrative moments.

---

# 27. RECORDING MODE STATES

Recording Mode should support at least:

```text
NORMAL
RECORDING
```

Normal mode:

```text
full application UI
navigation
controls
```

Recording mode:

```text
cinematic layout
minimal navigation
larger content
stronger visual hierarchy
```

A clear indicator should communicate that Recording Mode is active.

---

# 28. RECORDING MODE NAVIGATION

Recording Mode should not trap the user.

The user must be able to:

* exit recording mode;
* return to normal mode;
* navigate between relevant career views;
* continue the career.

Keyboard shortcuts may be implemented if useful, but are optional.

---

# 29. RECORDING COMPOSITION

The recording layout should preserve a consistent visual frame.

Avoid layouts where content constantly jumps because of different text lengths.

Major elements should occupy predictable areas.

Suggested composition:

```text
┌───────────────────────────────────────────────┐
│ FL                     SEASON       STATUS    │
│                                               │
│ PLAYER                                         │
│ CLUB                                           │
│                                               │
│                  MAIN CONTENT                  │
│                                               │
│                                               │
│ OVR     VALUE     GOALS     TROPHIES          │
│                                               │
└───────────────────────────────────────────────┘
```

Exact composition may vary depending on the active view.

---

# 30. ANIMATION SYSTEM

Phase 15 should introduce restrained motion.

Animation categories:

### Micro interaction

* hover;
* focus;
* button feedback;
* selection.

### State change

* OVR changes;
* statistics changes;
* season changes;
* new event;
* decision state.

### Navigation

* route transition;
* panel entrance;
* panel exit.

### Cinematic

* major event;
* milestone;
* trophy;
* career transition.

Animations should be:

* short;
* deterministic;
* purposeful.

Avoid continuous decorative animations that distract from recording.

---

# 31. REDUCED MOTION

Respect:

```text
prefers-reduced-motion
```

When enabled:

* disable non-essential animations;
* preserve state transitions;
* maintain full functionality.

---

# 32. LOADING STATES

Every asynchronous operation should have a visual loading state.

Examples:

```text
Creating career...
Advancing career...
Loading presentation...
Resolving decision...
```

Avoid freezing the interface without explanation.

---

# 33. ERROR STATES

Errors should be understandable.

Example:

```text
CAREER COULD NOT ADVANCE

Something went wrong while processing
the next career step.

[ TRY AGAIN ]
```

Do not expose raw stack traces to the UI.

---

# 34. EMPTY STATES

Empty states must be intentional.

Examples:

```text
NO TROPHIES YET

The career has not produced any major
honours yet.
```

Do not show broken layouts or empty cards.

---

# 35. SUCCESS FEEDBACK

Important successful operations may display lightweight notifications:

```text
CAREER CREATED
DECISION RESOLVED
SEASON ADVANCED
RECORDING MODE ENABLED
```

Notifications must not obstruct important information.

---

# 36. RESPONSIVE DESIGN

Primary target:

```text
Desktop
1920 × 1080
```

Secondary support:

```text
1366 × 768
1440 × 900
1280 × 720
```

The application should remain functional at smaller desktop sizes.

Mobile optimization is not a primary requirement for Phase 15.

---

# 37. ACCESSIBILITY

Phase 15 must improve baseline accessibility.

Required:

* semantic buttons;
* keyboard navigation;
* visible focus states;
* sufficient text contrast;
* labels for controls;
* meaningful ARIA labels where needed;
* no information conveyed exclusively by color;
* reduced-motion support.

---

# 38. PERFORMANCE

The UI must remain responsive.

Avoid:

* unnecessary polling;
* excessive DOM generation;
* expensive animations;
* unnecessary API requests;
* repeated presentation generation when data has not changed.

Prefer:

* Angular signals where appropriate;
* computed state;
* efficient change detection;
* CSS animations;
* lightweight visualizations.

---

# 39. API USAGE

Existing Phase 14 APIs should be reused.

Do not create redundant endpoints for frontend convenience.

Expected existing endpoints include:

```text
POST /career
GET /career/{id}
POST /career/{id}/advance
POST /career/{id}/decision
POST /career/{id}/pause
GET /career/{id}/events
GET /career/{id}/presentation
```

Only add backend endpoints if the existing API genuinely cannot support a required Phase 15 feature.

---

# 40. STATE MANAGEMENT

The frontend must maintain a clear distinction between:

```text
Career session state
Presentation state
UI state
Recording state
```

Do not mix these responsibilities unnecessarily.

Example:

```text
Career session
    ↓
authoritative simulation state

Presentation
    ↓
derived visual representation

UI
    ↓
navigation / overlays / loading

Recording
    ↓
visual layout state
```

---

# 41. DATA INTEGRITY

The frontend must never fabricate career information.

Every displayed career fact must originate from backend/session/presentation data.

Forbidden:

```text
fake goals
fake trophies
fake transfers
fake statistics
fake career events
fake salary changes
```

Demo/sample data may only be used when explicitly identified as sample/demo data.

---

# 42. DETERMINISM

Phase 15 must not introduce nondeterministic career behavior.

Visual animations may use normal browser animation timing, but they must not affect:

* career state;
* simulation;
* decisions;
* event generation;
* narrative generation;
* presentation data.

No:

```text
Math.random()
Date.now()
random career IDs
```

should be introduced into simulation or presentation state.

---

# 43. SECURITY

The frontend must not introduce:

* `eval`;
* `new Function`;
* unsafe HTML injection;
* arbitrary script execution;
* untrusted HTML rendering.

External HTML should not be trusted.

Use Angular's normal template sanitization mechanisms.

---

# 44. FILE STRUCTURE

Phase 15 should reuse the existing frontend architecture.

Potential additions:

```text
frontend/football-life/src/app/
├── core/
│   ├── models/
│   └── services/
│
└── career/
    ├── career-dashboard/
    ├── career-create/
    ├── career-event/
    ├── career-decision/
    ├── career-notification/
    ├── career-recording-mode/
    │
    ├── career-shell/
    ├── career-profile/
    ├── career-timeline/
    ├── career-clubs/
    ├── career-achievements/
    ├── career-story/
    └── career-script/
```

Only create additional components when they provide clear architectural value.

Do not create dozens of components for trivial markup.

---

# 45. BACKEND FILE BOUNDARY

Avoid unnecessary backend modifications.

If backend changes are required, they must be limited to:

```text
backend/app/api/
backend/app/career/
```

or clearly justified compatibility changes.

Do not alter Phase 8–12 engines simply to support styling.

---

# 46. TESTING

Phase 15 must include frontend tests for:

### Career Dashboard

* renders player information;
* renders current season;
* renders key statistics;
* advance button works;
* loading state works;
* error state works.

### Events

* renders event information;
* respects priority;
* closes correctly.

### Decisions

* renders available options;
* prevents invalid selection;
* resolves correctly;
* handles loading state.

### Recording Mode

* toggles correctly;
* changes recording layout;
* exits correctly;
* does not alter career state.

### Navigation

* all primary career routes load;
* active route state works;
* career context remains available.

---

# 47. VISUAL TESTING

The implementation must include browser-level visual verification.

At minimum verify:

```text
Career Dashboard
Career Profile
Career Timeline
Career Stats
Career Clubs
Career Achievements
Career Story
Career Script
Decision Overlay
Event Overlay
Recording Mode
```

Visual inspection should verify:

* no overflow;
* no broken layout;
* readable typography;
* correct logo;
* correct spacing;
* correct responsive behavior;
* consistent theme;
* no accidental scrollbars where inappropriate.

---

# 48. RECORDING TEST

A dedicated recording-mode verification must be performed at:

```text
1920 × 1080
```

Verify:

* content remains inside viewport;
* no critical controls overlap;
* player information is readable;
* OVR is prominent;
* statistics remain readable;
* event overlays are readable;
* decision overlays are readable;
* navigation does not dominate the frame.

---

# 49. REGRESSION TESTING

All previous tests must continue passing.

Minimum required:

```text
Phase 8 tests
Phase 9 tests
Phase 10 tests
Phase 11 tests
Phase 12 tests
Phase 13 tests
Phase 14 tests
Phase 15 tests
```

Angular tests must also pass.

Production build must pass:

```text
npm run build
```

Backend tests must pass:

```text
PYTHONPATH=backend pytest backend/tests
```

---

# 50. PHASE 15 AUDIT

Before Phase 15 is considered complete, perform a final audit covering:

### Product

* [ ] Application feels cohesive
* [ ] Navigation is coherent
* [ ] Visual hierarchy is clear
* [ ] Prototype-like UI elements removed

### UX

* [ ] Loading states
* [ ] Error states
* [ ] Empty states
* [ ] Success feedback
* [ ] Decision UX
* [ ] Event UX

### Visual

* [ ] Logo
* [ ] Typography
* [ ] Design tokens
* [ ] Spacing
* [ ] Animations
* [ ] Responsive layout

### Recording

* [ ] 1920×1080 layout
* [ ] Minimal recording chrome
* [ ] Readable statistics
* [ ] Readable events
* [ ] Readable decisions
* [ ] Clean transitions

### Integrity

* [ ] No fabricated data
* [ ] No simulation changes
* [ ] Phase boundaries preserved
* [ ] Deterministic backend behavior preserved

### Security

* [ ] No eval
* [ ] No exec
* [ ] No unsafe HTML
* [ ] No external untrusted execution

### Tests

* [ ] Backend tests pass
* [ ] Frontend tests pass
* [ ] Production build passes
* [ ] Browser verification passes
* [ ] Recording-mode verification passes

---

# 51. ACCEPTANCE CRITERIA

Phase 15 is complete only if all of the following are true:

1. The application has a consistent Football Life visual identity.

2. The existing Phase 13 and Phase 14 screens feel like parts of the same product.

3. Career progression provides clear visual feedback.

4. Events and decisions have meaningful visual presentation.

5. Loading, error and empty states are handled gracefully.

6. The application is usable at 1920×1080.

7. Recording Mode provides a clean composition for manual screen recording.

8. Recording Mode does not modify career simulation behavior.

9. No career facts are fabricated by the frontend.

10. Existing Phase 8–14 behavior remains intact.

11. No automatic video generation is introduced.

12. No unnecessary backend architecture is introduced.

13. Accessibility is improved.

14. All automated tests pass.

15. Production Angular build passes.

16. Browser visual verification passes.

17. Recording-mode verification passes.

18. The resulting application feels like a **finished football career experience rather than a technical prototype**.

---

# 52. NON-GOALS

The following are explicitly outside Phase 15:

```text
Automatic TikTok generation
Automatic video editing
AI-generated video
AI voice generation
Text-to-speech
Social media publishing
Online accounts
Cloud infrastructure
Multiplayer
Authentication
New simulation systems
New event probability systems
New narrative generation systems
New career mechanics
```

If a feature requires any of these systems, it belongs to a future phase.

---

# 53. EXPECTED USER EXPERIENCE

The final Phase 15 experience should feel approximately like:

```text
OPEN FOOTBALL LIFE
        ↓
SEE PLAYER
        ↓
START / CONTINUE CAREER
        ↓
ADVANCE
        ↓
VISUAL FEEDBACK
        ↓
EVENT
        ↓
DECISION
        ↓
CONSEQUENCE
        ↓
PLAYER EVOLVES
        ↓
CAREER HISTORY GROWS
        ↓
OPEN STORY / TIMELINE / STATS
        ↓
RECORDING MODE
        ↓
CAPTURE THE MOMENT
```

The user should not need to understand the internal architecture.

The simulation should simply feel alive.

---

# 54. DESIGN PHILOSOPHY

The central principle of Phase 15 is:

> **Make the existing system feel good.**

Do not add complexity for the sake of complexity.

Football Life already has:

* simulation;
* events;
* decisions;
* career history;
* narrative;
* scripts;
* presentation;
* interactive career sessions.

Phase 15 exists to connect these pieces into a polished experience.

---

# 55. FINAL DEFINITION OF DONE

Phase 15 is considered complete when:

```text
Football Life launches
        ↓
User creates a career
        ↓
User advances the career
        ↓
Events appear naturally
        ↓
Decisions are visually clear
        ↓
Player state evolves
        ↓
Career presentation updates
        ↓
All views feel visually connected
        ↓
Recording Mode can be activated
        ↓
The entire experience can be comfortably
captured at 1920×1080
```

without:

* broken layouts;
* inconsistent visual styles;
* fabricated information;
* unnecessary backend complexity;
* simulation regressions;
* blocking UI issues.

---

# 56. FINAL PHASE 15 TARGET

The final product should no longer feel like:

> "a football simulation project with a frontend."

It should feel like:

> **"Football Life — a cinematic interactive football career simulator."**

The user should be able to sit in front of the application, run a career, watch the player's story develop, and record the most interesting moments without needing the application to produce the final video itself.
