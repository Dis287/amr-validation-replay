from src.semantic_replay import BinaryBreakpoint, label_concordance, parse_mic


def test_parse_mic():
    assert parse_mic("<=0.03") == 0.03
    assert parse_mic("0.25") == 0.25
    assert parse_mic(">=32") == 32.0


def test_breakpoint_concordance():
    eu = BinaryBreakpoint("EUCAST", 0.25)
    clsi = BinaryBreakpoint("CLSI", 1.0)
    mics = [0.125, 0.25, 0.38, 0.5, 1.0, 1.5]
    r = label_concordance(mics, eu, clsi)
    assert r["n"] == 6
    assert r["discordant"] == 3
    assert r["concordant"] == 3
