# VISTA M0 — First Presence

## Milestone statement

**First Presence** is the smallest useful immersive proof-of-concept for VISTA.

Success means an operator can enter the Constellarium on the target headset, manipulate two manuscript representations in space, invoke FREEZE, and later recover the same Candidate Observation outside the headset.

This milestone validates the immersive instrument path. It does **not** validate any Voynich correspondence hypothesis.

## Target environment

Primary target:

- Meta Quest 3
- WebXR-capable browser/runtime unless empirical testing shows a different runtime is required

Development may use desktop emulation, but desktop success is not Quest verification.

## M0 workspace

The initial Constellarium workspace is the **Overlay Chamber**.

Only two active manuscript representations are required.

Suggested initial pair for engineering continuity:

- source representation: Voynich folio 2v
- target representation: a previously explored target folio or wheel image

The exact pair is an engineering fixture, not a correspondence claim.

## Required user workflow

The operator must be able to:

1. enter the immersive workspace;
2. see both source representations with provenance labels available on demand;
3. move through the workspace with controller-based locomotion;
4. select a representation;
5. grab and release it;
6. translate it in three-dimensional space;
7. rotate it;
8. scale it;
9. change its opacity;
10. establish or use an anchor / pivot;
11. place one representation relative to the other;
12. enter an exact operator note, by supported input method;
13. invoke **FREEZE**;
14. receive a visible confirmation that a Candidate Observation was captured;
15. continue manipulating the live workspace without altering the frozen state;
16. read back the frozen state from outside the headset.

## FREEZE acceptance criteria

A successful M0 FREEZE must emit the canonical `freeze_state` object and preserve at least:

- unique `freeze_id`
- timestamp
- `epistemic_class = observation`
- `evidence_status = not_evidence`
- `measurement_status = unmeasured` unless a separately classified measurement is linked
- source references
- representation references
- stack / ordering state
- visibility
- opacity
- translation
- rotation
- scale
- pivot
- pivot rule when used
- coordinate-space reference
- runtime identifier
- exact operator note when supplied
- headset / controller or hand state when available
- source provenance

## Immutability test

After FREEZE:

1. change at least two live transform values;
2. change opacity;
3. move or rotate the representation again;
4. read back the frozen record;
5. verify that the frozen record retains the pre-change values.

Passing this test demonstrates that FREEZE is a temporal snapshot rather than a pointer to mutable live state.

## Cross-runtime reproducibility test

At least one frozen VISTA state must be inspected outside VR.

The external review surface must show:

- the same `freeze_id`;
- the same exact operator note;
- the same source and representation references;
- the same epistemic classification;
- the preserved runtime-native transform;
- sufficient coordinate-space metadata to reproduce or convert the state deterministically.

Numerical coordinates do not need to equal desktop pixel coordinates. They must be explicitly named and reproducibly convertible.

## Visual interaction requirements

The M0 interface should favor research clarity over spectacle.

Required visible cues:

- selected representation state
- anchor / pivot cue when active
- opacity / transform feedback
- FREEZE action
- frozen confirmation
- `Candidate Observation — not evidence`
- clear distinction between live state and frozen state

Atmospheric design is welcome, but it must not obscure source material, transform state, provenance, or epistemic status.

## Locomotion boundary

M0 requires controller / joystick locomotion sufficient to approach, step back from, and move around the representations.

Room-scale physical walking may work opportunistically but is not required for milestone success.

Comfort requirements:

- no forced camera motion during manuscript manipulation
- no automatic rotation of the operator viewpoint
- reasonable default movement speed
- ability to operate primarily from a stationary physical position

## Explicitly out of scope for M0

The following are intentionally deferred:

- automatic alignment suggestions
- grammar inference
- density-match scoring
- glyph interpretation
- semantic interpretation
- procedural sequence claims
- multi-user collaboration
- Constellation Chamber multi-folio graphing
- Procedural Theater
- AI-generated manuscript meaning
- evidentiary promotion based solely on visual fit

## Instrument tests

M0 should include deterministic checks for:

- FREEZE schema validity
- required provenance
- transform serialization
- quaternion / rotation representation
- create-only frozen persistence
- read-back equality
- coordinate-space labeling
- epistemic classification
- source immutability
- live-state mutation not affecting frozen state

## Human target-device validation

The final M0 gate must be performed on the actual Quest 3.

Minimum human validation script:

1. enter VISTA;
2. identify both representations;
3. grab the movable folio;
4. rotate to an arbitrary memorable angle/state;
5. set a visibly distinct opacity;
6. translate it to a memorable position;
7. enter the note `JT VISTA M0 validation 01`;
8. invoke FREEZE;
9. record the returned `freeze_id`;
10. change the live folio state substantially;
11. exit or switch to the external review surface;
12. read back the frozen record;
13. confirm original transform, opacity, note, provenance, and epistemic classification.

## Validation status vocabulary

Each M0 capability receives one of these statuses:

- **Designed** — specified but not implemented
- **Implemented** — code exists
- **Desktop-emulated** — exercised using non-headset XR or desktop simulation
- **Quest-observed** — seen operating on Quest but not independently validated
- **Quest-verified** — exercised on Quest and state/output independently confirmed

## Milestone pass condition

VISTA M0 — First Presence passes only when all of the following are true:

1. immersive workspace loads on Quest 3;
2. two representations are present and manipulable;
3. controller locomotion works;
4. translate / rotate / scale / opacity controls work;
5. FREEZE creates a canonical Candidate Observation;
6. the operator can continue exploring after FREEZE;
7. the frozen record remains immutable;
8. the record can be read back outside VR;
9. provenance survives the round trip;
10. the record remains explicitly **observation, not evidence**.

## Research boundary

**Geometry first. Measurement second. Meaning last.**

A successful First Presence milestone proves that VOXIS can preserve immersive spatial experiments with provenance. It does not prove that the manuscript was intended to be manipulated, overlaid, stacked, or read procedurally.
