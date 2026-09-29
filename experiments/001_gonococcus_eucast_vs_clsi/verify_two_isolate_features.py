"""Independently check two DSK count files and a SEER combined output.

Usage: python verify_two_isolate_features.py NAME1 FILTERED1.fa DSK1.txt \
       NAME2 FILTERED2.fa DSK2.txt COMBINED.gz
Exit nonzero on any disagreement. This verifies a toolchain pilot, not a model.
"""

import collections
import gzip
import json
import sys


def fasta_sequences(path):
    parts = []
    with open(path) as handle:
        for line in handle:
            if line.startswith(">"):
                if parts:
                    yield "".join(parts)
                parts = []
            else:
                parts.append(line.strip().upper())
    if parts:
        yield "".join(parts)


ORDER = str.maketrans({"A": "0", "C": "1", "T": "2", "G": "3"})
COMPLEMENT = str.maketrans("ACGT", "TGCA")


def canonical(word):
    reverse = word.translate(COMPLEMENT)[::-1]
    return min((word, reverse), key=lambda item: item.translate(ORDER))


def from_fasta(path):
    result = collections.Counter()
    for sequence in fasta_sequences(path):
        for offset in range(len(sequence) - 30):
            word = sequence[offset : offset + 31]
            if all(base in "ACGT" for base in word):
                result[canonical(word)] += 1
    return result


def from_dsk(path):
    result = {}
    duplicate = 0
    with open(path) as handle:
        for line in handle:
            word, abundance = line.split()
            duplicate += word in result
            result[word] = int(abundance)
    return result, duplicate


def compare(name1, fasta1, dsk1, name2, fasta2, dsk2, combined):
    if name1 == name2 or fasta1 == fasta2 or dsk1 == dsk2:
        raise ValueError("Two distinct sample names and input paths are required")
    names = (name1, name2)
    observed = []
    dsk_check = []
    for fasta, ascii_file in ((fasta1, dsk1), (fasta2, dsk2)):
        independent = from_fasta(fasta)
        dsk, duplicates = from_dsk(ascii_file)
        missing = independent.keys() - dsk.keys()
        extra = dsk.keys() - independent.keys()
        wrong = sum(independent[word] != count for word, count in dsk.items() if word in independent)
        dsk_check.append({"independent_count": len(independent), "dsk_count": len(dsk),
                          "missing": len(missing), "extra": len(extra),
                          "abundance_mismatches": wrong, "duplicate_rows": duplicates})
        observed.append(dsk)
    expected = observed[0].keys() & observed[1].keys()
    seen = set()
    errors = collections.Counter()
    examples = []
    with gzip.open(combined, "rt") as handle:
        for line in handle:
            word, *tags = line.split()
            reason = None
            if word in seen:
                errors["duplicate_output_row"] += 1
                reason = "duplicate_output_row"
            seen.add(word)
            if word not in expected:
                errors["extra_or_singleton"] += 1
                reason = "extra_or_singleton"
            else:
                wanted = [f"{name}:{observed[i][word]}" for i, name in enumerate(names)]
                reason = "sample_or_abundance_mismatch" if sorted(tags) != sorted(wanted) else None
                if reason:
                    errors[reason] += 1
            if reason and len(examples) < 8:
                examples.append({"kmer": word, "tags": tags, "error": reason})
    errors["missing_shared"] = len(expected - seen)
    result = {"samples": list(names), "dsk_checks": dsk_check,
              "independent_shared": len(expected), "seer_unique_output": len(seen),
              "seer_errors": dict(errors), "first_errors": examples}
    return result


if __name__ == "__main__":
    if len(sys.argv) != 8:
        raise SystemExit(__doc__)
    report = compare(*sys.argv[1:])
    print(json.dumps(report, indent=2))
    if any(any(value for key, value in check.items() if key not in ("independent_count", "dsk_count"))
           or check["independent_count"] != check["dsk_count"] for check in report["dsk_checks"]):
        raise SystemExit(1)
    if any(report["seer_errors"].values()):
        raise SystemExit(2)
