# Slice 1 — Stem Lab v2 through the common record path

Status: implementation-ready specification; not implemented by this document.
Depends on the unified architecture direction, not a database migration or new UI
framework. Preserve the accepted Bridge/Browser behavior and existing native files.

## User journey and exact scope

Home -> Stem Lab 0.2 -> capture a mirrored take -> Save session -> Bridge import
-> Browser summary and native inspection -> Export original -> manually reopen
that exported file in Stem Lab 0.2 -> verify the same take/reflection.

Manual reopen is an acceptance check of the native file, not implementation of
Workbench native recall. Returning to an existing tab is not restoring a checkpoint.

## Adapter contract

| Input | Required treatment |
| --- | --- |
| stem-session/1 + appVersion 0.1.0 + existing detector | Retain legacy support; missing flip means original handedness; reject a declared true reflection masquerading as v1 |
| stem-session/2 + appVersion 0.2.0 + polyline-circle-subdivision/1 | Validate existing fields plus strict boolean overlay.flipX in draft and every take |
| v2 missing flip, string/number/null flip, malformed take | Invalid; original retained; research use prohibited under existing policy |
| Unknown schema/app/detector combination | Unsupported; retain original and explain capability boundary |
| WXR/native historical invalidations | Preserve existing behavior and evidence restrictions |

Do not coerce 0/1 or strings to booleans. A legacy file declaring flipX=false may
be supported only if explicitly covered by tests; never silently ignore true or
invalid values. Validate every take independently: draft On/take Off is legitimate.
Bump adapter version; retain producer/schema/version in summaries.

Summary adds draft reflection and each capture's reflection, with operation order:
source-local horizontal reflection about anchor before rotation. For v1 display
"Off (legacy format)"; for supported v2 show explicit On/Off. Unknown records must
show unknown/unsupported, never a fabricated Off. Preserve native JSON inspection.
A structurally valid record remains `structure_checked`, not replay-verified.

No geometry recomputation, source retrieval, model execution, cross-engine conversion
or source-file mutation occurs at import. If geometry checking is later added,
report it separately from structural and human validation.

## Existing store / migration handling

Keep original bytes, hash-derived ID, duplicate behavior, database tables and
exclusive export unchanged. Adapter changes affect new summaries only. Existing
unsupported imports must not silently gain a new status just because software was
updated. Define a bounded explicit reinspection command using stored bytes before
shipping if the same file is already archived: transactional summary replacement,
original/ID/import metadata/session links unchanged, report old/new adapter/status,
and retain prior summary provenance. If that needs a schema migration, defer it
and test the first slice in a copied/new index with an honest explanation. Never
recommend deleting the operator's existing record or index to make a demo pass.

Use existing Search Session reference field; keep it unassigned when no reference
exists. Do not generate fictitious canonical sessions to fill a display slot.

## Required tests

1. v1, v2 flip On, v2 flip Off, and mixed draft/take flips import with correct labels.
2. Strict invalid/missing flip cases and incompatible version/detector are explicit.
3. Originals with whitespace, Unicode and different formatting export byte-identically.
4. Reimport is duplicate and preserves original identity and existing links.
5. Existing WXR, invalidation, missing-index, overwrite and invalid-destination
   tests pass; no dependency on installed Engine or actual research files.
6. Browser summary distinguishes draft versus take reflection, displays unknown
   correctly, retains selection/filter context and native JSON, and never starts replay.
7. Already-archived unsupported v2 behavior is demonstrated before shipping;
   do not hide the store's current cached-summary behavior.
8. Forge: operator saves one real mirrored take, inspects it, exports, manually
   reopens in new Stem Lab and confirms its flip and trajectory. Preserve the
   original working session until the reopened copy is checked.

## Completion evidence

Record implementation commit/package identity, adapter version, tests, original
and exported hashes, target-device result and remaining exclusions. Reuse the
existing instrument-triage and integration work items; keep full Home acceptance
and native recall milestones independent. No manuscript inference follows from
this software acceptance.
