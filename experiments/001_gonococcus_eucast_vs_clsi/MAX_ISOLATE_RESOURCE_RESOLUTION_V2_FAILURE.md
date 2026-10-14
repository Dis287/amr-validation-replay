# MAX_ISOLATE_RESOURCE_RESOLUTION_V2 — terminal harness result

GitHub Actions run `38600205769` executed once from commit
`4bea3506388d5b48b579caf3aae7aed374420f69` and ended `FAIL_DSK_STAGE`.
Both artifact ZIP digests and the internal evidence TAR digest were independently
verified after download.

## What passed

- preflight and the V2 single-attempt guard
- exact input byte-size and MD5 checks for both `ERR223688` FASTQs
- SPAdes 4.3.0 with the frozen `-t 2 -m 8` command
- the frozen contig filter
- QUAST 5.2.0
- durable upload of the evidence and final-outcome artifacts

SPAdes exited zero in 2,934.196472 seconds, inside the frozen 5,400-second
ceiling. Peak process-tree RSS was 2,517,740 KiB, peak watched SPAdes output was
3,413,998,978 bytes, and peak complete working-root size was 5,551,425,952
bytes. There was no recorded OOM, filesystem exhaustion, timeout, or envelope
termination. The filtered assembly retained 163 of 431 contigs and QUAST
reported filtered N50 = 40,334 bp.

## Exact failure

DSK exited `1` after 0.534487 seconds. Its retained log states that it could not
open a path beneath the declared `dsk_tmp` directory because that directory did
not exist. The V2 harness passed `-out-tmp .../dsk_tmp` but did not create the
directory before invoking DSK. The earlier resource-panel runner explicitly
created its DSK temporary directory before the same command shape.

This is a harness-preparation defect. It is not evidence of DSK computational
failure, biological/QC failure, OOM, disk exhaustion, or timeout.

The surviving `kmers.h5` is not accepted as scientific output: DSK exited
nonzero, no DSK ASCII output exists, and the independent oracle did not run.

V2 remains terminal and must not be rerun or reclassified. The original n=8
gate remains failed. Corrected-SEER n=8, the 1,102-run reconstruction, and model
training remain unauthorized.

Exact run, artifact, stage, and hash evidence is recorded in
`max_isolate_resource_resolution_v2_failure.json`.
