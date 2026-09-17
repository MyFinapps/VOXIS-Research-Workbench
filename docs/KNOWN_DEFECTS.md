# Known Validation Defects

## VD-001 — GK-M1 2v primitive-coordinate offset

**Discovered:** during EX-GRAMMAR-002A Stage A candidate-inventory construction  
**Affected historical bindings:** `VM.f2v.upper_stem_axis`, `VM.f2v.central_y`  
**Affected historical result:** `EX-GRAMMAR-001-R1`

Close inspection of the original `VM.f2v` source raster showed that the stored 2v stem-axis segment and central-Y point were visibly offset from the botanical structures they were intended to mark. The previous human approval is retained as a historical event, but annotation adequacy does not survive the later close audit.

### Current handling

- EX-GRAMMAR-001 R1 is retained but marked `invalidated_by_binding_defect`.
- The event may not be used as evidence or IF state input.
- Corrected Stage A geometry received human review on 2026-09-02 and was frozen under SHA-256 `735d9a58ab0305048617ffa20d99c2f86826e5863f7f0355eacd476740d810d7`.
- The canonical binding was patched explicitly as version `0.2.2`, retaining the superseded coordinates and defect provenance.
- EX-GRAMMAR-002A Stage B subsequently completed against that frozen inventory. Its result does not rehabilitate EX-GRAMMAR-001 R1.

This defect concerns annotation geometry only and does not support either a positive or negative manuscript-grammar claim.
