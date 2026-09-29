from src.metric_replay import balanced_accuracy


def test_balanced_accuracy():
    r = balanced_accuracy(
        y_true=[1, 1, 0, 0],
        y_pred=[1, 0, 0, 0],
    )
    assert r.sensitivity == 0.5
    assert r.specificity == 1.0
    assert r.balanced_accuracy == 0.75
