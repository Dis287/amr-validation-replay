# 31-mer reconstruction gate: method check before scaling

Status: **source-verified method correction; DSK/SEER execution pending** (2026-09-29). This note records a decision boundary, not a new model result.

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

## Execution boundary observed here

The previous pilot's FASTQs and SPAdes contigs were in transient `/tmp/hicks_pilot`; they are no longer present in this execution workspace. The current repo contains the manifest and measurements, not sequence data or assembled contigs. DSK and SEER executables are not installed here. An attempted 15-second HTTPS HEAD request for the ENA pilot read did not complete before timeout; this does not establish that the public read is unavailable.

## Decision and next bounded experiment

**Do not authorize the 1,102-run reconstruction yet.** Re-stage the checksum-verified `ERR1067709` reads/contigs and a second distinct dataset-2 isolate. Preserve both read hashes, assembly commands, versions, filtered contig hashes and QC. Run DSK 31-mer counting (`-abundance-min 1`) for each, compare canonicalized output with an independent reverse-complement-aware count, then run original SEER `combineKmers -r sample_list.txt -o combined --min_samples 2` on the pair. Validate two unique sample identifiers, exactly two opened nonempty ASCII inputs, no duplicate rows, expected shared-set equality, binary presence for both, and record warnings plus exit status. Measure wall time, peak RSS, temporary/final disk, per-isolate distinct canonical 31-mers, shared features, and a two-column binary-presence check. Only after that sample several input-size strata and assess whole-cohort memory, storage, time, and software compatibility.

The exact Hicks SPAdes/DSK/SEER versions, original assembly files, outer partitions and per-isolate predictions remain unverified. A successful two-isolate gate would establish toolchain behavior, not a Hicks metric replay.
