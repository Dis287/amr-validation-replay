#!/usr/bin/env python3
"""Deterministically select the frozen nested 8 -> 16 -> 32 calibration panel."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

BASE8 = [0, 110, 275, 550, 826, 991, 1090, 1101]
EXPECTED_MANIFEST_ROWS = 1102
EXPECTED_MANIFEST_SHA256 = "f15dfdcdf649e5e4a067e4bcdc1b643c1a124fcba7d6d24bfe135d992f58610f"


def sha256(path):
    value = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def extend(selected, additions):
    selected = sorted(selected)
    added = []
    for _ in range(additions):
        intervals = [(right - left, left, right)
                     for left, right in zip(selected, selected[1:])
                     if right - left > 1]
        if not intervals:
            raise RuntimeError("no selectable interval remains")
        _, left, right = max(intervals, key=lambda item: (item[0], -item[1]))
        midpoint = (left + right) // 2
        if midpoint in selected:
            raise RuntimeError("midpoint collision")
        selected.append(midpoint)
        selected.sort()
        added.append(midpoint)
    return selected, added


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    manifest = Path(args.manifest)
    observed_manifest_sha256 = sha256(manifest)
    if observed_manifest_sha256 != EXPECTED_MANIFEST_SHA256:
        raise RuntimeError(f"manifest hash mismatch: {observed_manifest_sha256}")
    with manifest.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != EXPECTED_MANIFEST_ROWS:
        raise RuntimeError(f"expected {EXPECTED_MANIFEST_ROWS} rows, observed {len(rows)}")
    for row in rows:
        parts = row["fastq_bytes"].split(";")
        if len(parts) != 2:
            raise RuntimeError(f"non-paired byte record: {row['run_accession']}")
        row["total_bytes"] = sum(map(int, parts))
    rows.sort(key=lambda row: (row["total_bytes"], row["run_accession"]))
    selected16, added16 = extend(BASE8, 8)
    selected32, added32 = extend(selected16, 16)
    records = []
    for rank in selected32:
        row = rows[rank]
        stage = "existing8" if rank in BASE8 else ("add_to_16" if rank in added16 else "add_to_32")
        records.append({
            "rank_index_zero_based": rank,
            "stage": stage,
            "run_accession": row["run_accession"],
            "fastq_ftp": row["fastq_ftp"].split(";"),
            "fastq_bytes": [int(value) for value in row["fastq_bytes"].split(";")],
            "fastq_md5": row["fastq_md5"].split(";"),
            "total_bytes": row["total_bytes"],
        })
    result = {
        "schema": "amr-cohort-resource-calibration-selection-v1",
        "manifest_path": manifest.as_posix(),
        "manifest_rows": len(rows),
        "manifest_sha256": sha256(manifest),
        "sort": ["total paired compressed FASTQ bytes ascending", "run accession ascending"],
        "algorithm": "start with frozen BASE8; repeatedly select floor midpoint of widest adjacent rank interval, tie by lower left endpoint; add 8 for n16 then 16 for n32",
        "base8_rank_indices": BASE8,
        "add_to_16_rank_indices_in_selection_order": added16,
        "add_to_32_rank_indices_in_selection_order": added32,
        "n16_rank_indices_sorted": selected16,
        "n32_rank_indices_sorted": selected32,
        "records": records,
    }
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
