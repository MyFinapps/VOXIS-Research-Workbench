# GK-M1 Provenance

## Source

Project PDF: `Manuscript-voynich-manuscript-v1.0-3.pdf`

The bindings use the original embedded rasters extracted from the PDF pages for 2r, 2v, and 3r.

| Folio | PDF page | Image ID | PDF image xref | Embedded raster | SHA-256 |
|---|---:|---:|---:|---:|---|
| 2r | 5 | 1006078 | 882 | 1428 × 2000 | `8d307234d0eeb4ddad54aaad68beb9f145d5be052afac1ac5ab2b5c26071a451` |
| 2v | 6 | 1006079 | 885 | 1460 × 2000 | `df73d9f9e37285ea5d3e8627dd71a81854bf0ecc84362b8a059316e26b49215a` |
| 3r | 7 | 1006080 | 888 | 1428 × 2000 | `75e9400c2c3e149465c21d238712f551845e1d5e9e3737d4dbf211af47055963` |

The full manuscript PDF and high-resolution research imagery are not stored in the public engineering repository.

## Annotation method

Initial coordinates were visually selected from the extracted embedded rasters using normalized grid and pixel-grid inspection. Both source-pixel and normalized geometry are retained for reproducibility.

## Human validation event

- validation pack: `GK_M1_validation_pack.zip` (local research artifact; not committed to the public repository)
- decision: **all seven seed annotations accepted**
- recorded at: `2026-08-26T04:09:45Z`
- validator role: human operator
- scope: operational annotation adequacy only

This validation event does **not** establish cross-folio correspondence, recurring grammar, procedure, manuscript intent, or meaning.

## Verification

- deterministic regression suite: **14/14 pass**
- final GitHub Actions verification run prior to provenance closeout: `32929554439`
- CI verifies both deterministic tests and the milestone SHA-256 manifest

## Epistemic classification

- Source-image identity and dimensions: **measurement / provenance**
- Seed primitive locations: **human-validated operational annotations**
- Geometry functions: **deterministic measurement method**
- Geometric relation/alignment: **requires a separate predeclared Search Session and measurement**
- Interpretation: **separate layer**
- Manuscript-wide procedural grammar: **not established by GK-M1**
