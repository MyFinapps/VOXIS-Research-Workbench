# Engineering Roadmap

## Baseline — current

- GK-M0 shared event model
- P001 Enter the Folio Unity/OpenXR starter
- P002-WXR-001 Dual Folio First Contact
- Kepler geometry registry v0.1

## In progress — GK-M1

- [x] human-validated 2r/2v/3r primitive bindings
  - all 7 seed annotations accepted by the human operator
  - validation confirms annotation adequacy only
- [x] deterministic relation measurement functions
- [x] reusable Observation / Search Session / Alignment Candidate record emitters
  - Alignment Candidate emission rejects unvalidated primitive bindings
- [x] shared runtime contract for VR and Veyu'lithra IF
- [ ] repeatable post-validation CI regression pass
- [ ] refresh milestone/provenance hashes after validation
- [ ] predeclare first manuscript-bound Search Session before relation measurement

## Then — P003 Grammar Mode First Light

- selectable primitives
- live measured relations
- operator annotation
- sequence recorder/replay
- explicit counterexample/null-result capture

## Shared experimental loop

Validated manuscript annotation → predeclared Search Session → deterministic measurement → Observation/Alignment record → VR/IF replay → controls/counterexamples → source review.
