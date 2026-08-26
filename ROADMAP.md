# Engineering Roadmap

## Baseline — current

- GK-M0 shared event model
- P001 Enter the Folio Unity/OpenXR starter
- P002-WXR-001 Dual Folio First Contact
- Kepler geometry registry v0.1

## GK-M1 — merge-ready

- [x] human-validated 2r/2v/3r primitive bindings
  - all 7 seed annotations accepted by the human operator
  - validation confirms annotation adequacy only
- [x] deterministic relation measurement functions
- [x] reusable Observation / Search Session / Alignment Candidate record emitters
  - Alignment Candidate emission rejects unvalidated primitive bindings
- [x] shared runtime contract for VR and Veyu'lithra IF
- [x] repeatable post-validation CI regression pass
- [x] validated SHA-256 milestone/provenance manifest verified in CI

## Next — EX-GRAMMAR-001 / P003 Grammar Mode First Light

Before any manuscript-bound relation measurement, predeclare the Search Session: eligible folios/primitives, relations, transforms, tolerances, and control/counterexample strategy.

Then:

- selectable primitives
- live measured relations
- operator annotation
- sequence recorder/replay
- explicit counterexample/null-result capture

## Shared experimental loop

Validated manuscript annotation → predeclared Search Session → deterministic measurement → Observation/Alignment record → VR/IF replay → controls/counterexamples → source review.
