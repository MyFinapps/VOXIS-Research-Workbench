"""Veyu'lithra IF adapter for VOXIS Grammar Kernel GK-M0.

This adapter applies canonical relations to symbolic state. It does not invent
geometry and it does not add interpretation.
"""
from copy import deepcopy

RELATION_KEYS = {
    "ALIGN": "aligned_with",
    "POINT": "points_to",
    "OVERLAP": "overlaps",
    "COVER": "covers",
    "TERMINATE": "terminates_at",
}


def apply_event(world_state, event):
    """Apply a canonical event to symbolic IF state.

    Returns a new state plus a trace. The event itself is not mutated.
    """
    state = deepcopy(world_state)
    actor_id = event["actor"]["entity_id"]
    target_id = event["target"]["entity_id"]
    op = event["operation"]

    actor_state = state.setdefault(actor_id, {"relations": {}})
    relations = actor_state.setdefault("relations", {})
    key = RELATION_KEYS[op]

    if op in {"OVERLAP", "COVER", "TERMINATE"}:
        relations[key] = {
            "target": target_id,
            "measurements": deepcopy(event.get("measurements", {})),
        }
    else:
        relations[key] = target_id

    trace = {
        "adapter": "if",
        "event_id": event["event_id"],
        "operation": op,
        "actor": actor_id,
        "target": target_id,
        "interpretation_added": False,
    }
    return state, trace
