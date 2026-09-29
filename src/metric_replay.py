from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class BalancedAccuracy:
    balanced_accuracy: float
    sensitivity: float
    specificity: float
    tp: int
    tn: int
    fp: int
    fn: int


def balanced_accuracy(y_true: Iterable[int], y_pred: Iterable[int]) -> BalancedAccuracy:
    tp = tn = fp = fn = 0
    for y, p in zip(y_true, y_pred):
        if p == 1 and y == 1:
            tp += 1
        elif p == 0 and y == 0:
            tn += 1
        elif p == 1 and y == 0:
            fp += 1
        else:
            fn += 1

    if tp + fn == 0 or tn + fp == 0:
        raise ValueError("Balanced accuracy requires both classes")

    sensitivity = tp / (tp + fn)
    specificity = tn / (tn + fp)
    return BalancedAccuracy(
        balanced_accuracy=(sensitivity + specificity) / 2,
        sensitivity=sensitivity,
        specificity=specificity,
        tp=tp,
        tn=tn,
        fp=fp,
        fn=fn,
    )
