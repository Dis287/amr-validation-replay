#!/usr/bin/env python3
"""Inert-by-default harness for N8_DSK_EXACT_INPUT_RECOVERY_V1.

Only the manual workflow invokes network/scientific subcommands.  ``self-test``
uses synthetic local fixtures and performs no network or biological work.
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import hashlib
import json
import os
import pathlib
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile


HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
PROTOCOL_JSON = HERE / "exact_input_recovery_v1.json"
PROTOCOL_MD = HERE / "EXACT_INPUT_RECOVERY_V1.md"
SELECTION = HERE / "resource_panel_selection.json"
FILTER = HERE / "filter_contigs.py"
BOUNDED = HERE / "bounded_stage.py"
ORIGINAL_RUNNER = HERE / "run_resource_panel_isolate.py"
EXPERIMENT_ID = "N8_DSK_EXACT_INPUT_RECOVERY_V1"
WORKFLOW_FILE = "exact-input-recovery-v1.yml"
RELEASE_TAG = "experiment001-n8-exact-inputs-v1"
PROTECTED_SHA256 = {
    "experiments/001_gonococcus_eucast_vs_clsi/EXACT_INPUT_RECOVERY_V1.md": "0dbd315208bc6668c1f956e2ceaf717c769492fe8d0352e9b663e4b4dfd24bb2",
    "experiments/001_gonococcus_eucast_vs_clsi/exact_input_recovery_v1.json": "382a93fdaba8fff3ac74b3d7e8adef7ce108fb979812efec2305d4651c5d77a7",
    "experiments/001_gonococcus_eucast_vs_clsi/run_resource_panel_isolate.py": "1af9392259bb7e132c52f7c9c22eca76d5a7b64e874e8a3a739fe66ad9087f4e",
    "experiments/001_gonococcus_eucast_vs_clsi/filter_contigs.py": "2cb8e2e46e494737de52a2a31a9e6078e95ad09dcff780c46d77e89e27b47e16",
    "experiments/001_gonococcus_eucast_vs_clsi/bounded_stage.py": "4bfe89eeb03c144bbfe5030b16fa216afb695315a4e9ea7571f9da162228fd6b",
    "experiments/001_gonococcus_eucast_vs_clsi/resource_panel_selection.json": "af7efa9e53c129788844dea0f77af6f1152840467e1d649059fa25407f4bb1a5",
    ".github/workflows/experiment001-n8.yml": "0dc37a81f35af557e9a5bd61214373b8010115a32d625cd719b0928695c5b6f8",
}
TOOL_SOURCES = {
    "spades": ("https://github.com/ablab/spades/releases/download/v4.3.0/SPAdes-4.3.0-Linux.tar.gz", "e88a8c533c8614dd4b7c5788cfcd46427848a0575267f97c690a75fd2a343034"),
    "quast": ("https://github.com/ablab/quast/releases/download/quast_5.2.0/quast-5.2.0.tar.gz", "ccd911087cfa254ad4b8eadac4f95d4685e44c3996f5516b8e0ce6f7cfa7e0db"),
    "dsk": ("https://github.com/GATB/dsk/releases/download/v2.3.3/dsk-v2.3.3-bin-Linux.tar.gz", "626a4663f70323a80834c013f1d9dcb4a3b3a73a1c9ab5da95a013783d81b0f6"),
}
FAILURES = {
    "FAIL_INPUT_INTEGRITY", "FAIL_TOOL_INTEGRITY", "FAIL_SPADES_TIMEOUT",
    "FAIL_SPADES_NONZERO", "FAIL_SPADES_OUTPUT", "FAIL_QC_STAGE",
    "FAIL_DSK_STAGE", "FAIL_DSK_EQUALITY", "FAIL_EXPECTED_IDENTITY_MISMATCH",
    "FAIL_EVIDENCE_RETENTION", "FAIL_PREFLIGHT_INFRASTRUCTURE",
}


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def write_json(path: pathlib.Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def digest(path: pathlib.Path, algorithm: str = "sha256") -> str:
    h = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_protocol() -> dict:
    observed = {name: digest(REPO / name) for name in PROTECTED_SHA256}
    mismatches = {name: {"expected": PROTECTED_SHA256[name], "observed": value}
                  for name, value in observed.items() if value != PROTECTED_SHA256[name]}
    if mismatches:
        raise RuntimeError(f"protected file hash mismatch: {mismatches}")
    value = json.loads(PROTOCOL_JSON.read_text(encoding="utf-8"))
    if value.get("experiment_id") != EXPERIMENT_ID or value.get("status") != "FROZEN_NOT_EXECUTED":
        raise RuntimeError("unexpected frozen protocol identity or status")
    phase = value["phase_b_regeneration"]
    invariant_checks = {
        "runner": phase["runner"] == "public standard ubuntu-24.04 x64",
        "larger_runner": phase["larger_runner_allowed"] is False,
        "parallel": phase["max_parallel_isolates"] == 4,
        "whole_job": phase["whole_job_wall_seconds_per_isolate"] == 4500,
        "sampling": phase["sample_interval_seconds"] == 0.5,
        "termination": phase["termination"] == {"first": "SIGTERM", "grace_seconds": 2, "then": "SIGKILL"},
        "one_attempt": phase["one_attempt_per_missing_isolate"] is True and phase["automatic_scientific_retry"] is False,
        "spades": phase["spades"] == {"mode": "default paired-read", "threads": 2, "memory_parameter_gib": 8, "wall_seconds": 2700},
        "filter": phase["filter"] == {"minimum_length_bp": 200, "minimum_spades_header_coverage": 10},
        "quast": phase["quast"] == {"minimum_contig_bp": 200, "threads": 2, "wall_seconds": 300, "flags": ["--no-plots", "--no-html", "--no-icarus"]},
        "dsk": phase["dsk"] == {"kmer_size": 31, "abundance_min": 1, "max_memory": 8000, "wall_seconds": 900},
        "dsk2ascii": phase["dsk2ascii"] == {"wall_seconds": 300},
        "oracle": phase["oracle"] == {"canonical_order": "A<C<T<G", "reverse_complement": True, "required_missing": 0, "required_extra": 0, "required_duplicates": 0, "required_abundance_mismatches": 0},
        "no_seer": phase["seer_allowed"] is False,
        "retention": value["evidence_retention"]["actions_retention_days"] == 90 and value["evidence_retention"]["pass_release_tag"] == RELEASE_TAG,
    }
    for name, (_, archive_sha256) in TOOL_SOURCES.items():
        invariant_checks[f"tool_{name}"] = phase["tools"][name]["archive_sha256"] == archive_sha256
    if not all(invariant_checks.values()):
        raise RuntimeError(f"harness/protocol invariant mismatch: {invariant_checks}")
    return value


def targets() -> dict[str, dict]:
    return {row["rank"]: row for row in load_protocol()["targets"]}


def api_json(url: str, token: str) -> tuple[int, dict | None, dict]:
    request = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "amr-validation-replay/1",
    })
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.status, json.load(response), dict(response.headers)
    except urllib.error.HTTPError as error:
        body = error.read()
        try:
            payload = json.loads(body)
        except (ValueError, UnicodeDecodeError):
            payload = {"message": body[:1000].decode("utf-8", "replace")}
        return error.code, payload, dict(error.headers)


def api_download(url: str, token: str, destination: pathlib.Path) -> tuple[int, dict]:
    request = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "amr-validation-replay/1",
    })
    try:
        with urllib.request.urlopen(request, timeout=120) as response, destination.open("wb") as output:
            shutil.copyfileobj(response, output, length=8 * 1024 * 1024)
            return response.status, dict(response.headers)
    except urllib.error.HTTPError as error:
        return error.code, dict(error.headers)


def safe_extract_zip(archive: pathlib.Path, destination: pathlib.Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    root = destination.resolve()
    with zipfile.ZipFile(archive) as handle:
        for info in handle.infolist():
            target = (destination / info.filename).resolve()
            if root != target and root not in target.parents:
                raise RuntimeError(f"unsafe ZIP member: {info.filename}")
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with handle.open(info) as source, target.open("wb") as output:
                    shutil.copyfileobj(source, output)


def safe_extract_tar(archive: pathlib.Path, destination: pathlib.Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "r:gz") as handle:
        handle.extractall(destination, filter="data")


def inspect_dsk(path: pathlib.Path) -> dict:
    rows = 0
    duplicates = 0
    seen: set[str] = set()
    parse_valid = True
    parse_error = None
    try:
        with path.open("rt", encoding="ascii", newline="") as handle:
            for physical, line in enumerate(handle, 1):
                rows += 1
                fields = line.split()
                if len(fields) != 2 or len(fields[0]) != 31 or any(base not in "ACGT" for base in fields[0]):
                    raise ValueError(f"invalid two-field 31-mer row at line {physical}")
                int(fields[1])
                if fields[0] in seen:
                    duplicates += 1
                seen.add(fields[0])
    except (OSError, UnicodeError, ValueError) as error:
        parse_valid = False
        parse_error = str(error)
    return {
        "path": str(path), "bytes": path.stat().st_size, "sha256": digest(path),
        "physical_rows": rows, "parse_valid": parse_valid,
        "parse_error": parse_error, "duplicate_rows": duplicates,
    }


def exact_identity(observed: dict, target: dict) -> bool:
    return (observed["bytes"] == target["expected_dsk_ascii_bytes"] and
            observed["sha256"] == target["expected_dsk_ascii_sha256"] and
            observed["physical_rows"] == target["expected_dsk_rows"] and
            observed["parse_valid"] is True and observed["duplicate_rows"] == 0)


def dispatch_guard(token: str) -> dict:
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    run_id = int(os.environ.get("GITHUB_RUN_ID", "0"))
    attempt = int(os.environ.get("GITHUB_RUN_ATTEMPT", "0"))
    if not repo or not token or run_id <= 0 or attempt != 1:
        return {"passed": False, "reason": "missing context/token or run attempt is not 1", "attempt": attempt}
    workflow = urllib.parse.quote(WORKFLOW_FILE, safe="")
    status, payload, _ = api_json(
        f"https://api.github.com/repos/{repo}/actions/workflows/{workflow}/runs?event=workflow_dispatch&per_page=100",
        token,
    )
    if status != 200 or payload is None:
        return {"passed": False, "reason": f"workflow-run query returned HTTP {status}"}
    earlier = sorted(int(row["id"]) for row in payload.get("workflow_runs", []) if int(row["id"]) != run_id)
    release_status, release, _ = api_json(f"https://api.github.com/repos/{repo}/releases/tags/{RELEASE_TAG}", token)
    release_absent = release_status == 404
    return {
        "passed": not earlier and release_absent,
        "current_run_id": run_id, "run_attempt": attempt, "prior_run_ids": earlier,
        "release_query_status": release_status,
        "release_absent_before_execution": release_absent,
        "release_id_if_present": None if release is None else release.get("id"),
    }


def command_prepare(args: argparse.Namespace) -> int:
    protocol = load_protocol()
    root = pathlib.Path(args.root).resolve()
    phase = root / "phase_a"
    phase.mkdir(parents=True, exist_ok=True)
    token = os.environ.get("GITHUB_TOKEN", "")
    guard = dispatch_guard(token)
    write_json(phase / "dispatch_guard.json", guard)
    if not guard["passed"]:
        write_json(phase / "outcome.json", {"experiment_id": EXPERIMENT_ID, "state": "FAIL_PREFLIGHT_INFRASTRUCTURE", "guard": guard})
        return 2
    repo = os.environ["GITHUB_REPOSITORY"]
    manifest = {"schema": "amr-n8-dsk-phase-a-v1", "experiment_id": EXPERIMENT_ID,
                "created_at_utc": now(), "biological_computation_performed": False, "isolates": []}
    for target in protocol["targets"]:
        rank = target["rank"]
        record = {"rank": rank, "isolate": target["isolate"], "artifact_id": target["historical_artifact_id"]}
        metadata_url = f"https://api.github.com/repos/{repo}/actions/artifacts/{target['historical_artifact_id']}"
        status, payload, _ = api_json(metadata_url, token)
        record["metadata_query"] = {"url": metadata_url, "http_status": status, "payload": payload}
        record["state"] = "UNAVAILABLE_FOR_EXACT_COPY"
        if status == 200 and payload and not payload.get("expired", False):
            archive = phase / "queries" / f"{rank}.zip"
            archive.parent.mkdir(parents=True, exist_ok=True)
            download_status, _ = api_download(payload["archive_download_url"], token, archive)
            record["download_http_status"] = download_status
            if download_status == 200:
                extracted = phase / "queries" / rank
                safe_extract_zip(archive, extracted)
                hits = [path for path in extracted.rglob("kmers.txt") if path.is_file()]
                record["candidate_count"] = len(hits)
                record["candidates"] = []
                for candidate in hits:
                    checked = inspect_dsk(candidate)
                    checked["source"] = f"github-actions-artifact:{target['historical_artifact_id']}"
                    checked["exact_match"] = exact_identity(checked, target)
                    record["candidates"].append(checked)
                accepted = [candidate for candidate, checked in zip(hits, record["candidates"]) if checked["exact_match"]]
                if len(accepted) == 1 and len(hits) == 1:
                    destination = phase / "exact" / rank / "kmers.txt"
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(accepted[0], destination)
                    record["state"] = "RECOVERED_EXACT"
                    record["accepted"] = inspect_dsk(destination)
                elif hits:
                    record["state"] = "REJECTED_CANDIDATE_MISMATCH"
            archive.unlink(missing_ok=True)
        manifest["isolates"].append(record)
    manifest["missing_subset"] = [row["rank"] for row in manifest["isolates"] if row["state"] != "RECOVERED_EXACT"]
    manifest["recovered_subset"] = [row["rank"] for row in manifest["isolates"] if row["state"] == "RECOVERED_EXACT"]
    manifest["subset_frozen_before_fastq_download"] = True
    write_json(phase / "phase_a_manifest.json", manifest)
    write_json(phase / "outcome.json", {"experiment_id": EXPERIMENT_ID, "state": "PHASE_A_COMPLETE", "missing_subset": manifest["missing_subset"], "biological_computation_performed": False})
    return 0


def environment_record() -> dict:
    disk = shutil.disk_usage(pathlib.Path(os.environ.get("RUNNER_TEMP", "/tmp")))
    ram_kib = None
    for line in pathlib.Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
        if line.startswith("MemTotal:"):
            ram_kib = int(line.split()[1])
            break
    cpu_model = "UNKNOWN"
    for line in pathlib.Path("/proc/cpuinfo").read_text(encoding="utf-8").splitlines():
        if line.startswith("model name"):
            cpu_model = line.split(":", 1)[1].strip()
            break
    packages = {}
    for package in ("curl", "libboost-program-options-dev", "libgzstream-dev", "zlib1g-dev", "python3"):
        completed = subprocess.run(["dpkg-query", "-W", "-f=${Version}", package], text=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        packages[package] = completed.stdout.strip() if completed.returncode == 0 else "NOT_INSTALLED"
    runner_candidates = sorted(path for path in pathlib.Path("/home/runner/runners").glob("*/bin/Runner.Listener"))
    runner_versions = []
    for candidate in runner_candidates:
        try:
            completed = subprocess.run([str(candidate), "--version"], text=True, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT, timeout=10)
            runner_versions.append({"path": str(candidate), "exit_code": completed.returncode,
                                    "reported_version": completed.stdout.strip()})
        except (OSError, subprocess.TimeoutExpired) as error:
            runner_versions.append({"path": str(candidate), "error": str(error)})
    return {
        "recorded_at_utc": now(), "runner_name": os.environ.get("RUNNER_NAME"),
        "runner_os": os.environ.get("RUNNER_OS"), "runner_arch": os.environ.get("RUNNER_ARCH"),
        "image_os": os.environ.get("ImageOS"), "image_version": os.environ.get("ImageVersion"),
        "image_provisioner": os.environ.get("ImageProvisioner", "UNKNOWN_NOT_EXPOSED"),
        "actions_runner_version_env": os.environ.get("ACTIONS_RUNNER_VERSION", "UNKNOWN_NOT_EXPOSED"),
        "actions_runner_listener_versions": runner_versions,
        "architecture": platform.machine(), "cpu_model": cpu_model,
        "cpu_count": os.cpu_count(), "total_ram_kib": ram_kib,
        "filesystem_total_bytes": disk.total, "filesystem_free_bytes": disk.free,
        "repository_commit": os.environ.get("GITHUB_SHA"),
        "repository": os.environ.get("GITHUB_REPOSITORY"), "workflow_ref": os.environ.get("GITHUB_WORKFLOW_REF"),
        "workflow_run_id": os.environ.get("GITHUB_RUN_ID"), "workflow_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "protected_sha256": {name: digest(REPO / name) for name in PROTECTED_SHA256},
        "installed_package_versions": packages, "python": sys.version, "platform": platform.platform(),
    }


def download_file(url: str, destination: pathlib.Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "amr-validation-replay/1"})
    with urllib.request.urlopen(request, timeout=120) as response, destination.open("wb") as output:
        shutil.copyfileobj(response, output, length=8 * 1024 * 1024)


def run_checked(command: list[str], log: pathlib.Path | None = None) -> None:
    if log is None:
        subprocess.run(command, check=True)
    else:
        with log.open("wb") as output:
            subprocess.run(command, check=True, stdout=output, stderr=subprocess.STDOUT)


def install_tools(root: pathlib.Path, evidence: pathlib.Path) -> dict:
    tools = root / "tools"
    tools.mkdir(parents=True, exist_ok=True)
    records = {}
    run_checked(["sudo", "apt-get", "update"], evidence / "apt-update.log")
    run_checked(["sudo", "apt-get", "install", "-y", "libboost-program-options-dev", "libgzstream-dev", "zlib1g-dev"], evidence / "apt-install.log")
    for name, (url, expected) in TOOL_SOURCES.items():
        archive = tools / f"{name}.tar.gz"
        download_file(url, archive)
        observed = digest(archive)
        records[name] = {"url": url, "expected_sha256": expected, "observed_sha256": observed, "exact_match": observed == expected}
        if observed != expected:
            raise RuntimeError(f"{name} archive SHA-256 mismatch")
        safe_extract_tar(archive, tools)
    write_json(evidence / "tool_integrity.json", records)
    return records


def stage(root: pathlib.Path, name: str, timeout: int, watch: pathlib.Path, command: list[str]) -> dict:
    record = root / "evidence" / f"{name}.json"
    completed = subprocess.run([
        sys.executable, str(BOUNDED), "--name", name, "--cwd", str(root),
        "--watch-dir", str(watch), "--evidence", str(record), "--timeout", str(timeout), "--", *map(str, command)
    ])
    value = json.loads(record.read_text(encoding="utf-8")) if record.exists() else {}
    if completed.returncode != 0:
        raise StageFailure(name, value, completed.returncode)
    return value


class StageFailure(Exception):
    def __init__(self, name: str, record: dict, returncode: int):
        super().__init__(f"{name} failed with {returncode}")
        self.name, self.record, self.returncode = name, record, returncode


RANK_ORDER = {"A": 0, "C": 1, "T": 2, "G": 3}
COMPLEMENT = str.maketrans("ACTG", "TGAC")


def canonical(word: str) -> str:
    reverse = word.translate(COMPLEMENT)[::-1]
    key = lambda text: tuple(RANK_ORDER[base] for base in text)
    return min((word, reverse), key=key)


def verify_dsk(fasta: pathlib.Path, ascii_path: pathlib.Path, output: pathlib.Path) -> dict:
    independent: dict[str, int] = collections.defaultdict(int)
    sequence: list[str] = []
    def consume() -> None:
        joined = "".join(sequence).upper()
        for offset in range(max(0, len(joined) - 30)):
            word = joined[offset:offset + 31]
            if len(word) == 31 and all(base in RANK_ORDER for base in word):
                independent[canonical(word)] += 1
    with fasta.open(encoding="ascii") as handle:
        for line in handle:
            if line.startswith(">"):
                consume(); sequence.clear()
            else:
                sequence.append(line.strip())
        consume()
    observed: dict[str, int] = {}
    duplicates = 0
    with ascii_path.open(encoding="ascii") as handle:
        for number, line in enumerate(handle, 1):
            fields = line.split()
            if len(fields) != 2 or len(fields[0]) != 31 or any(base not in RANK_ORDER for base in fields[0]):
                raise ValueError(f"invalid DSK row {number}")
            if fields[0] in observed:
                duplicates += 1
            observed[fields[0]] = int(fields[1])
    missing = set(independent) - set(observed)
    extra = set(observed) - set(independent)
    abundance = sum(independent[kmer] != value for kmer, value in observed.items() if kmer in independent)
    result = {"canonical_order": "A<C<T<G", "reverse_complement": True,
              "independent_canonical_31mers": len(independent), "observed_rows": len(observed),
              "missing": len(missing), "extra": len(extra), "duplicates": duplicates,
              "abundance_mismatches": abundance, "filtered_fasta_sha256": digest(fasta),
              "dsk_ascii_bytes": ascii_path.stat().st_size, "dsk_ascii_sha256": digest(ascii_path)}
    write_json(output, result)
    return result


def selection_for(rank: str) -> dict:
    rows = json.loads(SELECTION.read_text(encoding="utf-8"))
    return next(row for row in rows if row["label"] == rank)


def initial_outcome(rank: str, isolate: str) -> dict:
    return {"schema": "amr-n8-dsk-exact-input-recovery-isolate-v1", "experiment_id": EXPERIMENT_ID,
            "rank": rank, "isolate": isolate, "state": "INCOMPLETE", "started_at_utc": now(),
            "finished_at_utc": None, "one_attempt": True, "no_retry_occurred": True,
            "corrected_seer_executed": False, "full_cohort_executed": False, "model_training_executed": False}


def command_isolate(args: argparse.Namespace) -> int:
    protocol = load_protocol()
    target = next(row for row in protocol["targets"] if row["rank"] == args.rank)
    root = pathlib.Path(args.root).resolve()
    phase = pathlib.Path(args.phase_a).resolve()
    evidence = root / "evidence"; output = root / "accepted" / args.rank
    evidence.mkdir(parents=True, exist_ok=True); output.mkdir(parents=True, exist_ok=True)
    outcome = initial_outcome(args.rank, target["isolate"])
    write_json(evidence / "outcome.json", outcome)
    def marker(stage_name: str) -> None:
        write_json(evidence / "current_stage.json", {"stage": stage_name, "recorded_at_utc": now()})
    try:
        marker("phase_a_decision")
        manifest = json.loads((phase / "phase_a_manifest.json").read_text(encoding="utf-8"))
        phase_row = next(row for row in manifest["isolates"] if row["rank"] == args.rank)
        if not manifest.get("subset_frozen_before_fastq_download"):
            raise RuntimeError("Phase A subset is not frozen")
        write_json(evidence / "phase_a_decision.json", phase_row)
        if phase_row["state"] == "RECOVERED_EXACT":
            source = phase / "exact" / args.rank / "kmers.txt"
            shutil.copyfile(source, output / "kmers.txt")
            checked = inspect_dsk(output / "kmers.txt")
            if not exact_identity(checked, target):
                raise RuntimeError("recovered exact file failed read-back")
            outcome.update(state="RECOVERED_EXACT", exact_identity=checked, finished_at_utc=now())
            write_json(evidence / "outcome.json", outcome)
            return 0
        if args.rank not in manifest["missing_subset"]:
            raise RuntimeError("rank absent from frozen regeneration subset")
        marker("environment_preflight")
        write_json(evidence / "environment_preflight.json", environment_record())
        marker("tool_setup")
        try:
            install_tools(root, evidence)
        except Exception as error:
            outcome.update(state="FAIL_TOOL_INTEGRITY", error=f"{type(error).__name__}: {error}", finished_at_utc=now())
            write_json(evidence / "outcome.json", outcome)
            return 2
        write_json(evidence / "environment_preflight.json", environment_record())
        row = selection_for(args.rank)
        if row["run_accession"] != target["isolate"]:
            raise RuntimeError("selection/target isolate mismatch")
        work = root / "work" / target["isolate"]; work.mkdir(parents=True, exist_ok=True)
        marker("input_download_and_integrity")
        observed_inputs = []
        for index, frozen in enumerate(target["fastqs"]):
            url = "https://" + row["fastq_ftp"].split(";")[index]
            path = work / frozen["name"]
            download_file(url, path)
            observed = {"name": path.name, "url": url, "bytes": path.stat().st_size, "md5": digest(path, "md5")}
            observed["exact_match"] = observed["bytes"] == frozen["bytes"] and observed["md5"] == frozen["md5"]
            observed_inputs.append(observed)
        write_json(evidence / "input_integrity.json", observed_inputs)
        if not all(row["exact_match"] for row in observed_inputs):
            outcome.update(state="FAIL_INPUT_INTEGRITY", finished_at_utc=now())
            write_json(evidence / "outcome.json", outcome); return 2
        tools = root / "tools"; spades = work / "spades"; spades.mkdir()
        marker("spades")
        try:
            stage(root, "spades", 2700, spades, [str(tools / "SPAdes-4.3.0-Linux/bin/spades.py"),
                  "-1", str(work / target["fastqs"][0]["name"]), "-2", str(work / target["fastqs"][1]["name"]),
                  "-o", str(spades), "-t", "2", "-m", "8"])
        except StageFailure as failure:
            outcome.update(state="FAIL_SPADES_TIMEOUT" if failure.record.get("timed_out") else "FAIL_SPADES_NONZERO",
                           stage_record=failure.record, finished_at_utc=now())
            write_json(evidence / "outcome.json", outcome); return 2
        contigs = spades / "contigs.fasta"
        if not contigs.is_file() or contigs.stat().st_size == 0:
            outcome.update(state="FAIL_SPADES_OUTPUT", finished_at_utc=now()); write_json(evidence / "outcome.json", outcome); return 2
        filtered = work / "filtered.fasta"; filter_metrics = evidence / "filter.json"
        marker("qc")
        try:
            run_checked([sys.executable, str(FILTER), str(contigs), str(filtered), str(filter_metrics)], evidence / "filter.log")
            quast = work / "quast"; quast.mkdir()
            stage(root, "quast", 300, quast, [sys.executable, str(tools / "quast-5.2.0/quast.py"),
                  "--min-contig", "200", "--no-plots", "--no-html", "--no-icarus", "-t", "2",
                  "-l", "raw,filtered", "-o", str(quast), str(contigs), str(filtered)])
        except (subprocess.CalledProcessError, StageFailure, OSError, ValueError) as error:
            outcome.update(state="FAIL_QC_STAGE", error=str(error), finished_at_utc=now()); write_json(evidence / "outcome.json", outcome); return 2
        dsk_tmp = work / "dsk_tmp"; dsk_tmp.mkdir()
        marker("dsk")
        try:
            stage(root, "dsk", 900, dsk_tmp, [str(tools / "dsk-v2.3.3-bin-Linux/bin/dsk"), "-file", str(filtered),
                  "-kmer-size", "31", "-abundance-min", "1", "-out", str(work / "kmers"),
                  "-out-tmp", str(dsk_tmp), "-max-memory", "8000"])
            stage(root, "dsk2ascii", 300, work, [str(tools / "dsk-v2.3.3-bin-Linux/bin/dsk2ascii"),
                  "-file", str(work / "kmers.h5"), "-out", str(work / "kmers.txt")])
        except (StageFailure, OSError) as error:
            outcome.update(state="FAIL_DSK_STAGE", error=str(error), finished_at_utc=now()); write_json(evidence / "outcome.json", outcome); return 2
        marker("independent_oracle")
        verification = verify_dsk(filtered, work / "kmers.txt", evidence / "independent_verification.json")
        if any(verification[key] for key in ("missing", "extra", "duplicates", "abundance_mismatches")):
            outcome.update(state="FAIL_DSK_EQUALITY", verification=verification, finished_at_utc=now()); write_json(evidence / "outcome.json", outcome); return 2
        identity = inspect_dsk(work / "kmers.txt")
        identity["filtered_fasta_sha256"] = digest(filtered)
        if not exact_identity(identity, target) or identity["filtered_fasta_sha256"] != target["expected_filtered_fasta_sha256"]:
            outcome.update(state="FAIL_EXPECTED_IDENTITY_MISMATCH", exact_identity=identity, verification=verification, finished_at_utc=now())
            write_json(evidence / "outcome.json", outcome); return 2
        shutil.copyfile(work / "kmers.txt", output / "kmers.txt")
        shutil.copyfile(filtered, output / "filtered.fasta")
        marker("complete")
        outcome.update(state="REGENERATED_EXACT", exact_identity=identity, verification=verification, finished_at_utc=now())
        write_json(evidence / "outcome.json", outcome)
        for path in work.glob("*.fastq.gz"):
            path.unlink()
        return 0
    except Exception as error:
        outcome.update(state="FAIL_PREFLIGHT_INFRASTRUCTURE", error=f"{type(error).__name__}: {error}", finished_at_utc=now())
        write_json(evidence / "outcome.json", outcome)
        return 2


def recursive_ledger(root: pathlib.Path, output: pathlib.Path) -> dict:
    excluded = output.resolve()
    files = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.resolve() != excluded:
            files.append({"path": str(path.relative_to(root)), "bytes": path.stat().st_size, "sha256": digest(path)})
    value = {"root": str(root), "file_count": len(files), "total_bytes": sum(row["bytes"] for row in files), "files": files}
    write_json(output, value)
    return value


def command_finalize_isolate(args: argparse.Namespace) -> int:
    root = pathlib.Path(args.root).resolve(); evidence = root / "evidence"; evidence.mkdir(parents=True, exist_ok=True)
    outcome_path = evidence / "outcome.json"
    if not outcome_path.exists() or json.loads(outcome_path.read_text()).get("state") == "INCOMPLETE":
        rank = args.rank; target = targets()[rank]
        outcome = initial_outcome(rank, target["isolate"])
        try:
            current = json.loads((evidence / "current_stage.json").read_text(encoding="utf-8")).get("stage")
        except (OSError, ValueError):
            current = "unknown"
        classification = {
            "tool_setup": "FAIL_TOOL_INTEGRITY",
            "input_download_and_integrity": "FAIL_INPUT_INTEGRITY",
            "spades": "FAIL_SPADES_TIMEOUT",
            "qc": "FAIL_QC_STAGE",
            "dsk": "FAIL_DSK_STAGE",
            "independent_oracle": "FAIL_DSK_EQUALITY",
        }.get(current, "FAIL_PREFLIGHT_INFRASTRUCTURE")
        outcome.update(state=classification, current_stage=current,
                       error="execution terminated before a classified outcome", finished_at_utc=now())
        write_json(outcome_path, outcome)
    discarded = []
    for path in root.rglob("*.fastq.gz"):
        if path.is_file():
            discarded.append({"path": str(path.relative_to(root)), "bytes": path.stat().st_size,
                              "md5": digest(path, "md5"), "sha256": digest(path)})
            path.unlink()
    write_json(evidence / "discarded_raw_fastqs.json", {"files": discarded})
    shutil.rmtree(root / "tools", ignore_errors=True)
    recursive_ledger(root, evidence / "recursive_ledger.json")
    return 0


def command_finalize_phase_a(args: argparse.Namespace) -> int:
    root = pathlib.Path(args.root).resolve(); phase = root / "phase_a"; phase.mkdir(parents=True, exist_ok=True)
    outcome = phase / "outcome.json"
    if not outcome.exists():
        write_json(outcome, {"experiment_id": EXPERIMENT_ID, "state": "FAIL_PREFLIGHT_INFRASTRUCTURE",
                            "error": "Phase A terminated before a classified outcome",
                            "biological_computation_performed": False})
    recursive_ledger(phase, phase / "recursive_ledger.json")
    return 0


def locate_isolate_artifacts(root: pathlib.Path) -> dict[str, pathlib.Path]:
    found = {}
    for outcome in root.rglob("outcome.json"):
        try:
            row = json.loads(outcome.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        rank = row.get("rank")
        if rank in targets():
            if rank in found:
                raise RuntimeError(f"duplicate outcome for {rank}")
            found[rank] = outcome.parent.parent
    return found


def command_audit(args: argparse.Namespace) -> int:
    source = pathlib.Path(args.source).resolve(); output = pathlib.Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    protocol = load_protocol(); roots = locate_isolate_artifacts(source)
    manifest = {"schema": "amr-n8-dsk-exact-input-set-v1", "experiment_id": EXPERIMENT_ID,
                "audited_at_utc": now(), "isolates": []}
    passed = set(roots) == set(targets())
    accepted = output / "release" / "accepted"; accepted.mkdir(parents=True, exist_ok=True)
    for target in protocol["targets"]:
        rank = target["rank"]; row = {"rank": rank, "isolate": target["isolate"]}
        if rank not in roots:
            row.update(state="MISSING", exact=False); passed = False
        else:
            outcome = json.loads((roots[rank] / "evidence" / "outcome.json").read_text(encoding="utf-8"))
            candidate = roots[rank] / "accepted" / rank / "kmers.txt"
            row["state"] = outcome.get("state")
            row["provenance"] = outcome
            if outcome.get("state") not in ("RECOVERED_EXACT", "REGENERATED_EXACT") or not candidate.is_file():
                row["exact"] = False; passed = False
            else:
                checked = inspect_dsk(candidate); row["identity"] = checked
                row["exact"] = exact_identity(checked, target)
                passed &= row["exact"]
                if row["exact"]:
                    destination = accepted / rank / "kmers.txt"; destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(candidate, destination)
        manifest["isolates"].append(row)
    manifest["exact_total_bytes"] = sum(row.get("identity", {}).get("bytes", 0) for row in manifest["isolates"])
    manifest["expected_total_bytes"] = protocol["expected_total_dsk_ascii_bytes"]
    passed &= manifest["exact_total_bytes"] == manifest["expected_total_bytes"]
    manifest["independent_audit_pass"] = bool(passed)
    write_json(output / "release" / "complete_manifest.json", manifest)
    if not passed:
        write_json(output / "outcome.json", {"experiment_id": EXPERIMENT_ID, "state": "FAIL_EXPECTED_IDENTITY_MISMATCH", "manifest": manifest})
        return 2
    bundle = output / "experiment001-n8-exact-inputs-v1.tar.gz"
    with tarfile.open(bundle, "w:gz", format=tarfile.PAX_FORMAT) as archive:
        for path in sorted((output / "release").rglob("*")):
            if path.is_file():
                info = archive.gettarinfo(str(path), arcname=str(path.relative_to(output / "release")))
                info.uid = info.gid = 0; info.uname = info.gname = ""; info.mtime = 0
                with path.open("rb") as handle:
                    archive.addfile(info, handle)
    write_json(output / "bundle_ledger.json", {"path": bundle.name, "bytes": bundle.stat().st_size,
               "sha256": digest(bundle), "uncompressed_exact_dsk_bytes": manifest["exact_total_bytes"], "file_count": 8})
    write_json(output / "outcome.json", {"experiment_id": EXPERIMENT_ID, "state": "AUDIT_PASS_RELEASE_NOT_YET_READ_BACK", "independent_audit_pass": True})
    return 0


def command_audit_release(args: argparse.Namespace) -> int:
    archive = pathlib.Path(args.archive).resolve(); expected_ledger = json.loads(pathlib.Path(args.ledger).read_text())
    output = pathlib.Path(args.output).resolve(); output.mkdir(parents=True, exist_ok=True)
    asset_api = json.loads(pathlib.Path(args.asset_api).read_text(encoding="utf-8"))
    record = {"archive_bytes": archive.stat().st_size, "archive_sha256": digest(archive),
              "expected_archive_bytes": expected_ledger["bytes"], "expected_archive_sha256": expected_ledger["sha256"]}
    record["archive_digest_exact"] = record["archive_bytes"] == record["expected_archive_bytes"] and record["archive_sha256"] == record["expected_archive_sha256"]
    extracted = output / "readback"; safe_extract_tar(archive, extracted)
    manifest = json.loads((extracted / "complete_manifest.json").read_text(encoding="utf-8"))
    exact = record["archive_digest_exact"] and manifest.get("independent_audit_pass") is True
    for target in load_protocol()["targets"]:
        checked = inspect_dsk(extracted / "accepted" / target["rank"] / "kmers.txt")
        exact &= exact_identity(checked, target)
    assets = [row for row in asset_api.get("assets", []) if row.get("name") == archive.name]
    record["release_asset_api_count"] = len(assets)
    record["release_asset_api"] = assets[0] if len(assets) == 1 else None
    api_digest = None if len(assets) != 1 else assets[0].get("digest")
    record["release_api_digest_matches"] = api_digest in (None, f"sha256:{record['archive_sha256']}")
    exact &= len(assets) == 1 and int(assets[0]["id"]) == int(args.asset_id) and record["release_api_digest_matches"]
    record["contents_exact"] = bool(exact); record["release_asset_id"] = int(args.asset_id)
    record["release_tag"] = RELEASE_TAG; record["protocol_terminal_state"] = "PASS" if exact else "FAIL_EVIDENCE_RETENTION"
    record["acceptance_commit_pending"] = bool(exact)
    write_json(output / "release_readback.json", record)
    write_json(output / "outcome.json", {"experiment_id": EXPERIMENT_ID, "state": record["protocol_terminal_state"],
               "release_readback": record, "corrected_seer_n8_authorized": False,
               "full_1102_reconstruction_authorized": False, "model_training_authorized": False})
    return 0 if exact else 2


def command_finalize_final(args: argparse.Namespace) -> int:
    root = pathlib.Path(args.root).resolve(); root.mkdir(parents=True, exist_ok=True)
    outcome = root / "outcome.json"
    try:
        value = json.loads(outcome.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        value = {"experiment_id": EXPERIMENT_ID, "state": "INCOMPLETE"}
    if value.get("state") not in FAILURES | {"PASS"}:
        value.update(state="FAIL_EVIDENCE_RETENTION", finished_at_utc=now(),
                     error="Final exact audit, release creation, or release read-back did not complete")
        write_json(outcome, value)
    recursive_ledger(root, root / "final_recursive_ledger.json")
    return 0


def command_self_test(_: argparse.Namespace) -> int:
    load_protocol()
    with tempfile.TemporaryDirectory() as temporary:
        root = pathlib.Path(temporary)
        valid = root / "valid.txt"; valid.write_text("A" * 31 + " 2\n" + "C" * 31 + " 1\n", encoding="ascii")
        checked = inspect_dsk(valid)
        assert checked["parse_valid"] and checked["physical_rows"] == 2 and checked["duplicate_rows"] == 0
        duplicate = root / "duplicate.txt"; duplicate.write_text(("A" * 31 + " 2\n") * 2, encoding="ascii")
        assert inspect_dsk(duplicate)["duplicate_rows"] == 1
        fasta = root / "tiny.fasta"; fasta.write_text(">x\n" + "ACGT" * 10 + "\n", encoding="ascii")
        observed = root / "observed.txt"
        counts = collections.Counter(canonical(("ACGT" * 10)[i:i + 31]) for i in range(10))
        observed.write_text("".join(f"{key} {value}\n" for key, value in counts.items()), encoding="ascii")
        result = verify_dsk(fasta, observed, root / "verification.json")
        assert result["missing"] == result["extra"] == result["duplicates"] == result["abundance_mismatches"] == 0
        archive = root / "safe.tar.gz"
        with tarfile.open(archive, "w:gz") as handle:
            handle.add(valid, arcname="accepted/min/kmers.txt")
        safe_extract_tar(archive, root / "extract")
    print(json.dumps({"self_test": "PASS", "network_used": False, "biological_data_used": False}))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    commands = result.add_subparsers(dest="command", required=True)
    p = commands.add_parser("prepare"); p.add_argument("--root", required=True); p.set_defaults(function=command_prepare)
    p = commands.add_parser("isolate"); p.add_argument("--rank", required=True); p.add_argument("--root", required=True); p.add_argument("--phase-a", required=True); p.set_defaults(function=command_isolate)
    p = commands.add_parser("finalize-isolate"); p.add_argument("--rank", required=True); p.add_argument("--root", required=True); p.set_defaults(function=command_finalize_isolate)
    p = commands.add_parser("finalize-phase-a"); p.add_argument("--root", required=True); p.set_defaults(function=command_finalize_phase_a)
    p = commands.add_parser("audit"); p.add_argument("--source", required=True); p.add_argument("--output", required=True); p.set_defaults(function=command_audit)
    p = commands.add_parser("audit-release"); p.add_argument("--archive", required=True); p.add_argument("--ledger", required=True); p.add_argument("--asset-api", required=True); p.add_argument("--asset-id", required=True); p.add_argument("--output", required=True); p.set_defaults(function=command_audit_release)
    p = commands.add_parser("finalize-final"); p.add_argument("--root", required=True); p.set_defaults(function=command_finalize_final)
    p = commands.add_parser("self-test"); p.set_defaults(function=command_self_test)
    return result


if __name__ == "__main__":
    arguments = parser().parse_args()
    raise SystemExit(arguments.function(arguments))
