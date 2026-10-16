# CORRECTED_SEER_N8_COMBINE_V1

Status: **FROZEN_NOT_EXECUTED**

This is a separate prospective experiment. It is not a rerun or
reinterpretation of the failed original n=8 resource gate.

## Question

Can the source-identified corrected SEER `combineKmers` implementation at
commit `a6bd405754726467a93f39820fb4719457395ae7` produce the exact feature
matrix for the eight predeclared resource-panel isolates when every input and
output row is checked independently?

This experiment tests n=8 feature-combine correctness and bounded resource use
only. It does not test full-cohort feasibility or reproduce Hicks SCM/RF
balanced accuracy.

## Evidence classification before execution

### VERIFIED FACT

- Seven exact DSK ASCII inputs passed
  `N8_DSK_EXACT_INPUT_RECOVERY_V1` and survive in the read-back-verified
  release `experiment001-n8-exact-inputs-v1`.
- The maximum input from `MAX_ISOLATE_RESOURCE_RESOLUTION_V3` has 2,098,204
  rows, 71,339,203 bytes, and SHA-256
  `cc33735372a337f45c1cb07681739bb14adaf14ae4142fcad1e9326e3b42695b`.
  Those values were independently re-read from durable artifact
  `11950830857`.
- The complete eight-file input set has 16,731,962 rows and 568,888,831 bytes.
- Corrected SEER at `a6bd405…` passed exact two-isolate and n=4 checks.
- The n=4 combine completed in 16.724 seconds with sampled peak RSS 417,732
  KiB. Its four inputs differ from the newly frozen exact n=8 inputs, so this is
  not a linear runtime or memory predictor.
- Corrected-SEER n=8 has never run.

### INFERENCE

The eight-input combine is plausibly containable on a standard GitHub runner
because the input corpus is 568,888,831 bytes and prior smaller combines were
well below the retained 900-second ceiling. This is only an execution-envelope
rationale, not a predicted runtime or proof of scalability.

### UNKNOWN

- n=8 output feature count, compressed bytes, hash, runtime, and peak RSS.
- Whether the n=8 combine or independent oracle will finish inside the frozen
  envelope.
- Scaling behavior at 1,102 isolates.
- The exact SEER revision used by Hicks.
- Hicks feature matrix, model predictions, and replayed balanced accuracy.

## Exact inputs

Input order is scientific state and must not change.

| Rank | Sample | Rows | Bytes | SHA-256 | Verified source |
| --- | --- | ---: | ---: | --- | --- |
| min | `ERR1067833` | 2,103,513 | 71,519,738 | `1b60a3c86547f95055e3d51e138c6f7d6b2329967f3851ebe7112df309276a44` | release `experiment001-n8-exact-inputs-v1` |
| p10 | `ERR1067740` | 2,100,606 | 71,420,896 | `4ad0b03e3d184f5d694d43f5f43d7bfc7478eb655018e0bcefe58c6070f5eab2` | same release |
| p25 | `ERR1067765` | 2,101,892 | 71,464,617 | `9489718a0b3990b0c59146861148f9898a96128fce09202cb6fb5b1e12c687e3` | same release |
| median | `ERR855281` | 2,092,013 | 71,128,704 | `dee3cf91f0bba7fb5667a5818aa6992fe904209e26ddc73a77b8fc505f48355c` | same release |
| p75 | `ERR855022` | 2,045,008 | 69,530,491 | `518d08abb3127485e555e46c73dc71c16a14e218c267ea99d197d89bcca79a9b` | same release |
| p90 | `ERR854935` | 2,094,204 | 71,203,186 | `d6b821a29508df203a057620830004b3eab96eeea3b90ba495830fb2d1bd9175` | same release |
| p99 | `ERR223664` | 2,096,522 | 71,281,996 | `d3a57a04d3a3093e86e8af73dd966598112cde6790eceb166d547140886fdb0d` | same release |
| max | `ERR223688` | 2,098,204 | 71,339,203 | `cc33735372a337f45c1cb07681739bb14adaf14ae4142fcad1e9326e3b42695b` | V3 artifact `11950830857` or an exact verified copy |

No input may be regenerated or substituted inside this experiment. If an exact
input is unavailable, the experiment terminates `FAIL_INPUT_AVAILABILITY`.

## Tool identity

Use upstream SEER commit
`a6bd405754726467a93f39820fb4719457395ae7`.

Required source identities:

- source archive SHA-256:
  `e6ed83b2e60c1c45beeee24949203bd34e7dbc5107b77bc120d5afddff8e8e01`
- `src/combineKmers.cpp` Git blob:
  `54cb1acb01abf3285e6255f4e6f8480f2a27b4a3`
- `src/combineInit.cpp` Git blob:
  `8a0b168e51fa8f6994fc54035d4abd2b970effe7`
- `src/combineCmdLine.cpp` Git blob:
  `4cd634590631ff61096174d9c6eb45c1517f2af8`

Build without source edits:

```sh
g++ -O3 -std=c++11 -Isrc -o combineKmers-a6bd405 \
  src/combineInit.cpp src/combineCmdLine.cpp src/combineKmers.cpp \
  -lgzstream -lz -lboost_program_options
```

Record the runner image, compiler version, resolved library package versions,
binary byte count, and binary SHA-256. Source identities are acceptance
requirements; the compiled binary hash is measured evidence, not assumed equal
across runner images.

No historical SEER 1.1.3 binary and no other SEER revision are allowed.

## Frozen sample list

Create exactly 254 UTF-8 bytes with LF endings:

```text
ERR1067833	inputs/min/kmers.txt
ERR1067740	inputs/p10/kmers.txt
ERR1067765	inputs/p25/kmers.txt
ERR855281	inputs/median/kmers.txt
ERR855022	inputs/p75/kmers.txt
ERR854935	inputs/p90/kmers.txt
ERR223664	inputs/p99/kmers.txt
ERR223688	inputs/max/kmers.txt
```

Required SHA-256:
`2efa6bddf14a4f6b8e26fca0a3eb7d62d408d37c9d563393402d7270f38241d8`.

Before combine execution, verify:

- exactly eight nonempty rows;
- exactly eight distinct sample identifiers;
- exactly eight distinct paths;
- all files exist and are nonempty;
- every file matches its frozen rows, bytes, and SHA-256.

## Exact combine command

From the experiment working root:

```sh
tools/combineKmers-a6bd405 \
  -r inputs/n8_samples.tsv \
  -o work/combined/panel8_combined \
  --min_samples 2
```

There is no SEER model training in this experiment.

## Execution envelope

- runner: public standard `ubuntu-24.04` x64 only;
- no larger runner class;
- maximum runner allocation: 4 vCPU, 16 GiB RAM;
- combine is single-process; no unrecorded parallel invocation;
- minimum pre-acquisition free space: 12,884,901,888 bytes;
- complete working-root usage ceiling: 10,737,418,240 bytes;
- sampled process-tree RSS ceiling: 12,582,912 KiB;
- combine wall ceiling: 900 seconds;
- independent-oracle wall ceiling: 900 seconds;
- whole-job ceiling: 5,400 seconds;
- sample interval: 0.5 seconds;
- termination: SIGTERM, fixed 10-second grace, then SIGKILL.

The 900-second combine bound is retained from the pre-existing n=8 resource
protocol; it is a containment limit, not a runtime estimate. The memory and disk
limits prevent an uncontrolled run on the standard runner. They are not claims
of expected consumption.

Preflight records runner image/version, architecture, CPU model/count, total
RAM, filesystem free bytes, repository commit, protocol hashes, input-source
identities, and all tool/source hashes. A preflight violation stops before
combine execution.

## Independent oracle

The oracle must not reuse SEER code. It must use a bounded external-sort and
k-way-merge procedure rather than assuming the DSK files are ordered or loading
all 16,731,962 rows into memory.

For each input it must independently validate:

- exactly two whitespace-delimited fields per row;
- a 31-character uppercase A/C/G/T k-mer;
- a positive integer abundance;
- exact physical row count;
- zero duplicate k-mer rows;
- exact file byte count and SHA-256.

The oracle constructs the expected mapping for every k-mer present in at least
two distinct samples. Each expected tag is exactly
`sample_identifier:abundance`.

It independently parses the gzip output and requires:

- malformed rows = 0;
- missing expected features = 0;
- extra or below-minimum features = 0;
- duplicate output rows = 0;
- duplicate sample tags = 0;
- unknown sample tags = 0;
- missing sample tags = 0;
- abundance mismatches = 0;
- physical output rows = unique expected features;
- exact output byte count and SHA-256 recorded.

Successful process exit alone is never sufficient.

## Outcomes

Exactly one terminal state must be written:

- `PASS`
- `FAIL_PREFLIGHT_INFRASTRUCTURE`
- `FAIL_INPUT_AVAILABILITY`
- `FAIL_INPUT_INTEGRITY`
- `FAIL_TOOL_INTEGRITY`
- `FAIL_SAMPLE_LIST_INTEGRITY`
- `FAIL_COMBINE_TIMEOUT`
- `FAIL_MEMORY_ENVELOPE`
- `FAIL_STORAGE_ENVELOPE`
- `FAIL_COMBINE_NONZERO`
- `FAIL_COMBINE_OUTPUT`
- `FAIL_ORACLE_TIMEOUT`
- `FAIL_ORACLE_STAGE`
- `FAIL_FEATURE_EQUALITY`
- `FAIL_EVIDENCE_RETENTION`

Every terminal path writes `outcome.json` and attempts durable evidence
upload. No retry is allowed. No parameter, input, ceiling, sample name, order,
or command may change after dispatch.

## PASS rule

PASS requires all of the following to survive:

1. all eight exact input identities;
2. exact source identities and recorded build identity;
3. exact sample-list identity;
4. combine exit 0 inside every execution envelope;
5. completed gzip output;
6. all independent-oracle counters equal zero;
7. output rows equal independently expected features;
8. output hash, wall time, peak RSS, and peak working-root bytes saved;
9. complete logs, stage records, input/output manifests, and outcome saved;
10. independent post-run audit;
11. versioned release `experiment001-corrected-seer-n8-v1` containing the
    exact combined output, sample list, verification, manifests, logs, and
    outcome;
12. fresh release download with exact archive and member read-back;
13. final evidence-retention receipt survives.

Anything less is not PASS.

## Evidence retention

Actions artifacts use `if: always()` behavior and 90-day retention. The output
release must include all eight exact DSK input files, not only references to
their current sources. Their hashes, byte counts, row counts, and source
receipts must also survive. This prevents a repeat of the expired-artifact
input blockage.

Release asset name:
`experiment001-corrected-seer-n8-v1.tar.gz`.

The release archive must carry a recursive path/bytes/SHA-256 manifest and a
whole-archive byte count and SHA-256. A GitHub Actions artifact alone cannot
produce PASS.

## Authorization boundary

This protocol commit authorizes no execution. It authorizes only a separately
audited, manual-only execution harness in a later commit.

Even a future PASS would establish only corrected-SEER feature-combine
integrity at this exact n=8 panel. It would not:

- rewrite the original n=8 failure;
- establish 1,102-isolate feasibility;
- authorize full-cohort reconstruction;
- authorize Kover or ranger training;
- reproduce Hicks balanced accuracy;
- establish a final claim-state transition;
- establish commercial value or breakthrough status.

After a future independently audited PASS, the next decision would be a
separate full-cohort resource-feasibility assessment. No downstream execution
is authorized here.
