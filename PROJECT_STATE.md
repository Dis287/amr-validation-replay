# PROJECT_STATE — authoritative continuation record

This file is the single source of truth for continuing the AMR Validation Replay project across chats.

## Operating contract

- Continue until the core best survives.
- Collision = drill deeper, not automatic stop.
- No hype. No speculative claims presented as fact.
- FACT / INFERENCE / UNKNOWN must remain distinct.
- Do not claim a source was checked unless it was actually opened/read.
- Do not mix unrelated projects.
- No dashboard, SaaS, broad architecture, agents, or generic Scientific Claim CI before Experiment 001 resolves.
- Research/tooling only. No diagnosis, prescribing, dosing, treatment selection, or patient-care guidance.
- BioLlama is excluded from this project.

## Project

**Name:** AMR Validation Replay

**Thesis:** a model-validation result is a versioned scientific artifact. In AMR, changing breakpoint authority/version or other phenotype semantics can change the apparent ground truth and therefore the validity of a published/model validation claim.

The surviving layer is **claim-level dependency-aware replay**, not breakpoint interpretation or bulk relabeling.

Core primitives:
1. Claim Manifest
2. Replayability Audit
3. Semantic Replay

Potential claim states:
- UNAFFECTED
- VALID_AFTER_REPLAY
- METRIC_CHANGED
- CONCLUSION_CHANGED
- REVALIDATION_REQUIRED
- NON_REPLAYABLE
- UNKNOWN

## Evidence status

The technical thesis under test is that phenotype semantics can alter a model-validation claim. The measured label and fixed-prediction effects below support that mechanism. The Hicks model result has not yet been independently replayed, and a commercial/buyer claim is not established.

## What is already proven

### Experiment 001A — phenotype semantic drift

Source:
- Hicks et al. 2019, PLOS Computational Biology
- DOI: 10.1371/journal.pcbi.1007349
- Public processed S7-derived gonococcal table from `Leonardini/CABBAGE`
- File: `SelectedTables/PMID_31479500_pcbi.1007349.s007_NGonorrhoeae_Processed.csv`

AZM thresholds used:
- EUCAST: non-susceptible if MIC > 0.25 µg/mL
- CLSI: non-susceptible if MIC > 1.0 µg/mL

Independently reproduced on 3,946 isolates:
- EUCAST NS = 1,827
- CLSI NS = 536
- concordant = 2,655
- discordant = 1,291
- concordance = 67.2833%
- discordance = 32.7167%

Status:
- `LABEL_DRIFT_REPRODUCED = YES`
- `HICKS_MODEL_METRIC_REPLAY_REPRODUCED = NO`

### Experiment 001B — independent fixed-prediction metric sensitivity

A separate deterministic mechanism-feature classifier on 3,799 overlapping isolates produced five-fold out-of-fold EUCAST-trained predictions. Scoring the same prediction vector against EUCAST labels yielded bACC 62.47%; scoring it against CLSI labels yielded 56.41%, a change of −6.05 percentage points. This is a measured fixed-prediction result using a different classifier and outer split design. It is not a Hicks SCM/RF reproduction. See `experiments/001_gonococcus_eucast_vs_clsi/independent_mechanism_replay.json`.

### Published model-performance evidence

Hicks supplementary S5 reports aggregate mean balanced accuracy:

| Model | EUCAST | CLSI | Difference |
| --- | ---: | ---: | ---: |
| SCM S/NS | 77.60% | 85.32% | +7.72 points |
| RF-C S/NS | 84.04% | 88.03% | +3.99 points |

These are **published values only**. They have not been independently reproduced here.

## Critical correction to evaluation design

The Hicks study did **not** use five-fold CV as the outer evaluation.

Published design:
- 10 random, distinct, stratified outer partitions
- 2/3 training
- 1/3 testing
- mean balanced accuracy and 95% CI over the 10 repeats
- five-fold CV was used inside model selection/tuning

Model recipe:
- assemblies processed into DSK 31-mers
- SEER `combinekmers`
- singleton 31-mers removed
- binary presence/absence features
- SCM via Kover, at most five rules
- RF via ranger, 1,000 trees
- inner five-fold tuning/model selection

## Current provenance boundary

Verified public:
- SRA/ENA accessions
- MIC/method metadata
- S7
- supplementary S5 aggregate performance
- published model recipe

Still unverified / unrecovered:
- original outer split memberships
- random seeds
- trained model files
- per-isolate prediction vectors
- exact assembled 31-mer feature matrix

Do **not** call the study non-replayable yet.

A from-scratch reconstruction remains possible in principle because public sequence data and phenotype metadata exist.

## Dataset-2 evidence chain and pilot (2026-09-29)

- The Grad-authored Zenodo archive `10.5281/zenodo.2618836` passed its published file MD5. All 1,102 Hicks S7 dataset-2 runs map one-to-one to its 1,102 FASTA members through the recorded third-party accession mapping. S7 AZM non-susceptible counts also match the paper's S5 dataset-2 counts. See `experiments/001_gonococcus_eucast_vs_clsi/ZENODO_OVERLAP.md` and `zenodo_overlap.json`.
- The Zenodo assemblies came from the 2016 source study's Velvet pipeline. Hicks describes SPAdes assembly. Accession overlap is verified; Hicks-equivalent assembly/31-mer features are **not** verified. Do not substitute Velvet features into a faithful reconstruction.
- The official ENA filereport resolves all 1,102 dataset-2 paired runs: 2,204 compressed FASTQs totaling 344,835,597,770 reported bytes. The manifest and generation script are committed. See `RAW_READ_FEASIBILITY.md` and `ena_dataset2_manifest.tsv`.
- One S7 dataset-2 run, `ERR1067709`, was downloaded and checksum-verified. A SPAdes 4.3.0 assembly completed in 16 min 26 sec to contigs output, with 161 MB final output directory. A documented pilot filter retained 135 contigs and yielded 2,095,091 direct distinct forward 31-mers. SPAdes 3.13.0 failed in this runtime; the exact Hicks SPAdes version remains unidentified. This pilot does **not** produce a DSK/SEER matrix, model predictions, or bACC. See `RAW_READ_PILOT.md`.
- The related later `gradlab/mtrC-GWAS` SharePoint archive remains unverified for accessibility, contents, and equivalence; it is separate from the checked Zenodo archive.
- Primary DSK and SEER documentation confirms reverse-complement canonicalization and SEER `combineKmers --min_samples 2`. The pilot's direct forward 31-mer number cannot stand in for DSK output; a single isolate cannot test the shared-feature matrix. A second distinct dataset-2 isolate is required for the minimum combine pilot. See `KMER_RECONSTRUCTION_GATE.md`. Original SEER source resolves `-r` (despite no-argument help showing `-s`), silently resets an invalid minimum to 1, and skips missing input files. The gate requires explicit two-input and shared-set checks. `FEATURE_GENERATION_GATE.md` retains the later size-ranked panel but its earlier order is superseded.

## Two-isolate gate result (2026-09-29)

Both ENA read pairs (ERR1067709 and ERR1082197) passed manifest size/MD5 verification and assembled with declared SPAdes 4.3.0 settings. The first contig SHA-256 reproduced the earlier pilot exactly. DSK 2.3.3 canonical 31-mer counts matched an independent per-k-mer and abundance check for both isolates (2,089,781 and 962,089). Their independent shared set contained 875,897 k-mers.

Original SEER 1.1.3 `combineKmers --min_samples 2` exited zero but emitted 875,898 rows: one false singleton and one duplicated sample tag on a shared row. The independent verifier failed as required. **Toolchain feature-integrity gate = FAIL for this binary; no Hicks metric replay.** The second assembly raw N50 was 7,802 bp, and cohort-level N50 eligibility remains unresolved. See `TWO_ISOLATE_GATE_RESULT.md` and `verify_two_isolate_features.py`.

A source-identified corrected upstream SEER implementation at commit `a6bd405754726467a93f39820fb4719457395ae7` was compiled without source edits and run on the **same** DSK ASCII files and sample list. It emitted exactly 875,897 rows, matching the independent shared set with zero missing/extra features or sample/abundance errors. **Corrected two-isolate feature-combine integrity gate = PASS.** The historical 1.1.3 failure remains documented. See `CORRECTED_SEER_RETEST.md`. This pass is limited to two isolates and is not proof of Hicks's exact SEER version or full-cohort replay.

A declared current QC/resource protocol is now in use while historical Hicks QC remains unresolved. The deterministic minimum, p10, p25, and median ranks passed SPAdes, filtered-assembly/QUAST, exact independent DSK checks, and corrected-SEER verification. At n=4, the independent truth contained 2,093,979 canonical 31-mers present in at least two isolates; corrected SEER emitted exactly 2,093,979 unique rows with zero missing, extra, duplicate, tag, or abundance errors. See `RESOURCE_PANEL_CHECKPOINT.md`, `resource_panel_n2.json`, and `resource_panel_n4.json`. This is a PASS at n=4 only. Next: execute only the predeclared p75, p90, p99, and maximum ranks and verify the corrected-SEER n=8 output. Full-cohort reconstruction and model training remain unauthorized.

### Source-identified SEER correction

The original SEER repository contains an explicit repair commit:
`a6bd405754726467a93f39820fb4719457395ae7` (2017-11-17), titled
**"Fix to combineKmers. Thanks to Kevin Ma"**. It changes the defective EOF loop from
`while (kmer_counts)` followed by extraction to
`while (kmer_counts >> kmer >> abundance)`, preventing the stale final record from
being appended. This repair predates the 2019 Hicks publication, but the exact SEER
revision Hicks used remains UNKNOWN.

Use that source revision (or a later revision proven to contain exactly this fix) on
the **same two verified DSK ASCII files**. Require exact equality with the independent
875,897-k-mer intersection and exact sample/abundance tags before proceeding.

The second isolate's low SPAdes-4.3.0 N50 does not invalidate its use for this bounded
software-integrity retest. It does block using that isolate as evidence about cohort
feature/resource behavior until the assembly-QC discrepancy is resolved. Hicks reports
removing assemblies with N50 below two dataset standard deviations; because
`ERR1082197` is present in the paper's S7 dataset-2 record, S7 records its dataset-2 membership, but no original N50 or exclusion list was recovered;
this alone does not establish that our SPAdes-4.3.0 reconstruction is equivalent. Treat the low N50 as a reconstruction
divergence signal, not as proof that the published isolate was ineligible.

**Resource decision:** full 1,102-run reconstruction is not yet authorized by feasibility evidence. The single run demonstrates bounded assembly, but runtime variation, aggregate feature union, DSK/SEER behavior, and Kover/ranger memory and compute remain unmeasured. Do not download the entire dataset on a one-isolate extrapolation.

## Durable n=8 execution result (2026-09-30)

The transient workspace remains unauthorized evidence. Vanished earlier p75/p90/p99 outputs remain VOID and were not reconstructed.

Durable GitHub Actions run `36665031444` executed the pinned envelope:
- per-isolate runner: `28b3595a3eaf13388081d00dcd62fcebd023a8ac`
- independent n=8 verifier: `b3607d790935548d74c9d533b8b355a2184b3e45`
- workflow/head: `4a6e83c89a40ddb6dc82dbcaf9cea226549c1db3`

Result: **n=8 GATE FAIL**.

Seven ranks—minimum, p10, p25, median, p75, p90, and p99—produced retained artifacts whose GitHub archive digests matched and whose retained DSK files passed an independent exact canonical 31-mer and abundance audit with zero missing, extra, duplicate, or abundance-mismatched rows.

The maximum rank, `ERR223688`, reached the unchanged SPAdes 4.3.0 command (`-t 2 -m 8`) but exceeded the declared 2,700-second ceiling. Surviving job-log evidence records `timed_out=true`, exit `-15`, wall 2,702.424 s, peak process-tree RSS 2,518,544 KiB, peak watched stage disk 3,415,816,271 bytes, and stage-log SHA-256 `e542d9fbd467ee5e654c0f1687dadaf0bd641dff881afb54992900bacc2b30ff`. The success-gated maximum artifact was not uploaded, so no maximum filtered/QC/DSK evidence survives. Corrected-SEER n=8 was skipped.

Acceptance law:
- `641b66604c5a484c2e9a20300a192b9068bfd74c` (n=4 PASS) remains the last passing scientific checkpoint.
- n=8 correctness and resource feasibility are **NOT established**.
- The fixed ceiling is not changed to manufacture a pass.
- Full 1,102-run reconstruction and model training remain **UNAUTHORIZED**.
- Exact machine-readable failure evidence is in `experiments/001_gonococcus_eucast_vs_clsi/resource_panel_n8_failure.json`.

Ceiling-intent audit: **UNKNOWN**. Repository history proves that the 2,700-second
SPAdes ceiling was fixed and enforced, but it does not prove whether that value
was a resource-feasibility acceptance threshold or an operational safety bound.
The first relevant committed occurrence is
`e6628e6f82787afd2d34d7d5a092ca933eb376ef`, which commits the ceiling,
bounded runner, and already measured n=2 results together without a
value-selection rationale. No max-isolate rerun or replacement experiment is
authorized until a separately named prospective protocol is explicitly frozen
in a future commit. See
`experiments/001_gonococcus_eucast_vs_clsi/CEILING_INTENT_DETERMINATION.md` and
`ceiling_intent_determination.json`.

## Prospective maximum-isolate resource resolution

`MAX_ISOLATE_RESOURCE_RESOLUTION_V1` is now **FROZEN / NOT EXECUTED**. This is
a separately named prospective infrastructure experiment for `ERR223688`; it
does not alter or retry the failed n=8 gate. The protocol preserves the exact
ENA inputs and hashes, SPAdes 4.3.0 default paired-read assembly with `-t 2 -m
8`, the declared filter/QUAST/DSK procedures, and exact independent canonical
31-mer verification.

The seven surviving resource points are nonmonotone in runtime versus compressed
input size, so no linear completion prediction is accepted. The new 5,400-second
SPAdes limit is a containment decision providing one additional 2,700-second
observation interval beyond the old censor point, not an estimate of required
runtime. The compute class, operational RSS/disk caps, no-retry law, explicit
failure taxonomy, and always-retain evidence bundle are frozen in
`experiments/001_gonococcus_eucast_vs_clsi/MAX_ISOLATE_RESOURCE_RESOLUTION_V1.md`
and `max_isolate_resource_resolution_v1.json`.

This protocol commit does **not** authorize execution. Execution is a separate
next step. Even a future PASS would leave the original n=8 gate failed and would
not authorize corrected-SEER n=8, the 1,102-run reconstruction, or model
training.

## Active task — Experiment 001 only

**Objective:** independently recompute balanced accuracy under EUCAST vs CLSI with the Hicks model/evaluation logic as faithfully as possible.

Order of work:
1. Recover original predictions/folds/seeds/models if publicly available.
2. If unavailable, reconstruct from public sequence data.
3. Preserve the paper's 10 stratified 2/3–1/3 outer partitions as the target design.
4. Use the published 31-mer/Kover/ranger recipe or document every unavoidable deviation.
5. Produce per-isolate out-of-sample predictions and balanced accuracy under the two breakpoint semantics.
6. Compare with published S5 values.
7. Only then classify the claim as METRIC_CHANGED / CONCLUSION_CHANGED / etc.

## Integrity rule

Do not confuse these two estimands:

1. **Paper-specific reproduction:** separately train EUCAST and CLSI models using the paper's procedure.
2. **Fixed-prediction semantic replay:** freeze one model's predictions and rescore the same isolates under both label definitions.

Both can be scientifically useful, but they are different questions.

Any 001B result using a different classifier/split design is **not** a reproduction of Hicks and must remain labeled accordingly.

## Hard gate

No architecture expansion until Experiment 001 is resolved.

PASS:
- real model metric change independently reproduced under faithful or clearly documented reconstruction.

DOWNGRADE:
- label drift is large but validation metric effect is small.

PROVENANCE-LIMITED:
- exact reproduction cannot be achieved because required original artifacts are unrecoverable, while a documented reconstruction remains possible.

KILL:
- existing tooling already provides the complete claim-level dependency/replay decision with no meaningful additional logic.

## Current repo

https://github.com/Dis287/amr-validation-replay

Two-isolate corrected-SEER result was committed as `ee30c417c14097fec5e4e2c04797c30212b55033`; read the current main files linked above for authoritative status.

## Resume instruction

Continue only from this line:

> Search for original Hicks-specific partitions, predictions, models, assemblies, or feature matrices. The corrected upstream SEER two-isolate combine passed exact independent feature and tag checks; the old 1.1.3 binary failed. Resolve cohort assembly/QC, then run the deterministic resource-variation panel before deciding on full dataset-2 reconstruction. Keep Hicks-specific versions, partitions, and metric replay unverified. Preserve separate paper-style and fixed-prediction estimands. Commit only Experiment 001 evidence. No architecture, dashboard, or scope expansion.
