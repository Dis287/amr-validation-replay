# Zenodo assembly overlap: Hicks dataset 2

## Inputs inspected

1. Hicks et al. 2019 original S7 spreadsheet, DOI
   `10.1371/journal.pcbi.1007349.s007` (Run ID, dataset, AZM MIC).
2. Sanger Pathogens ARIBA training data, `Notebooks/ARIBA/data/mic_data.tsv`,
   commit `19186e1ffc7094a0903d18de380184f42494c116` (Run ID to GCGS name):
   https://github.com/sanger-pathogens/pathogen-informatics-training/blob/19186e1ffc7094a0903d18de380184f42494c116/Notebooks/ARIBA/data/mic_data.tsv
3. Grad's Zenodo record `10.5281/zenodo.2618836`, file
   `gcgs-contigs.tar.gz` (725,561,345 bytes, published MD5
   `fb93e97d22814f2dbe008dbeb2efd72c`):
   https://zenodo.org/records/2618836
4. The source cohort paper (Grad et al. 2016), PMID 27638945, methods:
   https://pmc.ncbi.nlm.nih.gov/articles/PMC5091375/

Run `python verify_zenodo_overlap.py S7.xlsx mic_data.tsv gcgs-contigs.tar.gz`
after downloading those inputs. The output and input hashes are preserved in
`zenodo_overlap.json`. The tarball was checked against Zenodo's published MD5.

## Verified overlap

- All **1,102** Hicks S7 isolates tagged dataset 2 (`926` dataset 2 only,
  `176` also tagged dataset 3) map one-to-one to the 1,102 `GCGS*.fa` members
  actually present in the archive. There are zero unmatched archive members
  and zero unmatched dataset-2 runs under the inspected mapping.
- S7 yields **910** EUCAST AZM non-susceptible (`MIC > 0.25`) and **295** CLSI
  non-susceptible (`MIC > 1`), matching the dataset-2 counts in the paper's
  S5 table.
- S5's dataset-2 published outer-test mean bACC: SCM **62.44% EUCAST** and
  **81.46% CLSI**; RF-C **65.16% EUCAST** and **82.34% CLSI**. These are
  reference values, **not** independently reproduced metrics.

## Critical equivalence boundary

The archive is from the 2016 source cohort, whose methods say its reads were
assembled with **Velvet 1.0.12 and VelvetOptimiser**. Hicks 2019 says it
assembled reads with **SPAdes**, then filtered contigs by length, coverage,
and assembly N50. Thus exact isolate overlap **does not establish feature
equivalence**: 31-mer matrices derived from the archived Velvet contigs may
differ from Hicks's SPAdes-derived matrices. The archive is a useful
reconstruction pilot or sensitivity comparator, but a faithful Hicks feature
reconstruction requires the SRA reads and the paper's assembly/filtering
procedure, unless an exact Hicks assembly or 31-mer matrix is recovered.

The accession mapping comes from a third-party training repository, not a
Hicks-provided prediction or fold artifact. It is corroborated by complete
one-to-one archive coverage and the S5 phenotype counts; its provenance is
still recorded explicitly.

## Next gate

Use dataset 2 as a bounded reconstruction target. Recover any Hicks-specific
SPAdes assemblies, 31-mer matrix, splits, or predictions first. Otherwise
obtain the 1,102 public raw read sets, recreate and record the SPAdes/DSK/SEER
feature pipeline, then use matched 10-repeat stratified outer partitions with
inner model selection. Score both paper-style separately trained classifiers
and a frozen-prediction semantic replay as distinct analyses. Do not call the
Velvet archive a faithful substitute or claim exact numerical reproduction
without the paper's original random partitions and software parameters.
