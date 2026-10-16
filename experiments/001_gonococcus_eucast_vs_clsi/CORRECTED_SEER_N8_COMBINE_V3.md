# CORRECTED_SEER_N8_COMBINE_V3

Status: **FROZEN_NOT_EXECUTED**

## Question

Can corrected SEER `combineKmers` at commit
`a6bd405754726467a93f39820fb4719457395ae7` produce the exact independently
verified feature matrix for the eight frozen resource-panel DSK inputs?

V1 and V2 remain terminal pre-combine failures and are not retried or
reclassified. V3 changes only acquisition: all eight inputs must come from the
read-back-verified unified release `experiment001-n8-exact-inputs-v2`.

## Unified input source

- release run: `38967348167` (PASS)
- release tag: `experiment001-n8-exact-inputs-v2`
- asset ID: `648632466`
- asset: `experiment001-n8-exact-inputs-v2.tar.gz`
- asset bytes: 141,491,724
- asset SHA-256:
  `4685554ea77eba521198ed73edff197fa65ac9b0967eb86b6842fff3188edef6`

The archive and every extracted input must be verified before SEER source
acquisition or build.

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

Totals: **8 files, 16,731,962 rows, 568,888,831 bytes**. The sample list is
exactly 254 bytes with SHA-256
`2efa6bddf14a4f6b8e26fca0a3eb7d62d408d37c9d563393402d7270f38241d8`.

## Scientific invariants

The following are value-for-value inherited from corrected-SEER n=8 V2:

- SEER source commit `a6bd405754726467a93f39820fb4719457395ae7`;
- source archive and Git blob identities;
- build command and no source edits;
- exact sample order and paths;
- command `combineKmers -r inputs/n8_samples.tsv -o work/combined/panel8_combined --min_samples 2`;
- standard `ubuntu-24.04` x64 runner, maximum 4 vCPU and 16 GiB RAM;
- 900-second combine bound, 900-second oracle bound, 5,400-second job bound;
- 12,582,912 KiB sampled process-tree RSS ceiling;
- 10,737,418,240-byte working-root ceiling;
- 0.5-second sampling and SIGTERM/10-second/SIGKILL termination;
- independent external-sort plus k-way-merge oracle;
- all zero-error counters, exact rows/tags/abundances, and output hash;
- always-attempted evidence retention, one attempt, no retry;
- a new result release plus fresh readback for PASS.

## PASS rule

PASS requires exact unified archive and all eight extracted inputs, exact SEER
source/build, combine exit zero inside every bound, completed gzip output, all
independent-oracle discrepancy counters equal zero, exact physical row equality,
resource/hash evidence, independent post-run audit, result release
`experiment001-corrected-seer-n8-v3`, and fresh release readback.

Process exit alone is insufficient.

## Boundary

A V3 PASS would establish corrected-SEER n=8 feature-combine correctness and
measured n=8 resource use only. It would not rewrite the original n=8 resource
gate, establish 1,102-run feasibility, reproduce Hicks SCM/RF metrics, or
authorize model training.
