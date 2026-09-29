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
- `MODEL_METRIC_REPLAY_REPRODUCED = NO`

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

## Related assembly lead

`gradlab/mtrC-GWAS` links an assemblies archive, but:
- it is a later related study
- archive accessibility = UNVERIFIED
- exact overlap with Hicks cohort = UNVERIFIED
- assembly equivalence = UNVERIFIED

Do not substitute it into a Hicks reconstruction without checking provenance and accession overlap.

A Grad-authored Zenodo gonococcal assembly archive from March 2019 is also a possible constituent-data lead, but overlap/equivalence remain UNVERIFIED.

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

Latest verified provenance commit before this state file:
`127454ee10435ed52f562398d387c194e7250d45`

## Resume instruction

Continue only from this line:

> Recover the original Hicks 2019 outer partitions/predictions/models if possible; otherwise perform the smallest faithful reconstruction necessary to independently recompute EUCAST-vs-CLSI balanced accuracy. Commit only Experiment 001 evidence. No new architecture, dashboard, or scope expansion.
