"""Desktop Alignment Engine adapter for the canonical VOXIS FREEZE record.

This module converts the current manual-overlay UI state into the shared
``freeze_state`` object. It intentionally does not measure the geometry or
promote a visual configuration to evidence.
"""
from __future__ import annotations

from pathlib import Path
import json
import math
import re

from workbench.freeze.record import emit_freeze_record

SOURCE_PIVOT = (867.0, 1041.0)
FIXED_SCALE = 0.46123348
FREEZE_ID_RE = re.compile(r"^FREEZE-[A-Za-z0-9._:-]+$")


def rotation_quaternion_z(degrees):
    half = math.radians(float(degrees)) / 2.0
    return [0.0, 0.0, math.sin(half), math.cos(half)]


def capture_desktop_state(*, rotation_deg, opacity, anchor_x, anchor_y, operator_note_exact=None, trigger_type="ui", created_at=None):
    if not 0.0 <= float(opacity) <= 1.0:
        raise ValueError("opacity must be between 0 and 1")

    representation_states = [
        {
            "representation_ref": "VM.ROS.background",
            "source_ref": "ROS",
            "stack_index": 0,
            "visible": True,
            "opacity": 1.0,
            "transform": {
                "coordinate_space_ref": "ROS.pixel",
                "units": "px",
                "translation": [0.0, 0.0, 0.0],
                "rotation_quaternion_xyzw": [0.0, 0.0, 0.0, 1.0],
                "scale": [1.0, 1.0, 1.0],
                "pivot": [0.0, 0.0, 0.0],
                "pivot_rule": None,
                "reflection": {"x": False, "y": False, "z": False},
                "native_transform": {"role": "target-background"},
            },
        },
        {
            "representation_ref": "VM.f2v.overlay",
            "source_ref": "F2V",
            "stack_index": 1,
            "visible": True,
            "opacity": float(opacity),
            "transform": {
                "coordinate_space_ref": "ROS.pixel",
                "units": "px",
                "translation": [float(anchor_x), float(anchor_y), 0.0],
                "rotation_quaternion_xyzw": rotation_quaternion_z(rotation_deg),
                "scale": [FIXED_SCALE, FIXED_SCALE, 1.0],
                "pivot": [SOURCE_PIVOT[0], SOURCE_PIVOT[1], 0.0],
                "pivot_rule": "operational 2v Y pivot; validation pending",
                "reflection": {"x": False, "y": False, "z": False},
                "native_transform": {
                    "rotation_deg": float(rotation_deg),
                    "anchor_xy_px": [float(anchor_x), float(anchor_y)],
                    "source_pivot_xy_px": list(SOURCE_PIVOT),
                    "fixed_scale": FIXED_SCALE,
                },
            },
        },
    ]

    return emit_freeze_record(
        trigger={"type": trigger_type, "raw_input": "FREEZE", "device_ref": "desktop-ui"},
        capture_context={
            "runtime": "desktop",
            "runtime_version": "M1_FREEZE_POC_v0.1",
            "mode_before": "discovery",
            "mode_after": "candidate_observation",
            "coordinate_space_ref": "ROS.pixel",
            "units": "px",
            "camera_state": None,
            "controller_states": [],
        },
        representation_states=representation_states,
        provenance={
            "source_refs": ["F2V", "ROS"],
            "representation_refs": ["VM.f2v.overlay", "VM.ROS.background"],
            "software_build_ref": "VOXIS_Research_Workbench_M1_FREEZE_POC_v0.1",
            "device_refs": ["desktop-ui"],
            "research_boundary": "Geometric fit is a research aid, not proof of manuscript correspondence.",
        },
        operator_note_exact=operator_note_exact,
        active_features=[{
            "feature_ref": "VM.f2v.operational_y_pivot",
            "feature_type": "pivot",
            "representation_ref": "VM.f2v.overlay",
            "operator_label": "2v Y pivot",
        }],
        created_at=created_at,
    )


def persist_immutable(record, directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    freeze_id = record.get("freeze_id", "")
    if not FREEZE_ID_RE.fullmatch(freeze_id):
        raise ValueError("invalid freeze_id")
    path = directory / f"{freeze_id}.json"
    payload = json.dumps(record, indent=2, ensure_ascii=False) + "\n"
    try:
        with path.open("x", encoding="utf-8") as handle:
            handle.write(payload)
    except FileExistsError as exc:
        raise ValueError("freeze record is immutable and already exists") from exc
    return path


def read_frozen(freeze_id, directory):
    if not FREEZE_ID_RE.fullmatch(freeze_id):
        raise ValueError("invalid freeze_id")
    path = Path(directory) / f"{freeze_id}.json"
    if not path.exists():
        raise FileNotFoundError(freeze_id)
    return json.loads(path.read_text(encoding="utf-8"))
