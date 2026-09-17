#!/usr/bin/env python3
"""C02 Record Browser: loopback-only, read-only inspection plus explicit export."""
import argparse
import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import secrets
import sqlite3
import threading
from urllib.parse import urlsplit, parse_qs
import webbrowser

import adapters
import bridge
import store

VERSION = "0.1.0"
WEB = Path(__file__).with_name("browser_web")
ASSETS = {"/": ("index.html", "text/html"),
          "/app.js": ("app.js", "text/javascript"),
          "/style.css": ("style.css", "text/css")}


def inspect_record(index, record_id):
    raw, summary = store.retrieve(index, record_id)
    # A modified summary must never promote eligibility or hide invalidation.
    if adapters.inspect(raw) != summary:
        raise ValueError("Stored summary differs from this adapter's interpretation. Export blocked; use Bridge Verify index to investigate.")
    rows = store.records(index)
    row = next((r for r in rows if r["id"] == record_id), None)
    if row is None:
        raise ValueError("Record no longer available. Refresh the records list.")
    try:
        native = raw.decode("utf-8-sig")
        encoding_note = "UTF-8 text view. Export preserves the original bytes, including any BOM."
    except UnicodeDecodeError:
        native = raw.hex(" ")
        encoding_note = "Invalid UTF-8: hexadecimal byte view. Export preserves the original bytes."
    return {"record": row, "summary": summary, "native": native,
            "encoding_note": encoding_note, "bytes": len(raw)}


def export_record(index, record_id, target):
    inspect_record(index, record_id)
    if not isinstance(target, str) or not target.strip() or any(ord(c) < 32 for c in target):
        raise ValueError("Enter a full destination path ending in .json.")
    path = Path(target)
    if not path.is_absolute() or path.suffix.lower() != ".json":
        raise ValueError("Choose an absolute destination path ending in .json.")
    if any(":" in part for part in path.parts[1:]):
        raise ValueError("The destination must be an ordinary JSON file, not a device or alternate stream.")
    if path.stem.upper() in {"CON", "PRN", "AUX", "NUL", *[f"COM{i}" for i in range(1, 10)], *[f"LPT{i}" for i in range(1, 10)]}:
        raise ValueError("Choose an ordinary filename, not a reserved device name.")
    if not path.parent.is_dir():
        raise ValueError("The destination folder does not exist. Choose an existing folder.")
    return store.export_original(index, record_id, path)


class BrowserServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = False

    def __init__(self, index, port=0):
        self.index = Path(index).resolve()
        self.token = secrets.token_urlsafe(32)
        super().__init__(("127.0.0.1", port), Handler)
        self.origin = f"http://127.0.0.1:{self.server_port}"

    @property
    def launch_url(self):
        return self.origin + "/#" + self.token


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass  # Never log private filenames, request bodies or session tokens.

    def setup(self):
        super().setup()
        self.connection.settimeout(15)

    def send_payload(self, code, value, mime="application/json"):
        data = json.dumps(value, ensure_ascii=True, allow_nan=False).encode() if mime == "application/json" else value
        self.send_response(code)
        self.send_header("Content-Type", mime + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'")
        self.end_headers()
        self.wfile.write(data)

    def authorized(self, api=False):
        if self.headers.get("Host") != urlsplit(self.server.origin).netloc:
            return False
        origin = self.headers.get("Origin")
        if origin is not None and origin != self.server.origin:
            return False
        if self.headers.get("Sec-Fetch-Site") == "cross-site":
            return False
        return not api or hmac.compare_digest(self.headers.get("X-VOXIS-Token", "").encode("utf-8"), self.server.token.encode("utf-8"))

    def do_GET(self):
        parsed = urlsplit(self.path)
        if not self.authorized(parsed.path.startswith("/api/")):
            self.send_payload(403, {"error": "Session unavailable. Reopen the Browser using its launcher."})
            return
        try:
            if parsed.path == "/favicon.ico":
                self.send_payload(204, b"", "image/x-icon")
            elif parsed.path in ASSETS:
                name, mime = ASSETS[parsed.path]
                self.send_payload(200, (WEB / name).read_bytes(), mime)
            elif parsed.path == "/api/records":
                if not self.server.index.exists():
                    self.send_payload(200, {"state": "missing", "records": []})
                else:
                    rows = store.records(self.server.index)
                    self.send_payload(200, {"state": "ready" if rows else "empty", "records": rows})
            elif parsed.path == "/api/record":
                rid = parse_qs(parsed.query).get("id", [None])[0]
                self.send_payload(200, inspect_record(self.server.index, rid))
            elif parsed.path == "/api/info":
                self.send_payload(200, {"version": VERSION, "index": str(self.server.index),
                                        "export_folder": str(Path.home() / "Downloads")})
            else:
                self.send_payload(404, {"error": "Not found"})
        except (ValueError, OSError, sqlite3.Error, KeyError, TypeError, RecursionError) as exc:
            self.fail(exc)

    def do_POST(self):
        if not self.authorized(True):
            self.send_payload(403, {"error": "Session unavailable. Reopen the Browser using its launcher."})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if self.headers.get("Content-Type") != "application/json" or not 0 < size <= 16384:
                raise ValueError("Expected a small JSON request.")
            payload = json.loads(self.rfile.read(size))
            if not isinstance(payload, dict):
                raise ValueError("Expected a JSON object.")
            if self.path == "/api/export":
                self.send_payload(200, export_record(self.server.index, payload.get("id"), payload.get("path")))
            elif self.path == "/api/stop":
                self.send_payload(200, {"stopped": True})
                threading.Thread(target=self.server.shutdown, daemon=True).start()
            else:
                self.send_payload(404, {"error": "Not found"})
        except (ValueError, OSError, sqlite3.Error, KeyError, TypeError, RecursionError) as exc:
            self.fail(exc)

    def fail(self, exc):
        if isinstance(exc, FileExistsError):
            message = "That destination already exists. Choose a new filename; nothing was overwritten."
        elif isinstance(exc, PermissionError):
            message = "Access denied. Choose a writable export folder or check index permissions."
        elif isinstance(exc, sqlite3.OperationalError) and "locked" in str(exc).lower():
            message = "Index is busy. Finish the Bridge operation, then refresh."
        elif isinstance(exc, (sqlite3.Error, KeyError, TypeError, RecursionError)):
            message = "Index could not be read safely. Use Bridge Verify index on a copy; no repair was attempted."
        else:
            message = str(exc)
        self.send_payload(422, {"error": message})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--store", type=Path, default=bridge.default_store())
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--no-open", action="store_true", help="Print URL without opening the default browser")
    args = parser.parse_args()
    with BrowserServer(args.store, args.port) as server:
        print("VOXIS Record Browser " + VERSION, flush=True)
        print("Index: " + str(server.index), flush=True)
        print("Open this local session: " + server.launch_url, flush=True)
        print("Use Stop Browser in the interface to end this session.", flush=True)
        if not args.no_open:
            webbrowser.open(server.launch_url)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
