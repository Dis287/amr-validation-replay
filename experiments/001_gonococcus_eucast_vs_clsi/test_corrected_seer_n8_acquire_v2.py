#!/usr/bin/env python3
"""Synthetic fresh-root acquisition test for CORRECTED_SEER_N8_COMBINE_V2."""

import hashlib
import io
import json
import os
import pathlib
import shutil
import tarfile
import tempfile
import zipfile

import corrected_seer_n8_combine_v2 as harness


def digest_bytes(data):
    return hashlib.sha256(data).hexdigest()


def tar_gz(path, members):
    with tarfile.open(path, "w:gz", format=tarfile.PAX_FORMAT) as archive:
        for name, data in members.items():
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.mode = 0o644
            archive.addfile(info, io.BytesIO(data))


def main():
    kmers = {}
    bases = ["A", "C", "G", "T", "AC", "AG", "AT", "CG"]
    ranks = ["min", "p10", "p25", "median", "p75", "p90", "p99", "max"]
    samples = ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"]
    for index, rank in enumerate(ranks):
        word = (bases[index] * 31)[:31].encode("ascii")
        kmers[rank] = word + b" " + str(index + 1).encode("ascii") + b"\n"

    with tempfile.TemporaryDirectory(prefix="seer-n8-v2-acquire-test-") as name:
        fixtures = pathlib.Path(name) / "fixtures"
        fixtures.mkdir()
        seven_archive = fixtures / "seven.tar.gz"
        tar_gz(seven_archive, {
            f"accepted/{rank}/kmers.txt": kmers[rank]
            for rank in ranks[:-1]
        })
        internal = fixtures / "maximum.tar.gz"
        tar_gz(internal, {"evidence/primary/kmers.txt": kmers["max"]})
        maximum_zip = fixtures / "maximum.zip"
        with zipfile.ZipFile(maximum_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.write(internal, "bundle/max-isolate-resource-resolution-v3-evidence.tar.gz")

        inputs = []
        for order, (rank, sample) in enumerate(zip(ranks, samples), 1):
            data = kmers[rank]
            source = (
                {
                    "kind": "github_actions_artifact_or_exact_verified_copy",
                    "artifact_id": 888,
                    "artifact_sha256": harness.sha256(maximum_zip),
                    "internal_archive_sha256": harness.sha256(internal),
                }
                if rank == "max"
                else {
                    "kind": "github_release",
                    "tag": "synthetic-seven",
                    "asset_id": 777,
                    "asset_sha256": harness.sha256(seven_archive),
                }
            )
            inputs.append({
                "order": order,
                "rank": rank,
                "sample": sample,
                "path": f"inputs/{rank}/kmers.txt",
                "rows": 1,
                "bytes": len(data),
                "sha256": digest_bytes(data),
                "source": source,
            })
        lines = [f"{row['sample']}\t{row['path']}" for row in inputs]
        sample_data = ("\n".join(lines) + "\n").encode()
        fake_protocol = {
            "inputs": inputs,
            "sample_list": {
                "path": "inputs/n8_samples.tsv",
                "content_lines": lines,
                "bytes": len(sample_data),
                "sha256": digest_bytes(sample_data),
                "row_count": 8,
            },
        }

        def fake_api_json(url, token):
            if "/releases/tags/synthetic-seven" in url:
                return 200, {"assets": [{
                    "id": 777,
                    "browser_download_url": seven_archive.as_uri(),
                }]}, {}
            if "/actions/artifacts/888" in url:
                return 200, {
                    "expired": False,
                    "archive_download_url": maximum_zip.as_uri(),
                }, {}
            raise AssertionError(f"unexpected API URL: {url}")

        opened_destinations = []
        def fake_download(url, token, destination):
            assert destination.parent.is_dir(), "destination parent was not pre-created"
            opened_destinations.append(destination.relative_to(root).as_posix())
            shutil.copyfile(pathlib.Path(url.removeprefix("file://")), destination)
            return 200, {}

        root = pathlib.Path(name) / "fresh-root"
        assert not root.exists()
        original_protocol = harness.protocol
        original_api_json = harness.utility.api_json
        original_api_download = harness.utility.api_download
        original_size = harness.SEVEN_ARCHIVE_BYTES
        original_repository = os.environ.get("GITHUB_REPOSITORY")
        try:
            os.environ["GITHUB_REPOSITORY"] = "synthetic/repository"
            harness.protocol = lambda: fake_protocol
            harness.utility.api_json = fake_api_json
            harness.utility.api_download = fake_download
            harness.SEVEN_ARCHIVE_BYTES = seven_archive.stat().st_size
            harness.acquire(root, "synthetic-token")
        finally:
            harness.protocol = original_protocol
            harness.utility.api_json = original_api_json
            harness.utility.api_download = original_api_download
            harness.SEVEN_ARCHIVE_BYTES = original_size
            if original_repository is None:
                os.environ.pop("GITHUB_REPOSITORY", None)
            else:
                os.environ["GITHUB_REPOSITORY"] = original_repository

        required_directories = [
            "evidence", "sources", "tools/source", "work/combined",
            "inputs", "oracle-work",
        ]
        assert all((root / item).is_dir() for item in required_directories)
        integrity = json.loads((root / "evidence/input_integrity.json").read_text())
        assert integrity["all_exact"] is True
        assert integrity["total_rows"] == 8
        assert integrity["total_bytes"] == sum(len(value) for value in kmers.values())
        assert (root / "inputs/n8_samples.tsv").read_bytes() == sample_data
        assert opened_destinations == ["sources/seven.tar.gz", "sources/maximum.zip"]
        print(json.dumps({
            "test": "synthetic_fresh_root_acquisition",
            "status": "PASS",
            "network_biological_download": False,
            "required_directories_created": required_directories,
            "download_destinations": opened_destinations,
            "all_eight_exact": True,
            "sample_list_exact": True,
        }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
