# VISTA M1 - Precision & Annotation

## Milestone statement

Enter the Constellarium on Quest 3, manipulate three manuscript representations with stable single-purpose transform modes, use configurable spatial grids and snapping, place persistent spatial observations, form and lock an Alignment Group, then FREEZE the resulting state without promoting any geometric relationship to evidence.

## Research boundary

- Geometric fit is a research aid, not proof of manuscript correspondence.
- Thumbtacks, yarn, sticky notes, and Alignment Groups preserve operator-created spatial structure.
- A spatial annotation is not automatically a measurement, inference, interpretation, or evidence claim.
- FREEZE remains an immutable Candidate Observation with `observation / not_evidence` status.

## M1 capabilities

### Stable manipulation

Right-thumbstick input is mode-gated:

- `MOVE` - dominant-axis latch rejects diagonal drift.
- `ROTATE` - accepts only the horizontal axis.
- `SCALE` - accepts only the vertical axis.
- `Precision Mode` - temporarily reduces transform sensitivity.

Direct right-trigger grabbing remains independent of the research pivot and preserves the exact contact point.

### Multidimensional grid

The Alignment Engine exposes independent controls for:

- visual grid resolution;
- snap resolution;
- snap strength;
- angular snap increment;
- XZ, XY, and YZ world grids;
- angular rings around the active pivot;
- stack/depth planes.

Visual resolution and snap resolution are intentionally separate.

### Spatial research objects

- `ANCHOR-*` - thumbtack / spatial anchor marker.
- `NOTE-*` - exact-wording observation annotation.
- `LINK-*` - yarn / operator-declared candidate relation.
- `AG-*` - versioned Alignment Group workspace structure.

Spatial records are immutable. Revisions emit new records and may reference `supersedes_record_id`.

### Alignment Groups

An Alignment Group preserves the relative arrangement of two or more representations and can be manipulated as one object. Group locks independently constrain position, rotation, scale, pivot, or all transforms.

An Alignment Group is workspace structure, not an evidence claim.

## Three-folio engineering fixture

M1 uses 2r, 2v, and 3r to exercise group behavior. This is an engineering fixture only and does not assert manuscript intent, correspondence, or a preferred stacking order.

## Validation ladder

1. Designed
2. Implemented
3. Local contract-tested
4. Desktop-emulated
5. Quest-observed
6. Quest-verified

M1 must not be called Quest-verified until target-device manipulation, spatial-record persistence, group behavior, and FREEZE/read-back have been human-validated on the actual Quest 3.
