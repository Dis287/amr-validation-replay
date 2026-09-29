import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.semantic_replay import BinaryBreakpoint, parse_mic, label_concordance


def main(csv_path: str):
    values = []
    with open(csv_path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            mic = parse_mic(row.get("AZM MIC"))
            if mic is not None:
                values.append(mic)

    result = label_concordance(
        values,
        BinaryBreakpoint("EUCAST", 0.25),
        BinaryBreakpoint("CLSI", 1.0),
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python run.py <processed_gonococcal_csv>")
    main(sys.argv[1])
