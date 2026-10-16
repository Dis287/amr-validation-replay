# N8_DSK_UNIFIED_RELEASE_V2 — PASS

GitHub Actions run `38967348167` executed exactly once from commit
`8284c8e67b7fdac15745b72905e976ac58ba6ae5`.

## Audited result

- preflight: PASS
- standard runner: `ubuntu24`, x86_64, 4 CPUs, 16,373,452 KiB RAM
- free disk before acquisition: 92,103,516,160 bytes
- prior V2 manual runs: none
- target release before execution: absent
- seven-input release acquisition: PASS
- pinned official cross-run maximum artifact acquisition: PASS
- source artifact digest: exact
- internal maximum TAR: exact
- all eight source DSK identities: exact
- malformed input rows: 0
- duplicate input rows: 0
- copied package identities: exact
- sample list: exact
- deterministic archive creation: PASS
- release creation: PASS
- fresh release download: PASS
- fresh archive hash: exact
- all eight extracted readback identities: exact
- evidence uploads: PASS
- retry: none

## Durable release

- tag: `experiment001-n8-exact-inputs-v2`
- target commit:
  `8284c8e67b7fdac15745b72905e976ac58ba6ae5`
- asset: `experiment001-n8-exact-inputs-v2.tar.gz`
- asset bytes: 141,491,724
- asset SHA-256:
  `4685554ea77eba521198ed73edff197fa65ac9b0967eb86b6842fff3188edef6`
- release:
  https://github.com/Dis287/amr-validation-replay/releases/tag/experiment001-n8-exact-inputs-v2

The release contains the eight exact DSK files (16,731,962 total rows;
568,888,831 total bytes), the exact 254-byte sample list, a complete manifest,
and source receipts.

## Evidence artifacts

- evidence artifact ID: `12074948375`
- evidence digest:
  `sha256:ce03cb8501d1a61ee39e2324beea2be5287504ba73e673317b795b8b2dd48b2f`
- receipt artifact ID: `12075098040`
- receipt digest:
  `sha256:e4d08598d1f3bbeee47ded93bbafc6f9f9770fb670afa933850d62cebb029fa1`

## Boundary

This PASS establishes one stable, exact, read-back-verified n=8 DSK input source.
It does not make corrected-SEER n=8 correct, does not authorize the 1,102-run
cohort, and does not reproduce Hicks models or metrics.

The next allowed action is a separately frozen corrected-SEER n=8 combine
experiment that uses only this unified release.
