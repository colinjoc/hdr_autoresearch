"""
Phase B Discovery: Construction cost driver ranking and regulatory cost burden.

Outputs:
  discoveries/cost_driver_ranking.csv — each cost component ranked by contribution
  discoveries/regulatory_cost_burden.csv — estimated cost additions from NZEB/BCAR/Part L
"""
import numpy as np
import pandas as pd
from pathlib import Path
from parse_data import parse_wpm28, parse_ehq03

PROJECT = Path(__file__).parent
DISCOVERIES = PROJECT / "discoveries"
DISCOVERIES.mkdir(exist_ok=True)


def compute_cost_driver_ranking():
    """
    Rank each cost component by its contribution to total cost growth 2015-2024.
    Contribution = share_of_hard_cost x CAGR
    """
    wpm = parse_wpm28()
    ehq = parse_ehq03()

    def get_cagr(mc):
        sub = wpm[wpm["material_code"] == mc][["date", "index_value"]].set_index("date")["index_value"].sort_index().dropna()
        if len(sub) < 2:
            return np.nan
        years = (sub.index[-1] - sub.index[0]).days / 365.25
        return ((sub.iloc[-1] / sub.iloc[0]) ** (1 / years) - 1) * 100

    mat_lookup = wpm.drop_duplicates("material_code").set_index("material_code")["material_label"].to_dict()

    # Trade-level mapping: trade -> (share_of_hard_cost, [(material_code, weight_in_trade)])
    trades = {
        "Substructure": {
            "share": 0.08,
            "materials": [("621", 0.6), ("611", 0.3), ("652", 0.1)],
        },
        "Frame & Upper Floors": {
            "share": 0.12,
            "materials": [("65", 0.4), ("621", 0.3), ("64", 0.3)],
        },
        "Roof": {
            "share": 0.07,
            "materials": [("661", 0.4), ("65", 0.3), ("702", 0.3)],
        },
        "External Walls & Cladding": {
            "share": 0.10,
            "materials": [("631", 0.4), ("702", 0.4), ("704", 0.2)],
        },
        "Windows & External Doors": {
            "share": 0.06,
            "materials": [("706", 0.5), ("67162", 0.3), ("708", 0.2)],
        },
        "Internal Walls & Partitions": {
            "share": 0.04,
            "materials": [("631", 0.5), ("704", 0.3), ("705", 0.2)],
        },
        "Internal Finishes": {
            "share": 0.08,
            "materials": [("704", 0.4), ("705", 0.3), ("706", 0.3)],
        },
        "Fittings & Fixtures": {
            "share": 0.05,
            "materials": [("67162", 0.4), ("708", 0.3), ("709", 0.3)],
        },
        "Mechanical Services": {
            "share": 0.14,
            "materials": [("701", 0.5), ("700", 0.3), ("703", 0.2)],
        },
        "Electrical Services": {
            "share": 0.10,
            "materials": [("691", 0.6), ("69162", 0.2), ("69163", 0.2)],
        },
        "Stairs": {
            "share": 0.02,
            "materials": [("661", 0.5), ("65", 0.3), ("708", 0.2)],
        },
        "Preliminaries & Site Overhead": {
            "share": 0.10,
            "materials": [],  # labour-dominated, not material-driven
        },
        "External & Site Works": {
            "share": 0.04,
            "materials": [("681", 0.4), ("60161", 0.3), ("703", 0.3)],
        },
    }

    # Also include labour as a separate component
    ehq_2015 = ehq[ehq["year"] >= 2015].copy()
    labour_cagr = np.nan
    if "EHQ03C08" in ehq_2015.columns:
        lc = ehq_2015[["date", "EHQ03C08"]].dropna()
        if len(lc) >= 2:
            years = (lc["date"].iloc[-1] - lc["date"].iloc[0]).days / 365.25
            labour_cagr = ((lc["EHQ03C08"].iloc[-1] / lc["EHQ03C08"].iloc[0]) ** (1 / years) - 1) * 100

    rows = []

    # Material components via trades
    for trade_name, trade_info in trades.items():
        share = trade_info["share"]
        materials = trade_info["materials"]

        if len(materials) == 0:
            # Labour-dominated trade
            weighted_cagr = labour_cagr if not np.isnan(labour_cagr) else 3.0
            driver_type = "labour"
        else:
            weighted_cagr = 0
            for mc, w in materials:
                mc_cagr = get_cagr(mc)
                if not np.isnan(mc_cagr):
                    weighted_cagr += w * mc_cagr
            driver_type = "materials"

        contribution = share * weighted_cagr
        rows.append({
            "component": trade_name,
            "share_of_hard_cost_pct": share * 100,
            "weighted_cagr_pct_yr": round(weighted_cagr, 2),
            "contribution_pp": round(contribution, 4),
            "driver_type": driver_type,
            "primary_materials": ", ".join([mat_lookup.get(mc, mc) for mc, _ in materials]) if materials else "labour",
        })

    # Add overall labour component
    rows.append({
        "component": "Labour (all trades, ~50% of hard cost)",
        "share_of_hard_cost_pct": 50.0,
        "weighted_cagr_pct_yr": round(labour_cagr, 2) if not np.isnan(labour_cagr) else "N/A",
        "contribution_pp": round(0.50 * labour_cagr, 4) if not np.isnan(labour_cagr) else "N/A",
        "driver_type": "labour",
        "primary_materials": "construction workforce",
    })

    # Add overall materials component
    all_mat_cagr = get_cagr("-")
    rows.append({
        "component": "Materials (all, ~50% of hard cost)",
        "share_of_hard_cost_pct": 50.0,
        "weighted_cagr_pct_yr": round(all_mat_cagr, 2),
        "contribution_pp": round(0.50 * all_mat_cagr, 4),
        "driver_type": "materials",
        "primary_materials": "WPM28 All-Materials index",
    })

    df = pd.DataFrame(rows)
    # Sort by absolute contribution (excluding the aggregate rows)
    trade_rows = df[~df["component"].str.contains("all trades|all,")].copy()
    trade_rows["abs_contribution"] = trade_rows["contribution_pp"].astype(float).abs()
    trade_rows = trade_rows.sort_values("abs_contribution", ascending=False)

    # Combine
    agg_rows = df[df["component"].str.contains("all trades|all,")]
    result = pd.concat([trade_rows.drop(columns=["abs_contribution"]), agg_rows], ignore_index=True)

    result.to_csv(DISCOVERIES / "cost_driver_ranking.csv", index=False)
    print(f"Saved cost_driver_ranking.csv ({len(result)} rows)")
    print("\nTop-5 trade-level cost drivers:")
    for _, r in trade_rows.head(5).iterrows():
        print(f"  {r['component']}: share={r['share_of_hard_cost_pct']:.0f}%, CAGR={r['weighted_cagr_pct_yr']}%, contribution={r['contribution_pp']}pp")

    return result


def compute_regulatory_cost_burden():
    """
    Estimate cost additions from NZEB, BCAR, and Part L changes.
    Compare pre/post NZEB inflation rates for affected materials.
    """
    wpm = parse_wpm28()
    nzeb_date = pd.Timestamp("2019-11-01")

    regulatory_materials = {
        "702": ("Insulation", "NZEB Part L 2019 — enhanced insulation requirements"),
        "706": ("Glass", "NZEB Part L 2019 — triple glazing requirement"),
        "701": ("HVAC", "NZEB Part L 2019 — heat pump mandate, enhanced ventilation"),
        "691": ("Electrical Fittings", "NZEB — heat pump controls, solar PV wiring, smart metering"),
        "69162": ("Lighting", "Part L — LED requirements, emergency lighting"),
        "69163": ("Protection & Communication", "BCAR — fire detection, alarm systems"),
        "700": ("Plumbing", "NZEB — heat pump plumbing, enhanced water conservation"),
    }

    rows = []
    for mc, (name, regulation) in regulatory_materials.items():
        sub = wpm[wpm["material_code"] == mc][["date", "index_value"]].set_index("date")["index_value"].sort_index().dropna()
        pre = sub[sub.index < nzeb_date]
        post = sub[sub.index >= nzeb_date]

        if len(pre) >= 6 and len(post) >= 6:
            pre_trend = (pre.iloc[-1] / pre.iloc[0] - 1) / (len(pre) / 12) * 100
            post_trend = (post.iloc[-1] / post.iloc[0] - 1) / (len(post) / 12) * 100
            excess = post_trend - pre_trend

            # Estimate EUR/sqm impact
            # Semi-detached ~EUR 1975/sqm hard cost
            # Material share depends on trade
            material_share_map = {
                "702": 0.04,  # insulation ~4% of hard cost
                "706": 0.03,  # glass ~3%
                "701": 0.07,  # HVAC ~7%
                "691": 0.06,  # electrical ~6%
                "69162": 0.02,  # lighting ~2%
                "69163": 0.02,  # protection ~2%
                "700": 0.04,  # plumbing ~4%
            }
            base_cost = 1975  # EUR/sqm semi-detached
            mat_share = material_share_map.get(mc, 0.03)
            excess_cost_per_sqm = base_cost * mat_share * (excess / 100)

            rows.append({
                "material": name,
                "material_code": mc,
                "regulation": regulation,
                "pre_nzeb_inflation_pct_yr": round(pre_trend, 2),
                "post_nzeb_inflation_pct_yr": round(post_trend, 2),
                "excess_inflation_pp_yr": round(excess, 2),
                "est_share_of_hard_cost_pct": mat_share * 100,
                "est_excess_cost_eur_sqm_yr": round(excess_cost_per_sqm, 2),
                "confounding_note": "COVID/Ukraine overlap with post-NZEB period"
            })

    df = pd.DataFrame(rows).sort_values("excess_inflation_pp_yr", ascending=False)
    df.to_csv(DISCOVERIES / "regulatory_cost_burden.csv", index=False)
    print(f"\nSaved regulatory_cost_burden.csv ({len(df)} rows)")
    print("\nRegulatory cost burden (excess inflation post-NZEB):")
    for _, r in df.iterrows():
        print(f"  {r['material']}: excess={r['excess_inflation_pp_yr']:+.2f}pp/yr, est. EUR {r['est_excess_cost_eur_sqm_yr']:.2f}/sqm/yr")

    total_excess = df["est_excess_cost_eur_sqm_yr"].sum()
    print(f"\n  Total estimated excess: EUR {total_excess:.2f}/sqm/yr across all regulatory-affected materials")

    return df


if __name__ == "__main__":
    print("=" * 60)
    print("PHASE B: DISCOVERY")
    print("=" * 60)

    print("\n--- Cost Driver Ranking ---")
    drivers = compute_cost_driver_ranking()

    print("\n--- Regulatory Cost Burden ---")
    regulatory = compute_regulatory_cost_burden()

    print("\n" + "=" * 60)
    print("PHASE B COMPLETE")
    print("=" * 60)
