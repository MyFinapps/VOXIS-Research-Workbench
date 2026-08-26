# EX-GRAMMAR-002A Stage A — Binding Defect Discovered

**Status:** measurement blocked pending human review of corrected geometry

During blind candidate-inventory construction for EX-GRAMMAR-002A, close inspection of the original `VM.f2v` embedded raster showed that two GK-M1 annotations used by EX-GRAMMAR-001 are visibly offset from the visual structures they were intended to mark:

- `VM.f2v.central_y` is offset leftward into the adjacent negative-space lobe rather than centered on the visible Y-like botanical junction;
- `VM.f2v.upper_stem_axis` runs materially left of the visible green stem for a substantial portion of its declared segment.

The prior human approval is preserved as a historical validation event, but Stage A demonstrates that annotation adequacy does not survive closer inspection under the stricter candidate-inventory workflow.

## Consequence

EX-GRAMMAR-001's numerical POINT result is not used as evidence or as an index-case score in EX-GRAMMAR-002A until the geometry is corrected and revalidated. The prior result remains preserved for provenance and must be labeled **invalidated_by_binding_defect** rather than deleted.

## Boundary

This defect concerns annotation geometry only. It says nothing about whether a STEM → POINT → Y relation exists or does not exist in the manuscript.

## Recovery procedure

1. construct corrected Stage A candidate annotations without pairwise distance/angle output;
2. record all included and excluded candidates;
3. obtain human accept/adjust/reject review;
4. freeze and hash the corrected inventory;
5. correct the canonical binding through an explicit versioned patch;
6. rerun EX-GRAMMAR-001 only as a corrected historical comparison, not as the original preregistered result;
7. execute EX-GRAMMAR-002A only after the corrected inventory is frozen.

No EX-GRAMMAR-002A pairwise measurement may run before steps 1–4 are complete.
