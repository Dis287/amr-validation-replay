# MAX_ISOLATE_RESOURCE_RESOLUTION_V1

Status: **FROZEN / NOT EXECUTED** (2026-09-30).

This is a new prospective infrastructure experiment. It is not a rerun, retry,
or continuation of the failed n=8 gate. Its sole question is whether maximum-rank
isolate `ERR223688` can complete the unchanged declared reconstruction pipeline
inside the separately defined containment envelope below.

The parent n=8 gate at
`9627020e44157c717b4fad2589ed47830958efd0` remains **FAILED / UNVERIFIED**.
The old 2,700-second ceiling intent remains **UNKNOWN** under
`4c7cb7e710ec1d221c9d84ef54b1116e5ec0033b`.

Committing this protocol freezes it but does not execute or authorize execution.
Execution requires a separate explicit step after remote readback of the protocol
commit.

## Evidence base

Source: `resource_panel_n8_failure.json`, retained from GitHub Actions run
`36665031444` and committed at `9627020e44157c717b4fad2589ed47830958efd0`.

| Rank | Isolate | Compressed input bytes | SPAdes wall s | Peak process-tree RSS KiB | Peak watched stage disk bytes |
| --- | --- | ---: | ---: | ---: | ---: |
| min | `ERR1067833` | 70,656,305 | 299.528 | 1,279,840 | 581,808,411 |
| p10 | `ERR1067740` | 177,141,208 | 653.872 | 1,523,880 | 1,431,877,181 |
| p25 | `ERR1067765` | 226,917,919 | 1,074.414 | 1,762,324 | 1,836,688,542 |
| median | `ERR855281` | 325,143,380 | 666.621 | 1,279,508 | 1,401,847,618 |
| p75 | `ERR855022` | 355,223,967 | 847.386 | 1,279,612 | 1,516,533,857 |
| p90 | `ERR854935` | 389,562,829 | 846.077 | 1,704,780 | 1,613,270,878 |
| p99 | `ERR223664` | 771,033,917 | 2,365.749 | 2,097,024 | 2,429,652,499 |

The failed maximum execution reached 2,702.424 seconds after the 2,700-second
termination threshold, with sampled peak RSS 2,518,544 KiB and sampled peak
watched stage disk 3,415,816,271 bytes. Those are censored partial-run
measurements, not completion requirements.

## Scaling assessment

### FACT

- The seven successful runtimes span 299.528 to 2,365.749 seconds, a 7.8983-fold
  range.
- Runtime is not monotone with compressed input size: p25 took 1,074.414 seconds
  while the larger median took 666.621 seconds; p75 took 847.386 seconds while
  the larger p90 took 846.077 seconds.
- Across seven points, Pearson input-size/runtime correlation is 0.9209 and
  Spearman rank correlation is 0.75. A seven-point ordinary least-squares line
  has descriptive R-squared 0.8480, but this is dominated by the high-leverage
  p99 point. Fitting only min through p90 gives R-squared 0.3854 and predicts
  1,416.365 seconds at p99, under the observed p99 runtime by 949.384 seconds.
- Maximum input size is 1,078,536,686 bytes. It is 307,502,769 bytes larger
  than p99 and 1.3988187 times p99.
- p99 finished only 334.251 seconds below 2,700 seconds.
- Multiplying p99 runtime by the input-size ratio gives 3,309.254 seconds. This
  arithmetic is recorded only as a naive proportional reference, not a runtime
  estimate.
- The censored maximum run proves only that completion time exceeded the old
  threshold under that execution. It does not reveal the remaining runtime.

### INFERENCE

- Compressed input size contains useful resource information, but it is not a
  sufficient runtime predictor for these seven isolates.
- A new experiment may defensibly allocate a finite additional observation
  window while treating completion inside that window as unknown.
- A 5,400-second limit is a containment decision: it supplies exactly one
  additional 2,700-second interval beyond the established censor point. It is
  2.2826 times the observed p99 runtime and 1.6318 times the naive proportional
  reference. These ratios describe the bound; they do not predict completion.

### UNKNOWN

- Whether `ERR223688` will finish inside 5,400 seconds.
- Its completed assembly, filtered assembly, QUAST metrics, DSK output, and
  canonical 31-mer count.
- Which internal SPAdes stage would have completed after the old termination.
- The true relationship between compressed read size and SPAdes runtime outside
  these seven completed observations.
- Whole-cohort resource feasibility and the historical Hicks-equivalent feature
  matrix.

## Frozen scientific invariants

- target: `ERR223688`, maximum rank 1101 of 1,102
- library layout: paired
- input 1: `ERR223688_1.fastq.gz`, 529,561,823 bytes,
  MD5 `7cec28e9c5123b8a4ec8dee92efe71c6`
- input 2: `ERR223688_2.fastq.gz`, 548,974,863 bytes,
  MD5 `a7f04fcc8cddc16b3d54f267d551528c`
- ENA locations: the two exact URLs recorded in
  `resource_panel_selection.json`
- SPAdes 4.3.0 archive SHA-256:
  `e88a8c533c8614dd4b7c5788cfcd46427848a0575267f97c690a75fd2a343034`
- SPAdes mode: default paired-read assembly
- SPAdes command template: `spades.py -1 ERR223688_1.fastq.gz -2
  ERR223688_2.fastq.gz -o spades -t 2 -m 8`; no other scientific option
  change
- filter: retain contigs with length >=200 and SPAdes header `_cov_` >=10
- QUAST 5.2.0 command template: `quast.py --min-contig 200 --no-plots
  --no-html --no-icarus -t 2 -l raw,filtered -o quast spades/contigs.fasta
  filtered.fasta`; archive SHA-256
  `ccd911087cfa254ad4b8eadac4f95d4685e44c3996f5516b8e0ce6f7cfa7e0db`
- DSK 2.3.3 command template: `dsk -file filtered.fasta -kmer-size 31
  -abundance-min 1 -out kmers -out-tmp dsk_tmp -max-memory 8000`, followed
  once by `dsk2ascii -file kmers.h5 -out kmers.txt`;
  archive SHA-256
  `626a4663f70323a80834c013f1d9dcb4a3b3a73a1c9ab5da95a013783d81b0f6`
- independent DSK oracle: A<C<T<G canonical reverse-complement counting, exact
  set and abundance equality
- any later combine remains pinned to corrected SEER commit
  `a6bd405754726467a93f39820fb4719457395ae7`; combine is not part of this
  experiment

## Frozen execution envelope

GitHub's current official documentation lists the public-repository
`ubuntu-24.04` standard x64 runner as 4 CPU, 16 GB RAM, and 14 GB SSD. It also
states that a GitHub-hosted job can run for at most six hours. These are platform
claims, not measured biological results:

- https://docs.github.com/en/actions/reference/runners/github-hosted-runners
- https://docs.github.com/en/actions/reference/limits

The experiment may use no larger compute class.

| Resource | Frozen limit | Rationale |
| --- | ---: | --- |
| Runner | public standard `ubuntu-24.04` x64 only | Same durable platform class as the failed gate; no compute-class upgrade |
| Runner CPU | maximum 4 vCPU; SPAdes restricted to 2 threads | Preserves `-t 2`; additional runner CPUs must not be assigned to SPAdes |
| Runner RAM | maximum 16 GB | Current published standard-runner class; no larger-memory runner |
| SPAdes memory parameter | `-m 8` | Unchanged scientific command |
| Sampled process-tree RSS kill ceiling | 10,485,760 KiB (10 GiB) | 4.163 times the censored sampled maximum; leaves nominal runner headroom; containment, not predicted need |
| Runner SSD | maximum 14 GB | Current published standard-runner class |
| Watched SPAdes-stage disk kill ceiling | 8,589,934,592 bytes (8 GiB) | 2.515 times the censored sampled maximum while reserving nominal disk for reads, tools, evidence, and packaging |
| Minimum free disk before input download | 12,884,901,888 bytes (12 GiB) | Preflight guard; failure stops before biological execution |
| SPAdes wall-clock ceiling | 5,400 s | One additional old-ceiling interval; bounded observation, not a runtime forecast |
| QUAST ceiling | 300 s | Unchanged from declared resource-panel procedure |
| DSK ceiling | 900 s | Unchanged from declared resource-panel procedure |
| `dsk2ascii` ceiling | 300 s | Unchanged from declared resource-panel procedure |
| Independent oracle ceiling | 900 s | Bounded exact verification |
| Whole job ceiling | 9,000 s | Allows staging, fixed pipeline, verification, and mandatory evidence upload while remaining far below the platform maximum |
| Sampling interval | 0.5 s | Unchanged measurement cadence |

Before downloading inputs, record runner image name/version, CPU model and count,
total RAM, mounted-filesystem capacity/free bytes, tool hashes, repository commit,
and protocol-file hashes. If the runner exceeds the allowed compute class or has
less than the predeclared free disk, stop and save a preflight FAIL. Do not move
to a larger runner.

Resource supervisors must terminate the complete process group on wall, sampled
RSS, or watched-stage-disk breach: SIGTERM, a fixed 10-second grace interval,
then SIGKILL if still alive. A sampled cap can overshoot between 0.5-second
samples; record the measured peak and do not relabel the breach.

## Frozen outcome handling

No automatic or manual retry is permitted. No parameter may change after start.

| Event | Required classification and action |
| --- | --- |
| input byte or MD5 mismatch | `FAIL_INPUT_INTEGRITY`; stop before SPAdes |
| SPAdes exits 0 inside all bounds and `contigs.fasta` is nonempty | continue once to filter, QUAST, DSK, and independent verification |
| 5,400-second breach | terminate; `FAIL_SPADES_TIMEOUT` |
| sampled RSS breach or kernel OOM evidence | terminate if possible; `FAIL_MEMORY_ENVELOPE`; do not infer a SPAdes defect |
| watched disk breach or filesystem exhaustion | terminate if possible; `FAIL_STORAGE_ENVELOPE`; distinguish sampled cap from OS exhaustion |
| nonzero SPAdes exit without an established envelope breach | `FAIL_SPADES_NONZERO`; retain logs; root cause remains unknown unless directly established |
| missing or empty `contigs.fasta` after exit 0 | `FAIL_SPADES_OUTPUT` |
| filter or QUAST failure/missing output | `FAIL_QC_STAGE` |
| DSK or `dsk2ascii` nonzero/timeout/missing output | `FAIL_DSK_STAGE` |
| any DSK missing, extra, duplicate, or abundance mismatch | `FAIL_DSK_EQUALITY` |
| required artifact or upload missing | `FAIL_EVIDENCE_RETENTION`, regardless of computational success |

Every failure must produce one explicit `outcome.json` with the classification,
first failing stage, commands, exit/termination state, bounds, measurements,
hashes available at failure, missing-evidence list, and a statement that no retry
occurred.

## Frozen retention policy

All uploads use `if: always()` and 30-day retention. Upload success is part of
the scientific acceptance rule.

Always retain:

- `outcome.json`, input-integrity record, environment/preflight record
- every bounded-stage JSON and stdout/stderr log, including timeout evidence
- SPAdes `spades.log`, `params.txt`, warnings, and any pipeline-state text/JSON
- recursive path/byte/SHA-256 manifest of the working stage at termination
- every primary scientific output that exists: `contigs.fasta`,
  `scaffolds.fasta`, assembly graph/path files, filtered FASTA, filter metrics,
  QUAST outputs, DSK HDF5, DSK ASCII, and independent-verification JSON
- artifact archive digest, file count, compressed and uncompressed bytes

Raw FASTQs and replaceable downloaded tool archives are not uploaded; their exact
source identities, byte sizes, MD5/tool SHA-256 values, and integrity results are
retained. Temporary SPAdes scratch binaries that are not primary outputs are
represented by the recursive manifest; all textual diagnostics and primary
partial outputs are retained. If the mandatory evidence bundle cannot be
uploaded intact, the experiment is FAIL.

After independent audit, commit the small machine-readable outcome, manifest,
hash ledger, and synchronized project state. Do not claim evidence that exists
only in an expired or missing artifact.

## Pass condition

`MAX_ISOLATE_RESOURCE_RESOLUTION_V1` passes only if all of these survive in the
mandatory evidence artifact and are independently audited:

1. exact input bytes and MD5 values match;
2. SPAdes exits 0 before 5,400 seconds without RSS/disk breach;
3. nonempty completed assembly survives;
4. filter metrics/FASTA and QUAST output survive;
5. DSK HDF5 and ASCII survive;
6. the independent canonical oracle reports zero missing, extra, duplicate, and
   abundance-mismatched rows;
7. all required logs, hashes, resource records, manifests, and artifact digests
   survive durably; and
8. an independent audit accepts the evidence.

Anything less is not PASS.

## Post-result boundary

Even on PASS:

- the original n=8 gate remains FAILED / UNVERIFIED;
- no corrected-SEER n=8 run is authorized by this experiment alone;
- no 1,102-isolate reconstruction is authorized;
- no model training is authorized; and
- the only possible next gate is a separately named, prospectively frozen n=8
  combine protocol using all eight durable isolate outputs and the corrected
  SEER revision plus an exact independent oracle.

On FAIL, stop and classify only what the saved evidence establishes. Do not run a
second attempt inside this experiment.
