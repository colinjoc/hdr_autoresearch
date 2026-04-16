"""Irish housing permission-to-completion pipeline 2019-2025.

CSO BHQ15 has SHD vs non-SHD permission grants 2019 Q1 - 2025 Q3.
CSO NDA05 / NDA12 have completions 2012-2025.

Questions:
  Q1: How many permissions granted 2019-2024? How many completed 2021-2025 (2-yr lag)?
  Q2: SHD (2017-2022 fast-track) vs Non-SHD — did SHD permissions convert to completions
      at different rates?
  Q3: Which years show a pipeline break?
"""
from pathlib import Path
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).parent
RAW = HERE / "data" / "raw"
CHARTS = HERE / "charts"; CHARTS.mkdir(exist_ok=True)
DISCOVERIES = HERE / "discoveries"; DISCOVERIES.mkdir(exist_ok=True)
RESULTS = HERE / "results.tsv"


def load_jsonstat(path):
    d = json.load(open(path))
    dims = d["id"]; size = d["size"]; values = d["value"]
    indices = {k: d["dimension"][k]["category"]["index"] for k in dims}
    labels = {k: d["dimension"][k]["category"]["label"] for k in dims}
    def iter_ix(s):
        if not s: yield []; return
        for i in range(s[0]):
            for r in iter_ix(s[1:]): yield [i] + r
    rows = []
    for flat, ix in enumerate(iter_ix(size)):
        v = values[flat] if flat < len(values) else None
        if v is None: continue
        row = {dims[j]: labels[dims[j]][indices[dims[j]][p]] for j, p in enumerate(ix)}
        row["value"] = v
        rows.append(row)
    return pd.DataFrame(rows)


def main():
    # PERMISSIONS — BHQ15
    bhq = load_jsonstat(RAW / "BHQ15.json")
    bhq.columns = ["statistic", "quarter", "shd_type", "value"]
    bhq["year"] = bhq["quarter"].str[:4].astype(int)
    bhq["value"] = pd.to_numeric(bhq["value"], errors="coerce").fillna(0)

    # Annual totals: sum ALL house units + apartment units
    # Filter to per-type counts (avoid double counting "All house units" which already includes multi-dev)
    perm_ann = bhq[bhq["statistic"].isin(["Apartment units", "All house units"])].groupby(
        ["year", "shd_type"])["value"].sum().reset_index()
    perm_ann_total = bhq[bhq["statistic"].isin(["Apartment units", "All house units"])].groupby(
        "year")["value"].sum().reset_index(name="permissions")
    # SHD share
    perm_shd = bhq[(bhq["statistic"].isin(["Apartment units", "All house units"])) &
                   (bhq["shd_type"] == "Strategic housing development units")].groupby(
        "year")["value"].sum().reset_index(name="shd_permissions")
    perm_nshd = bhq[(bhq["statistic"].isin(["Apartment units", "All house units"])) &
                    (bhq["shd_type"] == "Non strategic housing development units")].groupby(
        "year")["value"].sum().reset_index(name="nshd_permissions")

    # COMPLETIONS — NDA12 "All house types"
    nda = load_jsonstat(RAW / "NDA12.json")
    nda.columns = ["statistic", "year", "area", "type", "value"]
    nda["year"] = nda["year"].astype(int)
    nda["value"] = pd.to_numeric(nda["value"], errors="coerce").fillna(0)
    # No "All areas" aggregate in NDA12; sum across all 867 towns for national total.
    # Use "All house types" to avoid triple-counting house types.
    comp_ann = nda[nda["type"] == "All house types"].groupby(
        "year")["value"].sum().reset_index(name="completions")

    # Merge
    pipeline = perm_ann_total.merge(perm_shd, on="year", how="left").merge(
        perm_nshd, on="year", how="left").merge(comp_ann, on="year", how="outer").fillna(0)
    pipeline = pipeline.sort_values("year").reset_index(drop=True)
    print("=== Irish housing pipeline 2012-2025 ===")
    print(pipeline.to_string(index=False))
    pipeline.to_csv(DISCOVERIES / "pipeline_annual.csv", index=False)

    # 2-year-lag pipeline ratio
    pipeline["completions_lag2"] = pipeline["completions"].shift(-2)
    pipeline["conversion_2yr"] = pipeline["completions_lag2"] / pipeline["permissions"].replace(0, float("nan"))
    print("\n=== 2-year conversion: permissions in year T → completions in T+2 ===")
    print(pipeline[["year", "permissions", "completions_lag2", "conversion_2yr"]].dropna().to_string(index=False))

    # SHD peak years 2019-2021 (SHD scheme ran Dec 2017 - Dec 2021)
    shd_years = pipeline[pipeline["year"].between(2019, 2021)]
    total_shd_perm = int(shd_years["shd_permissions"].sum())
    total_nshd_perm = int(shd_years["nshd_permissions"].sum())
    print(f"\n=== SHD scheme window 2019-2021 ===")
    print(f"SHD permissions total 2019-2021: {total_shd_perm:,}")
    print(f"Non-SHD permissions total 2019-2021: {total_nshd_perm:,}")
    # Completions 2021-2023 as the roughly 2-yr-lagged return
    comp_shd_window = pipeline[pipeline["year"].between(2021, 2023)]["completions"].sum()
    print(f"Completions 2021-2023 (2-yr lag from SHD era): {int(comp_shd_window):,}")

    # Chart
    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.bar(pipeline["year"] - 0.2, pipeline["permissions"], width=0.4, label="permissions granted", color="steelblue")
    ax.bar(pipeline["year"] + 0.2, pipeline["completions"], width=0.4, label="completions", color="darkorange")
    ax.axvspan(2017, 2022, alpha=0.08, color="red", label="SHD scheme window")
    ax.set_xlabel("year"); ax.set_ylabel("housing units")
    ax.set_title("Irish housing pipeline: permissions granted vs completions 2012-2025")
    ax.legend(); ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(CHARTS / "pipeline.png", dpi=120); plt.close(fig)

    # === Phase 2.75 reviewer R1-R4 follow-ups ===
    # R1: aggregate vs cohort ratio is noted as caveat in paper (no re-computation needed).
    # R2: pre-2019 context from BHQ16 (Planning permissions granted, scheme + unit counts,
    #     back to 1975). Lets us place the 2019-2025 plateau against a longer baseline.
    bhq16_path = RAW / "BHQ16.json"
    pre_2019_units = {}
    pre_2019_conv = {}
    if bhq16_path.exists():
        bhq16 = load_jsonstat(bhq16_path)
        bhq16.columns = ["statistic", "quarter", "region", "type", "value"]
        bhq16["year"] = bhq16["quarter"].str[:4].astype(int)
        bhq16["value"] = pd.to_numeric(bhq16["value"], errors="coerce").fillna(0)
        sel = bhq16[(bhq16["region"] == "Ireland") &
                    (bhq16["statistic"] == "Units for which Permission Granted") &
                    (bhq16["type"].isin(["All houses", "Apartments"]))]
        pre = sel.groupby("year")["value"].sum().reset_index(name="units_permitted")
        for y in (2016, 2017, 2018):
            row = pre[pre["year"] == y]
            if not row.empty:
                pre_2019_units[y] = int(row["units_permitted"].iloc[0])
                comp_row = pipeline[pipeline["year"] == y + 2]
                if not comp_row.empty and pre_2019_units[y] > 0:
                    pre_2019_conv[y] = comp_row["completions"].iloc[0] / pre_2019_units[y]
        print("\n=== Pre-2019 context (BHQ16, R2 follow-up) ===")
        for y, u in pre_2019_units.items():
            print(f"{y} permissions {u:,} → completions {y+2} "
                  f"{int(pipeline.loc[pipeline.year==y+2,'completions'].iloc[0]):,} = "
                  f"{pre_2019_conv.get(y, float('nan')):.1%}")

    # R3: scheme-count normalisation attempt (BHQ15 has only unit counts by SHD/non-SHD,
    #     not scheme counts, so the per-scheme comparison is NOT computable from available
    #     data). We therefore soften the SHD-vs-non-SHD claim in the paper rather than
    #     normalise. Record as a known methodology gap.

    # Lag sensitivity (recommended in §3 of review) — 1yr, 2yr, 3yr conversion ratios
    lag_tbl = pipeline[["year", "permissions", "completions"]].copy()
    for lag in (1, 2, 3):
        lag_tbl[f"conv_{lag}yr"] = pipeline["completions"].shift(-lag) / pipeline["permissions"].replace(0, float("nan"))
    lag_view = lag_tbl[lag_tbl["permissions"] > 0][["year", "permissions", "conv_1yr", "conv_2yr", "conv_3yr"]]
    print("\n=== Lag sensitivity (1/2/3-yr T+k completions ÷ T permissions) ===")
    print(lag_view.to_string(index=False, float_format=lambda v: f"{v:.2f}"))
    lag_view.to_csv(DISCOVERIES / "lag_sensitivity.csv", index=False)

    HEADER = ["experiment_id", "commit", "description", "metric", "value", "seed", "status", "notes"]
    rows = [
        {"experiment_id": "E00", "commit": "phase0.5",
         "description": "Irish housing permissions + completions pipeline 2012-2025",
         "metric": "perm_2023_vs_comp_2025",
         "value": f"{int(pipeline[pipeline['year']==2023]['permissions'].iloc[0])}→{int(pipeline[pipeline['year']==2025]['completions'].iloc[0])}",
         "seed": 0, "status": "BASELINE",
         "notes": f"SHD 2019-2021 permissions {total_shd_perm:,}; Non-SHD {total_nshd_perm:,}"},
        {"experiment_id": "E01-R1", "commit": "phase2.75",
         "description": "R1 caveat: 2-yr conversion is aggregate T+2 ratio, not cohort-tracked",
         "metric": "conv_2yr_2019",
         "value": f"{pipeline.loc[pipeline.year==2019,'conversion_2yr'].iloc[0]:.2f}",
         "seed": 0, "status": "CAVEAT",
         "notes": "Aggregate numerator/denominator mismatch; pre-2019 permissions feeding 2020-2021 completions not observed in BHQ15"},
        {"experiment_id": "E02-R2", "commit": "phase2.75",
         "description": "R2 pre-2019 context from BHQ16: 2016-2018 permissions and T+2 conversion",
         "metric": "conv_2yr_pre2019",
         "value": ",".join(f"{y}:{pre_2019_conv.get(y, float('nan')):.2f}" for y in sorted(pre_2019_conv)) if pre_2019_conv else "unavailable",
         "seed": 0, "status": "CAVEAT",
         "notes": f"2016 perms {pre_2019_units.get(2016, 'na'):,}, 2017 {pre_2019_units.get(2017, 'na'):,}, 2018 {pre_2019_units.get(2018, 'na'):,}; 2019-2025 plateau is ABOVE pre-2019 but 41%→65% rise is recovery from 2019-20 COVID trough, not above pre-COVID 77-86%"},
        {"experiment_id": "E03-R3", "commit": "phase2.75",
         "description": "R3 SHD vs non-SHD: scheme-count normalisation not possible from BHQ15",
         "metric": "shd_nshd_units_2019_2021",
         "value": f"{total_shd_perm}/{total_nshd_perm}",
         "seed": 0, "status": "CAVEAT",
         "notes": "BHQ15 lacks scheme counts split by SHD/non-SHD; per-scheme productivity not computable; paper softened to descriptive note"},
        {"experiment_id": "E04-R4", "commit": "phase2.75",
         "description": "R4 commencement-notice middle stage is NOT in pipeline (CSO NHC01 unavailable via PxStat)",
         "metric": "has_commencement_stage",
         "value": "False",
         "seed": 0, "status": "CAVEAT",
         "notes": "Paper retitled from 'pipeline' to 'permission vs completion comparison'; commencement notices are DoH not CSO, not ingested"},
        {"experiment_id": "E05-LAG", "commit": "phase2.75",
         "description": "Lag sensitivity 1/2/3-yr conversion ratios",
         "metric": "conv_1_2_3yr_2019",
         "value": f"{lag_tbl.loc[lag_tbl.year==2019,'conv_1yr'].iloc[0]:.2f}/{lag_tbl.loc[lag_tbl.year==2019,'conv_2yr'].iloc[0]:.2f}/{lag_tbl.loc[lag_tbl.year==2019,'conv_3yr'].iloc[0]:.2f}",
         "seed": 0, "status": "ROBUSTNESS",
         "notes": "2022 is the best year at every lag (71%/65%/74%); 2019-20 are the trough at every lag; ordering of years is robust to lag choice"},
    ]
    with RESULTS.open("w") as f:
        f.write("\t".join(HEADER) + "\n")
        for r in rows:
            f.write("\t".join(str(r[c]) for c in HEADER) + "\n")


if __name__ == "__main__":
    main()
