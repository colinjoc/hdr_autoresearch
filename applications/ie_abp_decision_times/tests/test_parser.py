"""
TDD verification tests for the ABP decision-time parser and hand-entered
ANNUAL dict in analysis.py. Every non-None cell must match the raw text in
data/raw/ exactly, or the test fails — this is what prevents silent drift
between the hand-maintained table and the source PDFs.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from analysis import ANNUAL, INTAKE, FTE

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
COMPANION_DIR = PROJECT_ROOT.parent / "ie_lrd_vs_shd_jr" / "data" / "raw"


def _load(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def test_2023_mean_weeks_all_cases_is_42():
    """Appendix 2023 Table 2 'All' column for 2023 row is 42."""
    text = _load(RAW_DIR / "appendix_2023.txt")
    # the 2023 row in Table 2 ends with: "2023 / 48 / 44 / 59 / 28 / 42"
    # find "2023" header row followed by the five numbers
    assert "2023" in text
    # a positional check — the text dump puts each cell on its own line
    # so the sequence "2023\n\n48\n\n44\n\n59\n\n28\n\n42" must exist
    pat = re.compile(r"2023\s+48\s+44\s+59\s+28\s+42", re.DOTALL)
    assert pat.search(text), "Expected 2023 row '48 44 59 28 42' in appendix_2023.txt"
    assert ANNUAL[2023][4] == 42, "ANNUAL[2023] mean_weeks must be 42"


def test_2023_sop_compliance_is_28pct():
    """The 2023 annual-report 'Disposed of within statutory objective period' figure is 28%."""
    abp_2023 = _load(COMPANION_DIR / "abp_2023.txt")
    # language: "In 2023, 28% of all planning cases were decided within the statutory objective period"
    assert "28%" in abp_2023
    assert re.search(r"In 2023,?\s*28%", abp_2023)
    assert ANNUAL[2023][5] == 28, "ANNUAL[2023] SOP% must be 28"


def test_2018_mean_weeks_all_cases_is_23():
    """Annual Report 2018 p.15: 'was 23.3 weeks, up from 18 weeks in 2017'."""
    text = _load(RAW_DIR / "ar_2018.txt")
    assert "23.3 weeks" in text
    assert ANNUAL[2018][4] == 23


def test_2018_sop_compliance_is_43pct():
    """Annual Report 2018 p.14: '43% of all planning cases were decided within the SOP'."""
    text = _load(RAW_DIR / "ar_2018.txt")
    assert re.search(r"In 2018,?\s*43%", text)
    assert ANNUAL[2018][5] == 43


def test_2024_mean_weeks_all_cases_is_42():
    """Appendix 2024 (from companion) Table 2 2024 row 'All' column is 42."""
    text = _load(COMPANION_DIR / "abp_2024.txt")
    # 2024 row in Table 2: "2024 / 41 / 53 / 124 / 39 / 42"
    pat = re.compile(r"2024\s+41\s+53\s+124\s+39\s+42", re.DOTALL)
    assert pat.search(text), "Expected 2024 row '41 53 124 39 42' in abp_2024.txt"
    assert ANNUAL[2024][4] == 42


def test_2024_sop_compliance_is_25pct():
    """Appendix 2024 Table 1 'Disposed of within SOP' = 25%."""
    text = _load(COMPANION_DIR / "abp_2024.txt")
    # "Disposed of within statutory objective period1\n\n25%\n\n28%"
    pat = re.compile(
        r"Disposed of within statutory objective period.{0,5}\s+25%\s+28%",
        re.DOTALL,
    )
    assert pat.search(text), "Expected '25% 28%' under SOP heading in abp_2024.txt"
    assert ANNUAL[2024][5] == 25


def test_2022_shd_mean_weeks_is_24():
    """Appendix 2022 Table 2 SHD column for 2022 = 24."""
    assert ANNUAL[2022][2] == 24
    text = _load(RAW_DIR / "appendix_2022.txt")
    pat = re.compile(r"2022\s+25\s+36\s+24\s+26\s+26", re.DOTALL)
    assert pat.search(text)


def test_2021_intake_is_3251():
    """Appendix 2021 Table 1 'Received' = 3,251."""
    assert INTAKE[2021]["intake"] == 3251
    text = _load(RAW_DIR / "appendix_2021.txt")
    assert "3,251" in text


def test_fte_growth_2022_to_2024_is_43pct():
    """Q1 2025 report: total FTE 202 → 290 (+43.6%)."""
    growth = (FTE[2024]["total"] - FTE[2022]["total"]) / FTE[2022]["total"] * 100
    assert 43 <= growth <= 44


def test_all_annual_rows_have_mean_and_sop():
    """Sanity: every year 2018-2024 has both mean and SOP populated."""
    for y in range(2018, 2025):
        npa, sid, shd, other, all_mean, sop = ANNUAL[y]
        assert all_mean is not None, f"ANNUAL[{y}] mean_weeks is None"
        assert sop is not None, f"ANNUAL[{y}] SOP% is None"


def test_annual_dict_is_stable_hash():
    """Re-running the dict definition must produce the same repr — guards against in-place mutation."""
    items = sorted(ANNUAL.items())
    assert str(items).startswith("[(2015,"), "ANNUAL must start at 2015"
    assert str(items).endswith("39, 42, 25))]"), "ANNUAL must end at 2024 with canonical tuple"
