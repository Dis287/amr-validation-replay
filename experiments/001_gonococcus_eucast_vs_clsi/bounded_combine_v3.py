#!/usr/bin/env python3
"""Bound one process tree by time, sampled RSS, and working-root bytes."""

import argparse
import hashlib
import json
import os
import pathlib
import signal
import subprocess
import time


def rows():
    result = {}
    for path in pathlib.Path("/proc").glob("[0-9]*/status"):
        try:
            values = dict(line.split(":", 1) for line in path.read_text().splitlines() if ":" in line)
            result[int(path.parent.name)] = {
                "ppid": int(values["PPid"]),
                "rss_kib": int(values.get("VmRSS", "0 kB").split()[0]),
            }
        except (OSError, ValueError, KeyError):
            pass
    return result


def descendants(table, root):
    result = {root}
    while True:
        added = {pid for pid, value in table.items() if value["ppid"] in result}
        if added <= result:
            return result
        result |= added


def tree_bytes(path):
    total = 0
    for member in pathlib.Path(path).rglob("*"):
        try:
            if member.is_file():
                total += member.stat().st_size
        except OSError:
            pass
    return total


def sha256(path):
    value = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--cwd", required=True)
    parser.add_argument("--watch-root", required=True)
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--log", required=True)
    parser.add_argument("--timeout", type=int, required=True)
    parser.add_argument("--rss-kib", type=int, required=True)
    parser.add_argument("--disk-bytes", type=int, required=True)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command and args.command[0] == "--" else args.command
    if not command:
        parser.error("missing command")
    evidence = pathlib.Path(args.evidence)
    log = pathlib.Path(args.log)
    evidence.parent.mkdir(parents=True, exist_ok=True)
    log.parent.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    peak_rss = 0
    peak_disk = tree_bytes(args.watch_root)
    reason = None
    with log.open("wb") as output:
        process = subprocess.Popen(
            command, cwd=args.cwd, stdout=output, stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        while process.poll() is None:
            table = rows()
            family = descendants(table, process.pid)
            rss = sum(table[pid]["rss_kib"] for pid in family if pid in table)
            disk = tree_bytes(args.watch_root)
            peak_rss = max(peak_rss, rss)
            peak_disk = max(peak_disk, disk)
            if time.monotonic() - start > args.timeout:
                reason = "timeout"
            elif rss > args.rss_kib:
                reason = "memory"
            elif disk > args.disk_bytes:
                reason = "storage"
            if reason:
                os.killpg(process.pid, signal.SIGTERM)
                deadline = time.monotonic() + 10
                while process.poll() is None and time.monotonic() < deadline:
                    time.sleep(0.1)
                if process.poll() is None:
                    os.killpg(process.pid, signal.SIGKILL)
                break
            time.sleep(0.5)
    exit_code = process.wait()
    record = {
        "schema": "amr-corrected-seer-n8-stage-v3",
        "name": args.name,
        "command": command,
        "cwd": str(pathlib.Path(args.cwd).resolve()),
        "timeout_seconds": args.timeout,
        "rss_ceiling_kib": args.rss_kib,
        "disk_ceiling_bytes": args.disk_bytes,
        "termination_reason": reason,
        "exit_code": exit_code,
        "wall_seconds": round(time.monotonic() - start, 3),
        "sample_interval_seconds": 0.5,
        "termination_grace_seconds": 10,
        "sampled_peak_process_tree_rss_kib": peak_rss,
        "sampled_peak_working_root_bytes": peak_disk,
        "final_working_root_bytes": tree_bytes(args.watch_root),
        "log_sha256": sha256(log),
    }
    evidence.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(json.dumps(record, indent=2, sort_keys=True))
    if reason == "timeout":
        raise SystemExit(124)
    if reason == "memory":
        raise SystemExit(125)
    if reason == "storage":
        raise SystemExit(126)
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
