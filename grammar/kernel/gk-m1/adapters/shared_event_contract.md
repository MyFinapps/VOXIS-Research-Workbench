# GK-M1 Shared Runtime Contract

VR and Veyu'lithra IF consume the **same canonical grammar event**.

FREEZE is a shared state-capture command that precedes evidentiary promotion. Desktop, VR, IF-adjacent tooling, and future runtimes should reference the same canonical `freeze_state` record rather than invent runtime-specific freeze objects.

Canonical FREEZE schema:

`schemas/records/freeze_record.schema.json`

## VR responsibility

- present bound primitives and explicit transforms;
- let the operator manipulate source objects;
- invoke deterministic measurement functions on the post-transform geometry;
- display measured relations separately from interpretation;
- save the original transform and measurements;
- on FREEZE, preserve the complete operator-visible state and emit/reference one canonical `freeze_state` record;
- preserve runtime-native pose/transform data when available without replacing the canonical cross-runtime transform.

VR must not silently promote a proposed primitive to `human_validated`.

FREEZE in VR must not silently promote an observed fit to evidence or manuscript correspondence.

## IF responsibility

- apply the canonical relation to symbolic world state;
- preserve the event ID, actor, target, operation, measurement payload, and epistemic entries;
- render prose separately from the event record;
- when referencing a frozen research state, preserve the original `freeze_id` rather than rewriting the freeze as narrative evidence.

IF prose is a rendering of an event/state transition, not manuscript evidence.

## Shared FREEZE boundary

A canonical FREEZE record is observational state capture:

- `epistemic_class: observation`
- `evidence_status: not_evidence`

It may preserve active glyphs, glyph clusters, roots, stems, leaves, pipes, landmarks, pivots, or arbitrary operator-selected regions without asserting that those features have a validated grammatical role.

Later Measurement, Alignment, Evidence, Interpretation, or Hypothesis records may reference the `freeze_id`; they must not overwrite the original frozen state.

## Shared prohibition

Neither runtime may automatically convert a geometric relation into semantic terms such as transmitter, receiver, injection, receptacle, earth/dirt, activation, or grounding.

Neither runtime may treat FREEZE as proof merely because multiple features appear to align in the captured state.
