"""TDD tests for the LRD-vs-SHD JR analysis.

Required by program.md artifact list:
  at minimum assert that parsed SHD JR counts match predecessor project's
  22 SHD-era cases and 14/16 (87.5%) state-loss rate for 2018-2021 within
  the expected tolerance.

Also exercises the ABP-facts table + analysis helpers to verify that
the headline LRD numbers match what the ABP 2024 annual report prints.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).parent.parent
sys.path.insert(0, str(HERE))

from parser_v2 import parse_cases, is_shd, classify_outcome  # noqa: E402
import analysis  # noqa: E402


# ---------------------------------------------------------------------
# Parser + predecessor cross-check
# ---------------------------------------------------------------------
@pytest.fixture(scope="module")
def shd_cases():
    text = (HERE / "data" / "jr_raw.txt").read_text()
    cases = parse_cases(text)
    shd = [c for c in cases if is_shd(c["body"])]
    for c in shd:
        c["outcome"] = classify_outcome(c["body"])
    return shd


def test_total_shd_matches_predecessor(shd_cases):
    """Predecessor project reported 22 SHD cases in OPR Appendix-2."""
    assert abs(len(shd_cases) - 22) <= 1, (
        f"Expected 22 SHD cases ±1, got {len(shd_cases)}"
    )


def test_shd_2018_2021_state_loss_rate(shd_cases):
    """Predecessor headline: 14/16 state losses for SHD 2018-2021.

    program.md-stated acceptance: match predecessor within ±1.
    """
    window = [c for c in shd_cases if c["decision_year"]
              and 2018 <= c["decision_year"] <= 2021]
    losses = sum(1 for c in window if c["outcome"] in ("quashed", "conceded"))
    assert abs(len(window) - 16) <= 1, (
        f"Expected ~16 decided SHD JRs in 2018-2021, got {len(window)}"
    )
    assert abs(losses - 14) <= 1, (
        f"Expected ~14 state losses in 2018-2021, got {losses}"
    )


def test_state_loss_rate_is_between_80_and_95_percent(shd_cases):
    window = [c for c in shd_cases if c["decision_year"]
              and 2018 <= c["decision_year"] <= 2021]
    losses = sum(1 for c in window if c["outcome"] in ("quashed", "conceded"))
    rate = losses / len(window)
    assert 0.80 <= rate <= 0.95, (
        f"SHD 2018-2021 loss rate {rate*100:.1f}% outside expected 80-95% band"
    )


# ---------------------------------------------------------------------
# ABP_FACTS verification against raw text (spot-checks)
# ---------------------------------------------------------------------
def test_abp_2024_jr_lodged_matches_report_text():
    raw = (HERE / "data" / "raw" / "abp_2024.txt").read_text()
    # The ABP 2024 report literally says "147 applications for judicial review"
    assert "147 applications for judicial review" in raw
    assert analysis.ABP_FACTS[2024]["jr_lodged"] == 147


def test_abp_2024_lrd_appeals_received_matches_report_text():
    raw = (HERE / "data" / "raw" / "abp_2024.txt").read_text()
    assert "71 Largescale Residential Development (LRD) appeals" in raw \
        or "received 71 LRD" in raw
    assert analysis.ABP_FACTS[2024]["lrd_appeals_received"] == 71


def test_abp_2023_lrd_appeals_52_matches_report_text():
    raw = (HERE / "data" / "raw" / "abp_2023.txt").read_text()
    assert "52 valid Large-scale Residential Development" in raw \
        or "52 Large-scale Residential Development" in raw
    assert analysis.ABP_FACTS[2023]["lrd_appeals_received"] == 52


def test_abp_2024_table3_lrd_row_is_0_0_2_0():
    """Table 3 of ABP 2024 report: LRD 0/0/2/0 (won/lost/conceded/withdrawn)."""
    assert analysis.ABP_FACTS[2024]["substantive_by_type"]["LRD"] == (0, 0, 2, 0)


# ---------------------------------------------------------------------
# Analysis headline numbers
# ---------------------------------------------------------------------
def test_wilson_ci_shd_87_5_percent():
    lo, hi = analysis.wilson_ci(14, 16)
    assert lo < 0.875 < hi
    # Standard SHD 14/16 Wilson 95% CI is approximately (0.64, 0.97)
    assert 0.55 < lo < 0.75
    assert 0.90 < hi < 1.0


def test_fisher_exact_trivial_equal_rates_gives_high_p():
    p = analysis.fisher_exact_2x2(5, 5, 5, 5)
    assert p > 0.5


def test_fisher_exact_extreme_difference_gives_low_p():
    p = analysis.fisher_exact_2x2(10, 0, 0, 10)
    assert p < 0.01


def test_lrd_denominator_116():
    """LRD appeals concluded 2022+2023+2024 = 1+36+79 = 116."""
    total = (analysis.ABP_FACTS[2022]["lrd_appeals_concluded"]
             + analysis.ABP_FACTS[2023]["lrd_appeals_concluded"]
             + analysis.ABP_FACTS[2024]["lrd_appeals_concluded"])
    assert total == 116


def test_lrd_jr_intake_10():
    """LRD JRs served on the Board 2023 (3) + 2024 intake (7) = 10."""
    n = (analysis.ABP_FACTS[2023]["jrs_by_type_served_2023"]["LRD"]
         + analysis.ABP_FACTS[2024]["jrs_by_type_2024_intake"]["LRD"])
    assert n == 10
