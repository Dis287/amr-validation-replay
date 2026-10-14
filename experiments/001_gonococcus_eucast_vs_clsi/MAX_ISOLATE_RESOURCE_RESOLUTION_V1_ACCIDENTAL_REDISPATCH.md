# MAX_ISOLATE_RESOURCE_RESOLUTION_V1 — accidental redispatch record

GitHub Actions run `38594673384` accidentally dispatched the already-terminal
V1 workflow a second time on 2026-10-14 from commit
`70aab41f28cc98cd8298db271ca2f697233b4d3c`.

This run is not a V1 retry result and does not alter the terminal V1 failure
record for run `38591577348`. The V1 single-attempt guard detected that prior
run and stopped at preflight. The retained preflight record lists both
`single_attempt_guard` and the already-known V1 `filesystem_total` violation.

Durable evidence establishes:

- workflow event: `workflow_dispatch`
- run number / attempt: `2 / 1`
- terminal workflow conclusion: `failure`
- scientific classification: `INFRASTRUCTURE_PREFLIGHT_FAILURE`
- prior run detected by guard: `38591577348`
- input-integrity stage: `NOT_REACHED`
- biological input list: empty
- scientific command ledger: empty
- SPAdes, QUAST, DSK, and independent oracle: not reached
- evidence upload: succeeded
- final-outcome upload: succeeded

Both downloaded artifact ZIP hashes matched the digests reported by GitHub.
The evidence archive contained an independently hashed internal TAR. Exact
identifiers and hashes are recorded in
`max_isolate_resource_resolution_v1_accidental_redispatch.json`.

No scientific conclusion follows from this dispatch. V1 remains terminal and
must not be dispatched again. V2 remains a distinct experiment and had zero
runs when this record was prepared.
