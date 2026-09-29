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

## Immediate next gate

Independently replay a model's predictions against both valid label semantics and compute the
metric delta. Until that rerun is completed, the repo must not claim independent reproduction
of the model-performance change.
