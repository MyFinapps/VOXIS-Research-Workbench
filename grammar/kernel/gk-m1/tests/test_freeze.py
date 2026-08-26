import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from records.freeze import emit_freeze_record


def _representation_state():
    return {
        "representation_ref": "rep.voynich.f2v",
        "source_ref": "source.voynich.f2v",
        "stack_index": 1,
        "visible": True,
        "opacity": 0.6,
        "transform": {
            "coordinate_space_ref": "folio-local-mm",
            "units": "mm",
            "translation": [1.0, 2.0, 0.0],
            "rotation_quaternion_xyzw": [0.0, 0.0, 0.0, 1.0],
            "scale": [1.0, 1.0, 1.0],
            "pivot": [12.5, 84.0, 0.0],
            "pivot_rule": "operator-selected root pivot",
            "reflection": {"x": False, "y": False, "z": False},
        },
    }


def _context():
    return {
        "runtime": "desktop",
        "runtime_version": "poc",
        "mode_before": "discovery",
        "mode_after": "candidate_observation",
        "coordinate_space_ref": "folio-local-mm",
        "units": "mm",
        "camera_state": None,
        "controller_states": [],
    }


def _assert_raises(fn, contains):
    try:
        fn()
    except ValueError as exc:
        assert contains in str(exc), str(exc)
    else:
        raise AssertionError(f"expected ValueError containing {contains!r}")


def test_freeze_emits_observation_not_evidence():
    record = emit_freeze_record(
        trigger={"type": "keyboard", "raw_input": "FREEZE", "device_ref": None},
        capture_context=_context(),
        representation_states=[_representation_state()],
        provenance={"source_refs": ["source.voynich.f2v"]},
        operator_note_exact="stem appears to point at dense glyph cluster",
    )

    assert record["record_type"] == "freeze_state"
    assert record["epistemic_class"] == "observation"
    assert record["evidence_status"] == "not_evidence"
    assert record["measurement_status"] == "unmeasured"
    assert record["freeze_id"].startswith("FREEZE-")
    assert record["operator_note_exact"] == "stem appears to point at dense glyph cluster"


def test_freeze_requires_source_provenance():
    _assert_raises(
        lambda: emit_freeze_record(
            trigger={"type": "ui"},
            capture_context=_context(),
            representation_states=[_representation_state()],
            provenance={},
        ),
        "source_ref",
    )


def test_freeze_requires_representation_state():
    _assert_raises(
        lambda: emit_freeze_record(
            trigger={"type": "ui"},
            capture_context=_context(),
            representation_states=[],
            provenance={"source_refs": ["source.voynich.f2v"]},
        ),
        "representation",
    )


def test_partial_capture_is_explicit():
    record = emit_freeze_record(
        trigger={"type": "physical_log", "raw_input": "manual freeze", "device_ref": None},
        capture_context=_context(),
        representation_states=[_representation_state()],
        provenance={"source_refs": ["source.voynich.f2v"]},
        capture_completeness="partial",
        missing_fields=["camera_state", "controller_states"],
    )

    assert record["capture_completeness"] == "partial"
    assert record["missing_fields"] == ["camera_state", "controller_states"]


def test_missing_fields_cannot_masquerade_as_full_capture():
    _assert_raises(
        lambda: emit_freeze_record(
            trigger={"type": "ui"},
            capture_context=_context(),
            representation_states=[_representation_state()],
            provenance={"source_refs": ["source.voynich.f2v"]},
            capture_completeness="full",
            missing_fields=["camera_state"],
        ),
        "partial",
    )


def test_measurement_links_require_explicit_classification():
    _assert_raises(
        lambda: emit_freeze_record(
            trigger={"type": "ui"},
            capture_context=_context(),
            representation_states=[_representation_state()],
            provenance={"source_refs": ["source.voynich.f2v"]},
            linked_measurement_ids=["MEAS-001"],
        ),
        "measurement_linked",
    )


def main():
    tests = [
        test_freeze_emits_observation_not_evidence,
        test_freeze_requires_source_provenance,
        test_freeze_requires_representation_state,
        test_partial_capture_is_explicit,
        test_missing_fields_cannot_masquerade_as_full_capture,
        test_measurement_links_require_explicit_classification,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"PASS all {len(tests)} FREEZE record tests")


if __name__ == "__main__":
    main()
