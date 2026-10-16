# CORRECTED_SEER_N8_COMBINE_V2 — terminal acquisition result

`CORRECTED_SEER_N8_COMBINE_V2` was dispatched exactly once by GitHub Actions
run `38964235718` from commit
`995e40f42a2bca66b9b6d81def39fc736dc8af62`.

## Audited result

- workflow event: `workflow_dispatch`
- run number / attempt: `1 / 1`
- GitHub conclusion: `failure`
- recorded state: `FAIL_INPUT_INTEGRITY`
- preflight: PASS
- seven-input release acquisition: completed
- seven extracted DSK identities: all seven match frozen bytes and SHA-256
- maximum artifact acquisition: failed before a destination file survived
- corrected-SEER build: not reached
- corrected-SEER combine: not run
- independent feature oracle: not run
- result release: not created
- candidate and final evidence artifacts: retained

The V2 harness called the GitHub artifact archive URL for maximum input artifact
`11950830857`. Its download helper returned a non-200 status: this follows
from the short-circuit branch that raised `RuntimeError("maximum artifact
mismatch")` while `sources/maximum.zip` did not exist. The exact HTTP status
was not recorded and is therefore UNKNOWN.

The generic recorded state `FAIL_INPUT_INTEGRITY` is preserved. It must not be
interpreted as proof that the maximum DSK content differed, because the V2
runner never received an outer ZIP to hash or extract.

An independent post-run audit downloaded artifact `11950830857` successfully
and verified:

- outer ZIP bytes: 35,661,650
- outer ZIP SHA-256:
  `f6b889c5084eda46f2469a763cf44ee2f80bff6eb346cecd008e73496633e6e6`
- internal evidence TAR bytes: 35,664,515
- internal evidence TAR SHA-256:
  `9415eade3e0ce172e6443f09a285b8dff08d23eda107958123ccb2fc65ceeaa0`
- maximum DSK rows: 2,098,204
- maximum DSK bytes: 71,339,203
- maximum DSK SHA-256:
  `cc33735372a337f45c1cb07681739bb14adaf14ae4142fcad1e9326e3b42695b`

Those post-run checks confirm the frozen maximum content remains recoverable;
they do not convert V2 into a pass. V2 is terminal and must not be rerun.

## Durable evidence identities

- run: https://github.com/Dis287/amr-validation-replay/actions/runs/38964235718
- candidate artifact ID: `12073124396`
- candidate artifact digest:
  `sha256:dd4b61b20225808314b82d9240cdd7fce931521ebb024b7175982f9f7f9730f0`
- candidate-receipt artifact ID: `12073807863`
- candidate-receipt digest:
  `sha256:83de6cbf8c9d944ee7fb93f20bbee2843611caa8baa2c082c81794fcc8a80464`
- final-audit artifact ID: `12073429014`
- final-audit digest:
  `sha256:d2150246aef8195190990f50a8d018dbec7389e2fc4782fc789fbcd80256ce90`
- final-receipt artifact ID: `12073618177`
- final-receipt digest:
  `sha256:761c1def718178756a187e35f7ce4b4616e7878b37adaf45c58466cefa648f08`
- run-log archive SHA-256:
  `ddaf0f45c3809744a7a33a4b88f93ca3ebbfd98557e7c6d68f13a880d6a55fd7`

## Next justified gate

Do not retry V2. Freeze a separately named input-consolidation experiment that
creates one immutable, independently read-back-verified release containing all
eight exact DSK files. Only after that release exists may a new corrected-SEER
n=8 combine protocol reference one stable source.

The original n=8 gate remains failed. Corrected-SEER n=8 correctness,
full-cohort feasibility, and Hicks model replay remain unestablished.
Full-cohort execution and model training remain unauthorized.
