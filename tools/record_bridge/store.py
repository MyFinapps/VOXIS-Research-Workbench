"""Transactional local intake store. Original bytes and summaries commit together."""
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import ntpath
from pathlib import Path
import re
import sqlite3

from adapters import inspect

MAX_BYTES = 8 * 1024 * 1024
STORE_VERSION = 1
HEX = re.compile(r"[0-9a-f]{64}\Z")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def reference(value):
    if value is not None and (not isinstance(value, str) or not value.strip() or len(value) > 200
                              or any(ord(c) < 32 for c in value)):
        raise ValueError("Search Session reference must be 1-200 visible characters")
    return value


@contextmanager
def connection(path, create=False):
    path = Path(path).resolve()
    if create:
        path.parent.mkdir(parents=True, exist_ok=True)
    elif not path.is_file():
        raise ValueError("No index at this location. Import a record to start one.")
    db = sqlite3.connect(path.as_uri() + ("?mode=rwc" if create else "?mode=ro"), uri=True, timeout=5)
    db.row_factory = sqlite3.Row
    try:
        db.execute("PRAGMA foreign_keys=ON")
        if create:
            db.execute("PRAGMA synchronous=FULL")
            db.execute("BEGIN IMMEDIATE")
        version = db.execute("PRAGMA user_version").fetchone()[0]
        tables = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        if version == 0 and create and not tables:
            db.execute("CREATE TABLE records (id TEXT PRIMARY KEY, original BLOB NOT NULL, summary TEXT NOT NULL, imported_at TEXT NOT NULL, original_name TEXT NOT NULL)")
            db.execute("CREATE TABLE session_links (record_id TEXT REFERENCES records(id), search_session_ref TEXT NOT NULL, PRIMARY KEY(record_id, search_session_ref))")
            db.execute("PRAGMA user_version=1")
        elif version != STORE_VERSION or {r[0] for r in tables} != {"records", "session_links"}:
            raise ValueError("Unsupported store schema. Use a new empty index path.")
        yield db
        if create:
            db.commit()
    except BaseException:
        if create:
            db.rollback()
        raise
    finally:
        db.close()


def ingest(path, source, search_session_ref=None):
    reference(search_session_ref)
    source = Path(source)
    with source.open("rb") as handle:
        raw = handle.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("Input exceeds 8 MiB; original left at its source location")
    record_id = digest(raw)
    summary = inspect(raw)
    with connection(path, create=True) as db:
        existing = db.execute("SELECT original, summary FROM records WHERE id=?", (record_id,)).fetchone()
        duplicate = existing is not None
        if existing:
            if bytes(existing["original"]) != raw:
                raise ValueError("Stored original differs from its hash identity; run verify")
            summary = json.loads(existing["summary"])
        else:
            db.execute("INSERT INTO records VALUES (?,?,?,?,?)", (record_id, raw,
                       json.dumps(summary, ensure_ascii=True, allow_nan=False),
                       datetime.now(timezone.utc).isoformat(), ntpath.basename(str(source))))
        if search_session_ref is not None:
            db.execute("INSERT OR IGNORE INTO session_links VALUES (?,?)", (record_id, search_session_ref))
    return {"id": record_id, "duplicate": duplicate, "summary": summary}


def records(path):
    with connection(path) as db:
        result = []
        for row in db.execute("SELECT id, summary, imported_at, original_name FROM records ORDER BY imported_at, id"):
            s = json.loads(row["summary"])
            links = [r[0] for r in db.execute("SELECT search_session_ref FROM session_links WHERE record_id=? ORDER BY search_session_ref", (row["id"],))]
            result.append({"id": row["id"], "name": row["original_name"], "imported_at": row["imported_at"],
                           "format": s["format"], "status": s["status"], "search_session_refs": links})
        return result


def retrieve(path, record_id):
    if not isinstance(record_id, str) or not HEX.fullmatch(record_id):
        raise ValueError("Use the complete 64-character record ID from the index")
    with connection(path) as db:
        row = db.execute("SELECT * FROM records WHERE id=?", (record_id,)).fetchone()
        if row is None:
            raise ValueError("Record not found")
        raw = bytes(row["original"])
        if digest(raw) != record_id:
            raise ValueError("Original checksum mismatch; export blocked")
        return raw, json.loads(row["summary"])


def export_original(path, record_id, target):
    raw, _ = retrieve(path, record_id)
    # Exclusive creation: never overwrite a file, source, or the intake database.
    with Path(target).open("xb") as handle:
        handle.write(raw)
        handle.flush()
        import os
        os.fsync(handle.fileno())
    return {"id": record_id, "bytes": len(raw), "path": str(Path(target).resolve())}


def verify(path):
    with connection(path) as db:
        integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
        foreign_keys = db.execute("PRAGMA foreign_key_check").fetchall()
        failures, count = [], 0
        for row in db.execute("SELECT id, original, summary FROM records"):
            count += 1
            if digest(bytes(row["original"])) != row["id"]:
                failures.append({"id": row["id"], "error": "checksum_mismatch"})
            elif inspect(bytes(row["original"])) != json.loads(row["summary"]):
                failures.append({"id": row["id"], "error": "summary_mismatch_or_adapter_version_change"})
    return {"ok": integrity == "ok" and not foreign_keys and not failures,
            "record_count": count, "sqlite_integrity": integrity,
            "foreign_key_errors": len(foreign_keys), "failures": failures}
