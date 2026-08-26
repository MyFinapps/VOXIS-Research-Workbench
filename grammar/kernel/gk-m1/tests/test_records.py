import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from records.emitters import (
    ValidationGateError,
    emit_alignment_candidate,
    emit_observation_record,
    emit_search_session_record,
)


def test_observation_preserves_exact_wording():
    wording = "this enters that"
    rec = emit_observation_record(source_refs=["VM.f2r", "VM.f2v"], exact_wording=wording, operator="human")
    assert rec["exact_wording"] == wording
    assert rec["epistemic_class"] == "observation"


def test_search_session_predeclares_scope():
    rec = emit_search_session_record(
        source_refs=["VM.f2r", "VM.f2v"],
        declared_primitives=["ROOT", "Y"],
        declared_relations=["ALIGN"],
        allowed_transforms={"rotate": True, "uniform_scale": True, "flip_h": False},
    )
    assert rec["declared_relations"] == ["ALIGN"]
    assert rec["status"] == "open"


def test_alignment_candidate_rejects_unvalidated_binding():
    proposed = {"entity_id": "VM.f2v.central_y", "annotation_status": "proposed_pending_human_validation"}
    validated = {"entity_id": "VM.f2r.root_pivot", "annotation_status": "human_validated"}
    try:
        emit_alignment_candidate(
            search_session_id="SEARCH-test",
            actor=proposed,
            target=validated,
            operation="ALIGN",
            transform={"rotation_deg": 0},
            measurements={"landmark_residual": 0.01},
            method_ref="gk-m1.measure_align",
        )
    except ValidationGateError:
        pass
    else:
        raise AssertionError("unvalidated primitive was allowed to become an alignment candidate")


def test_alignment_candidate_contains_no_correspondence_claim():
    a = {"entity_id": "A", "annotation_status": "human_validated"}
    b = {"entity_id": "B", "annotation_status": "measured"}
    rec = emit_alignment_candidate(
        search_session_id="SEARCH-test",
        actor=a,
        target=b,
        operation="ALIGN",
        transform={"rotation_deg": 1.5, "uniform_scale": 1.0},
        measurements={"axis_angle_error_deg": 0.2, "landmark_residual": 0.01},
        method_ref="gk-m1.measure_align",
    )
    assert rec["correspondence_claim"] is None
    assert rec["interpretation"] is None
    assert rec["epistemic_class"] == "measurement"


def main():
    tests = [
        test_observation_preserves_exact_wording,
        test_search_session_predeclares_scope,
        test_alignment_candidate_rejects_unvalidated_binding,
        test_alignment_candidate_contains_no_correspondence_claim,
    ]
    for t in tests:
        t()
        print(f"PASS {t.__name__}")
    print(f"PASS all {len(tests)} GK-M1 record tests")


if __name__ == "__main__":
    main()
