"""Compare Hicks S7 run IDs with the GCGS Zenodo assembly archive.

Inputs are downloaded separately from the URLs in ZENODO_OVERLAP.md.
Requires openpyxl; does not extract or train on the assemblies.
"""

import argparse
import csv
import hashlib
import json
import re
import tarfile
from collections import Counter
from pathlib import Path

from openpyxl import load_workbook


def digest(path, algorithm):
    h = hashlib.new(algorithm)
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("s7", type=Path)
    p.add_argument("accession_map", type=Path)
    p.add_argument("assemblies", type=Path)
    args = p.parse_args()

    sheet = load_workbook(args.s7, read_only=True, data_only=True).active
    values = sheet.values
    next(values)  # title
    header = next(values)
    if tuple(header[:4]) != ("Run ID", "SRA Study ID", "Dataset(s)", "AZM MIC"):
        raise ValueError("unexpected S7 columns")
    cohort = {r[0]: r for r in values if isinstance(r[0], str) and "2" in str(r[2])}

    with args.accession_map.open(newline="", encoding="utf-8") as f:
        mapping = {r["Sample"]: r["Names"] for r in csv.DictReader(f, delimiter="\t")
                   if re.fullmatch(r"GCGS\d+", r["Names"])}

    with tarfile.open(args.assemblies, "r:gz") as archive:
        names = {m.group(1) for member in archive
                 if (m := re.fullmatch(r"gcgs-contigs/(GCGS\d+)\.fa", member.name))}

    matched = {run: mapping[run] for run in cohort if run in mapping and mapping[run] in names}
    if len(set(matched.values())) != len(matched):
        raise ValueError("accession mapping is not one-to-one")

    def mic(row):
        match = re.search(r"\d+(?:\.\d+)?", str(row[3]))
        if not match:
            raise ValueError(f"unparseable AZM MIC: {row[3]}")
        return float(match.group())

    result = {
        "s7_dataset2_tagged_runs": len(cohort),
        "s7_dataset_labels": dict(sorted(Counter(str(r[2]) for r in cohort.values()).items())),
        "accession_mapped_and_archive_present": len(matched),
        "archive_fasta_count": len(names),
        "archive_fasta_without_s7_dataset2_match": len(names - set(matched.values())),
        "s7_dataset2_without_archive_fasta": len(cohort) - len(matched),
        "azm_non_susceptible_eucast_mic_gt_0_25": sum(mic(r) > 0.25 for r in cohort.values()),
        "azm_non_susceptible_clsi_mic_gt_1": sum(mic(r) > 1 for r in cohort.values()),
        "inputs": {
            "s7_sha256": digest(args.s7, "sha256"),
            "accession_map_sha256": digest(args.accession_map, "sha256"),
            "assemblies_md5": digest(args.assemblies, "md5"),
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
