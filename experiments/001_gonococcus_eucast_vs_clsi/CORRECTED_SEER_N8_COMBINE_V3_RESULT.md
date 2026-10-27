# CORRECTED_SEER_N8_COMBINE_V3 — terminal result

## Decision

**PASS.** GitHub Actions run `38969013276`, at frozen harness commit
`615a76598cf426df7b93564f68f2cf55b17f3561`, completed its single permitted
attempt. Both the execution job and the independent audit/release-readback job
passed. This establishes corrected-SEER feature-combine correctness at n=8 for
the eight frozen DSK inputs. It does not repair or reclassify the original
failed n=8 resource gate.

## Exact input and tool integrity

- Unified input release: `experiment001-n8-exact-inputs-v2`
- Source archive: 141,491,724 bytes; SHA-256
  `4685554ea77eba521198ed73edff197fa65ac9b0967eb86b6842fff3188edef6`
- DSK files: 8/8 exact
- Total input rows: 16,731,962
- Total input bytes: 568,888,831
- Malformed rows: 0
- Sample list: 254 bytes, 8 rows; SHA-256
  `2efa6bddf14a4f6b8e26fca0a3eb7d62d408d37c9d563393402d7270f38241d8`
- Corrected SEER revision: `a6bd405754726467a93f39820fb4719457395ae7`
- Source archive SHA-256:
  `e6ed83b2e60c1c45beeee24949203bd34e7dbc5107b77bc120d5afddff8e8e01`
- Built binary: 148,096 bytes; SHA-256
  `a63e13be3a7d12550be6ef17b2021dc7a5903e95bd0222d62ed0ab1008184185`

## Exact scientific result

Corrected `combineKmers --min_samples 2` emitted:

- physical rows: **2,210,121**
- unique features: **2,210,121**
- expected features: **2,210,121**
- gzip bytes: **26,014,737**
- gzip SHA-256:
  `31bd862b2e3f93796a5241c5ce7bd86400297099203f2dd48bfd064d3a73b732`

Independent external-sort/k-way-merge oracle:

- missing expected: **0**
- extra or below-minimum: **0**
- duplicate output rows: **0**
- duplicate sample tags: **0**
- unknown sample tags: **0**
- missing sample tags: **0**
- abundance mismatches: **0**
- malformed rows: **0**
- duplicate input rows: **0**
- exact: **true**

The independently generated expected stream was 275,328,521 bytes with
SHA-256
`97f9c7c84113d0ab59383a13777e8c06c853dfc901d12d79e8d8923c6c8adc57`.

## Resource evidence

| Stage | Wall | Peak process-tree RSS | Peak watched root | Exit |
|---|---:|---:|---:|---:|
| corrected SEER combine | 21.325 s | 583,528 KiB | 1,309,767,078 bytes | 0 |
| independent oracle | 88.912 s | 502,216 KiB | 2,865,103,878 bytes | 0 |

No timeout, memory termination, or storage termination occurred.

## Durable evidence

- Candidate artifact: `12075234594`; digest
  `sha256:b05859504aa870b4e4b0f1bf15a74065cede2b1c69e1240196f6a01de5f77689`
- Candidate receipt: `12076510939`; digest
  `sha256:9fe88e0436a5efcf638850e96bd7f92528fca6c029d95f829ad8c9dc7c28cea9`
- Final audit artifact: `12077017286`; digest
  `sha256:243e874d5b151ce1f9e51b12e8487fbab3cf177c0c40d0d9fccbb5a39f69e7da`
- Final receipt: `12077426921`; digest
  `sha256:a739833b549c362882d289a5f5fc5e8d15b181164f5d38016a6b4af9403d3c88`
- Immutable release:
  `experiment001-corrected-seer-n8-v3`
- Release asset: 490,458,525 bytes; SHA-256
  `19dff7c3ec05c0b0783b45e13d11da843b125eb0c6ea01b03b9b4fb9d5856bfe`
- Fresh release readback: all eight inputs exact; oracle exact; combined output
  bytes and SHA-256 exact.

## Packaging audit finding

The immutable release TAR contains **60 regular members at 26 distinct paths**.
Twenty-five paths are repeated because the packager recursively added
directories and later added their descendants again. This is a
**non-scientific archive-redundancy defect**, not concealed evidence.

Every occurrence of every repeated path was independently streamed and hashed.
All repeated occurrences are byte-identical; conflicting duplicate paths = 0.
The immutable archive hash, fresh readback, exact input identities, oracle
result, and combined-output identity all agree. Therefore no effect on the
scientific PASS is established. The release must not be rewritten; future
packagers must add each path once.

## Boundary

Established:

> Corrected SEER revision `a6bd405…` exactly matches the independent n=8
> feature and sample-abundance oracle for the eight frozen DSK inputs.

Not established:

- full 1,102-isolate reconstruction feasibility;
- faithful Hicks SCM/RF replay;
- EUCAST-versus-CLSI model metric reproduction;
- final claim-state transition;
- commercial value or breakthrough status.

The original n=8 resource gate remains failed. Full-cohort execution and model
training remain unauthorized. The next allowed step is a separately frozen
resource-feasibility decision using durable isolate and n=8 combine evidence.
