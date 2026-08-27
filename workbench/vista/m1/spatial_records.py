"""Immutable spatial research records for VISTA M1."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import json
import re
import uuid

KINDS = {
    "anchor_marker": "ANCHOR",
    "observation_annotation": "NOTE",
    "relation_link": "LINK",
    "alignment_group": "AG",
}
ID_RE = re.compile(r"^(ANCHOR|NOTE|LINK|AG)-[A-Za-z0-9._:-]+$")


def _utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _new_id(kind):
    return f"{KINDS[kind]}-{uuid.uuid4().hex[:12]}"


def emit_spatial_record(
    *,
    kind,
    data,
    operator=None,
    record_id=None,
    created_at=None,
    linked_freeze_id=None,
    supersedes_record_id=None,
    source_refs=None,
    representation_refs=None,
):
    if kind not in KINDS:
        raise ValueError(f"unsupported spatial record kind: {kind}")
    record_id = record_id or _new_id(kind)
    if not ID_RE.fullmatch(record_id):
        raise ValueError("invalid spatial record id")
    if supersedes_record_id is not None and not ID_RE.fullmatch(supersedes_record_id):
        raise ValueError("invalid supersedes_record_id")

    claim_bearing = kind in {"anchor_marker", "observation_annotation", "relation_link"}
    return {
        "record_type": kind,
        "schema_version": "0.1.0",
        "record_id": record_id,
        "created_at": created_at or _utc_now(),
        "operator": operator,
        "record_class": "workspace_structure" if kind == "alignment_group" else "spatial_observation",
        "epistemic_class": "observation" if claim_bearing else None,
        "evidence_status": "not_evidence",
        "coordinate_space_ref": "VISTA.m1.world",
        "units": "m",
        "linked_freeze_id": linked_freeze_id,
        "supersedes_record_id": supersedes_record_id,
        "data": deepcopy(data),
        "provenance": {
            "source_refs": list(source_refs or []),
            "representation_refs": list(representation_refs or []),
            "software_build_ref": "VISTA_M1_PRECISION_ANNOTATION_v0.2.0",
            "research_boundary": "Spatial annotations and groups preserve operator structure; they do not establish manuscript correspondence or meaning.",
        },
    }


def persist_immutable(record, directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    record_id = record.get("record_id", "")
    if not ID_RE.fullmatch(record_id):
        raise ValueError("invalid spatial record id")
    path = directory / f"{record_id}.json"
    payload = json.dumps(record, indent=2, ensure_ascii=False) + "\n"
    try:
        with path.open("x", encoding="utf-8") as handle:
            handle.write(payload)
    except FileExistsError as exc:
        raise ValueError("spatial record is immutable and already exists") from exc
    return path


def read_record(record_id, directory):
    if not ID_RE.fullmatch(record_id):
        raise ValueError("invalid spatial record id")
    path = Path(directory) / f"{record_id}.json"
    if not path.exists():
        raise FileNotFoundError(record_id)
    return json.loads(path.read_text(encoding="utf-8"))


def list_records(directory):
    directory = Path(directory)
    if not directory.exists():
        return []
    records = []
    for path in sorted(directory.glob("*.json"), key=lambda p: p.stat().st_mtime):
        try:
            records.append(json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            continue
    return records
