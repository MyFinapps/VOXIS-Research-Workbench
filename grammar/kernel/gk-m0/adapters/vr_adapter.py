"""Runtime-neutral VR adapter contract for VOXIS Grammar Kernel GK-M0.

The actual WebXR/Unity runtime will replace the command emission hooks. This
module proves that the same canonical event can be converted to VR commands
without changing its epistemic or semantic content.
"""
from copy import deepcopy


def event_to_vr_command(event):
    command = {
        "adapter": "vr",
        "event_id": event["event_id"],
        "operation": event["operation"],
        "actor_entity_id": event["actor"]["entity_id"],
        "target_entity_id": event["target"]["entity_id"],
        "before_state": deepcopy(event.get("before_state", {})),
        "requested_after_state": deepcopy(event.get("after_state", {})),
        "measurements": deepcopy(event.get("measurements", {})),
        "interpretation_added": False,
    }
    return command


def measurement_contract(operation):
    contracts = {
        "ALIGN": ["axis_angle_error_deg", "landmark_residual", "tolerance"],
        "POINT": ["angular_deviation_deg", "target_distance", "tolerance"],
        "OVERLAP": ["intersection_area", "actor_overlap_fraction", "target_overlap_fraction"],
        "COVER": ["target_covered_fraction", "layer_order", "depth_separation"],
        "TERMINATE": ["endpoint_distance", "tolerance"],
    }
    return contracts[operation]
