# Corrected SEER retest on the identical two-isolate DSK inputs

**Gate outcome: PASS for feature-combine integrity on these two isolates.** Measured 2026-09-29. This supersedes only the SEER 1.1.3 toolchain failure in `TWO_ISOLATE_GATE_RESULT.md`; it does not establish Hicks's exact SEER revision, dataset-2 cohort QC, full-cohort feasibility, or SCM/RF balanced accuracy.

## Corrected implementation provenance

Original SEER source was obtained from upstream GitHub commit `a6bd405754726467a93f39820fb4719457395ae7` as a source archive (SHA-256 `e6ed83b2e60c1c45beeee24949203bd34e7dbc5107b77bc120d5afddff8e8e01`). The source at this commit has the corrected input loop `while (kmer_counts >> kmer >> abundance)` in `src/combineKmers.cpp`. Its Git blob SHA is `54cb1acb01abf3285e6255f4e6f8480f2a27b4a3`; the local extracted file produced the same `git hash-object`. The other two compiled source files, `src/combineInit.cpp` and `src/combineCmdLine.cpp`, had Git blob SHAs `8a0b168e51fa8f6994fc54035d4abd2b970effe7` and `4cd634590631ff61096174d9c6eb45c1517f2af8`. Upstream source: https://github.com/johnlees/seer/blob/a6bd405754726467a93f39820fb4719457395ae7/src/combineKmers.cpp

Built **these upstream source files without source edits** using:

```sh
g++ -O3 -std=c++11 -I/usr/include -o combineKmers-a6bd405 \
  src/combineInit.cpp src/combineCmdLine.cpp src/combineKmers.cpp \
  -lgzstream -lz -lboost_program_options
```

Runtime/development libraries: Ubuntu Boost Program Options 1.83.0 (`1.83.0-2.1ubuntu3.2`) and gzstream (`1.5+git20171107.9a20658-1`), with zlib. The resulting binary SHA-256 was `23ea9102d2bd20da51437db01ef092448ec3604185108db06eb040b3f505a7bd`. This is a locally compiled upstream revision, not an identified Hicks binary. On the two-file synthetic sanity fixture described in `KMER_RECONSTRUCTION_GATE.md`, it emitted only the genuinely shared `AAAA` row.

## Same real inputs, exact check

The input DSK ASCII SHA-256 hashes were unchanged from the failed historical-binary run:

| Isolate | DSK ASCII SHA-256 | Distinct canonical 31-mers |
| --- | --- | ---: |
| `ERR1067709` | `35b2dd347eb891ab72952122998f5fc179b80beba06fe1e75e73c3a12fced239` | 2,089,781 |
| `ERR1082197` | `38acef2c926eea87e8e44ec1d1505e51925c67e1d7d8beee052b54cbb541bc3b` | 962,089 |

The two-line sample list SHA-256 remained `72517796761219d0c44983fa971be2c443c3944ab9928321523b9b5debbd210f`. The command was `combineKmers-a6bd405 -r two_samples.tsv -o two_combined_corrected --min_samples 2`. It exited 0 in **8.125 seconds**, with child peak RSS **365,212 KiB**. Output gzip: **9,139,914 bytes**, SHA-256 `e16e487b46f6aa09c71e764053016ccba25bb85ff7b39f17b7c80280370bfee0`.

The committed independent `verify_two_isolate_features.py` read both filtered FASTAs, both DSK ASCII files, and the corrected gzip. It exited **0** and found:

- DSK versus independent canonical counter: **zero** missing, extra, duplicate, or abundance-mismatched rows for each isolate.
- Independently shared set: **875,897** 31-mers.
- Corrected SEER unique output: **875,897** rows.
- Missing shared features: **0**.
- Extra/singleton features: **0**.
- Incorrect or repeated sample/abundance tags: **0**.

A separate old-versus-corrected comparison found precisely one old-only false singleton row and one shared row whose duplicate tag was removed; no corrected-only rows. This matches the two discrepancies in `TWO_ISOLATE_GATE_RESULT.md`.

## Decision boundary

The **two-isolate feature-combine integrity gate passes with the corrected upstream revision**. The historical SEER 1.1.3 binary remains failed. The exact Hicks SEER revision and feature matrix remain unknown. `ERR1082197` has a low SPAdes-4.3.0 raw N50 (7,802 bp); this is a reconstruction-divergence/QC question, not proof of original-study ineligibility. The full 1,102-run reconstruction is not authorized from a two-isolate test. Next: resolve cohort assembly/QC handling and test resource variation on a deterministic panel before any full-cohort run. No model prediction or balanced accuracy was generated.
