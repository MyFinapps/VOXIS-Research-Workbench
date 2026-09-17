# FREEZE State Capture v0.1

## Status

Proof-of-concept design note for the VOXIS Research Workbench.

## Core definition

**FREEZE is a state-transition command.** It is not an engine and is not necessarily a full operating mode.

Primary transition:

`Discovery -> FREEZE -> Candidate Observation`

FREEZE preserves the exact research state at the moment an operator identifies a potentially meaningful configuration, without converting that configuration into evidence or proof.

## Minimum captured state

A FREEZE record should preserve, at minimum:

- folios or representations present
- stacking order
- position / translation of each active representation
- scale
- rotation
- pivot location and pivot rule
- opacity and visibility state
- active landmarks, anchors, or selected features
- operator note or spoken annotation
- timestamp
- source context and provenance identifiers
- optional short pre-FREEZE media buffer when available

## Relationship to modes

### Discovery Mode

Free exploration. The operator may move, rotate, scale, stack, compare, and annotate representations without implying that any observed fit is evidentiary.

### Evidence Mode

A frozen candidate can be promoted for formal measurement, residual calculation, reproducibility checks, and control testing.

### Review Mode

Frozen states can be replayed, compared, annotated, and inspected without altering the preserved source state.

### Control / Test Mode

A frozen candidate can seed randomized, constrained, or preregistered comparison procedures.

## Epistemic boundary

FREEZE preserves discovery; it does not validate it.

The Workbench must continue to distinguish:

1. observation
2. measurement
3. inference
4. interpretation
5. speculation

A visually compelling alignment may be frozen as a candidate observation before any measurement has occurred. Geometric fit remains a research aid, not proof of manuscript correspondence.

## POC acceptance criteria

This POC is successful when:

1. this document exists on the dedicated GitHub feature branch;
2. a matching checkpoint document exists in the VOXIS Research Workbench Dropbox tree;
3. both documents can be read back from their respective systems;
4. the GitHub branch remains isolated from `main` until human review;
5. no existing research records are modified or deleted.
