#!/usr/bin/env python3
"""Fail-closed support harness for corrected-SEER n=8 V3."""

import argparse
import hashlib
import json
import os
import pathlib
import platform
import shutil
import subprocess
import tarfile
import tempfile
import urllib.parse

import exact_input_recovery_v1 as utility

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
PROTOCOL_FILE = HERE / "corrected_seer_n8_combine_v3.json"
EXPERIMENT = "CORRECTED_SEER_N8_COMBINE_V3"
WORKFLOW = "corrected-seer-n8-combine-v3.yml"
RELEASE_TAG = "experiment001-corrected-seer-n8-v3"
ASSET_NAME = "experiment001-corrected-seer-n8-v3.tar.gz"
SOURCE_URL = "https://github.com/johnlees/seer/archive/a6bd405754726467a93f39820fb4719457395ae7.tar.gz"
PROTECTED = {
    "experiments/001_gonococcus_eucast_vs_clsi/CORRECTED_SEER_N8_COMBINE_V3.md":
        "38d59850e30d0e17eadbcd10ea010e60485a6c39324f0b5f874841118a8543ee",
    "experiments/001_gonococcus_eucast_vs_clsi/corrected_seer_n8_combine_v3.json":
        "4c2de9dce67b565bc59aa12650877daa3f44e0a8efa8f541f2c3f64a4fdce883",
}


def write_json(path, value):
    utility.write_json(pathlib.Path(path), value)


def sha256(path):
    return utility.digest(pathlib.Path(path))


def protocol():
    mismatches = {}
    for relative, expected in PROTECTED.items():
        observed = sha256(REPO / relative)
        if observed != expected:
            mismatches[relative] = {"expected": expected, "observed": observed}
    if mismatches:
        raise RuntimeError(f"protected protocol mismatch: {mismatches}")
    value = json.loads(PROTOCOL_FILE.read_text())
    if value["experiment_id"] != EXPERIMENT or value["status"] != "FROZEN_NOT_EXECUTED":
        raise RuntimeError("unexpected protocol identity")
    return value


def git_blob(path):
    data = pathlib.Path(path).read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def inspect(path):
    path = pathlib.Path(path)
    rows = malformed = 0
    with path.open(encoding="ascii", newline="") as handle:
        for line in handle:
            rows += 1
            fields = line.split()
            if len(fields) != 2 or len(fields[0]) != 31 or any(x not in "ACGT" for x in fields[0]):
                malformed += 1
                continue
            try:
                if int(fields[1]) <= 0:
                    malformed += 1
            except ValueError:
                malformed += 1
    return {"rows": rows, "bytes": path.stat().st_size, "sha256": sha256(path), "malformed_rows": malformed}


def exact(observed, frozen):
    return (observed["rows"] == frozen["rows"] and
            observed["bytes"] == frozen["bytes"] and
            observed["sha256"] == frozen["sha256"] and
            observed["malformed_rows"] == 0)


def guard(token):
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    run_id = int(os.environ.get("GITHUB_RUN_ID", "0"))
    attempt = int(os.environ.get("GITHUB_RUN_ATTEMPT", "0"))
    if not repository or not token or not run_id or attempt != 1:
        return {"passed": False, "reason": "missing run context or attempt is not 1"}
    encoded = urllib.parse.quote(WORKFLOW, safe="")
    status, payload, _ = utility.api_json(
        f"https://api.github.com/repos/{repository}/actions/workflows/{encoded}/runs?event=workflow_dispatch&per_page=100",
        token,
    )
    if status != 200 or payload is None:
        return {"passed": False, "reason": f"workflow query HTTP {status}"}
    prior = sorted(int(row["id"]) for row in payload["workflow_runs"] if int(row["id"]) != run_id)
    release_status, release, _ = utility.api_json(
        f"https://api.github.com/repos/{repository}/releases/tags/{RELEASE_TAG}", token
    )
    return {
        "passed": not prior and release_status == 404,
        "current_run_id": run_id,
        "run_attempt": attempt,
        "prior_run_ids": prior,
        "release_query_status": release_status,
        "release_id_if_present": None if release is None else release.get("id"),
    }


def preflight(root, token):
    value = protocol()
    envelope = value["execution_envelope"]
    memory = 0
    for line in pathlib.Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemTotal:"):
            memory = int(line.split()[1])
    disk = shutil.disk_usage(root)
    cpu_model = None
    for line in pathlib.Path("/proc/cpuinfo").read_text().splitlines():
        if line.startswith("model name"):
            cpu_model = line.split(":", 1)[1].strip()
            break
    dispatch = guard(token)
    record = {
        "runner_image": os.environ.get("ImageOS"),
        "runner_image_version": os.environ.get("ImageVersion"),
        "architecture": platform.machine(),
        "cpu_model": cpu_model,
        "cpu_count": os.cpu_count(),
        "total_ram_kib": memory,
        "filesystem_total_bytes": disk.total,
        "filesystem_free_bytes": disk.free,
        "repository_commit": os.environ.get("GITHUB_SHA"),
        "protocol_sha256": {key: sha256(REPO / key) for key in PROTECTED},
        "dispatch_guard": dispatch,
    }
    record["checks"] = {
        "dispatch": dispatch["passed"],
        "architecture": platform.machine().lower() in {"x86_64", "amd64"},
        "cpu": (os.cpu_count() or 999) <= envelope["maximum_vcpu"],
        "ram": memory <= envelope["maximum_ram_gib"] * 1024 * 1024,
        "free_disk": disk.free >= envelope["minimum_preacquisition_free_bytes"],
        "commit": os.environ.get("GITHUB_SHA") == subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True
        ).strip(),
    }
    record["passed"] = all(record["checks"].values())
    write_json(root / "evidence" / "environment_preflight.json", record)
    return record["passed"]


def prepare_root(root):
    """Create the complete fixed working tree before any destination is opened."""
    for relative in ["evidence", "sources", "tools/source", "work/combined", "inputs", "oracle-work"]:
        (root / relative).mkdir(parents=True, exist_ok=True)


def acquire(root, archive):
    prepare_root(root)
    value = protocol()
    unified = value["unified_input_release"]
    archive = pathlib.Path(archive)
    source_record = {
        "tag": unified["tag"], "asset_id": unified["asset_id"],
        "asset_name": unified["asset_name"], "bytes": archive.stat().st_size,
        "sha256": sha256(archive),
    }
    if archive.stat().st_size != unified["asset_bytes"] or sha256(archive) != unified["asset_sha256"]:
        raise RuntimeError("unified input archive mismatch")
    extracted = root / "sources" / "unified"
    utility.safe_extract_tar(archive, extracted)
    records = []
    for frozen in value["inputs"]:
        source = extracted / frozen["path"]
        if not source.is_file():
            raise RuntimeError(f"missing unified source for {frozen['rank']}")
        observed_source = inspect(source)
        if not exact(observed_source, frozen):
            raise RuntimeError(f"unified input mismatch for {frozen['rank']}")
        destination = root / frozen["path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        observed = inspect(destination)
        observed.update({"rank": frozen["rank"], "sample": frozen["sample"]})
        observed["exact"] = exact(observed, frozen)
        records.append(observed)
    result = {
        "source": source_record, "records": records,
        "total_rows": sum(row["rows"] for row in records),
        "total_bytes": sum(row["bytes"] for row in records),
        "all_exact": all(row["exact"] for row in records),
    }
    write_json(root / "evidence" / "input_integrity.json", result)
    if not result["all_exact"]:
        raise RuntimeError("input integrity mismatch")
    sample_expected = value["sample_list"]
    source_sample = extracted / sample_expected["path"]
    sample = root / sample_expected["path"]
    sample.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_sample, sample)
    sample_record = {"bytes": sample.stat().st_size, "sha256": sha256(sample), "rows": len(sample.read_text().splitlines())}
    if sample_record != {"bytes": sample_expected["bytes"], "sha256": sample_expected["sha256"], "rows": sample_expected["row_count"]}:
        raise RuntimeError("sample list mismatch")
    write_json(root / "evidence" / "sample_list_integrity.json", sample_record)


def build(root, token):
    value = protocol()
    archive = root / "sources" / "seer.tar.gz"
    code, _ = utility.api_download(SOURCE_URL, token, archive)
    if code != 200 or sha256(archive) != value["tool"]["source_archive_sha256"]:
        raise RuntimeError("source archive mismatch")
    parent = root / "tools" / "source"
    utility.safe_extract_tar(archive, parent)
    directories = [path for path in parent.iterdir() if path.is_dir()]
    if len(directories) != 1:
        raise RuntimeError("unexpected source layout")
    source = directories[0]
    blobs = {relative: git_blob(source / relative) for relative in value["tool"]["source_git_blobs"]}
    if blobs != value["tool"]["source_git_blobs"]:
        raise RuntimeError("source blob mismatch")
    binary = root / "tools" / "combineKmers-a6bd405"
    command = list(value["tool"]["build_command"])
    command[command.index("combineKmers-a6bd405")] = str(binary)
    completed = subprocess.run(command, cwd=source, capture_output=True, text=True)
    (root / "evidence" / "build.stdout").write_text(completed.stdout)
    (root / "evidence" / "build.stderr").write_text(completed.stderr)
    if completed.returncode or not binary.is_file():
        raise RuntimeError("build failed")
    format_value = "$" + "{Package}\t$" + "{Version}\n"
    packages = subprocess.run([
        "dpkg-query", "-W", "-f=" + format_value,
        "g++", "libboost-program-options-dev", "libgzstream-dev", "zlib1g-dev"
    ], capture_output=True, text=True)
    write_json(root / "evidence" / "tool_integrity.json", {
        "source_archive_bytes": archive.stat().st_size,
        "source_archive_sha256": sha256(archive),
        "source_git_blobs": blobs,
        "build_command": command,
        "compiler": subprocess.check_output(["g++", "--version"], text=True).splitlines()[0],
        "packages": packages.stdout.splitlines(),
        "binary_bytes": binary.stat().st_size,
        "binary_sha256": sha256(binary),
    })


def initialize(root):
    prepare_root(root)
    write_json(root / "evidence" / "outcome.json", {
        "experiment_id": EXPERIMENT,
        "state": "INCOMPLETE",
        "one_attempt": True,
        "no_retry_occurred": True,
    })


def classify(root, run_outcome):
    value = protocol()
    existing = json.loads((root / "evidence" / "outcome.json").read_text())
    state = existing.get("state", "FAIL_PREFLIGHT_INFRASTRUCTURE")
    combine_path = root / "evidence" / "combine.stage.json"
    oracle_stage_path = root / "evidence" / "oracle.stage.json"
    oracle_path = root / "evidence" / "oracle.json"
    combined = root / value["combine"]["output_gzip"]
    if combine_path.is_file():
        combine = json.loads(combine_path.read_text())
        if combine["termination_reason"] == "timeout":
            state = "FAIL_COMBINE_TIMEOUT"
        elif combine["termination_reason"] == "memory":
            state = "FAIL_MEMORY_ENVELOPE"
        elif combine["termination_reason"] == "storage":
            state = "FAIL_STORAGE_ENVELOPE"
        elif combine["exit_code"] != 0:
            state = "FAIL_COMBINE_NONZERO"
        elif not combined.is_file() or not combined.stat().st_size:
            state = "FAIL_COMBINE_OUTPUT"
        elif oracle_stage_path.is_file():
            oracle_stage = json.loads(oracle_stage_path.read_text())
            if oracle_stage["termination_reason"] == "timeout":
                state = "FAIL_ORACLE_TIMEOUT"
            elif oracle_stage["termination_reason"] == "memory":
                state = "FAIL_MEMORY_ENVELOPE"
            elif oracle_stage["termination_reason"] == "storage":
                state = "FAIL_STORAGE_ENVELOPE"
            elif oracle_stage["exit_code"] != 0 and oracle_path.is_file() and not json.loads(oracle_path.read_text()).get("exact"):
                state = "FAIL_FEATURE_EQUALITY"
            elif oracle_stage["exit_code"] != 0:
                state = "FAIL_ORACLE_STAGE"
            elif not oracle_path.is_file() or not json.loads(oracle_path.read_text()).get("exact"):
                state = "FAIL_FEATURE_EQUALITY"
            else:
                state = "PASS_CANDIDATE"
        else:
            state = "FAIL_ORACLE_STAGE"
    elif state == "INCOMPLETE":
        state = "FAIL_PREFLIGHT_INFRASTRUCTURE"
    outcome = {
        "experiment_id": EXPERIMENT,
        "state": state,
        "one_attempt": True,
        "no_retry_occurred": True,
        "original_n8_gate_remains_failed": True,
        "full_1102_reconstruction_authorized": False,
        "model_training_authorized": False,
    }
    write_json(root / "evidence" / "outcome.json", outcome)
    manifest(root, root / "evidence" / "recursive_manifest.json")
    return 0 if state == "PASS_CANDIDATE" else 2


def manifest(root, destination):
    rows = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.resolve() != destination.resolve():
            rows.append({"path": path.relative_to(root).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)})
    write_json(destination, rows)
    return rows


def audit(source, output):
    output.mkdir(parents=True, exist_ok=True)
    value = protocol()
    outcome = json.loads((source / "evidence" / "outcome.json").read_text())
    if outcome.get("state") != "PASS_CANDIDATE":
        write_json(output / "outcome.json", outcome)
        return 2
    for frozen in value["inputs"]:
        if not exact(inspect(source / frozen["path"]), frozen):
            write_json(output / "outcome.json", {"experiment_id": EXPERIMENT, "state": "FAIL_EVIDENCE_RETENTION"})
            return 2
    oracle = json.loads((source / "evidence" / "oracle.json").read_text())
    combined = source / value["combine"]["output_gzip"]
    if not oracle.get("exact") or not combined.is_file():
        return 2
    release_root = output / "release"
    for path in sorted(source.rglob("*")):
        if path.is_file() and (
            path.is_relative_to(source / "inputs") or path.is_relative_to(source / "evidence") or
            path == source / value["sample_list"]["path"] or path == combined
        ):
            destination = release_root / path.relative_to(source)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, destination)
    rows = manifest(release_root, release_root / "release_manifest.json")
    archive = output / ASSET_NAME
    with tarfile.open(archive, "w:gz", format=tarfile.PAX_FORMAT) as handle:
        for path in sorted(release_root.rglob("*")):
            handle.add(path, arcname=path.relative_to(release_root))
    ledger = {
        "archive_bytes": archive.stat().st_size,
        "archive_sha256": sha256(archive),
        "release_file_count": len(rows) + 1,
        "all_eight_inputs_included": True,
        "combined_bytes": combined.stat().st_size,
        "combined_sha256": sha256(combined),
        "candidate_audit_pass": True,
    }
    write_json(output / "bundle_ledger.json", ledger)
    write_json(output / "outcome.json", {"experiment_id": EXPERIMENT, "state": "AUDIT_PASS_RELEASE_PENDING"})
    return 0


def audit_release(archive, ledger_path, output):
    value = protocol()
    ledger = json.loads(ledger_path.read_text())
    if archive.stat().st_size != ledger["archive_bytes"] or sha256(archive) != ledger["archive_sha256"]:
        write_json(output / "outcome.json", {"experiment_id": EXPERIMENT, "state": "FAIL_EVIDENCE_RETENTION"})
        return 2
    with tempfile.TemporaryDirectory(prefix="seer-n8-readback-") as name:
        extracted = pathlib.Path(name)
        utility.safe_extract_tar(archive, extracted)
        input_exact = all(exact(inspect(extracted / frozen["path"]), frozen) for frozen in value["inputs"])
        oracle = json.loads((extracted / "evidence" / "oracle.json").read_text())
        combined = extracted / value["combine"]["output_gzip"]
        passed = input_exact and oracle.get("exact") is True and combined.is_file()
        record = {
            "archive_bytes": archive.stat().st_size,
            "archive_sha256": sha256(archive),
            "all_eight_inputs_exact": input_exact,
            "oracle_exact": oracle.get("exact"),
            "combined_bytes": combined.stat().st_size if combined.is_file() else None,
            "combined_sha256": sha256(combined) if combined.is_file() else None,
            "exact": passed,
        }
    write_json(output / "release_readback.json", record)
    write_json(output / "outcome.json", {
        "experiment_id": EXPERIMENT,
        "state": "PASS" if passed else "FAIL_EVIDENCE_RETENTION",
        "release_readback": record,
        "original_n8_gate_remains_failed": True,
        "full_1102_reconstruction_authorized": False,
        "model_training_authorized": False,
    })
    return 0 if passed else 2


def self_test():
    value = protocol()
    content = "".join(line + "\n" for line in value["sample_list"]["content_lines"]).encode()
    assert len(content) == value["sample_list"]["bytes"]
    assert hashlib.sha256(content).hexdigest() == value["sample_list"]["sha256"]
    assert hashlib.sha256(content + b"X").hexdigest() != value["sample_list"]["sha256"]
    print(json.dumps({"self_test": "PASS", "protocol_hashes": PROTECTED}, indent=2, sort_keys=True))


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ["initialize", "preflight", "build"]:
        item = sub.add_parser(name)
        item.add_argument("--root", required=True)
    item = sub.add_parser("acquire")
    item.add_argument("--root", required=True)
    item.add_argument("--archive", required=True)
    item = sub.add_parser("classify")
    item.add_argument("--root", required=True)
    item.add_argument("--run-outcome", required=True)
    item = sub.add_parser("audit")
    item.add_argument("--source", required=True)
    item.add_argument("--output", required=True)
    item = sub.add_parser("audit-release")
    item.add_argument("--archive", required=True)
    item.add_argument("--ledger", required=True)
    item.add_argument("--output", required=True)
    sub.add_parser("self-test")
    args = parser.parse_args()
    if args.command == "self-test":
        self_test()
        return
    if args.command == "initialize":
        initialize(pathlib.Path(args.root))
        return
    if args.command == "preflight":
        root = pathlib.Path(args.root)
        passed = preflight(root, os.environ.get("GITHUB_TOKEN", ""))
        if not passed:
            write_json(root / "evidence" / "outcome.json", {"experiment_id": EXPERIMENT, "state": "FAIL_PREFLIGHT_INFRASTRUCTURE"})
        raise SystemExit(0 if passed else 2)
    if args.command == "acquire":
        root = pathlib.Path(args.root)
        try:
            acquire(root, pathlib.Path(args.archive))
        except Exception as error:
            message = str(error)
            state = "FAIL_INPUT_AVAILABILITY" if any(word in message for word in ["unavailable", "missing", "HTTP"]) else ("FAIL_SAMPLE_LIST_INTEGRITY" if "sample list" in message else "FAIL_INPUT_INTEGRITY")
            write_json(root / "evidence" / "outcome.json", {"experiment_id": EXPERIMENT, "state": state, "error": message})
            raise
        return
    if args.command == "build":
        root = pathlib.Path(args.root)
        try:
            build(root, os.environ.get("GITHUB_TOKEN", ""))
        except Exception as error:
            write_json(root / "evidence" / "outcome.json", {"experiment_id": EXPERIMENT, "state": "FAIL_TOOL_INTEGRITY", "error": str(error)})
            raise
        return
    if args.command == "classify":
        raise SystemExit(classify(pathlib.Path(args.root), args.run_outcome))
    if args.command == "audit":
        raise SystemExit(audit(pathlib.Path(args.source), pathlib.Path(args.output)))
    raise SystemExit(audit_release(pathlib.Path(args.archive), pathlib.Path(args.ledger), pathlib.Path(args.output)))


if __name__ == "__main__":
    main()
