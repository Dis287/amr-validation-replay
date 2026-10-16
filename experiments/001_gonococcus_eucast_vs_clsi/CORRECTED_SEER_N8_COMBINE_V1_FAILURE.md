# CORRECTED_SEER_N8_COMBINE_V1 — terminal infrastructure result

`CORRECTED_SEER_N8_COMBINE_V1` was dispatched exactly once by GitHub Actions
run `38962929988` from commit
`4b8813636a34da16e18eda208da9aed8ef2a19e9`.

## Audited result

- workflow event: `workflow_dispatch`
- run number / attempt: `1 / 1`
- GitHub conclusion: `failure`
- recorded harness state: `FAIL_INPUT_INTEGRITY`
- independently audited cause: pre-input harness filesystem initialization defect
- preflight: PASS
- input download: not completed
- exact input verification: not reached
- corrected-SEER build: not reached
- corrected-SEER combine: not run
- independent oracle: not run
- result release: not created
- candidate, receipt, final-audit, final-receipt, and run-log artifacts: retained and hash-verified

The harness resolved the seven-input release asset and then attempted to open
`$ROOT/sources/seven.tar.gz` for writing without first creating
`$ROOT/sources`. Python raised `FileNotFoundError` at
`destination.open("wb")`. No biological input archive was written.

The emitted `FAIL_INPUT_INTEGRITY` value is preserved as the V1 terminal
record. It is not evidence of a mismatched biological input because no input was
downloaded or checked. The evidence establishes only a harness defect before
input acquisition.

V1 is terminal under its one-attempt law. It must not be rerun, reclassified,
or overwritten. A correction requires a separately named prospective
experiment.

## Evidence identities

- run: https://github.com/Dis287/amr-validation-replay/actions/runs/38962929988
- execute job: `117182235235`
- independent-audit job: `117182399052`
- candidate artifact ID: `12073546984`
- candidate artifact ZIP SHA-256:
  `3bd53881321e726661ddfa05de30386ff9b27336cfb2a2cde071ccef1f2cea24`
- candidate-receipt artifact ID: `12073860886`
- candidate-receipt ZIP SHA-256:
  `fde0fe8ad4e8f21a2ea891602b9a98b44d47c670fd8192d0c4001d03b834de34`
- final-audit artifact ID: `12073447510`
- final-audit ZIP SHA-256:
  `cf21bf033c245a27c84ca68378135241cabef30f25e741964c692e46fc316a92`
- final-receipt artifact ID: `12073387452`
- final-receipt ZIP SHA-256:
  `835af0cbb19de8138390fcbd4c87f4001ce0b158e93ede92415e2ef810f40562`
- run-log archive SHA-256:
  `55be4b8eec116bfa82432cc97da3b828969ccb5dc61e2f8f8365c6187653cf15`

The original n=8 gate remains failed. Corrected-SEER n=8 correctness, full-cohort
feasibility, and Hicks model replay remain unestablished. Full-cohort execution
and model training remain unauthorized.
