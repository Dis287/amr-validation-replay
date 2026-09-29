# Experiment 001: two-isolate 31-mer toolchain result

**Gate outcome: FAIL for SEER 1.1.3 output integrity; DSK count checks PASS.** Measured 2026-09-29. This is a bounded toolchain result, not a Hicks model reproduction or a whole-cohort resource estimate.

## Inputs, versions, and methods

The two distinct Hicks S7 dataset-2 runs were `ERR1067709` (AZM MIC 0.5) and `ERR1082197` (AZM MIC 2). The second was selected deterministically as the other manifest run whose total reported compressed FASTQ size is closest to the first (171,996,072 vs 171,697,594 bytes); similar read size is not evidence of genomic representativeness.

All four paired FASTQ byte sizes and MD5 hashes matched `ena_dataset2_manifest.tsv`:

| Run | Mate 1 bytes / MD5 | Mate 2 bytes / MD5 |
| --- | --- | --- |
| ERR1067709 | 86,006,426 / `24813e50f500f8559f2993f842596d39` | 85,691,168 / `0c5fdb42e078bfe6bdc0729b85e9570e` |
| ERR1082197 | 87,249,304 / `e4eafb3156061b30153e264cf9c1f9b5` | 84,746,768 / `31d64f7646f687c8de455824349f66c4` |

Tool binaries: official SPAdes 4.3.0 Linux release archive SHA-256 `e88a8c533c8614dd4b7c5788cfcd46427848a0575267f97c690a75fd2a343034`; GATB DSK 2.3.3 Linux release archive SHA-256 `626a4663f70323a80834c013f1d9dcb4a3b3a73a1c9ab5da95a013783d81b0f6`; original SEER 1.1.3 `static_all` release archive SHA-256 `a69e5384e4c9ceea0fae321cc348e5dfa41271bbc8e440a35c6f8d4ee6a7c2ef` and `combineKmers` binary SHA-256 `d95eea12c0a0168ce34739ad553d0ac98902d9b6e0b5d8f42f603d27284532b7`. Hicks's exact versions are **unknown**. Both assemblies used `spades.py -1 MATE1 -2 MATE2 -o OUT -t 2 -m 8` with default mode and read correction. Contigs were retained when length >=200 bp and SPAdes header `_cov_` >=10. This is a declared approximation of the paper's coverage criterion; dataset-wide N50 filtering remains untested.

## Measured results

| Measure | ERR1067709 | ERR1082197 |
| --- | ---: | ---: |
| SPAdes exit | 0 | 0 |
| SPAdes wall seconds | 953.10 | 817.15 |
| SPAdes child peak RSS KiB | 1,398,088 | 1,223,628 |
| Raw contigs / bases / N50 bp | 395 / 2,142,914 / 60,512 | 569 / 2,060,976 / 7,802 |
| Filtered contigs / bases | 135 / 2,118,820 | 85 / 976,099 |
| Filtered FASTA SHA-256 | `1633a9805d50c50c66ebedd507e466b5bab267b19d18003deb9b9bedb39e9159` | `2f5903acebb6a4f6e1a976391ca00f8964e695f1d03bcc646472f857bd608df4` |
| DSK distinct canonical 31-mers | 2,089,781 | 962,089 |
| DSK wall seconds | 0.465 | 0.240 |
| DSK child peak RSS KiB | 70,224 | 63,344 |
| HDF5 / ASCII bytes | 35,916,864 / 71,052,828 | 17,881,888 / 32,711,118 |
| Sampled peak DSK temporary bytes | 2,061,386 | 950,616 |

The first assembly's `contigs.fasta` SHA-256 is `abcec97b2e7b47dc39614fcd6b5ea6a2f364f86a46c64bc38bfc42e8e7ee8c5b`, **identical** to the earlier one-isolate pilot. The second is `2e83e87ff7fe257ee7f3ea0d0d05a5ad8604033a4e89f96db24affc7f9ea4159`. The second's low raw N50 and large drop under coverage filtering require dataset-wide QC review; this pair is a toolchain check, not a declaration that both isolates would pass Hicks's cohort filter.

DSK commands were `dsk -file FILTERED.fa -kmer-size 31 -abundance-min 1 -nb-cores 2 -out-tmp TMP -out PREFIX` followed by `dsk2ascii -file PREFIX.h5 -out PREFIX.txt`. An independent canonical reverse-complement counter (using DSK's A<C<T<G orientation rule) matched every k-mer and abundance in **both** ASCII outputs: zero missing, extra, duplicate, or abundance-mismatch rows. The earlier 2,095,091 direct forward count for ERR1067709 was only a sizing observation and is not compared as if it should equal the canonical DSK count.

## SEER combine integrity failure

The two-line sample list used distinct run IDs and the two DSK ASCII files. SEER was called as `combineKmers -r two_samples.tsv -o two_combined --min_samples 2`. Its exit code was **0**, wall time **8.83 seconds**, child peak RSS **387,632 KiB**, and gzip output **9,267,638 bytes** (SHA-256 `3cbbddabb9d5dc13adfed7de6816306304b5b2dc18f839cb86fe2818abc224ac`).

The independent set intersection contained **875,897** canonical k-mers; SEER emitted **875,898** unique k-mer rows. Every genuinely shared k-mer was present, but:

- `GGGGCGTATTAGAACACATCGCGCCCGCCCC` appeared with `ERR1067709:1 ERR1067709:1` despite absence from ERR1082197: **one false shared feature**.
- `GGGTTGGCGGCAAATTGGACGACAATCCCCC` is shared but included `ERR1082197:1` twice: **one incorrect sample-tag/abundance row**.

Both input DSK ASCII files had zero duplicate k-mer rows. The behavior matches the tagged SEER 1.1.3 source's EOF loop defect documented in `KMER_RECONSTRUCTION_GATE.md`. The independent verifier `verify_two_isolate_features.py` exited **2** on these mismatches. This historical binary **fails** the active feature-integrity gate despite its successful exit. The two-isolate memory/timing values cannot be projected to 1,102 samples.

## Decision

Do **not** expand to the resource-variation panel or full cohort with this binary's output. The next bounded step is to test a source-identified corrected `combineKmers` implementation on the **same two DSK ASCII files**, compare its output exactly against the independent intersection and original output, record its version and any format change, and separately resolve dataset-wide N50 eligibility for the second isolate. Do not silently post-filter the defective output or claim exact Hicks feature equivalence. No model prediction or balanced accuracy was produced.

Temporary high-water disk was sampled every 0.2 seconds and may miss shorter peaks; peak RSS is the operating system's child-process maximum. The raw FASTQs and assembly files are transient and are not in GitHub; the input manifest, hashes, commands, result, and verifier are retained for re-execution.
