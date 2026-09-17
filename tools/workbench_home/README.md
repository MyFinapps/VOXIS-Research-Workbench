# Workbench Home 0.1 — C03 candidate

One local starting point for Record Browser, Record Bridge, Stem Lab, WXR-003 and
the Resonance Engine. Existing instruments retain their own files and data.
**Forge integration acceptance is pending.** A configured path or running process
is not verification of the instrument or of manuscript geometry or meaning.

## Start on The Forge

1. Extract the entire candidate ZIP into a new folder. Keep `workbench_home` and
   `record_bridge` beside each other. Do not run inside the ZIP.
2. Open `workbench_home` and double-click **Start-Workbench-Home.cmd**. Python
   3.10+ is required. No Node, installation, network or account is needed for Home.
3. Your default browser opens Home. If opening fails, use the local session address
   in the launcher window. Do not share that address: it carries the session token.
4. Choose **Configure** beside each instrument. Paste its confirmed location.
   Saving does not launch it. No source files, captures or indexes are moved.
5. Choose **Open**. Browser opens its session in a new tab; **Return** reuses it.
   If a popup is blocked, use **Open instrument session** in the message bar.

| Instrument | Location to configure | Launch behavior |
| --- | --- | --- |
| Record Browser | Existing `Start-Record-Browser.cmd` or `browser.py` | Runs the unchanged `browser.py --no-open`, probes its authenticated local info endpoint, opens its fresh session. Uses the instrument's default Bridge index. |
| Record Bridge | Existing `Start-Record-Bridge.cmd` or `bridge.py` | Runs unchanged `bridge.py` in a new Windows console. Import/verify remain explicit Bridge actions. |
| Stem Lab | Existing `.html` or `.htm` file | Sends its local file URL to the machine's default browser; no remote upload. |
| WXR-003 | Confirmed HTTPS instrument URL | Opens that URL. Desktop opening does not verify Quest behavior or the deployed build. |
| Resonance Engine | Existing `.py`, `.exe`, `.cmd`, `.bat` or `.ps1` launcher | Uses its folder as working directory. No arbitrary argument field, automatic dependency install or PowerShell execution-policy bypass. |

For Browser/Bridge, choosing the standard `.cmd` wrapper resolves its sibling
Python entry point. Home deliberately invokes that entry directly with its own
Python interpreter instead of invoking a batch shell; this enables session handoff
and process tracking. This is a documented implementation refinement to the
original launcher-oriented definition. Custom wrapper flags are not imported.
The interpreter used by Home must meet each instrument's needs. A custom Python
virtual environment or additional command arguments are outside 0.1's adapter;
use an existing suitable native launcher for Resonance or keep it unconfigured.

The Resonance Engine executable location is unresolved in the project inventory.
Do not guess it. Its unavailable entry remains visible and blocks full common-launch
acceptance until the correct existing launcher is configured and tested.

## Settings and identities

Default private settings: `%LOCALAPPDATA%\VOXIS\WorkbenchHome\home.json` on Windows;
otherwise `~/.local/share/VOXIS/WorkbenchHome/home.json`. Help displays the actual
path. It stores fixed instrument IDs, locations, operator-declared versions,
entry-file SHA-256 values and launch reminders. Session tokens are never persisted.

Home checks entry-file bytes again before launching. Changed or missing files
require inspection and reconfiguration. This is not a whole-package audit, code
trust assessment or independent verification of the declared version. Configure
only known, trusted local instruments. Home does not protect against another
program already running as your account.

Only one Home instance may use a given configuration at a time. Writes replace
settings atomically; invalid configuration is left untouched. Home's first visit
does not create an instrument index. An OS lock file is created beside settings.

## Process lifecycle and recovery

- **Configured**: location saved; not a reachability or runtime claim.
- **Running**: Home's launched process has not exited. Browser additionally passed
  an authenticated readiness check before Home offers its session.
- **Check existing session**: after a Home restart/crash, or an exited Resonance wrapper,
  a launched instrument may still be running. Open cannot create another copy.
- Close the instrument and its launcher first, then **Configure → I have closed
  the previous instrument session → Clear launch reminder**. This acknowledges
  your observation; Home does not kill a process or prove that children stopped.
- Browser's own **Stop Browser** shuts down its server. A later Open creates a new
  session. Bridge and Resonance are stopped in their own windows.
- Bridge **Q Quit** ends the directly launched process. Within the next Home
  refresh (up to five seconds), Bridge returns to **Configured** with **Open**
  enabled. No manual reminder clearing is needed while the same Home is running.
  A nonzero Bridge exit also permits retry and displays its exit code.
- When upgrading from the first candidate, clear any old Bridge reminder once
  after confirming Bridge is closed; persisted reminders cannot prove an exit.
- **Close Home** stops only Home. Closing its tab leaves Home running. Never kill
  processes by name/port as a recovery shortcut. External instrument processes
  started outside Home are not discovered or claimed as Home-owned.
- Failed launch/readiness checks preserve uncertainty and show guidance. Check
  the launcher and configured files. For an unresolved hidden Browser startup,
  inspect the exact Home-started process before retrying; do not terminate other
  Python sessions. Fixed-port conflicts in external instruments must be resolved
  in their own launchers. Home and Browser use free ports by default.
- If Home itself cannot bind a requested fixed port, it exits with the OS error
  without touching other services. Start without `--port` to choose a free port.
- Batch launcher paths containing `% ! & | < > ^ "` are refused to prevent shell
  interpretation. Spaces are supported. Use an appropriate existing launcher in
  a path without these characters. Python/PowerShell paths are passed as arguments.

## Backup and restore

Close Browser, Bridge and every other index user before copying the SQLite index.
Keep the live index local, outside sync folders. To restore, first preserve the
current file under a new name; test the backup in a disposable location with
Bridge `--store ... verify`. Do not replace a live index as a test. Home provides
instructions, not a database backup/restore automation.

For Home settings, close Home, preserve `home.json` and copy a known-good backup
into its place. Launch reminders are deliberately preserved across restoration;
clear them only after confirming the instrument is closed. No repair/migration
or rollback is attempted automatically.

## Development and package

```text
python -m unittest discover -s tools/workbench_home -v
python tools/workbench_home/home.py --config /absolute/disposable/home.json --no-open
python tools/workbench_home/package_home.py /new/output.zip --source-ref FULL_COMMIT_SHA
```

Packaging requires Git and exact committed bytes (use `core.autocrlf=false` for
that checkout). The package verifies bundled files against the resolved commit,
uses exclusive creation, deterministic entries and SHA256SUMS.txt. Extracted runtime
needs only Python. BUILD.json identifies the source, not target-machine acceptance.

## Forge acceptance checklist

Use the existing [Forge integration task](https://app.clickup.com/t/86bc1v97h).
Record the candidate commit from BUILD.json, device, date, operator and outcomes.

1. Extract; start by double-click; check desktop layout and keyboard navigation.
2. Configure actual instrument locations; restart Home; confirm settings persist.
3. Through Home launch Browser, inspect both supported records and export both to
   fresh filenames. Compare SHA-256 to original record IDs; check index unchanged.
4. Return to the same Browser session without a duplicate; Stop Browser; launch again.
5. Launch Bridge, Stem Lab, WXR and the confirmed Resonance launcher; record each
   exact build and narrow smoke-test result. Missing targets block full acceptance.
6. Use disposable paths for missing/changed file, startup error, path-with-spaces,
   duplicate launch, Home restart reminder and occupied-port checks. Never damage
   a working instrument or live database to manufacture an error.
7. Close Home while a disposable launched instrument is running. Confirm it remains
   separate. Reopen Home, close that instrument, clear its reminder and relaunch.
8. Test backup/restore guidance with disposable copies. Confirm private config,
   captures and tokens stay out of public reports.

Native recall, cross-engine replay, FREEZE/VISTA acceptance, and manuscript research
validation are outside this release. Existing Browser Forge acceptance at
`97bbccb3eec4d15b08205d7a07115fdd14497feb` does not substitute for Home acceptance.
