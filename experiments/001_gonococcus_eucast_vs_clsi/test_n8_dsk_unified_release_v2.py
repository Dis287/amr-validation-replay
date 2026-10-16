#!/usr/bin/env python3
"""Synthetic stage/readback controls for N8_DSK_UNIFIED_RELEASE_V2."""

import hashlib
import pathlib
import tempfile

import n8_dsk_unified_release_v2 as harness


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fixture(root):
    ranks = ["min", "p10", "p25", "median", "p75", "p90", "p99", "max"]
    bases = ["A", "C", "G", "T", "AC", "AG", "AT", "CG"]
    seven = root / "seven"
    maximum = root / "maximum.txt"
    inputs = []
    for index, rank in enumerate(ranks):
        data = ((bases[index] * 31)[:31] + f" {index + 1}\n").encode()
        path = maximum if rank == "max" else seven / rank / "kmers.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        inputs.append({
            "order": index + 1,
            "rank": rank,
            "sample": f"S{index + 1}",
            "path": f"inputs/{rank}/kmers.txt",
            "rows": 1,
            "bytes": len(data),
            "sha256": sha(data),
        })
    seven_archive = root / "seven.tar.gz"
    seven_archive.write_bytes(b"synthetic-seven-archive")
    maximum_tar = root / "maximum.tar.gz"
    maximum_tar.write_bytes(b"synthetic-maximum-tar")
    lines = [f"{row['sample']}\t{row['path']}" for row in inputs]
    sample = ("\n".join(lines) + "\n").encode()
    value = {
        "inputs": inputs,
        "sample_list": {
            "path": "inputs/n8_samples.tsv",
            "content_lines": lines,
            "bytes": len(sample),
            "sha256": sha(sample),
            "row_count": 8,
        },
        "source_policy": {
            "seven_source_archive_bytes": seven_archive.stat().st_size,
            "seven_source_archive_sha256": harness.sha256(seven_archive),
            "maximum_source_artifact_digest": "sha256:synthetic",
            "maximum_source_internal_tar_bytes": maximum_tar.stat().st_size,
            "maximum_source_internal_tar_sha256": harness.sha256(maximum_tar),
            "seven_source_release_tag": "synthetic",
            "seven_source_asset_id": 1,
            "maximum_source_artifact_id": 2,
        },
        "packaging": {
            "asset_name": "synthetic.tar.gz",
            "release_tag": "synthetic-release",
        },
    }
    return value, seven_archive, seven, maximum_tar, maximum


def main():
    with tempfile.TemporaryDirectory(prefix="n8-unified-v2-stage-") as name:
        root = pathlib.Path(name)
        value, seven_archive, seven, maximum_tar, maximum = fixture(root)
        build_root = root / "positive"
        result = harness.build(
            value, build_root, seven_archive, seven, "sha256:synthetic",
            maximum_tar, maximum,
        )
        archive = pathlib.Path(result["archive"]["path"])
        output = root / "readback.json"
        assert harness.verify_readback(
            value, archive, result["archive"]["sha256"],
            result["archive"]["bytes"], output,
        ) == 0
        assert output.read_text().find('"state": "PASS"') >= 0

        mutated = root / "mutated"
        mutated.mkdir()
        bad_maximum = mutated / "maximum.txt"
        bad_maximum.write_bytes(maximum.read_bytes() + b"X")
        rejected = False
        try:
            harness.build(
                value, root / "negative", seven_archive, seven,
                "sha256:synthetic", maximum_tar, bad_maximum,
            )
        except RuntimeError:
            rejected = True
        assert rejected
        print('{"synthetic_stage":"PASS","fresh_readback":"PASS","mutation_control":"REJECTED"}')


if __name__ == "__main__":
    main()
