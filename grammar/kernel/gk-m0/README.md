# VOXIS Grammar Kernel — GK-M0 v0.1.0

**Milestone:** GK-M0 — Shared Event Model  
**Status:** seed / implementation-ready / not manuscript-proof  
**Purpose:** Provide one canonical grammar/event model that can be executed by both the VOXIS VR Workbench and the Veyu'lithra Interactive Fiction (IF) runtime without merging measurement and interpretation.

## Core principle

The same canonical event is used in both environments:

- **VR adapter:** embodied execution and geometric measurement.
- **IF adapter:** symbolic/stateful execution and procedural consequence.

Neither adapter may silently add semantic meaning. Interpretation is an optional layer attached to an unchanged underlying event.

## Seed vocabulary

### Primitives

- `ROOT`
- `STEM`
- `Y`
- `DENSE_FIELD`
- `GLYPH_CLUSTER`

### Relations / operations

- `ALIGN`
- `POINT`
- `OVERLAP`
- `COVER`
- `TERMINATE`

The vocabulary is intentionally tiny. A useful grammar should compress many observations with a small reusable set. If new observations require a new verb every time, that is evidence against the current grammar model.

## Epistemic classes

Every claim-bearing object must explicitly use one of:

1. `observation`
2. `measurement`
3. `inference`
4. `interpretation`
5. `speculation`

A geometric event can carry multiple entries from different classes, but they remain separate records. Example: a measured overlap may have an operator observation and an optional interpretation; the interpretation may not overwrite the measurement.

## Package layout

- `schema/grammar-kernel.schema.json` — JSON Schema for the canonical event/sequence/state model.
- `registry/primitives.json` — seed primitive registry.
- `registry/relations.json` — seed relation registry and expected measurement outputs.
- `bindings/voynich_2r_2v_3r_seed.json` — provenance-only folio bindings and candidate primitive slots; intentionally unassessed.
- `examples/EX-GRAMMAR-001.json` — synthetic ROOT/STEM/Y sequence used to test the kernel without manuscript claims.
- `examples/OBS-2R2V-CANDIDATE-001.json` — a deliberately provisional candidate record showing how a human observation can be encoded without promotion to evidence.
- `adapters/if_adapter.py` — symbolic state adapter.
- `adapters/vr_adapter.py` — VR command/measurement contract adapter (runtime-neutral stub).
- `tests/test_kernel.py` — deterministic tests for shared-event behavior and epistemic separation.
- `PROVENANCE.md` — source/provenance notes and boundaries.

## Canonical event rule

A canonical event records:

- actor primitive instance
- operation
- target primitive instance
- before state
- after state
- exact transform(s), if any
- declared measurements
- operator wording verbatim when useful
- epistemic entries kept separate
- provenance

A VR event and an IF event referencing the same `event_id` must preserve the same actor, operation, target, and source provenance.

## Promotion ladder

A saved configuration or event is **not automatically an Alignment Record or Evidence Record**.

Suggested progression:

`configuration/event -> measured candidate -> Alignment Record -> optional Evidence link -> optional Hypothesis/Interpretation link`

Null and negative results must be retained.

## First shared experiment

`EX-GRAMMAR-001` is synthetic by design. It tests whether the kernel can represent:

`ROOT -> STEM -> Y`

using `ALIGN`, `POINT`, and `COVER` without manuscript-specific interpretation.

Only after deterministic synthetic tests pass should manuscript-bound events be promoted beyond provisional observation.

## Run the tests

```bash
python tests/test_kernel.py
```

No external Python packages are required.

## Next milestone

**GK-M1** should add human-validated folio coordinates/masks for selected primitives, deterministic measurement functions for all five relations, and adapters that write Observation/Search Session/Alignment records into the existing VOXIS research spine.
