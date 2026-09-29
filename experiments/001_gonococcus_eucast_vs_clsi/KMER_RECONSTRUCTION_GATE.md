# 31-mer reconstruction gate: method check before scaling

Status: **two-isolate DSK counts and corrected SEER combine passed exact independent checks** (2026-09-29). The original SEER 1.1.3 binary failed; see `TWO_ISOLATE_GATE_RESULT.md` and `CORRECTED_SEER_RETEST.md`. This gate note records the method boundary, not a model result.

## Primary evidence inspected

- Hicks et al. 2019, Materials and methods, "Isolate selection and dataset preparation" and "ML-based prediction of resistance phenotypes": https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1007349
- DSK authors' README, input, dsk2ascii, reverse-complement canonicalization, and disk guidance: https://github.com/GATB/dsk
- Original SEER authors' usage wiki, "dsk" subsection: https://github.com/johnlees/seer/wiki/Usage
- Original SEER implementation at commit `5a9db20e113e649021bd79e52ccf55728f76b301`: [`combineCmdLine.cpp`](https://github.com/johnlees/seer/blob/5a9db20e113e649021bd79e52ccf55728f76b301/src/combineCmdLine.cpp), [`combineInit.cpp`](https://github.com/johnlees/seer/blob/5a9db20e113e649021bd79e52ccf55728f76b301/src/combineInit.cpp), [`combineKmers.cpp`](https://github.com/johnlees/seer/blob/5a9db20e113e649021bd79e52ccf55728f76b301/src/combineKmers.cpp)
- pyseer authors' usage, which explicitly requires original SEER `combineKmers` when using DSK: https://github.com/mgalardini/pyseer/blob/master/docs/usage.rst

## Verified method and consequences

1. Hicks assembled reads with default SPAdes, removed contigs below 200 bp or 10x coverage, and excluded assemblies with N50 below two dataset standard deviations. It counted assembled 31-mers with DSK, combined profiles with SEER `combinekmers`, removed 31-mers present in only one **genome**, then binarized the resulting per-isolate matrix.
2. DSK canonicalizes reverse complements. Its README specifies the ordering `A<C<T<G` for selecting the representative; plain Python forward-strand distinct 31-mers in `RAW_READ_PILOT.md` are therefore **not** a DSK output count or matrix-size estimate.
3. The SEER authors' documented route is `dsk -file sample_contigs.fa -abundance-min 1 -out sample_dsk`, `dsk2ascii -file sample_dsk.h5 -out sample_dsk.txt`, and `combineKmers -r sample_list.txt -o combined --min_samples 2`. Supply `-kmer-size 31` to DSK to match Hicks. Inspection of original SEER source at commit `5a9db20e113e649021bd79e52ccf55728f76b301` resolves the list format: whitespace-delimited `sample_name path_to_dsk_ascii`, one distinct sample per line. Its no-argument usage string incorrectly says `-s`; the actual option parser defines `--samples` / `-r`. Use `-r`, then verify the installed binary's `--help` and version/checksum.
4. A critical implementation trap: `checkMin` silently resets a requested minimum greater than the list length to **1**. With a single isolate, `--min_samples 2` therefore does not enforce the paper's singleton-across-genomes removal. The implementation counts the length of each k-mer's sample-index vector, so duplicate list entries or duplicate k-mer rows could also falsely satisfy the minimum. Missing k-mer input files are logged and skipped, yet processing continues. The pilot must reject duplicate sample names/paths and per-file duplicate k-mers, check every input exists and is read, and independently compare the emitted shared set and per-isolate presence to a set intersection.

With a single isolate, a feature cannot satisfy a genuine `--min_samples 2` criterion across genomes. Thus the existing one-isolate assembly can test DSK counting but **cannot** test the nonempty shared-feature matrix or the combined memory footprint. The minimum scientifically useful combine pilot needs at least two distinct Hicks dataset-2 isolates.
5. SEER's wiki gives an example of approximately 25 GB RAM and 90 minutes to combine 21-mers for 3,000 samples. This is **an example for a different k and cohort**, not a projection for 1,102 gonococcal 31-mer profiles. It is enough to reject an unsupported assumption that the combine stage fits this workspace's approximately 9.7 GiB RAM. DSK also advises several times the input size in free temporary disk.

## Version-specific SEER failure discovered before biological combine

A synthetic two-file sanity fixture was run with the official SEER `v1.1.3_static_all` release binary (SHA-256 `d95eea12c0a0168ce34739ad553d0ac98902d9b6e0b5d8f42f603d27284532b7`). File A contained `AAAA 1`, `CCCC 2`; file B contained `AAAA 3`, `GGGG 4`. The command `combineKmers -r list.txt -o out --min_samples 2` exited successfully yet emitted `CCCC a:2 a:2` and `GGGG b:4 b:4` alongside the true shared `AAAA`. These singleton rows are **synthetic tool-check output, not biological evidence**.

The tagged `v1.1.3` and `v1.1.4` source reads `while (kmer_counts)` and pushes the old `kmer, abundance` even after extraction fails at EOF. It therefore duplicates each input's last row; the filter counts vector length rather than distinct sample IDs. The inspected later master source changes the loop to `while (kmer_counts >> kmer >> abundance)`, but its version and output format differ, and Hicks's exact SEER version is unknown. Sources: [v1.1.3 implementation](https://github.com/johnlees/seer/blob/v1.1.3/src/combineKmers.cpp) and [later corrected source](https://github.com/johnlees/seer/blob/5a9db20e113e649021bd79e52ccf55728f76b301/src/combineKmers.cpp).

**Gate implication:** an older SEER binary can produce a false shared feature even with two valid distinct files. The real-data pilot must compare emitted feature/sample pairs against an independently derived intersection and **fail** on any singleton, duplicate sample tag, or count mismatch. Do not silently drop offending output and call the historical command faithful; record the binary/version defect and decide a documented correction or software version before scaling.

## Execution boundary observed here

At the time this gate was designed, the prior `/tmp/hicks_pilot` files had been lost across workspaces. The two read pairs were subsequently re-staged and checksum-verified; their assemblies and DSK/SEER outputs remain transient workspace files, not committed sequence data. The repo preserves input hashes, commands, verifier, and measured results in `TWO_ISOLATE_GATE_RESULT.md` and `CORRECTED_SEER_RETEST.md`. The earlier short ENA request timeout did not mean the reads were unavailable.

## Decision and next bounded experiment

**Do not authorize the 1,102-run reconstruction yet.** The now-completed bounded execution was to re-stage the checksum-verified `ERR1067709` reads/contigs and a second distinct dataset-2 isolate. Preserve both read hashes, assembly commands, versions, filtered contig hashes and QC. Run DSK 31-mer counting (`-abundance-min 1`) for each, compare canonicalized output with an independent reverse-complement-aware count, then run original SEER `combineKmers -r sample_list.txt -o combined --min_samples 2` on the pair. Validate two unique sample identifiers, exactly two opened nonempty ASCII inputs, no duplicate rows, expected shared-set equality, binary presence for both, and record warnings plus exit status. Measure wall time, peak RSS, temporary/final disk, per-isolate distinct canonical 31-mers, shared features, and a two-column binary-presence check. Only after that sample several input-size strata and assess whole-cohort memory, storage, time, and software compatibility.

The exact Hicks SPAdes/DSK/SEER versions, original assembly files, outer partitions and per-isolate predictions remain unverified. The successful corrected two-isolate gate establishes toolchain behavior, not a Hicks metric replay.
