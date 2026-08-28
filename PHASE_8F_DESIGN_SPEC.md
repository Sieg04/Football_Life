# FOOTBALL LIFE

## Phase 8F — Event Decision & Choice Engine

**Project:** Football Life
**Phase:** 8F
**Status:** Design Specification
**Version:** 1.0
**Primary implementation target:** `backend/app/event/`
**Depends on:** Phase 8A, 8B, 8C, 8D, 8E
**Next phase:** Phase 9 — Narrative Engine

---

# 1. PURPOSE

Phase 8F introduces the **Event Decision & Choice Engine**.

Its responsibility is to represent and resolve explicit choices associated with events.

The engine answers:

> **"When an event presents one or more choices, which choice is selected, and why?"**

8F does **not** apply the consequences of the selected choice.

That responsibility remains with Phase 8E.

The intended flow is:

```text
Event
  ↓
Conditions
  ↓
Probability
  ↓
Resolution
  ↓
Decision / Choice
  ↓
Selected Option
  ↓
Effect Application
  ↓
State
```

---

# 2. RELATIONSHIP WITH PREVIOUS PHASES

Phase 8 is composed of:

```text
8A — Event Domain
8B — Candidate Generation
8C — Conditions & Probability
8D — Resolution
8E — Effect & State Application
8F — Decision & Choice
```

The responsibilities are intentionally separated.

## 8A

Defines event structures.

## 8B

Generates event candidates.

## 8C

Determines eligibility and probability.

## 8D

Resolves whether/how an event occurs.

## 8E

Applies state effects.

## 8F

Represents and resolves explicit decisions.

---

# 3. ARCHITECTURAL PRINCIPLE

The central invariant is:

```text
8F selects.
8E applies.
```

8F must never directly mutate simulation state.

Example:

```text
Decision:
    Accept transfer

8F:
    selected_option = ACCEPT

8E:
    applies ACCEPT effects
```

This separation is mandatory.

---

# 4. NON-GOALS

Phase 8F must NOT implement:

* narrative generation;
* story beats;
* career arcs;
* legacy calculation;
* timeline generation;
* prose generation;
* transfer simulation;
* match simulation;
* injury simulation;
* competition logic;
* condition evaluation;
* probability calculation;
* state mutation;
* persistence;
* API endpoints;
* Angular UI;
* community voting;
* TikTok integration;
* LLM integration.

These belong to other phases or future systems.

---

# 5. CORE CONCEPT

A decision consists of:

```text
Decision
├── identity
├── prompt
├── options
└── resolution policy
```

Each option consists of:

```text
DecisionOption
├── identity
├── label
├── description
├── availability
└── effect reference
```

The selected option is represented separately:

```text
DecisionResult
├── decision
├── selected option
└── resolution metadata
```

The exact field names may be adapted to the existing repository conventions.

---

# 6. DOMAIN OBJECTS

The initial implementation should introduce the minimum necessary domain abstractions.

Recommended conceptual objects:

```text
Decision
DecisionOption
DecisionResult
DecisionResolution
DecisionResolutionType
DecisionError
```

Optional objects may be introduced only when genuinely necessary.

Do not create abstractions merely because they are listed here if an existing repository model already provides the required functionality.

---

# 7. DECISION

A `Decision` represents a choice presented by an event.

Conceptually:

```python
Decision(
    id="transfer_offer",
    prompt="The player receives a transfer offer. What should he do?",
    options=[...],
)
```

A decision must contain at least:

```text
id
options
```

A human-readable prompt is recommended.

The decision object should be immutable if consistent with the existing event-domain architecture.

---

# 8. DECISION OPTION

Each `DecisionOption` represents one possible choice.

Conceptually:

```text
DecisionOption
├── id
├── label
├── description
└── effect reference
```

Example:

```text
id:
ACCEPT

label:
Accept the transfer

description:
Move to the new club.

effects:
[...]
```

The option itself does not apply its effects.

---

# 9. OPTION IDENTITY

Option IDs must be:

* deterministic;
* stable;
* unique within a decision;
* suitable for serialization.

Example:

```text
ACCEPT
REJECT
WAIT
```

Duplicate option IDs within the same decision must be rejected.

---

# 10. OPTION ORDER

Options must preserve explicit deterministic ordering.

Example:

```text
[
    ACCEPT,
    REJECT,
    WAIT
]
```

must remain in that order.

Do not derive option order from:

* sets;
* hash ordering;
* dictionary iteration assumptions;
* object identity.

Option ordering may later matter for UI presentation and deterministic replay.

---

# 11. OPTION AVAILABILITY

An option may be unavailable depending on the current event context.

However:

> 8F must not create a second condition engine.

If the repository already provides a condition system from Phase 8C, reuse it where appropriate.

Conceptually:

```text
Decision
   ↓
Options
   ├── ACCEPT → available
   ├── REJECT → available
   └── WAIT   → unavailable
```

Unavailable options must not be selectable.

---

# 12. AVAILABILITY SEMANTICS

If an option is unavailable:

```text
option.available = false
```

it must not be returned as the selected option.

If all options are unavailable, the decision must fail explicitly.

Do not silently choose the first option.

Do not randomly select an unavailable option.

---

# 13. DECISION RESOLUTION MODES

8F should support explicit deterministic resolution policies.

The initial architecture should be designed around at least:

```text
EXPLICIT
WEIGHTED
DEFAULT
```

These modes have different purposes.

---

# 14. EXPLICIT RESOLUTION

`EXPLICIT` means an external caller supplies the selected option.

Example:

```text
Decision:
    ACCEPT
    REJECT
    WAIT

Input:
    REJECT
```

Result:

```text
selected_option = REJECT
```

This is the preferred mode for:

* future UI decisions;
* user-controlled careers;
* community decisions;
* externally supplied choices.

No randomness is required.

---

# 15. EXPLICIT VALIDATION

If the caller selects:

```text
ACCEPT
```

but `ACCEPT` does not exist:

```text
INVALID_OPTION
```

must be returned.

If the option exists but is unavailable:

```text
OPTION_UNAVAILABLE
```

must be returned.

Never silently substitute another option.

---

# 16. WEIGHTED RESOLUTION

`WEIGHTED` allows the simulation to resolve a decision autonomously.

Each available option may have a deterministic weight.

Example:

```text
ACCEPT = 0.60
REJECT = 0.30
WAIT   = 0.10
```

The engine may use the project's deterministic RNG mechanism to select an option according to those weights.

This is the primary mechanism for decisions that should be simulated without direct user input.

---

# 17. WEIGHT VALIDATION

Weights must satisfy:

```text
weight >= 0
```

Invalid values include:

```text
negative
NaN
Infinity
```

An option with zero weight is valid but cannot be selected while positive-weight options exist.

If all available options have zero weight:

```text
NO_SELECTABLE_OPTION
```

must be returned.

---

# 18. WEIGHT NORMALIZATION

Weights may be provided as arbitrary non-negative values.

For example:

```text
ACCEPT = 60
REJECT = 30
WAIT = 10
```

is semantically equivalent to:

```text
0.60
0.30
0.10
```

The engine may normalize weights internally.

The resulting selection probability must be:

```text
weight_i / sum(weights)
```

No hidden weighting should be introduced.

---

# 19. RANDOMNESS BOUNDARY

Unlike Phase 8E, 8F may use deterministic randomness for autonomous weighted decisions.

However:

> Randomness must come exclusively from the project's established deterministic RNG/seed architecture.

Do not use uncontrolled:

```python
random.random()
```

if the repository already provides a simulation RNG.

Do not use:

```python
hash(...)
```

for seed generation.

Do not use timestamps.

Do not use process identity.

---

# 20. DETERMINISTIC WEIGHTED DECISIONS

Given:

```text
same decision
+
same available options
+
same weights
+
same RNG seed/context
```

the selected option must always be identical.

Example:

```text
seed = 12345
decision = transfer_decision
```

must always produce the same result.

This is essential for replayable careers.

---

# 21. DEFAULT RESOLUTION

`DEFAULT` represents a deterministic fallback option.

Example:

```text
default_option = REJECT
```

If no explicit user choice exists and the decision is configured for default resolution:

```text
selected_option = REJECT
```

The default option must:

* exist;
* be available;
* be valid.

Otherwise the decision fails explicitly.

Do not silently choose another option.

---

# 22. DECISION RESOLUTION PRIORITY

When multiple mechanisms are available, the resolution policy must be explicit.

Recommended priority:

```text
EXPLICIT
    ↓
DEFAULT
    ↓
WEIGHTED
```

However, the implementation must not silently combine policies.

A `Decision` should specify its intended resolution mode.

---

# 23. NO IMPLICIT PLAYER PSYCHOLOGY

8F must not automatically infer choices from:

* personality;
* ambition;
* loyalty;
* morale;
* reputation;
* club prestige;
* age;
* potential.

Those systems may eventually influence decision weights, but they must do so through explicit data supplied to the decision resolver.

Do not hardcode hidden football psychology into 8F.

---

# 24. FUTURE PERSONALITY INTEGRATION

The architecture should permit future systems to calculate weights such as:

```text
Ambitious player:
    ACCEPT big-club offer = higher weight

Loyal player:
    STAY = higher weight

Risk-averse player:
    REJECT uncertain move = higher weight
```

But Phase 8F itself should only consume the resulting weights.

Conceptually:

```text
Future Personality System
          ↓
Decision weights
          ↓
8F
          ↓
Selected option
```

---

# 25. DECISION RESULT

A successful decision resolution should return structured information.

Conceptually:

```text
DecisionResult
├── success
├── decision_id
├── selected_option
├── resolution_type
└── metadata
```

Recommended metadata:

```text
seed
weight
probability
available_options
```

Only include information that is useful and compatible with the existing architecture.

---

# 26. NO STATE MUTATION

The following must NOT happen inside 8F:

```text
player.confidence += 2
player.club = new_club
player.morale = 80
```

Instead:

```text
8F
 ↓
DecisionResult
 ↓
8E
 ↓
State transition
```

This is one of the most important architectural boundaries in Phase 8.

---

# 27. EFFECT REFERENCES

Decision options should be able to identify their associated consequences.

Conceptually:

```text
DecisionOption
    ↓
effect set
```

Example:

```text
ACCEPT
    ↓
effects:
    transfer-related effects

REJECT
    ↓
effects:
    confidence +1
```

8F must not execute those effects.

It only identifies the selected option and its associated effect definition/reference.

---

# 28. 8F → 8E INTEGRATION

The intended pipeline is:

```text
8D
 ↓
resolved event
 ↓
8F
 ↓
selected decision option
 ↓
8E
 ↓
effect application
```

Example:

```text
Event:
"Club X offers the player a transfer."

Decision:
    ACCEPT
    REJECT

8F:
    ACCEPT selected

8E:
    applies ACCEPT effects
```

8F should expose enough structured information for 8E to consume the selected effect set.

---

# 29. MULTIPLE DECISIONS

An event may theoretically contain multiple decisions.

Example:

```text
Event
 ├── Decision 1
 │     ├── ACCEPT
 │     └── REJECT
 │
 └── Decision 2
       ├── SIGN
       └── DECLINE
```

If supported by the existing event architecture, decisions must be resolved in deterministic order.

Do not introduce multi-decision orchestration unless the repository actually requires it.

The initial implementation may support one decision per event if that is sufficient.

---

# 30. DECISION DEPENDENCIES

Phase 8F should not introduce a complex decision-tree system in the initial implementation.

Do not implement:

```text
decision trees
nested decision graphs
recursive branching narratives
```

unless already required by the existing event domain.

Keep the initial system flat:

```text
Decision
    ↓
Options
    ↓
One selected option
```

Future phases can extend this architecture.

---

# 31. INVALID DECISION

A decision must fail explicitly if:

* it contains no options;
* options have duplicate IDs;
* an option is malformed;
* an explicit option ID does not exist;
* an explicit option is unavailable;
* a default option does not exist;
* a default option is unavailable;
* weighted resolution has invalid weights;
* all selectable weights are zero;
* the resolution mode is unsupported.

Do not silently recover.

---

# 32. ERROR CODES

Recommended conceptual errors:

```text
INVALID_DECISION
INVALID_OPTION
DUPLICATE_OPTION
OPTION_UNAVAILABLE
NO_OPTIONS
NO_SELECTABLE_OPTION
INVALID_WEIGHT
INVALID_RESOLUTION_TYPE
INVALID_DEFAULT_OPTION
```

Adapt names to existing project conventions.

---

# 33. TYPE SAFETY

Decision IDs, option IDs, weights and resolution types must be validated.

Examples:

```text
option_id must be a valid identifier/string type
weight must be numeric
weight must be finite
resolution type must be recognized
```

Do not silently coerce arbitrary values.

---

# 34. IMMUTABILITY

Decision objects and option objects should follow the existing event-domain immutability conventions.

Resolving a decision must not mutate:

```text
Decision
DecisionOption
available option collections
input context
```

The result should be a new immutable domain result where appropriate.

---

# 35. SERIALIZATION

The new decision-domain objects must serialize consistently with the existing event domain.

Verify:

```text
Decision
DecisionOption
DecisionResult
DecisionResolutionType
DecisionError
```

including nested options.

Enum serialization must follow existing project conventions.

Do not introduce a second serialization system.

---

# 36. AUDITABILITY

A decision result should provide enough structured information to reconstruct what happened.

At minimum:

```text
decision_id
selected_option
resolution_type
```

For weighted decisions, preferably:

```text
weights
normalized probabilities
seed/context identifier
```

This is important for future timeline and narrative systems.

Phase 9 will eventually need to understand significant career decisions without requiring access to internal 8F implementation details.

---

# 37. NARRATIVE BOUNDARY

8F does not generate narrative.

It may produce structured metadata such as:

```text
decision_id
selected_option
```

but must not produce:

```text
"He bravely rejected the offer..."
```

That interpretation belongs to Phase 9.

---

# 38. PERSISTENCE BOUNDARY

8F must not directly access:

```text
SQLAlchemy
SQLite
Alembic
database sessions
```

Decision results are domain objects.

Persistence may later store them through an external application layer.

---

# 39. API BOUNDARY

Do not create FastAPI endpoints for 8F.

The engine must remain callable directly from the simulation domain.

---

# 40. UI BOUNDARY

Do not implement Angular UI.

8F should expose structured data that a future UI can consume.

Potential future representation:

```text
What should the player do?

[ Accept ]
[ Reject ]
[ Wait ]
```

But the actual UI belongs to a later phase.

---

# 41. COMMUNITY DECISION COMPATIBILITY

The architecture should allow a future external system to supply:

```text
selected_option = ACCEPT
```

without changing 8F.

For example:

```text
TikTok/community system
        ↓
ACCEPT
        ↓
8F explicit resolution
        ↓
DecisionResult
        ↓
8E
```

Do not implement community integration now.

---

# 42. DETERMINISTIC REPLAY

The same career seed and decision context should produce the same autonomous decision.

For example:

```text
Career Seed:
12345

Decision:
TRANSFER_OFFER_001

Weights:
ACCEPT = 60
REJECT = 30
WAIT = 10
```

must produce the same selected option during replay.

---

# 43. WEIGHTED SELECTION ALGORITHM

If weighted selection is implemented, use a standard cumulative-weight selection.

Conceptually:

```text
total = sum(weights)

draw = deterministic_rng()

cursor = 0

for option in ordered_options:
    cursor += option.weight / total

    if draw < cursor:
        return option
```

The exact RNG mechanism must follow the existing repository architecture.

Do not implement a custom pseudo-random algorithm unnecessarily.

---

# 44. EDGE CASES

Test at minimum:

```text
one option
two options
many options
all options unavailable
one available option
zero-weight options
all zero weights
negative weights
NaN weights
Infinity weights
duplicate option IDs
missing option
invalid explicit selection
unavailable explicit selection
valid default
invalid default
weighted deterministic selection
```

---

# 45. SINGLE OPTION

A decision with exactly one available option should resolve deterministically.

Example:

```text
ACCEPT
```

Result:

```text
ACCEPT
```

No random draw is necessary.

This avoids unnecessary randomness.

---

# 46. ALL BUT ONE UNAVAILABLE

Example:

```text
ACCEPT → unavailable
REJECT → unavailable
WAIT   → available
```

Result:

```text
WAIT
```

This should be deterministic regardless of weighted selection.

---

# 47. EXPLICIT SELECTION OVERRIDES WEIGHTS

If resolution mode is `EXPLICIT`:

```text
weights do not determine the selection
```

The supplied option must be validated and returned.

Do not perform an unnecessary random draw.

---

# 48. DEFAULT SELECTION

If resolution mode is `DEFAULT`:

```text
default_option
```

must be selected deterministically.

Do not use randomness.

---

# 49. WEIGHTED SELECTION AND FLOAT PRECISION

Floating-point weights must be handled safely.

Do not allow floating-point edge cases to cause:

```text
no option selected
multiple options selected
```

The implementation should guarantee that a valid positive total produces exactly one selected option.

---

# 50. ZERO-WEIGHT OPTIONS

Zero-weight options:

```text
weight = 0
```

remain valid but cannot be selected while positive-weight options exist.

If every available option has zero weight:

```text
NO_SELECTABLE_OPTION
```

must be returned.

---

# 51. NEGATIVE WEIGHTS

Negative weights are invalid.

Example:

```text
ACCEPT = -10
```

must fail validation.

Do not clamp negative values to zero silently.

---

# 52. NaN / INFINITY

Reject:

```text
NaN
Infinity
-Infinity
```

for all numeric decision weights.

This follows the project's deterministic simulation requirements.

---

# 53. OPTION LABELS

Human-readable labels should remain presentation data.

The engine must select by stable option ID, not by label.

For example:

```text
id:
ACCEPT

label:
Accept the offer
```

Selection should use:

```text
ACCEPT
```

not:

```text
"Accept the offer"
```

This avoids localization and wording problems.

---

# 54. OPTION DESCRIPTIONS

Descriptions are informational.

They must not contain executable logic.

Forbidden:

```text
description = "if player.overall > 80 then..."
```

Decision logic must remain structured data.

---

# 55. NO EXECUTABLE DECISION EXPRESSIONS

Never evaluate arbitrary strings using:

```python
eval(...)
exec(...)
compile(...)
```

Decision definitions must remain declarative.

---

# 56. TESTING REQUIREMENTS

Create dedicated Phase 8F tests following existing repository conventions.

Minimum test groups:

## Domain construction

* valid decision;
* valid options;
* invalid empty decision;
* duplicate IDs;
* malformed options.

## Explicit resolution

* valid selection;
* invalid selection;
* unavailable selection.

## Default resolution

* valid default;
* invalid default;
* unavailable default.

## Weighted resolution

* deterministic selection;
* zero weights;
* negative weights;
* NaN;
* Infinity;
* one available option;
* all unavailable;
* mixed available/unavailable options.

## Ordering

Verify that option ordering is preserved.

## Immutability

Verify that resolving a decision does not mutate the decision or options.

## Serialization

Verify serialization of the decision domain.

## Integration

Verify:

```text
8F selected option
        ↓
8E consumes corresponding effect set
```

without moving state mutation into 8F.

---

# 57. DETERMINISM TESTING

Determinism must be tested seriously.

At minimum:

```text
same seed
+
same decision
+
same weights
=
same result
```

repeated many times.

Also test cross-process determinism if the repository's deterministic infrastructure supports it.

Do not rely solely on a single successful execution.

---

# 58. REGRESSION REQUIREMENTS

After implementation:

```text
Phase 8F tests
+
Phase 8E tests
+
Phase 8D tests
+
Phase 8C tests
+
full test suite
```

must pass.

No regression should be introduced into earlier phases.

---

# 59. PERFORMANCE

8F should remain lightweight.

A normal decision should require:

```text
O(n)
```

where `n` is the number of options.

Do not introduce:

* database queries;
* network calls;
* expensive graph traversal;
* unnecessary serialization;
* external services.

---

# 60. FILE SCOPE

Expected implementation area:

```text
backend/app/event/
```

Potential implementation:

```text
decisions.py
```

Potential tests:

```text
backend/tests/
```

Adapt exact paths to existing project conventions.

Do not create unnecessary directories.

---

# 61. CHANGE SCOPE

Allowed:

```text
new 8F domain models
new 8F decision resolver
8F tests
minimal integration with existing event structures
minimal exports
```

Not allowed:

```text
frontend changes
database migrations
API endpoints
Narrative Engine
community integration
TikTok integration
LLM integration
transfer implementation
match implementation
8C redesign
8D redesign
8E redesign
unrelated refactoring
```

---

# 62. COMPATIBILITY WITH PHASE 8E

The implementation must preserve the architectural relationship:

```text
8F → selects effect set
8E → applies effect set
```

Do not duplicate `apply_effect()` or `apply_effects()` inside 8F.

Reuse Phase 8E primitives where appropriate.

---

# 63. COMPATIBILITY WITH PHASE 8C

If option availability depends on conditions:

```text
8C condition engine
        ↓
option availability
        ↓
8F resolution
```

Do not create duplicate condition evaluation logic.

---

# 64. COMPATIBILITY WITH PHASE 8D

8F must consume the resolved event context produced by 8D.

It must not:

* resolve the event again;
* recalculate probability;
* reroll the event;
* modify event outcome.

---

# 65. EXAMPLE — TRANSFER DECISION

Event:

```text
Player receives an offer from a stronger club.
```

Decision:

```text
TRANSFER_DECISION
```

Options:

```text
ACCEPT
REJECT
```

Weights:

```text
ACCEPT = 70
REJECT = 30
```

8F:

```text
seed = 12345

→ selected_option = ACCEPT
```

8F result:

```text
DecisionResult(
    decision_id="TRANSFER_DECISION",
    selected_option="ACCEPT",
    resolution_type="WEIGHTED"
)
```

Then:

```text
DecisionResult
      ↓
8E
      ↓
ACCEPT effects
```

8F itself does NOT transfer the player.

---

# 66. EXAMPLE — USER DECISION

Decision:

```text
Should the player accept the offer?
```

Options:

```text
ACCEPT
REJECT
```

External input:

```text
ACCEPT
```

8F:

```text
resolve_explicit("ACCEPT")
```

Result:

```text
selected_option = ACCEPT
```

No randomness.

No state mutation.

---

# 67. EXAMPLE — DEFAULT

Decision:

```text
Player is unable to make a choice.
```

Default:

```text
REJECT
```

8F:

```text
resolution_type = DEFAULT
selected_option = REJECT
```

No randomness.

---

# 68. EVENT WITHOUT DECISION

Not every event requires a decision.

Example:

```text
Player suffers an unexpected minor setback.
```

If no decision exists:

```text
8F is not invoked.
```

The event continues through the normal 8D → 8E flow.

Do not force every event to have a decision.

---

# 69. NON-DECISION EVENT

A decision must never be fabricated simply because 8F exists.

The system must support:

```text
Event
 ├── no decision
 └── effects
```

as well as:

```text
Event
 ├── decision
 └── decision-dependent effects
```

---

# 70. DECISION EVENT FLOW

For events containing a decision:

```text
Event
  ↓
8C
  ↓
8D
  ↓
Decision available?
  │
  ├── NO → 8E
  │
  └── YES
        ↓
       8F
        ↓
   Selected Option
        ↓
       8E
```

---

# 71. DECISION AUDIT TRAIL

The final structured event result should eventually allow future systems to identify:

```text
event occurred
decision was presented
option selected
effects applied
```

This creates the foundation for future narrative interpretation.

Example future Phase 9 input:

```text
Event:
TRANSFER_OFFER

Decision:
ACCEPT

Result:
PLAYER_MOVED_TO_CLUB_X
```

Phase 9 can later interpret that as a career event.

8F itself must not perform that interpretation.

---

# 72. FUTURE EXTENSIBILITY

The architecture should permit future resolution policies such as:

```text
PLAYER
COMMUNITY
PERSONALITY
AI
SCRIPTED
```

but these should NOT be implemented now unless required.

The important design principle is:

```text
resolution policy
        ↓
selected option
```

rather than hardcoding one source of decisions.

---

# 73. NO AI REQUIRED

8F must remain fully functional without an LLM.

The project explicitly treats LLM integration as optional/future infrastructure.

Decision resolution must be deterministic using structured rules.

---

# 74. FINAL ACCEPTANCE CRITERIA

Phase 8F is complete only when:

```text
[ ] Decision domain exists
[ ] DecisionOption domain exists
[ ] DecisionResult exists
[ ] Resolution type exists
[ ] Explicit resolution works
[ ] Default resolution works
[ ] Weighted resolution works
[ ] Invalid options fail explicitly
[ ] Unavailable options cannot be selected
[ ] Duplicate option IDs fail
[ ] Invalid weights fail
[ ] NaN/Infinity fail
[ ] Zero-weight behavior is correct
[ ] All-zero weights fail explicitly
[ ] Option ordering is deterministic
[ ] No state mutation occurs in 8F
[ ] 8F → 8E integration works
[ ] 8F does not duplicate 8E
[ ] 8F does not duplicate 8C
[ ] 8F does not duplicate 8D
[ ] Serialization works
[ ] Deterministic replay works
[ ] Cross-process determinism verified where applicable
[ ] Dedicated tests pass
[ ] 8C regression passes
[ ] 8D regression passes
[ ] 8E regression passes
[ ] Full suite passes
[ ] No unrelated changes
```

---

# 75. DEFINITION OF DONE

Phase 8F is considered complete when:

```text
Code exists
+
Tests exist
+
Decision resolution works
+
Invalid decisions fail safely
+
State remains untouched
+
8E applies selected consequences
+
8C/8D/8E behavior remains unchanged
+
Deterministic replay works
+
Full regression suite passes
```

---

# 76. PHASE 8 COMPLETE ARCHITECTURE

After Phase 8F:

```text
                    EVENT ENGINE
                         │
                         ▼
                 ┌───────────────┐
                 │ Event Domain  │
                 └───────┬───────┘
                         │
                         ▼
                 ┌───────────────┐
                 │ 8B Candidate  │
                 │  Generation   │
                 └───────┬───────┘
                         │
                         ▼
                 ┌───────────────┐
                 │ 8C Conditions │
                 │ + Probability│
                 └───────┬───────┘
                         │
                         ▼
                 ┌───────────────┐
                 │  8D Resolution│
                 └───────┬───────┘
                         │
                         ▼
                 ┌───────────────┐
                 │ 8F Decision   │
                 │ & Choice      │
                 └───────┬───────┘
                         │
                         ▼
                 ┌───────────────┐
                 │ 8E Effects    │
                 │ & State Apply │
                 └───────┬───────┘
                         │
                         ▼
                  Simulation State
                         │
                         ▼
                 ┌───────────────┐
                 │ Phase 9       │
                 │ Narrative     │
                 └───────────────┘
```

Note that 8F and 8E are logically adjacent but have different responsibilities:

```text
8F = WHAT IS CHOSEN?
8E = WHAT HAPPENS BECAUSE OF IT?
```

---

# 77. FINAL DESIGN PRINCIPLE

The Event Engine must remain composable.

A decision should be representable as:

```text
Event
    ↓
Decision
    ↓
Option
    ↓
Effect Set
```

without embedding state mutation, narrative interpretation, persistence, or UI concerns into the decision system.

The final Phase 8 architecture should therefore allow Football Life to represent:

```text
automatic event
        +
automatic consequences
```

as well as:

```text
event
  +
player/community decision
  +
decision-dependent consequences
```

using the same underlying domain architecture.

---

# 78. NEXT PHASE

After Phase 8F is implemented, audited and frozen:

```text
PHASE 8
========
8A ✅
8B ✅
8C ✅
8D ✅
8E ✅
8F → Decision & Choice Engine
```

The next major system is:

```text
PHASE 9 — NARRATIVE ENGINE
```

Phase 9 will consume structured simulation history, important events, decisions, effects, achievements and career milestones to construct:

```text
timeline
story beats
career arcs
legacy
narrative significance
story output
```

Phase 8F must therefore expose structured, deterministic information suitable for future consumption by Phase 9, without implementing any narrative functionality itself.
