Vamos. Voy a cerrar ahora el **Phase 8E Design Spec** como documento de implementación, pero antes hago una precisión importante: el `PROJECT_SPEC_v1.6.md` que tenemos en Library deja Phase 8 a nivel conceptual —eventos, condiciones, probabilidades, efectos y decisiones—, mientras que el desglose concreto 8C/8D/8E procede del trabajo que hemos ido realizando. 

Por tanto, el documento siguiente será el **contrato técnico de 8E**, no una modificación retroactiva del spec general.

# PHASE 8E — EVENT EFFECT & STATE APPLICATION ENGINE

**Project:** Football Life
**Phase:** 8E
**Status:** Design Specification
**Purpose:** Implementation contract for Jules
**Architecture:** Pure deterministic simulation domain

---

## 1. Phase Objective

Phase 8E introduces the **Event Effect & State Application Engine**.

Its responsibility is to take a successfully resolved event from Phase 8D and transform its declared effects into **validated, deterministic state changes**.

Core flow:

```text
Event
  ↓
8C — Conditions & Probability
  ↓
8D — Resolution
  ↓
8E — Effects
  ↓
State Changes
```

8E answers:

> **"Given that this event outcome occurred, what changes does it produce in the simulation state?"**

It does **not** decide whether the event occurs.

---

# 2. Architectural Boundary

The responsibilities of Phase 8 must remain strictly separated.

```text
8A
Event Definition
      ↓
8B
Candidate Generation
      ↓
8C
Condition + Probability
      ↓
8D
Resolution
      ↓
8E
Effect Application
```

### 8C owns

```text
eligibility
conditions
probability
probability modifiers
```

### 8D owns

```text
resolution
outcome selection
success/failure
resolved event result
```

### 8E owns

```text
effect interpretation
target resolution
value validation
state modification
application result
```

This separation follows the project's broader principle that engines should remain independent and deterministic rather than mixing responsibilities. 

---

# 3. Non-Goals

Phase 8E must **not** implement:

* condition evaluation;
* probability calculation;
* candidate generation;
* outcome selection;
* narrative generation;
* story beats;
* transfer logic;
* injury simulation;
* match simulation;
* competition logic;
* database persistence;
* API endpoints;
* Angular UI;
* random event selection.

It must not duplicate functionality already implemented in 8C or 8D.

---

# 4. Core Domain Objects

8E should introduce the minimum necessary domain objects.

Recommended:

```text
EventEffect
EffectOperation
EffectTarget
EffectApplication
EffectApplicationResult
EffectApplicationError
```

Optional:

```text
EffectContext
EffectBatchResult
```

Only introduce additional objects when the existing repository architecture requires them.

---

# 5. EffectOperation

The initial supported operations are:

```text
ADD
SET
MULTIPLY
```

### ADD

```text
new_value = current_value + value
```

Example:

```text
confidence 60
ADD 5
→ 65
```

### SET

```text
new_value = value
```

Example:

```text
morale 60
SET 80
→ 80
```

### MULTIPLY

```text
new_value = current_value × value
```

Example:

```text
form 50
MULTIPLY 1.10
→ 55
```

Values must be validated before application.

---

# 6. EffectTarget

Every effect must identify:

```text
scope
attribute
```

Conceptually:

```python
EffectTarget(
    scope="player",
    attribute="confidence"
)
```

Possible scopes depend on the existing state model.

Examples:

```text
player
career
club
team
```

**Jules must inspect the repository before introducing targets.**

8E must never silently create a target that does not exist in the domain.

---

# 7. Effect Value

The initial implementation should support deterministic explicit values.

Examples:

```text
+2
-1
+5
1.10
80
```

The system must distinguish between:

```text
integer
float
boolean
string
enum
```

where applicable.

No arbitrary Python expressions are allowed.

For example, this is forbidden:

```text
value = "player.current_ability * 0.1"
```

Effects are declarative, not executable code.

---

# 8. EventEffect

Conceptually:

```text
EventEffect
├── target
├── operation
└── value
```

Example:

```json
{
  "target": "player.confidence",
  "operation": "ADD",
  "value": 2
}
```

Multiple effects are supported.

Example:

```json
[
  {
    "target": "player.confidence",
    "operation": "ADD",
    "value": 2
  },
  {
    "target": "player.form",
    "operation": "ADD",
    "value": 1
  }
]
```

---

# 9. Effect Ordering

Effects are applied in deterministic order.

Given:

```text
[A, B, C]
```

application must always be:

```text
A
↓
B
↓
C
```

Order must not depend on:

* hash ordering;
* sets;
* unordered collections;
* process state;
* random selection.

This is essential because the project requires reproducible simulation results. 

---

# 10. Sequential Semantics

Effects are sequential.

Example:

```text
confidence = 60

ADD 5
SET 20
ADD 3
```

Result:

```text
60
↓
65
↓
20
↓
23
```

Final value:

```text
23
```

The engine must record each application.

---

# 11. EffectApplication

Each applied effect should produce a structured record containing, at minimum:

```text
target
operation
requested_value
previous_value
resulting_value
applied
```

Recommended additional metadata:

```text
event_id
effect_index
```

Example:

```text
target:
    player.confidence

operation:
    ADD

requested_value:
    2

previous_value:
    61

resulting_value:
    63

applied:
    true
```

This provides an audit trail without generating narrative.

---

# 12. EffectApplicationResult

The complete result should expose enough information to understand what happened.

Conceptually:

```text
EffectApplicationResult
├── success
├── applications
├── skipped_effects
├── errors
└── resulting_state
```

Example:

```text
success = true

applications:
    confidence: 61 → 63
    form:       50 → 51

errors:
    none
```

---

# 13. Immutability

The input state must not be silently mutated.

Preferred semantics:

```text
input state
     ↓
8E
     ↓
new resulting state
```

rather than:

```text
input state
     ↓
mutate in place
```

This is consistent with the existing project's preference for pure/immutable domain operations where appropriate; for example, the Competition Engine explicitly requires standings/form operations not to mutate their inputs. 

---

# 14. State Copying

The implementation must preserve the existing project's state model.

Jules must **not introduce a generic deep-copy architecture blindly**.

If the state is already represented through immutable/domain objects:

```text
dataclass(frozen=True)
```

or equivalent, use that architecture.

If state transitions already use constructors/factories, reuse them.

The goal is:

> **No mutation of caller-owned state.**

---

# 15. Attribute Resolution

Target resolution must be explicit.

Valid:

```text
player.confidence
```

Invalid:

```text
player.some_random_field
```

The engine must return a structured error instead of silently returning `None`, `0`, or another fallback.

---

# 16. Missing Attributes

Unknown attributes must produce an explicit error.

Recommended error:

```text
UNKNOWN_TARGET
```

Example:

```text
player.nonexistent_stat
```

must not become:

```text
0
```

This protects the simulator from silently corrupted state.

---

# 17. Type Validation

Before applying an effect:

```text
target type
        +
operation
        +
value type
```

must be compatible.

Example:

```text
confidence = 60
ADD 2
```

valid.

But:

```text
confidence = 60
ADD "high"
```

invalid.

The result must contain a structured error.

---

# 18. Domain Validation

Type correctness is not enough.

Example:

```text
age = 25
SET -10
```

may be numerically valid but domain-invalid.

Therefore:

```text
Type Validation
       ↓
Domain Validation
       ↓
Application
```

---

# 19. Bounded Attributes

Where the target has an explicit domain range, the range must be enforced.

For normalized attributes:

```text
minimum = 0
maximum = 100
```

Example:

```text
confidence = 98
ADD 10
```

Recommended behavior:

```text
→ 100
```

rather than:

```text
→ 108
```

The bounds must be explicit and deterministic.

---

# 20. No Universal OVR Modification

8E must not introduce generic rules such as:

```text
every positive event → OVR +1
```

or:

```text
every successful event → CA +2
```

The project's player/match systems already distinguish actual player attributes, performance and career development. Future event effects must not bypass those systems.

The Match Engine itself is explicitly separated from Career interpretation. 

---

# 21. Outcome Dependency

8E must apply effects based on the **resolved outcome from 8D**.

Example:

```text
Event
├── SUCCESS effects
└── FAILURE effects
```

If 8D returns:

```text
SUCCESS
```

8E applies:

```text
SUCCESS effects
```

If:

```text
FAILURE
```

it applies:

```text
FAILURE effects
```

---

# 22. Non-Triggered Events

Critical invariant:

```text
NOT_TRIGGERED
        ↓
NO EFFECTS
```

If 8D determines that an event did not occur, 8E must not modify state.

This prevents accidental side effects.

---

# 23. Conditional Effects

8E should **not implement an independent condition language**.

Do not create a second:

```text
evaluate_condition()
```

inside `effects.py`.

If conditional effects are needed later, they must reuse the existing Condition Engine.

For the initial 8E implementation:

> **Only effects associated with the already-resolved outcome are applied.**

---

# 24. Error Strategy

Recommended error categories:

```text
INVALID_EFFECT
UNKNOWN_TARGET
INVALID_OPERATION
TYPE_MISMATCH
INVALID_VALUE
OUT_OF_RANGE
INVALID_STATE
```

Errors must be explicit.

Forbidden:

```python
except Exception:
    pass
```

Forbidden:

```python
except Exception:
    return original_state
```

unless the existing architecture explicitly defines such behavior.

---

# 25. Partial Application Policy

This must be deterministic.

Recommended default:

> **Atomic batch application.**

If an effect batch contains:

```text
A valid
B valid
C invalid
```

then:

```text
A
B
C
```

must not leave the state partially modified.

Instead:

```text
batch rejected
state unchanged
structured error returned
```

This is safer for simulation integrity.

Individual `EffectApplication` records may still explain what validation failed.

---

# 26. Determinism

8E itself should contain **no randomness**.

Given:

```text
same initial state
+
same resolved event
+
same effect definitions
+
same rules
```

the result must always be:

```text
same resulting state
+
same application records
+
same errors
```

No:

```python
random.random()
```

No:

```python
hash(...)
```

for simulation identity or ordering.

The project specifically requires deterministic seeding and prohibits Python's randomized `hash()` for simulation seeds. 

---

# 27. Persistence Boundary

8E does not write directly to:

```text
SQLite
SQLAlchemy
Alembic
```

Instead:

```text
Simulation State
       ↓
8E
       ↓
EffectApplicationResult
       ↓
higher-level state/persistence layer
```

This preserves the infrastructure boundary.

---

# 28. Narrative Boundary

8E does not generate prose.

It may expose structured information such as:

```text
event_id
outcome
target
previous_value
resulting_value
```

A future Narrative Engine can then transform that into:

```text
story beat
timeline entry
career moment
narrative significance
```

This fits the project's future Narrative Engine direction, where events such as breakthroughs, failures, transfers, injuries, rivalries and comebacks are eventually interpreted narratively. 

---

# 29. Example

### Event

```text
"Young player receives first-team opportunity"
```

### 8C

```text
eligible = true
probability = 0.38
```

### 8D

```text
outcome = SUCCESS
```

### 8E

```text
confidence +2
morale +1
form +1
```

Input:

```text
confidence = 61
morale = 55
form = 50
```

Result:

```text
confidence = 63
morale = 56
form = 51
```

Application log:

```text
1. confidence 61 → 63
2. morale     55 → 56
3. form       50 → 51
```

---

# 30. Failure Example

8D:

```text
outcome = FAILURE
```

Failure effects:

```text
confidence -2
morale -1
```

Input:

```text
confidence = 61
morale = 55
```

Result:

```text
confidence = 59
morale = 54
```

No success effects are applied.

---

# 31. Testing Requirements

8E must include dedicated tests.

## Domain

Test:

* valid `EventEffect`;
* invalid target;
* invalid operation;
* invalid value;
* invalid combinations.

## Operations

Test:

```text
ADD
SET
MULTIPLY
```

## Sequential effects

Test:

```text
A → B → C
```

with dependent results.

## Bounds

Test:

```text
0
100
below 0
above 100
```

## Unknown target

Must fail explicitly.

## Type mismatch

Must fail explicitly.

## Atomicity

If one effect is invalid:

```text
original state == resulting state
```

## Immutability

Verify the caller's original state remains unchanged.

## Outcome integration

Test:

```text
SUCCESS → success effects
FAILURE → failure effects
NOT_TRIGGERED → no effects
```

## Determinism

Run the same input repeatedly and verify identical results.

---

# 32. Regression Requirements

Before completion:

```text
Phase 8E tests
+
all Phase 8C tests
+
all Phase 8D tests
+
complete existing test suite
```

must pass.

Jules must report:

```text
passed
failed
skipped
```

and identify any unrelated pre-existing failures.

---

# 33. Forbidden Regression

Phase 8E must not alter the behavior of:

```text
conditions.py
probability.py
8C
8D
```

unless an integration change is **strictly necessary** and explicitly justified.

The default expectation is:

```text
8C unchanged
8D unchanged
8E added
```

---

# 34. Repository Inspection Requirement

Before coding, Jules must inspect:

```text
backend/app/event/
backend/app/
tests/
```

and determine:

* existing event models;
* existing state models;
* actual 8C interfaces;
* actual 8D interfaces;
* naming conventions;
* existing error conventions;
* existing immutability conventions;
* existing test conventions.

**Jules must adapt this design to the actual repository rather than inventing parallel abstractions.**

---

# 35. Implementation Scope

Expected primary location:

```text
backend/app/event/effects.py
```

Expected tests:

```text
tests/event/
```

Exact filenames may be adapted to the existing repository structure.

No unrelated refactoring.

No frontend work.

No migrations.

No dependency additions unless strictly required.

---

# 36. Definition of Done

Phase 8E is complete only when:

```text
EventEffect exists
        +
EffectOperation exists
        +
Target resolution works
        +
Effects apply correctly
        +
Multiple effects work
        +
Bounds work
        +
Type validation works
        +
Unknown targets fail explicitly
        +
Atomicity works
        +
Input state remains unchanged
        +
8D integration works
        +
NOT_TRIGGERED produces no changes
        +
Determinism verified
        +
Dedicated tests pass
        +
Regression suite passes
```

This follows the project's broader definition that simulation features require not just code and tests, but believable/reproducible behavior and deterministic replay. 

---

# 37. Final Phase 8 Architecture

Once 8E is complete:

```text
                         EVENT SYSTEM
                              │
                              ▼
                    ┌──────────────────┐
                    │  Event Definition│
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ 8B Candidate Gen │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ 8C Conditions +  │
                    │    Probability   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  8D Resolution   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   8E Effects     │
                    │ State Application│S
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Simulation State │
                    └────────┬─────────┘
                             │
                 ┌───────────┴───────────┐
                 ▼                       ▼
          Future Career              Narrative
             Systems                  Systems
```

