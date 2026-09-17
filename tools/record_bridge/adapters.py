"""Read-only summaries of native VOXIS records. No geometry or state execution."""
import json
import math
import re

ADAPTER_VERSION = "0.1.0"
SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def number(value, low=-1e12, high=1e12):
    return type(value) in (int, float) and math.isfinite(value) and low <= value <= high


def text(value, limit=500):
    return isinstance(value, str) and 0 < len(value) <= limit


def point(value):
    return isinstance(value, dict) and all(number(value.get(k), -10000, 10000) for k in ("x", "y"))


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "Duplicate JSON key: " + key[:80])
            result[key] = value
        return result

    def constant(value):
        raise ValueError("Non-finite JSON constant: " + value)

    return json.loads(raw.decode("utf-8-sig"), object_pairs_hook=pairs, parse_constant=constant)


def stem_config(c):
    require(isinstance(c, dict), "Missing Stem Lab configuration")
    require(c.get("folio") in ("2r", "2v") and point(c.get("pivot")), "Invalid folio or pivot")
    o = c.get("overlay", {})
    require(isinstance(o, dict) and point(o.get("origin")) and point(o.get("anchor")), "Invalid overlay points")
    require(number(o.get("scale"), .03, 2) and number(o.get("opacity"), 0, 1), "Invalid overlay scale or opacity")
    require(c.get("contactMode") in ("stroke", "tip") and number(c.get("tolerance"), 0, 10), "Invalid contact settings")
    stem = c.get("stem")
    require(isinstance(stem, list) and 2 <= len(stem) <= 100 and all(point(p) for p in stem), "Invalid stem trace")
    regions = c.get("regions")
    require(isinstance(regions, list) and len(regions) <= 100, "Invalid region list")
    ids = set()
    for r in regions:
        require(point(r) and number(r.get("r"), 4, 100) and text(r.get("id"), 80)
                and isinstance(r.get("label"), str) and len(r["label"]) <= 100, "Invalid region")
        require(r["id"] not in ids, "Duplicate region ID")
        ids.add(r["id"])
    timing, camera = c.get("timing", {}), c.get("camera", {})
    require(isinstance(timing, dict) and type(timing.get("enabled")) is bool
            and number(timing.get("bpm"), 30, 180), "Invalid timing settings")
    require(point(camera) and number(camera.get("size"), 200, 4000), "Invalid camera")
    return ids


def stem_summary(s):
    require(text(s.get("id"), 100) and text(s.get("createdAt")), "Missing session identity or timestamp")
    require(number(s.get("angle"), -360000, 360000), "Invalid draft angle")
    stem_config(s.get("config"))
    sources = s.get("sources", {})
    require(isinstance(sources, dict) and isinstance(sources.get("pdfSHA256"), str)
            and SHA256.fullmatch(sources["pdfSHA256"]), "Invalid source PDF checksum")
    assets = sources.get("assets")
    require(isinstance(assets, list) and 1 <= len(assets) <= 100, "Missing source assets")
    reps, paths = [], set()
    for a in assets:
        require(isinstance(a, dict) and text(a.get("path")) and text(a.get("folio")), "Invalid source asset")
        require(a["path"] not in paths, "Duplicate source path")
        paths.add(a["path"])
        require(isinstance(a.get("sha256"), str) and SHA256.fullmatch(a["sha256"]), "Invalid source checksum")
        require(all(type(a.get(k)) is int and 0 < a[k] <= 100000 for k in ("width", "height")), "Invalid image dimensions")
        reps.append({"folio": a["folio"], "native_path": a["path"], "sha256": a["sha256"],
                     "width": a["width"], "height": a["height"], "identity": "sha256:" + a["sha256"]})
    takes = s.get("takes")
    require(isinstance(takes, list) and len(takes) <= 30, "Invalid takes list")
    take_ids, total_samples, take_summaries = set(), 0, []
    for take in takes:
        require(isinstance(take, dict) and text(take.get("id"), 100), "Invalid take identity")
        require(take["id"] not in take_ids, "Duplicate take ID")
        take_ids.add(take["id"])
        ids = stem_config(take.get("config"))
        require(take.get("mapping") == "single-click-432Hz-45ms/1", "Unsupported take sound mapping")
        duration = take.get("duration")
        require(number(duration, 0, 60000), "Invalid take duration")
        samples, events = take.get("samples"), take.get("events")
        require(isinstance(samples, list) and 1 <= len(samples) <= 20000, "Invalid trajectory")
        require(isinstance(events, list) and len(events) <= 100000, "Invalid event list")
        prev_t, prev_angle = -1, None
        for sample in samples:
            require(isinstance(sample, dict) and number(sample.get("t"), 0, duration)
                    and number(sample.get("angle"), -360000, 360000), "Invalid trajectory sample")
            require(sample["t"] > prev_t, "Trajectory time must increase")
            require(prev_angle is None or abs(sample["angle"] - prev_angle) <= 720, "Invalid angular jump")
            prev_t, prev_angle = sample["t"], sample["angle"]
        require(samples[0]["t"] == 0 and abs(samples[-1]["t"] - duration) <= .001, "Trajectory duration mismatch")
        total_samples += len(samples)
        require(total_samples <= 100000, "Too many trajectory samples")
        prev_t, active = -1, set()
        for event in events:
            require(isinstance(event, dict) and event.get("kind") in ("enter", "exit")
                    and isinstance(event.get("regionId"), str) and event["regionId"] in ids
                    and number(event.get("t"), 0, duration) and number(event.get("angle"), -360000, 360000)
                    and type(event.get("initial")) is bool, "Invalid contact event")
            require(event["t"] >= prev_t, "Contact events must be ordered")
            require(not event["initial"] or (event["t"] == 0 and event["kind"] == "enter"), "Invalid initial contact")
            rid = event["regionId"]
            require((rid not in active) if event["kind"] == "enter" else (rid in active), "Unbalanced contact events")
            (active.add if event["kind"] == "enter" else active.remove)(rid)
            prev_t = event["t"]
        take_summaries.append({"id": take["id"], "folio": take["config"]["folio"], "duration_ms": duration,
                               "sample_count": len(samples), "event_count": len(events), "mapping": take["mapping"]})
    return {"producer": "Stem Lab 0.1.0", "native_id": s["id"], "captured_at": s["createdAt"],
            "representations": reps, "pdf_sha256": sources["pdfSHA256"], "captures": take_summaries,
            "coordinates": "Source raster pixels; top-left origin; x right; y down; angles unwrapped degrees; time milliseconds",
            "warnings": ["Structure checked only. Contact geometry was not recomputed.",
                         "Source checksums are declarations; no source images were fetched or compared.",
                         "Use Stem Lab to validate native replay. Contact regions retain their native annotation status."]}


def wxr_state(state):
    require(isinstance(state, dict) and type(state.get("schemaVersion")) is int and state["schemaVersion"] == 1
            and state.get("prototypeId") == "P002-WXR-003", "Unsupported WXR state")
    require(state.get("selected") in ("r", "v") and text(state.get("capturedAt")), "Invalid WXR selection or timestamp")
    folios = state.get("folios")
    require(isinstance(folios, dict), "Missing WXR folios object")
    for key in ("r", "v"):
        f = folios.get(key)
        require(isinstance(f, dict), "Missing WXR folio")
        require(isinstance(f.get("model"), list) and len(f["model"]) == 16
                and all(number(x) for x in f["model"]), "WXR model must have 16 finite numbers")
        require(isinstance(f.get("anchor"), list) and len(f["anchor"]) == 3
                and all(number(x) for x in f["anchor"]), "WXR anchor must have three finite numbers")
        require(number(f.get("alpha"), 0, 1) and number(f.get("scale"), 1e-12, 1e12)
                and type(f.get("flipped")) is bool and f.get("mode") in ("free", "pivot")
                and type(f.get("step")) is int, "Invalid WXR controls")
    if "fingerprint" in state:
        require(isinstance(state["fingerprint"], str) and re.fullmatch(r"[0-9A-F]{8}", state["fingerprint"]), "Invalid fingerprint shape")
    return {"captured_at": state["capturedAt"], "selected": state["selected"],
            "folios": folios, "declared_fingerprint": state.get("fingerprint")}


def wxr_summary(s):
    require(s.get("prototypeId") == "P002-WXR-003" and text(s.get("exportedAt")), "Invalid WXR export identity")
    captures = [{"slot": "current", **wxr_state(s.get("current"))}]
    slots = s.get("savedSlots")
    require(isinstance(slots, dict) and set(slots) <= {"A", "B", "C"}, "Invalid WXR slots")
    for name, state in slots.items():
        captures.append({"slot": name, **wxr_state(state)})
    return {"producer": "P002-WXR-003", "captured_at": s["exportedAt"], "captures": captures,
            "representations": [{"folio": "2r", "identity": None}, {"folio": "2v", "identity": None}],
            "coordinates": "Native 4x4 model arrays and 3D anchors preserved; no planar conversion",
            "warnings": ["Structure checked only. WXR fingerprints were not recomputed.",
                         "Export has no per-image checksums; representation identity remains unresolved.",
                         "No import-to-VR or cross-instrument replay is implemented."]}


def inspect(raw):
    """Never evaluates files, follows their paths, or promotes evidence."""
    result = {"adapter_version": ADAPTER_VERSION, "format": "unknown", "status": "unsupported",
              "research_eligibility": "not_assessed", "media_links": [], "warnings": []}
    try:
        s = strict_json(raw)
        require(isinstance(s, dict), "Top-level JSON must be an object")
        if s.get("schema") == "voxis.stem-session/1":
            result["format"] = "voxis.stem-session/1"
            if s.get("appVersion") != "0.1.0" or s.get("detector") != "polyline-circle-subdivision/1":
                result["warnings"] = ["Unsupported Stem Lab version or detector; original retained."]
                return result
            result.update(stem_summary(s))
            result["status"] = "structure_checked"
        elif s.get("exportSchema") == "VOXIS.configuration-export.v1":
            result["format"] = s["exportSchema"]
            result.update(wxr_summary(s))
            result["status"] = "structure_checked"
        elif s.get("event_type") == "measured_relation_invalidated":
            result["format"] = "voxis.invalidated-event/history"
            require(text(s.get("event_id")) and s.get("evidentiary_use") == "prohibited", "Invalid historical event record")
            result.update(status="invalidated", research_eligibility="prohibited", native_id=s["event_id"],
                          native_search_session_ref=s.get("search_session_id"),
                          warnings=["Historical invalidation retained. Do not use as valid research input."])
        else:
            result["warnings"] = ["Unsupported JSON format; original retained for inspection."]
    except (ValueError, TypeError, AttributeError, KeyError, OverflowError, RecursionError) as exc:
        result.update(status="invalid", research_eligibility="prohibited", warnings=[str(exc)[:500]])
    return result
