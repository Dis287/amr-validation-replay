# Deterministic resource panel — n=2 checkpoint

Status: **PASS at nested subset n=2 only** (2026-09-30). The n=4 and n=8 resource/union gates remain open. This checkpoint does not authorize 1,102-run reconstruction or model training.

## Declared protocol

The eight panel members were selected before execution by sorting all 1,102 ENA manifest rows by total paired compressed FASTQ bytes, breaking ties by run accession, and taking fixed ranks: minimum, p10, p25, median, p75, p90, p99, maximum. The exact rows are in `resource_panel_selection.json`.

Each stage has a predeclared ceiling: SPAdes 2,700 s; DSK and corrected SEER 900 s. The committed `bounded_stage.py` samples the process tree and output directory every 0.5 s, terminates a process group after its ceiling, and writes the command, exit, timeout state, wall time, sampled peak RSS/disk, and log SHA-256. Positive and timeout controls passed before biological execution. Measurements below use SPAdes 4.3.0 default assembly with `-t 2 -m 8`, filter contigs at length >=200 and SPAdes header `_cov_` >=10, QUAST 5.2.0 with `--min-contig 200`, and DSK 2.3.3 with k=31 and abundance minimum 1.

This is a declared current reconstruction protocol. It does not identify the historical Hicks SPAdes/QUAST versions, coverage interpretation, or cohort N50 cutoff.

## Per-isolate results

Both read pairs matched ENA byte sizes and MD5 hashes before execution.

| Rank | Run | Paired compressed bytes | SPAdes wall s | Sampled peak RSS KiB | Sampled peak stage disk bytes | Raw N50 bp | Filtered contigs / bases / N50 bp | Canonical 31-mers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| minimum | `ERR1067833` | 70,656,305 | 319.781 | 1,202,484 | 607,562,038 | 5,973 | 83 / 788,061 / 27,360 | 778,809 |
| p10 | `ERR1067740` | 177,141,208 | 927.973 | 1,505,836 | 1,498,138,988 | 11,305 | 86 / 1,045,003 / 48,575 | 1,030,460 |

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

## Rejected attempt retained

The first minimum-isolate DSK invocation exited 1 because the declared temporary directory did not exist. Its partial HDF5 and empty ASCII output were rejected and deleted. After explicitly creating the directory, DSK exited 0 and passed the independent exact count check. This is recorded in `resource_panel_n2.json`.

## Decision

The n=2 nested resource/correctness gate passes. It proves the declared pipeline works for the minimum and p10 size ranks and that corrected SEER is exact for their shared features.

It does **not** establish resource growth at n=4 or n=8, union-memory behavior at larger subsets, whole-cohort assembly/QC, the historical Hicks feature matrix, or SCM/RF balanced accuracy. Continue next with the predeclared p25 and median ranks, then run and independently verify the n=4 corrected-SEER union. Do not begin the full cohort.

Machine-readable evidence and input/tool hashes are in `resource_panel_n2.json`. Sub-second DSK stages can complete between 0.5-second samples, so their sampled RSS values are lower bounds; no DSK peak-memory conclusion is drawn from those samples.
