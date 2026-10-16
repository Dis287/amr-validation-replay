#!/usr/bin/env python3
"""Independent bounded-sort oracle for corrected-SEER n=8 V2."""

import argparse
import collections
import gzip
import hashlib
import heapq
import json
import os
import pathlib
import subprocess
import tempfile


def digest(path):
    value = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def write_json(path, value):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def sort_file(source, destination, temporary):
    env = dict(os.environ)
    env["LC_ALL"] = "C"
    subprocess.run([
        "sort", "-T", str(temporary), "-S", "512M", "-t", "\t",
        "-k1,1", "-k2,2", "-o", str(destination), str(source)
    ], env=env, check=True)


def normalize_inputs(specs, work, counters):
    temporary = work / "sort-tmp"
    temporary.mkdir(parents=True, exist_ok=True)
    results = []
    for spec in specs:
        raw = work / (spec["rank"] + ".normalized")
        with open(spec["path"], encoding="ascii") as source, raw.open("w", encoding="ascii") as output:
            for line in source:
                fields = line.split()
                if len(fields) != 2 or len(fields[0]) != 31 or any(x not in "ACGT" for x in fields[0]):
                    counters["malformed_rows"] += 1
                    continue
                try:
                    abundance = int(fields[1])
                    if abundance <= 0:
                        raise ValueError
                except ValueError:
                    counters["malformed_rows"] += 1
                    continue
                output.write(f"{fields[0]}\t{spec['sample']}\t{abundance}\n")
        sorted_path = work / (spec["rank"] + ".sorted")
        sort_file(raw, sorted_path, temporary)
        raw.unlink()
        results.append(sorted_path)
    return results


def merged_groups(paths):
    handles = [path.open(encoding="ascii") for path in paths]
    heap = []
    try:
        for index, handle in enumerate(handles):
            line = handle.readline()
            if line:
                kmer, sample, abundance = line.rstrip("\n").split("\t")
                heapq.heappush(heap, (kmer, index, sample, int(abundance)))
        while heap:
            key = heap[0][0]
            group = []
            while heap and heap[0][0] == key:
                _, index, sample, abundance = heapq.heappop(heap)
                group.append((sample, abundance))
                line = handles[index].readline()
                if line:
                    kmer, sample, abundance = line.rstrip("\n").split("\t")
                    heapq.heappush(heap, (kmer, index, sample, int(abundance)))
            yield key, group
    finally:
        for handle in handles:
            handle.close()


def normalize_actual(combined, work, allowed, counters):
    raw = work / "actual.normalized"
    physical = 0
    with gzip.open(combined, "rt", encoding="ascii") as source, raw.open("w", encoding="ascii") as output:
        for line in source:
            physical += 1
            fields = line.split()
            if not fields:
                counters["malformed_rows"] += 1
                continue
            kmer = fields[0]
            tags = fields[1:]
            if tags and tags[0] == "|":
                tags = tags[1:]
            if len(kmer) != 31 or any(x not in "ACGT" for x in kmer):
                counters["malformed_rows"] += 1
                continue
            normalized = []
            seen = set()
            bad = False
            for tag in tags:
                if ":" not in tag:
                    counters["malformed_rows"] += 1
                    bad = True
                    break
                sample, abundance_text = tag.rsplit(":", 1)
                try:
                    abundance = int(abundance_text)
                    if abundance <= 0:
                        raise ValueError
                except ValueError:
                    counters["malformed_rows"] += 1
                    bad = True
                    break
                if sample in seen:
                    counters["duplicate_sample_tags"] += 1
                seen.add(sample)
                if sample not in allowed:
                    counters["unknown_sample_tags"] += 1
                normalized.append(f"{sample}:{abundance}")
            if not bad:
                output.write(f"{kmer}\t{','.join(sorted(normalized))}\n")
    counters["physical_output_rows"] = physical
    destination = work / "actual.sorted"
    sort_file(raw, destination, work / "sort-tmp")
    raw.unlink()
    return destination


def compare(specs, combined, work):
    work.mkdir(parents=True, exist_ok=True)
    counters = collections.Counter({
        "malformed_rows": 0,
        "missing_expected": 0,
        "extra_or_below_minimum": 0,
        "duplicate_output_rows": 0,
        "duplicate_sample_tags": 0,
        "unknown_sample_tags": 0,
        "missing_sample_tags": 0,
        "abundance_mismatches": 0,
        "duplicate_input_rows": 0,
    })
    sorted_inputs = normalize_inputs(specs, work, counters)
    expected = work / "expected.sorted"
    expected_count = 0
    with expected.open("w", encoding="ascii") as output:
        for kmer, group in merged_groups(sorted_inputs):
            if len(group) != len({sample for sample, _ in group}):
                counters["duplicate_input_rows"] += len(group) - len({sample for sample, _ in group})
            mapping = dict(group)
            if len(mapping) >= 2:
                tags = ",".join(sorted(f"{sample}:{abundance}" for sample, abundance in mapping.items()))
                output.write(f"{kmer}\t{tags}\n")
                expected_count += 1
    allowed = {spec["sample"] for spec in specs}
    actual = normalize_actual(combined, work, allowed, counters)
    expected_handle = expected.open(encoding="ascii")
    actual_handle = actual.open(encoding="ascii")
    expected_line = expected_handle.readline()
    actual_line = actual_handle.readline()
    previous_actual = None
    unique_actual = 0
    while expected_line or actual_line:
        expected_key = expected_line.split("\t", 1)[0] if expected_line else None
        actual_key = actual_line.split("\t", 1)[0] if actual_line else None
        if actual_key is not None and actual_key == previous_actual:
            counters["duplicate_output_rows"] += 1
            actual_line = actual_handle.readline()
            continue
        if actual_key is not None:
            unique_actual += 1
            previous_actual = actual_key
        if expected_key is None:
            counters["extra_or_below_minimum"] += 1
            actual_line = actual_handle.readline()
        elif actual_key is None:
            counters["missing_expected"] += 1
            expected_line = expected_handle.readline()
        elif expected_key < actual_key:
            counters["missing_expected"] += 1
            expected_line = expected_handle.readline()
        elif actual_key < expected_key:
            counters["extra_or_below_minimum"] += 1
            actual_line = actual_handle.readline()
        else:
            expected_tags = expected_line.rstrip("\n").split("\t", 1)[1].split(",")
            actual_tags = actual_line.rstrip("\n").split("\t", 1)[1].split(",")
            expected_map = dict(tag.rsplit(":", 1) for tag in expected_tags if tag)
            actual_map = dict(tag.rsplit(":", 1) for tag in actual_tags if tag)
            counters["missing_sample_tags"] += len(set(expected_map) - set(actual_map))
            for sample in set(expected_map) & set(actual_map):
                if expected_map[sample] != actual_map[sample]:
                    counters["abundance_mismatches"] += 1
            counters["abundance_mismatches"] += len((set(actual_map) & allowed) - set(expected_map))
            expected_line = expected_handle.readline()
            actual_line = actual_handle.readline()
    expected_handle.close()
    actual_handle.close()
    exact_keys = [
        "malformed_rows", "missing_expected", "extra_or_below_minimum",
        "duplicate_output_rows", "duplicate_sample_tags", "unknown_sample_tags",
        "missing_sample_tags", "abundance_mismatches", "duplicate_input_rows",
    ]
    exact = (all(counters[key] == 0 for key in exact_keys) and
             counters["physical_output_rows"] == expected_count == unique_actual)
    return {
        "schema": "amr-corrected-seer-n8-oracle-v3",
        "strategy": "bounded external sort plus k-way merge",
        "expected_features": expected_count,
        "physical_output_rows": counters["physical_output_rows"],
        "unique_output_features": unique_actual,
        "counters": dict(counters),
        "expected_stream_bytes": expected.stat().st_size,
        "expected_stream_sha256": digest(expected),
        "combined_bytes": pathlib.Path(combined).stat().st_size,
        "combined_sha256": digest(combined),
        "exact": exact,
    }


def write_combined(path, rows):
    with gzip.open(path, "wt", encoding="ascii") as handle:
        for kmer, tags in rows:
            handle.write(f"{kmer} | {' '.join(tags)}\n")


def self_test():
    k1, k2, k3 = "A" * 31, "C" * 31, "G" * 31
    with tempfile.TemporaryDirectory(prefix="seer-oracle-self-test-") as name:
        root = pathlib.Path(name)
        specs = []
        for rank, rows in [
            ("a", [(k1, 2), (k2, 3)]),
            ("b", [(k1, 5), (k3, 7)]),
            ("c", [(k1, 11), (k2, 13)]),
        ]:
            path = root / (rank + ".txt")
            path.write_text("".join(f"{k} {a}\n" for k, a in rows))
            specs.append({"rank": rank, "sample": rank, "path": str(path)})
        cases = {
            "pass": ([(k1, ["a:2", "b:5", "c:11"]), (k2, ["a:3", "c:13"])], None),
            "missing": ([(k1, ["a:2", "b:5", "c:11"])], "missing_expected"),
            "extra": ([(k1, ["a:2", "b:5", "c:11"]), (k2, ["a:3", "c:13"]), (k3, ["b:7"])], "extra_or_below_minimum"),
            "duplicate_row": ([(k1, ["a:2", "b:5", "c:11"]), (k1, ["a:2", "b:5", "c:11"]), (k2, ["a:3", "c:13"])], "duplicate_output_rows"),
            "duplicate_tag": ([(k1, ["a:2", "a:2", "b:5", "c:11"]), (k2, ["a:3", "c:13"])], "duplicate_sample_tags"),
            "unknown_tag": ([(k1, ["a:2", "b:5", "c:11", "z:9"]), (k2, ["a:3", "c:13"])], "unknown_sample_tags"),
            "missing_tag": ([(k1, ["a:2", "b:5"]), (k2, ["a:3", "c:13"])], "missing_sample_tags"),
            "abundance": ([(k1, ["a:99", "b:5", "c:11"]), (k2, ["a:3", "c:13"])], "abundance_mismatches"),
            "extra_known_tag": ([(k1, ["a:2", "b:5", "c:11"]), (k2, ["a:3", "b:7", "c:13"])], "abundance_mismatches"),
        }
        evidence = {}
        for case, (rows, counter) in cases.items():
            case_root = root / case
            case_root.mkdir()
            combined = case_root / "combined.gz"
            write_combined(combined, rows)
            result = compare(specs, combined, case_root / "work")
            if counter is None:
                assert result["exact"]
            else:
                assert not result["exact"]
                assert result["counters"].get(counter, 0) > 0
            evidence[case] = {"exact": result["exact"], "expected_counter": counter}
        print(json.dumps({"self_test": "PASS", "cases": evidence}, indent=2, sort_keys=True))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", nargs="+")
    parser.add_argument("--combined")
    parser.add_argument("--work")
    parser.add_argument("--out")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    if not all([args.inputs, args.combined, args.work, args.out]):
        parser.error("--inputs, --combined, --work, and --out are required")
    specs = []
    for value in args.inputs:
        rank, sample, path = value.split("=", 2)
        specs.append({"rank": rank, "sample": sample, "path": path})
    result = compare(specs, pathlib.Path(args.combined), pathlib.Path(args.work))
    write_json(args.out, result)
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["exact"] else 2)


if __name__ == "__main__":
    main()
