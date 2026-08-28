from copy import deepcopy
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from workbench.vista.m1.adapter import capture_webxr_state, persist_immutable, read_frozen


def fixture():
    return {
        "operator": "JT",
        "operator_note_exact": "JT VISTA M1 Rosette Flight validation 01",
        "trigger_type": "xr_controller",
        "device_hint": "meta-quest-3",
        "user_agent": "Quest test harness",
        "camera_state": {"position": [0.4, 3.82, -1.1], "rotation_quaternion_xyzw": [0, 0, 0, 1]},
        "controller_states": [{"hand": "left", "position": [-0.2, 1.3, -0.4]}],
        "transform_mode": "rotate",
        "annotation_tool": "tack",
        "grid_state": {"snapEnabled": True, "snapResolution": 0.05, "snapStrength": 0.65},
        "active_group_id": "AG-test",
        "environment_state": {"theme_ref": "VISTA.theme.rosette_chamber.v0.1", "rosette_chamber_enabled": True},
        "navigation_state": {
            "flight_enabled": True,
            "rig_position_xyz_m": [0.4, 2.2, -1.1],
            "elevation_m": 2.2,
            "flight_speed_m_s": 1.25,
            "vertical_speed_m_s": 1.10,
        },
        "active_features": [
            {"feature_ref": "ANCHOR-test", "feature_type": "anchor_marker", "representation_ref": "VM.f2v.overlay"},
            {"feature_ref": "AG-test", "feature_type": "alignment_group", "representation_ref": None},
        ],
        "representation_states": [
            {"representation_ref": "VM.f2r.anchor", "visible": True, "opacity": 1.0, "transform": {"translation": [-0.7,1.55,-2.85], "rotation_quaternion_xyzw": [0,0,0,1], "scale": [0.82,0.82,0.82], "pivot": [0,0,0], "pivot_rule": "operator-set local pivot", "native_transform": {}}},
            {"representation_ref": "VM.f2v.overlay", "visible": True, "opacity": 0.47, "transform": {"translation": [0.18,1.62,-2.1], "rotation_quaternion_xyzw": [0,0,0.3173047,0.9483237], "scale": [0.83,0.83,0.83], "pivot": [0.12,-0.18,0], "pivot_rule": "operator-set local pivot", "native_transform": {"rotation_deg_xyz": [0,0,37]}}},
            {"representation_ref": "VM.f3r.overlay", "visible": True, "opacity": 0.88, "transform": {"translation": [0.82,1.55,-2.75], "rotation_quaternion_xyzw": [0,0,0,1], "scale": [0.82,0.82,0.82], "pivot": [0,0,0], "pivot_rule": "operator-set local pivot", "native_transform": {}}},
        ],
    }


def test_capture_boundary_and_spatial_context():
    record = capture_webxr_state(fixture(), created_at="2026-08-28T00:00:00Z")
    assert record["record_type"] == "freeze_state"
    assert record["epistemic_class"] == "observation"
    assert record["evidence_status"] == "not_evidence"
    assert record["measurement_status"] == "unmeasured"
    assert record["capture_context"]["runtime_version"] == "VISTA_M1_ROSETTE_FLIGHT_v0.3.0"
    assert record["capture_context"]["coordinate_space_ref"] == "VISTA.m1.world"
    assert record["capture_context"]["transform_mode"] == "rotate"
    assert record["capture_context"]["annotation_tool"] == "tack"
    assert record["capture_context"]["active_group_id"] == "AG-test"
    assert record["capture_context"]["environment_state"]["theme_ref"] == "VISTA.theme.rosette_chamber.v0.1"
    assert record["capture_context"]["environment_state"]["rosette_chamber_enabled"] is True
    assert record["capture_context"]["navigation_state"]["flight_enabled"] is True
    assert record["capture_context"]["navigation_state"]["elevation_m"] == 2.2
    assert len(record["representation_states"]) == 3
    assert record["representation_states"][1]["transform"]["pivot"] == [0.12, -0.18, 0.0]
    assert record["active_features"][0]["feature_ref"] == "ANCHOR-test"
    assert record["provenance"]["software_build_ref"] == "VISTA_M1_ROSETTE_FLIGHT_v0.3.0"


def test_live_mutation_does_not_change_frozen_record():
    payload = fixture()
    record = capture_webxr_state(payload, created_at="2026-08-28T00:00:00Z")
    before = deepcopy(record)
    payload["representation_states"][1]["opacity"] = 0.91
    payload["representation_states"][1]["transform"]["translation"][0] = 99
    payload["navigation_state"]["elevation_m"] = 11.7
    payload["environment_state"]["rosette_chamber_enabled"] = False
    payload["active_features"].append({"feature_ref": "NOTE-late"})
    assert record == before


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
            raise AssertionError("duplicate VISTA M1 FREEZE overwrote an immutable record")


def main():
    tests = [test_capture_boundary_and_spatial_context, test_live_mutation_does_not_change_frozen_record, test_persistence_is_create_only_and_round_trips]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"PASS all {len(tests)} VISTA M1 Rosette/flight adapter tests")


if __name__ == "__main__":
    main()
