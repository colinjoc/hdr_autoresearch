"""
Run all mandated reviewer experiments (RV01–RV06) from paper_review.md.
Appends results to results.tsv.
"""
import sys
import os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feedback_model import (
    run_feedback_loop, compute_cost_reduction, BASELINE, LEVER_SETTINGS,
    run_monte_carlo
)

def soft_ceiling_model(gross, base_ceiling=35000, wf_mult=1.0, congestion=0.02):
    effective_ceiling = base_ceiling * wf_mult
    if gross <= effective_ceiling:
        return gross
    excess = gross - effective_ceiling
    delivered_excess = excess / (1 + congestion * excess / effective_ceiling * 10)
    return effective_ceiling + delivered_excess


EVERYTHING = {
    "duration_reduction": 0.50, "modular_reduction": 0.30, "vat_rate": 0.0,
    "part_v_rate": 0.0, "dev_contribs_fraction": 0.0, "bcar_fraction": 0.0,
    "land_cost_multiplier": 0.1, "finance_rate_new": 0.03,
    "developer_margin_new": 0.06, "workforce_multiplier": 1.5,
}

FEASIBLE = {
    "duration_reduction": 0.25, "modular_reduction": 0.10, "vat_rate": 0.09,
    "part_v_rate": 0.10, "dev_contribs_fraction": 0.5,
}

results = []

# ============ RV01: Workforce ramp-rate sensitivity ============
print("RV01: Workforce ramp-rate sensitivity...")
# Current workforce ~160k. +50% = 80k additional.
# Scenarios: +5k/yr (SOLAS), +10k/yr (optimistic), +20k/yr (unprecedented)
current_workforce = 160_000
target_additional = 80_000  # for +50%

for rate_name, workers_per_year in [("SOLAS_5k", 5000), ("optimistic_10k", 10000), ("unprecedented_20k", 20000)]:
    for year in range(1, 11):
        additional = min(workers_per_year * year, target_additional)
        wf_mult = 1.0 + additional / current_workforce
        # Use everything package but with computed workforce multiplier
        levers = {k: v for k, v in EVERYTHING.items() if k != "workforce_multiplier"}
        levers["workforce_multiplier"] = wf_mult
        r = run_feedback_loop(levers)
        soft = soft_ceiling_model(r["gross_completions_uncapped"], wf_mult=wf_mult)
        results.append({
            "id": f"RV01_{rate_name}_yr{year}",
            "desc": f"WF ramp {rate_name} year {year}: mult={wf_mult:.3f}",
            "status": "RUN_RV",
            "cost_red": round(r["cost_reduction"] * 100, 1),
            "viab": round(r["viability_margin"] * 100, 1),
            "gross": round(r["gross_completions_uncapped"]),
            "hard": round(r["completions"]),
            "soft": round(soft),
            "ceiling": round(35000 * wf_mult),
            "notes": f"WF +{additional} workers, mult {wf_mult:.3f}"
        })

# Summary: years to reach target for each scenario
for rate_name, workers_per_year in [("SOLAS_5k", 5000), ("optimistic_10k", 10000), ("unprecedented_20k", 20000)]:
    years_to_target = min(int(np.ceil(target_additional / workers_per_year)), 99)
    print(f"  {rate_name}: {years_to_target} years to +50% workforce")

# ============ RV02: Diminishing-returns workforce model ============
print("\nRV02: Diminishing-returns workforce model...")

def diminishing_workforce_capacity(additional_workers, base_capacity=35000,
                                     base_workforce=160000, decay_rate=0.5):
    """Diminishing returns: each additional worker adds less capacity.
    effective_additional = additional * (base / (base + additional))^decay_rate
    """
    if additional_workers <= 0:
        return base_capacity
    ratio = base_workforce / (base_workforce + additional_workers)
    effective_mult = ratio ** decay_rate
    per_worker_capacity = base_capacity / base_workforce  # 0.21875 units/worker
    effective_additional = additional_workers * per_worker_capacity * effective_mult
    return base_capacity + effective_additional

for additional in [0, 20000, 40000, 60000, 80000, 120000]:
    eff_cap = diminishing_workforce_capacity(additional)
    linear_cap = 35000 * (1 + additional / 160000)
    levers = {k: v for k, v in EVERYTHING.items() if k != "workforce_multiplier"}
    # Use the diminishing capacity directly
    r = run_feedback_loop(levers, capacity_ceiling=eff_cap)
    soft = soft_ceiling_model(r["gross_completions_uncapped"],
                               base_ceiling=eff_cap, wf_mult=1.0)
    results.append({
        "id": f"RV02_dim_{additional}",
        "desc": f"Dim-returns WF +{additional}: eff_cap={eff_cap:.0f} vs linear={linear_cap:.0f}",
        "status": "RUN_RV",
        "cost_red": round(r["cost_reduction"] * 100, 1),
        "viab": round(r["viability_margin"] * 100, 1),
        "gross": round(r["gross_completions_uncapped"]),
        "hard": round(min(r["gross_completions_uncapped"], eff_cap)),
        "soft": round(soft),
        "ceiling": round(eff_cap),
        "notes": f"Diminishing returns: +{additional} workers, eff_cap={eff_cap:.0f}, linear={linear_cap:.0f}"
    })

# ============ RV03: Saturating elasticity (tanh) ============
print("\nRV03: Saturating elasticity (tanh)...")

def run_with_tanh_elasticity(levers, k=1.0):
    """Replace linear elasticity with tanh saturation."""
    cost_red = compute_cost_reduction(levers)
    viability_delta = cost_red
    scale_factor = 0.10
    r = BASELINE["viability_apps_r"]
    # Saturating: tanh(x) ≈ x for small x, saturates at ±1
    x = viability_delta / scale_factor * k
    app_multiplier = 1.0 + r * np.tanh(x) / k  # normalised so small x ≈ linear

    baseline_apps = BASELINE["current_completions"] / (BASELINE["approval_rate"] * BASELINE["build_yield"])
    apps = baseline_apps * max(app_multiplier, 0.1)
    perms = apps * BASELINE["approval_rate"]
    gross = perms * BASELINE["build_yield"]

    wf_mult = levers.get("workforce_multiplier", 1.0)
    ceiling = BASELINE["capacity_ceiling"] * wf_mult
    hard = min(gross, ceiling)
    soft = soft_ceiling_model(gross, wf_mult=wf_mult)

    return gross, hard, soft, cost_red, app_multiplier

for k in [0.5, 1.0, 2.0]:
    for pkg_name, pkg_levers in [("everything", EVERYTHING), ("feasible", FEASIBLE)]:
        gross, hard, soft, cr, am = run_with_tanh_elasticity(pkg_levers, k=k)
        # Compare to linear
        r_linear = run_feedback_loop(pkg_levers)
        wf = pkg_levers.get("workforce_multiplier", 1.0)
        soft_linear = soft_ceiling_model(r_linear["gross_completions_uncapped"], wf_mult=wf)
        results.append({
            "id": f"RV03_tanh_k{k}_{pkg_name}",
            "desc": f"Tanh elasticity k={k} {pkg_name}: soft={soft:.0f} vs linear={soft_linear:.0f}",
            "status": "RUN_RV",
            "cost_red": round(cr * 100, 1),
            "viab": round((BASELINE["viability_margin"] + cr) * 100, 1),
            "gross": round(gross),
            "hard": round(hard),
            "soft": round(soft),
            "ceiling": round(35000 * wf),
            "notes": f"Tanh k={k}, app_mult={am:.2f}, linear_soft={soft_linear:.0f}"
        })

# ============ RV04: First-order GE price correction ============
print("\nRV04: First-order GE price correction...")

def ge_corrected_completions(levers, demand_elasticity=-0.5):
    """Single-step GE correction.
    1. Compute unconstrained supply
    2. Compute implied price change from demand_elasticity
    3. Subtract margin compression from cost reduction
    4. Re-run with corrected cost reduction
    """
    r = run_feedback_loop(levers)
    wf = levers.get("workforce_multiplier", 1.0)
    soft_supply = soft_ceiling_model(r["gross_completions_uncapped"], wf_mult=wf)

    # Supply increase as fraction
    supply_increase = (soft_supply - 35000) / 35000
    if supply_increase <= 0:
        return soft_supply, 0, r["cost_reduction"]

    # Price change: delta_p / p = (delta_q / q) / elasticity
    # elasticity = -0.5 means 1% supply increase => 2% price decrease
    price_change = supply_increase / abs(demand_elasticity)  # fraction price drop

    # Margin compression: the developer's margin is squeezed by price_change
    # Net cost reduction = original cost_red - price_change
    original_cr = r["cost_reduction"]
    effective_cr = max(original_cr - price_change, 0)

    # Re-compute with effective cost reduction
    # Use the linear formula: gross = 35000 * (1 + 9.1 * cr)
    gross_corrected = 35000 * (1 + 9.1 * effective_cr)
    soft_corrected = soft_ceiling_model(gross_corrected, wf_mult=wf)

    return soft_corrected, price_change, effective_cr

for pkg_name, pkg_levers in [("baseline", {}), ("feasible", FEASIBLE),
                               ("feasible_wf12", {**FEASIBLE, "workforce_multiplier": 1.2}),
                               ("radical_wf15", {"duration_reduction":0.33, "modular_reduction":0.20,
                                                  "vat_rate":0.0, "part_v_rate":0.0,
                                                  "dev_contribs_fraction":0.0,
                                                  "land_cost_multiplier":0.1,
                                                  "workforce_multiplier":1.5}),
                               ("everything", EVERYTHING)]:
    soft_ge, price_drop, eff_cr = ge_corrected_completions(pkg_levers)
    r = run_feedback_loop(pkg_levers)
    wf = pkg_levers.get("workforce_multiplier", 1.0)
    soft_orig = soft_ceiling_model(r["gross_completions_uncapped"], wf_mult=wf)
    results.append({
        "id": f"RV04_ge_{pkg_name}",
        "desc": f"GE correction {pkg_name}: {soft_orig:.0f} -> {soft_ge:.0f} (price drop {price_drop*100:.1f}%)",
        "status": "RUN_RV",
        "cost_red": round(eff_cr * 100, 1),
        "viab": round((BASELINE["viability_margin"] + eff_cr) * 100, 1),
        "gross": round(35000 * (1 + 9.1 * eff_cr)),
        "hard": round(min(35000 * (1 + 9.1 * eff_cr), 35000 * wf)),
        "soft": round(soft_ge),
        "ceiling": round(35000 * wf),
        "notes": f"GE corrected: orig_soft={soft_orig:.0f}, price_drop={price_drop*100:.1f}%, eff_cr={eff_cr*100:.1f}%"
    })

# ============ RV05: Decompose modular × CPO interaction ============
print("\nRV05: Decompose modular × CPO interaction...")

modular_levers = {"modular_reduction": 0.30}
cpo_levers = {"land_cost_multiplier": 0.1}
both_levers = {**modular_levers, **cpo_levers}

r_base = run_feedback_loop({})
r_mod = run_feedback_loop(modular_levers)
r_cpo = run_feedback_loop(cpo_levers)
r_both = run_feedback_loop(both_levers)

# Gross (uncapped) interaction
gross_interaction = (r_both["gross_completions_uncapped"] -
                     r_mod["gross_completions_uncapped"] -
                     r_cpo["gross_completions_uncapped"] +
                     r_base["gross_completions_uncapped"])

# Soft-ceiling interaction
base_soft = soft_ceiling_model(r_base["gross_completions_uncapped"])
mod_soft = soft_ceiling_model(r_mod["gross_completions_uncapped"])
cpo_soft = soft_ceiling_model(r_cpo["gross_completions_uncapped"])
both_soft = soft_ceiling_model(r_both["gross_completions_uncapped"])
soft_interaction = both_soft - mod_soft - cpo_soft + base_soft

results.append({
    "id": "RV05_decompose",
    "desc": f"Mod×CPO interaction: gross={gross_interaction:.0f}, soft={soft_interaction:.0f}, ceiling_artifact={soft_interaction-gross_interaction:.0f}",
    "status": "RUN_RV",
    "cost_red": 0,
    "viab": 0,
    "gross": round(gross_interaction),
    "hard": 0,
    "soft": round(soft_interaction),
    "ceiling": 35000,
    "notes": f"Gross interaction={gross_interaction:.0f} (should be ~0 for linear model), soft interaction={soft_interaction:.0f}, difference={soft_interaction-gross_interaction:.0f} is ceiling artifact"
})

# ============ RV06: Monte Carlo CIs on interaction terms ============
print("\nRV06: Monte Carlo CIs on interaction terms...")

lever_pairs = [
    ("Land CPO × Workforce", {"land_cost_multiplier": 0.1}, {"workforce_multiplier": 1.5}),
    ("Modular × Workforce", {"modular_reduction": 0.30}, {"workforce_multiplier": 1.5}),
    ("VAT × Workforce", {"vat_rate": 0.0}, {"workforce_multiplier": 1.5}),
    ("Modular × Land CPO", {"modular_reduction": 0.30}, {"land_cost_multiplier": 0.1}),
    ("VAT × Land CPO", {"vat_rate": 0.0}, {"land_cost_multiplier": 0.1}),
]

rng = np.random.RandomState(42)
n_mc = 1000

for pair_name, la, lb in lever_pairs:
    interactions_mc = []
    for _ in range(n_mc):
        by = np.clip(rng.normal(0.596, 0.023), 0.40, 0.80)
        ar = np.clip(rng.normal(0.68, 0.03), 0.50, 0.90)
        ve = np.clip(rng.normal(0.91, 0.05), 0.50, 1.0)

        r_base_mc = run_feedback_loop({}, viability_elasticity=ve, build_yield=by, approval_rate=ar)
        r_a_mc = run_feedback_loop(la, viability_elasticity=ve, build_yield=by, approval_rate=ar)
        r_b_mc = run_feedback_loop(lb, viability_elasticity=ve, build_yield=by, approval_rate=ar)
        combined = {**la, **lb}
        r_ab_mc = run_feedback_loop(combined, viability_elasticity=ve, build_yield=by, approval_rate=ar)

        wf_base = 1.0
        wf_a = la.get("workforce_multiplier", 1.0)
        wf_b = lb.get("workforce_multiplier", 1.0)
        wf_ab = combined.get("workforce_multiplier", 1.0)

        s_base = soft_ceiling_model(r_base_mc["gross_completions_uncapped"], wf_mult=wf_base)
        s_a = soft_ceiling_model(r_a_mc["gross_completions_uncapped"], wf_mult=wf_a)
        s_b = soft_ceiling_model(r_b_mc["gross_completions_uncapped"], wf_mult=wf_b)
        s_ab = soft_ceiling_model(r_ab_mc["gross_completions_uncapped"], wf_mult=wf_ab)

        interaction = s_ab - (s_a + s_b - s_base)
        interactions_mc.append(interaction)

    ci_low = np.percentile(interactions_mc, 2.5)
    ci_high = np.percentile(interactions_mc, 97.5)
    mean_int = np.mean(interactions_mc)
    includes_zero = ci_low <= 0 <= ci_high

    results.append({
        "id": f"RV06_{pair_name.replace(' ', '_').replace('×', 'x')}",
        "desc": f"MC interaction {pair_name}: {mean_int:.0f} [{ci_low:.0f}, {ci_high:.0f}]",
        "status": "RUN_RV",
        "cost_red": 0,
        "viab": 0,
        "gross": round(mean_int),
        "hard": round(ci_low),
        "soft": round(ci_high),
        "ceiling": 0,
        "notes": f"95% CI: [{ci_low:.0f}, {ci_high:.0f}], includes_zero={includes_zero}"
    })

# ============ Write results to TSV ============
print("\nWriting results to results.tsv...")

tsv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.tsv")
with open(tsv_path, "a") as f:
    for r in results:
        row = [
            r["id"], r["desc"], r["status"],
            str(r["cost_red"]), str(r["viab"]),
            str(r["gross"]), str(r["hard"]), str(r["soft"]),
            str(r["ceiling"]), "", "", r["notes"]
        ]
        f.write("\t".join(row) + "\n")

print(f"\nAppended {len(results)} rows to results.tsv")

# ============ Print summary ============
print("\n" + "=" * 70)
print("REVIEWER EXPERIMENT SUMMARY")
print("=" * 70)

print("\nRV01 — Workforce ramp-rate:")
for r in results:
    if r["id"].startswith("RV01") and "yr5" in r["id"]:
        print(f"  {r['id']}: soft={r['soft']} at year 5")
    if r["id"].startswith("RV01") and "yr10" in r["id"]:
        print(f"  {r['id']}: soft={r['soft']} at year 10")

print("\nRV02 — Diminishing returns:")
for r in results:
    if r["id"].startswith("RV02"):
        print(f"  {r['desc']}")

print("\nRV03 — Tanh elasticity:")
for r in results:
    if r["id"].startswith("RV03"):
        print(f"  {r['desc']}")

print("\nRV04 — GE correction:")
for r in results:
    if r["id"].startswith("RV04"):
        print(f"  {r['desc']}")

print("\nRV05 — Interaction decomposition:")
for r in results:
    if r["id"].startswith("RV05"):
        print(f"  {r['desc']}")

print("\nRV06 — MC CIs on interactions:")
for r in results:
    if r["id"].startswith("RV06"):
        print(f"  {r['desc']}")
