#!/usr/bin/env python3
"""One-attempt deterministic packager for N8_DSK_UNIFIED_RELEASE_V1."""

import argparse
import gzip
import hashlib
import io
import json
import os
import pathlib
import shutil
import subprocess
import tarfile
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
PROTOCOL_PATH = HERE / "n8_dsk_unified_release_v1.json"
PROTECTED = {
    "experiments/001_gonococcus_eucast_vs_clsi/N8_DSK_UNIFIED_RELEASE_V1.md":
        "9b04e40740ca6a484e4d3f12227197fe7ab849c73639eb8f8f9c0204a5eca0e4",
    "experiments/001_gonococcus_eucast_vs_clsi/n8_dsk_unified_release_v1.json":
        "4a472aa20b08edd06418ce2a246e65fb3ecf617ea0d1fbe918f09395a3927521",
}
EXPERIMENT = "N8_DSK_UNIFIED_RELEASE_V1"


def sha256(path):
    value = hashlib.sha256()
    with pathlib.Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def write_json(path, value):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def load_protocol():
    mismatches = {}
    for name, expected in PROTECTED.items():
        observed = sha256(REPO / name)
        if observed != expected:
            mismatches[name] = {"expected": expected, "observed": observed}
    if mismatches:
        raise RuntimeError(f"protected protocol mismatch: {mismatches}")
    value = json.loads(PROTOCOL_PATH.read_text())
    if value["experiment_id"] != EXPERIMENT or value["status"] != "FROZEN_NOT_EXECUTED":
        raise RuntimeError("unexpected protocol identity")
    return value


def inspect(path):
    path = pathlib.Path(path)
    rows = malformed = duplicates = 0
    seen = set()
    with path.open(encoding="ascii", newline="") as handle:
        for line in handle:
            rows += 1
            fields = line.split()
            if len(fields) != 2 or len(fields[0]) != 31 or any(base not in "ACGT" for base in fields[0]):
                malformed += 1
                continue
            try:
                if int(fields[1]) <= 0:
                    malformed += 1
            except ValueError:
                malformed += 1
            if fields[0] in seen:
                duplicates += 1
            seen.add(fields[0])
    return {
        "rows": rows,
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "malformed_rows": malformed,
        "duplicate_rows": duplicates,
    }


def exact(record, frozen):
    return (
        record["rows"] == frozen["rows"]
        and record["bytes"] == frozen["bytes"]
        and record["sha256"] == frozen["sha256"]
        and record["malformed_rows"] == 0
        and record["duplicate_rows"] == 0
    )


def safe_extract(archive, destination):
    destination.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "r:gz") as handle:
        handle.extractall(destination, filter="data")


def normalized_tar_gz(source, archive):
    members = sorted(path for path in source.rglob("*") if path.is_file())
    with tempfile.NamedTemporaryFile(prefix="n8-unified-", suffix=".tar", delete=False) as temporary:
        tar_path = pathlib.Path(temporary.name)
    try:
        with tarfile.open(tar_path, "w", format=tarfile.PAX_FORMAT) as output:
            for path in members:
                relative = path.relative_to(source).as_posix()
                data = path.read_bytes()
                info = tarfile.TarInfo(relative)
                info.size = len(data)
                info.mode = 0o644
                info.mtime = 0
                info.uid = 0
                info.gid = 0
                info.uname = ""
                info.gname = ""
                output.addfile(info, io.BytesIO(data))
        with tar_path.open("rb") as raw, pathlib.Path(archive).open("wb") as destination:
            with gzip.GzipFile(filename="", mode="wb", fileobj=destination, compresslevel=6, mtime=0) as compressed:
                shutil.copyfileobj(raw, compressed, length=8 * 1024 * 1024)
    finally:
        tar_path.unlink(missing_ok=True)


def preflight(expected_head):
    value = load_protocol()
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    free = shutil.disk_usage(REPO).free
    checks = {
        "head": head == expected_head,
        "clean_protocol_identity": value["status"] == "FROZEN_NOT_EXECUTED",
        "free_disk": free >= value["execution"]["minimum_free_bytes"],
    }
    return {"head": head, "expected_head": expected_head, "free_bytes": free, "checks": checks, "passed": all(checks.values())}


def build(value, root, seven_archive, seven_dir, maximum_zip, maximum_tar, maximum_kmers):
    root = pathlib.Path(root)
    package = root / "package"
    package.mkdir(parents=True, exist_ok=False)
    source = value["source_policy"]
    source_checks = {
        "seven_archive_bytes": pathlib.Path(seven_archive).stat().st_size,
        "seven_archive_sha256": sha256(seven_archive),
        "maximum_outer_zip_bytes": pathlib.Path(maximum_zip).stat().st_size,
        "maximum_outer_zip_sha256": sha256(maximum_zip),
        "maximum_internal_tar_bytes": pathlib.Path(maximum_tar).stat().st_size,
        "maximum_internal_tar_sha256": sha256(maximum_tar),
    }
    required = {
        "seven_archive_bytes": source["seven_source_archive_bytes"],
        "seven_archive_sha256": source["seven_source_archive_sha256"],
        "maximum_outer_zip_bytes": source["maximum_source_outer_zip_bytes"],
        "maximum_outer_zip_sha256": source["maximum_source_outer_zip_sha256"],
        "maximum_internal_tar_bytes": source["maximum_source_internal_tar_bytes"],
        "maximum_internal_tar_sha256": source["maximum_source_internal_tar_sha256"],
    }
    if source_checks != required:
        raise RuntimeError(f"source archive mismatch: {source_checks}")

    records = []
    for frozen in value["inputs"]:
        origin = pathlib.Path(maximum_kmers) if frozen["rank"] == "max" else pathlib.Path(seven_dir) / frozen["rank"] / "kmers.txt"
        observed = inspect(origin)
        if not exact(observed, frozen):
            raise RuntimeError(f"input mismatch: {frozen['rank']} {observed}")
        destination = package / frozen["path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(origin, destination)
        copied = inspect(destination)
        if not exact(copied, frozen):
            raise RuntimeError(f"copied input mismatch: {frozen['rank']}")
        records.append({"rank": frozen["rank"], "sample": frozen["sample"], **copied, "exact": True})

    sample = value["sample_list"]
    sample_path = package / sample["path"]
    sample_path.write_bytes(("\n".join(sample["content_lines"]) + "\n").encode())
    sample_record = {"bytes": sample_path.stat().st_size, "sha256": sha256(sample_path), "rows": len(sample_path.read_text().splitlines())}
    if sample_record != {"bytes": sample["bytes"], "sha256": sample["sha256"], "rows": sample["row_count"]}:
        raise RuntimeError("sample-list mismatch")

    receipts = {
        "experiment_id": EXPERIMENT,
        "sources": source_checks,
        "source_ids": {
            "seven_release_tag": source["seven_source_release_tag"],
            "seven_asset_id": source["seven_source_asset_id"],
            "maximum_artifact_id": source["maximum_source_artifact_id"],
        },
    }
    write_json(package / "source_receipts.json", receipts)
    primary = [
        {"path": row["path"], "bytes": row["bytes"], "sha256": row["sha256"], "rows": row["rows"]}
        for row in value["inputs"]
    ]
    primary.append({"path": sample["path"], "bytes": sample["bytes"], "sha256": sample["sha256"], "rows": sample["row_count"]})
    primary.append({"path": "source_receipts.json", "bytes": (package / "source_receipts.json").stat().st_size, "sha256": sha256(package / "source_receipts.json")})
    write_json(package / "complete_manifest.json", {"experiment_id": EXPERIMENT, "files": primary})

    archive = root / value["packaging"]["asset_name"]
    normalized_tar_gz(package, archive)
    result = {
        "experiment_id": EXPERIMENT,
        "state": "PACKAGE_PASS_RELEASE_PENDING",
        "archive": {"path": str(archive), "bytes": archive.stat().st_size, "sha256": sha256(archive)},
        "input_records": records,
        "sample_list": sample_record,
        "source_checks": source_checks,
        "release_tag": value["packaging"]["release_tag"],
    }
    write_json(root / "package_result.json", result)
    return result


def verify_readback(value, archive, expected_sha256, expected_bytes, output):
    archive = pathlib.Path(archive)
    archive_exact = archive.stat().st_size == expected_bytes and sha256(archive) == expected_sha256
    with tempfile.TemporaryDirectory(prefix="n8-unified-readback-") as name:
        extracted = pathlib.Path(name)
        safe_extract(archive, extracted)
        records = []
        for frozen in value["inputs"]:
            observed = inspect(extracted / frozen["path"])
            observed.update({"rank": frozen["rank"], "exact": exact(observed, frozen)})
            records.append(observed)
        sample = value["sample_list"]
        sample_path = extracted / sample["path"]
        sample_exact = (
            sample_path.stat().st_size == sample["bytes"]
            and sha256(sample_path) == sample["sha256"]
            and len(sample_path.read_text().splitlines()) == sample["row_count"]
        )
        passed = archive_exact and all(row["exact"] for row in records) and sample_exact
        record = {
            "experiment_id": EXPERIMENT,
            "state": "PASS" if passed else "FAIL_RELEASE_READBACK",
            "archive_exact": archive_exact,
            "archive_bytes": archive.stat().st_size,
            "archive_sha256": sha256(archive),
            "all_eight_exact": all(row["exact"] for row in records),
            "sample_list_exact": sample_exact,
            "records": records,
            "corrected_seer_n8_combine_authorized": False,
            "full_1102_reconstruction_authorized": False,
            "model_training_authorized": False,
        }
    write_json(output, record)
    return 0 if passed else 2


def self_test():
    with tempfile.TemporaryDirectory(prefix="n8-unified-self-test-") as name:
        root = pathlib.Path(name)
        source = root / "source"
        source.mkdir()
        (source / "a.txt").write_bytes(b"alpha\n")
        (source / "b.txt").write_bytes(b"beta\n")
        first = root / "first.tar.gz"
        second = root / "second.tar.gz"
        normalized_tar_gz(source, first)
        normalized_tar_gz(source, second)
        assert first.read_bytes() == second.read_bytes()
        extracted = root / "extracted"
        safe_extract(first, extracted)
        assert (extracted / "a.txt").read_bytes() == b"alpha\n"
        assert (extracted / "b.txt").read_bytes() == b"beta\n"
        print(json.dumps({"self_test": "PASS", "deterministic_archive_sha256": sha256(first)}, indent=2, sort_keys=True))


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("self-test")
    item = sub.add_parser("preflight")
    item.add_argument("--expected-head", required=True)
    item = sub.add_parser("stage")
    item.add_argument("--root", required=True)
    item.add_argument("--seven-archive", required=True)
    item.add_argument("--seven-dir", required=True)
    item.add_argument("--maximum-zip", required=True)
    item.add_argument("--maximum-tar", required=True)
    item.add_argument("--maximum-kmers", required=True)
    item = sub.add_parser("verify-readback")
    item.add_argument("--archive", required=True)
    item.add_argument("--expected-sha256", required=True)
    item.add_argument("--expected-bytes", required=True, type=int)
    item.add_argument("--output", required=True)
    args = parser.parse_args()
    if args.command == "self-test":
        self_test()
        return
    if args.command == "preflight":
        result = preflight(args.expected_head)
        print(json.dumps(result, indent=2, sort_keys=True))
        raise SystemExit(0 if result["passed"] else 2)
    value = load_protocol()
    if args.command == "stage":
        result = build(value, pathlib.Path(args.root), args.seven_archive, args.seven_dir, args.maximum_zip, args.maximum_tar, args.maximum_kmers)
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    raise SystemExit(verify_readback(value, args.archive, args.expected_sha256, args.expected_bytes, pathlib.Path(args.output)))


if __name__ == "__main__":
    main()
