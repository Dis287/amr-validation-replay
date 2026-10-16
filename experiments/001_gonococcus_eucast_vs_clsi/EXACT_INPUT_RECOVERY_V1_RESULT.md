# N8_DSK_EXACT_INPUT_RECOVERY_V1 result

Status: `PASS_INDEPENDENTLY_AUDITED`

## Identity

- Experiment: `N8_DSK_EXACT_INPUT_RECOVERY_V1`
- GitHub Actions run: [`38922709421`](https://github.com/Dis287/amr-validation-replay/actions/runs/38922709421)
- Run number / attempt: `1 / 1`
- Trigger: manual `workflow_dispatch`
- Frozen head: `b10e424a17b4ba82586159493e22e398b69aa03b`
- Started: `2026-10-16T15:17:25Z`
- Completed: `2026-10-16T16:30:48Z`
- GitHub conclusion: `success`

The GitHub conclusion was not accepted by itself. Acceptance required exact
per-file identities, independent canonical-k-mer equality for every regenerated
isolate, an independently built seven-file manifest, a versioned GitHub Release
asset, and a fresh release download/read-back audit.

## Phase A and execution boundary

Phase A queried the seven predeclared historical artifact IDs. Each returned
HTTP 404. Before any FASTQ download, the workflow froze the missing subset as
exactly `min`, `p10`, `p25`, `median`, `p75`, `p90`, and `p99`.
Phase A performed no biological computation.

Each missing isolate then received exactly one prospectively bounded
regeneration attempt under the frozen scientific pipeline. No automatic or
silent retry occurred.

## Exact seven-file result

| Rank | Isolate | Rows | Bytes | DSK ASCII SHA-256 |
| --- | --- | ---: | ---: | --- |
| min | `ERR1067833` | 2,103,513 | 71,519,738 | `1b60a3c86547f95055e3d51e138c6f7d6b2329967f3851ebe7112df309276a44` |
| p10 | `ERR1067740` | 2,100,606 | 71,420,896 | `4ad0b03e3d184f5d694d43f5f43d7bfc7478eb655018e0bcefe58c6070f5eab2` |
| p25 | `ERR1067765` | 2,101,892 | 71,464,617 | `9489718a0b3990b0c59146861148f9898a96128fce09202cb6fb5b1e12c687e3` |
| median | `ERR855281` | 2,092,013 | 71,128,704 | `dee3cf91f0bba7fb5667a5818aa6992fe904209e26ddc73a77b8fc505f48355c` |
| p75 | `ERR855022` | 2,045,008 | 69,530,491 | `518d08abb3127485e555e46c73dc71c16a14e218c267ea99d197d89bcca79a9b` |
| p90 | `ERR854935` | 2,094,204 | 71,203,186 | `d6b821a29508df203a057620830004b3eab96eeea3b90ba495830fb2d1bd9175` |
| p99 | `ERR223664` | 2,096,522 | 71,281,996 | `d3a57a04d3a3093e86e8af73dd966598112cde6790eceb166d547140886fdb0d` |

For every isolate:

- both FASTQ byte counts and MD5 values matched the frozen protocol;
- the filtered-FASTA SHA-256 matched the frozen expected identity;
- the DSK ASCII row count, byte count, and SHA-256 matched exactly;
- the independent A<C<T<G reverse-complement oracle reported zero missing,
  extra, duplicate, and abundance-mismatched rows;
- the accepted state was `REGENERATED_EXACT`.

The seven accepted DSK files total exactly 497,549,628 bytes. The p99 SPAdes
stage completed in 2,472.237 seconds, inside the frozen 2,700-second bound.

## Durable evidence and release read-back

| Evidence | ID | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| Phase-A artifact | `12055776279` | recorded by GitHub | `8fedd9fce4675499939224ef2d9311e95ba167177aa698f08e6c7692af15a9e0` |
| Final independent-audit artifact | `12059946653` | 362,456,438 | `e9975746c55178c230c05a93d1d5c030360e11efa59165fa2b6971098b779b7a` |
| Final receipt artifact | `12059991120` | 431 | `45e51f863aebead07a828fde8720c5b44e1739e04dd00021e189c27ba7f1fc5f` |

The immutable release is
[`experiment001-n8-exact-inputs-v1`](https://github.com/Dis287/amr-validation-replay/releases/tag/experiment001-n8-exact-inputs-v1).
Its asset `experiment001-n8-exact-inputs-v1.tar.gz` has release asset ID
`647907441`, size 120,220,273 bytes, and SHA-256
`b132c289f07d18378e052b69d2987fb6f5ee03f74d38958cdc7c1e7f1f2aca5b`.

A fresh download independently matched that byte count and SHA-256. The archive
contained exactly the seven accepted `kmers.txt` files plus
`complete_manifest.json`. Every extracted DSK file again matched its frozen
row count, byte count, and SHA-256, and the manifest total was exactly
497,549,628 bytes.

## Scientific boundary

This PASS resolves only the exact-input availability gate for the seven
previously expired n=8 DSK inputs. It does not rewrite the original n=8 failure,
the V1 failure, or the V2 failure. It does not establish corrected-SEER n=8
correctness, 1,102-isolate feasibility, Hicks SCM/RF metric replay, a final
claim-state transition, commercial value, or breakthrough status.

Corrected-SEER n=8 remains **unexecuted**. The only newly allowed next step is
to design, audit, and freeze a separate prospective corrected-SEER n=8 combine
protocol using the seven release-verified inputs and the independently audited
maximum-isolate V3 output. Full-cohort reconstruction and model training remain
unauthorized.

Machine-readable evidence:
`exact_input_recovery_v1_result.json`.
