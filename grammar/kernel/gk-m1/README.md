# GK-M1 — Bind the Grammar to the Manuscript

GK-M1 advances the VOXIS Grammar Kernel from synthetic-only behavior to reproducible manuscript-bound geometry while preserving the Workbench epistemic boundary.

## Scope

GK-M1 does five things:

1. defines a reproducible source-image coordinate frame for Voynich folios 2r, 2v, and 3r;
2. records a small set of **human-validated operational primitive geometries**;
3. implements deterministic geometry measurements for the seed relations `ALIGN`, `POINT`, `OVERLAP`, `COVER`, and `TERMINATE`;
4. provides provenance-preserving Observation, Search Session, and Alignment Candidate emitters with an explicit validation gate;
5. keeps the same canonical event compatible with both VR and Veyu'lithra IF adapters without adding semantic interpretation.

## Important status boundary

All seven seed annotations in `bindings/voynich_2r_2v_3r_gk_m1.json` were accepted by the human operator on `2026-08-26T04:09:45Z` after visual review of the GK-M1 validation pack.

That validation confirms **annotation adequacy only**. It does not establish a cross-folio correspondence, alignment, recurring grammar, procedure, manuscript intent, or meaning.

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

The first pass intentionally stays small:

- `VM.f2r.root_pivot` — human-validated `ROOT` point
- `VM.f2r.lower_stem_axis` — human-validated `STEM` segment
- `VM.f2r.root_region` — human-validated coarse `ROOT` bbox
- `VM.f2v.central_y` — human-validated `Y` point
- `VM.f2v.upper_stem_axis` — human-validated `STEM` segment
- `VM.f3r.root_crown` — human-validated `ROOT` point
- `VM.f3r.root_region` — human-validated coarse `ROOT` bbox

`DENSE_FIELD` and `GLYPH_CLUSTER` manuscript bindings remain deliberately deferred until reproducible selection rules are declared.

## Measurement rule

Measurements operate on geometry **after an explicit recorded planar transform**. Source-normalized geometry is never silently reinterpreted as a cross-folio alignment.

## Record emission rule

Observation Records preserve exact operator wording. Search Sessions predeclare source scope, primitives, relations, and allowed transforms. Alignment Candidate emission rejects any primitive that has not been promoted to `human_validated` or `measured`, and always leaves `correspondence_claim` and `interpretation` null by default.

## Validation and CI

The 14-test regression suite covers binding status/provenance boundaries, coordinate round-trips, deterministic transform/relation behavior, semantic leakage, exact observation wording, Search Session scope, and rejection of unvalidated Alignment Candidates.

The post-validation suite passed in GitHub Actions. Repeatable CI is defined in `.github/workflows/gk-m1-tests.yml`.

## Next gate

Before measuring a manuscript-bound relation, create a recorded Search Session that predeclares:

- source folios;
- eligible validated primitives;
- tested relations;
- allowed transforms;
- tolerances/measurement method;
- control or counterexample strategy where applicable.

Only then may a measured result become an Alignment Candidate. Interpretation remains separate.
