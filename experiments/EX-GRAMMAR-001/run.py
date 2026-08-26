"""Run the preregistered EX-GRAMMAR-001 deterministic measurement.

This script records measurements only. It creates no correspondence, grammar,
function, intent, or semantic interpretation claim.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[2]
GK_M1 = REPO / "grammar" / "kernel" / "gk-m1"
sys.path.insert(0, str(GK_M1))

from measurement.geometry import measure_point  # noqa: E402

SESSION_PATH = REPO / "experiments" / "EX-GRAMMAR-001" / "search_session.json"
BINDING_PATH = GK_M1 / "bindings" / "voynich_2r_2v_3r_gk_m1.json"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    session = load_json(SESSION_PATH)
    binding = load_json(BINDING_PATH)

    if session["status"] != "predeclared_not_measured":
        raise RuntimeError("EX-GRAMMAR-001 must be run from its preregistered session definition")
    if session["operation"] != "POINT":
        raise RuntimeError("EX-GRAMMAR-001 preregisters POINT only")
    if session["allowed_transform"]["mode"] != "identity_only":
        raise RuntimeError("EX-GRAMMAR-001 preregisters identity transform only")

    entities = {e["entity_id"]: e for e in binding["entities"]}
    actor = entities[session["actor"]]
    target = entities[session["target"]]

    for entity in (actor, target):
        if entity["annotation_status"] != "human_validated":
            raise RuntimeError(f"{entity['entity_id']} is not human_validated")

    tolerance = float(session["predeclared_context"]["tolerance_normalized"])
    measurements = measure_point(actor["geometry"], target["geometry"], tolerance=tolerance)

    result = {
        "record_type": "measurement_result",
        "result_id": "EX-GRAMMAR-001-R1",
        "search_session_id": session["search_session_id"],
        "source_refs": session["source_refs"],
        "actor": actor["entity_id"],
        "operation": session["operation"],
        "target": target["entity_id"],
        "transform": session["allowed_transform"],
        "measurements": measurements,
        "measurement_method": session["measurement_method"],
        "epistemic_class": "measurement",
        "selected_case_pipeline_only": True,
        "correspondence_claim": None,
        "interpretation": None,
        "provenance": {
            "search_session_sha256": sha256_file(SESSION_PATH),
            "binding_sha256": sha256_file(BINDING_PATH),
            "parent_milestone": "GK-M1"
        }
    }

    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
