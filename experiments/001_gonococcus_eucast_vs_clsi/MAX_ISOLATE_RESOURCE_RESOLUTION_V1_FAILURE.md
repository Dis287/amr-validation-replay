# MAX_ISOLATE_RESOURCE_RESOLUTION_V1 — terminal infrastructure result

`MAX_ISOLATE_RESOURCE_RESOLUTION_V1` was executed once by GitHub Actions run
`38591577348` from commit
`64b3f06d5eeb9a89a3f69f0abfc2c3ed42dc6d84`.

## Audited result

- workflow event: `workflow_dispatch`
- run number / attempt: `1 / 1`
- terminal state: `failure`
- scientific classification: `INFRASTRUCTURE_PREFLIGHT_FAILURE`
- first failing stage: `preflight`
- violation: `filesystem_total`
- mounted-filesystem total: `154894188544` bytes
- mounted-filesystem free: `90323972096` bytes
- input download: not reached
- SPAdes, QUAST, DSK and oracle: not run
- full evidence artifact: uploaded and hash-verified
- final outcome artifact: uploaded and hash-verified

The runner was the requested standard public `ubuntu-24.04` x64 class with four
CPUs and less than 16 GiB RAM. The harness rejected it because it compared the
mounted filesystem's total backing capacity with the published 14 GB standard
runner storage specification. That check does not measure experiment disk use
and made the declared standard runner fail solely because its mounted backing
filesystem reported a larger total capacity.

This is a terminal infrastructure failure for V1. It is not a result for
`ERR223688`, and it must not be rerun or reclassified.

## Evidence identities

- run: `https://github.com/Dis287/amr-validation-replay/actions/runs/38591577348`
- full evidence artifact ID: `11906849923`
- full evidence artifact ZIP SHA-256:
  `7d3a1739723a28e3e6cf880bc20bf70878c43d12948278031993ba3234b3fac3`
- internal evidence TAR SHA-256:
  `731923277524723da3a55eaa637b9d51e53133ccac964021212e9aa2a92bac42`
- final outcome artifact ID: `11908360225`
- final outcome artifact ZIP SHA-256:
  `29cd33dbfb8790a7d14e72d117af29f8e02fec07d10da4c469cbb35a61389b35`

The original n=8 gate remains failed. Corrected-SEER n=8, the full cohort and
model training remain unauthorized.
