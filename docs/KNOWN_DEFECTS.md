# Known Validation Defects

## VD-001 — GK-M1 2v primitive-coordinate offset

**Discovered:** during EX-GRAMMAR-002A Stage A candidate-inventory construction  
**Affected historical bindings:** `VM.f2v.upper_stem_axis`, `VM.f2v.central_y`  
**Affected historical result:** `EX-GRAMMAR-001-R1`

Close inspection of the original `VM.f2v` source raster showed that the stored 2v stem-axis segment and central-Y point were visibly offset from the botanical structures they were intended to mark. The previous human approval is retained as a historical event, but annotation adequacy does not survive the later close audit.

### Current handling

- EX-GRAMMAR-001 R1 is retained but marked `invalidated_by_binding_defect`.
- The event may not be used as evidence or IF state input.
- EX-GRAMMAR-002A Stage B is blocked pending corrected Stage A geometry and human review.
- Corrected geometry will be versioned rather than overwriting the original record without trace.

This defect concerns annotation geometry only and does not support either a positive or negative manuscript-grammar claim.
