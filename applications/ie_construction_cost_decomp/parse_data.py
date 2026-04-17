"""
Parse CSO JSON-stat 2.0 files (WPM28, EHQ03, BEA04) into pandas DataFrames.
TDD: tests/test_parse_data.py written first.
"""
import json
import numpy as np
import pandas as pd
from pathlib import Path

RAW = Path(__file__).parent / "data" / "raw"


def parse_jsonstat(path: Path) -> dict:
    """Load a JSON-stat 2.0 file and return its raw dict."""
    with open(path) as f:
        return json.load(f)


def parse_wpm28(path: Path = RAW / "WPM28.json") -> pd.DataFrame:
    """
    Parse WPM28 into a tidy DataFrame:
      columns: date, material_code, material_label, index_value, mom_pct, yoy_pct
    Shape should be 40 materials x 117 months = 4680 rows.
    """
    d = parse_jsonstat(path)

    stat_dim = d["dimension"]["STATISTIC"]["category"]
    time_dim = d["dimension"]["TLIST(M1)"]["category"]
    mat_dim = d["dimension"]["C01409V03262"]["category"]

    stat_codes = stat_dim["index"]  # 3 statistics
    time_codes = time_dim["index"]  # 117 months
    mat_codes = mat_dim["index"]    # 40 materials

    stat_labels = stat_dim["label"]
    time_labels = time_dim["label"]
    mat_labels = mat_dim["label"]

    values = d["value"]
    sizes = d["size"]  # [3, 117, 40]

    rows = []
    for si, sc in enumerate(stat_codes):
        for ti, tc in enumerate(time_codes):
            for mi, mc in enumerate(mat_codes):
                idx = si * sizes[1] * sizes[2] + ti * sizes[2] + mi
                val = values[idx]
                rows.append({
                    "statistic": sc,
                    "date_code": tc,
                    "material_code": mc,
                    "material_label": mat_labels[mc],
                    "value": val
                })

    df_long = pd.DataFrame(rows)

    # Parse date
    df_long["date"] = pd.to_datetime(df_long["date_code"], format="%Y%m")

    # Pivot statistics into columns
    df_index = df_long[df_long["statistic"] == "WPM28C01"][["date", "material_code", "material_label", "value"]].rename(columns={"value": "index_value"})
    df_mom = df_long[df_long["statistic"] == "WPM28C02"][["date", "material_code", "value"]].rename(columns={"value": "mom_pct"})
    df_yoy = df_long[df_long["statistic"] == "WPM28C03"][["date", "material_code", "value"]].rename(columns={"value": "yoy_pct"})

    df = df_index.merge(df_mom, on=["date", "material_code"], how="left")
    df = df.merge(df_yoy, on=["date", "material_code"], how="left")

    return df.sort_values(["material_code", "date"]).reset_index(drop=True)


def parse_ehq03(path: Path = RAW / "EHQ03.json") -> pd.DataFrame:
    """
    Parse EHQ03, filtering to construction sector (NACE F) and all employees.
    Returns quarterly data with columns for each statistic.
    """
    d = parse_jsonstat(path)

    stat_dim = d["dimension"]["STATISTIC"]["category"]
    time_dim = d["dimension"]["TLIST(Q1)"]["category"]
    sector_dim = d["dimension"]["C02665V03225"]["category"]
    occ_dim = d["dimension"]["C02397V02888"]["category"]

    stat_codes = stat_dim["index"]
    time_codes = time_dim["index"]
    sector_codes = sector_dim["index"]
    occ_codes = occ_dim["index"]

    sizes = d["size"]  # [21, 72, 21, 4]
    values = d["value"]

    # Find indices for construction (F) and all employees (-)
    sector_target = "F"
    occ_target = "-"
    si_sector = sector_codes.index(sector_target)
    si_occ = occ_codes.index(occ_target)

    rows = []
    for stat_i, stat_code in enumerate(stat_codes):
        stat_label = stat_dim["label"][stat_code]
        for time_i, time_code in enumerate(time_codes):
            idx = (stat_i * sizes[1] * sizes[2] * sizes[3] +
                   time_i * sizes[2] * sizes[3] +
                   si_sector * sizes[3] +
                   si_occ)
            val = values[idx]
            rows.append({
                "statistic": stat_code,
                "stat_label": stat_label,
                "quarter_code": time_code,
                "value": val
            })

    df = pd.DataFrame(rows)

    # Parse quarter: e.g. "20081" -> 2008-Q1
    df["year"] = df["quarter_code"].str[:4].astype(int)
    df["quarter"] = df["quarter_code"].str[4:].astype(int)
    df["date"] = pd.to_datetime(df["year"].astype(str) + "-" + (df["quarter"] * 3).astype(str) + "-01")

    # Pivot to wide
    df_wide = df.pivot_table(index=["date", "year", "quarter"], columns="statistic", values="value").reset_index()
    df_wide.columns.name = None

    return df_wide.sort_values("date").reset_index(drop=True)


def parse_bea04(path: Path = RAW / "BEA04.json") -> pd.DataFrame:
    """Parse BEA04 production index for building & construction."""
    d = parse_jsonstat(path)

    stat_dim = d["dimension"]["STATISTIC"]["category"]
    time_dim = d["dimension"]["TLIST(A1)"]["category"]
    sector_dim = d["dimension"]["C02402V02895"]["category"]

    stat_codes = stat_dim["index"]
    time_codes = time_dim["index"]
    sector_codes = sector_dim["index"]

    sizes = d["size"]  # [4, 25, 5]
    values = d["value"]

    rows = []
    for stat_i, sc in enumerate(stat_codes):
        for time_i, tc in enumerate(time_codes):
            for sec_i, sec_c in enumerate(sector_codes):
                idx = stat_i * sizes[1] * sizes[2] + time_i * sizes[2] + sec_i
                val = values[idx]
                rows.append({
                    "statistic": sc,
                    "stat_label": stat_dim["label"][sc],
                    "year": int(tc),
                    "sector_code": sec_c,
                    "sector_label": sector_dim["label"][sec_c],
                    "value": val
                })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    wpm = parse_wpm28()
    print(f"WPM28: {wpm.shape[0]} rows, {wpm['material_code'].nunique()} materials, {wpm['date'].nunique()} months")
    print(f"Date range: {wpm['date'].min()} to {wpm['date'].max()}")

    ehq = parse_ehq03()
    print(f"\nEHQ03 (Construction): {ehq.shape[0]} quarters")
    print(f"Date range: {ehq['date'].min()} to {ehq['date'].max()}")

    bea = parse_bea04()
    print(f"\nBEA04: {bea.shape[0]} rows")
