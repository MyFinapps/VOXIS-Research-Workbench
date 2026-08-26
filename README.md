# VOXIS Research Workbench

Versioned engineering spine for the VOXIS Alignment Engine, Voynich VR Lab, Grammar Kernel, experiment definitions, and provenance tooling.

> **Public staging mode:** This repository is temporarily public. The engineering baseline excludes raw/private evidence and heavyweight research media; see `PUBLIC_REPOSITORY_NOTICE.md`.

> **Research rule:** Geometry first. Measurement second. Meaning last.
>
> Geometric fit is a research aid, not proof of manuscript correspondence.

## Why this repository exists

This repository stores reproducible engineering artifacts: source code, schemas, registries, deterministic tests, small canonical fixtures, experiment definitions, and provenance metadata.

It is **not** the master archive for heavyweight source evidence. High-resolution manuscript PDFs, raw photography, large videos, Blender assets, and other bulky research media remain in the external/local research archive and are referenced here by provenance records and hashes.

## Current baseline

| Area | Baseline | Status |
|---|---|---|
| Grammar | `grammar/kernel/gk-m0` | synthetic tests passed; manuscript bindings provisional |
| WebXR | `vr/webxr/p002-dual-folio` | desktop/browser surface QA complete; Quest immersive interaction requires validation |
| Unity VR | `vr/unity/p001-enter-the-folio` | statically assembled; Unity/Quest runtime validation still required |
| Geometry Registry | `registries/kepler` | seed registry; Voynich crosswalk unassessed |

## Repository map

```text
grammar/
  kernel/
    gk-m0/                 Shared canonical grammar/event model
vr/
  webxr/
    p002-dual-folio/       Quest-browser Dual Folio First Contact
  unity/
    p001-enter-the-folio/  Unity/OpenXR Enter the Folio starter
registries/
  kepler/                  Kepler geometry seed registry
experiments/               Versioned experiment definitions/results
provenance/
  source-manifests/        Hashes and source identity records
docs/                      Workbench policies and architecture notes
```

## Epistemic classes

Claim-bearing records distinguish:

1. observation
2. measurement
3. inference
4. interpretation
5. speculation

Interpretation may reference measured geometry; it may never overwrite it.

## Engineering workflow

1. Preserve source identity and hashes.
2. Declare primitives/operators before testing where feasible.
3. Record exact transforms and measurement outputs.
4. Retain null and negative results.
5. Validate locally/on target hardware before promoting a feature to infrastructure.
6. Commit changes with a clear milestone/experiment reference.
7. Tag frozen milestones only after validation status is explicit.

## Next milestone

**GK-M1 — Bind the Grammar to the Manuscript**

Human-validate selected primitive coordinates/masks for 2r, 2v, and 3r; implement deterministic measurement functions for the seed relations; then feed the same canonical events into Grammar Mode VR and Veyu'lithra IF.
