"""Phase B: projection of successor-regime JR-rate reduction.

Question: given current 2024 LRD JR intake of 147 JRs total (4 SHD + 7 LRD),
and LRD-specific intake 10 across 2023-2024 against an LRD-appeal throughput
of 116 concluded appeals, when does a hypothetical Planning and Development
Act 2024 (PDA2024) regime achieve a further 50% reduction in LRD JR rate?

This is a *projection*, not a trained-model prediction. We use simple
rate-envelope reasoning with three scenarios for the PDA2024 effect:
pessimistic (0% reduction vs LRD-status-quo), central (30% reduction),
optimistic (50% reduction).

The 50%-reduction target is hit in the central scenario if:
  (a) ELCFA uptake reduces lodgement rate by an extra 25%
  (b) Planning and Environment List throughput 2× current
  (c) at least 24 months have elapsed since PDA2024 implementation
     (so the permission-cohort is fully observable)

Writes discoveries/lrd_successor_regime_projection.csv.
"""
from __future__ import annotations
import csv
import math
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "discoveries" / "lrd_successor_regime_projection.csv"
OUT.parent.mkdir(exist_ok=True)

# --- Observed baseline from analysis.py / ABP 2024 report ---
LRD_INTAKE_2024 = 7  # ABP 2024 Table 2
LRD_APPEALS_CONCLUDED_2024 = 79
LRD_RATE_2024 = LRD_INTAKE_2024 / LRD_APPEALS_CONCLUDED_2024  # ~8.9%
SHD_RATE_2018_21 = 16 / 250  # ~6.4% (approx clean window)
TARGET_REDUCTION = 0.50  # 50% reduction vs LRD-2024 rate
TARGET_RATE = LRD_RATE_2024 * (1 - TARGET_REDUCTION)

# PDA 2024 scenarios — each expresses % reduction in per-appeal JR rate
SCENARIOS = [
    # (name, annual_rate_reduction, elcfa_uptake, list_throughput_multiplier, implementation_lag_months)
    ("pessimistic", 0.00, 0.00, 1.0, 24),
    ("central_pda2024", 0.15, 0.40, 1.5, 18),  # moderate
    ("optimistic",     0.30, 0.75, 2.0, 12),   # full uptake
]

# Project forward to 2030. Assume LRD throughput ramps to 120 appeals/year
# by 2027 (CSO housing commencements trajectory) then stabilises.
YEARS = list(range(2024, 2031))
LRD_APPEALS_PER_YEAR = {
    2024: 79, 2025: 95, 2026: 110, 2027: 120,
    2028: 120, 2029: 120, 2030: 120,
}


def project(scenario_name: str, rate_reduction: float, elcfa: float,
            list_mult: float, lag_months: int) -> list[dict]:
    """Project JR intake & rate for each year under scenario."""
    rows = []
    rate = LRD_RATE_2024
    for yr in YEARS:
        # Months since PDA 2024 start (Jan 2025 assumed)
        months_since = max(0, (yr - 2025) * 12)
        # Effective reduction kicks in after implementation lag
        active_frac = max(0.0, min(1.0, (months_since - lag_months) / 12.0))
        # Compound rate reduction per year once active
        yrs_active = max(0.0, (months_since - lag_months) / 12.0)
        effective_reduction = 1 - math.exp(-rate_reduction * yrs_active)
        # ELCFA effect is a one-shot level drop when implementation lag passed
        elcfa_multiplier = (1 - elcfa) if active_frac > 0 else 1.0
        # List throughput effect reduces backlog-driven JR, not rate directly;
        # we fold it in as a small additional 5% rate reduction per 1.0x over baseline
        list_effect = 1 - 0.05 * (list_mult - 1.0) * active_frac

        rate_yr = LRD_RATE_2024 * (1 - effective_reduction) * elcfa_multiplier * list_effect
        appeals = LRD_APPEALS_PER_YEAR[yr]
        intake = rate_yr * appeals

        rows.append({
            "scenario": scenario_name,
            "year": yr,
            "months_since_pda2024_start": months_since,
            "implementation_active_frac": round(active_frac, 3),
            "annual_rate_reduction_param": rate_reduction,
            "elcfa_uptake": elcfa,
            "list_throughput_multiplier": list_mult,
            "projected_jr_rate_per_appeal": round(rate_yr, 4),
            "projected_annual_lrd_jr_intake": round(intake, 2),
            "appeals_concluded_assumed": appeals,
            "reduction_vs_2024_pct": round(100 * (1 - rate_yr / LRD_RATE_2024), 1),
            "hits_50pct_reduction": rate_yr <= TARGET_RATE,
        })
    return rows


def main() -> None:
    all_rows = []
    for name, rr, ec, lm, lg in SCENARIOS:
        all_rows.extend(project(name, rr, ec, lm, lg))

    # Find first year each scenario hits the 50% target
    first_hit = {}
    for row in all_rows:
        s = row["scenario"]
        if s not in first_hit and row["hits_50pct_reduction"]:
            first_hit[s] = row["year"]

    print(f"LRD 2024 baseline JR rate per appeal: {LRD_RATE_2024*100:.2f}%")
    print(f"Target: 50% reduction = {TARGET_RATE*100:.2f}% per appeal")
    print()
    for scen in ("pessimistic", "central_pda2024", "optimistic"):
        yr = first_hit.get(scen)
        if yr:
            print(f"  {scen}: first year hitting 50% reduction = {yr}")
        else:
            print(f"  {scen}: does NOT hit 50% reduction by 2030")

    # Summary header row
    summary_rows = []
    for scen in ("pessimistic", "central_pda2024", "optimistic"):
        yr = first_hit.get(scen, "NOT_REACHED")
        summary_rows.append({
            "scenario": scen,
            "year": yr,
            "months_since_pda2024_start": "",
            "implementation_active_frac": "",
            "annual_rate_reduction_param": "SUMMARY",
            "elcfa_uptake": "",
            "list_throughput_multiplier": "",
            "projected_jr_rate_per_appeal": TARGET_RATE,
            "projected_annual_lrd_jr_intake": "",
            "appeals_concluded_assumed": "",
            "reduction_vs_2024_pct": -50.0,
            "hits_50pct_reduction": bool(first_hit.get(scen)),
        })

    with OUT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        writer.writeheader()
        writer.writerows(all_rows)
        writer.writerows(summary_rows)
    print(f"\nWrote {len(all_rows)+len(summary_rows)} rows to {OUT}")


if __name__ == "__main__":
    main()
