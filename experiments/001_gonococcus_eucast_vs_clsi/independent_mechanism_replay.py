from __future__ import annotations

import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


FEATURES = ("MtrA", "MtrC", "FarA", "Mtr_Upregulation")


def parse_mic(value: str):
    m = re.search(r"([0-9]*\.?[0-9]+)", str(value))
    return float(m.group(1)) if m else None


def fnv1a_32(text: str) -> int:
    h = 2166136261
    for ch in text:
        h ^= ord(ch)
        h = (h * 16777619) & 0xFFFFFFFF
    return h


def bacc(rows, predictions, label):
    tp = tn = fp = fn = 0
    for r in rows:
        y = r[label]
        p = predictions[r["id"]]
        if p == 1 and y == 1:
            tp += 1
        elif p == 0 and y == 0:
            tn += 1
        elif p == 1:
            fp += 1
        else:
            fn += 1

    sensitivity = tp / (tp + fn)
    specificity = tn / (tn + fp)
    return {
        "balanced_accuracy": (sensitivity + specificity) / 2,
        "sensitivity": sensitivity,
        "specificity": specificity,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
    }


def out_of_fold_predictions(rows, label):
    predictions = {}

    for fold in range(5):
        train = [r for r in rows if r["fold"] != fold]
        test = [r for r in rows if r["fold"] == fold]

        n_ns = sum(r[label] for r in train)
        n_s = len(train) - n_ns
        counts = defaultdict(lambda: [0, 0])

        for r in train:
            counts[r["pattern"]][r[label]] += 1

        n_patterns = max(len(counts), 1)

        for r in test:
            s_count, ns_count = counts[r["pattern"]]
            p_pattern_given_ns = (ns_count + 1) / (n_ns + n_patterns)
            p_pattern_given_s = (s_count + 1) / (n_s + n_patterns)
            predictions[r["id"]] = int(p_pattern_given_ns > p_pattern_given_s)

    return predictions


def load_rows(cabbage_csv: Path, mechanism_csv: Path):
    with mechanism_csv.open(newline="", encoding="utf-8") as fh:
        mechanisms = {r["Accession"]: r for r in csv.DictReader(fh)}

    rows = []
    with cabbage_csv.open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            accession = r["Run ID"]
            m = mechanisms.get(accession)
            if m is None:
                continue

            azm_mic = parse_mic(r["AZM MIC"])
            if azm_mic is None:
                continue

            pattern = "|".join((m.get(k) or "UNK") for k in FEATURES)
            rows.append(
                {
                    "id": accession,
                    "pattern": pattern,
                    "eu": int(azm_mic > 0.25),
                    "clsi": int(azm_mic > 1.0),
                    "fold": fnv1a_32(accession) % 5,
                }
            )

    return rows


def main(cabbage_csv: str, mechanism_csv: str):
    rows = load_rows(Path(cabbage_csv), Path(mechanism_csv))

    pred_eu = out_of_fold_predictions(rows, "eu")
    pred_clsi = out_of_fold_predictions(rows, "clsi")

    eu_on_eu = bacc(rows, pred_eu, "eu")
    eu_on_clsi = bacc(rows, pred_eu, "clsi")
    clsi_on_clsi = bacc(rows, pred_clsi, "clsi")

    result = {
        "n": len(rows),
        "eu_model_on_eu": eu_on_eu,
        "same_eu_predictions_on_clsi": eu_on_clsi,
        "semantics_only_bacc_delta":
            eu_on_clsi["balanced_accuracy"] - eu_on_eu["balanced_accuracy"],
        "clsi_model_on_clsi": clsi_on_clsi,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(
            "usage: python independent_mechanism_replay.py "
            "<CABBAGE_processed_gonococcus.csv> <gradlab_strain_table.csv>"
        )
    main(sys.argv[1], sys.argv[2])
