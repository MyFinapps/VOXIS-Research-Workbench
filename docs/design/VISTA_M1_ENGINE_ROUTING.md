# VISTA M1 - Engine Routing Contract

## Principle

VISTA hosts interaction and research state. Engines exchange intent, identifiers, and immutable records. No downstream analytical engine silently changes the original geometry or operator observation.

## Runtime flow

1. Operator input arrives from the **VR Interaction Engine**.
2. The **Alignment Engine** resolves locks, transform mode, grids/snapping, pivot/group frame, and resulting geometry.
3. Spatial observations are emitted through the **Observation & Evidence Engine** as immutable anchor, note, and link records.
4. `FREEZE` captures the fully resolved state plus references to active spatial records and Alignment Group state.
5. Later engines consume those references:
   - **Geometry Grammar Engine** -> candidate recurring relations or predictions;
   - **Harmonic Registration Engine** -> quantitative stability or fit measurements;
   - **Experiment Engine** -> controls, randomization, and reproducibility;
   - interpretation layers -> separately labeled meaning/context hypotheses.
6. Results link back to the original IDs. They do not overwrite them.

## Conceptual interaction intent

```json
{
  "intent": "rotate",
  "target_ref": "VM.f2v.overlay",
  "group_ref": "AG-...",
  "input_axis": "x",
  "precision": true
}
```

## Conceptual alignment resolution

```json
{
  "target_ref": "VM.f2v.overlay",
  "coordinate_space_ref": "VISTA.m1.world",
  "resolved_transform": {},
  "constraints_applied": [
    "rotation_mode",
    "angle_snap_5deg",
    "group_rotation_lock=false"
  ]
}
```

## Spatial record identifiers

- `ANCHOR-*` - thumbtack / landmark
- `NOTE-*` - exact operator wording
- `LINK-*` - yarn / declared candidate relation
- `AG-*` - versioned Alignment Group structure
- `FREEZE-*` - immutable Candidate Observation state

## Epistemic rule

A link may carry the relation label `aligned_with`, but that label records the operator's declared candidate relation. It is not a measurement that the items are aligned. Quantitative confirmation belongs in a separate measurement record referencing the LINK and/or FREEZE identifiers.
