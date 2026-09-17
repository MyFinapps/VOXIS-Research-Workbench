"""C01 regression suite. All input geometries are synthetic engineering fixtures."""
import copy
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

import adapters
import store


def stem_fixture():
    config = {"folio": "2v", "pivot": {"x": 0, "y": 0},
              "overlay": {"origin": {"x": 0, "y": 0}, "anchor": {"x": 0, "y": 0}, "scale": 1, "opacity": .5},
              "contactMode": "tip", "tolerance": 0, "stem": [{"x": 0, "y": 0}, {"x": 10, "y": 0}],
              "regions": [{"id": "demo", "label": "Synthetic region", "x": 10, "y": 0, "r": 4}],
              "timing": {"enabled": False, "bpm": 60}, "camera": {"x": 0, "y": 0, "size": 400}}
    take = {"id": "synthetic-take", "config": config, "mapping": "single-click-432Hz-45ms/1", "duration": 1000,
            "samples": [{"t": 0, "angle": 0}, {"t": 1000, "angle": 90}],
            "events": [{"kind": "enter", "regionId": "demo", "t": 0, "angle": 0, "initial": True},
                       {"kind": "exit", "regionId": "demo", "t": 300, "angle": 27, "initial": False}]}
    return {"schema": "voxis.stem-session/1", "appVersion": "0.1.0", "detector": "polyline-circle-subdivision/1",
            "id": "synthetic-session", "createdAt": "2026-01-01T00:00:00Z", "angle": 0, "config": copy.deepcopy(config),
            "sources": {"pdfSHA256": "0" * 64, "assets": [{"path": "synthetic.jpg", "folio": "2v",
                        "sha256": "1" * 64, "width": 100, "height": 100}]}, "takes": [take]}


def wxr_fixture():
    folio = {"model": [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, .125, -.25, -2, 1],
             "anchor": [.02, -.39, .011], "alpha": .72, "scale": 1.1,
             "flipped": False, "mode": "pivot", "step": 1}
    state = {"schemaVersion": 1, "prototypeId": "P002-WXR-003", "capturedAt": "2026-01-01T00:00:00Z",
             "selected": "r", "folios": {"r": copy.deepcopy(folio), "v": copy.deepcopy(folio)}}
    return {"exportSchema": "VOXIS.configuration-export.v1", "prototypeId": "P002-WXR-003",
            "exportedAt": "2026-01-01T00:00:00Z", "current": state, "savedSlots": {"A": copy.deepcopy(state)}}


def raw(data):
    return json.dumps(data, ensure_ascii=False).encode("utf-8")


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.db = self.root / "index.sqlite"

    def put(self, data, name="input.json", session=None):
        path = self.root / name
        path.write_bytes(data if isinstance(data, bytes) else raw(data))
        return store.ingest(self.db, path, session)

    def test_byte_exact_roundtrip_including_bom_whitespace_and_unicode(self):
        data = wxr_fixture(); data["note"] = "J.T. — test"
        original = b"\xef\xbb\xbf \r\n" + raw(data) + b"\r\n "
        result = self.put(original)
        self.assertEqual(result["summary"]["status"], "structure_checked")
        target = self.root / "export.json"
        store.export_original(self.db, result["id"], target)
        self.assertEqual(original, target.read_bytes())
        self.assertTrue(store.verify(self.db)["ok"])

    def test_stem_timing_and_native_values_are_preserved(self):
        data = stem_fixture()
        result = self.put(data)
        recovered, summary = store.retrieve(self.db, result["id"])
        self.assertEqual(json.loads(recovered), data)
        self.assertEqual(summary["captures"][0]["duration_ms"], 1000)
        self.assertEqual(summary["research_eligibility"], "not_assessed")
        self.assertTrue(any("not recomputed" in s for s in summary["warnings"]))

    def test_wxr_preserves_matrices_anchors_and_slots(self):
        data = wxr_fixture()
        result = self.put(data)
        self.assertEqual(result["summary"]["captures"][0]["folios"], data["current"]["folios"])
        self.assertEqual(result["summary"]["captures"][1]["slot"], "A")
        self.assertIsNone(result["summary"]["representations"][0]["identity"])

    def test_same_folio_different_hashes_stay_distinct(self):
        a = stem_fixture(); b = copy.deepcopy(a); b["sources"]["assets"][0]["sha256"] = "2" * 64
        ra, rb = self.put(a, "a.json"), self.put(b, "b.json")
        self.assertNotEqual(ra["id"], rb["id"])
        self.assertNotEqual(ra["summary"]["representations"][0]["identity"], rb["summary"]["representations"][0]["identity"])
        self.assertEqual(len(store.records(self.db)), 2)

    def test_duplicate_is_idempotent_and_links_are_explicit(self):
        first = self.put(wxr_fixture(), session="SEARCH-existing")
        second = self.put(wxr_fixture(), session="SEARCH-existing")
        self.put(wxr_fixture(), session="SEARCH-other")
        self.assertEqual(first["id"], second["id"])
        self.assertTrue(second["duplicate"])
        rows = store.records(self.db)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["search_session_refs"], ["SEARCH-existing", "SEARCH-other"])

    def test_unassigned_import_does_not_create_a_search_session(self):
        self.put(wxr_fixture())
        self.assertEqual(store.records(self.db)[0]["search_session_refs"], [])

    def test_concurrent_duplicate_imports_commit_one_record(self):
        source = self.root / "concurrent.json"; source.write_bytes(raw(wxr_fixture()))
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(lambda _: store.ingest(self.db, source, "SEARCH-concurrent"), range(4)))
        self.assertEqual(sum(not r["duplicate"] for r in results), 1)
        self.assertEqual(len(store.records(self.db)), 1)
        self.assertTrue(store.verify(self.db)["ok"])

    def test_verify_detects_summary_corruption(self):
        result = self.put(wxr_fixture())
        with sqlite3.connect(self.db) as db:
            db.execute("UPDATE records SET summary=? WHERE id=?", ('{}', result["id"]))
        self.assertFalse(store.verify(self.db)["ok"])

    def test_malformed_duplicate_keys_and_nonfinite_are_retained_invalid(self):
        for i, value in enumerate([b'{"x":', b'{"x":1,"x":2}', b'{"x":NaN}', b'\xff', b'[]']):
            result = self.put(value, str(i) + ".json")
            self.assertEqual(result["summary"]["status"], "invalid")
            self.assertEqual(store.retrieve(self.db, result["id"])[0], value)

    def test_unknown_versions_are_retained_without_acceptance(self):
        a = stem_fixture(); a["appVersion"] = "9.0"
        for i, value in enumerate([a, {"exportSchema": "future/2"}]):
            result = self.put(value, str(i) + ".json")
            self.assertEqual(result["summary"]["status"], "unsupported")

    def test_invalid_stem_trajectory_and_events_rejected(self):
        for mutate in [lambda s: s["takes"][0]["samples"].append({"t": 1000, "angle": 120}),
                       lambda s: s["takes"][0]["events"][0].update(regionId="absent"),
                       lambda s: s["takes"].append(copy.deepcopy(s["takes"][0])),
                       lambda s: s["takes"][0]["config"]["regions"].append(copy.deepcopy(s["takes"][0]["config"]["regions"][0]))]:
            s = stem_fixture(); mutate(s)
            self.assertEqual(adapters.inspect(raw(s))["status"], "invalid")

    def test_wxr_bad_matrix_anchor_and_controls_rejected(self):
        for key, value in [("model", [1] * 15), ("anchor", "2r.root"), ("scale", True), ("mode", "script")]:
            s = wxr_fixture(); s["current"]["folios"]["r"][key] = value
            self.assertEqual(adapters.inspect(raw(s))["status"], "invalid")

    def test_historical_invalidation_is_not_promoted(self):
        data = {"event_type": "measured_relation_invalidated", "event_id": "history-only",
                "search_session_id": "EX-existing", "evidentiary_use": "prohibited"}
        result = self.put(data)
        self.assertEqual(result["summary"]["status"], "invalidated")
        self.assertEqual(result["summary"]["research_eligibility"], "prohibited")

    def test_failed_transaction_rolls_back_record_and_session_link(self):
        self.put(wxr_fixture())
        with sqlite3.connect(self.db) as db:
            db.execute("CREATE TRIGGER deny_link BEFORE INSERT ON session_links BEGIN SELECT RAISE(ABORT, 'injected failure'); END")
        with self.assertRaises(sqlite3.IntegrityError):
            self.put(stem_fixture(), session="SEARCH-test")
        self.assertEqual(len(store.records(self.db)), 1)
        self.assertTrue(store.verify(self.db)["ok"])

    def test_corrupt_original_blocks_export(self):
        r = self.put(wxr_fixture())
        with sqlite3.connect(self.db) as db:
            db.execute("UPDATE records SET original=? WHERE id=?", (b'{}', r["id"]))
        self.assertFalse(store.verify(self.db)["ok"])
        with self.assertRaisesRegex(ValueError, "checksum"):
            store.export_original(self.db, r["id"], self.root / "out.json")
        self.assertFalse((self.root / "out.json").exists())

    def test_existing_export_target_is_never_overwritten(self):
        r = self.put(wxr_fixture())
        with self.assertRaises(FileExistsError):
            store.export_original(self.db, r["id"], self.root / "input.json")
        self.assertEqual((self.root / "input.json").read_bytes(), raw(wxr_fixture()))

    def test_oversize_input_does_not_create_index(self):
        p = self.root / "big.json"; p.write_bytes(b' ' * (store.MAX_BYTES + 1))
        with self.assertRaisesRegex(ValueError, "8 MiB"):
            store.ingest(self.db, p)
        self.assertFalse(self.db.exists())

    def test_unrelated_database_is_not_modified(self):
        with sqlite3.connect(self.db) as db:
            db.execute("CREATE TABLE unrelated (x)")
        before = self.db.read_bytes()
        with self.assertRaisesRegex(ValueError, "schema"):
            self.put(wxr_fixture())
        self.assertEqual(self.db.read_bytes(), before)

    def test_missing_read_does_not_initialize_database(self):
        with self.assertRaises(ValueError):
            store.records(self.db)
        self.assertFalse(self.db.exists())

    def test_fresh_process_reopen_and_unchanged_read_operations(self):
        data = wxr_fixture(); result = self.put(data)
        before = self.db.read_bytes()
        script = str(Path(__file__).with_name("bridge.py"))
        for command in [["list"], ["show", result["id"]], ["verify"]]:
            process = subprocess.run([sys.executable, script, "--store", str(self.db)] + command,
                                     capture_output=True, text=True, check=True)
            self.assertTrue(json.loads(process.stdout))
        self.assertEqual(self.db.read_bytes(), before)

    def test_real_invalidated_repository_fixture(self):
        fixture = Path(__file__).resolve().parents[2] / "experiments/EX-GRAMMAR-001/canonical_event.json"
        if not fixture.exists():
            self.skipTest("Repository historical fixture not bundled with standalone release")
        result = store.ingest(self.db, fixture)
        self.assertEqual(result["summary"]["status"], "invalidated")
        self.assertEqual(store.retrieve(self.db, result["id"])[0], fixture.read_bytes())


if __name__ == "__main__":
    unittest.main()
