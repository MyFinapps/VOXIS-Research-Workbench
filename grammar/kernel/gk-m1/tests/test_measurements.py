import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from measurement.geometry import (
    axis_angle_error_deg,
    measure_align,
    measure_cover,
    measure_overlap,
    measure_point,
    measure_terminate,
    transform_geometry,
)


def g_point(x, y):
    return {"shape": "point", "normalized": [x, y]}


def g_segment(a, b):
    return {"shape": "segment", "normalized": [list(a), list(b)]}


def g_bbox(x1, y1, x2, y2):
    return {"shape": "bbox", "normalized": [x1, y1, x2, y2]}


def load_binding():
    with open(os.path.join(ROOT, "bindings", "voynich_2r_2v_3r_gk_m1.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def test_binding_status_boundary():
    payload = load_binding()
    assert payload["status"] == "proposed_pending_human_validation"
    for entity in payload["entities"]:
        assert entity["annotation_status"] == "proposed_pending_human_validation"
    assert {d["primitive_type"] for d in payload["deferred_bindings"]} == {"DENSE_FIELD", "GLYPH_CLUSTER"}


def test_source_coordinates_roundtrip():
    payload = load_binding()
    sources = payload["sources"]
    for entity in payload["entities"]:
        folio = entity["source_ref"].split(".")[-1].removeprefix("f")
        src = sources[folio]
        geom = entity["geometry"]
        if geom["shape"] == "point":
            px = geom["pixel"]
            norm = geom["normalized"]
            assert abs(px[0] / src["width_px"] - norm[0]) < 1e-6
            assert abs(px[1] / src["height_px"] - norm[1]) < 1e-6


def test_transform_point_geometry():
    p = g_point(0.25, 0.5)
    t = {"pivot": [0, 0], "translation": [1, -1], "uniform_scale": 2, "rotation_deg": 90, "flip_h": False, "flip_v": False}
    out = transform_geometry(p, t)
    x, y = out["normalized"]
    assert abs(x - 0.0) < 1e-9
    assert abs(y + 0.5) < 1e-9


def test_align_parallel_segments():
    a = g_segment((0, 0), (1, 0))
    b = g_segment((0, 0.1), (1, 0.1))
    m = measure_align(a, b, tolerance=0.2)
    assert abs(m["axis_angle_error_deg"]) < 1e-9
    assert abs(m["landmark_residual"] - 0.1) < 1e-9


def test_axis_undirected():
    a = g_segment((0, 0), (1, 0))
    b = g_segment((1, 0), (0, 0))
    assert abs(axis_angle_error_deg(a, b)) < 1e-9


def test_point_relation():
    ray = g_segment((0, 0), (1, 0))
    target = g_point(2, 0.1)
    m = measure_point(ray, target, tolerance=0.2)
    assert m["angular_deviation_deg"] > 0
    assert abs(m["target_distance"] - 0.1) < 1e-9


def test_overlap_bbox():
    a = g_bbox(0, 0, 1, 1)
    b = g_bbox(0.5, 0.5, 1.5, 1.5)
    m = measure_overlap(a, b)
    assert abs(m["intersection_area"] - 0.25) < 1e-9
    assert abs(m["actor_overlap_fraction"] - 0.25) < 1e-9
    assert abs(m["target_overlap_fraction"] - 0.25) < 1e-9


def test_cover_is_directional_overlap_only():
    a = g_bbox(0, 0, 1, 1)
    b = g_bbox(0.25, 0.25, 0.75, 0.75)
    m = measure_cover(a, b, layer_order=["actor", "target"], depth_separation=0.01)
    assert abs(m["target_covered_fraction"] - 1.0) < 1e-9
    assert m["layer_order"] == ["actor", "target"]
    assert m["depth_separation"] == 0.01


def test_terminate():
    stem = g_segment((0, 0), (1, 1))
    target = g_point(1.01, 1.0)
    m = measure_terminate(stem, target, tolerance=0.02)
    assert abs(m["endpoint_distance"] - 0.01) < 1e-9


def test_no_semantic_outputs():
    forbidden = {"transmitter", "receiver", "injection", "receptacle", "activation", "grounding"}
    samples = [
        measure_align(g_point(0, 0), g_point(0, 0), 0.1),
        measure_point(g_segment((0, 0), (1, 0)), g_point(2, 0), 0.1),
        measure_overlap(g_bbox(0, 0, 1, 1), g_bbox(0, 0, 1, 1)),
        measure_cover(g_bbox(0, 0, 1, 1), g_bbox(0, 0, 1, 1), ["a", "b"], 0),
        measure_terminate(g_segment((0, 0), (1, 0)), g_point(1, 0), 0.1),
    ]
    text = json.dumps(samples).lower()
    for word in forbidden:
        assert word not in text


def main():
    tests = [
        test_binding_status_boundary,
        test_source_coordinates_roundtrip,
        test_transform_point_geometry,
        test_align_parallel_segments,
        test_axis_undirected,
        test_point_relation,
        test_overlap_bbox,
        test_cover_is_directional_overlap_only,
        test_terminate,
        test_no_semantic_outputs,
    ]
    for t in tests:
        t()
        print(f"PASS {t.__name__}")
    print(f"PASS all {len(tests)} GK-M1 tests")


if __name__ == "__main__":
    main()
