# N8_DSK_EXACT_INPUT_RECOVERY_V1 protocol

Status: `FROZEN_NOT_EXECUTED`

## Scientific boundary

This is a separately named prospective recovery experiment. Its sole purpose is
to restore the seven exact DSK ASCII inputs that are no longer retrievable from
GitHub Actions run `36665031444`.

It is not an n=8 combine run, an n=8 retry, a full-cohort reconstruction, or a
model-training experiment. It does not change the failed original n=8 record,
V1, V2, or the independently audited V3 maximum-isolate PASS.

Parent blockage record:
`babd3e65400149b70f17fdf404f78ddd30994946`.

## Evidence that fixes this protocol

The seven original isolate jobs remain visible and successful in GitHub Actions,
and their job logs remain readable. Their artifacts do not: the run-level
artifact inventory is empty and all seven recorded artifact IDs return HTTP
404. The original workflow set `retention-days: 14`; this audit occurred after
that interval. The API did not return a deletion-cause field, so the exact cause
of each 404 is not promoted beyond the observed retention configuration and
current absence.

All seven jobs used runner version `2.337.0` and the `ubuntu-24.04` label. Six
used runner image `20260920.314.1`; `median` used `20260927.320.1`. Therefore a
single exact historical runner image did not generate all seven outputs. The
future runner image cannot be assumed equivalent. Exact output identity is the
acceptance oracle.

## Frozen target identities

The order below is fixed. `kmers.txt` is accepted only when both its exact byte
count and SHA-256 match.

| Rank | Isolate | FASTQ 1 bytes / MD5 | FASTQ 2 bytes / MD5 | Expected rows | Expected DSK ASCII bytes | Expected DSK ASCII SHA-256 | Expected filtered FASTA SHA-256 |
| --- | --- | --- | --- | ---: | ---: | --- | --- |
| min | `ERR1067833` | 35,204,390 / `b2e9cf0b59ad5f339c32a1c7cbe8dd9b` | 35,451,915 / `4ff4e92056137f16f49ff7bf45cac20c` | 2,103,513 | 71,519,738 | `1b60a3c86547f95055e3d51e138c6f7d6b2329967f3851ebe7112df309276a44` | `d11fa38dd04596375d2f5a159657e42b4ecb503695d628b926f832ef59aa4b1a` |
| p10 | `ERR1067740` | 87,872,847 / `4571426afa06e4645477a2f78c9a15b6` | 89,268,361 / `55e8622fcc0cfa531b1abddaddf89d63` | 2,100,606 | 71,420,896 | `4ad0b03e3d184f5d694d43f5f43d7bfc7478eb655018e0bcefe58c6070f5eab2` | `6d22902f2e39d6cbcc8d4e336de7a1149ce5f7c820c3c9d723c327c1ef4220c2` |
| p25 | `ERR1067765` | 113,016,971 / `6ace1e2116e0c9404db1c07d007c59d7` | 113,900,948 / `7b5a5076a5d6d2b636e5f347b797379f` | 2,101,892 | 71,464,617 | `9489718a0b3990b0c59146861148f9898a96128fce09202cb6fb5b1e12c687e3` | `4c38f70a5cc3f9c33ff4a42a0cd3956a576722f1ffaca62eaee195a741693ec7` |
| median | `ERR855281` | 159,832,392 / `4d94a6c4e9bf48574b1268494f079a5c` | 165,310,988 / `48937b9dceeb433a3757b0903f0d0936` | 2,092,013 | 71,128,704 | `dee3cf91f0bba7fb5667a5818aa6992fe904209e26ddc73a77b8fc505f48355c` | `a74eb50ddba37ee649c32c74f7ecd93aad4327527cb75dc539d6cf295b50374d` |
| p75 | `ERR855022` | 174,914,715 / `5dd2d5e869875046cab33a515ba1af8b` | 180,309,252 / `09992162f84607c77ce4ea5e4de72fc3` | 2,045,008 | 69,530,491 | `518d08abb3127485e555e46c73dc71c16a14e218c267ea99d197d89bcca79a9b` | `ca0e573792e4abfb0efc22fc676cf60303de45a018b62362745b4647da28c77f` |
| p90 | `ERR854935` | 192,013,858 / `8455b4df44da542a1de5b31d9676eb73` | 197,548,971 / `43b24bac47caef467cce9fec0f67345b` | 2,094,204 | 71,203,186 | `d6b821a29508df203a057620830004b3eab96eeea3b90ba495830fb2d1bd9175` | `8664421aaa9e7b739baa826add2eaf20f1559f06471b9c7286b5741a11041751` |
| p99 | `ERR223664` | 377,899,592 / `59ecbe0c66b5ad93ead9577308724bce` | 393,134,325 / `668fb209d9ef01b1897c1105e09ef7ba` | 2,096,522 | 71,281,996 | `d3a57a04d3a3093e86e8af73dd966598112cde6790eceb166d547140886fdb0d` | `4554581dbdd6ed424f216906216b1660ae04d279ad0529c50c2dcf367769e74b` |

The seven target ASCII files total exactly 497,549,628 bytes.

## Phase A — exact-copy recovery first

No biological computation is allowed in Phase A.

1. Query each recorded artifact ID again and record the API response.
2. Inspect only candidate copies explicitly supplied from a known prior export or
   storage location. Do not infer a file from its name.
3. For every candidate, record source, path, bytes, SHA-256, physical row count,
   duplicate-row count, and parse validity (`31-base A/C/G/T k-mer`, integer
   abundance, exactly two fields).
4. Mark an isolate `RECOVERED_EXACT` only when bytes, SHA-256, row count, parse
   validity, and zero duplicates all match the frozen target.
5. A mismatch is `REJECTED_CANDIDATE_MISMATCH`; preserve its manifest but never
   substitute it for the target.

If all seven are `RECOVERED_EXACT`, skip Phase B. If any remain unavailable,
Phase B may run only for that fixed missing subset. The subset and Phase A
manifest must be frozen in the execution record before any FASTQ download.

## Phase B — prospective regeneration of missing targets

Phase B tests whether the original scientific procedure regenerates the exact
recorded byte streams. It does not assume determinism.

### Environment and execution envelope

- dedicated future workflow: manual `workflow_dispatch` only
- repository commit: the later harness commit, recorded before dispatch
- runner: public standard `ubuntu-24.04`, x64; no larger runner class
- maximum parallel isolate jobs: 4
- whole-job ceiling per isolate: 4,500 s
- stage sampling interval: 0.5 s
- stage termination: SIGTERM, fixed 2-second grace, SIGKILL if still alive
- no automatic or silent scientific retry
- one regeneration attempt per missing isolate in this experiment
- every terminal path writes `outcome.json` and attempts evidence upload

The actual runner version, image version, image provisioner version/commit, CPU,
RAM, filesystem capacity/free bytes, installed package versions, repository
commit, and support-file hashes must be recorded before FASTQ download. A
different future runner image is evidence, not equivalence.

### Frozen tools and support code

| Component | Frozen identity |
| --- | --- |
| SPAdes | 4.3.0 archive SHA-256 `e88a8c533c8614dd4b7c5788cfcd46427848a0575267f97c690a75fd2a343034` |
| QUAST | 5.2.0 archive SHA-256 `ccd911087cfa254ad4b8eadac4f95d4685e44c3996f5516b8e0ce6f7cfa7e0db` |
| DSK | 2.3.3 archive SHA-256 `626a4663f70323a80834c013f1d9dcb4a3b3a73a1c9ab5da95a013783d81b0f6` |
| original isolate runner | SHA-256 `1af9392259bb7e132c52f7c9c22eca76d5a7b64e874e8a3a739fe66ad9087f4e` |
| contig filter | SHA-256 `2cb8e2e46e494737de52a2a31a9e6078e95ad09dcff780c46d77e89e27b47e16` |
| bounded-stage recorder | SHA-256 `4bfe89eeb03c144bbfe5030b16fa216afb695315a4e9ea7571f9da162228fd6b` |
| rank selection | SHA-256 `af7efa9e53c129788844dea0f77af6f1152840467e1d649059fa25407f4bb1a5` |

The future harness may add fail-closed retention and outcome handling around
these operations, but it may not change their scientific commands.

The four support files above were also read back from the historical workflow
commit `4a6e83c89a40ddb6dc82dbcaf9cea226549c1db3`; their Git blob identities
(`cca9f407…`, `7ae222715…`, `0f4007823…`, `b0eb3ccda…`) match the current
files exactly. The old workflow blob remains `e233c395…` and is not modified or
reused as the new harness.

### Frozen scientific procedure

For each missing isolate:

1. Download the two declared ENA FASTQs and require exact byte count and MD5.
2. Run SPAdes 4.3.0 in default paired-read mode:
   `spades.py -1 MATE1 -2 MATE2 -o OUT -t 2 -m 8`.
   Ceiling: 2,700 s.
3. Retain contigs only when sequence length is at least 200 bp and the SPAdes
   header `_cov_` value is at least 10. The filter implementation is frozen by
   the hash above.
4. Run QUAST 5.2.0:
   `quast.py --min-contig 200 --no-plots --no-html --no-icarus -t 2 -l raw,filtered -o OUT raw.fasta filtered.fasta`.
   Ceiling: 300 s.
5. Create the DSK temporary directory, then run DSK 2.3.3:
   `dsk -file filtered.fasta -kmer-size 31 -abundance-min 1 -out kmers -out-tmp dsk_tmp -max-memory 8000`.
   Ceiling: 900 s.
6. Run:
   `dsk2ascii -file kmers.h5 -out kmers.txt`.
   Ceiling: 300 s.
7. Independently count canonical reverse-complement 31-mers using order
   `A<C<T<G` and require zero missing, extra, duplicate, and abundance-mismatched
   rows against `kmers.txt`.
8. Require the regenerated filtered FASTA SHA-256, DSK row count, DSK ASCII byte
   count, and DSK ASCII SHA-256 to equal the frozen target for that isolate.

No SEER command is allowed.

## Outcomes and acceptance

Per-isolate states are:

- `RECOVERED_EXACT`
- `REGENERATED_EXACT`
- `REJECTED_CANDIDATE_MISMATCH`
- `FAIL_INPUT_INTEGRITY`
- `FAIL_TOOL_INTEGRITY`
- `FAIL_SPADES_TIMEOUT`
- `FAIL_SPADES_NONZERO`
- `FAIL_SPADES_OUTPUT`
- `FAIL_QC_STAGE`
- `FAIL_DSK_STAGE`
- `FAIL_DSK_EQUALITY`
- `FAIL_EXPECTED_IDENTITY_MISMATCH`
- `FAIL_EVIDENCE_RETENTION`
- `FAIL_PREFLIGHT_INFRASTRUCTURE`

Experiment PASS requires all seven isolates to finish as `RECOVERED_EXACT` or
`REGENERATED_EXACT`, with an exact seven-file manifest and an independent audit.
Anything less is FAIL. Seven identities may be restored by a mixture of recovery
and regeneration; provenance must remain explicit per isolate.

A semantically equal but byte-different DSK output is
`FAIL_EXPECTED_IDENTITY_MISMATCH`. It may motivate a separately frozen
divergence study, but it cannot enter the n=8 combine under this protocol.

## Durable evidence rule

Every terminal path must retain all available manifests, outcomes, stage JSON,
stdout/stderr, SPAdes logs/state files, filter metrics, QUAST outputs, DSK HDF5
and ASCII outputs when produced, independent-verifier results, environment
records, and a recursive path/size/SHA-256 ledger. Raw FASTQs need not be
retained, but their observed identities must be recorded.

Temporary GitHub Actions evidence must use `if: always()` and 90-day retention.
A PASS additionally requires the accepted seven exact DSK ASCII files, their
per-isolate provenance, and the complete manifest to be stored as a versioned
GitHub Release asset under tag `experiment001-n8-exact-inputs-v1`. The release
asset must be downloaded again, its digest and contents independently verified,
and its asset ID/digest committed. If that durable read-back fails, the
experiment is `FAIL_EVIDENCE_RETENTION`. Actions artifacts alone cannot satisfy
PASS.

## Post-PASS boundary

Even a PASS:

- does not rewrite the original n=8, V1, or V2 failures;
- does not establish corrected-SEER n=8 correctness;
- does not authorize corrected-SEER execution;
- does not authorize the 1,102-isolate reconstruction;
- does not authorize model training.

It authorizes only freezing a new corrected-SEER n=8 combine protocol against
the restored exact eight-input set, including the already audited V3 maximum.

## Current authorization

This protocol commit authorizes no recovery query, candidate-file read,
biological download, regeneration, release creation, workflow dispatch, or
scientific execution. A dedicated harness must be built and audited in a
separate step. Execution requires another explicit authorization after that
harness is committed and read back.

Machine-readable protocol: `exact_input_recovery_v1.json`.
