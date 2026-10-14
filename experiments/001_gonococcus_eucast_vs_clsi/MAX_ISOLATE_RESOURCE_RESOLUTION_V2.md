# MAX_ISOLATE_RESOURCE_RESOLUTION_V2

Status: `FROZEN_NOT_EXECUTED`

V2 is a separately named prospective experiment. It is not a rerun or
reinterpretation of V1. V1 remains the terminal infrastructure failure recorded
for GitHub Actions run `38591577348`.

## Purpose

Determine whether `ERR223688` can complete the unchanged scientific pipeline
inside the same predeclared resource limits after correcting one infrastructural
preflight error.

## Inherited scientific protocol

Every scientific identity, version, input hash, command, filtering rule,
wall-time limit, RSS limit, SPAdes-stage disk limit, evidence requirement and
downstream authorization boundary is inherited byte-for-byte in meaning from:

- `MAX_ISOLATE_RESOURCE_RESOLUTION_V1.md`
- `max_isolate_resource_resolution_v1.json`

Specifically unchanged: `ERR223688`; both ENA file names, byte counts and MD5s;
SPAdes 4.3.0 default paired mode with `-t 2 -m 8`; length >=200 and header
coverage >=10 filtering; QUAST 5.2.0; DSK 2.3.3 with k=31, abundance-min=1 and
max-memory=8000; A<C<T<G reverse-complement canonical oracle; 5,400-second
SPAdes ceiling; 10 GiB sampled RSS ceiling; 8 GiB watched SPAdes-stage ceiling;
0.5-second sampling; SIGTERM, ten-second grace and SIGKILL; no SEER.

## Sole correction

V1 treated the mounted filesystem's total backing capacity as experiment usage
and rejected the requested standard `ubuntu-24.04` runner when that capacity was
greater than 14 GiB. V2 does not use total mounted capacity as a rejection
criterion. It still records total and free bytes.

V2 enforces storage prospectively as follows:

1. workflow runner label remains exactly public standard `ubuntu-24.04`;
2. architecture must be x64, CPU count <=4 and total RAM <=16 GiB;
3. free disk before biological input download must be >=12,884,901,888 bytes;
4. the complete experiment working root is sampled and capped at
   15,032,385,536 bytes (14 GiB);
5. the SPAdes output directory remains independently sampled and capped at
   8,589,934,592 bytes (8 GiB);
6. any working-root cap breach or filesystem exhaustion is
   `FAIL_STORAGE_ENVELOPE`.

This correction limits what the experiment consumes; it does not reject an
otherwise allowed standard runner because its backing filesystem reports extra
capacity.

## Attempt and retention law

V2 permits exactly one manual `workflow_dispatch` attempt from its frozen
workflow. No automatic retry, rerun, matrix, hidden fallback or parameter
mutation is allowed. Every terminal path must attempt 30-day durable upload of
the same evidence classes required by V1.

V2 passes only if the complete inherited V1 pass conditions survive and an
independent audit accepts the artifacts. Otherwise it produces an explicit
saved failure. A V2 pass would not change the failed n=8 or V1 records and would
authorize only a separately frozen corrected-SEER n=8 combine protocol.
