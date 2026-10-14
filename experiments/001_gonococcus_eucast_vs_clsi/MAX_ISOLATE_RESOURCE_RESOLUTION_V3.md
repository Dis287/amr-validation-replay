# MAX_ISOLATE_RESOURCE_RESOLUTION_V3

Status: `FROZEN_NOT_EXECUTED`

V3 is a separately named prospective experiment. It is not a rerun or
reinterpretation of V2. V2 remains the terminal `FAIL_DSK_STAGE` harness result
recorded for GitHub Actions run `38600205769`.

## Purpose

Determine whether `ERR223688` can complete the unchanged scientific pipeline
inside the same predeclared resource limits after correcting the demonstrated
V2 DSK temporary-directory preparation defect.

## Inherited scientific and resource protocol

Every target, input identity/hash, scientific tool version, scientific command,
filtering rule, resource ceiling, sampling interval, termination rule, evidence
requirement, and downstream authorization boundary is unchanged from V2 and its
inherited V1 scientific protocol.

Specifically unchanged: `ERR223688`; both ENA file names, byte counts and MD5s;
SPAdes 4.3.0 default paired mode with `-t 2 -m 8`; length >=200 and header
coverage >=10 filtering; QUAST 5.2.0; DSK 2.3.3 with k=31, abundance-min=1 and
max-memory=8000; A<C<T<G reverse-complement canonical oracle; 5,400-second
SPAdes ceiling; 10 GiB sampled RSS ceiling; 8 GiB watched SPAdes-output ceiling;
14 GiB complete working-root ceiling; 0.5-second sampling; 9,000-second whole-job
ceiling; SIGTERM, ten-second grace and SIGKILL; no SEER.

## Sole correction

Before DSK is invoked, V3 must create exactly the already-declared
`work/dsk_tmp` directory. The DSK command and its `-out-tmp` value remain
unchanged. No other scientific or resource parameter changes.

## Attempt and retention law

V3 permits exactly one manual `workflow_dispatch` attempt from its frozen
workflow. No automatic retry, rerun, matrix, hidden fallback, reuse of the
failed V2 HDF5, or parameter mutation is allowed. Every terminal path must
attempt 30-day durable upload of the complete evidence bundle and final outcome.

V3 passes only if every inherited end-to-end pass condition survives and an
independent audit accepts the artifacts. Otherwise it produces an explicit
saved failure. A V3 pass would not change the failed n=8, V1, or V2 records and
would authorize only freezing a separate corrected-SEER n=8 combine protocol.
