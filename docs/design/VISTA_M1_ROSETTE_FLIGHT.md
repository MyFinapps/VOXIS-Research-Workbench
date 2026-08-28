# VISTA M1 - Rosette Chamber & Freeflight

Status: implementation experiment / target-device validation pending

## Purpose

Add an evocative Rosette-inspired environment and deliberate 3D locomotion to VISTA without contaminating research geometry or epistemic status.

## Research boundary

- The Rosette Chamber is an interface/environment theme inspired by the visual logic of the Voynich rosette foldout.
- It is **not** a claim that the foldout depicts a physical room, machine, map, cosmology, or intended VR-like workspace.
- Geometric fit remains a research aid, not proof of manuscript correspondence.
- Viewpoint, altitude, room styling, and bay location are runtime context; they do not promote an observation to evidence.

## Separation rule

**Instrument state and environment theme remain independent.**

The following canonical research state must remain unchanged whether the Rosette theme is visible or hidden:

- folio source/representation identity;
- translation, rotation, scale, and pivot;
- multidimensional grid/snap settings;
- anchors/thumbtacks;
- yarn/relation links;
- exact-wording notes;
- Alignment Group membership/internal geometry;
- locks;
- FREEZE epistemic classification.

Theme reference: `VISTA.theme.rosette_chamber.v0.1`.

## Spatial mnemonic

Eight bays surround the central FREEZE Nexus:

1. Observation - notice / mark / capture.
2. Alignment - pivots / grids / groups.
3. Measurement - distance / angle / stability.
4. Grammar - candidate pattern families.
5. Review - replay / compare / revisit.
6. Archive - provenance / retrieval / export.
7. Experiment - controls / randomization.
8. Constellation - multi-group spatial relations.

These are workflow landmarks only. Entering a bay does not change the epistemic class of a record.

## FREEZE Nexus

The central hub remains the explicit transition:

`Live discovery -> FREEZE -> Candidate Observation`

FREEZE preserves the resolved research state plus runtime viewpoint/environment context. It does not convert styling, navigation, or spatial intuition into evidence.

## Freeflight rationale

Freeflight supports inspection of:

- stacked folios from above or below;
- stack/depth planes;
- 3D yarn links;
- Alignment Groups as spatial wholes;
- constellation-scale organization of multiple discoveries.

Flight is a **navigation mode**, not a transform mode.

## Freeflight interaction contract

Research mode and Freeflight are mutually exclusive controller postures.

While Freeflight is active:

- left thumbstick moves forward/back and strafes;
- left trigger ascends;
- left grip descends;
- right grip enables precision/slow flight;
- A/B adjust flight speed;
- right-stick press returns to floor elevation;
- left-stick press exits Freeflight;
- folio grabbing/manipulation and annotation-tool actions are suspended;
- Y/grid visibility and X/FREEZE remain available.

Altitude is held when vertical input is absent and clamped to the chamber operating range.

## FREEZE runtime context

The WebXR adapter accepts and immutably snapshots:

- `environment_state.theme_ref`;
- `environment_state.rosette_chamber_enabled`;
- `navigation_state.flight_enabled`;
- `navigation_state.rig_position_xyz_m`;
- `navigation_state.elevation_m`;
- `navigation_state.flight_speed_m_s`;
- `navigation_state.vertical_speed_m_s`.

These fields are runtime/provenance context and remain separate from representation geometry.

## Engine routing

- VR Interaction Engine owns ground/freeflight intent, controller input, and comfort/precision behavior.
- Alignment Engine owns folio/group geometry, pivots, grids, snap, and locks.
- Observation & Evidence Engine owns exact wording and observation record classification.
- FREEZE snapshots the resolved state and runtime context.
- Grammar/Harmonic/Experiment engines may later reference immutable IDs; they do not rewrite the frozen state.

## Validation ladder

1. Designed - complete.
2. Implemented - local standalone v0.3.0 vertical slice complete.
3. Contract-tested - local deterministic adapter and interaction tests pass.
4. Desktop-rendered - pending full A-Frame runtime in a supported visual browser environment.
5. Quest-observed - pending operator test on Meta Quest 3.
6. Quest-verified - requires successful flight/manipulation separation plus FREEZE/readback validation.

## Target-device validation

Minimum Quest pass:

1. Enter Rosette Chamber and verify bays/causeways are spatially legible.
2. Toggle Freeflight with left-stick press.
3. Ascend with left trigger, release, and confirm altitude hold.
4. Move/strafe at elevation.
5. Hold right grip and confirm slower precision flight.
6. While flying, verify right trigger does not grab a folio and left trigger does not place a pivot/annotation.
7. Return to floor with right-stick press.
8. Exit Freeflight and confirm research controls resume.
9. FREEZE from a non-zero flight elevation and read the record back externally.
10. Confirm environment/navigation context, transforms, note wording, provenance, and `observation / not_evidence` survive exactly.
