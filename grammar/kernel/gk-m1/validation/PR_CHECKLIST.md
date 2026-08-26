# GK-M1 PR Checklist

- [x] Source raster identity, dimensions, xrefs, and hashes recorded
- [x] Human operator reviewed the validation pack
- [x] All 7 proposed manuscript annotations accepted
- [x] Binding/entity statuses promoted to `human_validated`
- [x] Deterministic 2-D transform and relation measurements implemented
- [x] Observation / Search Session / Alignment Candidate emitters implemented
- [x] Unvalidated primitive bindings are blocked from Alignment Candidate emission
- [x] 14-test deterministic regression suite passes after validation
- [x] Semantic leakage guard test passes
- [x] Repeatable GitHub Actions CI is installed and final verification run passed
- [x] Validated milestone SHA-256 manifest refreshed
- [x] Documentation preserves the observation/measurement/inference/interpretation boundary

## Next experimental gate — not a GK-M1 merge blocker

- [ ] Predeclare the first manuscript-bound Search Session before relation measurement
- [ ] Add manuscript-bound relation example(s) only from that recorded Search Session

Human validation confirms annotation adequacy only; it does not establish correspondence, grammar, procedure, intent, or meaning.
