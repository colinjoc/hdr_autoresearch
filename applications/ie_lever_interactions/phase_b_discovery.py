"""
Phase B: Discovery — optimal housing policy packages for Ireland.

Outputs:
  discoveries/optimal_packages.csv — Top-10 lever combinations ranked by completions/yr
  discoveries/interaction_matrix.csv — 45-cell pairwise interaction matrix
  discoveries/pareto_frontier.csv — 3-lever combos on the efficiency frontier
"""

import numpy as np
import csv
import os
from itertools import combinations

from feedback_model import (
    run_feedback_loop, generate_full_factorial,
    BASELINE, LEVER_SETTINGS, LEVER_NAMES, describe_levers
)

DISC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'discoveries')
os.makedirs(DISC_DIR, exist_ok=True)


def soft_ceiling_model(gross, base_ceiling=35000, wf_mult=1.0, congestion=0.02):
    """Soft capacity ceiling: above capacity, marginal cost rises."""
    effective_ceiling = base_ceiling * wf_mult
    if gross <= effective_ceiling:
        return gross
    excess = gross - effective_ceiling
    delivered_excess = excess / (1 + congestion * excess / effective_ceiling * 10)
    return effective_ceiling + delivered_excess


def main():
    max_settings = {
        "duration_reduction": 0.50, "modular_reduction": 0.30, "vat_rate": 0.0,
        "part_v_rate": 0.0, "dev_contribs_fraction": 0.0, "bcar_fraction": 0.0,
        "land_cost_multiplier": 0.1, "finance_rate_new": 0.03,
        "developer_margin_new": 0.06, "workforce_multiplier": 1.5,
    }
    lever_costs_max = {
        "duration_reduction": 0, "modular_reduction": 300e6, "vat_rate": 1400e6,
        "part_v_rate": 400e6, "dev_contribs_fraction": 300e6, "bcar_fraction": 40e6,
        "land_cost_multiplier": 1500e6, "finance_rate_new": 500e6,
        "developer_margin_new": 0, "workforce_multiplier": 600e6,
    }

    # ====== 1. OPTIMAL PACKAGES (full factorial, top 10) ======
    print("Computing full factorial (104,976 combinations)...")
    combos = generate_full_factorial()
    all_results = []
    for combo in combos:
        r = run_feedback_loop(combo)
        wf = combo.get("workforce_multiplier", 1.0)
        soft = soft_ceiling_model(r["gross_completions_uncapped"], wf_mult=wf)
        all_results.append({
            "description": describe_levers(combo),
            "cost_reduction_pct": round(r["cost_reduction"] * 100, 1),
            "gross_completions": round(r["gross_completions_uncapped"]),
            "hard_ceiling_completions": round(r["completions"]),
            "soft_ceiling_completions": round(soft),
            "net_additional": round(soft - 35000),
        })

    all_results.sort(key=lambda x: x["soft_ceiling_completions"], reverse=True)

    with open(os.path.join(DISC_DIR, 'optimal_packages.csv'), 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["rank", "description", "cost_reduction_pct",
                                                "gross_completions", "hard_ceiling_completions",
                                                "soft_ceiling_completions", "net_additional"])
        writer.writeheader()
        for i, row in enumerate(all_results[:10], 1):
            row["rank"] = i
            writer.writerow(row)
    print(f"  -> discoveries/optimal_packages.csv (top 10 of {len(all_results):,})")

    # ====== 2. INTERACTION MATRIX (45 unique pairs) ======
    print("Computing pairwise interaction matrix (45 pairs)...")
    lever_names_ordered = list(LEVER_SETTINGS.keys())
    base_soft = soft_ceiling_model(35000)
    interactions = []

    for i, la in enumerate(lever_names_ordered):
        for j, lb in enumerate(lever_names_ordered):
            if j <= i:
                continue
            la_d = {la: max_settings[la]}
            lb_d = {lb: max_settings[lb]}
            lab_d = {la: max_settings[la], lb: max_settings[lb]}

            r_a = run_feedback_loop(la_d)
            r_b = run_feedback_loop(lb_d)
            r_ab = run_feedback_loop(lab_d)

            wf_a = la_d.get("workforce_multiplier", 1.0)
            wf_b = lb_d.get("workforce_multiplier", 1.0)
            wf_ab = lab_d.get("workforce_multiplier", 1.0)

            s_a = soft_ceiling_model(r_a["gross_completions_uncapped"], wf_mult=wf_a)
            s_b = soft_ceiling_model(r_b["gross_completions_uncapped"], wf_mult=wf_b)
            s_ab = soft_ceiling_model(r_ab["gross_completions_uncapped"], wf_mult=wf_ab)

            interaction = s_ab - (s_a + s_b - base_soft)
            sign = "synergy" if interaction > 100 else ("redundancy" if interaction < -100 else "neutral")

            interactions.append({
                "lever_a": LEVER_NAMES[la],
                "lever_b": LEVER_NAMES[lb],
                "interaction_units": round(interaction),
                "sign": sign,
            })

    interactions.sort(key=lambda x: x["interaction_units"], reverse=True)

    with open(os.path.join(DISC_DIR, 'interaction_matrix.csv'), 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["lever_a", "lever_b", "interaction_units", "sign"])
        writer.writeheader()
        for row in interactions:
            writer.writerow(row)
    print(f"  -> discoveries/interaction_matrix.csv ({len(interactions)} pairs)")

    # ====== 3. PARETO FRONTIER (3-lever combos) ======
    print("Computing Pareto frontier (3-lever combinations)...")
    lever_list = list(LEVER_SETTINGS.keys())
    pareto_data = []

    for combo_keys in combinations(lever_list, 3):
        levers = {k: max_settings[k] for k in combo_keys}
        cost = sum(lever_costs_max[k] for k in combo_keys)
        r = run_feedback_loop(levers)
        wf = levers.get("workforce_multiplier", 1.0)
        soft = soft_ceiling_model(r["gross_completions_uncapped"], wf_mult=wf)

        names = " + ".join([LEVER_NAMES[k] for k in combo_keys])
        pareto_data.append({
            "levers": names,
            "soft_completions": round(soft),
            "gross_completions": round(r["gross_completions_uncapped"]),
            "fiscal_cost_eur_m": round(cost / 1e6),
            "cost_effectiveness": round(soft / max(cost / 1e6, 1), 1),
        })

    # Compute Pareto frontier
    pareto_sorted = sorted(pareto_data, key=lambda x: x["soft_completions"], reverse=True)
    frontier = []
    min_cost = float('inf')
    for row in pareto_sorted:
        if row["fiscal_cost_eur_m"] < min_cost:
            frontier.append(row)
            min_cost = row["fiscal_cost_eur_m"]

    with open(os.path.join(DISC_DIR, 'pareto_frontier.csv'), 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["levers", "soft_completions", "gross_completions",
                                                "fiscal_cost_eur_m", "cost_effectiveness"])
        writer.writeheader()
        for row in frontier:
            writer.writerow(row)
    print(f"  -> discoveries/pareto_frontier.csv ({len(frontier)} frontier points)")

    # ====== SUMMARY ======
    print("\n" + "=" * 60)
    print("DISCOVERY SUMMARY")
    print("=" * 60)
    print(f"\nOptimal package: {all_results[0]['description'][:80]}")
    print(f"  Soft-ceiling completions: {all_results[0]['soft_ceiling_completions']:,}/yr")
    print(f"  Net additional: +{all_results[0]['net_additional']:,}/yr")
    print(f"\nLargest synergy: {interactions[0]['lever_a']} x {interactions[0]['lever_b']} = +{interactions[0]['interaction_units']:,}")
    print(f"Largest redundancy: {interactions[-1]['lever_a']} x {interactions[-1]['lever_b']} = {interactions[-1]['interaction_units']:,}")
    print(f"\nPareto-efficient 3-lever combo: {frontier[0]['levers']}")
    print(f"  Completions: {frontier[0]['soft_completions']:,}/yr at €{frontier[0]['fiscal_cost_eur_m']}M")


if __name__ == "__main__":
    main()
