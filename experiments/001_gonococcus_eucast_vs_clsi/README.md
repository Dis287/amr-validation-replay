# Experiment 001 — Gonococcal AZM: EUCAST vs CLSI

## Objective

Independently reproduce the semantic label divergence reported by Hicks et al. 2019 before
attempting any model-metric replay.

## Public data source

CABBAGE processed table derived from the paper's S7 supplementary data:

`Leonardini/CABBAGE`
`SelectedTables/PMID_31479500_pcbi.1007349.s007_NGonorrhoeae_Processed.csv`

The original PLOS paper states that the relevant azithromycin non-susceptibility thresholds were:

- EUCAST: MIC > 0.25 µg/mL
- CLSI: MIC > 1.0 µg/mL

## Reproduced result

Using all 3,946 gonococcal rows with AZM MIC values:

- EUCAST NS: 1,827
- CLSI NS: 536
- labels concordant: 2,655
- labels discordant: 1,291
- concordance: 0.672832... (67.2833%)
- discordance: 0.327167... (32.7167%)

This independently reproduces the paper's statement that only ~67% of isolates were consistently
classified across the two breakpoint systems.

## Integrity boundary

The paper also reports a significant model-performance difference (balanced accuracy, P < 0.0001)
for AZM classifiers between EUCAST and CLSI.

**That metric delta has not yet been independently rerun here.**

Experiment 001 therefore has two states:

- `LABEL_DRIFT_REPRODUCED = YES`
- `MODEL_METRIC_REPLAY_REPRODUCED = NO`

The next action is to obtain/reconstruct model predictions or a reproducible model pipeline and
recompute the metrics under both label semantics.
