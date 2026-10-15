# MAX_ISOLATE_RESOURCE_RESOLUTION_V3 result

Status: `PASS_INDEPENDENTLY_AUDITED`

## Identity

- Experiment: `MAX_ISOLATE_RESOURCE_RESOLUTION_V3`
- GitHub Actions run: `38680749205`
- Run number / attempt: `1 / 1`
- Trigger: manual `workflow_dispatch`
- Frozen head: `0cd6f51e6fa567b9cb00c05f8a6b5a8d048b76cd`
- Started: `2026-10-15T04:18:09Z`
- Completed: `2026-10-15T05:21:56Z`
- GitHub conclusion: `success`

The GitHub conclusion was not accepted by itself. Both retained artifact ZIPs,
the internal evidence archive, all stage records, every retained primary output,
and the independent canonical-k-mer result were audited after the run.

## Durable artifact integrity

| Artifact | GitHub artifact ID | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| Complete evidence | `11950830857` | 35,661,650 | `f6b889c5084eda46f2469a763cf44ee2f80bff6eb346cecd008e73496633e6e6` |
| Final outcome | `11950771061` | 1,923 | `7ae30a74ab4e563361b36d1d6bf5a81bfb5affbd9eda1dfe03892c0b9b64ba22` |

The complete-evidence ZIP contained a 35,664,515-byte evidence TAR with SHA-256
`9415eade3e0ce172e6443f09a285b8dff08d23eda107958123ccb2fc65ceeaa0`.
Its ledger declared 48 files and 121,922,002 uncompressed bytes; both totals
matched extraction. All 32 retained primary scientific files matched their
recursive run-manifest path, byte count, and SHA-256.

## Pass evidence

- Both `ERR223688` FASTQs matched the frozen byte counts and MD5 values exactly.
- SPAdes 4.3.0 ran in default paired-read mode with unchanged `-t 2 -m 8` and
  exited zero in 2,920.074492 seconds, below the prospective 5,400-second bound.
- Peak process-tree RSS was 2,519,092 KiB, peak watched SPAdes-stage disk was
  3,415,372,552 bytes, and peak complete working-root usage was 5,552,577,271
  bytes. None crossed its frozen envelope; no timeout, OOM, or ENOSPC evidence
  was recorded.
- The unchanged filter retained 163 of 431 input contigs. The filtered FASTA
  SHA-256 is
  `ee1a643a185d5dcc0e926c9c42da79e67054e340967afb082b36eb55e299dbc5`.
- QUAST 5.2.0 exited zero. The filtered assembly N50 was 40,334 bp.
- DSK 2.3.3 exited zero with unchanged k=31, abundance-min=1,
  max-memory=8000 and the prospectively corrected `work/dsk_tmp` preparation.
- DSK2ASCII exited zero. The retained ASCII output has 2,098,204 rows and
  SHA-256
  `cc33735372a337f45c1cb07681739bb14adaf14ae4142fcad1e9326e3b42695b`.
- The independent A<C<T<G reverse-complement canonical oracle found exactly
  2,098,204 expected and 2,098,204 observed features: missing 0, extra 0,
  duplicate rows 0, abundance mismatches 0.
- No automatic or silent retry occurred.

## Scientific boundary

This PASS establishes that the maximum-rank isolate can complete the unchanged
assembly, filter/QC, DSK and independent-equality pipeline inside the separately
predeclared V3 execution envelope. It resolves the maximum-isolate resource
question tested by V3.

It does **not** rewrite the original n=8 gate, V1, or V2; each retains its
recorded failure. It does not establish corrected-SEER n=8 correctness,
1,102-isolate feasibility, Hicks SCM/RF metric replay, or model performance.

The only newly authorized action is to **design and freeze** a separate,
prospective corrected-SEER n=8 combine protocol using the eight durable isolate
outputs. Execution of that combine, full-cohort reconstruction, and model
training remain unauthorized.

Machine-readable evidence: `max_isolate_resource_resolution_v3_result.json`.
