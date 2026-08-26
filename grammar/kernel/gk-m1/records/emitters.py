"""Minimal provenance-preserving record emitters for GK-M1.

These emitters create structured records; they do not interpret manuscript
meaning. Alignment-candidate emission is gated on human-validated/measured
primitive annotations so proposed landmarks cannot silently become evidence.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import uuid


class ValidationGateError(ValueError):
    pass


def _utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _id(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def emit_observation_record(*, source_refs, exact_wording, operator=None, geometry_refs=None, created_at=None, provenance=None):
    if not exact_wording or not exact_wording.strip():
        raise ValueError("exact_wording is required")
    return {
        "record_type": "observation",
        "observation_id": _id("OBS"),
        "created_at": created_at or _utc_now(),
        "source_refs": list(source_refs),
        "geometry_refs": list(geometry_refs or []),
        "exact_wording": exact_wording,
        "operator": operator,
        "epistemic_class": "observation",
        "provenance": deepcopy(provenance or {}),
    }


def emit_search_session_record(*, source_refs, declared_primitives, declared_relations, allowed_transforms, operator=None, created_at=None, provenance=None):
    return {
        "record_type": "search_session",
        "search_session_id": _id("SEARCH"),
        "created_at": created_at or _utc_now(),
        "source_refs": list(source_refs),
        "declared_primitives": list(declared_primitives),
        "declared_relations": list(declared_relations),
        "allowed_transforms": deepcopy(allowed_transforms),
        "operator": operator,
        "status": "open",
        "provenance": deepcopy(provenance or {}),
    }


def _require_validated_entity(entity):
    status = entity.get("annotation_status")
    if status not in {"human_validated", "measured"}:
        raise ValidationGateError(
            f"{entity.get('entity_id', '<unknown>')} is {status!r}; alignment candidates require human_validated/measured annotations"
        )


def emit_alignment_candidate(*, search_session_id, actor, target, operation, transform, measurements, method_ref, created_at=None, provenance=None):
    _require_validated_entity(actor)
    _require_validated_entity(target)
    if not measurements:
        raise ValidationGateError("alignment candidate requires a non-empty measurement payload")
    if operation not in {"ALIGN", "POINT", "OVERLAP", "COVER", "TERMINATE"}:
        raise ValueError(f"unsupported grammar relation: {operation}")
    return {
        "record_type": "alignment_candidate",
        "alignment_id": _id("ALIGN"),
        "created_at": created_at or _utc_now(),
        "search_session_id": search_session_id,
        "actor": deepcopy(actor),
        "target": deepcopy(target),
        "operation": operation,
        "transform": deepcopy(transform),
        "measurements": deepcopy(measurements),
        "method_ref": method_ref,
        "epistemic_class": "measurement",
        "correspondence_claim": None,
        "interpretation": None,
        "provenance": deepcopy(provenance or {}),
    }
