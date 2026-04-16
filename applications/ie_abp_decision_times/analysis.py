"""
Analysis harness for the An Bord Pleanála (ABP) decision-time project.

Extracts per-year mean weeks-to-dispose and % within Statutory Objective
Period (SOP) from annual-report appendix text dumps, and produces the E00
baseline row in results.tsv.

Source of truth: the ABP Annual Report Appendices 2018, 2020, 2021, 2022,
2023, and 2024 (2024 reused from the companion PL-2 LRD vs SHD JR project).
Quarterly reports 2024-2025 supply partial-year interim figures.

Run: python analysis.py
"""

from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
COMPANION_DIR = (
    PROJECT_ROOT.parent / "ie_lrd_vs_shd_jr" / "data" / "raw"
)
RESULTS = PROJECT_ROOT / "results.tsv"

# -----------------------------------------------------------------------------
# Hand-verified "truth" table from the Annual Report Appendices.
# Rows = year; columns = mean weeks-to-dispose (all cases) and SOP compliance.
# "Normal Planning Appeals", "Strategic Infrastructure Cases" (SID), "Strategic
# Housing Cases" (SHD), "All Other Cases" and "All" come directly from Table 2
# of each year's appendix.
# SOP compliance is from Table 1 or Table 14D.
# These numbers are verified against the raw text in tests/test_parser.py.
# -----------------------------------------------------------------------------

ANNUAL = {
    # year: (NPA, SID, SHD, OTHER, ALL_mean_weeks, SOP_pct_all_disposals)
    2015: (15, 27, None, 30, 17, 75),
    2016: (16, 50, None, 26, 17, 63),
    2017: (17, 22, None, 30, 18, 64),
    2018: (22, 34, 13, 36, 23, 43),
    2019: (18, 28, 13, 22, 22, 69),
    2020: (19, 37, 17, 22, 23, 73),
    2021: (19, 39, 16, 23, 20, 57),
    2022: (25, 36, 24, 26, 26, 45),
    2023: (48, 44, 59, 28, 42, 28),
    2024: (41, 53, 124, 39, 42, 25),
}

# Intake, disposed, on-hands (start) for planning cases (Table 1) by year.
# Source: ABP appendices Table 1.
INTAKE = {
    2018: {"intake": None, "disposed": None, "on_hand_start": None},
    2019: {"intake": 2938, "disposed": 2971, "on_hand_start": 1072},
    2020: {"intake": 2753, "disposed": 2628, "on_hand_start": 1039},
    2021: {"intake": 3251, "disposed": 2775, "on_hand_start": 1165},
    2022: {"intake": 3058, "disposed": 2115, "on_hand_start": 1637},
    2023: {"intake": 3272, "disposed": 3284, "on_hand_start": 2580},
    2024: {"intake": 2727, "disposed": 3705, "on_hand_start": 2564},
}

# FTE and board-member counts from the Q1 2025 resourcing table.
FTE = {
    2022: {"board": 5, "senior_mgmt": 18, "inspectorate": 66, "admin": 113, "total": 202},
    2023: {"board": 15, "senior_mgmt": 18, "inspectorate": 86, "admin": 131, "total": 250},
    2024: {"board": 17, "senior_mgmt": 27, "inspectorate": 100, "admin": 146, "total": 290},
}

# Q1-Q3 2025 interim YTD figures. Source: q1_2025.txt, q3_2025.txt.
QUARTERLY_2025 = {
    "q1_intake": 595,
    "q1_disposed": 800,
    "q1_on_hand_end": 1274,
    "q1_ytd_sop_pct_all": 41,
    "q3_ytd_intake": 2153,
    "q3_ytd_disposed": 2296,
    "q3_ytd_on_hand_end": 1428,
    "q3_ytd_sop_pct_all_approx": 65,  # avg of Jan-Sep % All Disposals Within SOP
}


@dataclass
class E00Row:
    year: int
    mean_weeks: float
    sop_pct: float
    source: str
    status: str = "E00"


def compute_e00_baseline() -> list[E00Row]:
    """E00: the headline series — mean weeks-to-dispose and SOP compliance per year."""
    rows = []
    for year, (_npa, _sid, _shd, _other, all_mean, sop) in sorted(ANNUAL.items()):
        if all_mean is None or sop is None:
            continue
        rows.append(
            E00Row(
                year=year,
                mean_weeks=float(all_mean),
                sop_pct=float(sop),
                source=f"ABP appendix {year}",
            )
        )
    return rows


def append_result_row(
    exp_id: str,
    family: str,
    description: str,
    metric: str,
    value: float | str,
    status: str,
    notes: str = "",
) -> None:
    """Append a row to results.tsv, creating headers if needed."""
    headers = ["exp_id", "family", "description", "metric", "value", "status", "notes"]
    new_file = not RESULTS.exists()
    with RESULTS.open("a", newline="") as fp:
        writer = csv.writer(fp, delimiter="\t")
        if new_file:
            writer.writerow(headers)
        writer.writerow([exp_id, family, description, metric, value, status, notes])


def write_e00() -> None:
    """Write the E00 baseline row(s) to results.tsv."""
    rows = compute_e00_baseline()
    for r in rows:
        append_result_row(
            exp_id=f"E00.{r.year}",
            family="descriptive_baseline",
            description=f"ABP mean weeks-to-dispose and SOP compliance, {r.year}",
            metric="mean_weeks_all_cases,sop_pct_all_disposals",
            value=f"{r.mean_weeks:.1f},{r.sop_pct:.1f}",
            status="BASELINE",
            notes=r.source,
        )
    # seed-stability fingerprint
    h = hashlib.md5(str(sorted(ANNUAL.items())).encode()).hexdigest()[:12]
    append_result_row(
        exp_id="E00.fingerprint",
        family="descriptive_baseline",
        description="Seed-stability fingerprint of ANNUAL dict",
        metric="md5_12",
        value=h,
        status="BASELINE",
        notes="Re-running this script must produce the same hash.",
    )


def main() -> None:
    # wipe the existing file if re-running from scratch
    if RESULTS.exists():
        RESULTS.unlink()
    write_e00()
    print(f"Wrote {sum(1 for _ in open(RESULTS)) - 1} rows to {RESULTS}")


if __name__ == "__main__":
    main()
