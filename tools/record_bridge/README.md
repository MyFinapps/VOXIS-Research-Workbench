# VOXIS Record Bridge C01

Version 0.1.0. Local intake for Stem Lab sessions and WXR-003 configuration exports.
This is the first consolidation step: one index of captures with their originals intact.
It is an inspection utility, not a replacement for the existing instruments.

## Start on Windows

1. Extract the candidate ZIP into its own folder, or open this folder in a repository checkout.
2. Double-click `Start-Record-Bridge.cmd`. Python 3.10 or later must already be installed.
3. Choose **1 Import JSON**, then paste the path of a JSON file saved by Stem Lab or WXR-003.
4. Enter an existing Search Session reference, or press Enter to leave it unassigned.
5. Choose **2 List records** or **3 Inspect record**. **4 Export original** writes an unchanged copy to a new filename.
6. Quit, reopen the launcher, and list the records again. They should remain present.

No package installation, server, browser, network connection, audio, or manuscript images are needed.
The Windows launcher is supplied for target-machine trial; Windows execution has not been verified here.
The core and subprocess workflow are tested on Linux with Python.

The default index is `%LOCALAPPDATA%\VOXIS\RecordBridge\index.sqlite` on Windows,
or `~/.local/share/VOXIS/RecordBridge/index.sqlite` when LOCALAPPDATA is absent.
The utility prints the location on startup. It never searches your drives or contacts the running engine.
Keep this live index local. To preserve the entire index, close the utility and copy its SQLite file.
Portable original JSON exports can be filed in the existing research archive.

## What each status means

| Status | Meaning |
| --- | --- |
| structure_checked | Supported native shape passes C01 structural checks. Geometry, source-image identity and native replay are not verified. |
| invalid | JSON or required structure is invalid. Original bytes retained for inspection; excluded from research use. |
| unsupported | JSON is readable but its format or producer version is not supported. Original retained. |
| invalidated | Recognized historical invalidation record. Retained as history; evidentiary use prohibited. |

Successful intake never sets evidence eligibility to valid. Structure-checked records remain `not_assessed`.
Files over 8 MiB are declined before the index is opened; their originals remain at the input location.
Duplicate keys, malformed UTF-8, NaN constants and invalid JSON are retained with an invalid status.
Recognized but structurally invalid records remain exportable as their original bytes.

## Supported contracts

- Stem Lab `voxis.stem-session/1`, app `0.1.0`, detector `polyline-circle-subdivision/1`.
  Captures preserve configuration, source declarations, take IDs, millisecond timestamps,
  unwrapped degree angles and entry/exit events. No contact detector is reimplemented or invoked.
  Native Stem Lab validation remains necessary before replay.
- WXR-003 `VOXIS.configuration-export.v1`, captured state `schemaVersion: 1`.
  Native `folios.r` and `folios.v` matrices, numeric anchor arrays, selected folio,
  opacity, scale, flip, mode, step and slots are retained. Fingerprint shape is checked;
  its value is not recomputed. WXR export does not provide per-image hashes, so those
  representation identities are explicitly unresolved. No 3D-to-2D conversion occurs.
- Canonical `measured_relation_invalidated` events with `evidentiary_use: prohibited`
  can be cataloged as history. Other Grammar Kernel records remain unsupported originals for now.

SHA-256 identifies the exact imported file bytes. Stem Lab representation summaries use their
declared asset checksums, preserving differences even when folio labels match. The bridge neither
retrieves source assets nor asserts that declared checksums are correct. It follows no paths or URLs
inside imported documents, and never interprets source content as code.

`--session` creates an explicit index association with an existing Search Session reference.
It does not create a Search Session record, validate that reference, preregister an experiment,
or replace the established Folio / Representation / Observation / Search Session / Alignment /
Evidence / Hypothesis model. Missing media links remain empty; captures do not acquire invented links.

## Commands

Run these in the folder containing `bridge.py`. Place `--store` before the command.

```powershell
py -3 bridge.py --store "C:\VOXIS-C01-Trial\index.sqlite" import "C:\Captures\session.json" --session "SEARCH-existing"
py -3 bridge.py --store "C:\VOXIS-C01-Trial\index.sqlite" list
py -3 bridge.py --store "C:\VOXIS-C01-Trial\index.sqlite" show FULL_64_CHARACTER_ID
py -3 bridge.py --store "C:\VOXIS-C01-Trial\index.sqlite" export FULL_64_CHARACTER_ID "C:\Captures\recovered.json"
py -3 bridge.py --store "C:\VOXIS-C01-Trial\index.sqlite" verify
```

On Linux/macOS use `python3` in place of `py -3`.
CLI output is JSON; menu mode is for interactive use. Exit code 0 indicates completion,
2 indicates a retained invalid/unsupported/historical import or failed integrity check,
and 1 indicates an operating error. Do not retry imports blindly based only on a nonzero exit code.

## Persistence and failure behavior

Original bytes and their intake summary commit in one SQLite transaction. The file hash is the
record key, so repeated imports cannot silently duplicate a capture. One capture may explicitly
link to several Search Session references. Failed transactions roll back the capture and link together.
No API updates or deletes originals. A previously imported summary is not silently regenerated
by another import; future adapter changes require an explicit versioned migration.

List, show and verify open the existing database read-only. Export checks the original checksum
and uses exclusive file creation so it cannot overwrite an existing source, export or database.
Verify checks SQLite integrity, original checksums, links and summaries against this adapter version.
This detects corruption relative to stored identities; it is not a digital signature or an adversarial audit.

## Validation and next gate

Run `python -m unittest discover -s tools/record_bridge -v` from the repository root,
or `python -m unittest -v test_bridge` from this folder.
Tests cover exact-byte exports, native field fidelity, distinct image hashes, duplicate intake,
explicit session links, malformed records, unsupported versions, historical invalidation,
transaction rollback, corrupted originals, no-overwrite export, size limits, unrelated databases,
read-only operations and reopening from fresh processes.

Before integrating into Workbench Home, trial one real export from each instrument on The Forge,
quit/reopen the bridge, and compare the exported originals. WXR-003 file import and cross-instrument
replay are not implemented here. Resonance checkpoint repair, the unresolved Alignment v2 source,
shared image equivalence, user-reported Stem Lab bugs, and interface consolidation remain separate tasks.

## Sources and implementation identity

- Workbench base: `162e4cd0bed7a6870814910ed21d9fc651cc1694`.
- WXR-003 source: `MyFinapps/voxis-p002-wxr-001`, commit
  `8a4297cc72950396546878387be391f7eefbd0a0`, `wxr-003/index.html` (`captureState`, `exportPayload`).
- Stem Lab v0.1 source: supplied standalone package, `source/core.js` and `source/app.js`.
- Historical fixture: Workbench `experiments/EX-GRAMMAR-001/canonical_event.json`.
- Architecture: VOXIS Workbench Consolidation Map v0.1, 16 September 2026, task C01.

Test fixtures are synthetic and do not assert manuscript relations. Raw research images,
personal paths, saved sessions and database files are not included in the source change.
