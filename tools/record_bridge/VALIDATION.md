# C01 validation record

16 September 2026. Candidate 0.1.0. Includes the initial Linux checks and a subsequent
operator-supplied Forge trial. No research-claim validation.

## Initial Linux checks

- Python standard-library regression suite: **21 tests passed** on Linux.
- Imported the existing Stem Lab v0.1 example: one 12,000 ms take, 721 trajectory
  samples and 10 entry/exit events. Structural intake succeeded.
- Exported the Stem Lab original and compared every byte with its input: identical.
- Imported and exported a synthetic WXR-003 fixture with current state and slot A:
  identical bytes, including matrices and numeric anchor arrays.
- Opened the index in fresh Python processes for list and verify: both records remained
  available, all integrity checks passed, and read-only calls left database bytes unchanged.
- Interactive menu list, verify and quit smoke check passed on Linux.
- Tests exercise simultaneous duplicate imports, failed-transaction rollback, corrupted
  originals and summaries, unsupported versions, malformed JSON, distinct representation
  hashes, invalidated history, oversized input, no-overwrite export and unrelated databases.

The WXR fixture is synthetic engineering data, not a capture from J.T.'s headset.
The existing EX-GRAMMAR-001 invalidated canonical event is tested from the repository
and remains prohibited for evidentiary use. The standalone ZIP omits that repository
fixture; its test is explicitly skipped there, while the synthetic invalidation test runs.

## Boundaries

- A subsequent Forge trial is recorded below. The original Linux WXR fixture remains
  synthetic; the Forge trial used user-supplied native captures. Their original capture
  device and manuscript/source-image equivalence were not independently established.
- Native geometry recomputation, WXR fingerprint recomputation, source-image equivalence,
  instrument recall, cross-instrument replay and live audio are outside C01.
- Successful structure checks never promote a record to valid research evidence.
- CI is configured separately; this report describes local execution, not an observed CI pass.

## Repeatable target-trial procedure

1. Open the launcher on The Forge and import a saved Stem Lab JSON.
2. Import one real WXR-003 JSON export into the same index.
3. Quit, reopen, and confirm that both records appear.
4. Export each original to a new filename and compare its identity with the input.
   Record the method: direct byte comparison, whole-file SHA-256, or synced Dropbox
   content hashes. Do not label Dropbox content hashes as whole-file SHA-256.
5. Run Verify index. Record any failure before proceeding to recall integration.

This trial does not require shutting down or altering the Resonance Engine.


## Forge follow-up evidence — 16 September 2026

### Scope and provenance

The operator supplied Windows startup, list, verify and WXR export output in the
project conversation. The assistant separately inspected synced Dropbox file metadata
and compared content identities. This was not remote execution on The Forge.
Private captures, absolute user paths, database contents and raw transcripts remain
outside this public repository.

Candidate identity: `826e24b16e5ff5f39556ec91281aea9b5ad5c8e0`.
Dropbox block content hashes calculated from that commit's file bytes matched the
synced copies of `bridge.py`, `store.py`, `adapters.py`,
`Start-Record-Bridge.cmd` and `test_bridge.py`. These five matches identify the
inspected synced implementation; they do not independently prove the bytes executed
during an earlier Windows process. Local Windows file hashes were not collected.
This documentation update does not change those implementation files.

### Results

| Check | Result | Evidence |
| --- | --- | --- |
| Windows startup and index location | Pass, operator supplied | Bridge 0.1 banner and expected local application-data index path |
| List native records | Pass, operator supplied | One Stem Lab session and one WXR-003 configuration export, both `structure_checked` |
| Persistence after requested relaunch | Supported by operator follow-up | Both prior imports remained present; process closure/reopening was not independently observed |
| Index verification | Pass, operator supplied | `ok: true`, two records, SQLite integrity `ok`, zero foreign-key errors, no failures |
| Stem Lab duplicate recognition | Pass, operator reported | Reimport of an exported record recognized as a duplicate |
| Stem Lab original/export identity | Pass, synced-file comparison | Matching Dropbox content hashes; both 258,765 bytes |
| WXR original/export identity | Pass, synced-file comparison | Matching Dropbox content hashes; both 3,556 bytes; operator export output agrees with that size |

Both records had empty Search Session references. This is supported unassigned
state, not evidence of a failed index relationship.

Dropbox content hashes are distinct from a whole-file SHA-256. No direct binary
download comparison or independently computed whole-file SHA-256 is claimed for
these two private capture pairs. The Bridge record IDs are its reported SHA-256
identities; the independent check here compared synced content hashes.

### Remaining delivery gate

The scoped record-handling results are documented. Human review remains pending
before merge, including acceptance of the build-identity and relaunch qualifications
above. This does not establish blanket Windows compatibility or validate a future
Browser interface. Workbench Home integration and Browser acceptance are separate.
Native geometry, source-image identity, native recall, cross-engine replay and
manuscript meaning remain outside this evidence.
