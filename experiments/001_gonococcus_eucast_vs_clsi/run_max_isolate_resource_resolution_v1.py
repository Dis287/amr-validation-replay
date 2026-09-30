#!/usr/bin/env python3
"""Dedicated, single-attempt harness for MAX_ISOLATE_RESOURCE_RESOLUTION_V1.

The default command is inert.  Scientific execution requires the explicit
``run`` subcommand, which is invoked only by the separately named manual
workflow.  ``self-test`` uses local synthetic fixtures and no network access.
"""

from __future__ import annotations

import argparse
import collections
import contextlib
import datetime as dt
import errno
import gzip
import hashlib
import json
import os
import pathlib
import platform
import shutil
import signal
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.parse
import urllib.request


HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
PROTOCOL_JSON = HERE / "max_isolate_resource_resolution_v1.json"
PROTOCOL_MD = HERE / "MAX_ISOLATE_RESOURCE_RESOLUTION_V1.md"
PROTOCOL_HASHES = {
    str(PROTOCOL_MD.relative_to(REPO)): "f89571d25fd7a4f9c23675c93b818032ffe114e8e9699e116290649da0c8eebd",
    str(PROTOCOL_JSON.relative_to(REPO)): "48b346e2bfa4eefbbd2db9553fb348b977c17c718e473d434a78e523b3b74f8a",
}
EXPERIMENT_ID = "MAX_ISOLATE_RESOURCE_RESOLUTION_V1"
TARGET = "ERR223688"
FAILURES = {
    "FAIL_INPUT_INTEGRITY",
    "FAIL_SPADES_TIMEOUT",
    "FAIL_MEMORY_ENVELOPE",
    "FAIL_STORAGE_ENVELOPE",
    "FAIL_SPADES_NONZERO",
    "FAIL_SPADES_OUTPUT",
    "FAIL_QC_STAGE",
    "FAIL_DSK_STAGE",
    "FAIL_DSK_EQUALITY",
    "FAIL_EVIDENCE_RETENTION",
}
INFRA_FAILURE = "INFRASTRUCTURE_PREFLIGHT_FAILURE"
TOOLS = {
    "spades": {
        "url": "https://github.com/ablab/spades/releases/download/v4.3.0/SPAdes-4.3.0-Linux.tar.gz",
        "sha256": "e88a8c533c8614dd4b7c5788cfcd46427848a0575267f97c690a75fd2a343034",
    },
    "quast": {
        "url": "https://github.com/ablab/quast/releases/download/quast_5.2.0/quast-5.2.0.tar.gz",
        "sha256": "ccd911087cfa254ad4b8eadac4f95d4685e44c3996f5516b8e0ce6f7cfa7e0db",
    },
    "dsk": {
        "url": "https://github.com/GATB/dsk/releases/download/v2.3.3/dsk-v2.3.3-bin-Linux.tar.gz",
        "sha256": "626a4663f70323a80834c013f1d9dcb4a3b3a73a1c9ab5da95a013783d81b0f6",
    },
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def write_json(path: pathlib.Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def hash_file(path: pathlib.Path, algorithm: str = "sha256") -> str:
    digest = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def protocol() -> dict:
    observed = {
        str(path.relative_to(REPO)): hash_file(path)
        for path in (PROTOCOL_MD, PROTOCOL_JSON)
    }
    if observed != PROTOCOL_HASHES:
        raise RuntimeError(f"frozen protocol hash mismatch: {observed!r}")
    value = json.loads(PROTOCOL_JSON.read_text(encoding="utf-8"))
    if value["experiment_id"] != EXPERIMENT_ID or value["status"] != "FROZEN_NOT_EXECUTED":
        raise RuntimeError("unexpected frozen protocol identity/status")
    return value


def outcome_template() -> dict:
    return {
        "schema": "amr-max-isolate-resource-resolution-outcome-v1",
        "experiment_id": EXPERIMENT_ID,
        "target_isolate": TARGET,
        "status": "INCOMPLETE",
        "classification": None,
        "candidate_pass": False,
        "independent_audit_required": True,
        "first_failing_stage": None,
        "started_at_utc": utc_now(),
        "finished_at_utc": None,
        "no_retry_occurred": True,
        "original_n8_gate_remains_failed": True,
        "corrected_seer_n8_authorized": False,
        "full_1102_reconstruction_authorized": False,
        "model_training_authorized": False,
        "commands": [],
        "measurements": {},
        "available_hashes": {},
        "missing_evidence": [],
        "notes": [],
    }


class TerminalFailure(Exception):
    def __init__(self, classification: str, stage: str, message: str):
        super().__init__(message)
        self.classification = classification
        self.stage = stage


def download(url: str, destination: pathlib.Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "amr-validation-replay/1"})
    with urllib.request.urlopen(request, timeout=120) as response, destination.open("wb") as output:
        shutil.copyfileobj(response, output, length=8 * 1024 * 1024)


def extract_archive(archive: pathlib.Path, destination: pathlib.Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "r:gz") as handle:
        root = destination.resolve()
        for member in handle.getmembers():
            target = (destination / member.name).resolve()
            if root != target and root not in target.parents:
                raise RuntimeError(f"unsafe archive member: {member.name}")
        handle.extractall(destination)


def cpu_model() -> str:
    try:
        for line in pathlib.Path("/proc/cpuinfo").read_text(encoding="utf-8").splitlines():
            if line.startswith("model name"):
                return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or "UNKNOWN"


def total_ram_kib() -> int:
    for line in pathlib.Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
        if line.startswith("MemTotal:"):
            return int(line.split()[1])
    raise RuntimeError("MemTotal unavailable")


def prior_dispatch_guard(token: str) -> dict:
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    run_id = int(os.environ.get("GITHUB_RUN_ID", "0"))
    attempt = int(os.environ.get("GITHUB_RUN_ATTEMPT", "0"))
    if not repo or not token or run_id <= 0 or attempt != 1:
        return {"passed": False, "reason": "missing context/token or run attempt is not 1", "attempt": attempt}
    workflow = urllib.parse.quote("max-isolate-resource-resolution-v1.yml", safe="")
    url = f"https://api.github.com/repos/{repo}/actions/workflows/{workflow}/runs?event=workflow_dispatch&per_page=100"
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "amr-validation-replay/1",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    earlier = sorted(int(run["id"]) for run in payload.get("workflow_runs", []) if int(run["id"]) != run_id)
    return {"passed": not earlier, "current_run_id": run_id, "prior_run_ids": earlier, "attempt": attempt}


def process_tree_rss_kib(root_pid: int) -> int:
    parents: dict[int, int] = {}
    rss: dict[int, int] = {}
    for entry in pathlib.Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        try:
            fields = (entry / "stat").read_text(encoding="utf-8").split()
            parents[int(entry.name)] = int(fields[3])
            for line in (entry / "status").read_text(encoding="utf-8").splitlines():
                if line.startswith("VmRSS:"):
                    rss[int(entry.name)] = int(line.split()[1])
                    break
        except (OSError, ValueError, IndexError):
            continue
    descendants = {root_pid}
    changed = True
    while changed:
        changed = False
        for pid, parent in parents.items():
            if parent in descendants and pid not in descendants:
                descendants.add(pid)
                changed = True
    return sum(rss.get(pid, 0) for pid in descendants)


def directory_bytes(path: pathlib.Path) -> int:
    if not path.exists():
        return 0
    total = 0
    for item in path.rglob("*"):
        try:
            if item.is_file() and not item.is_symlink():
                total += item.stat().st_size
        except OSError:
            continue
    return total


def cgroup_oom_kill_count() -> int | None:
    candidates = [pathlib.Path("/sys/fs/cgroup/memory.events")]
    try:
        relative = pathlib.Path("/proc/self/cgroup").read_text(encoding="utf-8").splitlines()
        for line in relative:
            fields = line.split(":", 2)
            if len(fields) == 3 and fields[0] == "0":
                candidates.insert(0, pathlib.Path("/sys/fs/cgroup") / fields[2].lstrip("/") / "memory.events")
    except OSError:
        pass
    for path in candidates:
        try:
            values = dict(line.split() for line in path.read_text(encoding="utf-8").splitlines())
            return int(values.get("oom_kill", "0"))
        except (OSError, ValueError):
            continue
    return None


def terminate_group(process: subprocess.Popen, grace_seconds: int) -> dict:
    evidence = {"sigterm_sent": False, "sigkill_sent": False, "grace_seconds": grace_seconds}
    if process.poll() is not None:
        return evidence
    with contextlib.suppress(ProcessLookupError):
        os.killpg(process.pid, signal.SIGTERM)
        evidence["sigterm_sent"] = True
    deadline = time.monotonic() + grace_seconds
    while process.poll() is None and time.monotonic() < deadline:
        time.sleep(0.1)
    if process.poll() is None:
        with contextlib.suppress(ProcessLookupError):
            os.killpg(process.pid, signal.SIGKILL)
            evidence["sigkill_sent"] = True
    return evidence


def bounded_stage(
    name: str,
    command: list[str],
    cwd: pathlib.Path,
    evidence: pathlib.Path,
    wall_seconds: float,
    sample_seconds: float = 0.5,
    rss_ceiling_kib: int | None = None,
    disk_path: pathlib.Path | None = None,
    disk_ceiling_bytes: int | None = None,
    grace_seconds: int = 10,
) -> dict:
    log = evidence / f"{name}.log"
    record_path = evidence / f"{name}.stage.json"
    started = time.monotonic()
    record = {
        "stage": name,
        "command": command,
        "cwd": str(cwd),
        "wall_ceiling_seconds": wall_seconds,
        "sample_interval_seconds": sample_seconds,
        "rss_ceiling_kib": rss_ceiling_kib,
        "disk_ceiling_bytes": disk_ceiling_bytes,
        "started_at_utc": utc_now(),
        "peak_process_tree_rss_kib": 0,
        "peak_watched_disk_bytes": 0,
        "trigger": None,
        "exit_code": None,
        "termination": None,
    }
    oom_before = cgroup_oom_kill_count()
    try:
        with log.open("wb") as output:
            process = subprocess.Popen(
                command,
                cwd=cwd,
                stdout=output,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
            while process.poll() is None:
                elapsed = time.monotonic() - started
                rss = process_tree_rss_kib(process.pid)
                disk = directory_bytes(disk_path) if disk_path else 0
                record["peak_process_tree_rss_kib"] = max(record["peak_process_tree_rss_kib"], rss)
                record["peak_watched_disk_bytes"] = max(record["peak_watched_disk_bytes"], disk)
                if rss_ceiling_kib is not None and rss >= rss_ceiling_kib:
                    record["trigger"] = "rss_ceiling"
                elif disk_ceiling_bytes is not None and disk >= disk_ceiling_bytes:
                    record["trigger"] = "disk_ceiling"
                elif elapsed >= wall_seconds:
                    record["trigger"] = "wall_ceiling"
                if record["trigger"]:
                    record["termination"] = terminate_group(process, grace_seconds)
                    break
                time.sleep(sample_seconds)
            record["exit_code"] = process.wait()
    except OSError as exc:
        record["os_error"] = {"errno": exc.errno, "message": str(exc)}
        if exc.errno == errno.ENOSPC:
            record["trigger"] = "filesystem_exhaustion"
        record["exit_code"] = None
    record["wall_seconds"] = round(time.monotonic() - started, 6)
    oom_after = cgroup_oom_kill_count()
    record["cgroup_oom_kill_before"] = oom_before
    record["cgroup_oom_kill_after"] = oom_after
    record["kernel_oom_evidence"] = oom_before is not None and oom_after is not None and oom_after > oom_before
    try:
        log_tail = log.read_bytes()[-1024 * 1024 :]
    except OSError:
        log_tail = b""
    record["filesystem_enospc_evidence"] = b"No space left on device" in log_tail or b"ENOSPC" in log_tail
    record["finished_at_utc"] = utc_now()
    write_json(record_path, record)
    return record


def fasta_records(path: pathlib.Path):
    name = None
    parts: list[str] = []
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if name is not None:
                    yield name, "".join(parts)
                name, parts = line[1:], []
            else:
                parts.append(line)
    if name is not None:
        yield name, "".join(parts)


def filter_contigs(source: pathlib.Path, destination: pathlib.Path, metrics_path: pathlib.Path) -> dict:
    metrics = {"minimum_length_bp": 200, "minimum_header_coverage": 10, "input": 0, "retained": 0}
    with destination.open("w", encoding="utf-8") as output:
        for header, sequence in fasta_records(source):
            metrics["input"] += 1
            try:
                coverage = float(header.split("_cov_", 1)[1].split("_", 1)[0])
            except (IndexError, ValueError):
                raise RuntimeError(f"unparseable SPAdes coverage header: {header}")
            if len(sequence) >= 200 and coverage >= 10:
                metrics["retained"] += 1
                output.write(f">{header}\n{sequence}\n")
    metrics["output_bytes"] = destination.stat().st_size
    write_json(metrics_path, metrics)
    return metrics


RANK = {"A": 0, "C": 1, "T": 2, "G": 3}
COMPLEMENT = str.maketrans("ACTG", "TGAC")


def canonical(kmer: str) -> str:
    kmer = kmer.upper()
    rc = kmer.translate(COMPLEMENT)[::-1]
    key = lambda text: tuple(RANK[base] for base in text)
    return min((kmer, rc), key=key)


def independent_counts(fasta: pathlib.Path, k: int = 31) -> collections.Counter:
    result: collections.Counter = collections.Counter()
    for _header, sequence in fasta_records(fasta):
        sequence = sequence.upper()
        for start in range(0, len(sequence) - k + 1):
            kmer = sequence[start : start + k]
            if set(kmer) <= RANK.keys():
                result[canonical(kmer)] += 1
    return result


def verify_dsk(fasta: pathlib.Path, ascii_path: pathlib.Path, output: pathlib.Path) -> dict:
    expected = independent_counts(fasta, 31)
    observed: dict[str, int] = {}
    duplicate_rows = 0
    with ascii_path.open("r", encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            fields = line.split()
            if len(fields) != 2:
                raise RuntimeError(f"invalid DSK ASCII row {number}")
            kmer, abundance_text = fields
            normalized = canonical(kmer)
            if normalized in observed:
                duplicate_rows += 1
            else:
                observed[normalized] = int(abundance_text)
    missing = sorted(set(expected) - set(observed))
    extra = sorted(set(observed) - set(expected))
    abundance = sorted(k for k in set(expected) & set(observed) if expected[k] != observed[k])
    result = {
        "canonical_order": "A<C<T<G",
        "reverse_complement_canonicalization": True,
        "expected_feature_count": len(expected),
        "observed_feature_count": len(observed),
        "missing": len(missing),
        "extra": len(extra),
        "duplicate_rows": duplicate_rows,
        "abundance_mismatches": len(abundance),
        "missing_examples": missing[:20],
        "extra_examples": extra[:20],
        "abundance_mismatch_examples": abundance[:20],
        "exact": not (missing or extra or duplicate_rows or abundance),
    }
    write_json(output, result)
    return result


def copy_existing(source: pathlib.Path, destination: pathlib.Path) -> None:
    if not source.exists():
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, destination, dirs_exist_ok=True)
    else:
        shutil.copy2(source, destination)


def recursive_manifest(root: pathlib.Path, output: pathlib.Path) -> dict:
    rows = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path == output:
            continue
        rows.append({
            "path": str(path.relative_to(root)),
            "bytes": path.stat().st_size,
            "sha256": hash_file(path),
        })
    value = {"root": str(root), "file_count": len(rows), "files": rows}
    write_json(output, value)
    return value


def remaining(started: float, limit: float, requested: float) -> float:
    value = min(requested, limit - (time.monotonic() - started))
    if value <= 0:
        raise TerminalFailure(INFRA_FAILURE, "whole_job", "whole-job execution ceiling reached")
    return value


def classify_stage(record: dict, stage: str) -> None:
    trigger = record.get("trigger")
    if stage == "spades":
        if trigger == "wall_ceiling":
            raise TerminalFailure("FAIL_SPADES_TIMEOUT", stage, "SPAdes wall ceiling")
        if trigger == "rss_ceiling":
            raise TerminalFailure("FAIL_MEMORY_ENVELOPE", stage, "sampled RSS ceiling")
        if record.get("kernel_oom_evidence"):
            raise TerminalFailure("FAIL_MEMORY_ENVELOPE", stage, "cgroup oom_kill counter increased")
        if trigger in {"disk_ceiling", "filesystem_exhaustion"} or record.get("filesystem_enospc_evidence"):
            raise TerminalFailure("FAIL_STORAGE_ENVELOPE", stage, "SPAdes storage envelope")
        if record.get("exit_code") != 0:
            raise TerminalFailure("FAIL_SPADES_NONZERO", stage, "SPAdes nonzero exit")
    elif record.get("exit_code") != 0 or trigger:
        code = "FAIL_QC_STAGE" if stage == "quast" else "FAIL_DSK_STAGE"
        raise TerminalFailure(code, stage, f"{stage} failed or exceeded its bound")


def run_experiment(root: pathlib.Path, token: str) -> int:
    work = root / "work"
    evidence = root / "evidence"
    downloads = work / "downloads"
    tools_dir = work / "tools"
    reads = work / "reads"
    for path in (work, evidence, downloads, tools_dir, reads):
        path.mkdir(parents=True, exist_ok=True)
    outcome_path = evidence / "outcome.json"
    outcome = outcome_template()
    write_json(outcome_path, outcome)
    started = time.monotonic()
    try:
        spec = protocol()
        tool_records = {}
        tool_hash_violations = []
        for name, item in TOOLS.items():
            archive = downloads / pathlib.Path(urllib.parse.urlparse(item["url"]).path).name
            download(item["url"], archive)
            observed = hash_file(archive)
            exact = observed == item["sha256"]
            tool_records[name] = {
                "url": item["url"], "archive": archive.name,
                "expected_sha256": item["sha256"], "observed_sha256": observed, "exact": exact,
            }
            if observed != item["sha256"]:
                tool_hash_violations.append(name)
            else:
                extract_archive(archive, tools_dir / name)

        disk = shutil.disk_usage(root)
        guard = prior_dispatch_guard(token)
        preflight = {
            "recorded_at_utc": utc_now(),
            "runner_image": os.environ.get("ImageOS", "UNKNOWN"),
            "runner_image_version": os.environ.get("ImageVersion", "UNKNOWN"),
            "runner_name": os.environ.get("RUNNER_NAME", "UNKNOWN"),
            "architecture": platform.machine(),
            "cpu_model": cpu_model(),
            "cpu_count": os.cpu_count(),
            "total_ram_kib": total_ram_kib(),
            "filesystem_total_bytes": disk.total,
            "filesystem_free_bytes": disk.free,
            "repository_commit": os.environ.get("GITHUB_SHA", "UNKNOWN"),
            "protocol_file_sha256": PROTOCOL_HASHES,
            "downloaded_tool_sha256": tool_records,
            "single_attempt_guard": guard,
            "requirements": {
                "runner_label": "ubuntu-24.04",
                "architecture": "x64",
                "maximum_cpu_count": 4,
                "maximum_total_ram_kib": 16 * 1024 * 1024,
                "maximum_filesystem_total_bytes": 14 * 1024**3,
                "minimum_free_bytes": 12884901888,
            },
        }
        violations = []
        if tool_hash_violations:
            violations.append("tool_archive_sha256")
        if platform.machine() not in {"x86_64", "AMD64"}:
            violations.append("architecture")
        if (os.cpu_count() or 10**9) > 4:
            violations.append("cpu_count")
        if preflight["total_ram_kib"] > 16 * 1024 * 1024:
            violations.append("total_ram")
        if disk.total > 14 * 1024**3:
            violations.append("filesystem_total")
        if disk.free < 12884901888:
            violations.append("filesystem_free")
        if not guard["passed"]:
            violations.append("single_attempt_guard")
        preflight["passed"] = not violations
        preflight["violations"] = violations
        write_json(evidence / "environment_preflight.json", preflight)
        outcome["available_hashes"]["frozen_protocol_sha256"] = PROTOCOL_HASHES
        outcome["available_hashes"]["tool_archives"] = tool_records
        write_json(outcome_path, outcome)
        if violations:
            raise TerminalFailure(INFRA_FAILURE, "preflight", ",".join(violations))

        input_records = []
        for item in spec["target_isolate"]["inputs"]:
            destination = reads / item["name"]
            download(item["ena_url"], destination)
            observed = {"bytes": destination.stat().st_size, "md5": hash_file(destination, "md5")}
            record = {
                "name": item["name"], "url": item["ena_url"],
                "expected_bytes": item["expected_bytes"], "expected_md5": item["expected_md5"],
                "observed_bytes": observed["bytes"], "observed_md5": observed["md5"],
                "exact": observed["bytes"] == item["expected_bytes"] and observed["md5"] == item["expected_md5"],
            }
            input_records.append(record)
        integrity = {"target_isolate": TARGET, "inputs": input_records, "exact": all(x["exact"] for x in input_records)}
        write_json(evidence / "input_integrity.json", integrity)
        outcome["available_hashes"]["inputs"] = input_records
        write_json(outcome_path, outcome)
        if not integrity["exact"]:
            raise TerminalFailure("FAIL_INPUT_INTEGRITY", "input_integrity", "input bytes or MD5 mismatch")

        spades_bin = next((tools_dir / "spades").rglob("spades.py"))
        quast_bin = next((tools_dir / "quast").rglob("quast.py"))
        dsk_bin = next(path for path in (tools_dir / "dsk").rglob("dsk") if path.is_file())
        dsk2ascii_bin = next(path for path in (tools_dir / "dsk").rglob("dsk2ascii") if path.is_file())
        assembly = work / "spades"
        commands = {
            "spades": [str(spades_bin), "-1", str(reads / "ERR223688_1.fastq.gz"), "-2", str(reads / "ERR223688_2.fastq.gz"), "-o", str(assembly), "-t", "2", "-m", "8"],
            "quast": [str(quast_bin), "--min-contig", "200", "--no-plots", "--no-html", "--no-icarus", "-t", "2", "-l", "raw,filtered", "-o", str(work / "quast"), str(assembly / "contigs.fasta"), str(work / "filtered.fasta")],
            "dsk": [str(dsk_bin), "-file", str(work / "filtered.fasta"), "-kmer-size", "31", "-abundance-min", "1", "-out", str(work / "kmers"), "-out-tmp", str(work / "dsk_tmp"), "-max-memory", "8000"],
            "dsk2ascii": [str(dsk2ascii_bin), "-file", str(work / "kmers.h5"), "-out", str(work / "kmers.txt")],
        }
        outcome["commands"] = commands
        write_json(outcome_path, outcome)

        record = bounded_stage("spades", commands["spades"], work, evidence, remaining(started, 9000, 5400), 0.5, 10485760, assembly, 8589934592, 10)
        classify_stage(record, "spades")
        contigs = assembly / "contigs.fasta"
        if not contigs.is_file() or contigs.stat().st_size == 0:
            raise TerminalFailure("FAIL_SPADES_OUTPUT", "spades_output", "missing or empty contigs.fasta")

        try:
            filter_contigs(contigs, work / "filtered.fasta", evidence / "filter_metrics.json")
        except Exception as exc:
            raise TerminalFailure("FAIL_QC_STAGE", "filter", str(exc)) from exc
        record = bounded_stage("quast", commands["quast"], work, evidence, remaining(started, 9000, 300))
        classify_stage(record, "quast")
        if not (work / "quast").is_dir():
            raise TerminalFailure("FAIL_QC_STAGE", "quast", "QUAST output missing")

        record = bounded_stage("dsk", commands["dsk"], work, evidence, remaining(started, 9000, 900))
        classify_stage(record, "dsk")
        if not (work / "kmers.h5").is_file():
            raise TerminalFailure("FAIL_DSK_STAGE", "dsk", "kmers.h5 missing")
        record = bounded_stage("dsk2ascii", commands["dsk2ascii"], work, evidence, remaining(started, 9000, 300))
        classify_stage(record, "dsk2ascii")
        if not (work / "kmers.txt").is_file():
            raise TerminalFailure("FAIL_DSK_STAGE", "dsk2ascii", "kmers.txt missing")

        oracle_command = [sys.executable, str(pathlib.Path(__file__).resolve()), "oracle", "--fasta", str(work / "filtered.fasta"), "--ascii", str(work / "kmers.txt"), "--output", str(evidence / "independent_verification.json")]
        outcome["commands"]["oracle"] = oracle_command
        record = bounded_stage("independent_oracle", oracle_command, work, evidence, remaining(started, 9000, 900))
        if record.get("exit_code") != 0 or record.get("trigger"):
            raise TerminalFailure("FAIL_DSK_EQUALITY", "independent_oracle", "oracle failed or exceeded its bound")
        verification = json.loads((evidence / "independent_verification.json").read_text(encoding="utf-8"))
        if not verification["exact"]:
            raise TerminalFailure("FAIL_DSK_EQUALITY", "independent_oracle", "DSK output differs from independent oracle")
        outcome["status"] = "CANDIDATE_PASS_AWAITING_INDEPENDENT_AUDIT_AND_RETENTION"
        outcome["candidate_pass"] = True
    except TerminalFailure as exc:
        outcome["status"] = "FAIL"
        outcome["classification"] = exc.classification
        outcome["first_failing_stage"] = exc.stage
        outcome["notes"].append(str(exc))
    except Exception as exc:
        outcome["status"] = "FAIL"
        if isinstance(exc, OSError) and exc.errno == errno.ENOSPC:
            outcome["classification"] = "FAIL_STORAGE_ENVELOPE"
            outcome["first_failing_stage"] = "filesystem_exhaustion"
        else:
            outcome["classification"] = INFRA_FAILURE
            outcome["first_failing_stage"] = "harness_exception"
        outcome["notes"].append(f"{type(exc).__name__}: {exc}")
    finally:
        outcome["finished_at_utc"] = utc_now()
        outcome["measurements"]["harness_wall_seconds"] = round(time.monotonic() - started, 6)
        write_json(outcome_path, outcome)
        with contextlib.suppress(Exception):
            recursive_manifest(work, evidence / "recursive_manifest.json")
        for source, destination in (
            (work / "spades" / "contigs.fasta", evidence / "primary" / "spades" / "contigs.fasta"),
            (work / "spades" / "scaffolds.fasta", evidence / "primary" / "spades" / "scaffolds.fasta"),
            (work / "spades" / "assembly_graph.fastg", evidence / "primary" / "spades" / "assembly_graph.fastg"),
            (work / "spades" / "assembly_graph_with_scaffolds.gfa", evidence / "primary" / "spades" / "assembly_graph_with_scaffolds.gfa"),
            (work / "spades" / "contigs.paths", evidence / "primary" / "spades" / "contigs.paths"),
            (work / "spades" / "scaffolds.paths", evidence / "primary" / "spades" / "scaffolds.paths"),
            (work / "spades" / "spades.log", evidence / "primary" / "spades" / "spades.log"),
            (work / "spades" / "params.txt", evidence / "primary" / "spades" / "params.txt"),
            (work / "spades" / "warnings.log", evidence / "primary" / "spades" / "warnings.log"),
            (work / "spades" / "pipeline_state", evidence / "primary" / "spades" / "pipeline_state"),
            (work / "filtered.fasta", evidence / "primary" / "filtered.fasta"),
            (work / "quast", evidence / "primary" / "quast"),
            (work / "kmers.h5", evidence / "primary" / "kmers.h5"),
            (work / "kmers.txt", evidence / "primary" / "kmers.txt"),
        ):
            with contextlib.suppress(Exception):
                copy_existing(source, destination)
        if not (evidence / "input_integrity.json").exists():
            write_json(evidence / "input_integrity.json", {"target_isolate": TARGET, "status": "NOT_REACHED", "inputs": []})
        if not (evidence / "environment_preflight.json").exists():
            write_json(evidence / "environment_preflight.json", {"status": "NOT_COMPLETED", "recorded_at_utc": utc_now()})
        required = ["outcome.json", "input_integrity.json", "environment_preflight.json", "recursive_manifest.json"]
        if outcome.get("candidate_pass"):
            required.extend([
                "spades.stage.json", "spades.log", "filter_metrics.json", "quast.stage.json", "quast.log",
                "dsk.stage.json", "dsk.log", "dsk2ascii.stage.json", "dsk2ascii.log",
                "independent_oracle.stage.json", "independent_oracle.log", "independent_verification.json",
                "primary/spades/contigs.fasta", "primary/filtered.fasta", "primary/quast",
                "primary/kmers.h5", "primary/kmers.txt",
            ])
        outcome["missing_evidence"] = [name for name in required if not (evidence / name).exists()]
        if outcome["missing_evidence"] and outcome.get("candidate_pass"):
            outcome["status"] = "FAIL"
            outcome["classification"] = "FAIL_EVIDENCE_RETENTION"
            outcome["candidate_pass"] = False
            outcome["first_failing_stage"] = "local_evidence_validation"
        write_json(outcome_path, outcome)
    return 0 if outcome["candidate_pass"] else 1


def package_evidence(root: pathlib.Path) -> int:
    evidence = root / "evidence"
    bundle_dir = root / "bundle"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    outcome_path = evidence / "outcome.json"
    outcome = json.loads(outcome_path.read_text(encoding="utf-8"))
    base_required = ["outcome.json", "input_integrity.json", "environment_preflight.json", "recursive_manifest.json"]
    missing = [name for name in base_required if not (evidence / name).exists()]
    if missing:
        outcome["status"] = "FAIL"
        outcome["classification"] = "FAIL_EVIDENCE_RETENTION"
        outcome["candidate_pass"] = False
        outcome["first_failing_stage"] = outcome.get("first_failing_stage") or "evidence_packaging"
        outcome["missing_evidence"] = sorted(set(outcome.get("missing_evidence", []) + missing))
        write_json(outcome_path, outcome)
    archive = bundle_dir / "max-isolate-resource-resolution-v1-evidence.tar.gz"
    with tarfile.open(archive, "w:gz") as handle:
        handle.add(evidence, arcname="evidence")
    files = [path for path in evidence.rglob("*") if path.is_file()]
    ledger = {
        "archive": archive.name,
        "sha256": hash_file(archive),
        "file_count": len(files),
        "uncompressed_size_bytes": sum(path.stat().st_size for path in files),
        "compressed_size_bytes": archive.stat().st_size,
        "created_at_utc": utc_now(),
    }
    write_json(bundle_dir / "artifact_ledger.json", ledger)
    return 0


def finalize_retention(root: pathlib.Path, full_upload: str, final_upload: str | None = None) -> int:
    outcome_path = root / "evidence" / "outcome.json"
    outcome = json.loads(outcome_path.read_text(encoding="utf-8")) if outcome_path.exists() else outcome_template()
    outcome["artifact_upload"] = {"full_evidence_outcome": full_upload, "final_record_outcome": final_upload}
    if full_upload != "success":
        outcome["status"] = "FAIL"
        outcome["classification"] = "FAIL_EVIDENCE_RETENTION"
        outcome["candidate_pass"] = False
        outcome["first_failing_stage"] = outcome.get("first_failing_stage") or "artifact_upload"
        outcome["missing_evidence"].append("durable full evidence artifact")
    write_json(outcome_path, outcome)
    write_json(root / "bundle" / "final_outcome.json", outcome)
    return 0


def self_test() -> int:
    assert canonical("G" + "A" * 30) == "T" * 30 + "C"
    with tempfile.TemporaryDirectory() as raw:
        root = pathlib.Path(raw)
        fasta = root / "tiny.fasta"
        fasta.write_text(">NODE_1_length_220_cov_12.0\n" + "ACTG" * 55 + "\n>NODE_2_length_199_cov_50.0\n" + "A" * 199 + "\n", encoding="utf-8")
        filtered = root / "filtered.fasta"
        metrics = filter_contigs(fasta, filtered, root / "metrics.json")
        assert metrics["retained"] == 1
        counts = independent_counts(filtered)
        ascii_path = root / "kmers.txt"
        with ascii_path.open("w", encoding="utf-8") as handle:
            for kmer, abundance in counts.items():
                handle.write(f"{kmer} {abundance}\n")
        assert verify_dsk(filtered, ascii_path, root / "verify.json")["exact"]
        record = bounded_stage("timeout_fixture", [sys.executable, "-c", "import time; time.sleep(5)"], root, root, 0.2, 0.05, grace_seconds=10)
        assert record["trigger"] == "wall_ceiling" and record["termination"]["sigterm_sent"]
    print("synthetic self-test: PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--root", required=True, type=pathlib.Path)
    run.add_argument("--github-token", default=os.environ.get("GITHUB_TOKEN", ""))
    package = sub.add_parser("package")
    package.add_argument("--root", required=True, type=pathlib.Path)
    finalize = sub.add_parser("finalize-retention")
    finalize.add_argument("--root", required=True, type=pathlib.Path)
    finalize.add_argument("--full-upload", required=True)
    finalize.add_argument("--final-upload")
    oracle = sub.add_parser("oracle")
    oracle.add_argument("--fasta", required=True, type=pathlib.Path)
    oracle.add_argument("--ascii", required=True, type=pathlib.Path)
    oracle.add_argument("--output", required=True, type=pathlib.Path)
    sub.add_parser("self-test")
    args = parser.parse_args()
    if args.command == "run":
        return run_experiment(args.root, args.github_token)
    if args.command == "package":
        return package_evidence(args.root)
    if args.command == "finalize-retention":
        return finalize_retention(args.root, args.full_upload, args.final_upload)
    if args.command == "oracle":
        result = verify_dsk(args.fasta, args.ascii, args.output)
        return 0 if result["exact"] else 1
    if args.command == "self-test":
        return self_test()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
