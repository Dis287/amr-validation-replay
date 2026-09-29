# Hicks dataset-2 assembly/QC reconstruction gate

Status: **OPEN / historical eligibility unresolved** (2026-09-29). The corrected two-isolate SEER combine integrity passed; this document addresses a separate assembly provenance question. Do not start the resource panel until a comparable QC handling rule is defined, and do not initiate the 1,102-run reconstruction or model training.

## Primary sources inspected

- Hicks et al. 2019, Materials and methods, "Isolate selection and dataset preparation": https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1007349
- Hicks original S7 XLSX: https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1007349.s007&type=supplementary
- QUAST authors' current manual, metric definition and minimum-contig behavior: https://quast.sourceforge.net/docs/manual.html
- The checksum-verified ENA paired reads, SPAdes 4.3.0 assemblies and filtered FASTAs documented in `TWO_ISOLATE_GATE_RESULT.md`.

## What Hicks actually specifies

Reads were assembled with **default SPAdes**; assembly quality was assessed with **QUAST**; contigs shorter than 200 bp and/or below 10x coverage were removed; isolates whose assembly N50 fell below **the dataset mean minus two standard deviations** were excluded. This is a cohort-relative threshold, not an absolute N50 floor. The article does not identify SPAdes/QUAST versions, the QUAST `--min-contig` setting, the precise coverage estimator, the ordering of filtering and N50 calculation, the input cohort for mean/SD, the SD convention, individual N50 values, or excluded run IDs. The prose lists filtering before exclusion, which suggests but does not prove N50 was computed on filtered contigs.

QUAST's **current** manual states default `--min-contig 500`, and that N50 is computed after this threshold. This cannot be projected backward to the unspecified Hicks QUAST version or assumed to supersede the paper's 200-bp filtering instruction.

Original S7 has six columns (run ID, study ID, dataset membership, AZM MIC, CIP MIC, AST method) and **no N50/QC field**. Its row for `ERR1082197` has dataset membership 2 and AZM MIC 2; S7 contains 1,102 rows assigned to dataset 2, counting any multiple-dataset memberships. This supports the recorded dataset membership, but by itself cannot reconstruct a historical N50 value or the threshold.

## Controlled current-assembly sensitivity

The two raw assembly FASTAs and their length/coverage filtered FASTAs were read directly. N50 was independently calculated by sorting contig lengths descending and finding the length at which cumulative bases first reach half of retained bases. `_cov_` from the current SPAdes header was used as the pilot's coverage measure; whether Hicks applied precisely that interpretation is unverified.

| Isolate | Current FASTA treatment | Contigs | Bases | N50 (bp) |
| --- | --- | ---: | ---: | ---: |
| ERR1067709 | Raw all lengths | 395 | 2,142,914 | 60,512 |
| ERR1067709 | Raw lengths >=500 bp | 90 | 2,105,072 | 61,265 |
| ERR1067709 | >=200 bp and header coverage >=10 | 135 | 2,118,820 | 60,512 |
| ERR1082197 | Raw all lengths | 569 | 2,060,976 | **7,802** |
| ERR1082197 | Raw lengths >=500 bp | 418 | 2,036,957 | **7,890** |
| ERR1082197 | >=200 bp and header coverage >=10 | 85 | 976,099 | **48,515** |
| ERR1082197 | Filtered FASTA, lengths >=500 bp | 66 | 970,726 | **48,515** |

For `ERR1082197`, 353 raw contigs of length >=200 bp totaling 1,017,422 bases have header coverage below 1; a further 22 such contigs totaling 56,370 bases have coverage from 1 to below 10. The filtered assembly loses 1,073,792 bases from the raw >=200-bp assembly. This explains the large difference between the two *current* N50 computations. SPAdes logged a warning that its erroneous-connection coverage threshold may have been determined improperly. None of these observations proves the historical assembly or historical QC outcome.

## Decision

**QC reconstruction: NOT PASSED.** The present raw N50 of 7,802 bp cannot establish ineligibility; the filtered N50 of 48,515 bp cannot establish historical eligibility. Neither can be evaluated against a Hicks dataset-2 mean minus 2 SD without a comparable cohort distribution. S7 membership is not a substitute for a QUAST report or original exclusion list. The corrected SEER test on this second isolate remains valid as a bounded software integrity test, independent of cohort eligibility.

Before the size-stratified resource panel: find original Hicks assembly/QC logs, filtered assemblies, scripts, versions or per-isolate N50/exclusion table if publicly available. Otherwise define and record a provisional SPAdes/coverage/QUAST version and N50-order protocol, verify its QUAST output on both current assemblies, state its difference from the historical unknowns, and design a bounded cohort-QC sensitivity sample. Choose the panel deterministically from the ENA manifest, treating `ERR1082197` separately as an assembly divergence case, not as a representative size stratum. Any provisional panel only establishes resource behavior for its declared protocol; it cannot certify original Hicks eligibility or feature equivalence. Revisit the cohort-relative cutoff only when a suitable cohort N50 distribution exists.
