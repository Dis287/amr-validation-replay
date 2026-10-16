# N8_DSK_UNIFIED_RELEASE_V2

Status: **FROZEN_NOT_EXECUTED**

## Objective

Create one immutable, independently read-back-verified GitHub release containing
all eight exact DSK ASCII inputs required by the corrected-SEER n=8 combine.
This experiment performs no assembly, DSK generation, SEER execution, model
training, or biological transformation.

## Why this gate exists

Unified-release V1 is terminal `FAIL_PREFLIGHT`: its authorized local device had 1,589,616,640 free bytes below the frozen 3 GiB minimum. V1 is not rerun and its bound is not lowered.

V2 moves only the packaging execution environment to a standard GitHub Actions runner. Maximum artifact `11950830857` must be acquired with pinned official `actions/download-artifact` cross-run mode using run `38680749205`, artifact name `max-isolate-resource-resolution-v3-evidence`, repository identity, and GitHub token. The action-provided artifact is then checked through its frozen metadata digest, internal TAR hash, and exact maximum DSK identity.

Corrected-SEER n=8 V2 verified all seven files from the existing exact-input
release but its runner received a non-200 response when acquiring maximum
artifact `11950830857`. A separate authenticated post-run audit proved that the
artifact still exists and that its outer ZIP, internal TAR, and maximum DSK
match the frozen identities. V2 remains terminal. This experiment removes the
multi-source acquisition dependency without changing any scientific file.

## Frozen inputs

| Rank | Sample | Rows | Bytes | SHA-256 |
| --- | --- | ---: | ---: | --- |
| min | `ERR1067833` | 2,103,513 | 71,519,738 | `1b60a3c86547f95055e3d51e138c6f7d6b2329967f3851ebe7112df309276a44` |
| p10 | `ERR1067740` | 2,100,606 | 71,420,896 | `4ad0b03e3d184f5d694d43f5f43d7bfc7478eb655018e0bcefe58c6070f5eab2` |
| p25 | `ERR1067765` | 2,101,892 | 71,464,617 | `9489718a0b3990b0c59146861148f9898a96128fce09202cb6fb5b1e12c687e3` |
| median | `ERR855281` | 2,092,013 | 71,128,704 | `dee3cf91f0bba7fb5667a5818aa6992fe904209e26ddc73a77b8fc505f48355c` |
| p75 | `ERR855022` | 2,045,008 | 69,530,491 | `518d08abb3127485e555e46c73dc71c16a14e218c267ea99d197d89bcca79a9b` |
| p90 | `ERR854935` | 2,094,204 | 71,203,186 | `d6b821a29508df203a057620830004b3eab96eeea3b90ba495830fb2d1bd9175` |
| p99 | `ERR223664` | 2,096,522 | 71,281,996 | `d3a57a04d3a3093e86e8af73dd966598112cde6790eceb166d547140886fdb0d` |
| max | `ERR223688` | 2,098,204 | 71,339,203 | `cc33735372a337f45c1cb07681739bb14adaf14ae4142fcad1e9326e3b42695b` |

Totals: **8 files, 16,731,962 rows, 568,888,831 bytes**.

Regeneration, substitution, semantic-only equivalence, normalization, and
content rewriting are forbidden.

## Frozen sources

- seven-file release: `experiment001-n8-exact-inputs-v1`
- seven-file asset ID: `647907441`
- seven-file archive: 120,220,273 bytes, SHA-256
  `b132c289f07d18378e052b69d2987fb6f5ee03f74d38958cdc7c1e7f1f2aca5b`
- maximum artifact ID: `11950830857`
- maximum outer ZIP: 35,661,650 bytes, SHA-256
  `f6b889c5084eda46f2469a763cf44ee2f80bff6eb346cecd008e73496633e6e6`
- maximum internal TAR: 35,664,515 bytes, SHA-256
  `9415eade3e0ce172e6443f09a285b8dff08d23eda107958123ccb2fc65ceeaa0`

## Packaging

Release tag: `experiment001-n8-exact-inputs-v2`  
Asset: `experiment001-n8-exact-inputs-v2.tar.gz`

The archive must be deterministic: sorted paths, PAX tar format, gzip mtime 0,
member mtime 0, uid/gid 0, and empty user/group names. It contains exactly the
eight DSK files under `inputs/<rank>/kmers.txt`, the frozen 254-byte sample
list, `complete_manifest.json`, and `source_receipts.json`.

## Execution and retry law

- public standard `ubuntu-24.04` x64 GitHub Actions runner only;
- one attempt;
- no automatic or silent retry;
- release must be absent before execution;
- repository head must match the committed harness;
- at least 12,884,901,888 free bytes before packaging;
- every source identity must match before packaging;
- no biological download, SPAdes, DSK execution, SEER, or model training.

## PASS rule

PASS requires: all eight source identities; exact sample list; exact manifest;
recorded archive bytes and SHA-256; one release creation; fresh release download;
exact archive readback; all eight extracted identities reverified; and durable
result evidence committed afterward. Process exit alone is insufficient.

## Boundary

A pass authorizes only a separately frozen corrected-SEER n=8 combine protocol
to use this unified release. It does not make either earlier combine attempt a
pass and does not authorize the full cohort or model training.
