#!/usr/bin/env python3
"""Execute the frozen EX-GRAMMAR-002A Stage B opportunity matrix."""

from __future__ import annotations

import hashlib
import json
import statistics
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from grammar.kernel.gk_m1_import import measure_point  # noqa: E402


HERE = Path(__file__).resolve().parent
INVENTORY = HERE / "candidate_inventory.frozen.json"
EXPECTED_SHA256 = "735d9a58ab0305048617ffa20d99c2f86826e5863f7f0355eacd476740d810d7"
TOLERANCE = 0.03


def rounded(value: float) -> float:
    return round(float(value), 9)


def summarize(values: list[float]) -> dict[str, float]:
    return {
        "minimum": rounded(min(values)),
        "median": rounded(statistics.median(values)),
        "mean": rounded(statistics.fmean(values)),
        "maximum": rounded(max(values)),
    }


def main() -> None:
    raw = INVENTORY.read_bytes()
    actual_hash = hashlib.sha256(raw).hexdigest()
    if actual_hash != EXPECTED_SHA256:
        raise SystemExit(f"frozen inventory hash mismatch: {actual_hash}")

    inventory = json.loads(raw)
    stems = inventory["candidates"]["STEM"]
    ys = inventory["candidates"]["Y"]
    if len(stems) != 3 or len(ys) != 2:
        raise SystemExit("frozen opportunity dimensions are not 3 x 2")
    if any(item["review_status"] != "accepted" for item in stems + ys):
        raise SystemExit("unaccepted candidate in frozen opportunity set")

    rows = []
    for stem in stems:
        for target in ys:
            measured = measure_point(stem["geometry"], target["geometry"], TOLERANCE)
            rows.append({
                "actor_id": stem["id"],
                "actor_entity_id": stem["entity_id"],
                "target_id": target["id"],
                "target_entity_id": target["entity_id"],
                "source_ref": inventory["source"]["source_ref"],
                "transform": "identity",
                "angular_deviation_deg": rounded(measured["angular_deviation_deg"]),
                "target_distance": rounded(measured["target_distance"]),
                "tolerance": TOLERANCE,
                "qualifies_distance": measured["target_distance"] <= TOLERANCE,
                "method": "grammar/kernel/gk-m1/measurement/geometry.py::measure_point",
                "candidate_inventory_sha256": actual_hash,
            })

    if len(rows) != len(stems) * len(ys):
        raise SystemExit("incomplete Cartesian product")

    per_stem = []
    for stem in stems:
        own = sorted((row for row in rows if row["actor_id"] == stem["id"]), key=lambda row: row["target_distance"])
        qualifying = sum(row["qualifies_distance"] for row in own)
        per_stem.append({
            "actor_id": stem["id"],
            "nearest_target_id": own[0]["target_id"],
            "second_nearest_target_id": own[1]["target_id"],
            "minimum_target_distance": own[0]["target_distance"],
            "angular_deviation_to_nearest_y_deg": own[0]["angular_deviation_deg"],
            "qualifying_y_count": qualifying,
            "qualifying_y_fraction": rounded(qualifying / len(own)),
        })

    distances = [row["target_distance"] for row in rows]
    angles = [row["angular_deviation_deg"] for row in rows]
    index_row = next(row for row in rows if row["actor_id"] == "S1" and row["target_id"] == "Y1")
    index_distance = index_row["target_distance"]
    rank = 1 + sum(distance < index_distance for distance in distances)
    own_sorted = sorted((row for row in rows if row["actor_id"] == "S1"), key=lambda row: row["target_distance"])
    own_rank = 1 + sum(row["target_distance"] < index_distance for row in own_sorted)
    other_distance = next(row["target_distance"] for row in own_sorted if row["target_id"] != "Y1")
    qualifying_total = sum(row["qualifies_distance"] for row in rows)

    result = {
        "experiment_id": "EX-GRAMMAR-002A",
        "stage": "B_complete_opportunity_matrix",
        "status": "completed",
        "source": inventory["source"],
        "candidate_inventory_sha256": actual_hash,
        "transform_policy": "identity_only",
        "tolerance": TOLERANCE,
        "eligible_stem_count": len(stems),
        "eligible_y_count": len(ys),
        "opportunity_count": len(rows),
        "complete_opportunity_table": rows,
        "per_stem_summary": per_stem,
        "descriptive_statistics": {
            "target_distance": summarize(distances),
            "angular_deviation_deg": summarize(angles),
            "angular_deviation_values_sorted": sorted(angles),
            "qualifying_opportunity_count": qualifying_total,
            "qualifying_opportunity_fraction": rounded(qualifying_total / len(rows)),
        },
        "index_case": {
            "actor_id": "S1",
            "target_id": "Y1",
            "target_distance": index_distance,
            "angular_deviation_deg": index_row["angular_deviation_deg"],
            "distance_rank_all_opportunities": rank,
            "distance_percentile_less_than_or_equal": rounded(100 * sum(distance <= index_distance for distance in distances) / len(distances)),
            "rank_among_targets_for_own_stem": own_rank,
            "difference_from_other_y_for_same_stem": rounded(other_distance - index_distance),
            "qualifies_distance": index_row["qualifies_distance"],
            "historical_comparison_note": "Corrected comparison only; does not restore the invalidated original EX-GRAMMAR-001 result."
        },
        "epistemic_boundary": "Within-folio descriptive geometry only; no grammar, intentionality, function, meaning, or cross-folio inference is established."
    }
    output = HERE / "stage_b_results.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
