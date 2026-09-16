"""C02 API tests use disposable synthetic records; no live index is touched."""
import hashlib
import http.client
import json
from pathlib import Path
import sqlite3
from contextlib import closing
import tempfile
import threading
import unittest

import browser
import store
from test_bridge import stem_fixture, wxr_fixture, raw


class BrowserTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.index = self.root / "index.sqlite"
        self.server = browser.BrowserServer(self.index)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop)

    def stop(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)

    def put(self, data, name="sample.json", session=None):
        source = self.root / name
        source.write_bytes(data if isinstance(data, bytes) else raw(data))
        return store.ingest(self.index, source, session)

    def request(self, route, data=None, headers=None, authenticated=True):
        h = {"Origin": self.server.origin}
        if authenticated:
            h["X-VOXIS-Token"] = self.server.token
        if data is not None:
            h["Content-Type"] = "application/json"
        h.update(headers or {})
        c = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=10)
        try:
            c.request("POST" if data is not None else "GET", route,
                      body=json.dumps(data) if data is not None else None, headers=h)
            r = c.getresponse()
            content = r.read()
            return r.status, json.loads(content) if "application/json" in r.getheader("Content-Type", "") else content, dict(r.getheaders())
        finally:
            c.close()

    def test_missing_and_empty_are_distinct_without_creation(self):
        code, data, _ = self.request("/api/records")
        self.assertEqual((code, data["state"]), (200, "missing"))
        self.assertFalse(self.index.exists())
        with store.connection(self.index, create=True):
            pass
        before = self.index.read_bytes()
        self.assertEqual(self.request("/api/records")[1]["state"], "empty")
        self.assertEqual(before, self.index.read_bytes())

    def test_list_matches_bridge_and_preserves_duplicate_identity(self):
        stem = self.put(stem_fixture(), "stem.json", "SEARCH-synthetic")
        self.put(stem_fixture(), "stem-again.json", "SEARCH-second")
        self.put(wxr_fixture(), "wxr.json")
        before = self.index.read_bytes()
        rows = self.request("/api/records")[1]["records"]
        self.assertEqual(rows, store.records(self.index))
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["id"], stem["id"])
        self.assertEqual(rows[0]["search_session_refs"], ["SEARCH-second", "SEARCH-synthetic"])
        self.assertEqual(before, self.index.read_bytes())

    def test_inspect_preserves_native_content_and_declarations(self):
        for n, fixture in enumerate([stem_fixture(), wxr_fixture()]):
            b = b"\xef\xbb\xbf\r\n" + raw(fixture) + b"\r\n"
            result = self.put(b, f"fixture-{n}.json")
            before = self.index.read_bytes()
            code, data, _ = self.request("/api/record?id=" + result["id"])
            self.assertEqual(code, 200)
            self.assertEqual(json.loads(data["native"]), fixture)
            self.assertEqual(data["summary"]["research_eligibility"], "not_assessed")
            self.assertEqual(data["summary"], result["summary"])
            self.assertEqual(before, self.index.read_bytes())

    def test_export_is_exact_for_both_native_types(self):
        for n, fixture in enumerate([stem_fixture(), wxr_fixture()]):
            b = b"\xef\xbb\xbf \r\n" + raw(fixture) + b"\r\n "
            result = self.put(b, f"fixture-{n}.json")
            before = self.index.read_bytes()
            target = self.root / f"output-{n}.json"
            code, data, _ = self.request("/api/export", {"id": result["id"], "path": str(target)})
            self.assertEqual(code, 200)
            self.assertEqual(target.read_bytes(), b)
            self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(), result["id"])
            self.assertEqual(data["bytes"], len(b))
            self.assertEqual(before, self.index.read_bytes())

    def test_no_overwrite_bad_destination_or_implicit_folder_creation(self):
        record = self.put(wxr_fixture())
        target = self.root / "existing.json"; target.write_bytes(b"keep")
        for path in [str(target), str(self.index), "relative.json", str(self.root / "absent" / "x.json"), str(self.root / "x.cmd"), str(self.root / "NUL.json")]:
            self.assertEqual(self.request("/api/export", {"id": record["id"], "path": path})[0], 422)
        self.assertEqual(target.read_bytes(), b"keep")
        self.assertFalse((self.root / "absent").exists())

    def test_missing_record_and_invalid_id_have_actionable_errors(self):
        self.put(stem_fixture())
        for rid in ["bad", "0" * 64]:
            code, data, _ = self.request("/api/record?id=" + rid)
            self.assertEqual(code, 422)
            self.assertTrue(data["error"])

    def test_corrupt_original_and_summary_block_export(self):
        record = self.put(wxr_fixture())
        with closing(sqlite3.connect(self.index)) as db, db:
            db.execute("UPDATE records SET summary='{}'")
        target = self.root / "out.json"
        code, data, _ = self.request("/api/export", {"id": record["id"], "path": str(target)})
        self.assertEqual(code, 422)
        self.assertIn("summary", data["error"])
        with closing(sqlite3.connect(self.index)) as db, db:
            db.execute("UPDATE records SET original=?", (b"{}",))
        self.assertEqual(self.request("/api/export", {"id": record["id"], "path": str(target)})[0], 422)
        self.assertFalse(target.exists())

    def test_invalid_unsupported_and_invalidated_remain_distinct(self):
        fixtures = [(b"\xff", "invalid"), ({"schema":"future"}, "unsupported"),
                    ({"event_type":"measured_relation_invalidated", "event_id":"synthetic-history", "evidentiary_use":"prohibited"}, "invalidated")]
        for n, (fixture, status) in enumerate(fixtures):
            result = self.put(fixture, f"state-{n}.json")
            code, data, _ = self.request("/api/record?id="+result["id"])
            self.assertEqual(code, 200)
            self.assertEqual(data["record"]["status"], status)
            self.assertNotEqual(data["summary"]["research_eligibility"], "valid")
            target = self.root / f"retained-{n}.json"
            self.assertEqual(self.request("/api/export", {"id":result["id"],"path":str(target)})[0], 200)
            self.assertEqual(target.read_bytes(), store.retrieve(self.index,result["id"])[0])

    def test_broken_or_unrelated_database_is_not_modified(self):
        self.index.write_bytes(b"not sqlite")
        before = self.index.read_bytes()
        code, data, _ = self.request("/api/records")
        self.assertEqual(code, 422)
        self.assertIn("read safely", data["error"])
        self.assertEqual(before, self.index.read_bytes())

    def test_locked_index_reports_busy(self):
        self.put(wxr_fixture())
        with closing(sqlite3.connect(self.index)) as db, db:
            db.execute("BEGIN EXCLUSIVE")
            code, data, _ = self.request("/api/records")
            self.assertEqual(code, 422)
            self.assertIn("busy", data["error"])

    def test_token_origin_and_host_protect_all_private_routes(self):
        record = self.put(wxr_fixture())
        for route in ["/api/info", "/api/records", "/api/record?id="+record["id"]]:
            self.assertEqual(self.request(route, authenticated=False)[0], 403)
            self.assertEqual(self.request(route, headers={"Origin":"http://foreign.invalid"})[0], 403)
            self.assertEqual(self.request(route, headers={"Host":"foreign.invalid"})[0], 403)
        target = self.root / "never.json"
        self.assertEqual(self.request("/api/export", {"id":record["id"],"path":str(target)}, authenticated=False)[0], 403)
        self.assertEqual(self.request("/api/export", {"id":record["id"],"path":str(target)}, headers={"Origin":"null"})[0], 403)
        self.assertFalse(target.exists())

    def test_only_fixed_assets_are_served_and_no_import_endpoint(self):
        code, body, headers = self.request("/", authenticated=False)
        self.assertEqual(code, 200)
        self.assertIn(b"Record Browser", body)
        self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])
        self.assertEqual(headers["Cache-Control"], "no-store")
        for route in ["/../store.py", "/browser.py", "/api/import"]:
            self.assertEqual(self.request(route)[0], 404)
        self.assertEqual(self.request("/api/import", {"x":1})[0], 404)
        self.assertFalse(self.index.exists())

    def test_new_server_reopens_same_index(self):
        record = self.put(stem_fixture())
        before = self.index.read_bytes()
        second = browser.BrowserServer(self.index)
        try:
            self.assertNotEqual(self.server.token, second.token)
            self.assertEqual(browser.inspect_record(second.index, record["id"])["record"]["id"], record["id"])
        finally:
            second.server_close()
        self.assertEqual(before, self.index.read_bytes())


if __name__ == "__main__":
    unittest.main()
