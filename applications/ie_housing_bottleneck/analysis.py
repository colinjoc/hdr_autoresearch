"""
Irish Housing Bottleneck Synthesis — Meta-analysis pipeline model.

This module implements a waterfall pipeline model for Irish housing delivery,
synthesising parameters from 13 predecessor studies to rank bottlenecks
by their marginal impact on completions per year.

Option C: Decomposition-based analysis (no GPU required).
"""
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional
import csv
import os

PROJECT_DIR = Path(__file__).parent

# =============================================================================
# PARAMETERS — all from predecessor study results
# =============================================================================
PARAMS = {
    # Pipeline flow
    "permission_volume": 38000,           # BHQ15 median 2019-2025
    "lapse_rate": 0.095,                  # PL-4 NRU>0 2017-2019
    "lapse_rate_ci_lo": 0.044,            # PL-4 cluster-bootstrap
    "lapse_rate_ci_hi": 0.156,            # PL-4 cluster-bootstrap
    "ccc_filing_rate": 0.409,             # S-1 all commenced
    "ccc_filing_rate_nonoptout": 0.598,   # S-1 non-opt-out
    "opt_out_share": 0.316,              # S-1 fraction of commenced
    "opt_out_build_rate": 0.0,           # Baseline: no credit for opt-out
    "ccc_to_occupied": 0.95,             # S-1 estimated
    "capacity_ceiling": None,             # None = uncapped

    # Duration (days)
    "perm_to_comm_days": 232,             # PL-1 median
    "comm_to_ccc_days": 498,              # PL-1 median
    "total_pipeline_days": 962,           # PL-1 complete timeline

    # ABP
    "abp_weeks_baseline": 18,            # PL-3 2017
    "abp_weeks_current": 42,             # PL-3 2023-2024
    "abp_housing_share": 0.40,           # ~40% of ABP cases are housing
    "abp_annual_disposals": 2800,        # Approximate

    # JR
    "jr_direct_unit_months": 105504,     # S-2 central
    "jr_direct_range_lo": 85404,         # S-2 floor
    "jr_direct_range_hi": 150204,        # S-2 high
    "jr_counterfactual_uncapped": 16638, # S-2 units over 2018-2024
    "jr_counterfactual_35k": 7421,       # S-2 with capacity ceiling
    "jr_years": 7,                       # 2018-2024

    # LDA
    "lda_delivery_2023": 850,            # PL-3 LDA
    "lda_additionality": 0.0,            # 100% Tosaigh acquisition

    # Target
    "hfa_target": 50500,                 # Housing for All
    "completions_2024": 34177,           # NDA12

    # Construction sector
    "construction_workforce": 160000,    # CSO 2024
    "construction_workforce_needed": 200000,  # CIF estimate for HFA

    # International comparators
    "yield_nz": 0.80,
    "yield_nl": 0.90,
    "yield_uk": 0.60,  # midpoint of 50-70%
}


# =============================================================================
# WATERFALL MODEL (T01 / E00)
# =============================================================================
def waterfall_model(params: Dict) -> Dict[str, float]:
    """
    Compute the waterfall pipeline from permissions to completions.

    Returns a dict with units at each stage and losses.
    """
    pv = params["permission_volume"]
    lr = params["lapse_rate"]
    ccc_rate = params["ccc_filing_rate"]
    opt_share = params["opt_out_share"]
    opt_build = params.get("opt_out_build_rate", 0.0)
    ccc_occ = params["ccc_to_occupied"]
    cap = params.get("capacity_ceiling", None)

    # Stage 1: Permissions -> Commenced
    lapsed = pv * lr
    commenced = pv - lapsed

    # Stage 2: Commenced -> CCC filed
    # CCC non-filing: some is opt-out (homes built but not filed), rest is genuine
    ccc_filed = commenced * ccc_rate
    ccc_non_filed = commenced - ccc_filed

    # Stage 3: CCC filed -> Occupied
    ccc_to_occ_loss = ccc_filed * (1 - ccc_occ)
    completions = ccc_filed * ccc_occ

    # Apply capacity ceiling
    if cap is not None and completions > cap:
        completions = cap

    # Opt-out adjustment: count opt-out homes that ARE built
    opt_out_units = commenced * opt_share
    opt_out_built = opt_out_units * opt_build
    effective_completions = completions + opt_out_built

    if cap is not None and effective_completions > cap:
        effective_completions = cap

    return {
        "permissions": pv,
        "lapsed": lapsed,
        "commenced": commenced,
        "ccc_filed": ccc_filed,
        "ccc_non_filed": ccc_non_filed,
        "ccc_to_occupied_loss": ccc_to_occ_loss,
        "completions": completions,
        "effective_completions": effective_completions,
        "yield": completions / pv if pv > 0 else 0,
        "effective_yield": effective_completions / pv if pv > 0 else 0,
    }


# =============================================================================
# SENSITIVITY RANKING (T02)
# =============================================================================
def sensitivity_ranking(params: Dict) -> List[Dict]:
    """
    Compute partial derivative of completions w.r.t. each bottleneck parameter.
    Returns ranked list of bottlenecks by marginal completions/yr.
    """
    base = waterfall_model(params)
    base_comp = base["completions"]

    perturbations = [
        ("permission_volume", +10000, "Add 10k permissions/yr"),
        ("lapse_rate", -0.05, "Reduce lapse by 5pp"),
        ("ccc_filing_rate", +0.10, "Improve CCC rate by 10pp"),
        ("ccc_to_occupied", +0.05, "Improve CCC-to-occupied by 5pp"),
        ("opt_out_build_rate", +0.90, "Credit 90% opt-out as built"),
    ]

    results = []
    for param_name, delta, description in perturbations:
        p = params.copy()
        p[param_name] = params[param_name] + delta
        r = waterfall_model(p)
        marginal = r["effective_completions"] - base["effective_completions"]
        results.append({
            "name": param_name,
            "description": description,
            "delta": delta,
            "marginal_units_per_year": marginal,
            "base_completions": base_comp,
            "new_completions": r["completions"],
        })

    # Add capacity ceiling scenario
    p = params.copy()
    p["capacity_ceiling"] = 35000
    r_cap = waterfall_model(p)
    results.append({
        "name": "capacity_ceiling_35k",
        "description": "Apply 35k capacity ceiling",
        "delta": 35000,
        "marginal_units_per_year": r_cap["completions"] - base_comp,
        "base_completions": base_comp,
        "new_completions": r_cap["completions"],
    })

    # Add ABP speed scenario (indirect via JR counterfactual)
    jr_annual = params["jr_counterfactual_uncapped"] / params["jr_years"]
    results.append({
        "name": "abp_speed_18wk",
        "description": "ABP at 18-week SOP (counterfactual from S-2)",
        "delta": -24,  # weeks reduction
        "marginal_units_per_year": jr_annual,
        "base_completions": base_comp,
        "new_completions": base_comp + jr_annual,
    })

    # Add JR-removed scenario
    jr_annual_35k = params["jr_counterfactual_35k"] / params["jr_years"]
    results.append({
        "name": "jr_removed",
        "description": "Remove JR entirely (S-2 35k-ceiling counterfactual)",
        "delta": 0,
        "marginal_units_per_year": jr_annual_35k,
        "base_completions": base_comp,
        "new_completions": base_comp + jr_annual_35k,
    })

    # Construction duration (affects timing not throughput)
    results.append({
        "name": "construction_duration_halved",
        "description": "Halve construction duration (498d -> 249d)",
        "delta": -249,
        "marginal_units_per_year": 0,  # Duration shifts timing, not annual throughput
        "base_completions": base_comp,
        "new_completions": base_comp,
    })

    # LDA scaled
    lda_add = params["lda_delivery_2023"] * 2 * params["lda_additionality"]
    results.append({
        "name": "lda_3x",
        "description": "LDA scaled to 3x current (additionality = 0)",
        "delta": 2,
        "marginal_units_per_year": lda_add,
        "base_completions": base_comp,
        "new_completions": base_comp + lda_add,
    })

    # Sort by absolute marginal impact
    results.sort(key=lambda x: abs(x["marginal_units_per_year"]), reverse=True)
    return results


# =============================================================================
# MONTE CARLO (T05)
# =============================================================================
def monte_carlo_pipeline(params: Dict, n_draws: int = 5000, seed: int = 42) -> List[float]:
    """
    Monte Carlo propagation of uncertainty through the pipeline.
    """
    rng = np.random.default_rng(seed)

    completions_list = []
    for _ in range(n_draws):
        p = params.copy()

        # Sample lapse rate from approximate beta distribution
        lr_mean = params["lapse_rate"]
        lr_lo = params["lapse_rate_ci_lo"]
        lr_hi = params["lapse_rate_ci_hi"]
        # Use triangular as simple approximation
        p["lapse_rate"] = rng.triangular(lr_lo, lr_mean, lr_hi)

        # Sample CCC filing rate (narrow CI, use normal)
        p["ccc_filing_rate"] = rng.normal(params["ccc_filing_rate"], 0.01)
        p["ccc_filing_rate"] = max(0.01, min(0.99, p["ccc_filing_rate"]))

        # Sample permission volume (normal around current)
        p["permission_volume"] = rng.normal(params["permission_volume"], 3000)
        p["permission_volume"] = max(10000, p["permission_volume"])

        # Sample CCC-to-occupied
        p["ccc_to_occupied"] = rng.triangular(0.90, 0.95, 0.99)

        result = waterfall_model(p)
        completions_list.append(result["completions"])

    return completions_list


# =============================================================================
# TOURNAMENT (Phase 1)
# =============================================================================
def run_tournament(params: Dict) -> List[Dict]:
    """
    Run 5 model families on the same data.
    """
    families = []

    # T01: Simple waterfall accounting
    r01 = waterfall_model(params)
    families.append({
        "family": "T01_waterfall",
        "description": "Simple stage-by-stage product",
        "metric": "yield",
        "value": r01["yield"],
    })

    # T02: Sensitivity-based ranking
    ranking = sensitivity_ranking(params)
    families.append({
        "family": "T02_sensitivity",
        "description": "Partial derivative ranking",
        "metric": "top_bottleneck_marginal",
        "value": ranking[0]["marginal_units_per_year"] if ranking else 0,
    })

    # T03: Throughput accounting / TOC
    # Identify the stage with tightest capacity
    stages = {
        "permissions": params["permission_volume"],
        "commencement": params["permission_volume"] * (1 - params["lapse_rate"]),
        "ccc_filing": params["permission_volume"] * (1 - params["lapse_rate"]) * params["ccc_filing_rate"],
        "completion": r01["completions"],
    }
    if params.get("capacity_ceiling"):
        stages["construction_capacity"] = params["capacity_ceiling"]

    # The binding constraint is the stage with the lowest throughput
    # that is less than or equal to the HFA target
    binding = min(stages, key=stages.get)
    families.append({
        "family": "T03_toc",
        "description": "Theory of Constraints: identify binding stage",
        "metric": "binding_constraint",
        "value": binding,
    })

    # T04: Structural equation model (simplified path model)
    # Path coefficients: permissions -> commencements -> CCC -> completions
    path_perm_comm = 1 - params["lapse_rate"]  # 0.905
    path_comm_ccc = params["ccc_filing_rate"]    # 0.409
    path_ccc_comp = params["ccc_to_occupied"]    # 0.95
    total_yield = path_perm_comm * path_comm_ccc * path_ccc_comp

    # The weakest path coefficient is the bottleneck
    paths = {
        "perm_to_comm": path_perm_comm,
        "comm_to_ccc": path_comm_ccc,
        "ccc_to_comp": path_ccc_comp,
    }
    weakest = min(paths, key=paths.get)
    families.append({
        "family": "T04_sem",
        "description": "Path model with stage coefficients",
        "metric": "weakest_path",
        "value": weakest,
    })

    # T05: Monte Carlo
    mc = monte_carlo_pipeline(params, n_draws=1000, seed=42)
    families.append({
        "family": "T05_montecarlo",
        "description": "Monte Carlo uncertainty propagation",
        "metric": "completions_p50",
        "value": np.median(mc),
    })

    # T06: Linear sanity check (OLS: completions = a * permissions + b)
    # With a single point this is just the yield
    families.append({
        "family": "T06_linear",
        "description": "Linear sanity check: completions = yield * permissions",
        "metric": "yield_coefficient",
        "value": total_yield,
    })

    return families


# =============================================================================
# EXPERIMENTS (Phase 2)
# =============================================================================
def run_all_experiments(params: Dict) -> List[Dict]:
    """Run all 20+ experiments and return results."""
    experiments = []
    base = waterfall_model(params)
    base_comp = base["completions"]
    base_eff = base["effective_completions"]

    def exp(eid, desc, delta_comp, delta_eff=None, status="KEEP", **extra):
        if delta_eff is None:
            delta_eff = delta_comp
        experiments.append({
            "id": eid,
            "description": desc,
            "delta_completions": delta_comp,
            "delta_effective": delta_eff,
            "status": status,
            **extra,
        })

    # E00: Baseline
    exp("E00", "Baseline waterfall: 38k permissions, 35.1% yield", base_comp,
        base_eff, metric="completions", value=base_comp)

    # E01: Opt-out adjusted (90% built)
    p = params.copy(); p["opt_out_build_rate"] = 0.90
    r = waterfall_model(p)
    exp("E01", "Opt-out 90% built", r["completions"] - base_comp,
        r["effective_completions"] - base_eff,
        metric="effective_yield", value=r["effective_yield"])

    # E02a-c: Permission volume sensitivity
    for i, vol in enumerate([48000, 58000, 68000]):
        p = params.copy(); p["permission_volume"] = vol
        r = waterfall_model(p)
        exp(f"E02{'abc'[i]}", f"Permissions = {vol//1000}k",
            r["completions"] - base_comp, metric="completions", value=r["completions"])

    # E03a-b: ABP decision time sensitivity (using JR counterfactual as proxy)
    jr_annual_uncapped = params["jr_counterfactual_uncapped"] / params["jr_years"]
    jr_annual_35k = params["jr_counterfactual_35k"] / params["jr_years"]
    exp("E03a", "ABP at 18wk (full counterfactual, uncapped)",
        jr_annual_uncapped, metric="delta_completions", value=jr_annual_uncapped)
    exp("E03b", "ABP at 30wk (half excess, approx)",
        jr_annual_uncapped * 0.5, metric="delta_completions", value=jr_annual_uncapped * 0.5)

    # E04: JR removed
    exp("E04", "JR removed (35k-ceiling counterfactual)",
        jr_annual_35k, metric="delta_completions", value=jr_annual_35k)

    # E05: Lapse halved
    p = params.copy(); p["lapse_rate"] = params["lapse_rate"] / 2
    r = waterfall_model(p)
    exp("E05", "Lapse halved (9.5% -> 4.75%)",
        r["completions"] - base_comp, metric="delta_completions",
        value=r["completions"] - base_comp)

    # E06: Construction duration halved
    exp("E06", "Construction duration halved (498d -> 249d)",
        0, status="KEEP",  # KEEP because the finding (zero impact) is informative
        metric="delta_annual_completions", value=0,
        note="Duration shifts timing, not annual throughput in steady state")

    # E07a-c: Capacity ceiling scenarios
    for label, cap in [("35k", 35000), ("40k", 40000), ("50k", 50000)]:
        p = params.copy(); p["capacity_ceiling"] = cap
        r = waterfall_model(p)
        delta = r["completions"] - base_comp
        # If ceiling is above baseline completions, no binding
        binds = "binds" if r["completions"] < base_comp else "not_binding"
        exp(f"E07_{label}", f"Capacity ceiling = {label}",
            delta, metric="ceiling_status", value=binds)

    # E08: LDA 3x
    lda_add = params["lda_delivery_2023"] * 2 * params["lda_additionality"]
    exp("E08", "LDA scaled 3x (additionality = 0)", lda_add,
        metric="lda_additional", value=lda_add,
        note="LDA additionality is approximately zero; Tosaigh is attribution only")

    # E09: Combined: permission + capacity + ABP
    p = params.copy()
    p["permission_volume"] = 58000
    p["capacity_ceiling"] = 40000
    r = waterfall_model(p)
    combined_delta = (r["completions"] - base_comp) + jr_annual_35k
    combined_delta = min(combined_delta, 40000 - base_comp)
    exp("E09", "Combined: 58k perms + 40k cap + ABP speed",
        combined_delta, metric="delta_completions", value=combined_delta)

    # E10: Dublin-only pipeline
    dublin_share = 0.42  # PL-1 Dublin share
    dublin_comp = base_comp * dublin_share
    exp("E10", "Dublin-only pipeline (42% share)",
        0, metric="dublin_completions", value=dublin_comp,
        note="Dublin accounts for ~42% of pipeline throughput")

    # E11: Apartment-only pipeline (higher yield)
    apt_ccc_rate = 0.889  # S-1: 200+ unit schemes
    p = params.copy(); p["ccc_filing_rate"] = apt_ccc_rate
    r = waterfall_model(p)
    exp("E11", "Apartment-only pipeline (large schemes, CCC 88.9%)",
        r["completions"] - base_comp, metric="yield", value=r["yield"])

    # E12: Labour supply constraint proxy
    workforce_gap = (params["construction_workforce_needed"] - params["construction_workforce"])
    workforce_gap_frac = workforce_gap / params["construction_workforce_needed"]
    implied_capacity = params["completions_2024"] / (1 - workforce_gap_frac) if workforce_gap_frac < 1 else params["completions_2024"]
    exp("E12", "Labour supply constraint (160k vs 200k needed)",
        0, metric="workforce_gap_pct", value=workforce_gap_frac,
        note=f"20% workforce gap implies capacity limited to ~{implied_capacity:.0f} at full staffing")

    # E13: International comparison
    for country, yld in [("UK", 0.60), ("NZ", 0.80), ("NL", 0.90)]:
        perms_needed = params["hfa_target"] / yld
        exp(f"E13_{country}", f"If Ireland had {country} yield ({yld:.0%})",
            0, metric="permissions_needed_at_yield", value=perms_needed)

    # E14: Permission volume vs capacity nonlinearity
    volumes = list(range(30000, 100001, 10000))
    for vol in volumes:
        p = params.copy()
        p["permission_volume"] = vol
        p["capacity_ceiling"] = 35000
        r = waterfall_model(p)
        if vol == 70000:  # Pick one representative
            exp("E14", f"Volume-capacity kink at 70k perms / 35k cap",
                r["completions"] - base_comp, metric="completions_at_70k_35kcap",
                value=r["completions"])

    # E15: Commencement delay economic cost
    holding_cost_per_unit_month = 500  # EUR, from S-2
    annual_starts = params["permission_volume"] * (1 - params["lapse_rate"])
    delay_months = params["perm_to_comm_days"] / 30.44
    total_cost = annual_starts * delay_months * holding_cost_per_unit_month
    exp("E15", "Commencement delay holding cost",
        0, metric="eur_annual_holding_cost", value=total_cost)

    # E16: CCC non-filing decomposition
    non_filed = base["ccc_non_filed"]
    opt_out_in_nonfiled = base["commenced"] * params["opt_out_share"]
    genuine_nonfiled = non_filed - opt_out_in_nonfiled
    artefact_share = opt_out_in_nonfiled / non_filed if non_filed > 0 else 0
    exp("E16", "CCC non-filing decomposition",
        0, metric="opt_out_artefact_share", value=artefact_share,
        note=f"Opt-out accounts for {artefact_share:.0%} of CCC non-filing")

    # E17: Construction duration international comparison
    # UK 12-18 months, NZ 12 months, Ireland 16.6 months (498 days)
    exp("E17", "Construction duration: IE 498d vs UK 365-540d vs NZ 360d",
        0, metric="ie_duration_days", value=498,
        note="Ireland is slightly above average but not an outlier")

    # E18: ABP share of permissions
    abp_share = 0.15  # Approximately 15% of permissions go through ABP
    exp("E18", "ABP handles ~15% of all permissions",
        0, metric="abp_share", value=abp_share)

    # E19: Full constraint removal
    p = params.copy()
    p["permission_volume"] = 68000
    p["lapse_rate"] = 0.02
    p["ccc_filing_rate"] = 0.80
    p["capacity_ceiling"] = 50000
    r = waterfall_model(p)
    exp("E19", "Full constraint removal (68k perms, 2% lapse, 80% CCC, 50k cap)",
        r["completions"] - base_comp, metric="completions", value=r["completions"])

    # E20: Permission gap to HFA
    gap = params["hfa_target"] - params["completions_2024"]
    exp("E20", f"Permission gap to HFA target",
        gap, metric="completions_gap", value=gap)

    return experiments


# =============================================================================
# PAIRWISE INTERACTIONS (Phase 2.5)
# =============================================================================
def run_pairwise_interactions(params: Dict) -> List[Dict]:
    """Run pairwise interaction tests between top bottlenecks."""
    base = waterfall_model(params)
    base_comp = base["completions"]

    results = []

    # Interaction 1: Permission volume + capacity ceiling
    p1 = params.copy(); p1["permission_volume"] = 58000
    r1 = waterfall_model(p1)
    p2 = params.copy(); p2["capacity_ceiling"] = 40000
    r2 = waterfall_model(p2)
    p12 = params.copy(); p12["permission_volume"] = 58000; p12["capacity_ceiling"] = 40000
    r12 = waterfall_model(p12)
    additive = (r1["completions"] - base_comp) + (r2["completions"] - base_comp)
    actual = r12["completions"] - base_comp
    results.append({
        "id": "P01",
        "pair": "permission_volume + capacity_ceiling",
        "individual_sum": additive,
        "combined": actual,
        "interaction_effect": actual - additive,
        "interaction": True,
        "status": "KEEP",
        "note": "Capacity ceiling caps the permission-volume gain" if actual < additive else "Additive",
    })

    # Interaction 2: Lapse reduction + CCC improvement
    p1 = params.copy(); p1["lapse_rate"] = 0.0475
    r1 = waterfall_model(p1)
    p2 = params.copy(); p2["ccc_filing_rate"] = 0.509
    r2 = waterfall_model(p2)
    p12 = params.copy(); p12["lapse_rate"] = 0.0475; p12["ccc_filing_rate"] = 0.509
    r12 = waterfall_model(p12)
    additive = (r1["completions"] - base_comp) + (r2["completions"] - base_comp)
    actual = r12["completions"] - base_comp
    results.append({
        "id": "P02",
        "pair": "lapse_reduction + ccc_improvement",
        "individual_sum": additive,
        "combined": actual,
        "interaction_effect": actual - additive,
        "interaction": True,
        "status": "KEEP",
        "note": "Slightly super-additive: fewer lapsed means more to benefit from CCC improvement",
    })

    # Interaction 3: Permission volume + lapse reduction
    p1 = params.copy(); p1["permission_volume"] = 48000
    r1 = waterfall_model(p1)
    p2 = params.copy(); p2["lapse_rate"] = 0.0475
    r2 = waterfall_model(p2)
    p12 = params.copy(); p12["permission_volume"] = 48000; p12["lapse_rate"] = 0.0475
    r12 = waterfall_model(p12)
    additive = (r1["completions"] - base_comp) + (r2["completions"] - base_comp)
    actual = r12["completions"] - base_comp
    results.append({
        "id": "P03",
        "pair": "permission_volume + lapse_reduction",
        "individual_sum": additive,
        "combined": actual,
        "interaction_effect": actual - additive,
        "interaction": True,
        "status": "KEEP",
        "note": "Mildly super-additive: more permissions + fewer lapsed compounds",
    })

    # Interaction 4: Permission volume + opt-out credit
    p1 = params.copy(); p1["permission_volume"] = 48000
    r1 = waterfall_model(p1)
    p2 = params.copy(); p2["opt_out_build_rate"] = 0.90
    r2 = waterfall_model(p2)
    p12 = params.copy(); p12["permission_volume"] = 48000; p12["opt_out_build_rate"] = 0.90
    r12 = waterfall_model(p12)
    additive = (r1["effective_completions"] - base["effective_completions"]) + (r2["effective_completions"] - base["effective_completions"])
    actual = r12["effective_completions"] - base["effective_completions"]
    results.append({
        "id": "P04",
        "pair": "permission_volume + opt_out_credit",
        "individual_sum": additive,
        "combined": actual,
        "interaction_effect": actual - additive,
        "interaction": True,
        "status": "KEEP",
        "note": "Super-additive: more permissions means more opt-out homes to credit",
    })

    return results


# =============================================================================
# PHASE B: DISCOVERY OUTPUTS
# =============================================================================
def generate_bottleneck_ranking(params: Dict) -> pd.DataFrame:
    """Generate bottleneck_ranking.csv for Phase B."""
    ranking = sensitivity_ranking(params)

    # Also add specific computed bottlenecks
    base = waterfall_model(params)

    all_bottlenecks = []

    # Permission volume (main scenario: +10k)
    p = params.copy(); p["permission_volume"] = 48000
    r = waterfall_model(p)
    all_bottlenecks.append({
        "bottleneck": "permission_volume",
        "description": "Annual planning permissions granted",
        "current_value": f"{params['permission_volume']:,}",
        "scenario": "+10,000/yr",
        "marginal_units_per_year": round(r["completions"] - base["completions"]),
        "marginal_pct": f"{(r['completions'] - base['completions'])/base['completions']:.1%}",
    })

    # CCC non-filing (genuine, not opt-out)
    p = params.copy(); p["ccc_filing_rate"] = 0.509
    r = waterfall_model(p)
    all_bottlenecks.append({
        "bottleneck": "ccc_filing_rate",
        "description": "CCC filing rate among commenced projects",
        "current_value": f"{params['ccc_filing_rate']:.1%}",
        "scenario": "+10pp",
        "marginal_units_per_year": round(r["completions"] - base["completions"]),
        "marginal_pct": f"{(r['completions'] - base['completions'])/base['completions']:.1%}",
    })

    # Construction capacity ceiling
    current_cap = params.get("capacity_ceiling", "uncapped")
    all_bottlenecks.append({
        "bottleneck": "construction_capacity",
        "description": "Construction sector annual output ceiling",
        "current_value": f"~35,000 (observed peak)",
        "scenario": "Raise to 50,000",
        "marginal_units_per_year": max(0, base["completions"] - 35000) if base["completions"] > 35000 else 0,
        "marginal_pct": "Conditional on permissions",
    })

    # Permission lapse
    p = params.copy(); p["lapse_rate"] = 0.0475
    r = waterfall_model(p)
    all_bottlenecks.append({
        "bottleneck": "permission_lapse",
        "description": "Non-commencement rate",
        "current_value": f"{params['lapse_rate']:.1%}",
        "scenario": "Halved to 4.75%",
        "marginal_units_per_year": round(r["completions"] - base["completions"]),
        "marginal_pct": f"{(r['completions'] - base['completions'])/base['completions']:.1%}",
    })

    # ABP decision time
    jr_annual = params["jr_counterfactual_35k"] / params["jr_years"]
    all_bottlenecks.append({
        "bottleneck": "abp_decision_time",
        "description": "ABP mean weeks to dispose",
        "current_value": f"{params['abp_weeks_current']} weeks",
        "scenario": "Return to 18 weeks (35k-cap counterfactual)",
        "marginal_units_per_year": round(jr_annual),
        "marginal_pct": f"{jr_annual/base['completions']:.1%}",
    })

    # Judicial review
    all_bottlenecks.append({
        "bottleneck": "judicial_review",
        "description": "JR direct delay on housing schemes",
        "current_value": f"{params['jr_direct_unit_months']:,} unit-months (2018-2024)",
        "scenario": "Remove JR entirely",
        "marginal_units_per_year": round(jr_annual),
        "marginal_pct": f"{jr_annual/base['completions']:.1%}",
    })

    # Commencement delay
    all_bottlenecks.append({
        "bottleneck": "commencement_delay",
        "description": "Permission-to-commencement duration",
        "current_value": f"{params['perm_to_comm_days']} days median",
        "scenario": "Halved to 116 days",
        "marginal_units_per_year": 0,
        "marginal_pct": "0% (timing shift, not throughput)",
    })

    # Construction duration
    all_bottlenecks.append({
        "bottleneck": "construction_duration",
        "description": "Commencement-to-CCC duration",
        "current_value": f"{params['comm_to_ccc_days']} days median",
        "scenario": "Halved to 249 days",
        "marginal_units_per_year": 0,
        "marginal_pct": "0% (timing shift, not throughput)",
    })

    # LDA structural share
    all_bottlenecks.append({
        "bottleneck": "lda_structural_share",
        "description": "LDA delivery (attribution, not additionality)",
        "current_value": f"~{params['lda_delivery_2023']}/yr",
        "scenario": "Scaled 3x",
        "marginal_units_per_year": 0,
        "marginal_pct": "0% (attribution only, zero additionality)",
    })

    # Labour supply
    all_bottlenecks.append({
        "bottleneck": "labour_supply",
        "description": "Construction workforce gap",
        "current_value": f"{params['construction_workforce']:,} vs {params['construction_workforce_needed']:,} needed",
        "scenario": "Close workforce gap",
        "marginal_units_per_year": round(params["completions_2024"] * 0.20),
        "marginal_pct": "~20% (workforce gap fraction)",
    })

    df = pd.DataFrame(all_bottlenecks)
    df["rank"] = range(1, len(df) + 1)
    # Re-rank by marginal units
    df = df.sort_values("marginal_units_per_year", ascending=False).reset_index(drop=True)
    df["rank"] = range(1, len(df) + 1)
    return df


def generate_policy_simulator(params: Dict) -> pd.DataFrame:
    """Generate policy_package_simulator.csv for Phase B."""
    base = waterfall_model(params)
    base_comp = base["completions"]
    base_eff = base["effective_completions"]

    # Generate combinations of 3 policy levers
    scenarios = []

    # Lever options
    perm_options = [38000, 48000, 58000]
    lapse_options = [0.095, 0.0475]
    ccc_options = [0.409, 0.509]
    cap_options = [None, 40000, 50000]
    opt_options = [0.0, 0.90]

    scenario_id = 0
    for pv in perm_options:
        for lr in lapse_options:
            for ccc in ccc_options:
                for cap in cap_options:
                    for opt in opt_options:
                        p = params.copy()
                        p["permission_volume"] = pv
                        p["lapse_rate"] = lr
                        p["ccc_filing_rate"] = ccc
                        p["capacity_ceiling"] = cap
                        p["opt_out_build_rate"] = opt
                        r = waterfall_model(p)
                        scenarios.append({
                            "scenario_id": f"S{scenario_id:03d}",
                            "permission_volume": pv,
                            "lapse_rate": lr,
                            "ccc_filing_rate": ccc,
                            "capacity_ceiling": cap if cap else "uncapped",
                            "opt_out_build_rate": opt,
                            "completions": round(r["completions"]),
                            "effective_completions": round(r["effective_completions"]),
                            "projected_additional_completions_yr": round(r["effective_completions"] - base_eff),
                            "yield": round(r["yield"], 3),
                            "effective_yield": round(r["effective_yield"], 3),
                        })
                        scenario_id += 1

    return pd.DataFrame(scenarios)


# =============================================================================
# RESULTS.TSV WRITER
# =============================================================================
def write_results_tsv(params: Dict):
    """Write results.tsv with all experiment rows."""
    rows = []

    # E00
    base = waterfall_model(params)
    rows.append({
        "id": "E00", "phase": "0.5", "family": "waterfall",
        "metric": "completions", "value": round(base["completions"]),
        "status": "KEEP", "seed": 42,
        "description": f"Baseline: {params['permission_volume']} perms, {base['yield']:.1%} yield, {round(base['completions'])} completions"
    })

    # Tournament rows
    families = run_tournament(params)
    for f in families:
        rows.append({
            "id": f["family"], "phase": "1", "family": f["family"],
            "metric": f["metric"], "value": f["value"],
            "status": "KEEP", "seed": 42,
            "description": f["description"]
        })

    # Phase 2 experiments
    experiments = run_all_experiments(params)
    for e in experiments:
        if e["id"] == "E00":
            continue  # Already added
        rows.append({
            "id": e["id"], "phase": "2", "family": "waterfall",
            "metric": e.get("metric", "delta_completions"),
            "value": e.get("value", e.get("delta_completions", 0)),
            "status": e["status"], "seed": 42,
            "description": e["description"]
        })

    # Phase 2.5 interactions
    interactions = run_pairwise_interactions(params)
    for p in interactions:
        rows.append({
            "id": p["id"], "phase": "2.5", "family": "waterfall",
            "metric": "interaction_effect",
            "value": round(p["interaction_effect"]),
            "status": p["status"], "seed": 42,
            "interaction": True,
            "description": p["pair"]
        })

    # Phase B
    rows.append({
        "id": "B01", "phase": "B", "family": "discovery",
        "metric": "bottleneck_ranking", "value": "bottleneck_ranking.csv",
        "status": "KEEP", "seed": 42,
        "description": "Bottleneck ranking by marginal units/yr"
    })
    rows.append({
        "id": "B02", "phase": "B", "family": "discovery",
        "metric": "policy_simulator", "value": "policy_package_simulator.csv",
        "status": "KEEP", "seed": 42,
        "description": "Policy package simulator"
    })

    df = pd.DataFrame(rows)
    df.to_csv(PROJECT_DIR / "results.tsv", sep="\t", index=False)
    return df


# =============================================================================
# TOURNAMENT RESULTS CSV
# =============================================================================
def write_tournament_csv(params: Dict):
    """Write tournament_results.csv."""
    families = run_tournament(params)
    df = pd.DataFrame(families)
    df.to_csv(PROJECT_DIR / "tournament_results.csv", index=False)
    return df


# =============================================================================
# MAIN
# =============================================================================
# =============================================================================
# PHASE 2.75 MANDATED EXPERIMENTS (R1-R4)
# =============================================================================

def run_opt_out_sensitivity(params: Dict) -> List[Dict]:
    """
    R1: Opt-out sensitivity sweep at 50%, 70%, 90%, 100% build rates.
    For each, compute effective yield, effective completions,
    and marginal impact of +10k permissions vs +10pp CCC.
    Report whether the #1/#3 ranking swaps.
    """
    base = waterfall_model(params)
    results = []

    for opt_rate in [0.50, 0.70, 0.90, 1.00]:
        # Effective completions at this opt-out rate
        p = params.copy()
        p["opt_out_build_rate"] = opt_rate
        r = waterfall_model(p)

        # Marginal from +10k permissions at this opt-out rate
        p_perm = p.copy()
        p_perm["permission_volume"] = params["permission_volume"] + 10000
        r_perm = waterfall_model(p_perm)
        perm_marginal = r_perm["effective_completions"] - r["effective_completions"]

        # Marginal from +10pp CCC at this opt-out rate
        p_ccc = p.copy()
        p_ccc["ccc_filing_rate"] = params["ccc_filing_rate"] + 0.10
        r_ccc = waterfall_model(p_ccc)
        ccc_marginal = r_ccc["effective_completions"] - r["effective_completions"]

        # Does CCC outrank permissions?
        ranking_swaps = ccc_marginal > perm_marginal

        results.append({
            "opt_out_build_rate": opt_rate,
            "effective_yield": r["effective_yield"],
            "effective_completions": r["effective_completions"],
            "perm_marginal": perm_marginal,
            "ccc_marginal": ccc_marginal,
            "ranking_swaps": ranking_swaps,
        })

    return results


def run_ranking_robustness(params: Dict, n_draws: int = 5000, seed: int = 42) -> Dict:
    """
    R2: Monte Carlo ranking robustness.
    Draw parameter sets from stated CIs and check if the bottleneck
    ranking is preserved.
    """
    rng = np.random.default_rng(seed)

    perm_rank1_count = 0
    ccc_outranks_perm_count = 0
    perm_marginals = []
    ccc_marginals = []
    lapse_marginals = []
    abp_marginals = []
    jr_marginals = []

    for _ in range(n_draws):
        p = params.copy()

        # Sample parameters from CIs
        p["lapse_rate"] = rng.triangular(
            params["lapse_rate_ci_lo"], params["lapse_rate"], params["lapse_rate_ci_hi"]
        )
        p["ccc_filing_rate"] = rng.normal(params["ccc_filing_rate"], 0.01)
        p["ccc_filing_rate"] = max(0.01, min(0.99, p["ccc_filing_rate"]))
        p["permission_volume"] = rng.normal(params["permission_volume"], 3000)
        p["permission_volume"] = max(10000, p["permission_volume"])
        p["ccc_to_occupied"] = rng.triangular(0.90, 0.95, 0.99)
        p["opt_out_build_rate"] = rng.uniform(0.50, 1.00)

        base = waterfall_model(p)

        # Permission marginal (+10k)
        pp = p.copy()
        pp["permission_volume"] = p["permission_volume"] + 10000
        rr = waterfall_model(pp)
        pm = rr["effective_completions"] - base["effective_completions"]
        perm_marginals.append(pm)

        # CCC marginal (+10pp)
        pp = p.copy()
        pp["ccc_filing_rate"] = p["ccc_filing_rate"] + 0.10
        rr = waterfall_model(pp)
        cm = rr["effective_completions"] - base["effective_completions"]
        ccc_marginals.append(cm)

        # Lapse marginal (halved)
        pp = p.copy()
        pp["lapse_rate"] = p["lapse_rate"] / 2
        rr = waterfall_model(pp)
        lm = rr["effective_completions"] - base["effective_completions"]
        lapse_marginals.append(lm)

        # ABP marginal (from counterfactual, scaled by sampled params)
        abp_m = params["jr_counterfactual_uncapped"] / params["jr_years"]
        abp_marginals.append(abp_m)

        # JR marginal (from counterfactual)
        jr_m = params["jr_counterfactual_35k"] / params["jr_years"]
        jr_marginals.append(jr_m)

        # Rank: who is #1?
        marginals = {
            "perm": pm,
            "ccc": cm,
            "lapse": lm,
        }
        top = max(marginals, key=marginals.get)
        if top == "perm":
            perm_rank1_count += 1
        if cm > pm:
            ccc_outranks_perm_count += 1

    perm_arr = np.array(perm_marginals)
    ccc_arr = np.array(ccc_marginals)
    lapse_arr = np.array(lapse_marginals)
    abp_arr = np.array(abp_marginals)
    jr_arr = np.array(jr_marginals)

    return {
        "perm_rank1_frac": perm_rank1_count / n_draws,
        "ccc_outranks_perm_frac": ccc_outranks_perm_count / n_draws,
        "perm_marginal_ci_lo": float(np.percentile(perm_arr, 5)),
        "perm_marginal_ci_hi": float(np.percentile(perm_arr, 95)),
        "perm_marginal_median": float(np.median(perm_arr)),
        "ccc_marginal_ci_lo": float(np.percentile(ccc_arr, 5)),
        "ccc_marginal_ci_hi": float(np.percentile(ccc_arr, 95)),
        "ccc_marginal_median": float(np.median(ccc_arr)),
        "lapse_marginal_ci_lo": float(np.percentile(lapse_arr, 5)),
        "lapse_marginal_ci_hi": float(np.percentile(lapse_arr, 95)),
        "lapse_marginal_median": float(np.median(lapse_arr)),
        "abp_marginal_ci_lo": float(np.percentile(abp_arr, 5)),
        "abp_marginal_ci_hi": float(np.percentile(abp_arr, 95)),
        "jr_marginal_ci_lo": float(np.percentile(jr_arr, 5)),
        "jr_marginal_ci_hi": float(np.percentile(jr_arr, 95)),
        "n_draws": n_draws,
    }


def run_abp_jr_overlap_audit(params: Dict) -> Dict:
    """
    R3: Audit ABP/JR double-counting in combined-intervention scenario.

    The S-2 paper computes two counterfactuals:
    - ABP at 18 weeks (E03a): all excess ABP delay removed, including JR-caused delay.
      This is the UNCAPPED counterfactual (16,638 units / 7 years = 2,377/yr).
    - JR removed (E04): direct JR delay removed, with 35k capacity cap.
      This is 7,421 units / 7 years = 1,060/yr.

    The ABP counterfactual INCLUDES JR-induced delay (JR caused some of the excess
    ABP weeks). Therefore the overlap is 100%: the ABP counterfactual subsumes the
    JR effect on decision times. They are NOT independent interventions.

    The correct non-overlapping combination is:
    - ABP at 18 weeks (which includes JR removal as part of the speed gain)
    - NOT ABP + JR separately

    We use the 35k-capped ABP counterfactual for the combined figure since
    construction capacity binds.
    """
    abp_uncapped = params["jr_counterfactual_uncapped"] / params["jr_years"]
    abp_35k = params["jr_counterfactual_35k"] / params["jr_years"]
    jr_35k = params["jr_counterfactual_35k"] / params["jr_years"]

    # The ABP counterfactual includes the JR channel. The overlap is 100%:
    # removing JR is a subset of restoring ABP to 18 weeks.
    # The S-2 paper derives ABP speed from the same mechanism that JR disrupted.
    overlap_fraction = 1.0  # Complete overlap: JR removal is subsumed by ABP restoration

    # Non-overlapping combined = max(ABP, JR), not sum
    combined_no_overlap = max(abp_35k, jr_35k)

    # Revised "all efficiency" figure
    # Original: ABP (1,060) + JR (1,060) + lapse halved (701) + CCC +10pp (3,267) = 6,088
    # Corrected: ABP/JR (1,060, not double-counted) + lapse (701) + CCC (3,267) = 5,028
    base = waterfall_model(params)
    p_lapse = params.copy()
    p_lapse["lapse_rate"] = params["lapse_rate"] / 2
    r_lapse = waterfall_model(p_lapse)
    lapse_delta = r_lapse["completions"] - base["completions"]

    p_ccc = params.copy()
    p_ccc["ccc_filing_rate"] = params["ccc_filing_rate"] + 0.10
    r_ccc = waterfall_model(p_ccc)
    ccc_delta = r_ccc["completions"] - base["completions"]

    revised_all_efficiency = combined_no_overlap + lapse_delta + ccc_delta

    return {
        "abp_marginal": abp_35k,
        "jr_marginal": jr_35k,
        "overlap_fraction": overlap_fraction,
        "combined_no_overlap": combined_no_overlap,
        "lapse_delta": lapse_delta,
        "ccc_delta": ccc_delta,
        "revised_all_efficiency": revised_all_efficiency,
        "original_all_efficiency": abp_35k + jr_35k + lapse_delta + ccc_delta,
        "double_count_units": abp_35k,  # The entire JR figure was double-counted
    }


def run_bootstrap_marginal_cis(params: Dict, n_draws: int = 5000, seed: int = 42) -> List[Dict]:
    """
    R4: Bootstrap 95% CIs on marginal-units-per-year for top 5 bottlenecks.
    """
    rng = np.random.default_rng(seed)

    marginals_perm = []
    marginals_ccc = []
    marginals_lapse = []
    marginals_abp = []
    marginals_jr = []

    for _ in range(n_draws):
        p = params.copy()

        # Sample parameters
        p["lapse_rate"] = rng.triangular(
            params["lapse_rate_ci_lo"], params["lapse_rate"], params["lapse_rate_ci_hi"]
        )
        p["ccc_filing_rate"] = rng.normal(params["ccc_filing_rate"], 0.01)
        p["ccc_filing_rate"] = max(0.01, min(0.99, p["ccc_filing_rate"]))
        p["permission_volume"] = rng.normal(params["permission_volume"], 3000)
        p["permission_volume"] = max(10000, p["permission_volume"])
        p["ccc_to_occupied"] = rng.triangular(0.90, 0.95, 0.99)

        base = waterfall_model(p)

        # Permission volume +10k
        pp = p.copy()
        pp["permission_volume"] = p["permission_volume"] + 10000
        rr = waterfall_model(pp)
        marginals_perm.append(rr["completions"] - base["completions"])

        # CCC +10pp
        pp = p.copy()
        pp["ccc_filing_rate"] = p["ccc_filing_rate"] + 0.10
        rr = waterfall_model(pp)
        marginals_ccc.append(rr["completions"] - base["completions"])

        # Lapse halved
        pp = p.copy()
        pp["lapse_rate"] = p["lapse_rate"] / 2
        rr = waterfall_model(pp)
        marginals_lapse.append(rr["completions"] - base["completions"])

        # ABP (from S-2 counterfactual — uncertainty in the JR range)
        jr_range_lo = params["jr_direct_range_lo"]
        jr_range_hi = params["jr_direct_range_hi"]
        jr_central = params["jr_counterfactual_35k"]
        # Scale counterfactual proportionally to unit-month uncertainty
        scale_factor = rng.triangular(
            jr_range_lo / params["jr_direct_unit_months"],
            1.0,
            jr_range_hi / params["jr_direct_unit_months"]
        )
        abp_m = (params["jr_counterfactual_uncapped"] / params["jr_years"]) * scale_factor
        marginals_abp.append(abp_m)

        jr_m = (params["jr_counterfactual_35k"] / params["jr_years"]) * scale_factor
        marginals_jr.append(jr_m)

    results = []
    for name, arr in [
        ("permission_volume", marginals_perm),
        ("ccc_filing_rate", marginals_ccc),
        ("permission_lapse", marginals_lapse),
        ("abp_decision_time", marginals_abp),
        ("judicial_review", marginals_jr),
    ]:
        a = np.array(arr)
        results.append({
            "bottleneck": name,
            "marginal_point": float(np.median(a)),
            "ci_lo": float(np.percentile(a, 2.5)),
            "ci_hi": float(np.percentile(a, 97.5)),
            "mean": float(np.mean(a)),
        })

    return results


def main():
    """Run the full analysis pipeline."""
    print("=" * 60)
    print("IRISH HOUSING BOTTLENECK SYNTHESIS")
    print("=" * 60)

    # Phase 0.5: Baseline
    print("\n--- Phase 0.5: Baseline ---")
    base = waterfall_model(PARAMS)
    print(f"Permissions:  {base['permissions']:>10,}")
    print(f"Lapsed:       {base['lapsed']:>10,.0f}  ({PARAMS['lapse_rate']:.1%})")
    print(f"Commenced:    {base['commenced']:>10,.0f}")
    print(f"CCC filed:    {base['ccc_filed']:>10,.0f}  ({PARAMS['ccc_filing_rate']:.1%} of commenced)")
    print(f"CCC non-filed:{base['ccc_non_filed']:>10,.0f}")
    print(f"Completions:  {base['completions']:>10,.0f}  (yield = {base['yield']:.1%})")

    # Phase 1: Tournament
    print("\n--- Phase 1: Tournament ---")
    families = run_tournament(PARAMS)
    for f in families:
        print(f"  {f['family']:20s}  {f['metric']:30s}  {f['value']}")

    # Phase 2: Experiments
    print("\n--- Phase 2: Experiments ---")
    experiments = run_all_experiments(PARAMS)
    print(f"  {len(experiments)} experiments completed")
    for e in experiments[:5]:
        print(f"  {e['id']:6s}  {e['description'][:50]:50s}  delta={e['delta_completions']:>8,.0f}  {e['status']}")
    print(f"  ... and {len(experiments)-5} more")

    # Phase 2.5: Interactions
    print("\n--- Phase 2.5: Pairwise Interactions ---")
    interactions = run_pairwise_interactions(PARAMS)
    for p in interactions:
        print(f"  {p['id']}  {p['pair']:40s}  sum={p['individual_sum']:>8,.0f}  combined={p['combined']:>8,.0f}  interaction={p['interaction_effect']:>+8,.0f}")

    # Write results
    print("\n--- Writing artifacts ---")
    write_results_tsv(PARAMS)
    print("  results.tsv written")
    write_tournament_csv(PARAMS)
    print("  tournament_results.csv written")

    # Phase B: Discovery outputs
    print("\n--- Phase B: Discovery ---")
    ranking = generate_bottleneck_ranking(PARAMS)
    ranking.to_csv(PROJECT_DIR / "discoveries" / "bottleneck_ranking.csv", index=False)
    print("  discoveries/bottleneck_ranking.csv written")
    print("\n  BOTTLENECK RANKING:")
    for _, row in ranking.iterrows():
        print(f"    #{row['rank']:2d}  {row['bottleneck']:25s}  {row['marginal_units_per_year']:>+8,} units/yr  {row['scenario']}")

    simulator = generate_policy_simulator(PARAMS)
    simulator.to_csv(PROJECT_DIR / "discoveries" / "policy_package_simulator.csv", index=False)
    print(f"\n  discoveries/policy_package_simulator.csv written ({len(simulator)} scenarios)")

    # Print headline finding
    print("\n" + "=" * 60)
    print("HEADLINE FINDING")
    print("=" * 60)
    ranking_top3 = ranking.head(3)
    for _, row in ranking_top3.iterrows():
        print(f"  #{row['rank']}  {row['bottleneck']:25s}  {row['marginal_units_per_year']:>+8,} units/yr")

    # Opt-out adjustment
    p = PARAMS.copy(); p["opt_out_build_rate"] = 0.90
    r = waterfall_model(p)
    print(f"\n  Opt-out adjustment (90% built): effective yield {r['effective_yield']:.1%} vs {base['yield']:.1%}")
    print(f"  Effective completions: {r['effective_completions']:,.0f} vs {base['completions']:,.0f} (+{r['effective_completions']-base['completions']:,.0f})")

    print(f"\n  SINGLE MOST IMPORTANT POLICY FINDING:")
    print(f"  Ireland grants ~38,000 housing permissions per year.")
    print(f"  At the measured pipeline yield of {base['yield']:.1%}, this produces ~{base['completions']:,.0f} certified completions.")
    print(f"  The HFA target is {PARAMS['hfa_target']:,}. The gap is {PARAMS['hfa_target'] - base['completions']:,.0f}.")
    print(f"  No intervention on lapse, CCC filing, ABP speed, or JR can close this gap.")
    print(f"  Only increasing permission volume (or construction capacity) can.")


if __name__ == "__main__":
    main()
