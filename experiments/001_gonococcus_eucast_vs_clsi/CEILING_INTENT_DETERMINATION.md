# SPAdes 2,700-second ceiling intent determination

Status: **UNKNOWN** (2026-09-30).

This determination is limited to committed repository evidence through
`9627020e44157c717b4fad2589ed47830958efd0`. It does not alter the terminal
n=8 failure, authorize a rerun, or authorize corrected-SEER n=8, the 1,102-run
reconstruction, or model training.

## Question

Was the SPAdes 2,700-second ceiling a scientific/resource-feasibility
acceptance threshold or an operational safety bound?

Allowed classifications:

- `VERIFIED_FEASIBILITY_THRESHOLD`
- `VERIFIED_SAFETY_BOUND`
- `UNKNOWN`

## Repository evidence

1. In the commit immediately before the first resource-panel checkpoint,
   `265b1f8ac9c232a9daac999c6e73bbea5651f4de`,
   `FEATURE_GENERATION_GATE.md` requires measured resource curves and a clear
   safety margin before larger-scale authorization, but it does not specify a
   2,700-second SPAdes limit or define a timeout as either a feasibility
   threshold or a containment-only bound.
2. The first relevant committed occurrence of `2700` is
   `e6628e6f82787afd2d34d7d5a092ca933eb376ef`. That single commit adds all of:
   `bounded_stage.py`, `RESOURCE_PANEL_CHECKPOINT.md`, and the already measured
   `resource_panel_n2.json`. The checkpoint calls 2,700 seconds a
   "predeclared ceiling," while the runner enforces termination and the JSON
   records it. No rationale for selecting 2,700 seconds and no statement
   distinguishing feasibility acceptance from operational containment is
   present. Because the number first becomes durable in the same commit as the
   n=2 results, the repository does not independently verify an earlier frozen
   rationale for that value.
3. `641b66604c5a484c2e9a20300a192b9068bfd74c` preserves the same ceiling in the
   n=4 checkpoint and authorizes only the fixed n=8 panel next. It establishes
   protocol continuity, not the ceiling's original intent.
4. `28b3595a3eaf13388081d00dcd62fcebd023a8ac` hard-codes `--timeout 2700` in
   `run_resource_panel_isolate.py`. It specifies enforcement, not rationale.
5. `4a6e83c89a40ddb6dc82dbcaf9cea226549c1db3` names the workflow a bounded n=8
   resource gate, sets a separate 75-minute GitHub Actions job timeout, and
   invokes the unchanged per-isolate runner. It does not classify the
   2,700-second stage ceiling as feasibility or safety.
6. `9627020e44157c717b4fad2589ed47830958efd0` correctly records the n=8 gate as
   failed when `ERR223688` exceeded the enforced ceiling. That establishes the
   outcome under the declared protocol; it does not establish the ceiling's
   design intent.

The history query used for the provenance check was:

```text
git log --reverse -S'2700' -- . \
  ':(exclude)experiments/001_gonococcus_eucast_vs_clsi/ena_dataset2_manifest.tsv'
```

The relevant first result is `e6628e6f82787afd2d34d7d5a092ca933eb376ef`.

## Classification

`UNKNOWN`

The committed evidence proves that 2,700 seconds was a fixed, enforced gate
condition. It does not prove that the value encoded a resource-feasibility
acceptance threshold, and it does not prove that it was only an operational
safety bound. Terms such as "resource gate," "predeclared ceiling," and
"bounded" are compatible with both interpretations and therefore cannot
resolve the classification.

## Consequence

- The original n=8 run remains **FAILED / UNVERIFIED**.
- The seven verified isolates remain valid partial evidence; seven of eight is
  not a pass.
- `ERR223688` must not be rerun by increasing the old ceiling.
- No replacement max-isolate experiment is authorized by this determination.
- Before any rerun, a separately named protocol must be explicitly frozen in a
  future commit with a prospective bound, an evidence-based rationale, a
  declared pass/fail rule, durable failure-artifact retention, and the unchanged
  scientific inputs and methods required by the governing state.
- Corrected-SEER n=8, full-cohort reconstruction, and model training remain
  unauthorized.
