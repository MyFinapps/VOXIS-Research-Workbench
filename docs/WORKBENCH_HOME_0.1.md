# Workbench Home 0.1 — implementation definition

Status: defined, not implemented or accepted. Delivery follows Record Bridge and
Browser closure. Reuse the existing
[integration milestone](https://app.clickup.com/t/86bc1v7w9),
[entry-point task](https://app.clickup.com/t/86bc1v96m), and
[Forge integration task](https://app.clickup.com/t/86bc1v97h).

## Outcome

One local Windows entry point opens a Home surface from which J.T. can start or
open the existing instruments and Record Browser. Each entry explains its purpose,
configured location, known version and verification status. Unknown locations are
visible setup gaps, never guessed paths or working-looking launch buttons.

## First release

| Entry | Contract | Current integration prerequisite |
| --- | --- | --- |
| Record Browser | Start existing launcher, using the same Bridge index; open its fresh authenticated session | Resolve installed candidate location; never persist its session token |
| Record Bridge | Open existing import/verify utility | Resolve installed launcher; retain explicit import behavior |
| Stem Lab | Open configured standalone HTML in the default browser | Confirm current file and source identity |
| WXR-003 | Open the configured HTTPS instrument; label desktop vs Quest use | Confirm deployed URL/build; opening from Home is not Quest acceptance |
| Resonance Engine | Invoke its existing, verified local startup entry point | Executable location remains unresolved in the component inventory |

FREEZE, VISTA and the M1 prototype may be listed as experimental references with
their existing acceptance status. They are not dependencies for Home 0.1 closure
and must not be presented as accepted tools. Do not replace existing instruments.

## Architecture and data boundaries

- Use a small local launcher with an authenticated loopback Home service when
  process startup is required. A static web page alone cannot reliably start a
  local Windows command file. Prove one Browser launch end-to-end before expanding.
- A private local configuration maps fixed instrument IDs to explicit paths/URLs,
  working directories and launch types. Keep user paths out of public source.
  Resolve paths with spaces and launch from the instrument's required directory.
- UI requests select a configured ID; they never supply arbitrary shell commands.
  Apply the Browser's Host/Origin/session protections to process-launch routes.
- Launch is a user action. No auto-starting all engines, silent installs, source
  moves, database migration, record mutation, or background synchronization.
- For processes started by Home, track only those owned processes. Prevent duplicate
  starts or show a clear already-running state. Never kill processes by broad name
  or port. Closing Home leaves separately launched instruments alone unless the
  user explicitly chooses a supported stop action.
- Missing path, unavailable service, occupied fixed port and failed startup expose
  actionable recovery guidance. Distinguish configured, launched, reachable and
  verified; a reachable endpoint does not establish a matching build.
- Backup guidance requires closing users of the SQLite index before copying it.
  Restoration is explicit, preserves the previous copy, and is tested on fixtures.

## Acceptance

1. On The Forge, double-click the Home launcher; navigate by mouse and keyboard.
2. Configure confirmed entries once; settings survive a Home restart. Private
   configuration and tokens do not enter repository or public reports.
3. Launch Browser against the existing index, browse both record types and export
   unchanged originals. Home never creates an index when one is missing.
4. Launch/open each required instrument from its confirmed entry point. Record
   exact identities and narrow smoke-test results; unresolved entries block full
   common-launch acceptance rather than silently disappearing from scope.
5. Exercise spaces in paths, missing targets, startup failure and repeat launch.
   Test applicable occupied-port handling with isolated processes.
6. Stop/restart Home and verify process ownership, stored configuration and
   unchanged index. Document how each instrument is stopped.
7. Record the integrated build, operator, device, date, results and exceptions in
   the existing Forge integration task. Browser acceptance is supporting evidence,
   not a substitute for this new integration run.

## Work allocation

Retain the existing estimates: eight collaborative hours for implementation and
four for Forge integration, twelve total. A five-hour daily baseline with four
hours allocated and one hour reserved yields three workdays after prerequisites.
These are forecasts, not logged effort. The 5–8 hour capacity range does not create
an eight-hour commitment. Re-estimate if resolving instrument locations or the
launch proof of concept exceeds this allowance; preserve existing forecast dates
until the dependency gates and inventory are reconciled.

No native recall, cross-engine replay, new research experiment, manuscript meaning
claim, or Sunbow Bay work is part of Home 0.1.
