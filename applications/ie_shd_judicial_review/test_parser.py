"""TDD tests for the SHD JR parser.

Ground truth established by manual inspection of the OPR Appendix-2 PDF
raw text. Every SHD case is enumerated below with its decision year and
manually verified outcome label.

Run: python -m pytest test_parser.py -x --tb=short
"""
import re
from pathlib import Path
import pytest

HERE = Path(__file__).parent
RAW = HERE / "data" / "jr_raw.txt"


# ----- Module under test: importable parser -----
from parser_v2 import parse_cases, is_shd, classify_outcome


# ---------- Ground truth ----------
# Manually verified from raw text of OPR Appendix-2 (2012-2022).
# key = case number in the Appendix-2 list. Value = (decision_year, outcome).
# outcome in {"quashed", "conceded", "refused", "dismissed", "upheld"}.
# "upheld" = ABP/state wins on appeal.
GROUND_TRUTH = {
    63:  (2018, "conceded"),    # Clonres CLG v ABP — "Application/challenge conceded by ABP"
    71:  (2019, "quashed"),     # Heather Hill Management — "ABP decision quashed"
    72:  (2019, "quashed"),     # Southwood Park Residents — "permission set aside"
    86:  (2020, "quashed"),     # Redmond v ABP — "Grant order of certiorari quashing"
    94:  (2020, "conceded"),    # Protect East Meath — "ABP conceded; consented to certiorari"
    98:  (2020, "quashed"),     # O'Neill v ABP — "Quash ABP decision to grant permission"
    99:  (2020, "quashed"),     # Crekav Trading — "Grant order of certiorari quashing"
    101: (2020, "refused"),     # Morris v ABP — "Application refused"
    102: (2020, "quashed"),     # Dublin City Council — "Board's decision quashed"
    103: (2020, "quashed"),     # Higgins & Ors v ABP — "Grant certiorari"
    104: (2020, "quashed"),     # Dublin Cycling Campaign — "Quash ABP permission"
    106: (2020, "quashed"),     # Balscadden Road SAA — "Quash ABP permission"
    107: (2020, "quashed"),     # Highland Residents — "Quash ABP permission"
    110: (2021, "dismissed"),   # O'Riordan v ABP — "Application...dismissed as being out of time"
    115: (2021, "quashed"),     # Clonres CLG v ABP (2021) — "Quash ABP decision"
    116: (2021, "quashed"),     # Atlantic Diamond — "ABP decision quashed"
    133: (2022, "quashed"),     # Ballyboden Tidy Towns — "Quash ABP decision"
    137: (2022, "dismissed"),   # Manley Construction — "Application dismissed"
    138: (2022, "refused"),     # Heather Hill (2022) — "Application refused"
    140: (2022, "quashed"),     # Walsh v ABP — "Quash ABP decision to grant permission"
    143: (2022, "quashed"),     # Monkstown Road — "Quash ABP's decision"
    145: (2022, "upheld"),      # Waltham Abbey SC — "Allow the appeal and uphold validity"
}


# ----- Fixture -----
@pytest.fixture(scope="module")
def cases():
    return parse_cases(RAW.read_text())


# ----- Tests -----
def test_parser_finds_at_least_140_cases(cases):
    assert len(cases) >= 140, f"Expected ~144 cases, got {len(cases)}"


def test_parser_assigns_decision_year_from_neutral_citation(cases):
    """Decision year must match the [YYYY] IEHC/IESC/IECA citation, not the record-no year."""
    # Critical regression check: case #99 Crekav — record-no year is 2018, citation is [2020].
    c = next(c for c in cases if c["num"] == 99)
    assert c["decision_year"] == 2020, (
        f"Case 99 decision_year should be 2020 (from [2020] IEHC 400); got {c['decision_year']}"
    )


def test_parser_identifies_all_ground_truth_shd_cases(cases):
    """Every case in GROUND_TRUTH must be detected as SHD-related."""
    shd_nums = {c["num"] for c in cases if is_shd(c["body"])}
    missing = set(GROUND_TRUTH) - shd_nums
    assert not missing, f"Parser failed to flag as SHD: {sorted(missing)}"


def test_parser_total_shd_count_matches_ground_truth(cases):
    shd = [c for c in cases if is_shd(c["body"])]
    assert len(shd) == len(GROUND_TRUTH), (
        f"Expected {len(GROUND_TRUTH)} SHD cases, got {len(shd)}: "
        f"{sorted(c['num'] for c in shd)}"
    )


@pytest.mark.parametrize("case_num,expected_year,expected_outcome", [
    (num, yr, out) for num, (yr, out) in GROUND_TRUTH.items()
])
def test_per_case_year_and_outcome(cases, case_num, expected_year, expected_outcome):
    c = next((c for c in cases if c["num"] == case_num), None)
    assert c is not None, f"Case {case_num} not parsed at all"
    assert c["decision_year"] == expected_year, (
        f"Case {case_num}: year {c['decision_year']} != {expected_year}"
    )
    got_out = classify_outcome(c["body"])
    assert got_out == expected_outcome, (
        f"Case {case_num}: outcome {got_out!r} != {expected_outcome!r}"
    )


def test_state_loss_rate_2018_to_2021(cases):
    """Paper's headline: loss rate over the active SHD regime window."""
    shd = [c for c in cases if is_shd(c["body"])]
    shd_window = [c for c in shd if c["decision_year"] and 2018 <= c["decision_year"] <= 2021]
    state_loss = sum(1 for c in shd_window
                     if classify_outcome(c["body"]) in ("quashed", "conceded"))
    # 63(2018 conceded) + 71,72(2019 quashed) + 86,94,98,99,102,103,104,106,107(2020 q/c) + 115,116(2021 q)
    # = 1 + 2 + 9 + 2 = 14 state losses out of 16 total
    assert len(shd_window) == 16, f"Expected 16 SHD cases 2018-2021, got {len(shd_window)}"
    assert state_loss == 14, f"Expected 14 state losses 2018-2021, got {state_loss}"
