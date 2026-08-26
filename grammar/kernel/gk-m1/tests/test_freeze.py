import pytest

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
    with pytest.raises(ValueError, match="source_ref"):
        emit_freeze_record(
            trigger={"type": "ui"},
            capture_context=_context(),
            representation_states=[_representation_state()],
            provenance={},
        )


def test_freeze_requires_representation_state():
    with pytest.raises(ValueError, match="representation"):
        emit_freeze_record(
            trigger={"type": "ui"},
            capture_context=_context(),
            representation_states=[],
            provenance={"source_refs": ["source.voynich.f2v"]},
        )


def test_partial_capture_requires_explicit_missing_fields():
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
    with pytest.raises(ValueError, match="partial"):
        emit_freeze_record(
            trigger={"type": "ui"},
            capture_context=_context(),
            representation_states=[_representation_state()],
            provenance={"source_refs": ["source.voynich.f2v"]},
            capture_completeness="full",
            missing_fields=["camera_state"],
        )


def test_measurement_links_must_be_explicitly_classified():
    with pytest.raises(ValueError, match="measurement_linked"):
        emit_freeze_record(
            trigger={"type": "ui"},
            capture_context=_context(),
            representation_states=[_representation_state()],
            provenance={"source_refs": ["source.voynich.f2v"]},
            linked_measurement_ids=["MEAS-001"],
        )
