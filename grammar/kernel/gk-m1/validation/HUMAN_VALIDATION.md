# GK-M1 Human Validation Worksheet

The following bindings are proposals only. Validate them against the named embedded source image.

For each item choose one outcome:

- `accept` — proposed coordinate/region is an adequate operational landmark;
- `adjust` — provide corrected pixel coordinate(s) or bbox;
- `reject` — do not use this primitive binding.

## Proposed landmarks

### 2r — Image ID 1006078, 1428 × 2000

1. `VM.f2r.root_pivot`
   - proposed pixel: `(815, 1778)`
   - normalized: `(0.570728, 0.889000)`
   - intended landmark: center of junction where lower stem enters the red root structure

2. `VM.f2r.lower_stem_axis`
   - proposed segment: `(814,1725) -> (808,1260)`
   - intended landmark: lower central stem axis, before upper branching

3. `VM.f2r.root_region`
   - proposed bbox: `(610,1710) -> (1020,1920)`
   - intended region: coarse red root structure

### 2v — Image ID 1006079, 1460 × 2000

4. `VM.f2v.central_y`
   - proposed pixel: `(855,1075)`
   - normalized: `(0.585616, 0.537500)`
   - intended landmark: central bifurcation point in the Y/stub structure

5. `VM.f2v.upper_stem_axis`
   - proposed segment: `(900,1500) -> (862,1120)`
   - intended landmark: upper long-stem axis approaching the Y/stub

### 3r — Image ID 1006080, 1428 × 2000

6. `VM.f3r.root_crown`
   - proposed pixel: `(836,1570)`
   - normalized: `(0.585434,0.785000)`
   - intended landmark: crown of the root fan where the stem enters the root region

7. `VM.f3r.root_region`
   - proposed bbox: `(520,1545) -> (1170,1940)`
   - intended region: coarse visible root fan

## Rule

Human validation confirms only that the annotation adequately marks the selected visual primitive. It does **not** confirm a cross-folio alignment, manuscript grammar, function, or meaning.
