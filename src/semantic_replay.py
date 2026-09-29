from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass(frozen=True)
class BinaryBreakpoint:
    name: str
    non_susceptible_above: float

    def classify(self, mic: float) -> bool:
        return mic > self.non_susceptible_above


def label_concordance(
    mics: Iterable[float],
    a: BinaryBreakpoint,
    b: BinaryBreakpoint,
) -> dict:
    n = concordant = discordant = 0
    a_ns = b_ns = 0

    for mic in mics:
        n += 1
        la = a.classify(mic)
        lb = b.classify(mic)
        a_ns += int(la)
        b_ns += int(lb)
        if la == lb:
            concordant += 1
        else:
            discordant += 1

    if n == 0:
        raise ValueError("No MIC values supplied")

    return {
        "n": n,
        "concordant": concordant,
        "discordant": discordant,
        "concordance": concordant / n,
        "discordance": discordant / n,
        "a_non_susceptible": a_ns,
        "b_non_susceptible": b_ns,
    }


def parse_mic(value: str) -> Optional[float]:
    """Parse numeric magnitude from MIC strings such as '<=0.03', '0.25', '>=32'."""
    import re
    if value is None:
        return None
    match = re.search(r"([0-9]*\.?[0-9]+)", str(value).strip())
    return float(match.group(1)) if match else None
