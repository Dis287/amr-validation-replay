"""Filter ENA study filereports to the 1,102 Hicks S7 dataset-2 runs.

Usage: python build_ena_manifest.py S7.xlsx ERP008891.tsv ERP000144.tsv
       ERP001405.tsv > ena_dataset2_manifest.tsv
The ENA reports must include run_accession, fastq_ftp, fastq_bytes, fastq_md5,
and library_layout. Download commands and retrieval date are in RAW_READ_FEASIBILITY.md.
"""

import csv
import sys

from openpyxl import load_workbook


def main(s7, reports):
    values = load_workbook(s7, read_only=True, data_only=True).active.values
    next(values)
    if tuple(next(values)[:4]) != ("Run ID", "SRA Study ID", "Dataset(s)", "AZM MIC"):
        raise ValueError("unexpected S7 header")
    target = {r[0]: r for r in values if isinstance(r[0], str) and "2" in str(r[2])}
    ena = {}
    for path in reports:
        with open(path, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t"):
                if r["run_accession"] in target:
                    ena[r["run_accession"]] = r
    if target.keys() != ena.keys():
        raise ValueError(f"unresolved runs: {sorted(target.keys() - ena.keys())[:10]}")
    fields = ("run_accession", "s7_dataset", "s7_azm_mic", "library_layout",
              "fastq_ftp", "fastq_bytes", "fastq_md5")
    writer = csv.DictWriter(sys.stdout, fieldnames=fields, delimiter="\t")
    writer.writeheader()
    for run in sorted(target):
        row = target[run]
        r = ena[run]
        n = len(r["fastq_ftp"].split(";"))
        if not r["fastq_ftp"] or n != 2 or any(
            len(r[field].split(";")) != n for field in ("fastq_bytes", "fastq_md5")
        ):
            raise ValueError(f"incomplete paired FASTQ metadata: {run}")
        writer.writerow({
            "run_accession": run,
            "s7_dataset": row[2],
            "s7_azm_mic": row[3],
            "library_layout": r["library_layout"],
            "fastq_ftp": r["fastq_ftp"],
            "fastq_bytes": r["fastq_bytes"],
            "fastq_md5": r["fastq_md5"],
        })


if __name__ == "__main__":
    if len(sys.argv) != 5:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2:])
