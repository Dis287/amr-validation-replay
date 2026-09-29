# Hicks 2019 model provenance and reconstruction boundary

## Source inspected

Hicks et al., *PLOS Computational Biology* (2019), DOI
`10.1371/journal.pcbi.1007349`, Materials and methods, “ML-based prediction of
resistance phenotypes,” and the article's Supporting information index.

https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1007349

## Published evaluation recipe

- Input genomes: SRA accessions and isolate MIC/method metadata are identified in
  Table 1 and S7. Reads were assembled with SPAdes; short/low-coverage contigs
  and low-N50 assemblies were filtered as described in the paper.
- Features: DSK 31-mers from assemblies, combined with SEER `combinekmers`;
  31-mers present in only one genome were removed, then counts were converted
  to binary presence/absence.
- SCM: Kover, at most five rules; five-fold cross-validation selected the
  conjunctive/disjunctive model and the listed trade-off parameter.
- RF: ranger, 1,000 trees; five-fold cross-validation selected tree depth and
  `mtry` from the paper's stated candidate values.
- **Outer evaluation:** each analysis used 10 random, distinct, stratified
  partitions. Two-thirds of isolates trained the model and the remaining
  third tested it. The paper reports mean balanced accuracy and 95% confidence
  intervals over these 10 repeats.
- Separate models were trained and tested for EUCAST and CLSI categories;
  four individual gonococcal datasets lacked enough CLSI AZM non-susceptible
  isolates and were assessed only under EUCAST for AZM.

Random seeds, exact outer test memberships, trained models, per-isolate
predictions, and the assembled 31-mer feature matrix were not identified in
the inspected main text or the descriptions of S1–S7. The supplemental files
themselves and other repositories still require inspection. Their availability
remains **UNKNOWN**, not disproved.

## Distinguish the two comparisons

1. **Paper-specific reproduction:** train separate EUCAST and CLSI models on
   matched outer partitions using the published feature and model procedures;
   compare their test balanced accuracies across the 10 repeats. Exact numeric
   equality with the paper cannot be promised without its seeds and folds.
2. **Fixed-prediction semantic replay:** freeze one model's out-of-sample
   predictions and score the same isolates under both phenotype definitions.
   This isolates the scoring-label effect, but is a distinct estimand from the
   paper's separately trained model comparison.

Experiment 001B performs the second comparison with a small mechanism-feature
classifier and a different five-fold outer evaluation. It is **not** the
published 31-mer/Kover/ranger model or a reproduction of the paper's reported
balanced-accuracy difference.

## Next evidence gate

Search for original prediction vectors, folds/seeds, assembled genomes, or
feature matrices linked to the DOI and authors. If none are recoverable,
reconstruct from public SRA reads with recorded software versions, isolate
filtering, 31-mer processing, nested tuning, matched outer partitions, and
per-isolate prediction files. Record all departures from the paper before
calling the result a reconstruction. Do not label the original result
`NON_REPLAYABLE` solely because a code search returns no hits.
