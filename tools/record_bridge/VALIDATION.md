# C01 validation record

16 September 2026. Candidate 0.1.0. No Forge deployment or research-claim validation.

## Executed checks

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

- The Windows launcher and a real WXR-003 headset export await target-device trial.
- Native geometry recomputation, WXR fingerprint recomputation, source-image equivalence,
  instrument recall, cross-instrument replay and live audio are outside C01.
- Successful structure checks never promote a record to valid research evidence.
- CI is configured separately; this report describes local execution, not an observed CI pass.

## Target trial

1. Open the launcher on The Forge and import a saved Stem Lab JSON.
2. Import one real WXR-003 JSON export into the same index.
3. Quit, reopen, and confirm that both records appear.
4. Export each original to a new filename and compare its SHA-256 with the input.
5. Run Verify index. Record any failure before proceeding to recall integration.

This trial does not require shutting down or altering the Resonance Engine.
