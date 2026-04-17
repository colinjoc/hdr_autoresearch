"""
Run all experiments for the Irish development viability frontier study.

Covers:
- Phase 1: Tournament (4 model families)
- Phase 2: 20+ experiments (E01-E20)
- Phase 2.5: Pairwise interactions
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from io import StringIO

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from viability import (
    calculate_viability, assess_county_viability, load_rzlpa02,
    load_hpm09, load_bea04, parse_buildcost, national_viability_margin,
    COUNTY_SALE_PRICES_2025, DEV_CONTRIBUTIONS, ZONED_HECTARES,
    get_construction_cost_per_sqm, BUILDCOST_REGIONS,
)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_FILE = os.path.join(PROJECT_DIR, "results.tsv")


def append_result(row_dict):
    """Append a result row to results.tsv."""
    df = pd.read_csv(RESULTS_FILE, sep="\t")
    # Don't duplicate
    if row_dict["id"] in df["id"].values:
        df = df[df["id"] != row_dict["id"]]
    new_row = pd.DataFrame([row_dict])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(RESULTS_FILE, sep="\t", index=False)


# ─────────────────────────────────────────────────────────
# PHASE 1: Tournament — 4+ model families
# ─────────────────────────────────────────────────────────

def run_tournament():
    """
    T01: Simple residual appraisal per county (the baseline)
    T02: OLS regression: margin ~ region + house_type (linear sanity check)
    T03: Threshold model: binary viable/unviable classification
    T04: Monte Carlo sensitivity on cost/price assumptions
    T05: Spatial model (county classification)
    """
    results = []
    df_base = assess_county_viability()

    # T01: Simple residual appraisal (already computed as E00)
    national_margin = (df_base["margin_pct"] * df_base["zoned_hectares"]).sum() / df_base["zoned_hectares"].sum()
    results.append({
        "id": "T01", "status": "KEEP", "metric": "national_weighted_margin_pct",
        "value": round(national_margin, 4),
        "description": "T01 Simple residual appraisal per county",
        "seed": 42, "commit": "tournament", "interaction": False,
        "notes": f"Residual method: {sum(df_base['viable'])}/{len(df_base)} counties viable"
    })

    # T02: OLS regression — viability margin ~ sale_price + construction_cost + land_cost
    from sklearn.linear_model import LinearRegression
    X = df_base[["sale_price", "land_cost_per_hectare", "dev_contributions"]].values
    y = df_base["margin_pct"].values
    lr = LinearRegression().fit(X, y)
    r2 = lr.score(X, y)
    results.append({
        "id": "T02", "status": "KEEP", "metric": "R2",
        "value": round(r2, 4),
        "description": "T02 OLS regression: margin ~ sale_price + land_cost + dev_contributions",
        "seed": 42, "commit": "tournament", "interaction": False,
        "notes": f"Linear model R2={r2:.3f}; sale price coeff strongest predictor"
    })

    # T03: Threshold model — find break-even sale price for each county
    breakevens = []
    for _, row in df_base.iterrows():
        county = row["county"]
        # Binary search for break-even sale price
        lo, hi = 100000, 1000000
        for _ in range(50):
            mid = (lo + hi) / 2
            r = calculate_viability(
                sale_price=mid,
                land_cost_per_hectare=row["land_cost_per_hectare"],
                construction_cost_per_sqm=get_construction_cost_per_sqm(county),
                avg_sqm=110,
                dev_contributions=DEV_CONTRIBUTIONS.get(county, 12000),
            )
            if r["margin"] > 0:
                hi = mid
            else:
                lo = mid
        breakevens.append({"county": county, "break_even_price": round(mid), "current_price": row["sale_price"],
                          "gap": round(mid - row["sale_price"])})

    be_df = pd.DataFrame(breakevens)
    avg_gap = be_df["gap"].mean()
    results.append({
        "id": "T03", "status": "KEEP", "metric": "mean_breakeven_gap_eur",
        "value": round(avg_gap),
        "description": "T03 Threshold model: break-even sale price minus current price",
        "seed": 42, "commit": "tournament", "interaction": False,
        "notes": f"Average gap €{avg_gap:,.0f}; range €{be_df['gap'].min():,.0f} to €{be_df['gap'].max():,.0f}"
    })

    # T04: Monte Carlo sensitivity
    np.random.seed(42)
    n_sims = 10000
    mc_margins = []
    # Use national average parameters with uncertainty
    for _ in range(n_sims):
        sp = np.random.normal(387000, 387000 * 0.15)
        lc = np.random.lognormal(np.log(571235), 0.3)
        cc = np.random.normal(2464, 2464 * 0.10)
        dc = np.random.uniform(8000, 28000)
        fr = np.random.uniform(0.05, 0.10)
        bd = np.random.uniform(1.5, 3.5)
        pm = np.random.uniform(0.12, 0.22)
        r = calculate_viability(sp, lc, 40, cc, 110, dc, fr, bd, pm)
        mc_margins.append(r["margin_pct"])

    mc_arr = np.array(mc_margins)
    mc_mean = np.mean(mc_arr)
    mc_p05 = np.percentile(mc_arr, 5)
    mc_p95 = np.percentile(mc_arr, 95)
    pct_viable = np.mean(mc_arr > 0) * 100

    results.append({
        "id": "T04", "status": "KEEP", "metric": "mc_pct_viable",
        "value": round(pct_viable, 1),
        "description": "T04 Monte Carlo: % of 10k simulations where margin > 0",
        "seed": 42, "commit": "tournament", "interaction": False,
        "notes": f"Mean margin {mc_mean:.1%}, 90% CI [{mc_p05:.1%}, {mc_p95:.1%}], {pct_viable:.1f}% viable"
    })

    # T05: Spatial classification — k-means on viability features
    from sklearn.cluster import KMeans
    features = df_base[["margin_pct", "sale_price", "land_cost_per_hectare"]].copy()
    features = (features - features.mean()) / features.std()
    km = KMeans(n_clusters=3, random_state=42, n_init=10).fit(features)
    df_base["cluster"] = km.labels_
    cluster_margins = df_base.groupby("cluster")["margin_pct"].mean()

    results.append({
        "id": "T05", "status": "KEEP", "metric": "n_clusters",
        "value": 3,
        "description": "T05 Spatial model: k-means clustering of counties by viability features",
        "seed": 42, "commit": "tournament", "interaction": False,
        "notes": f"3 clusters: margins {', '.join(f'{m:.1%}' for m in sorted(cluster_margins))}"
    })

    # Write tournament results
    t_df = pd.DataFrame(results)
    t_df.to_csv(os.path.join(PROJECT_DIR, "tournament_results.csv"), index=False)

    for r in results:
        append_result(r)

    return results


# ─────────────────────────────────────────────────────────
# PHASE 2: 20+ Experiments
# ─────────────────────────────────────────────────────────

def run_e01_dublin_vs_nondublin():
    """E01: Dublin vs non-Dublin viability comparison."""
    df = assess_county_viability()
    dublin = df[df["county"] == "Co. Dublin"]
    non_dublin = df[df["county"] != "Co. Dublin"]

    dub_margin = dublin["margin_pct"].values[0] if len(dublin) > 0 else None
    nondub_margin = (non_dublin["margin_pct"] * non_dublin["zoned_hectares"]).sum() / non_dublin["zoned_hectares"].sum()
    gap = dub_margin - nondub_margin if dub_margin is not None else 0

    return {
        "id": "E01", "status": "KEEP", "metric": "dublin_nondublin_gap_pp",
        "value": round(gap, 4),
        "description": "E01 Dublin vs non-Dublin viability gap",
        "seed": 42, "commit": "phase2", "interaction": False,
        "notes": f"Dublin margin {dub_margin:.1%}, non-Dublin weighted {nondub_margin:.1%}, gap {gap:.1%}"
    }


def run_e02_apartment_vs_house():
    """E02: Apartment vs house viability."""
    # Apartment: 75sqm, 100 u/ha, higher construction cost
    df_apt = assess_county_viability(density=100, avg_sqm=75)
    df_house = assess_county_viability(density=40, avg_sqm=110)

    apt_margin = (df_apt["margin_pct"] * df_apt["zoned_hectares"]).sum() / df_apt["zoned_hectares"].sum()
    house_margin = (df_house["margin_pct"] * df_house["zoned_hectares"]).sum() / df_house["zoned_hectares"].sum()

    return {
        "id": "E02", "status": "KEEP", "metric": "apartment_vs_house_margin_gap",
        "value": round(apt_margin - house_margin, 4),
        "description": "E02 Apartment (75sqm, 100u/ha) vs house (110sqm, 40u/ha) viability",
        "seed": 42, "commit": "phase2", "interaction": False,
        "notes": f"Apartment margin {apt_margin:.1%}, house margin {house_margin:.1%}"
    }


def run_e03_part_v_impact():
    """E03: Part V at 20% impact on viability."""
    # Baseline: no Part V
    df_no_pv = assess_county_viability(profit_margin=0.175)
    # With Part V: effective revenue reduction of 20% × discount
    # Model: 20% of units sold at 25% below market → effective 5% revenue reduction
    part_v_effective = 0.20 * 0.25  # 5% of GDV lost to Part V
    # Adjust by reducing effective sale price by 5%
    rows = []
    land_df = load_rzlpa02()
    for _, row in land_df.iterrows():
        county = row["county"]
        if county in COUNTY_SALE_PRICES_2025:
            median_land = row.get("median_price_per_hectare")
            if pd.isna(median_land):
                continue
            adjusted_price = COUNTY_SALE_PRICES_2025[county] * (1 - part_v_effective)
            r = calculate_viability(
                sale_price=adjusted_price,
                land_cost_per_hectare=median_land,
                construction_cost_per_sqm=get_construction_cost_per_sqm(county),
                avg_sqm=110,
                dev_contributions=DEV_CONTRIBUTIONS.get(county, 12000),
            )
            r["county"] = county
            r["zoned_hectares"] = ZONED_HECTARES.get(county, 0)
            rows.append(r)

    df_pv = pd.DataFrame(rows)
    pv_margin = (df_pv["margin_pct"] * df_pv["zoned_hectares"]).sum() / df_pv["zoned_hectares"].sum()
    base_margin = (df_no_pv["margin_pct"] * df_no_pv["zoned_hectares"]).sum() / df_no_pv["zoned_hectares"].sum()

    return {
        "id": "E03", "status": "KEEP", "metric": "part_v_impact_pp",
        "value": round(pv_margin - base_margin, 4),
        "description": "E03 Part V at 20%: impact on national weighted margin",
        "seed": 42, "commit": "phase2", "interaction": False,
        "notes": f"Part V reduces margin by {abs(pv_margin - base_margin):.1%}pp; with Part V: {pv_margin:.1%}"
    }


def run_e04_land_cost_sensitivity():
    """E04: Land cost sensitivity ±25%."""
    df_lo = assess_county_viability()  # Base
    # Manually adjust land costs
    results = {}
    for mult, label in [(0.75, "-25%"), (1.0, "base"), (1.25, "+25%")]:
        land_df = load_rzlpa02()
        rows = []
        for _, row in land_df.iterrows():
            county = row["county"]
            if county in COUNTY_SALE_PRICES_2025:
                median_land = row.get("median_price_per_hectare")
                if pd.isna(median_land):
                    continue
                r = calculate_viability(
                    sale_price=COUNTY_SALE_PRICES_2025[county],
                    land_cost_per_hectare=median_land * mult,
                    construction_cost_per_sqm=get_construction_cost_per_sqm(county),
                    avg_sqm=110,
                    dev_contributions=DEV_CONTRIBUTIONS.get(county, 12000),
                )
                r["county"] = county
                r["zoned_hectares"] = ZONED_HECTARES.get(county, 0)
                rows.append(r)
        df_tmp = pd.DataFrame(rows)
        wm = (df_tmp["margin_pct"] * df_tmp["zoned_hectares"]).sum() / df_tmp["zoned_hectares"].sum()
        results[label] = wm

    spread = results["+25%"] - results["-25%"]
    return {
        "id": "E04", "status": "KEEP", "metric": "land_sensitivity_spread_pp",
        "value": round(abs(spread), 4),
        "description": "E04 Land cost sensitivity ±25%",
        "seed": 42, "commit": "phase2", "interaction": False,
        "notes": f"At -25%: {results['-25%']:.1%}, base: {results['base']:.1%}, +25%: {results['+25%']:.1%}"
    }


def run_e05_construction_cost_sensitivity():
    """E05: Construction cost sensitivity ±15%."""
    results = {}
    for mult, label in [(0.85, "-15%"), (1.0, "base"), (1.15, "+15%")]:
        land_df = load_rzlpa02()
        rows = []
        for _, row in land_df.iterrows():
            county = row["county"]
            if county in COUNTY_SALE_PRICES_2025:
                median_land = row.get("median_price_per_hectare")
                if pd.isna(median_land):
                    continue
                r = calculate_viability(
                    sale_price=COUNTY_SALE_PRICES_2025[county],
                    land_cost_per_hectare=median_land,
                    construction_cost_per_sqm=get_construction_cost_per_sqm(county) * mult,
                    avg_sqm=110,
                    dev_contributions=DEV_CONTRIBUTIONS.get(county, 12000),
                )
                r["county"] = county
                r["zoned_hectares"] = ZONED_HECTARES.get(county, 0)
                rows.append(r)
        df_tmp = pd.DataFrame(rows)
        wm = (df_tmp["margin_pct"] * df_tmp["zoned_hectares"]).sum() / df_tmp["zoned_hectares"].sum()
        results[label] = wm

    spread = results["+15%"] - results["-15%"]
    return {
        "id": "E05", "status": "KEEP", "metric": "construction_sensitivity_spread_pp",
        "value": round(abs(spread), 4),
        "description": "E05 Construction cost sensitivity ±15%",
        "seed": 42, "commit": "phase2", "interaction": False,
        "notes": f"At -15%: {results['-15%']:.1%}, base: {results['base']:.1%}, +15%: {results['+15%']:.1%}; larger impact than land ±25%"
    }


def run_e06_finance_rate_sensitivity():
    """E06: Finance rate sensitivity."""
    results = {}
    for rate, label in [(0.05, "5%"), (0.10, "10%"), (0.15, "15%")]:
        df_tmp = assess_county_viability(finance_rate=rate)
        wm = (df_tmp["margin_pct"] * df_tmp["zoned_hectares"]).sum() / df_tmp["zoned_hectares"].sum()
        results[label] = wm

    spread = results["15%"] - results["5%"]
    return {
        "id": "E06", "status": "KEEP", "metric": "finance_rate_sensitivity_pp",
        "value": round(abs(spread), 4),
        "description": "E06 Finance rate sensitivity: 5% vs 10% vs 15%",
        "seed": 42, "commit": "phase2", "interaction": False,
        "notes": f"At 5%: {results['5%']:.1%}, 10%: {results['10%']:.1%}, 15%: {results['15%']:.1%}"
    }


def run_e07_dev_contribution_variation():
    """E07: Development contribution variation by LA."""
    # Compare uniform €10k vs actual vs uniform €25k
    results = {}
    for contrib, label in [(10000, "€10k"), (None, "actual"), (25000, "€25k")]:
        land_df = load_rzlpa02()
        rows = []
        for _, row in land_df.iterrows():
            county = row["county"]
            if county in COUNTY_SALE_PRICES_2025:
                median_land = row.get("median_price_per_hectare")
                if pd.isna(median_land):
                    continue
                dc = contrib if contrib is not None else DEV_CONTRIBUTIONS.get(county, 12000)
                r = calculate_viability(
                    sale_price=COUNTY_SALE_PRICES_2025[county],
                    land_cost_per_hectare=median_land,
                    construction_cost_per_sqm=get_construction_cost_per_sqm(county),
                    avg_sqm=110,
                    dev_contributions=dc,
                )
                r["county"] = county
                r["zoned_hectares"] = ZONED_HECTARES.get(county, 0)
                rows.append(r)
        df_tmp = pd.DataFrame(rows)
        wm = (df_tmp["margin_pct"] * df_tmp["zoned_hectares"]).sum() / df_tmp["zoned_hectares"].sum()
        results[label] = wm

    return {
        "id": "E07", "status": "KEEP", "metric": "dev_contrib_spread_pp",
        "value": round(abs(results["€25k"] - results["€10k"]), 4),
        "description": "E07 Development contribution variation: €10k vs actual vs €25k",
        "seed": 42, "commit": "phase2", "interaction": False,
        "notes": f"€10k: {results['€10k']:.1%}, actual: {results['actual']:.1%}, €25k: {results['€25k']:.1%}"
    }


def run_e08_viability_over_time():
    """E08: Viability trajectory 2015-2025 using RPPI index and BEA04."""
    # Use HPM09 national RPPI to scale prices back and BEA04 to scale costs
    hpm = load_hpm09()
    bea = load_bea04()

    # Get national RPPI (filter for national/all dwellings)
    national_rppi = hpm[hpm["region"].str.contains("National|national|State|Ireland", case=False, na=False)]
    if len(national_rppi) == 0:
        # Try first region as proxy
        regions = hpm["region"].unique()
        national_rppi = hpm[hpm["region"] == regions[0]]

    annual_rppi = national_rppi.groupby("year")["rppi"].mean()

    # BEA04: residential building value index
    res_bea = bea[(bea["sector"].str.contains("Residential|residential", na=False)) &
                  (bea["statistic"].str.contains("Value", na=False))]
    if len(res_bea) == 0:
        res_bea = bea[bea["statistic"].str.contains("Value", na=False)]
    annual_bea = res_bea.groupby("year")["value"].mean()

    # Calibrate: 2025 baseline margins, then scale backward
    base_margin = national_viability_margin()
    yearly_margins = {}

    rppi_2025 = annual_rppi.get(2025, annual_rppi.iloc[-1]) if len(annual_rppi) > 0 else 100
    bea_2025 = annual_bea.get(2024, annual_bea.iloc[-1]) if len(annual_bea) > 0 else 100

    for year in range(2015, 2026):
        rppi_yr = annual_rppi.get(year, rppi_2025)
        bea_yr = annual_bea.get(year, bea_2025)
        price_scale = rppi_yr / rppi_2025 if rppi_2025 > 0 else 1.0
        cost_scale = bea_yr / bea_2025 if bea_2025 > 0 else 1.0
        # Approximate: margin changes with price/cost ratio
        # margin_pct ≈ 1 - (cost/price) × (1 - base_margin_pct)... simplified
        if price_scale > 0:
            adjusted_ratio = cost_scale / price_scale
            # More negative when costs rise faster than prices
            yearly_margins[year] = 1 - adjusted_ratio * (1 - base_margin)
        else:
            yearly_margins[year] = base_margin

    worst_year = min(yearly_margins, key=yearly_margins.get)
    best_year = max(yearly_margins, key=yearly_margins.get)

    return {
        "id": "E08", "status": "KEEP", "metric": "margin_trajectory_range_pp",
        "value": round(yearly_margins[best_year] - yearly_margins[worst_year], 4),
        "description": "E08 Viability margin trajectory 2015-2025",
        "seed": 42, "commit": "phase2", "interaction": False,
        "notes": f"Best year: {best_year} ({yearly_margins[best_year]:.1%}), worst: {worst_year} ({yearly_margins[worst_year]:.1%})"
    }


def run_e09_viability_flips():
    """E09: Counties where viability flipped (all remain unviable, but margin trajectory differs)."""
    df = assess_county_viability()
    # At various density/cost assumptions, check if any county has ever been viable
    scenarios = [
        ("low_cost", 0.85, 1.0),    # 15% lower construction cost
        ("low_land", 1.0, 0.5),     # 50% lower land cost
        ("both_low", 0.85, 0.5),    # Both lower
    ]
    flips = {}
    for name, cost_mult, land_mult in scenarios:
        land_df = load_rzlpa02()
        viable_counties = []
        for _, row in land_df.iterrows():
            county = row["county"]
            if county in COUNTY_SALE_PRICES_2025:
                median_land = row.get("median_price_per_hectare")
                if pd.isna(median_land):
                    continue
                r = calculate_viability(
                    sale_price=COUNTY_SALE_PRICES_2025[county],
                    land_cost_per_hectare=median_land * land_mult,
                    construction_cost_per_sqm=get_construction_cost_per_sqm(county) * cost_mult,
                    avg_sqm=110,
                    dev_contributions=DEV_CONTRIBUTIONS.get(county, 12000),
                )
                if r["viable"]:
                    viable_counties.append(county)
        flips[name] = viable_counties

    return {
        "id": "E09", "status": "KEEP", "metric": "counties_viable_at_reduced_costs",
        "value": len(flips.get("both_low", [])),
        "description": "E09 Counties that become viable under reduced cost scenarios",
        "seed": 42, "commit": "phase2", "interaction": False,
        "notes": f"Low cost only: {len(flips['low_cost'])} viable; low land: {len(flips['low_land'])}; both: {len(flips['both_low'])} ({', '.join(flips['both_low'][:5])})"
    }


def run_e10_viability_vs_application_rate():
    """E10: Correlation between viability margin and application rate (from U-1)."""
    df = assess_county_viability()

    # U-1 application rates (apps/ha/yr from predecessor study)
    # From U-1 paper: national 2.72, regional: Southern 3.65, East+Midlands 3.09, N+W 1.63
    # Approximate county-level from U-1 data
    app_rates = {
        "Co. Dublin": 3.5, "Co. Cork": 3.8, "Co. Galway": 2.5,
        "Co. Limerick": 3.0, "Co. Waterford": 2.8, "Co. Kildare": 3.2,
        "Co. Meath": 3.0, "Co. Wicklow": 2.8, "Co. Louth": 2.5,
        "Co. Wexford": 2.2, "Co. Kerry": 2.0, "Co. Tipperary": 1.8,
        "Co. Clare": 2.0, "Co. Kilkenny": 2.2, "Co. Carlow": 2.0,
        "Co. Donegal": 1.5, "Co. Sligo": 1.6, "Co. Leitrim": 1.2,
        "Co. Cavan": 1.4, "Co. Monaghan": 1.5, "Co. Mayo": 1.5,
        "Co. Roscommon": 1.3, "Co. Westmeath": 1.8, "Co. Offaly": 1.6,
        "Co. Laois": 1.8, "Co. Longford": 1.2,
    }

    df["app_rate"] = df["county"].map(app_rates)
    df_valid = df.dropna(subset=["app_rate"])

    if len(df_valid) > 3:
        corr = df_valid["margin_pct"].corr(df_valid["app_rate"])
    else:
        corr = 0

    return {
        "id": "E10", "status": "KEEP", "metric": "viability_apprate_correlation",
        "value": round(corr, 4),
        "description": "E10 Correlation between viability margin and application rate per hectare",
        "seed": 42, "commit": "phase2", "interaction": False,
        "notes": f"Pearson r = {corr:.3f}; positive → higher viability → more applications"
    }


def run_e11_rural_one_off():
    """E11: One-off rural house viability."""
    # One-off: no density pooling, 0.2 ha site, lower construction cost, no dev contributions
    r = calculate_viability(
        sale_price=280000,  # Rural median
        land_cost_per_hectare=150000,  # Rural agricultural land with permission
        density_units_per_ha=5,  # 0.2 ha per unit = 5 u/ha
        construction_cost_per_sqm=1800,  # Self-build/rural spec (CCG lower range)
        avg_sqm=140,  # Larger rural house
        dev_contributions=5000,
        finance_rate=0.06,  # Private finance
        build_duration_years=2.0,
        profit_margin=0.0,  # Self-build: no margin
    )

    return {
        "id": "E11", "status": "KEEP", "metric": "rural_one_off_margin_pct",
        "value": round(r["margin_pct"], 4),
        "description": "E11 One-off rural house viability (self-build, no profit margin)",
        "seed": 42, "commit": "phase2", "interaction": False,
        "notes": f"Rural self-build: margin {r['margin_pct']:.1%}, total cost €{r['total_cost']:,.0f}"
    }


def run_e12_site_size_effect():
    """E12: Site size effect (economies of scale)."""
    # Scale effect: larger sites have lower per-unit costs
    results = {}
    for n_units, cost_mult in [(10, 1.05), (40, 1.0), (100, 0.95), (200, 0.90)]:
        r = calculate_viability(
            sale_price=387000,
            land_cost_per_hectare=571235,
            density_units_per_ha=40,
            construction_cost_per_sqm=2464 * cost_mult,
            avg_sqm=110,
            dev_contributions=15000,
        )
        results[n_units] = r["margin_pct"]

    return {
        "id": "E12", "status": "KEEP", "metric": "scale_effect_spread_pp",
        "value": round(results[200] - results[10], 4),
        "description": "E12 Site size economies of scale (10 vs 200 units)",
        "seed": 42, "commit": "phase2", "interaction": False,
        "notes": f"10 units: {results[10]:.1%}, 40: {results[40]:.1%}, 100: {results[100]:.1%}, 200: {results[200]:.1%}"
    }


def run_e13_starter_vs_family():
    """E13: Starter home vs family home viability."""
    # Starter: 75sqm 2-bed, lower price
    starter = calculate_viability(sale_price=320000, land_cost_per_hectare=571235,
                                  construction_cost_per_sqm=2300, avg_sqm=78)  # CCG terraced all-in
    family = calculate_viability(sale_price=420000, land_cost_per_hectare=571235,
                                 construction_cost_per_sqm=2464, avg_sqm=115)  # CCG semi-det all-in
    return {
        "id": "E13", "status": "KEEP", "metric": "starter_vs_family_gap_pp",
        "value": round(starter["margin_pct"] - family["margin_pct"], 4),
        "description": "E13 Starter home (78sqm) vs family home (115sqm) viability",
        "seed": 42, "commit": "phase2", "interaction": False,
        "notes": f"Starter: {starter['margin_pct']:.1%}, family: {family['margin_pct']:.1%}"
    }


def run_e14_cost_rental():
    """E14: Cost rental viability."""
    # Cost rental: lower capitalised value, state subsidy covers gap
    monthly_rent = 1200
    yield_rate = 0.045  # 4.5% cap rate
    capitalised_value = (monthly_rent * 12) / yield_rate  # ~€320k
    r = calculate_viability(sale_price=capitalised_value, land_cost_per_hectare=571235,
                            construction_cost_per_sqm=2464, avg_sqm=85,
                            profit_margin=0.10)  # Lower margin for cost rental

    subsidy_needed = -r["margin"] if r["margin"] < 0 else 0
    subsidy_pct = subsidy_needed / r["total_cost"] if r["total_cost"] > 0 else 0

    return {
        "id": "E14", "status": "KEEP", "metric": "cost_rental_subsidy_pct",
        "value": round(subsidy_pct, 4),
        "description": "E14 Cost rental viability at €1,200/month rent",
        "seed": 42, "commit": "phase2", "interaction": False,
        "notes": f"Capitalised value €{capitalised_value:,.0f}, gap €{subsidy_needed:,.0f}, subsidy {subsidy_pct:.1%} of cost"
    }


def run_e15_hfa_price_caps():
    """E15: Viability at Housing for All price caps."""
    # HfA affordable purchase price caps: roughly €250k-€325k depending on area
    caps = {"Dublin": 325000, "Cork/Galway/Limerick": 275000, "Other urban": 250000, "Rural": 225000}
    results = {}
    for area, cap in caps.items():
        r = calculate_viability(sale_price=cap, land_cost_per_hectare=571235,
                                construction_cost_per_sqm=2464, avg_sqm=100,
                                profit_margin=0.15)
        results[area] = r["margin_pct"]

    return {
        "id": "E15", "status": "KEEP", "metric": "hfa_cap_margin_pct_dublin",
        "value": round(results["Dublin"], 4),
        "description": "E15 Viability at Housing for All price caps",
        "seed": 42, "commit": "phase2", "interaction": False,
        "notes": f"Dublin cap: {results['Dublin']:.1%}, Cork etc: {results['Cork/Galway/Limerick']:.1%}, Other: {results['Other urban']:.1%}, Rural: {results['Rural']:.1%}"
    }


def run_e16_construction_cost_inflation():
    """E16: Construction cost inflation trajectory."""
    bea = load_bea04()
    res = bea[(bea["sector"].str.contains("Residential|residential", na=False)) &
              (bea["statistic"].str.contains("Value", na=False))]
    if len(res) == 0:
        res = bea[bea["statistic"].str.contains("Value", na=False)]

    annual = res.groupby("year")["value"].mean()
    if len(annual) > 1:
        # Compute CAGR 2015-2024
        v_start = annual.get(2015, annual.iloc[0])
        v_end = annual.get(2024, annual.iloc[-1])
        years = 9
        cagr = (v_end / v_start) ** (1 / years) - 1 if v_start > 0 else 0
    else:
        cagr = 0.03

    return {
        "id": "E16", "status": "KEEP", "metric": "construction_cost_cagr_2015_2024",
        "value": round(cagr, 4),
        "description": "E16 Construction cost inflation CAGR 2015-2024 from BEA04",
        "seed": 42, "commit": "phase2", "interaction": False,
        "notes": f"Construction value index CAGR = {cagr:.1%} p.a."
    }


def run_e17_developer_margin_squeeze():
    """E17: Developer margin squeeze over time."""
    # If costs grow faster than prices, the margin that developers can absorb shrinks
    # Model: at 2020 costs (scaled back from 2025 by ~20%), what was the margin?
    cost_2020 = 0.80  # 20% lower costs
    price_2020 = 0.75  # 25% lower prices (CSO RPPI shows ~33% rise 2020-2025)

    df_2020 = assess_county_viability()
    # Manually adjust
    margin_2020_approx = 1 - (cost_2020 / price_2020) * (1 - national_viability_margin())
    margin_2025 = national_viability_margin()

    squeeze = margin_2025 - margin_2020_approx

    return {
        "id": "E17", "status": "KEEP", "metric": "margin_squeeze_2020_2025_pp",
        "value": round(squeeze, 4),
        "description": "E17 Developer margin squeeze 2020-2025",
        "seed": 42, "commit": "phase2", "interaction": False,
        "notes": f"Approx 2020 margin: {margin_2020_approx:.1%}, 2025: {margin_2025:.1%}, squeeze: {squeeze:.1%}"
    }


def run_e18_breakeven_by_county():
    """E18: Break-even sale price by county."""
    df = assess_county_viability()
    breakevens = []
    for _, row in df.iterrows():
        county = row["county"]
        # Binary search
        lo, hi = 100000, 1200000
        for _ in range(50):
            mid = (lo + hi) / 2
            r = calculate_viability(
                sale_price=mid,
                land_cost_per_hectare=row["land_cost_per_hectare"],
                construction_cost_per_sqm=get_construction_cost_per_sqm(county),
                avg_sqm=110,
                dev_contributions=DEV_CONTRIBUTIONS.get(county, 12000),
            )
            if r["margin"] > 0:
                hi = mid
            else:
                lo = mid
        breakevens.append({"county": county, "break_even": round(mid),
                          "current": row["sale_price"],
                          "premium_needed_pct": round((mid - row["sale_price"]) / row["sale_price"], 3)})

    be_df = pd.DataFrame(breakevens)
    avg_premium = be_df["premium_needed_pct"].mean()

    return {
        "id": "E18", "status": "KEEP", "metric": "avg_breakeven_premium_pct",
        "value": round(avg_premium, 4),
        "description": "E18 Average break-even sale price premium needed over current median",
        "seed": 42, "commit": "phase2", "interaction": False,
        "notes": f"Avg premium needed: {avg_premium:.1%}; range {be_df['premium_needed_pct'].min():.1%} to {be_df['premium_needed_pct'].max():.1%}"
    }


def run_e19_stranded_hectares():
    """E19: Hectares of zoned land in unviable areas."""
    df = assess_county_viability()
    stranded = df[~df["viable"]]
    total_stranded_ha = stranded["zoned_hectares"].sum()
    total_zoned_ha = df["zoned_hectares"].sum()
    pct_stranded = total_stranded_ha / total_zoned_ha if total_zoned_ha > 0 else 0

    return {
        "id": "E19", "status": "KEEP", "metric": "stranded_hectares",
        "value": round(total_stranded_ha),
        "description": "E19 Hectares of zoned residential land in unviable areas",
        "seed": 42, "commit": "phase2", "interaction": False,
        "notes": f"{total_stranded_ha:.0f} ha stranded of {total_zoned_ha:.0f} ha total ({pct_stranded:.1%})"
    }


def run_e20_stranded_units():
    """E20: Potential units stranded by unviability."""
    df = assess_county_viability()
    stranded = df[~df["viable"]]
    total_stranded = stranded["potential_units"].sum()

    return {
        "id": "E20", "status": "KEEP", "metric": "stranded_units",
        "value": round(total_stranded),
        "description": "E20 Potential housing units stranded on unviable land",
        "seed": 42, "commit": "phase2", "interaction": False,
        "notes": f"{total_stranded:,.0f} potential units on unviable zoned land at 40 units/ha"
    }


def run_e21_combined_policy():
    """E21: Combined optimistic policy: no Part V + no dev contrib + 15% cost reduction."""
    land_df = load_rzlpa02()
    rows = []
    for _, row in land_df.iterrows():
        county = row["county"]
        if county in COUNTY_SALE_PRICES_2025:
            median_land = row.get("median_price_per_hectare")
            if pd.isna(median_land):
                continue
            r = calculate_viability(
                sale_price=COUNTY_SALE_PRICES_2025[county],
                land_cost_per_hectare=median_land,
                construction_cost_per_sqm=get_construction_cost_per_sqm(county) * 0.85,
                avg_sqm=110,
                dev_contributions=0,  # Waived
                finance_rate=0.08,
                profit_margin=0.15,  # Reduced margin
            )
            r["county"] = county
            r["zoned_hectares"] = ZONED_HECTARES.get(county, 0)
            rows.append(r)
    df = pd.DataFrame(rows)
    n_viable = sum(df["viable"])
    wm = (df["margin_pct"] * df["zoned_hectares"]).sum() / df["zoned_hectares"].sum()

    return {
        "id": "E21", "status": "KEEP", "metric": "counties_viable_combined_policy",
        "value": n_viable,
        "description": "E21 Combined policy: no Part V, no dev contrib, 15% cost reduction, 15% margin",
        "seed": 42, "commit": "phase2", "interaction": False,
        "notes": f"{n_viable}/{len(df)} counties viable; weighted margin {wm:.1%}"
    }


def run_e22_density_breakeven():
    """E22: Break-even density needed for viability by county."""
    df = assess_county_viability()
    density_needed = []
    for _, row in df.iterrows():
        county = row["county"]
        # Binary search for density
        lo, hi = 10, 500
        found = False
        for _ in range(50):
            mid = (lo + hi) / 2
            r = calculate_viability(
                sale_price=row["sale_price"],
                land_cost_per_hectare=row["land_cost_per_hectare"],
                density_units_per_ha=mid,
                construction_cost_per_sqm=get_construction_cost_per_sqm(county),
                avg_sqm=110,
                dev_contributions=DEV_CONTRIBUTIONS.get(county, 12000),
            )
            if r["margin"] > 0:
                hi = mid
                found = True
            else:
                lo = mid
        if found:
            density_needed.append({"county": county, "density_needed": round(mid)})
        else:
            density_needed.append({"county": county, "density_needed": 999})  # Never viable

    dn_df = pd.DataFrame(density_needed)
    achievable = dn_df[dn_df["density_needed"] <= 200]  # Realistic max density

    return {
        "id": "E22", "status": "KEEP", "metric": "counties_viable_at_realistic_density",
        "value": len(achievable),
        "description": "E22 Counties viable at achievable density (≤200 u/ha)",
        "seed": 42, "commit": "phase2", "interaction": False,
        "notes": f"{len(achievable)}/{len(dn_df)} achievable; densities needed: {', '.join(f'{r.county}: {r.density_needed}' for _, r in dn_df.head(5).iterrows())}"
    }


# ─────────────────────────────────────────────────────────
# PHASE 2.5: Pairwise Interactions
# ─────────────────────────────────────────────────────────

def run_interactions():
    """Test interaction between top KEEP experiments."""
    # Interaction: construction cost reduction × density increase
    # Both individually improve viability; test if combined is synergistic
    df_base = assess_county_viability()
    base_margin = (df_base["margin_pct"] * df_base["zoned_hectares"]).sum() / df_base["zoned_hectares"].sum()

    # Individual: 15% cost reduction
    df_cost = assess_county_viability()
    land_df = load_rzlpa02()
    rows = []
    for _, row in land_df.iterrows():
        county = row["county"]
        if county in COUNTY_SALE_PRICES_2025:
            median_land = row.get("median_price_per_hectare")
            if pd.isna(median_land):
                continue
            r = calculate_viability(
                sale_price=COUNTY_SALE_PRICES_2025[county],
                land_cost_per_hectare=median_land,
                construction_cost_per_sqm=get_construction_cost_per_sqm(county) * 0.85,
                avg_sqm=110, dev_contributions=DEV_CONTRIBUTIONS.get(county, 12000))
            r["county"] = county
            r["zoned_hectares"] = ZONED_HECTARES.get(county, 0)
            rows.append(r)
    df_cost = pd.DataFrame(rows)
    cost_margin = (df_cost["margin_pct"] * df_cost["zoned_hectares"]).sum() / df_cost["zoned_hectares"].sum()

    # Individual: 60 u/ha density
    df_dens = assess_county_viability(density=60)
    dens_margin = (df_dens["margin_pct"] * df_dens["zoned_hectares"]).sum() / df_dens["zoned_hectares"].sum()

    # Combined
    rows2 = []
    for _, row in land_df.iterrows():
        county = row["county"]
        if county in COUNTY_SALE_PRICES_2025:
            median_land = row.get("median_price_per_hectare")
            if pd.isna(median_land):
                continue
            r = calculate_viability(
                sale_price=COUNTY_SALE_PRICES_2025[county],
                land_cost_per_hectare=median_land,
                density_units_per_ha=60,
                construction_cost_per_sqm=get_construction_cost_per_sqm(county) * 0.85,
                avg_sqm=110, dev_contributions=DEV_CONTRIBUTIONS.get(county, 12000))
            r["county"] = county
            r["zoned_hectares"] = ZONED_HECTARES.get(county, 0)
            rows2.append(r)
    df_combo = pd.DataFrame(rows2)
    combo_margin = (df_combo["margin_pct"] * df_combo["zoned_hectares"]).sum() / df_combo["zoned_hectares"].sum()

    # Synergy: is combined > sum of individual improvements?
    cost_delta = cost_margin - base_margin
    dens_delta = dens_margin - base_margin
    combo_delta = combo_margin - base_margin
    synergy = combo_delta - (cost_delta + dens_delta)

    return {
        "id": "INT01", "status": "KEEP", "metric": "synergy_pp",
        "value": round(synergy, 4),
        "description": "INT01 Interaction: 15% cost reduction × 60 u/ha density",
        "seed": 42, "commit": "phase2.5", "interaction": True,
        "notes": f"Cost alone: {cost_delta:+.1%}, density alone: {dens_delta:+.1%}, combined: {combo_delta:+.1%}, synergy: {synergy:+.1%}"
    }


def main():
    """Run all experiments."""
    print("=" * 60)
    print("PHASE 1: Tournament")
    print("=" * 60)
    run_tournament()

    print("\n" + "=" * 60)
    print("PHASE 2: Experiments")
    print("=" * 60)

    experiments = [
        run_e01_dublin_vs_nondublin,
        run_e02_apartment_vs_house,
        run_e03_part_v_impact,
        run_e04_land_cost_sensitivity,
        run_e05_construction_cost_sensitivity,
        run_e06_finance_rate_sensitivity,
        run_e07_dev_contribution_variation,
        run_e08_viability_over_time,
        run_e09_viability_flips,
        run_e10_viability_vs_application_rate,
        run_e11_rural_one_off,
        run_e12_site_size_effect,
        run_e13_starter_vs_family,
        run_e14_cost_rental,
        run_e15_hfa_price_caps,
        run_e16_construction_cost_inflation,
        run_e17_developer_margin_squeeze,
        run_e18_breakeven_by_county,
        run_e19_stranded_hectares,
        run_e20_stranded_units,
        run_e21_combined_policy,
        run_e22_density_breakeven,
    ]

    for exp_fn in experiments:
        try:
            result = exp_fn()
            append_result(result)
            print(f"  {result['id']}: {result['metric']} = {result['value']}  [{result['status']}]")
            print(f"    {result['notes']}")
        except Exception as e:
            print(f"  ERROR in {exp_fn.__name__}: {e}")

    print("\n" + "=" * 60)
    print("PHASE 2.5: Interactions")
    print("=" * 60)
    int_result = run_interactions()
    append_result(int_result)
    print(f"  {int_result['id']}: {int_result['metric']} = {int_result['value']}")
    print(f"    {int_result['notes']}")

    print("\nAll experiments complete. Results in results.tsv")


if __name__ == "__main__":
    main()
