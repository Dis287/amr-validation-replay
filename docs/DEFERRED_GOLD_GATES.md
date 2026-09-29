# Deferred Gold Gates

Status: **preserved for later; not active execution scope**

This note preserves strategic conclusions that should govern the project **after**
Experiment 001 reaches its current scientific gates. It must not be used to skip,
replace, or widen the active Experiment 001 work.

## Three distinct targets

### Gold A — exact historical Hicks reproduction
Recover the original Hicks 2019 numerical result using the original partitions,
seeds, models, prediction vectors, feature matrix, and exact assembly/QC toolchain.

Current status: **unresolved / provenance incomplete**.

Do not call this impossible or NON_REPLAYABLE merely because artifacts have not yet
been recovered. If bounded recovery efforts fail, record the exact search boundary
and use a state such as `ORIGINAL_ARTIFACTS_NOT_RECOVERED`.

This is not the product thesis.

### Gold B — faithful scientific reconstruction
Construct a declared, version-pinned genomic validation pipeline close enough to the
documented Hicks method to test whether changing AMR phenotype semantics materially
changes a real genomic model-validation claim.

Historical fidelity and scientific replay validity are separate dimensions.

A reconstruction may fail to be bit-identical to Hicks yet still be a legitimate
scientific test of semantic revalidation, provided every deviation is explicit.

### Gold C — dependency-aware AMR claim revalidation instrument
Potential breakthrough target:

> Convert an AMR model-validation claim into an executable dependency contract;
> determine whether a changed scientific or computational dependency affects that
> claim; determine whether the claim is replayable; execute the permitted replay;
> and emit an auditable claim state with pinned evidence and provenance.

This is narrower than generic provenance, reproducibility, breakpoint relabeling,
continuous benchmarking, or claim graphs.

Gold C is **not yet proven**. It must earn that status by surviving Gold B and at
least one independent second AMR case.

## Deferred sequence

Only after the currently active Experiment 001 gates are resolved:

1. Bound original-artifact recovery. Do not hunt indefinitely and do not manufacture
   impossibility from non-recovery.
2. Freeze a reconstruction contract separating documented historical facts from
   declared reconstruction choices.
3. Resolve assembly/QC sufficiently to define the reconstruction cohort.
4. Complete deterministic correctness/resource scaling before authorizing a full
   cohort reconstruction.
5. Run a clean fixed-prediction semantic replay on a version-pinned genomic pipeline.
6. Produce first-class versioned artifacts:
   - Claim Manifest
   - Replayability Audit
   - Semantic Replay Result
7. Evaluate a **predeclared claim**. Do not define the claim state after seeing the
   metric.
8. Repeat the same dependency-change -> replayability -> replay -> claim-state sequence
   on one structurally independent AMR validation case.
9. Only then consider packaging the instrument:
   - pyproject / lockfile
   - license
   - CLI
   - CI
   - versioned JSON artifacts
   - tagged release

## Estimand discipline

Never merge:

1. **Paper-style reconstruction** — separately train models under EUCAST and CLSI
   using a declared Hicks-like evaluation procedure.
2. **Fixed-prediction semantic replay** — freeze one out-of-sample prediction vector
   and rescore it under two legitimate phenotype semantics.

A difference between reconstructed numbers and Hicks's published numbers is a
**reconstruction-fidelity result**.

A difference caused by changing a dependency within the same controlled validation
claim is a **claim-replay result**.

Do not label one as the other.

## Productization boundary

Software packaging does not make the project gold.

Do not broaden into dashboards, generic Scientific Claim CI, multiple organisms, or
a SaaS layer merely because the repository becomes installable.

The technical thesis still has to satisfy the existing kill gate:
- a legitimate semantic replay materially changes a real validation metric or conclusion,
- missing provenance fails closed,
- and existing AMR tooling does not already provide the same claim-level dependency
  tracking, replay and stale/revalidate decision with trivial glue.

## Current execution remains unchanged

Return to `PROJECT_STATE.md` for the authoritative active step.

This document is intentionally deferred. It exists so the strategic insight is not
lost when the project is ready for it.
