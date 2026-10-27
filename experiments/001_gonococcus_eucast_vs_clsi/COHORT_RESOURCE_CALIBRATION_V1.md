# COHORT_RESOURCE_CALIBRATION_V1

Status: **FROZEN / NOT EXECUTED**

Parent decision:
`RESOURCE_FEASIBILITY_DECISION_V1`, commit
`4b7b6aee3d511e29196a770047816acc207b99ed`.

## Purpose and boundary

This prospective experiment measures additional size-stratified assembly
variability and corrected-SEER growth at n=16 and n=32. It is not a full-cohort
run, model-training run, Hicks metric replay, or proof of historical assembly/QC
equivalence.

This protocol commit authorizes no execution. A dedicated manual-only harness
must be built, statically audited, committed, and independently read back first.

## Frozen selection

Source: the committed 1,102-row ENA manifest, SHA-256
`f15dfdcdf649e5e4a067e4bcdc1b643c1a124fcba7d6d24bfe135d992f58610f`.

Sort by total paired compressed FASTQ bytes ascending, then run accession
ascending. Begin with existing zero-based ranks
`[0,110,275,550,826,991,1090,1101]`. Repeatedly choose the floor midpoint of
the widest adjacent selected-rank interval; break width ties by lower left
endpoint. Add eight ranks for n=16, then 16 for n=32.

Frozen selection artifact:
`cohort_resource_calibration_v1_selection.json`, SHA-256
`415fa09449730b23d2308fdc7aefd630b66a69c6eeee9b61c39b70b2b2897497`.

Frozen selector:
`select_cohort_resource_calibration_v1.py`, SHA-256
`d30e0f427cf825d98da7465d0853338a4b9cbe985a37bbbe2b9ad8132df77308`.

### Existing eight

Ranks: `0, 110, 275, 550, 826, 991, 1090, 1101`.

Their exact DSK inputs must come only from release
`experiment001-n8-exact-inputs-v2`, asset ID `648632466`, 141,491,724
bytes, SHA-256
`4685554ea77eba521198ed73edff197fa65ac9b0967eb86b6842fff3188edef6`.

### Eight additions for n=16

| Rank | Accession | Paired compressed bytes |
|---:|---|---:|
| 192 | ERR1067714 | 192,433,539 |
| 343 | ERR855099 | 291,977,134 |
| 412 | ERR956692 | 306,364,180 |
| 481 | ERR855062 | 317,001,678 |
| 619 | ERR855434 | 331,155,367 |
| 688 | ERR854974 | 339,500,623 |
| 757 | ERR854902 | 346,556,867 |
| 908 | ERR222928 | 368,065,594 |

### Sixteen additions for n=32

| Rank | Accession | Paired compressed bytes |
|---:|---|---:|
| 27 | ERR1067726 | 163,161,957 |
| 55 | ERR1067829 | 169,066,122 |
| 82 | ERR1067842 | 173,316,253 |
| 151 | ERR1067772 | 183,297,025 |
| 233 | ERR1067840 | 205,723,156 |
| 309 | ERR855058 | 273,723,030 |
| 377 | ERR855195 | 300,596,194 |
| 446 | ERR855059 | 312,065,962 |
| 515 | ERR855120 | 321,089,919 |
| 584 | ERR854953 | 328,487,533 |
| 653 | ERR854907 | 335,622,622 |
| 722 | ERR854952 | 342,286,445 |
| 791 | ERR854898 | 349,072,632 |
| 867 | ERR855372 | 360,500,073 |
| 949 | ERR854879 | 377,522,853 |
| 1040 | ERR223657 | 437,831,522 |

The selection JSON freezes both FASTQ paths, byte counts, and MD5 values for
every record. Substitution is forbidden.

## Unchanged isolate pipeline

For each of the 24 additions:

1. Require exact FASTQ byte counts and MD5 values.
2. SPAdes 4.3.0, archive SHA-256
   `e88a8c533c8614dd4b7c5788cfcd46427848a0575267f97c690a75fd2a343034`;
   default paired mode, `-t 2 -m 8`.
3. Retain contigs with length >=200 and SPAdes header coverage >=10.
4. QUAST 5.2.0, archive SHA-256
   `ccd911087cfa254ad4b8eadac4f95d4685e44c3996f5516b8e0ce6f7cfa7e0db`;
   the existing frozen command.
5. DSK 2.3.3, archive SHA-256
   `626a4663f70323a80834c013f1d9dcb4a3b3a73a1c9ab5da95a013783d81b0f6`;
   k=31, abundance minimum=1, max memory=8000.
6. DSK2ASCII using the frozen command.
7. Independent A<C<T<G reverse-complement canonical oracle; require exact set
   and abundance equality and zero duplicate rows.

No scientific option may change after execution begins.

## Per-isolate envelope

- public standard `ubuntu-24.04` x64 only;
- at most 4 vCPU / 16 GiB RAM / 14 GB SSD per job;
- maximum four parallel isolate jobs;
- pre-download free disk >=12,884,901,888 bytes;
- SPAdes wall <=5,400 s;
- QUAST wall <=300 s;
- DSK wall <=900 s;
- DSK2ASCII wall <=300 s;
- isolate oracle wall <=900 s;
- whole isolate job <=9,000 s;
- sampled process-tree RSS <=10,485,760 KiB;
- watched SPAdes stage <=8,589,934,592 bytes;
- complete working root <=15,032,385,536 bytes;
- sample every 0.5 s;
- terminate with SIGTERM, fixed 10-second grace, then SIGKILL.

These bounds are inherited unchanged from the prospectively justified maximum
isolate protocol. They are containment limits, not predictions.

## Corrected-SEER checkpoints

Only after all constituent isolate inputs pass and survive durably:

- n=16 over the exact sorted n=16 rank set;
- n=32 over the exact sorted n=32 rank set.

Use corrected SEER commit
`a6bd405754726467a93f39820fb4719457395ae7`, source archive SHA-256
`e6ed83b2e60c1c45beeee24949203bd34e7dbc5107b77bc120d5afddff8e8e01`,
and `--min_samples 2`.

For each checkpoint:

- combine wall <=900 s;
- oracle wall <=900 s;
- RSS <=12,582,912 KiB;
- working root <=10,737,418,240 bytes;
- whole job <=5,400 s;
- independent external-sort/k-way-merge oracle;
- exact expected feature set;
- exact sample tags and abundances;
- every defect counter = 0;
- physical rows = expected features = unique output features.

A successful process exit is never sufficient.

## Failure and retry law

Each new isolate gets one attempt. No automatic, silent, matrix, or manual
second attempt exists inside this experiment. No parameter mutation is allowed.

Any preflight, input, tool, timeout, memory, storage, SPAdes, QC, DSK, combine,
oracle, equality, or evidence-retention failure is terminal and must retain an
explicit outcome plus all surviving evidence.

## Evidence retention

Every terminal path must attempt a 90-day `if: always()` artifact upload.
A PASS additionally requires an immutable release and fresh readback containing:

- the exact 32 DSK inputs and fixed sample lists;
- n=16 and n=32 combined outputs;
- all integrity/oracle/resource records;
- recursive path/bytes/SHA-256 manifests;
- source and artifact receipts.

Archive member paths must be unique. Recursive duplicate TAR insertion is
forbidden. Raw FASTQs need not be uploaded, but their observed byte counts and
MD5 values must survive.

## PASS

PASS requires all 24 new isolates, all 24 DSK oracles, the eight existing exact
inputs, corrected-SEER n=16 and n=32, both combine oracles, all resource records,
independent audit, immutable release, and fresh readback to pass exactly.

Anything less is FAIL.

Even PASS does not authorize the 1,102-isolate cohort or model training. It
returns to a new resource-feasibility decision.
