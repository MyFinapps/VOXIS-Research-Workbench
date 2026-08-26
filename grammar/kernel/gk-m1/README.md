# GK-M1 — Bind the Grammar to the Manuscript

GK-M1 advances the VOXIS Grammar Kernel from synthetic-only behavior toward reproducible manuscript-bound geometry while preserving the Workbench epistemic boundary.

## Scope

GK-M1 does four things:

1. defines a reproducible source-image coordinate frame for Voynich folios 2r, 2v, and 3r;
2. records a small set of **assistant-proposed, human-validation-pending** primitive geometries;
3. implements deterministic geometry measurements for the seed relations `ALIGN`, `POINT`, `OVERLAP`, `COVER`, and `TERMINATE`;
4. keeps the same canonical event compatible with both VR and Veyu'lithra IF adapters without adding semantic interpretation.

## Important status boundary

The coordinates in `bindings/voynich_2r_2v_3r_gk_m1.json` are **not yet human validated**. They are proposed measurement anchors derived from the embedded source images in the project PDF and must remain `proposed_pending_human_validation` until a human operator confirms or edits them.

No cross-folio correspondence claim is created by this milestone.

## Coordinate system

Each folio binding is tied to the original embedded raster from the project PDF, not to a screenshot or PDF-page margin.

- origin: top-left of the embedded folio raster
- x: increases rightward
- y: increases downward
- normalized coordinates: `[0,1] x [0,1]`
- raw pixel coordinates are retained alongside normalized coordinates
- source image SHA-256 is retained for reproducibility

## Seed bound primitives

First pass intentionally stays small:

- `VM.f2r.root_pivot` — `ROOT` point candidate
- `VM.f2r.lower_stem_axis` — `STEM` segment candidate
- `VM.f2r.root_region` — coarse `ROOT` bbox candidate
- `VM.f2v.central_y` — `Y` point candidate
- `VM.f2v.upper_stem_axis` — `STEM` segment candidate
- `VM.f3r.root_crown` — `ROOT` point candidate
- `VM.f3r.root_region` — coarse `ROOT` bbox candidate

`DENSE_FIELD` and `GLYPH_CLUSTER` manuscript bindings are deliberately deferred until selection rules are declared.

## Measurement rule

Measurements operate on geometry **after an explicit recorded planar transform**. Source-normalized geometry is never silently reinterpreted as a cross-folio alignment.

## Promotion rule

A proposed binding may be promoted to `human_validated` only after a human operator confirms the landmark/region against the named source image. A geometric result may later become an alignment candidate only through a separate Search Session / Alignment Record workflow.
