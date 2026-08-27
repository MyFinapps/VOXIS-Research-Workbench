from pathlib import Path
import tempfile

from workbench.freeze.desktop_poc.adapter import capture_desktop_state, persist_immutable, read_frozen


def test_capture_is_observation_not_evidence():
    record = capture_desktop_state(rotation_deg=99, opacity=0.57, anchor_x=1088, anchor_y=351, operator_note_exact="stem appears to point at dense glyph cluster")
    assert record["record_type"] == "freeze_state"
    assert record["epistemic_class"] == "observation"
    assert record["evidence_status"] == "not_evidence"
    assert record["measurement_status"] == "unmeasured"


def test_transform_and_note_round_trip():
    record = capture_desktop_state(rotation_deg=99, opacity=0.57, anchor_x=1088, anchor_y=351, operator_note_exact="stem appears to point at dense glyph cluster")
    state = record["representation_states"][1]
    native = state["transform"]["native_transform"]
    assert native["rotation_deg"] == 99.0
    assert native["anchor_xy_px"] == [1088.0, 351.0]
    assert state["opacity"] == 0.57
    assert record["operator_note_exact"] == "stem appears to point at dense glyph cluster"


def test_persistence_is_create_only():
    with tempfile.TemporaryDirectory() as td:
        record = capture_desktop_state(rotation_deg=1, opacity=0.5, anchor_x=2, anchor_y=3)
        path = persist_immutable(record, td)
        assert path.exists()
        assert read_frozen(record["freeze_id"], td) == record
        try:
            persist_immutable(record, td)
        except ValueError as exc:
            assert "immutable" in str(exc)
        else:
            raise AssertionError("duplicate FREEZE overwrote an immutable record")


def main():
    tests = [test_capture_is_observation_not_evidence, test_transform_and_note_round_trip, test_persistence_is_create_only]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"PASS all {len(tests)} desktop FREEZE adapter tests")


if __name__ == "__main__":
    main()
