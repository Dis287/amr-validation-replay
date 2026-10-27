# RESOURCE_FEASIBILITY_DECISION_V1

Status: **FULL COHORT NOT AUTHORIZED**

Parent scientific result:
`CORRECTED_SEER_N8_COMBINE_V3` PASS, commit
`d4ae653e909c8e7bfbc047e598b4424e3a1f37ed`.

## Decision

The evidence is sufficient to authorize a bounded, prospective 32-isolate
calibration gate. It is not sufficient to authorize 1,102 assemblies,
corrected-SEER at n=1,102, or model training.

This is a feasibility decision, not an execution protocol. No biological
execution is authorized by this file.

## FACT

The committed ENA manifest contains exactly 1,102 paired runs totaling
344,835,597,770 compressed FASTQ bytes (321.153 GiB).

The eight predeclared input-size ranks produced the following durable SPAdes
measurements under version 4.3.0, default paired mode, `-t 2 -m 8`:

| Rank | Isolate | Input bytes | Wall s | Peak RSS KiB | Peak stage disk bytes |
|---|---|---:|---:|---:|---:|
| min | ERR1067833 | 70,656,305 | 299.528 | 1,279,840 | 581,808,411 |
| p10 | ERR1067740 | 177,141,208 | 653.872 | 1,523,880 | 1,431,877,181 |
| p25 | ERR1067765 | 226,917,919 | 1,074.414 | 1,762,324 | 1,836,688,542 |
| median | ERR855281 | 325,143,380 | 666.621 | 1,279,508 | 1,401,847,618 |
| p75 | ERR855022 | 355,223,967 | 847.386 | 1,279,612 | 1,516,533,857 |
| p90 | ERR854935 | 389,562,829 | 846.077 | 1,704,780 | 1,613,270,878 |
| p99 | ERR223664 | 771,033,917 | 2,365.749 | 2,097,024 | 2,429,652,499 |
| maximum | ERR223688 | 1,078,536,686 | 2,920.074 | 2,519,092 | 3,415,372,552 |

The maximum run's peak complete working root was 5,552,577,271 bytes. The eight
observed SPAdes walls sum to 9,673.721 seconds. The maximum input is 1.3988 times
the p99 input, while its wall time is 1.2343 times the p99 wall.

Input size does not monotonically order runtime: four of 28 ordered rank pairs
are inversions. The median runtime exceeds p75 and p90; p25 exceeds median,
p75, and p90. Therefore input size alone is not an observed deterministic
runtime function.

Seven regenerated isolates later reproduced every frozen filtered-FASTA and
DSK identity exactly. The p99 repeat took 2,472.237 seconds versus 2,365.749
seconds originally, a 106.488-second (4.50%) wall-time change despite exact
scientific output identity.

Corrected SEER at n=8 passed exactly:

- 2,210,121 expected, physical, and unique features;
- all mismatch counters zero;
- combine: 21.325 s, 583,528 KiB peak RSS, 1,309,767,078-byte peak root;
- oracle: 88.912 s, 502,216 KiB peak RSS, 2,865,103,878-byte peak root.

## INFERENCE — not an acceptance bound

Piecewise-linear interpolation across the eight size-rank anchors gives about
270 wall-hours, or 540 allocated two-core-hours, for 1,102 SPAdes runs.

This number is **illustrative only**. It is not an estimate suitable for
authorization because:

- only eight ranks were observed;
- 1,094 isolates remain unmeasured;
- runtime is non-monotonic in input size;
- run-to-run wall time varied even when scientific output reproduced exactly;
- no error-rate or tail-runtime distribution is established.

## UNKNOWN

The current evidence does not establish:

- an upper bound for total cohort compute;
- an upper bound for aggregate intermediate/final storage;
- failure frequency across the unsampled cohort;
- corrected-SEER memory, disk, runtime, or output size at n=1,102;
- whether n=1,102 combine fits a public standard runner;
- historical Hicks SPAdes/QUAST versions or cohort-QC equivalence;
- the Hicks feature matrix or SCM/RF metric replay.

The n=8 combined feature count plateau does not prove n=1,102 scalability.
Sample-tag payload and combine working state can grow even when unique 31-mer
count grows slowly.

## Next gate

Authorize protocol design only for
`COHORT_RESOURCE_CALIBRATION_V1`:

- total panel: 32 isolates;
- preserve and reuse the existing eight exact size-rank outputs;
- select 24 additional isolates deterministically from the frozen 1,102-row
  manifest before execution;
- freeze exact accessions, FASTQ bytes/MD5, selection algorithm, tool hashes,
  scientific commands, per-stage ceilings, and failure taxonomy;
- maximum four parallel isolate jobs;
- no retry or parameter mutation;
- retain per-isolate evidence durably;
- run corrected-SEER checkpoints at n=16 and n=32 only after their constituent
  isolates pass;
- require the independent exact oracle at both checkpoints.

Even a complete calibration PASS must return to a new feasibility decision. It
must not automatically launch the 1,102 cohort.

## Boundary

- Original n=8 resource gate: remains **FAILED**.
- Corrected-SEER n=8: **PASS**.
- Full 1,102 reconstruction: **NOT AUTHORIZED**.
- Model training: **NOT AUTHORIZED**.
- Hicks metric replay: **NOT ESTABLISHED**.
- Final claim-state transition: **NOT ESTABLISHED**.
- Breakthrough status: **NOT ESTABLISHED**.
