# Deterministic resource panel — n=4 checkpoint

Status: **PASS at nested subset n=4 only** (2026-09-29). The n=8 resource/union gate remains open. This checkpoint does not authorize 1,102-run reconstruction or model training.

## Declared protocol

The eight panel members were selected before execution by sorting all 1,102 ENA manifest rows by total paired compressed FASTQ bytes, breaking ties by run accession, and taking fixed ranks: minimum, p10, p25, median, p75, p90, p99, maximum. The exact rows are in `resource_panel_selection.json`.

Each stage has a predeclared ceiling: SPAdes 2,700 s; DSK and corrected SEER 900 s. The committed `bounded_stage.py` samples the process tree and output directory every 0.5 s, terminates a process group after its ceiling, and writes the command, exit, timeout state, wall time, sampled peak RSS/disk, and log SHA-256. Positive and timeout controls passed before biological execution. Measurements below use SPAdes 4.3.0 default assembly with `-t 2 -m 8`, filter contigs at length >=200 and SPAdes header `_cov_` >=10, QUAST 5.2.0 with `--min-contig 200`, and DSK 2.3.3 with k=31 and abundance minimum 1.

This is a declared current reconstruction protocol. It does not identify the historical Hicks SPAdes/QUAST versions, coverage interpretation, or cohort N50 cutoff.

## Per-isolate results

All four read pairs matched ENA byte sizes and MD5 hashes before execution.

| Rank | Run | Paired compressed bytes | SPAdes wall s | Sampled peak RSS KiB | Sampled peak stage disk bytes | Raw N50 bp | Filtered contigs / bases / N50 bp | Canonical 31-mers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| minimum | `ERR1067833` | 70,656,305 | 319.781 | 1,202,484 | 607,562,038 | 5,973 | 83 / 788,061 / 27,360 | 778,809 |
| p10 | `ERR1067740` | 177,141,208 | 927.973 | 1,505,836 | 1,498,138,988 | 11,305 | 86 / 1,045,003 / 48,575 | 1,030,460 |
| p25 | `ERR1067765` | 226,917,919 | 1,225.248 | 1,745,412 | 2,512,553,407 | 48,784 | 127 / 2,127,568 / 48,784 | 2,101,892 |
| median | `ERR855281` | 325,143,380 | 898.353 | 1,199,408 | 2,173,101,342 | 39,039 | 149 / 2,116,377 / 39,039 | 2,092,013 |

For each isolate, an independent reverse-complement canonical Python count matched every DSK row and abundance exactly: zero missing, extra, duplicate, or abundance-mismatched rows.

The minimum assembly retains only 788,061 bases after the declared coverage filter. It is a QC sensitivity observation, not proof of historical Hicks eligibility or exclusion.

## Corrected SEER n=2 result

Upstream SEER commit `a6bd405754726467a93f39820fb4719457395ae7` was compiled without edits to its SEER source. Its `combineKmers.cpp` Git blob remains `54cb1acb01abf3285e6255f4e6f8480f2a27b4a3`. A synthetic two-file sanity fixture emitted only the truly shared feature.

On the two deterministic panel DSK files:

- wall time: **4.541 s**
- sampled peak process-tree RSS: **227,860 KiB**
- independent shared canonical set: **439,012**
- corrected SEER unique output: **439,012**
- missing/extra/duplicate/tag/abundance errors: **0**

## Corrected SEER n=4 result

The p25 and median DSK files were added to the unchanged minimum/p10 pair. The two earlier DSK ASCII hashes still match `resource_panel_n2.json`. Four distinct sample names and four distinct, nonempty files were verified before execution.

On the deterministic nested four-isolate set:

- wall time: **16.724 s**
- sampled peak process-tree RSS: **417,732 KiB**
- independent canonical union before the `min_samples` filter: **2,243,633**
- independent features present in at least two distinct isolates: **2,093,979**
- corrected SEER rows / unique output: **2,093,979 / 2,093,979**
- missing/extra/below-minimum/duplicate/tag/abundance errors: **0**
- compressed combined output: **23,582,413 bytes**

The independent verifier derived occurrence counts and exact per-sample abundances from the four DSK ASCII inputs, then checked every SEER row and tag. A successful process exit was not used as the correctness oracle.

## Rejected attempt retained

The first minimum-isolate DSK invocation exited 1 because the declared temporary directory did not exist. Its partial HDF5 and empty ASCII output were rejected and deleted. After explicitly creating the directory, DSK exited 0 and passed the independent exact count check. This is recorded in `resource_panel_n2.json`.

## Decision

The n=4 nested resource/correctness gate passes. It proves the declared pipeline works for the minimum, p10, p25, and median size ranks and that corrected SEER is exact for all features present in at least two of those four isolates.

It does **not** establish resource behavior at n=8 or n=1,102, whole-cohort assembly/QC, the historical Hicks feature matrix, or SCM/RF balanced accuracy. Continue only with the predeclared p75, p90, p99, and maximum ranks, then run and independently verify the n=8 corrected-SEER output. Do not begin the full cohort.

Machine-readable evidence and input/tool hashes are in `resource_panel_n4.json`; the earlier n=2 checkpoint remains preserved in `resource_panel_n2.json`. Sub-second DSK stages can complete between 0.5-second samples, so their sampled RSS values are lower bounds; no DSK peak-memory conclusion is drawn from those samples.

## Durable n=8 attempt — terminal result (2026-09-30)

Status: **FAIL at the predeclared maximum-rank SPAdes ceiling**. This does not alter the accepted n=4 PASS above and does not authorize corrected-SEER n=8, the 1,102-run reconstruction, or model training.

GitHub Actions run `36665031444` used workflow/head `4a6e83c89a40ddb6dc82dbcaf9cea226549c1db3`. Seven ranks (minimum, p10, p25, median, p75, p90, p99) produced retained artifacts. Their GitHub ZIP digests matched, retained stage-log hashes matched, filtered FASTA metrics were independently reproduced, and an independent DSK canonical oracle returned zero missing, extra, duplicate, or abundance-mismatched rows for every retained isolate.

The maximum rank `ERR223688` failed in bounded SPAdes 4.3.0 with unchanged `-t 2 -m 8` settings:

- SPAdes start: 2026-09-30 04:06:16 UTC
- declared ceiling: 2,700 s
- `timed_out`: true
- exit: -15
- measured wall: 2,702.424 s
- sampled peak process-tree RSS: 2,518,544 KiB
- sampled peak watched stage disk: 3,415,816,271 bytes
- final watched directory: 1,538,680,619 bytes
- stage-log SHA-256: `e542d9fbd467ee5e654c0f1687dadaf0bd641dff881afb54992900bacc2b30ff`

The workflow uploads isolate evidence only after a successful isolate gate. Therefore no maximum artifact, completed assembly, filter/QC result, DSK output, or independent maximum-isolate k-mer verification survives. The downstream corrected-SEER n=8 job was skipped. A successful n=8 result is not claimed.

Machine-readable terminal evidence: `resource_panel_n8_failure.json`.
