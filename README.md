# AMR Validation Replay

Dependency-aware revalidation of AMR model claims under changing susceptibility semantics.

## Status

Research prototype. Research/evaluation tooling only.

This project does **not** provide diagnosis, treatment recommendations, dosing, formulations,
or patient-care guidance.

## Core question

When a scientific validation claim depends on a breakpoint standard or other phenotype semantics,
does that claim still hold when the dependency changes?

The system is designed around three outputs:

1. **Claim manifest** — what semantic dependencies does a validation claim rely on?
2. **Replayability audit** — is enough provenance preserved to reproduce/reinterpret the claim?
3. **Semantic replay** — if the semantic dependency changes, does the validation conclusion survive?

## Claim states

- UNAFFECTED
- VALID_AFTER_REPLAY
- METRIC_CHANGED
- CONCLUSION_CHANGED
- REVALIDATION_REQUIRED
- NON_REPLAYABLE
- UNKNOWN

## Experiment 001

Reproduce the known EUCAST-vs-CLSI azithromycin phenotype split from:

Hicks et al. 2019, PLOS Computational Biology,
"Evaluation of parameters affecting performance and reliability of machine learning-based
antibiotic susceptibility testing from whole genome sequencing data."

Using the public processed S7 gonococcal MIC table available in CABBAGE:

- n = 3,946 isolates
- EUCAST AZM non-susceptible threshold used by the paper: MIC > 0.25 µg/mL
- CLSI AZM non-susceptible threshold used by the paper: MIC > 1.0 µg/mL
- concordant labels = 2,655
- discordant labels = 1,291
- concordance = 67.2833%
- discordance = 32.7167%

This independently reproduces the paper's reported ~67% cross-standard concordance.

The paper further reports significantly higher balanced accuracy for AZM classifiers under CLSI
than EUCAST across datasets evaluated under both standards (P < 0.0001). That metric-impact claim
is currently recorded as **published evidence**, not yet an independently rerun model result.

## Independent metric replay (Experiment 001B)

Using 3,799 isolates shared between the CABBAGE-processed 2019 gonococcal MIC table and Grad Lab's
public `mtrC-GWAS` resistance-mechanism metadata, a deterministic 5-fold out-of-fold mechanism
classifier was trained without using MIC as a feature.

With the **same EUCAST-trained prediction vector**:
- balanced accuracy against EUCAST labels: **62.47%**
- balanced accuracy against CLSI labels: **56.41%**
- semantics-only delta: **-6.05 percentage points**

This independently demonstrates claim-level metric sensitivity to breakpoint semantics.

Integrity boundary: this is **not** a reproduction of the original 2019 Kover/RF model. The original
31-mer matrix and prediction vectors were not found in the public paper/repositories checked.

## Immediate next gate

Recover or reconstruct the original 2019 31-mer/Kover/RF prediction pipeline closely enough to
reproduce the paper-specific balanced-accuracy delta. Until that succeeds, the repository must keep
the original-model replay state as `NOT YET REPRODUCED`.
