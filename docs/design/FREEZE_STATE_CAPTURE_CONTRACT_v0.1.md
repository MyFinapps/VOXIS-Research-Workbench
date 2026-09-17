# FREEZE State Capture Contract v0.1

## Purpose

This contract defines the canonical Workbench behavior for the FREEZE command.

FREEZE is a state-transition command used to preserve a potentially meaningful research configuration at the instant the operator chooses to capture it.

Primary transition:

`Discovery -> FREEZE -> Candidate Observation`

FREEZE does **not** validate the captured configuration. It does not create evidence, establish correspondence, assign manuscript function, or infer meaning.

## Canonical object

Every FREEZE command emits one immutable `freeze_state` record conforming to:

`schemas/records/freeze_record.schema.json`

The same record shape is intended to be emitted by desktop, WebXR, Unity VR, physical-log import, and future runtime adapters.

## Required capture behavior

At invocation time, the runtime must capture the current research state without requiring the operator to reconstruct it manually.

Minimum state includes:

- active source and representation references;
- stack order;
- visibility and opacity;
- exact translation, rotation, scale, pivot, and reflection state;
- coordinate-space identity and units when known;
- active landmarks, anchors, pivots, glyphs, glyph clusters, stems, roots, leaves, pipes, or other selected features;
- runtime and mode context;
- operator identity when available;
- exact operator note or spoken wording when available;
- provenance references;
- optional camera/controller state;
- optional pre-FREEZE media buffer references.

If a runtime cannot capture a required field, the record must be marked `capture_completeness: partial` and list the unavailable elements in `missing_fields`. Missing data must not be silently fabricated.

## Immutability

A FREEZE record is immutable after emission.

Later research operations may create new records that reference the original `freeze_id`, but they must not overwrite the frozen state. This includes:

- Observation Records;
- Measurement Records;
- Alignment Records;
- Evidence Records;
- Review annotations;
- control/test runs;
- interpretations or hypotheses.

Corrections to a mistaken FREEZE record are represented by a new record plus provenance linking the replacement/supersession. The original remains retained.

## Epistemic boundary

A FREEZE record is classified as:

- `epistemic_class: observation`
- `evidence_status: not_evidence`

A frozen state may be visually compelling. That does not change its class.

Measurements may later be linked, changing `measurement_status` from `unmeasured` to `measurement_linked` in a derived/reference record, but the original frozen payload remains preserved.

The Workbench continues to distinguish:

1. observation
2. measurement
3. inference
4. interpretation
5. speculation

Geometric fit remains a research aid, not proof of manuscript correspondence.

## Runtime command semantics

### Voice

Example operator input:

`FREEZE`

The runtime records the raw trigger input, emits the canonical record, acknowledges capture, and returns to the configured post-capture mode.

Voice recognition confidence may be recorded in runtime-native metadata but must not alter the frozen geometry.

### Controller / keyboard / UI

Controller buttons, keyboard shortcuts, and UI actions are alternate trigger surfaces for the same canonical command. They must not emit a different record type.

## Modes

Recommended default behavior:

- Discovery Mode -> FREEZE -> Candidate Observation, then remain in Discovery Mode unless the operator explicitly promotes the candidate for measurement.
- Evidence Mode -> FREEZE preserves the current evidence-work state but does not itself produce additional evidence.
- Review Mode -> FREEZE may preserve a comparison/review configuration as a new candidate observation.
- Control/Test Mode -> FREEZE may preserve an operator-observed control configuration; control provenance must remain explicit.

The runtime should never force an automatic interpretation or hypothesis transition after FREEZE.

## Media buffer

When technically feasible, runtimes may maintain a short rolling local media buffer. FREEZE may retain references to a bounded interval immediately before and/or after capture.

The canonical record stores references and offsets rather than embedding large media objects. Heavyweight video/audio remains in the local/external archive with provenance and hashes.

## Coordinate and transform fidelity

The canonical cross-runtime transform contains:

- translation vector;
- quaternion rotation in XYZW order;
- scale vector;
- pivot vector;
- optional reflection flags;
- coordinate-space reference;
- units when known.

Runtime-native transform payloads may additionally be retained losslessly under `native_transform`.

No adapter may silently convert, normalize, or round a transform in a way that prevents reconstruction of the operator-visible state.

## Feature references

FREEZE may reference features whether or not those features are yet proven to participate in manuscript grammar.

Examples include:

- Y or stub landmarks;
- roots;
- stems and density regions;
- leaves;
- pipes;
- glyphs;
- glyph clusters;
- arbitrary operator-defined regions.

Feature selection inside a FREEZE record is observational context, not validation of the feature's grammatical role.

## Promotion path

A typical workflow is:

`Discovery -> FREEZE -> Candidate Observation -> Review -> Measurement -> Control/Test -> Evidence assessment`

Interpretation and hypothesis records may reference the resulting evidence chain but remain separate objects.

FREEZE therefore functions as the bridge between spontaneous discovery and reproducible research without collapsing those stages into one another.
