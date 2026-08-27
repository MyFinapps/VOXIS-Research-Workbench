from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from workbench.vista.m1.spatial_records import emit_spatial_record, list_records, persist_immutable, read_record


def test_anchor_is_observation_not_evidence():
    anchor = emit_spatial_record(
        kind="anchor_marker",
        record_id="ANCHOR-test-001",
        operator="JT",
        source_refs=["F2V"],
        representation_refs=["VM.f2v.overlay"],
        data={"local_position_xyz_m": [0.1, -0.2, 0.02], "label": "root junction"},
        created_at="2026-08-27T20:01:00Z",
    )
    assert anchor["epistemic_class"] == "observation"
    assert anchor["evidence_status"] == "not_evidence"
    assert anchor["coordinate_space_ref"] == "VISTA.m1.world"


def test_alignment_group_is_workspace_structure_and_versions():
    group = emit_spatial_record(
        kind="alignment_group",
        record_id="AG-test-001",
        operator="JT",
        source_refs=["F2R", "F2V", "F3R"],
        representation_refs=["VM.f2r.anchor", "VM.f2v.overlay", "VM.f3r.overlay"],
        data={"member_representation_refs": ["VM.f2r.anchor", "VM.f2v.overlay", "VM.f3r.overlay"], "locks": {"rotation": True}},
        created_at="2026-08-27T20:02:00Z",
    )
    assert group["record_class"] == "workspace_structure"
    assert group["epistemic_class"] is None
    assert group["evidence_status"] == "not_evidence"

    revised = emit_spatial_record(
        kind="alignment_group",
        record_id="AG-test-002",
        operator="JT",
        supersedes_record_id="AG-test-001",
        data={"member_representation_refs": ["VM.f2r.anchor", "VM.f2v.overlay", "VM.f3r.overlay"], "locks": {"rotation": True, "scale": True}},
    )
    assert revised["supersedes_record_id"] == "AG-test-001"


def test_spatial_persistence_is_create_only():
    anchor = emit_spatial_record(kind="anchor_marker", record_id="ANCHOR-test-003", data={"local_position_xyz_m": [0, 0, 0]})
    with tempfile.TemporaryDirectory() as td:
        persist_immutable(anchor, td)
        assert read_record("ANCHOR-test-003", td) == anchor
        assert len(list_records(td)) == 1
        try:
            persist_immutable(anchor, td)
        except ValueError as exc:
            assert "immutable" in str(exc)
        else:
            raise AssertionError("duplicate spatial record overwrote an immutable record")


def main():
    tests = [test_anchor_is_observation_not_evidence, test_alignment_group_is_workspace_structure_and_versions, test_spatial_persistence_is_create_only]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"PASS all {len(tests)} VISTA M1 spatial-record tests")


if __name__ == "__main__":
    main()
