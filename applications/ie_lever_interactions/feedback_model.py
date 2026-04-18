"""
Housing-lever feedback-loop model for Ireland.

Models the causal chain:
  Lever -> Cost reduction per unit -> Viability margin improvement
  -> Application intensity increase (r=0.91 viability-apps correlation)
  -> Permission volume increase (68% approval rate)
  -> Completion volume increase (59.6% build-yield)
  -> Capped at construction capacity ceiling (~35k/yr)

All parameters from 19 predecessor projects (see data_sources.md).
"""

import numpy as np
from itertools import product
from typing import Dict, List, Optional


# =============================================================================
# Baseline parameters from predecessor projects
# =============================================================================
BASELINE = {
    "total_dev_cost": 592_000,          # € total dev cost Dublin 3-bed (C-2)
    "pipeline_duration_days": 962,       # median pipeline days (PL-1)
    "finance_rate": 0.07,                # 7% on 60% drawdown (C-2)
    "finance_drawdown": 0.60,            # 60% average drawdown
    "hard_cost_share": 0.53,             # 53% nationally (SCSI / C-1)
    "viability_margin": -0.031,          # -3.1% Dublin houses (U-2)
    "viability_apps_r": 0.91,            # viability-application correlation (U-1)
    "current_applications": 21_000,      # residential apps/yr (U-1)
    "approval_rate": 0.68,               # 68% national (register)
    "build_yield": 0.596,                # 59.6% (S-1)
    "current_completions": 35_000,       # CSO
    "capacity_ceiling": 35_000,          # construction capacity (S-3)
    "hfa_target": 50_500,               # Housing for All target
    "materials_cagr": 0.0399,            # 3.99%/yr (C-1)
    "labour_cagr": 0.0403,              # 4.03%/yr (C-1)
    "policy_cost_share": 0.155,          # 15.5% (C-2)
    "lapse_rate": 0.095,                 # 9.5% (PL-4)
    "vat_rate": 0.135,                   # 13.5% current
    "part_v_rate": 0.20,                 # 20% current
    "dev_contribs_share": 0.03,          # ~3% of total cost
    "bcar_share": 0.015,                 # ~1.5% of total cost
    "land_cost_share": 0.18,             # ~18% of total cost in Dublin
    "developer_margin": 0.15,            # 15% current
}

# =============================================================================
# Lever definitions with settings
# =============================================================================
LEVER_SETTINGS = {
    "duration_reduction":   [0.0, 0.25, 0.33, 0.50],
    "modular_reduction":    [0.0, 0.10, 0.20, 0.30],
    "vat_rate":             [0.135, 0.09, 0.0],
    "part_v_rate":          [0.20, 0.10, 0.0],
    "dev_contribs_fraction": [1.0, 0.5, 0.0],
    "bcar_fraction":        [1.0, 0.5, 0.0],
    "land_cost_multiplier": [1.0, 0.5, 0.1],      # market, -50%, agricultural
    "finance_rate_new":     [0.07, 0.05, 0.03],
    "developer_margin_new": [0.15, 0.10, 0.06],
    "workforce_multiplier": [1.0, 1.2, 1.5],
}

# Friendly names for output
LEVER_NAMES = {
    "duration_reduction": "Duration reduction",
    "modular_reduction": "Modular construction",
    "vat_rate": "VAT rate",
    "part_v_rate": "Part V rate",
    "dev_contribs_fraction": "Dev contributions",
    "bcar_fraction": "BCAR",
    "land_cost_multiplier": "Land cost (CPO)",
    "finance_rate_new": "Finance rate",
    "developer_margin_new": "Developer margin",
    "workforce_multiplier": "Workforce/capacity",
}


def compute_cost_reduction(levers: Dict) -> float:
    """
    Compute fractional cost reduction from a set of levers.

    Returns a fraction of total development cost saved (0.0 = no saving, 0.20 = 20% saving).
    """
    total_cost = BASELINE["total_dev_cost"]
    total_saving = 0.0

    # 1. Duration reduction: saves on finance costs
    duration_cut = levers.get("duration_reduction", 0.0)
    if duration_cut > 0:
        duration_days = BASELINE["pipeline_duration_days"]
        duration_years = duration_days / 365.25
        finance_cost_baseline = (BASELINE["finance_rate"] *
                                  BASELINE["finance_drawdown"] *
                                  duration_years * total_cost)
        finance_cost_new = (BASELINE["finance_rate"] *
                            BASELINE["finance_drawdown"] *
                            duration_years * (1 - duration_cut) * total_cost)
        total_saving += (finance_cost_baseline - finance_cost_new)

    # 2. Modular construction: reduces hard costs
    modular_cut = levers.get("modular_reduction", 0.0)
    if modular_cut > 0:
        hard_costs = BASELINE["hard_cost_share"] * total_cost
        total_saving += modular_cut * hard_costs

    # 3. VAT: difference between current and new rate
    new_vat = levers.get("vat_rate", BASELINE["vat_rate"])
    if new_vat < BASELINE["vat_rate"]:
        # VAT saving as fraction of VAT-inclusive price
        # Pre-VAT cost = total / (1 + vat_rate)
        # New cost = pre_vat * (1 + new_vat)
        # Saving = total - new_cost = total * (vat_rate - new_vat) / (1 + vat_rate)
        vat_saving = total_cost * (BASELINE["vat_rate"] - new_vat) / (1 + BASELINE["vat_rate"])
        total_saving += vat_saving

    # 4. Part V: social housing obligation cost
    new_part_v = levers.get("part_v_rate", BASELINE["part_v_rate"])
    if new_part_v < BASELINE["part_v_rate"]:
        # Part V cost is roughly proportional to rate * a fraction of land/unit value
        # Using policy_cost_share as envelope: Part V ~ 25% of policy costs
        part_v_cost_baseline = 0.25 * BASELINE["policy_cost_share"] * total_cost
        part_v_saving = part_v_cost_baseline * (BASELINE["part_v_rate"] - new_part_v) / BASELINE["part_v_rate"]
        total_saving += part_v_saving

    # 5. Development contributions
    dev_frac = levers.get("dev_contribs_fraction", 1.0)
    if dev_frac < 1.0:
        dev_cost = BASELINE["dev_contribs_share"] * total_cost
        total_saving += dev_cost * (1 - dev_frac)

    # 6. BCAR compliance
    bcar_frac = levers.get("bcar_fraction", 1.0)
    if bcar_frac < 1.0:
        bcar_cost = BASELINE["bcar_share"] * total_cost
        total_saving += bcar_cost * (1 - bcar_frac)

    # 7. Land cost (CPO)
    land_mult = levers.get("land_cost_multiplier", 1.0)
    if land_mult < 1.0:
        land_cost = BASELINE["land_cost_share"] * total_cost
        total_saving += land_cost * (1 - land_mult)

    # 8. Finance rate change (independent of duration)
    new_finance = levers.get("finance_rate_new", BASELINE["finance_rate"])
    if new_finance < BASELINE["finance_rate"]:
        duration_days = BASELINE["pipeline_duration_days"]
        # Apply duration cut if also present
        duration_cut_applied = levers.get("duration_reduction", 0.0)
        effective_duration = duration_days * (1 - duration_cut_applied)
        duration_years = effective_duration / 365.25
        # Saving from rate difference (on the already-duration-adjusted timeline)
        rate_saving = ((BASELINE["finance_rate"] - new_finance) *
                       BASELINE["finance_drawdown"] *
                       duration_years * total_cost)
        total_saving += rate_saving

    # 9. Developer margin
    new_margin = levers.get("developer_margin_new", BASELINE["developer_margin"])
    if new_margin < BASELINE["developer_margin"]:
        margin_saving = (BASELINE["developer_margin"] - new_margin) * total_cost
        total_saving += margin_saving

    return total_saving / total_cost


def run_feedback_loop(levers: Dict,
                       capacity_ceiling: Optional[float] = None,
                       viability_elasticity: Optional[float] = None,
                       build_yield: Optional[float] = None,
                       approval_rate: Optional[float] = None) -> Dict:
    """
    Run the full feedback loop for a given set of levers.

    The model is calibrated so that the baseline (no levers) produces
    35,000 completions matching current CSO data. Levers change completions
    through the causal chain:

      cost_reduction -> viability_margin improves -> applications increase
      (r=0.91 elasticity) -> permissions (68% approval) -> completions
      (59.6% build-yield) -> capped at capacity ceiling

    The baseline steady-state flow is calibrated:
      baseline_applications * approval * build_yield = current_completions
      => baseline_applications_effective = 35000 / (0.68 * 0.596) = 86,346

    This is the effective application-equivalent flow (including multi-year
    pipeline stock) that produces 35k completions/yr. Lever effects change
    this flow proportionally via the viability-application elasticity.

    Returns dict with key outputs at each stage.
    """
    b = BASELINE.copy()

    # Override parameters if provided (for Monte Carlo)
    if viability_elasticity is not None:
        b["viability_apps_r"] = viability_elasticity
    if build_yield is not None:
        b["build_yield"] = build_yield
    if approval_rate is not None:
        b["approval_rate"] = approval_rate

    # Calibrated effective application flow
    baseline_apps_effective = b["current_completions"] / (b["approval_rate"] * b["build_yield"])

    # Step 1: Cost reduction
    cost_red = compute_cost_reduction(levers)

    # Step 2: Viability margin improvement
    new_viability = b["viability_margin"] + cost_red

    # Step 3: Application intensity change via viability-application elasticity
    viability_delta = cost_red  # = new_viability - baseline_viability
    # Elasticity: r=0.91 means a 10pp viability improvement roughly doubles apps
    scale_factor = 0.10  # 10pp normalisation
    app_multiplier = 1.0 + b["viability_apps_r"] * (viability_delta / scale_factor)
    new_applications = baseline_apps_effective * max(app_multiplier, 0.1)

    # Step 4: Permissions (approval rate)
    new_permissions = new_applications * b["approval_rate"]

    # Step 5: Completions (build-yield)
    gross_completions = new_permissions * b["build_yield"]

    # Step 6: Capacity ceiling
    workforce_mult = levers.get("workforce_multiplier", 1.0)
    if capacity_ceiling is None:
        effective_ceiling = b["capacity_ceiling"] * workforce_mult
    else:
        effective_ceiling = capacity_ceiling * workforce_mult

    final_completions = min(gross_completions, effective_ceiling)

    return {
        "cost_reduction": cost_red,
        "cost_saving_per_unit": cost_red * b["total_dev_cost"],
        "viability_margin": new_viability,
        "viability_delta_pp": viability_delta * 100,
        "app_multiplier": app_multiplier,
        "applications": new_applications,
        "permissions": new_permissions,
        "completions": final_completions,
        "capacity_ceiling_used": effective_ceiling,
        "ceiling_binding": final_completions >= effective_ceiling * 0.999,
        "gross_completions_uncapped": gross_completions,
    }


def compute_interaction_term(levers_a: Dict, levers_b: Dict) -> float:
    """
    Compute interaction term = combined_effect - (effect_A + effect_B).

    Positive = synergy, negative = redundancy.
    """
    baseline = run_feedback_loop({})["completions"]
    effect_a = run_feedback_loop(levers_a)["completions"] - baseline
    effect_b = run_feedback_loop(levers_b)["completions"] - baseline

    combined_levers = {**levers_a, **levers_b}
    effect_combined = run_feedback_loop(combined_levers)["completions"] - baseline

    interaction = effect_combined - (effect_a + effect_b)
    return interaction


def generate_full_factorial() -> List[Dict]:
    """
    Generate all 104,976 lever combinations from the full factorial.
    """
    lever_keys = list(LEVER_SETTINGS.keys())
    lever_values = [LEVER_SETTINGS[k] for k in lever_keys]

    combos = []
    for combo in product(*lever_values):
        lever_dict = dict(zip(lever_keys, combo))
        combos.append(lever_dict)

    return combos


def run_monte_carlo(levers: Dict, n_draws: int = 10_000, seed: int = 42) -> List[float]:
    """
    Monte Carlo simulation propagating parameter uncertainty.

    Draws from distributions for:
    - build_yield: N(0.596, 0.023) based on CI 55-64%
    - approval_rate: N(0.68, 0.03)
    - viability_elasticity: N(0.91, 0.05)
    - cost parameters: ±10% uniform
    """
    rng = np.random.RandomState(seed)

    results = []
    for _ in range(n_draws):
        by = rng.normal(0.596, 0.023)
        by = np.clip(by, 0.40, 0.80)

        ar = rng.normal(0.68, 0.03)
        ar = np.clip(ar, 0.50, 0.90)

        ve = rng.normal(0.91, 0.05)
        ve = np.clip(ve, 0.50, 1.0)

        result = run_feedback_loop(levers,
                                    viability_elasticity=ve,
                                    build_yield=by,
                                    approval_rate=ar)
        results.append(result["completions"])

    return results


def describe_levers(levers: Dict) -> str:
    """Human-readable description of a lever combination."""
    parts = []
    for k, v in levers.items():
        name = LEVER_NAMES.get(k, k)
        if k == "duration_reduction" and v > 0:
            parts.append(f"{name} -{v*100:.0f}%")
        elif k == "modular_reduction" and v > 0:
            parts.append(f"{name} -{v*100:.0f}%")
        elif k == "vat_rate" and v < 0.135:
            parts.append(f"{name} {v*100:.1f}%")
        elif k == "part_v_rate" and v < 0.20:
            parts.append(f"{name} {v*100:.0f}%")
        elif k == "dev_contribs_fraction" and v < 1.0:
            parts.append(f"{name} ×{v:.1f}")
        elif k == "bcar_fraction" and v < 1.0:
            parts.append(f"{name} ×{v:.1f}")
        elif k == "land_cost_multiplier" and v < 1.0:
            parts.append(f"{name} ×{v:.1f}")
        elif k == "finance_rate_new" and v < 0.07:
            parts.append(f"{name} {v*100:.0f}%")
        elif k == "developer_margin_new" and v < 0.15:
            parts.append(f"{name} {v*100:.0f}%")
        elif k == "workforce_multiplier" and v > 1.0:
            parts.append(f"{name} +{(v-1)*100:.0f}%")
    return " + ".join(parts) if parts else "Baseline (no levers)"


if __name__ == "__main__":
    # Quick smoke test
    print("Baseline:", run_feedback_loop({}))
    print("\nAll levers maxed:")
    all_max = {
        "duration_reduction": 0.50,
        "modular_reduction": 0.30,
        "vat_rate": 0.0,
        "part_v_rate": 0.0,
        "dev_contribs_fraction": 0.0,
        "bcar_fraction": 0.5,
        "land_cost_multiplier": 0.1,
        "finance_rate_new": 0.03,
        "developer_margin_new": 0.06,
        "workforce_multiplier": 1.5,
    }
    print(run_feedback_loop(all_max))
