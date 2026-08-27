# VISTA v0.1 Charter

## Name

**VISTA — VOXIS Immersive Spatial Testing & Analysis**

## Status

Initial architecture charter for the immersive/spatial research environment within the VOXIS Research Workbench.

## Core definition

VISTA is an **immersive research environment**, not an engine, hypothesis, evidence claim, or manuscript interpretation.

VISTA provides a spatial workspace in which VOXIS capabilities can operate together. Engines supply capabilities; VISTA supplies the embodied research space in which those capabilities are used.

Primary architectural relationship:

`VOXIS Research Workbench -> VISTA -> Constellarium workspace -> VOXIS engines + interaction modes`

## The Constellarium

**The Constellarium** is the first VISTA workspace.

It is a navigable spatial laboratory for handling manuscript representations, alignment candidates, frozen observations, annotations, measurements, comparisons, and later procedural experiments.

The Constellarium is not itself a claim about the structure or intended use of the Voynich Manuscript. It is a research substrate for testing spatial relationships.

## Initial trusted interaction primitives

VISTA v0.1 begins only with operations that are methodologically neutral:

- select
- grab / release
- translate
- rotate
- scale
- change opacity
- stack / reorder
- establish or move anchor / pivot
- annotate
- FREEZE
- read back a frozen state

These primitives permit exploration without asserting that any observed configuration is meaningful.

## Engine relationship

VISTA may recruit multiple VOXIS engines without becoming any of them.

Initial engine participation may include:

- Alignment Engine — transforms, registration, pivots, stacking, overlays
- Observation and Evidence Engine — epistemic classification and record linkage
- Geometry Grammar Engine — optional candidate grammar relations and later hypothesis-aware overlays
- Harmonic Registration Engine — optional stability/scoring where appropriate
- VR Interaction Engine — embodied input, locomotion, grabbing, spatial manipulation, controller/hand state

No engine is mandatory unless required by the active mode or experiment.

## Mode relationship

VISTA hosts modes; it is not itself a mode.

Initial modes:

- Discovery Mode — free spatial exploration
- Candidate Observation state — entered through FREEZE
- Review Mode — replay and inspect preserved states
- Evidence Mode — later formal measurement and reproducibility work
- Control / Test Mode — later randomized or constrained comparisons

## FREEZE contract

VISTA uses the same canonical FREEZE record as the desktop Workbench.

Primary transition:

`Discovery -> FREEZE -> Candidate Observation`

FREEZE preserves a state. It does not validate that state.

A VISTA FREEZE should preserve, when available:

- active source and representation references
- stack order
- visibility and opacity
- translation
- rotation
- scale
- pivot and pivot rule
- reflection state
- selected features / landmarks / anchors
- exact operator note
- timestamp
- runtime and build identifiers
- coordinate-space reference
- controller / hand pose
- camera / head pose
- optional pre-FREEZE media buffer
- source provenance

## Epistemic boundary

VISTA must preserve the VOXIS epistemic ladder:

1. observation
2. measurement
3. inference
4. interpretation
5. speculation

A visually compelling spatial alignment is an observation candidate until measured and tested.

**Geometric fit is a research aid, not proof of manuscript correspondence.**

## Hypothesis neutrality

The base VISTA environment must not hard-code manuscript hypotheses.

Generic spatial operations are tools. Specific ideas such as root-to-root alignment, glyph participation, density matching, multi-folio procedural ordering, or any semantic interpretation must remain optional hypothesis layers or experiment definitions.

VISTA should make it easy to test a hypothesis without making the hypothesis structurally necessary for the environment to function.

## Provenance and persistence principles

VISTA follows VOXIS local-first and non-destructive practice:

- source assets remain immutable
- derivatives are versioned
- frozen states are immutable
- later records reference frozen states rather than rewriting them
- null and negative results are retained
- runtime-specific coordinates are explicitly named
- conversions between desktop and VR coordinate spaces are reproducible
- human validation remains explicit

## Planned workspace progression

### Overlay Chamber

Two-representation spatial alignment workspace. This is the first implementation target.

### Constellation Chamber

Multi-representation workspace for comparing and linking roots, stems, glyphs, glyph clusters, regions, anchors, and candidate grammar relationships.

### Procedural Theater

Replayable sequence workspace for testing ordered operations or folio interactions. A procedure shown here remains a tested hypothesis unless independently supported.

## Validation ladder

VISTA capabilities should be described using explicit validation status:

1. Designed
2. Implemented
3. Desktop-emulated
4. Quest-observed
5. Quest-verified

A capability must not be described as Quest-verified until it has been exercised successfully on the actual target headset and the relevant persisted state has been read back or otherwise independently confirmed.

## v0.1 success boundary

VISTA v0.1 is successful when a minimal immersive workspace can host manuscript representations, permit neutral spatial manipulation, and emit the canonical VOXIS FREEZE object without changing the epistemic status of the captured configuration.
