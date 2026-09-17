# EX-GRAMMAR-002A — Within-folio Opportunity Test for STEM → POINT → Y on VM.f2v

**Status:** PREDECLARED — candidate inventory not yet frozen; relation measurements not yet run  
**Parent milestone:** GK-M1  
**Prior selected case:** EX-GRAMMAR-001  
**Primary source:** `VM.f2v` / Image ID `1006079`  
**Epistemic target:** measurement; limited within-folio distinctiveness inference only after candidate-set freeze and measurement  

## 1. Purpose

EX-GRAMMAR-001 measured one previously noticed relationship on folio 2v: the validated upper stem axis passes close to the validated central Y landmark. Because that case was noticed before preregistration, it is a **hypothesis-informed selected case** and cannot by itself establish that the relation is distinctive, recurrent, grammatical, functional, or meaningful.

EX-GRAMMAR-002A tests the narrower question:

> Within folio `VM.f2v`, how unusual is the EX-GRAMMAR-001 STEM → POINT → Y geometry relative to the complete preregistered set of eligible stem/Y opportunities under the same source geometry and measurement method?

This experiment is intended to distinguish a visually compelling selected example from the background opportunity structure of the same folio.

## 2. Research question

Among all eligible stem axes and eligible Y-junction targets identified on `VM.f2v` before pairwise relation measurement, where does the EX-GRAMMAR-001 actor/target pair rank by:

1. target-to-forward-axis distance;
2. angular deviation;
3. qualification under the preregistered POINT tolerance?

## 3. Source scope

The experiment is restricted to:

- `VM.f2v`
- original embedded source raster used by GK-M1
- Image ID `1006079`
- source dimensions `1460 × 2000`
- source SHA-256 as recorded by GK-M1

No other folios may be added to this experiment after preregistration. Cross-folio replication belongs in a separate experiment.

## 4. Relation under test

Canonical relation:

`STEM → POINT → Y`

The deterministic measurement implementation is:

`grammar/kernel/gk-m1/measurement/geometry.py::measure_point`

The method reports:

- `angular_deviation_deg`
- `target_distance`
- preregistered `tolerance`

No semantic label may be emitted by the measurement layer.

## 5. Transform policy

All measurements use the unmodified source geometry.

Allowed transform:

- identity only

Explicitly prohibited:

- translation
- rotation
- horizontal flip
- vertical flip
- uniform scale other than 1.0
- nonuniform scale
- warp
- perspective correction
- local deformation
- post-hoc pivot changes

The purpose of 002A is not to search transform space. It is to test the opportunity structure already present in the source folio.

## 6. Candidate inventory must be frozen before relation measurement

The experiment has two stages.

### Stage A — candidate inventory

All eligible STEM actors and Y targets are enumerated and geometrically annotated while pairwise POINT results are unavailable to the annotator/operator.

The candidate inventory must be committed as a versioned file and hashed before Stage B begins.

### Stage B — pairwise measurement

Only after the candidate inventory is frozen may the system compute the complete actor × target opportunity matrix.

No actor or target may be added, removed, moved, or reclassified after the first pairwise POINT result is generated. Any required change after measurement begins terminates the current run and requires a new amended experiment identifier/version with the deviation recorded.

## 7. STEM eligibility rule

A candidate is eligible as a `STEM` actor if all of the following are satisfied during Stage A:

1. It is a visually identifiable elongated botanical stem-like structure on `VM.f2v`.
2. A principal longitudinal direction can be represented reproducibly by a two-point segment without using any Y-target geometry to choose that direction.
3. The chosen segment follows the visible central direction of the stem section rather than being aimed toward a target after inspection of target locations.
4. The segment is bounded by visible structural endpoints, junctions, or a reproducibly declared stem section.
5. Tiny decorative spurs, isolated marks, uncertain bleed-through, and glyph strokes are excluded.
6. Ambiguous cases are not silently discarded: they must be listed in an inventory exclusion table with a brief reason.

The existing `VM.f2v.upper_stem_axis` is not automatically privileged. It must satisfy the same rule and appears in the final opportunity matrix only if it remains eligible under this preregistration.

## 8. Y eligibility rule

A candidate is eligible as a `Y` target if all of the following are satisfied during Stage A:

1. It is a visible botanical fork/junction on `VM.f2v` with a recognizable Y-like branch split.
2. The junction center can be represented reproducibly by a single point.
3. The point is placed at the visual branch junction, not shifted to improve a relation score.
4. Glyph Ys, ambiguous bleed-through marks, tiny decorative bifurcations, and severely occluded/indeterminate junctions are excluded.
5. Ambiguous cases must be recorded in the inventory exclusion table with a brief reason.

The existing `VM.f2v.central_y` is not automatically privileged. It must satisfy the same rule and appears in the final opportunity matrix only if it remains eligible under this preregistration.

## 9. Blindness / information-control rule during inventory

During Stage A, the inventory interface or workflow must not display:

- actor-to-target guide lines;
- angular deviations;
- distances to Ys;
- tolerance pass/fail indicators;
- nearest-target ranking;
- EX-GRAMMAR-001 score overlays.

The operator may know that EX-GRAMMAR-001 exists; complete blinding is impossible because the relation motivated this experiment. The purpose of this rule is narrower: prevent numerical pairwise results from influencing candidate inclusion or annotation placement.

## 10. Human validation gate

Before Stage B, the frozen candidate inventory must receive human review at the level of annotation adequacy only.

For each candidate or exclusion, the human operator may:

- `accept`
- `adjust`
- `reject`

All adjustments occur before pairwise relation measurement.

Human approval does not validate a relation or grammar claim. It validates only that the candidate inventory adequately represents the declared eligible visual primitives.

## 11. Opportunity set

After the candidate inventory is frozen and human-reviewed, define the opportunity set as the Cartesian product:

`all eligible STEM actors × all eligible Y targets`

Every pair is measured. No pair may be omitted because it appears visually implausible, redundant, weak, strong, or uninteresting.

If there are `S` eligible stems and `Y` eligible targets, the primary opportunity table contains exactly `S × Y` rows.

## 12. Primary tolerance

For continuity with EX-GRAMMAR-001:

`target_distance <= 0.03 normalized source units`

is the preregistered distance threshold for a qualifying POINT opportunity.

The raw continuous distance and angular deviation are always retained. The threshold does not replace the underlying measurements.

No threshold may be changed after Stage B begins.

## 13. Primary outputs

### 13.1 Complete opportunity table

For every eligible actor/target pair record:

- actor ID
- target ID
- source reference
- transform record
- `angular_deviation_deg`
- `target_distance`
- tolerance
- `qualifies_distance` boolean
- method reference
- candidate-inventory hash
- provenance

### 13.2 Per-STEM summary

For each eligible stem record:

- nearest eligible Y by `target_distance`
- second-nearest eligible Y, if present
- minimum target distance
- angular deviation to nearest Y
- count and fraction of eligible Ys satisfying the distance threshold

### 13.3 EX-GRAMMAR-001 index-case summary

If both original primitives remain eligible, record:

- its distance rank among all stem/Y opportunities;
- percentile rank within all opportunities;
- its rank among targets for its own stem;
- difference between its distance and the next-best Y for the same stem;
- whether it satisfies the preregistered tolerance.

If either original primitive fails the preregistered eligibility rule, that fact is itself retained as a result and the index-case ranking is reported as `not_applicable`; the object is not force-included.

## 14. Descriptive statistics

The run will report at minimum:

- number of eligible stems `S`;
- number of eligible Ys `Y`;
- total opportunities `S × Y`;
- minimum, median, mean, and maximum `target_distance`;
- distribution of `angular_deviation_deg`;
- number and fraction of opportunities satisfying the distance tolerance;
- per-stem nearest-Y distances;
- EX-GRAMMAR-001 rank if applicable.

Because the candidate set is a structured within-folio opportunity set rather than an independent random sample, these descriptive summaries must not be misrepresented as a conventional population-significance test.

## 15. Primary decision language

The experiment uses descriptive/inferential language rather than binary proof language.

### If the EX-GRAMMAR-001 case ranks strongly

Permitted wording:

> Within the preregistered `VM.f2v` opportunity set, the EX-GRAMMAR-001 STEM → POINT → Y case is geometrically distinctive relative to the other eligible stem/Y opportunities under the declared identity-transform measurement.

The degree of distinctiveness must be reported numerically.

### If many opportunities are comparable

Permitted wording:

> Within the preregistered `VM.f2v` opportunity set, the EX-GRAMMAR-001 case is not strongly distinctive; comparable STEM → POINT → Y geometry occurs elsewhere under the same criteria.

### If the original case is ineligible under the frozen rules

Permitted wording:

> The previously selected EX-GRAMMAR-001 case does not survive the preregistered primitive-eligibility rule and is not used for opportunity ranking in EX-GRAMMAR-002A.

## 16. Claims explicitly prohibited

Regardless of outcome, EX-GRAMMAR-002A alone may not establish or state as fact:

- that the Voynich Manuscript has a STEM → Y grammar rule;
- that a repeated relation is intentional;
- that 2v is a machine, instruction, process, map, or encoded mechanism;
- that a STEM transmits anything;
- that a Y receives, activates, injects, grounds, or routes anything;
- that the relation generalizes beyond `VM.f2v`;
- that geometric distinctiveness proves manuscript correspondence or meaning.

Interpretive terms may be discussed in a separately labeled interpretation/hypothesis layer, but may not be written into the measurement result.

## 17. Null and negative-result policy

All opportunities are retained, including:

- weak alignments;
- large distances;
- high angular deviations;
- non-qualifying pairs;
- candidate exclusions;
- failed human-validation candidates;
- cases that undermine the motivating hypothesis.

A null or negative result is a successful experimental outcome if the procedure was executed as preregistered.

## 18. Deviations and amendments

Any material change to:

- source scope;
- eligibility rules;
- transform policy;
- measurement method;
- tolerance;
- candidate inventory after pairwise measurement begins;
- ranking method;
- primary decision language;

must be recorded as a deviation.

If the change could reasonably affect results, the current run is frozen and a new version/experiment identifier must be created rather than silently overwriting the preregistration.

## 19. Relationship to EX-GRAMMAR-001

EX-GRAMMAR-001 remains a selected, hypothesis-informed pipeline result.

EX-GRAMMAR-002A does not retroactively convert EX-GRAMMAR-001 into an unbiased discovery. It supplies a preregistered within-folio comparison frame for assessing the selected case.

## 20. Relationship to VR and Veyu'lithra IF

After measurement, the same canonical event records may be rendered by both runtimes.

### VR

May display:

- frozen primitive annotations;
- measured axis/target geometry;
- raw distances and angles;
- opportunity ranking;
- null/counterexample opportunities.

### Veyu'lithra IF

May preserve the same actor, relation, target, measurement payload, and provenance as symbolic state input.

No narrative consequence is inferred merely because a POINT relation is measured. IF prose remains a rendering layer, not manuscript evidence.

## 21. Promotion rule

EX-GRAMMAR-002A may support only a limited within-folio distinctiveness inference after:

1. this preregistration is committed;
2. the candidate inventory is completed without pairwise-result feedback;
3. the candidate inventory is human-reviewed and frozen;
4. its hash is recorded;
5. the complete opportunity matrix is measured deterministically;
6. outputs are retained without deleting nulls or counterexamples;
7. the result is reviewed with the selection-bias boundary intact.

A manuscript-wide grammar inference requires separate cross-folio replication and control experiments.

## 22. Planned next experiment

If EX-GRAMMAR-002A completes successfully as an instrument/process test, the intended next step is a separately preregistered cross-folio replication/control experiment. Its candidate scope and rules must be frozen independently rather than inherited after examining favorable 002A results.

---

## Preregistration statement

This document is intentionally committed **before candidate enumeration is frozen and before any EX-GRAMMAR-002A pairwise STEM → POINT → Y relation measurement is performed**.

The motivating EX-GRAMMAR-001 measurement is already known and is explicitly treated as a selected index case rather than a discovery-neutral observation.
