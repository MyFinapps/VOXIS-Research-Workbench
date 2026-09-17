"""Canonical FREEZE-state emitter for VOXIS research runtimes.

FREEZE preserves a candidate observational state. It does not create evidence,
measurement, correspondence proof, interpretation, or manuscript meaning.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import uuid


def _utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _id():
    return f"FREEZE-{uuid.uuid4().hex[:12]}"


def emit_freeze_record(
    *,
    trigger,
    capture_context,
    representation_states,
    provenance,
    operator=None,
    parent_search_session_id=None,
    candidate_observation_id=None,
    operator_note_exact=None,
    active_features=None,
    media_buffer_refs=None,
    linked_measurement_ids=None,
    capture_completeness="full",
    missing_fields=None,
    measurement_status="unmeasured",
    created_at=None,
    content_hash=None,
):
    """Emit an immutable-by-contract FREEZE record payload.

    Validation here is intentionally minimal and deterministic. Full structural
    validation belongs to ``schemas/records/freeze_record.schema.json``.
    """
    if capture_completeness not in {"full", "partial"}:
        raise ValueError("capture_completeness must be 'full' or 'partial'")
    if measurement_status not in {"unmeasured", "measurement_linked"}:
        raise ValueError("unsupported measurement_status")
    if not representation_states:
        raise ValueError("FREEZE requires at least one representation state")
    source_refs = list((provenance or {}).get("source_refs") or [])
    if not source_refs:
        raise ValueError("FREEZE provenance requires at least one source_ref")

    missing_fields = list(missing_fields or [])
    if missing_fields and capture_completeness != "partial":
        raise ValueError("missing_fields requires capture_completeness='partial'")

    linked_measurement_ids = list(linked_measurement_ids or [])
    if linked_measurement_ids and measurement_status != "measurement_linked":
        raise ValueError(
            "linked_measurement_ids requires measurement_status='measurement_linked'"
        )

    return {
        "record_type": "freeze_state",
        "schema_version": "0.1.0",
        "freeze_id": _id(),
        "created_at": created_at or _utc_now(),
        "operator": operator,
        "parent_search_session_id": parent_search_session_id,
        "candidate_observation_id": candidate_observation_id,
        "epistemic_class": "observation",
        "evidence_status": "not_evidence",
        "measurement_status": measurement_status,
        "capture_completeness": capture_completeness,
        "missing_fields": missing_fields,
        "operator_note_exact": operator_note_exact,
        "trigger": deepcopy(trigger),
        "capture_context": deepcopy(capture_context),
        "representation_states": deepcopy(representation_states),
        "active_features": deepcopy(active_features or []),
        "media_buffer_refs": deepcopy(media_buffer_refs or []),
        "linked_measurement_ids": linked_measurement_ids,
        "content_hash": content_hash,
        "provenance": deepcopy(provenance),
    }
