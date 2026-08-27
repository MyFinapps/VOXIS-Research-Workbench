"""WebXR -> canonical VOXIS FREEZE adapter for VISTA M0."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import json
import re

from workbench.freeze.record import emit_freeze_record

FREEZE_ID_RE = re.compile(r"^FREEZE-[A-Za-z0-9._:-]+$")
PAIR = (
    ("VM.f2r.anchor", "F2R", 0),
    ("VM.f2v.overlay", "F2V", 1),
)


def _vec(value, n, label):
    if not isinstance(value, list) or len(value) != n:
        raise ValueError(f"{label} must have {n} numeric values")
    return [float(x) for x in value]


def _representation_state(raw, expected_ref, source_ref, stack_index):
    if raw.get("representation_ref") != expected_ref:
        raise ValueError(f"expected representation_ref {expected_ref}")
    transform = raw.get("transform") or {}
    return {
        "representation_ref": expected_ref,
        "source_ref": source_ref,
        "stack_index": stack_index,
        "visible": bool(raw.get("visible", True)),
        "opacity": float(raw.get("opacity", 1.0)),
        "transform": {
            "coordinate_space_ref": "VISTA.m0.world",
            "units": "m",
            "translation": _vec(transform.get("translation"), 3, "translation"),
            "rotation_quaternion_xyzw": _vec(transform.get("rotation_quaternion_xyzw"), 4, "rotation quaternion"),
            "scale": _vec(transform.get("scale"), 3, "scale"),
            "pivot": _vec(transform.get("pivot", [0, 0, 0]), 3, "pivot"),
            "pivot_rule": transform.get("pivot_rule"),
            "reflection": {"x": False, "y": False, "z": False},
            "native_transform": deepcopy(transform.get("native_transform") or {}),
        },
    }


def capture_webxr_state(payload, *, created_at=None):
    states_raw = payload.get("representation_states") or []
    if len(states_raw) != 2:
        raise ValueError("VISTA M0 requires exactly two representation states")
    states = [
        _representation_state(raw, ref, source, index)
        for raw, (ref, source, index) in zip(states_raw, PAIR)
    ]
    opacity = states[1]["opacity"]
    if not 0.0 <= opacity <= 1.0:
        raise ValueError("overlay opacity must be between 0 and 1")

    controller_states = deepcopy(payload.get("controller_states") or [])
    camera_state = deepcopy(payload.get("camera_state"))
    user_agent = str(payload.get("user_agent") or "")[:500]
    device_hint = str(payload.get("device_hint") or "webxr-headset")[:120]
    trigger_type = str(payload.get("trigger_type") or "xr_controller")[:80]

    return emit_freeze_record(
        trigger={"type": trigger_type, "raw_input": "FREEZE", "device_ref": device_hint},
        capture_context={
            "runtime": "webxr",
            "runtime_version": "VISTA_M0_FIRST_PRESENCE_v0.1",
            "mode_before": "discovery",
            "mode_after": "candidate_observation",
            "coordinate_space_ref": "VISTA.m0.world",
            "units": "m",
            "camera_state": camera_state,
            "controller_states": controller_states,
            "user_agent": user_agent,
        },
        representation_states=states,
        provenance={
            "source_refs": ["F2R", "F2V"],
            "representation_refs": ["VM.f2r.anchor", "VM.f2v.overlay"],
            "software_build_ref": "VISTA_M0_FIRST_PRESENCE_v0.1",
            "device_refs": [device_hint],
            "research_boundary": "Geometric fit is a research aid, not proof of manuscript correspondence.",
        },
        operator=str(payload.get("operator") or "JT")[:120],
        operator_note_exact=payload.get("operator_note_exact"),
        active_features=[{
            "feature_ref": "VISTA.m0.overlay_center_pivot",
            "feature_type": "pivot",
            "representation_ref": "VM.f2v.overlay",
            "operator_label": "M0 center pivot",
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


def latest_frozen(directory):
    directory = Path(directory)
    files = sorted(directory.glob("FREEZE-*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        return None
    return json.loads(files[0].read_text(encoding="utf-8"))
