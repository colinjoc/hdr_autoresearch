"""Irish local authority planning permission deliveries, 2012-2025.

Which councils are permitting the most housing per capita, and how has the
distribution moved through the Irish housing crisis?
"""
from pathlib import Path
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).parent
RAW = HERE / "data" / "raw"
CHARTS = HERE / "charts"; CHARTS.mkdir(exist_ok=True)
DISCOVERIES = HERE / "discoveries"; DISCOVERIES.mkdir(exist_ok=True)
RESULTS = HERE / "results.tsv"


def load_jsonstat(path, measure_filter=None):
    d = json.load(open(path))
    dims = d["id"]
    size = d["size"]
    values = d["value"]
    indices = {k: d["dimension"][k]["category"]["index"] for k in dims}
    labels = {k: d["dimension"][k]["category"]["label"] for k in dims}

    def iter_ix(s):
        if not s: yield []; return
        for i in range(s[0]):
            for rest in iter_ix(s[1:]):
                yield [i] + rest

    rows = []
    for flat, ix in enumerate(iter_ix(size)):
        v = values[flat] if flat < len(values) else None
        if v is None: continue
        row = {dims[j]: labels[dims[j]][indices[dims[j]][pos]] for j, pos in enumerate(ix)}
        row["value"] = v
        rows.append(row)
    return pd.DataFrame(rows)


def main():
    planning = load_jsonstat(RAW / "bhq01.json")
    # Rename only the actual dimension columns
    planning = planning.rename(columns={
        "TLIST(Q1)": "quarter",
        "C01912V02351": "housing_type",
        "C01947V02657": "la",
    })
    # Standardise: use "statistic_name" from STATISTIC dimension
    if "STATISTIC" in planning.columns:
        planning = planning.rename(columns={"STATISTIC": "statistic"})
    print(f"[planning] {len(planning)} rows; columns: {list(planning.columns)}")
    # Filter to "Units for which Permissions Granted" - actual housing units
    units = planning[planning["statistic"] == "Units for which Permissions Granted"].copy()
    # Parse quarter
    def parse_q(s):
        if isinstance(s, str) and len(s) == 6:
            return pd.Timestamp(year=int(s[:4]), month=(int(s[5])-1)*3 + 1, day=1)
        return pd.NaT
    units["date"] = units["quarter"].apply(lambda q: None)
    # quarters arrive as '2024Q1' string — reformat
    units["year"] = units["quarter"].str[:4].astype(int)
    units["q"] = units["quarter"].str[-2:]
    units["value"] = pd.to_numeric(units["value"], errors="coerce")

    # Annual aggregate by LA × housing type
    annual = units.groupby(["year", "la", "housing_type"])["value"].sum().reset_index()
    all_totals = annual[annual["housing_type"] == "Houses"]  # "Houses" is the aggregate
    latest_year = annual["year"].max()

    # Housing volume by LA, 2024 (or latest full year)
    latest = annual[(annual["year"] == latest_year) & (annual["la"] != "All Local Authorities")]
    by_la_latest = latest.groupby("la")["value"].sum().reset_index().sort_values("value", ascending=False)
    by_la_latest.to_csv(DISCOVERIES / f"la_housing_{latest_year}.csv", index=False)
    print(f"\n=== Top 10 LAs by {latest_year} housing units permitted ===")
    print(by_la_latest.head(10).to_string(index=False))
    print(f"\n=== Bottom 10 LAs by {latest_year} housing units permitted ===")
    print(by_la_latest.tail(10).to_string(index=False))

    # Time series for top 8 LAs
    top8 = by_la_latest.head(8)["la"].tolist()
    fig, ax = plt.subplots(figsize=(12, 6))
    by_la_year = annual[annual["la"].isin(top8)].groupby(["la", "year"])["value"].sum().reset_index()
    for la in top8:
        sub = by_la_year[by_la_year["la"] == la].sort_values("year")
        ax.plot(sub["year"], sub["value"], "o-", label=la[:22], linewidth=1)
    ax.set_xlabel("year"); ax.set_ylabel("housing units permitted (annual)")
    ax.set_title(f"Top 8 Irish local authorities — housing units permitted annually 2012-{latest_year}")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(CHARTS / "top8_la_housing_trend.png", dpi=120); plt.close(fig)

    # National total trend
    nat = annual[annual["la"] == "All Local Authorities"].groupby("year")["value"].sum().reset_index()
    print(f"\n=== National total trend ===")
    print(nat.to_string(index=False))

    HEADER = ["experiment_id", "commit", "description", "metric", "value", "seed", "status", "notes"]
    rows = [
        {"experiment_id": "E00", "commit": "phase0.5",
         "description": f"Irish LA planning permissions BHQ01 {annual['year'].min()}-{annual['year'].max()}",
         "metric": f"top_LA_{latest_year}_units", "value": f"{by_la_latest.iloc[0]['la']} ({by_la_latest.iloc[0]['value']:.0f})",
         "seed": 0, "status": "BASELINE",
         "notes": f"{annual['la'].nunique()} local authorities"},
    ]
    with RESULTS.open("w") as f:
        f.write("\t".join(HEADER) + "\n")
        for r in rows:
            f.write("\t".join(str(r[c]) for c in HEADER) + "\n")


if __name__ == "__main__":
    main()
