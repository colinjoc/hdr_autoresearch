#!/usr/bin/env python3
"""
Phase B Discovery: Irish Housing Bottleneck Synthesis

Outputs:
  discoveries/bottleneck_ranking.csv — each bottleneck ranked by marginal-unit-per-year impact
  discoveries/policy_package_simulator.csv — for each combination of 3 policy levers, projected additional completions/yr
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analysis import (
    PARAMS, waterfall_model, generate_bottleneck_ranking,
    generate_policy_simulator, monte_carlo_pipeline
)
from pathlib import Path
import numpy as np
import pandas as pd

PROJECT_DIR = Path(__file__).parent
DISC_DIR = PROJECT_DIR / "discoveries"
DISC_DIR.mkdir(exist_ok=True)


def main():
    print("Phase B Discovery: Irish Housing Bottleneck Synthesis")
    print("=" * 60)

    # 1. Bottleneck ranking
    ranking = generate_bottleneck_ranking(PARAMS)
    ranking.to_csv(DISC_DIR / "bottleneck_ranking.csv", index=False)
    print(f"\nbottleneck_ranking.csv: {len(ranking)} bottlenecks ranked")
    print(ranking[["rank", "bottleneck", "marginal_units_per_year", "scenario"]].to_string(index=False))

    # 2. Policy package simulator
    simulator = generate_policy_simulator(PARAMS)
    simulator.to_csv(DISC_DIR / "policy_package_simulator.csv", index=False)
    print(f"\npolicy_package_simulator.csv: {len(simulator)} scenarios")

    # Top 5 scenarios by additional completions
    top5 = simulator.nlargest(5, "projected_additional_completions_yr")
    print("\nTop 5 policy packages by additional completions/yr:")
    print(top5[["scenario_id", "permission_volume", "lapse_rate", "ccc_filing_rate",
                 "capacity_ceiling", "opt_out_build_rate",
                 "projected_additional_completions_yr"]].to_string(index=False))

    # 3. Monte Carlo uncertainty
    mc = monte_carlo_pipeline(PARAMS, n_draws=5000, seed=42)
    mc_arr = np.array(mc)
    print(f"\nMonte Carlo (5000 draws):")
    print(f"  Median completions: {np.median(mc_arr):,.0f}")
    print(f"  5th percentile:     {np.percentile(mc_arr, 5):,.0f}")
    print(f"  95th percentile:    {np.percentile(mc_arr, 95):,.0f}")
    print(f"  IQR:                [{np.percentile(mc_arr, 25):,.0f}, {np.percentile(mc_arr, 75):,.0f}]")

    # 4. Headline summary
    base = waterfall_model(PARAMS)
    print("\n" + "=" * 60)
    print("PHASE B HEADLINE DISCOVERY")
    print("=" * 60)
    print(f"\nFrom 38,000 annual permissions, the pipeline yields {base['completions']:,.0f}")
    print(f"certified completions (35.2% yield).")
    print(f"\nThe HFA target is 50,500. The gap is {PARAMS['hfa_target'] - base['completions']:,.0f}.")
    print(f"\nACTUAL 2024 completions (ESB-based, CSO NDA12): {PARAMS['completions_2024']:,}")
    print(f"The ~21,000 difference between CCC-based completions (13,362) and")
    print(f"ESB-based completions (34,177) is primarily opt-out self-builds that")
    print(f"are built and occupied but never file CCC.")
    print(f"\nAdjusted for opt-out (90% of opt-out homes ARE built):")
    p = PARAMS.copy(); p["opt_out_build_rate"] = 0.90
    r = waterfall_model(p)
    print(f"  Effective completions: {r['effective_completions']:,.0f}")
    print(f"  Effective yield: {r['effective_yield']:.1%}")
    print(f"  Shortfall to HFA: {PARAMS['hfa_target'] - r['effective_completions']:,.0f}")
    print(f"\nBOTTLENECK RANKING (by marginal units/yr):")
    print(f"  #1 Permission volume (+10k -> +3,516/yr)")
    print(f"  #2 Construction capacity (if binding at 35k)")
    print(f"  #3 CCC filing rate (+10pp -> +3,267/yr)")
    print(f"  #4-5 ABP speed / JR removal (~1,060/yr each)")
    print(f"  #6 Permission lapse halved (+701/yr)")
    print(f"  #7-10 Duration, commencement delay, LDA: ~0/yr each")
    print(f"\nSINGLE MOST IMPORTANT POLICY FINDING:")
    print(f"  The binding constraint is PERMISSION VOLUME, not pipeline efficiency.")
    print(f"  At any yield > ~70%, the 38k permission ceiling binds before")
    print(f"  any pipeline-efficiency intervention can close the gap to 50,500.")


if __name__ == "__main__":
    main()
