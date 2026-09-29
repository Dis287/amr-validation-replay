# Experiment 001 — DSK/SEER feature-generation gate

**Superseded execution order:** `KMER_RECONSTRUCTION_GATE.md` is the active minimum gate. First complete the two-isolate shared-feature test with verified input accounting; only then begin the size-ranked resource panel below. This file retains the subsequent panel design, not an independent authorization to run it.

## Purpose

This gate decides whether the verified dataset-2 raw-read route can be carried forward
into a faithful Hicks-style 31-mer reconstruction without committing to the full
1,102-run download and assembly first.

It does **not** produce a model result or balanced accuracy.

## Primary-tool facts

Hicks describes 31-mers generated from assemblies with DSK and combined with SEER.
The original SEER `combineKmers` implementation:

- reads one DSK-derived k-mer text file per sample,
- stores the cross-sample union in an in-memory
  `unordered_map<string, vector<tuple<int,int>>>`,
- writes the combined output only after the union has been built,
- supports `--min_samples` to exclude k-mers seen in fewer than N samples.

Because Hicks removed k-mers present in only one genome, the pilot must use:

`--min_samples 2`

DSK canonicalizes reverse-complement pairs. The earlier direct Python forward-31-mer
count in `RAW_READ_PILOT.md` is therefore a sizing observation only and must not be
treated as the DSK feature count.

## Gate A — reproduce the one-isolate DSK stage

Input:
- checksum-verified `ERR1067709` reads,
- the documented SPAdes 4.3.0 pilot procedure and contig filter; the assembly FASTA was not committed and must be re-staged.

Run DSK at k=31 on the filtered assembly and record:

- DSK commit/release or binary checksum,
- exact command,
- input FASTA SHA-256,
- wall time,
- peak RSS,
- peak temporary disk,
- final HDF5 size,
- `dsk2ascii` output size,
- canonical 31-mer count,
- abundance distribution summary.

Do not compare the canonical DSK count numerically to the earlier forward-only Python
count as if they should be equal.

## Gate B — measure biological/input-size variation (only after the two-isolate combine check)

Do not extrapolate from one isolate.

Select a small deterministic panel from `ena_dataset2_manifest.tsv` spanning the
compressed-read-size distribution. Use size-ranked quantiles, not hand-picked runs.

Recommended first panel: 8 isolates nearest these ranks:

- minimum
- 10th percentile
- 25th percentile
- median
- 75th percentile
- 90th percentile
- 99th percentile
- maximum

For each isolate:

1. checksum-verify the paired FASTQs,
2. run the same declared SPAdes procedure,
3. apply the same documented contig filter,
4. run DSK k=31,
5. convert with `dsk2ascii`,
6. record the same resource and feature-count metrics.

The panel is for resource variation only. It does not authorize changing the Hicks
evaluation cohort or model design.

## Gate C — test SEER union growth before full reconstruction

Create deterministic nested subsets of the completed panel:

- 2 isolates
- 4 isolates
- 8 isolates

For each subset run the historical SEER `combineKmers` path with:

`combineKmers -r samples.tsv -o all_kmers --min_samples 2`

The original SEER source's no-argument help prints `-s`, but its actual parser accepts `-r` / `--samples`. It silently reduces an invalid minimum above the sample-list length to one, and skips missing k-mer files while continuing. Validate distinct names and files, row uniqueness, read completion, and independent shared-set equality as specified in the active gate.

Record:

- SEER commit/release or binary checksum,
- exact subset membership,
- wall time,
- peak RSS,
- output gzip size,
- number of emitted k-mers,
- process exit status.

The key quantity is **union-memory growth**, because `combineKmers` holds the union
in memory. Do not infer full-cohort feasibility from output-file size alone.

## Decision rule for 1,102-run reconstruction

AUTHORIZE a larger staged reconstruction only if the measured DSK and `combineKmers`
resource curves leave a clear safety margin on the intended compute environment.

Do **not** authorize the full 1,102-run run merely because:
- one SPAdes assembly succeeded,
- DSK succeeds on one isolate,
- or the 8-isolate combined output is small.

If union-memory growth becomes the binding limit, record:

`CURRENT_WORKSPACE_FEATURE_COMBINE_INFEASIBLE`

This is an infrastructure result, not a scientific kill. The next choice would be
either:
1. move the same historical toolchain to a larger compute environment, or
2. implement an externally sorted/streaming union that is demonstrably output-equivalent.

Option 2 is a method deviation and must be validated against historical
`combineKmers` on the pilot before it can support a reconstruction claim.

## Evidence boundary

Until this gate passes:

- Hicks SCM/RF metric replay = **UNVERIFIED**
- dataset-2 method reconstruction feasibility = **UNVERIFIED**
- one-isolate assembly feasibility = **VERIFIED**
- dataset-2 raw-read provenance = **VERIFIED**

## Next commit condition

Commit only measured outputs from the active two-isolate gate and, after it passes, Gates B-C and the resulting feasibility decision.
Do not add model code, dashboards, or architecture before this gate resolves.
