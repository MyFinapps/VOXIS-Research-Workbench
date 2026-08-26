# GK-M1 Shared Runtime Contract

VR and Veyu'lithra IF consume the **same canonical grammar event**.

## VR responsibility

- present bound primitives and explicit transforms;
- let the operator manipulate source objects;
- invoke deterministic measurement functions on the post-transform geometry;
- display measured relations separately from interpretation;
- save the original transform and measurements.

VR must not silently promote a proposed primitive to `human_validated`.

## IF responsibility

- apply the canonical relation to symbolic world state;
- preserve the event ID, actor, target, operation, measurement payload, and epistemic entries;
- render prose separately from the event record.

IF prose is a rendering of an event/state transition, not manuscript evidence.

## Shared prohibition

Neither runtime may automatically convert a geometric relation into semantic terms such as transmitter, receiver, injection, receptacle, earth/dirt, activation, or grounding.
