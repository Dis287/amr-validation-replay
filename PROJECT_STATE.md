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

A declared QC/resource protocol is in use while historical Hicks QC remains unresolved. The deterministic minimum, p10, p25, and median ranks passed SPAdes, filtered-assembly/QUAST, exact independent DSK checks, and corrected-SEER verification. At n=4, the independent truth contained 2,093,979 canonical 31-mers present in at least two isolates; corrected SEER emitted exactly 2,093,979 unique rows with zero missing, extra, duplicate, tag, or abundance errors. See `RESOURCE_PANEL_CHECKPOINT.md`, `resource_panel_n2.json`, and `resource_panel_n4.json`. This remains the last passing combined-feature checkpoint. The later original n=8 gate failed, and corrected-SEER n=8 has not run. Full-cohort reconstruction and model training remain unauthorized.

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

## Maximum-isolate resource resolution

`MAX_ISOLATE_RESOURCE_RESOLUTION_V1` is a terminal
`INFRASTRUCTURE_PREFLIGHT_FAILURE`. GitHub Actions run `38591577348` executed
once from `64b3f06d5eeb9a89a3f69f0abfc2c3ed42dc6d84`. Both uploaded artifact ZIPs
and the internal evidence TAR were independently hash-verified. The requested
standard `ubuntu-24.04` x64 runner passed CPU, RAM, architecture, tool-hash and
single-attempt checks and had 90,323,972,096 free bytes, but the harness
rejected its 154,894,188,544-byte mounted filesystem total against a 14 GiB
comparison. No biological input was downloaded and no scientific stage ran.
V1 must not be rerun or reclassified. See
`MAX_ISOLATE_RESOURCE_RESOLUTION_V1_FAILURE.md` and
`max_isolate_resource_resolution_v1_failure.json`.

An accidental second V1 dispatch, GitHub Actions run `38594673384`, was stopped
at preflight by V1's single-attempt guard after detecting prior run
`38591577348`. Its durable records show `input_integrity = NOT_REACHED`, an
empty biological-input list, and an empty scientific-command ledger. Both
artifact ZIP hashes and the internal evidence TAR hash were independently
verified. This dispatch produced no scientific evidence, does not alter V1's
terminal result, and must not be repeated. See
`MAX_ISOLATE_RESOURCE_RESOLUTION_V1_ACCIDENTAL_REDISPATCH.md` and
`max_isolate_resource_resolution_v1_accidental_redispatch.json`.

`MAX_ISOLATE_RESOURCE_RESOLUTION_V2` was frozen as a separately named
prospective experiment, not a V1 retry. It inherited every V1 scientific
identity, parameter and scientific/resource ceiling. Its sole infrastructure
correction was to stop treating total mounted backing capacity as experiment
consumption. Its terminal execution result is recorded below.

The seven surviving resource points are nonmonotone in runtime versus compressed
input size, so no linear completion prediction is accepted. The new 5,400-second
SPAdes limit is a containment decision providing one additional 2,700-second
observation interval beyond the old censor point, not an estimate of required
runtime. The compute class, operational RSS/disk caps, no-retry law, explicit
failure taxonomy, and always-retain evidence bundle are frozen in
`experiments/001_gonococcus_eucast_vs_clsi/MAX_ISOLATE_RESOURCE_RESOLUTION_V1.md`
and `max_isolate_resource_resolution_v1.json`.

The V2 protocol and harness commits did not themselves execute the experiment.
The harness was manual-only and single-attempt. Its one terminal execution is
recorded below; no second V2 dispatch is authorized.

V2 was dispatched once as GitHub Actions run `38600205769` from commit
`4bea3506388d5b48b579caf3aae7aed374420f69` and is now terminal
`FAIL_DSK_STAGE`. Exact FASTQ integrity passed. SPAdes completed with exit zero
in 2,934.196472 seconds inside the 5,400-second ceiling, with no recorded OOM,
disk exhaustion, timeout, or envelope breach. Filtering and QUAST completed;
filtered N50 was 40,334 bp. DSK then exited `1` after 0.534487 seconds because
the harness supplied `work/dsk_tmp` to `-out-tmp` without creating that
directory. No DSK ASCII output or independent-oracle result exists, so the
surviving HDF5 is not accepted. V2 must not be rerun or reclassified. See
`MAX_ISOLATE_RESOURCE_RESOLUTION_V2_FAILURE.md` and
`max_isolate_resource_resolution_v2_failure.json`.

`MAX_ISOLATE_RESOURCE_RESOLUTION_V3` is
**PASS_INDEPENDENTLY_AUDITED**. GitHub Actions run `38680749205` executed once
from frozen commit `0cd6f51e6fa567b9cb00c05f8a6b5a8d048b76cd`. Both exact FASTQ
identities passed. SPAdes 4.3.0 completed with unchanged `-t 2 -m 8` in
2,920.074492 seconds inside the prospective 5,400-second limit. Filtering and
QUAST completed; filtered N50 was 40,334 bp. DSK 2.3.3 and DSK2ASCII completed
after the prospectively declared `work/dsk_tmp` preparation.

The independent A<C<T<G reverse-complement oracle found 2,098,204 expected and
2,098,204 observed canonical 31-mers, with zero missing, extra, duplicate, or
abundance-mismatched rows. Both GitHub artifact ZIP digests, the internal TAR
digest/ledger, all stage records, and all 32 retained primary file paths, sizes,
and SHA-256 values were independently audited. See
`MAX_ISOLATE_RESOURCE_RESOLUTION_V3_RESULT.md` and
`max_isolate_resource_resolution_v3_result.json`.

This V3 pass does not change the terminal failures of the original n=8 gate,
V1, or V2. It does not establish corrected-SEER n=8 correctness, full-cohort
feasibility, or Hicks model replay.

The earlier corrected-SEER n=8 input-availability audit remains historically
valid: on 2026-10-15, the seven recorded passing-isolate Actions artifacts were
unavailable. That blockage triggered the separately frozen
`N8_DSK_EXACT_INPUT_RECOVERY_V1` experiment and is not rewritten.

`N8_DSK_EXACT_INPUT_RECOVERY_V1` is now
**PASS_INDEPENDENTLY_AUDITED**. Manual GitHub Actions run `38922709421`
executed once from frozen commit
`b10e424a17b4ba82586159493e22e398b69aa03b`. Phase A found all seven
historical artifacts unavailable and froze the complete seven-isolate missing
subset before any FASTQ download. Each isolate then completed exactly one
prospectively bounded regeneration path with no automatic or silent retry.

For `min`, `p10`, `p25`, `median`, `p75`, `p90`, and `p99`, the
frozen FASTQ byte counts and MD5 values, filtered-FASTA SHA-256, DSK row count,
DSK byte count, and DSK SHA-256 all matched exactly. Every independent A<C<T<G
reverse-complement oracle reported zero missing, extra, duplicate, and
abundance-mismatched rows. The seven accepted DSK files total exactly
497,549,628 bytes.

The versioned release
`experiment001-n8-exact-inputs-v1` contains exactly those seven DSK inputs and
the complete manifest. A fresh release download independently matched the
120,220,273-byte asset and SHA-256
`b132c289f07d18378e052b69d2987fb6f5ee03f74d38958cdc7c1e7f1f2aca5b`;
every extracted DSK file again matched its frozen identity. See
`EXACT_INPUT_RECOVERY_V1_RESULT.md` and
`exact_input_recovery_v1_result.json`.

This PASS resolves only the exact-input availability gate. It does not rewrite
the failed original n=8 gate, V1, or V2.

`CORRECTED_SEER_N8_COMBINE_V1` is terminal after exactly one manual
dispatch. Run `38962929988`, from
`4b8813636a34da16e18eda208da9aed8ef2a19e9`, passed preflight and then
failed before input acquisition because the harness attempted to open
`$ROOT/sources/seven.tar.gz` without first creating `$ROOT/sources`.
No biological input archive was written; exact input verification, SEER build,
combine, and the independent oracle were not reached. No result release was
created.

The emitted V1 state `FAIL_INPUT_INTEGRITY` is preserved, but it is not
evidence of a biological-input mismatch because no input was downloaded or
checked. The independently audited cause is a pre-input harness filesystem
initialization defect. Candidate, receipt, final-audit, final-receipt, and
run-log archives survived and were hash-verified. See
`CORRECTED_SEER_N8_COMBINE_V1_FAILURE.md` and
`corrected_seer_n8_combine_v1_failure.json`.

GitHub's earlier validation-only run `38962302292` remains separate: it
contains zero jobs and zero artifacts and was caused by use of unavailable
`runner.temp` in workflow-level `env`. It produced no scientific evidence.

V1 must not be rerun, reclassified, or overwritten. Corrected-SEER n=8
correctness and resource use remain unestablished.

`CORRECTED_SEER_N8_COMBINE_V2` is now **FROZEN / NOT EXECUTED** as a
separately named prospective experiment. Its inputs, input policy, corrected
SEER source/build/command, sample list, execution envelope, oracle,
terminal states, retry policy, and PASS rule are value-for-value identical to
V1. Its only allowed infrastructure correction is creation of the full working
directory tree before any acquisition destination is opened. The future harness
must pass a synthetic fresh-root acquisition-path test before commit. See
`CORRECTED_SEER_N8_COMBINE_V2.md`,
`corrected_seer_n8_combine_v2.json`, and
`corrected_seer_n8_combine_v2_protocol_audit.json`.

`CORRECTED_SEER_N8_COMBINE_V2` is terminal after exactly one manual
dispatch, run `38964235718`, from
`995e40f42a2bca66b9b6d81def39fc736dc8af62`. Preflight passed. The
seven-input release downloaded and all seven extracted DSK files matched their
frozen identities. Acquisition of maximum artifact `11950830857` returned a
non-200 status before `sources/maximum.zip` survived, so all-eight input
verification, SEER build, combine, and the independent oracle were not reached.

The emitted state `FAIL_INPUT_INTEGRITY` is preserved. It is not proof of a
maximum DSK mismatch: the runner received no outer ZIP to hash. The exact HTTP
status was not recorded and is UNKNOWN. An independent post-run download
verified the still-available source artifact's outer ZIP, internal TAR, and
maximum DSK against every frozen byte count and SHA-256. That establishes
recoverability, not a V2 pass. See
`CORRECTED_SEER_N8_COMBINE_V2_FAILURE.md` and
`corrected_seer_n8_combine_v2_failure.json`.

V2 must not be rerun or reclassified.

`N8_DSK_UNIFIED_RELEASE_V1` is now **FROZEN / NOT EXECUTED**. It preserves
all eight V2 input identities and the exact sample list. It may only package the
eight already verified files into a deterministic archive, create release
`experiment001-n8-exact-inputs-v2` once, download it fresh, and independently
reverify the archive and every extracted file. Regeneration, substitution,
biological download, SPAdes, DSK execution, SEER, and model training are
forbidden. See `N8_DSK_UNIFIED_RELEASE_V1.md`,
`n8_dsk_unified_release_v1.json`, and
`n8_dsk_unified_release_v1_protocol_audit.json`.

The dedicated local `N8_DSK_UNIFIED_RELEASE_V1` harness is now **FROZEN /
NOT EXECUTED**. Static checks passed for protected protocol hashes, exact
pre-copy and post-copy input verification, exact sample list, deterministic tar
and gzip metadata, archive determinism, safe extraction, fresh-readback logic,
repository-head guard, and the 3 GiB free-space preflight. The harness itself
does not create a release; release creation remains a separately invoked,
one-attempt action after preflight.

No packaging or release creation occurred in this harness-freeze step. The next
allowed action is independent remote read-back followed by the one permitted
local preflight and execution decision. Only a read-back-verified unified
release may authorize a new corrected-SEER n=8 combine protocol. Full-cohort
reconstruction and model training remain unauthorized.

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

> Preserve terminal corrected-SEER n=8 V1/V2 and all earlier evidence. The unified-release V1 protocol and dedicated local one-attempt harness are frozen but not executed. Next independently read back the harness, verify hashes and absent release, then run its preflight. If the frozen 3 GiB free-space minimum fails, record terminal infrastructure failure; do not lower it. Do not authorize a new combine until a unified release is freshly downloaded and all eight identities pass.
