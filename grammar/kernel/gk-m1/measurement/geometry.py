"""Deterministic planar geometry methods for VOXIS Grammar Kernel GK-M1.

The module works in an arbitrary common 2-D coordinate frame. Manuscript
source-normalized geometry must first be placed into that common frame by an
explicit recorded transform.

No function in this module creates semantic interpretations or correspondence
claims.
"""
from __future__ import annotations

import math
from copy import deepcopy

EPS = 1e-12


def _point(p):
    if len(p) != 2:
        raise ValueError("point must contain exactly two numbers")
    return (float(p[0]), float(p[1]))


def point_distance(a, b):
    ax, ay = _point(a)
    bx, by = _point(b)
    return math.hypot(bx - ax, by - ay)


def centroid(geometry):
    shape = geometry["shape"]
    data = geometry["normalized"]
    if shape == "point":
        return _point(data)
    if shape in {"segment", "polyline", "polygon"}:
        pts = [_point(p) for p in data]
        if not pts:
            raise ValueError("geometry has no points")
        return (sum(x for x, _ in pts) / len(pts), sum(y for _, y in pts) / len(pts))
    if shape == "bbox":
        x1, y1, x2, y2 = map(float, data)
        return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)
    raise ValueError(f"unsupported shape: {shape}")


def geometry_points(geometry):
    shape = geometry["shape"]
    data = geometry["normalized"]
    if shape == "point":
        return [_point(data)]
    if shape in {"segment", "polyline", "polygon"}:
        return [_point(p) for p in data]
    if shape == "bbox":
        x1, y1, x2, y2 = map(float, data)
        return [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
    raise ValueError(f"unsupported shape: {shape}")


def transform_point(point, transform):
    """Apply recorded 2-D flip/scale/rotation/translation around a pivot."""
    x, y = _point(point)
    pivot = _point(transform.get("pivot", (0.0, 0.0)))
    tx, ty = _point(transform.get("translation", (0.0, 0.0)))
    scale = float(transform.get("uniform_scale", 1.0))
    if scale <= 0:
        raise ValueError("uniform_scale must be positive")
    flip_h = bool(transform.get("flip_h", False))
    flip_v = bool(transform.get("flip_v", False))
    angle = math.radians(float(transform.get("rotation_deg", 0.0)))

    x -= pivot[0]
    y -= pivot[1]
    if flip_h:
        x = -x
    if flip_v:
        y = -y
    x *= scale
    y *= scale
    c, s = math.cos(angle), math.sin(angle)
    xr = x * c - y * s
    yr = x * s + y * c
    return (xr + pivot[0] + tx, yr + pivot[1] + ty)


def transform_geometry(geometry, transform):
    out = deepcopy(geometry)
    pts = [transform_point(p, transform) for p in geometry_points(geometry)]
    shape = geometry["shape"]
    if shape == "point":
        out["normalized"] = list(pts[0])
    elif shape == "bbox":
        # Rotation can turn a box into a non-axis-aligned polygon, so preserve
        # the exact transformed corners as a polygon.
        out["shape"] = "polygon"
        out["normalized"] = [list(p) for p in pts]
    else:
        out["normalized"] = [list(p) for p in pts]
    out["transform_applied"] = deepcopy(transform)
    return out


def _segment_vector(geometry):
    if geometry["shape"] != "segment":
        raise ValueError("operation requires a segment geometry")
    p1, p2 = geometry_points(geometry)
    vx, vy = p2[0] - p1[0], p2[1] - p1[1]
    length = math.hypot(vx, vy)
    if length <= EPS:
        raise ValueError("zero-length segment")
    return p1, p2, (vx, vy), length


def axis_angle_error_deg(actor_segment, target_segment, undirected=True):
    _, _, a, alen = _segment_vector(actor_segment)
    _, _, b, blen = _segment_vector(target_segment)
    cosv = max(-1.0, min(1.0, (a[0] * b[0] + a[1] * b[1]) / (alen * blen)))
    angle = math.degrees(math.acos(cosv))
    if undirected:
        angle = min(angle, 180.0 - angle)
    return abs(angle)


def segment_midpoint(geometry):
    p1, p2, _, _ = _segment_vector(geometry)
    return ((p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0)


def measure_align(actor_geometry, target_geometry, tolerance):
    if actor_geometry["shape"] == "segment" and target_geometry["shape"] == "segment":
        angle = axis_angle_error_deg(actor_geometry, target_geometry, undirected=True)
        residual = point_distance(segment_midpoint(actor_geometry), segment_midpoint(target_geometry))
    else:
        angle = None
        residual = point_distance(centroid(actor_geometry), centroid(target_geometry))
    return {
        "axis_angle_error_deg": angle,
        "landmark_residual": residual,
        "tolerance": float(tolerance),
    }


def _angle_between(v1, v2):
    l1 = math.hypot(*v1)
    l2 = math.hypot(*v2)
    if l1 <= EPS or l2 <= EPS:
        raise ValueError("zero-length vector")
    cosv = max(-1.0, min(1.0, (v1[0] * v2[0] + v1[1] * v2[1]) / (l1 * l2)))
    return math.degrees(math.acos(cosv))


def measure_point(actor_segment, target_geometry, tolerance):
    p1, p2, direction, _ = _segment_vector(actor_segment)
    target = centroid(target_geometry)
    to_target = (target[0] - p1[0], target[1] - p1[1])
    angular = _angle_between(direction, to_target)

    # Distance from target to forward ray p1 -> p2. If the projected target
    # lies behind the ray origin, use distance to p1.
    dx, dy = direction
    denom = dx * dx + dy * dy
    t = ((target[0] - p1[0]) * dx + (target[1] - p1[1]) * dy) / denom
    if t < 0:
        ray_distance = point_distance(target, p1)
    else:
        proj = (p1[0] + t * dx, p1[1] + t * dy)
        ray_distance = point_distance(target, proj)
    return {
        "angular_deviation_deg": angular,
        "target_distance": ray_distance,
        "tolerance": float(tolerance),
    }


def polygon_area(points):
    pts = [_point(p) for p in points]
    if len(pts) < 3:
        return 0.0
    total = 0.0
    for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
        total += x1 * y2 - x2 * y1
    return abs(total) / 2.0


def _signed_polygon_area(points):
    pts = [_point(p) for p in points]
    total = 0.0
    for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
        total += x1 * y2 - x2 * y1
    return total / 2.0


def _inside(p, a, b, orientation):
    cross = (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
    return cross * orientation >= -EPS


def _line_intersection(s, e, a, b):
    x1, y1 = s
    x2, y2 = e
    x3, y3 = a
    x4, y4 = b
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(den) <= EPS:
        return e
    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / den
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / den
    return (px, py)


def convex_polygon_intersection(subject, clip):
    """Sutherland-Hodgman clipping; clip polygon must be convex."""
    output = [_point(p) for p in subject]
    clip_pts = [_point(p) for p in clip]
    if len(output) < 3 or len(clip_pts) < 3:
        return []
    orientation = 1.0 if _signed_polygon_area(clip_pts) >= 0 else -1.0
    for a, b in zip(clip_pts, clip_pts[1:] + clip_pts[:1]):
        input_list = output
        output = []
        if not input_list:
            break
        s = input_list[-1]
        for e in input_list:
            if _inside(e, a, b, orientation):
                if not _inside(s, a, b, orientation):
                    output.append(_line_intersection(s, e, a, b))
                output.append(e)
            elif _inside(s, a, b, orientation):
                output.append(_line_intersection(s, e, a, b))
            s = e
    return output


def measure_overlap(actor_geometry, target_geometry):
    actor_poly = geometry_points(actor_geometry)
    target_poly = geometry_points(target_geometry)
    actor_area = polygon_area(actor_poly)
    target_area = polygon_area(target_poly)
    if actor_area <= EPS or target_area <= EPS:
        raise ValueError("OVERLAP requires area geometry")
    intersection = convex_polygon_intersection(actor_poly, target_poly)
    intersection_area = polygon_area(intersection)
    return {
        "intersection_area": intersection_area,
        "actor_overlap_fraction": intersection_area / actor_area,
        "target_overlap_fraction": intersection_area / target_area,
    }


def measure_cover(actor_geometry, target_geometry, layer_order, depth_separation):
    overlap = measure_overlap(actor_geometry, target_geometry)
    return {
        "target_covered_fraction": overlap["target_overlap_fraction"],
        "layer_order": list(layer_order),
        "depth_separation": float(depth_separation),
    }


def endpoint(geometry):
    if geometry["shape"] not in {"segment", "polyline"}:
        raise ValueError("TERMINATE actor requires segment/polyline")
    pts = geometry_points(geometry)
    return pts[-1]


def measure_terminate(actor_geometry, target_geometry, tolerance):
    return {
        "endpoint_distance": point_distance(endpoint(actor_geometry), centroid(target_geometry)),
        "tolerance": float(tolerance),
    }


def measure_relation(operation, actor_geometry, target_geometry, **context):
    if operation == "ALIGN":
        return measure_align(actor_geometry, target_geometry, context["tolerance"])
    if operation == "POINT":
        return measure_point(actor_geometry, target_geometry, context["tolerance"])
    if operation == "OVERLAP":
        return measure_overlap(actor_geometry, target_geometry)
    if operation == "COVER":
        return measure_cover(actor_geometry, target_geometry, context["layer_order"], context["depth_separation"])
    if operation == "TERMINATE":
        return measure_terminate(actor_geometry, target_geometry, context["tolerance"])
    raise ValueError(f"unsupported operation: {operation}")
