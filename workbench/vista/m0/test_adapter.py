from copy import deepcopy
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from workbench.vista.m0.adapter import capture_webxr_state, persist_immutable, read_frozen


def fixture():
    return {
        "operator": "JT",
        "operator_note_exact": "JT VISTA M0 validation 01",
        "trigger_type": "xr_controller",
        "device_hint": "meta-quest-3",
        "user_agent": "Quest test harness",
        "camera_state": {"position": [0, 1.6, 0], "rotation_quaternion_xyzw": [0, 0, 0, 1]},
        "controller_states": [{"hand": "left", "position": [-0.2, 1.3, -0.4]}],
        "representation_states": [
            {
                "representation_ref": "VM.f2r.anchor", "visible": True, "opacity": 1.0,
                "transform": {"translation": [0, 1.5, -2.4], "rotation_quaternion_xyzw": [0, 0, 0, 1], "scale": [1, 1, 1], "pivot": [0, 0, 0], "pivot_rule": None, "native_transform": {"rotation_deg_xyz": [0,0,0]}},
            },
            {
                "representation_ref": "VM.f2v.overlay", "visible": True, "opacity": 0.47,
                "transform": {"translation": [0.18, 1.62, -2.1], "rotation_quaternion_xyzw": [0, 0, 0.3173047, 0.9483237], "scale": [0.83, 0.83, 0.83], "pivot": [0.12, -0.18, 0], "pivot_rule": "operator-set local pivot", "native_transform": {"rotation_deg_xyz": [0,0,37], "pivot_local_xyz_m": [0.12, -0.18, 0]}},
            },
        ],
    }


def test_capture_boundary_and_runtime():
    record = capture_webxr_state(fixture(), created_at="2026-08-27T01:50:00Z")
    assert record["record_type"] == "freeze_state"
    assert record["epistemic_class"] == "observation"
    assert record["evidence_status"] == "not_evidence"
    assert record["measurement_status"] == "unmeasured"
    assert record["capture_context"]["runtime"] == "webxr"
    assert record["capture_context"]["runtime_version"] == "VISTA_M0_FIRST_PRESENCE_v0.1.1"
    assert record["capture_context"]["coordinate_space_ref"] == "VISTA.m0.world"
    assert record["operator_note_exact"] == "JT VISTA M0 validation 01"


def test_operator_set_pivot_round_trips():
    record = capture_webxr_state(fixture())
    state = record["representation_states"][1]
    assert state["transform"]["pivot"] == [0.12, -0.18, 0.0]
    assert state["transform"]["pivot_rule"] == "operator-set local pivot"
    assert record["active_features"][0]["feature_ref"] == "VISTA.m0.overlay_pivot"
    assert record["provenance"]["software_build_ref"] == "VISTA_M0_FIRST_PRESENCE_v0.1.1"


def test_live_mutation_does_not_change_frozen_record():
    payload = fixture()
    record = capture_webxr_state(payload, created_at="2026-08-27T01:50:00Z")
    before = deepcopy(record)
    payload["representation_states"][1]["opacity"] = 0.91
    payload["representation_states"][1]["transform"]["translation"][0] = 99
    payload["representation_states"][1]["transform"]["pivot"][0] = -99
    assert record == before
    assert record["representation_states"][1]["opacity"] == 0.47


def test_persistence_is_create_only_and_round_trips():
    record = capture_webxr_state(fixture())
    with tempfile.TemporaryDirectory() as td:
        path = persist_immutable(record, td)
        assert path.exists()
        assert read_frozen(record["freeze_id"], td) == record
        try:
            persist_immutable(record, td)
        except ValueError as exc:
            assert "immutable" in str(exc)
        else:
            raise AssertionError("duplicate VISTA FREEZE overwrote an immutable record")


def main():
    tests = [
        test_capture_boundary_and_runtime,
        test_operator_set_pivot_round_trips,
        test_live_mutation_does_not_change_frozen_record,
        test_persistence_is_create_only_and_round_trips,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"PASS all {len(tests)} VISTA M0 adapter tests")


if __name__ == "__main__":
    main()
