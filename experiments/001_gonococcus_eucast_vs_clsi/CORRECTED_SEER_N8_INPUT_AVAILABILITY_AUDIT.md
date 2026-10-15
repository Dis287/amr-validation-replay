# Corrected-SEER n=8 input-availability audit

Status: `BLOCKED_SEVEN_INPUT_ARTIFACTS_UNAVAILABLE`

Audit date: `2026-10-15` (UTC)

## Question

Can a prospective corrected-SEER n=8 combine protocol be frozen as an
executable experiment using the eight exact, independently verified DSK ASCII
outputs?

## Result

No. The exact maximum-rank DSK ASCII output remains available in the surviving
V3 evidence artifact, but the seven DSK ASCII outputs from GitHub Actions run
`36665031444` are not currently retrievable from GitHub.

The GitHub Actions artifact inventory for run `36665031444` returned zero
artifacts. Direct retrieval of each recorded artifact ID returned GitHub API
HTTP 404:

| Rank | Isolate | Artifact ID | Recorded DSK ASCII bytes | Recorded DSK ASCII SHA-256 | Current retrieval |
| --- | --- | ---: | ---: | --- | --- |
| min | `ERR1067833` | `11075707766` | 71,519,738 | `1b60a3c86547f95055e3d51e138c6f7d6b2329967f3851ebe7112df309276a44` | HTTP 404 |
| p10 | `ERR1067740` | `11076277598` | 71,420,896 | `4ad0b03e3d184f5d694d43f5f43d7bfc7478eb655018e0bcefe58c6070f5eab2` | HTTP 404 |
| p25 | `ERR1067765` | `11076500162` | 71,464,617 | `9489718a0b3990b0c59146861148f9898a96128fce09202cb6fb5b1e12c687e3` | HTTP 404 |
| median | `ERR855281` | `11075718734` | 71,128,704 | `dee3cf91f0bba7fb5667a5818aa6992fe904209e26ddc73a77b8fc505f48355c` | HTTP 404 |
| p75 | `ERR855022` | `11076109913` | 69,530,491 | `518d08abb3127485e555e46c73dc71c16a14e218c267ea99d197d89bcca79a9b` | HTTP 404 |
| p90 | `ERR854935` | `11076448396` | 71,203,186 | `d6b821a29508df203a057620830004b3eab96eeea3b90ba495830fb2d1bd9175` | HTTP 404 |
| p99 | `ERR223664` | `11076768772` | 71,281,996 | `d3a57a04d3a3093e86e8af73dd966598112cde6790eceb166d547140886fdb0d` | HTTP 404 |

The seven recorded files total 497,549,628 bytes. Their identities and prior
independent equality results survive in committed
`resource_panel_n8_failure.json`; the file contents do not survive in the
queried GitHub artifact store. A checksum cannot recreate missing bytes.

The maximum-rank input remains separately available:

- isolate/rank: `ERR223688` / maximum
- GitHub artifact ID: `11950830857`
- artifact state: not expired at audit time
- artifact ZIP SHA-256:
  `f6b889c5084eda46f2469a763cf44ee2f80bff6eb346cecd008e73496633e6e6`
- DSK ASCII bytes: 71,339,203
- DSK ASCII SHA-256:
  `cc33735372a337f45c1cb07681739bb14adaf14ae4142fcad1e9326e3b42695b`

## Classification

### FACT

- Run `36665031444` currently exposes zero GitHub Actions artifacts through the
  repository API.
- All seven recorded artifact IDs return HTTP 404 when directly requested.
- The seven exact DSK ASCII byte streams are therefore not presently available
  from their recorded durable source.
- V3 artifact `11950830857` remains available and its recorded digest matches
  the current GitHub artifact metadata.
- Corrected-SEER n=8 has not run.

### UNKNOWN

- Whether an exact copy of any of the seven DSK ASCII files survives outside
  the repository's GitHub Actions artifact store.
- Whether exact regeneration will reproduce the recorded ASCII byte order and
  SHA-256 values. This must be tested, not assumed.
- Why the seven artifacts are absent. No deletion or expiry cause is claimed by
  this audit.

## Decision

Gate G1 for `CORRECTED_SEER_N8_COMBINE_V1` fails: eight exact input files are
not available for pre-execution integrity verification. Therefore:

- no corrected-SEER n=8 combine protocol is declared executable or frozen;
- no combine harness is built;
- no corrected-SEER command is run;
- no substitute inputs are accepted;
- no seven-of-eight result is accepted;
- no full-cohort or training authorization follows.

The next permissible step is a separately frozen input-recovery protocol. It
must first search for surviving exact copies and accept them only on exact byte
count and SHA-256 equality. If exact copies cannot be recovered, any regeneration
must be prospectively specified from the already recorded FASTQ identities and
unchanged assembly/filter/DSK procedure, and its output must match each recorded
DSK ASCII byte count and SHA-256 before it can feed the n=8 combine. A mismatch
is reconstruction divergence, not permission to replace the frozen identity.

Machine-readable audit:
`corrected_seer_n8_input_availability_audit.json`.
