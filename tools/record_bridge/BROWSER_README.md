# VOXIS Record Browser 0.1 — C02 candidate

A local visual companion to Record Bridge. Browse preserved Stem Lab and WXR
records, inspect native contents and validation limits, and export exact originals.
This candidate is separate from Bridge PR #6 and does not merge it.

## Start on Windows

1. Extract the entire candidate ZIP into a new folder. Do not run from inside the ZIP.
2. Double-click `Start-Record-Browser.cmd`. Python 3.10 or later must be available,
   as for Record Bridge. No Node, package installation or internet connection is needed.
3. The default browser opens a private local session. If automatic opening fails,
   copy the local session address printed in the launcher window into your browser.
4. Choose a record. Switch between **Overview** and **Native content**.
5. **Export original** opens a destination form. Enter the full path of a new JSON
   file in an existing folder, then choose **Save original**. This version uses a
   path field, not a native operating-system file chooser. Cancel writes nothing.
6. Choose **Stop Browser**, then **Stop session** to end the local server. Merely
   closing the browser tab leaves the server running; closing its launcher window
   also ends the process. The index remains intact.

The default index is `%LOCALAPPDATA%\VOXIS\RecordBridge\index.sqlite`, the same
as Bridge. **Index details** shows the actual location. The candidate does not
copy, create, import into or migrate an index. If it is missing, use the existing
Bridge import workflow, then Refresh. A missing index and an empty index have
different messages.

The ZIP also includes `Start-Record-Bridge.cmd` for the existing import workflow.
Do not place the live SQLite file in Dropbox. For an archive copy, close every
process using it before copying it.

## What this candidate does

- Search record names, IDs, formats, statuses and Search Session references.
- Filter by Stem Lab, WXR-003 or other retained records.
- Show stable identities, producer/version when declared, import/capture times,
  session assignments, structural status, evidence eligibility and stored warnings.
- Render imported content as text, including HTML-like content. Invalid UTF-8 is
  shown as hexadecimal bytes; export still preserves the original bytes.
- Inspect through the existing Bridge storage and adapter contracts.
- Block export when original checksum or stored-summary comparison fails.
- Export with exclusive file creation: existing files cannot be overwritten.
- Run only on loopback, with a random per-session token, Host/Origin checks and
  no remote assets, accounts, telemetry or record uploads.

The local session address is private. Do not share it. This is a local utility,
not an internet-facing service. It does not provide protection against another
program already running with access to your user account.

## Evidence boundaries

`structure_checked` means structural intake checks passed. It does not validate
geometry, manuscript meaning, source-image identity or replay. Stored asset
checksums remain declarations. Invalidated history remains prohibited for
evidentiary use. Empty Search Session references mean **Unassigned**.

No record editing, deletion, browser-side import, native recall, cross-engine
replay, live audio, image fetching or Workbench Home integration is included.
The existing Bridge implementation files are unchanged by this candidate.

## Development and verification

From the repository root:

```text
python -m unittest discover -s tools/record_bridge -v
python tools/record_bridge/browser.py --store /absolute/path/to/test-index.sqlite --no-open
```

Use `--port` only when a fixed local port is needed. The default chooses a free
port. Windows users can use `py -3` instead of `python`.

The 34-test Bridge/Browser suite covers byte-exact exports for both native types,
duplicate identity and session associations, no-overwrite and invalid destinations,
read-only access, missing/empty/locked/corrupt indexes, corrupted originals and
summaries, preserved invalid/unsupported/invalidated records, session protection,
fixed asset serving and reopening the index. Tests use disposable synthetic data.

Automated/Linux results do not certify the Windows launcher or Forge usability.
The target-machine acceptance gate remains open until the operator completes the
visual launch → browse → inspect → export → close/reopen journey and records the
candidate identity, index, results and any defects. Corruption scenarios must use
disposable fixtures, never the live index. Public evidence must omit private
captures, absolute user paths and session tokens.

## Acceptance mapping

| Checklist area | Candidate behavior | Remaining device gate |
| --- | --- | --- |
| RB-01 / RB-12 | Windows launcher, local UI, keyboard controls | Forge launch and usability |
| RB-02 / RB-03 / RB-04 | List, details, provenance and evidence distinctions | Confirm against Forge index |
| RB-05 | Distinct retained states; native content is inert text | Isolated fixture review |
| RB-06 / RB-07 | Byte-preserving exclusive export; cancel/error states | Forge visual export and permissions |
| RB-08 / RB-09 | Read-only reopen, missing and empty handling | Forge close/reopen |
| RB-10 | Busy/corrupt errors; unsafe export blocked | Disposable fixtures only |
| RB-11 | Existing content identity and associations reused | No Browser import introduced |

## Dependency

This branch is based on PR #6's documentation head
`f64ce25b87eb4dd983c3a4d46a382f362fc4c4a5`. Its core Bridge implementation is the
same candidate previously inspected at `826e24b16e5ff5f39556ec91281aea9b5ad5c8e0`.
Review and merge decisions remain separate from prototype testing.
