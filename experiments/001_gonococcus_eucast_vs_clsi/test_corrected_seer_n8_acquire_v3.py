#!/usr/bin/env python3
"""Synthetic unified-release acquisition test for corrected-SEER n8 V3."""

import gzip
import hashlib
import io
import pathlib
import tarfile
import tempfile

import corrected_seer_n8_combine_v3 as harness


def sha(data):
    return hashlib.sha256(data).hexdigest()


def make_archive(path, files):
    with tarfile.open(path, "w:gz", format=tarfile.PAX_FORMAT) as output:
        for name, data in sorted(files.items()):
            info = tarfile.TarInfo(name)
            info.size = len(data)
            output.addfile(info, io.BytesIO(data))


def main():
    ranks = ["min", "p10", "p25", "median", "p75", "p90", "p99", "max"]
    bases = ["A", "C", "G", "T", "AC", "AG", "AT", "CG"]
    files = {}
    inputs = []
    for index, rank in enumerate(ranks):
        data = ((bases[index] * 31)[:31] + f" {index + 1}\n").encode()
        path = f"inputs/{rank}/kmers.txt"
        files[path] = data
        inputs.append({
            "rank": rank, "sample": f"S{index + 1}", "path": path,
            "rows": 1, "bytes": len(data), "sha256": sha(data),
        })
    lines = [f"{row['sample']}\t{row['path']}" for row in inputs]
    sample = ("\n".join(lines) + "\n").encode()
    files["inputs/n8_samples.tsv"] = sample

    with tempfile.TemporaryDirectory(prefix="seer-n8-v3-acquire-") as name:
        parent = pathlib.Path(name)
        archive = parent / "unified.tar.gz"
        make_archive(archive, files)
        fake = {
            "inputs": inputs,
            "sample_list": {
                "path": "inputs/n8_samples.tsv", "bytes": len(sample),
                "sha256": sha(sample), "row_count": 8,
            },
            "unified_input_release": {
                "tag": "synthetic", "asset_id": 1, "asset_name": archive.name,
                "asset_bytes": archive.stat().st_size,
                "asset_sha256": harness.sha256(archive),
            },
        }
        original = harness.protocol
        try:
            harness.protocol = lambda: fake
            root = parent / "fresh-root"
            harness.acquire(root, archive)
            assert (root / "evidence/input_integrity.json").is_file()
            assert all((root / row["path"]).read_bytes() == files[row["path"]] for row in inputs)
            assert (root / "inputs/n8_samples.tsv").read_bytes() == sample

            bad = parent / "bad.tar.gz"
            bad.write_bytes(archive.read_bytes() + b"X")
            rejected = False
            try:
                harness.acquire(parent / "bad-root", bad)
            except RuntimeError:
                rejected = True
            assert rejected
        finally:
            harness.protocol = original
        print('{"unified_acquisition":"PASS","all_eight_exact":true,"mutation_control":"REJECTED"}')


if __name__ == "__main__":
    main()
