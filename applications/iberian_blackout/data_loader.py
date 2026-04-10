"""
Data loader for Iberian Blackout project.
Loads real data from REE REData API JSON files.
"""
import json
import os
import pandas as pd
import numpy as np
from typing import Optional


def _load_json(data_dir: str, filename: str) -> dict:
    """Load a JSON file from the data directory."""
    path = os.path.join(data_dir, filename)
    with open(path, "r") as f:
        return json.load(f)


def load_generation_daily(data_dir: str, month_tag: str) -> pd.DataFrame:
    """
    Load daily generation by technology from REE API JSON.

    Parameters
    ----------
    data_dir : str
        Path to the data directory
    month_tag : str
        Month identifier e.g. 'apr2025', 'mar2025'

    Returns
    -------
    pd.DataFrame
        Columns = technology names, index = dates, values = MWh
    """
    data = _load_json(data_dir, f"gen_structure_{month_tag}_daily.json")

    records = {}
    for item in data.get("included", []):
        tech_name = item["type"]
        values = item["attributes"]["values"]
        for v in values:
            dt = pd.Timestamp(v["datetime"])
            if dt not in records:
                records[dt] = {}
            records[dt][tech_name] = v["value"]

    df = pd.DataFrame.from_dict(records, orient="index")
    df.index = pd.DatetimeIndex(pd.to_datetime(list(df.index), utc=True))
    df = df.sort_index()
    # Values from REE are in MWh (daily totals)
    df = df.clip(lower=0)  # generation should be non-negative
    return df


def load_demand_hourly(data_dir: str, month_tag: str) -> pd.DataFrame:
    """
    Load hourly demand from REE API JSON.

    Parameters
    ----------
    data_dir : str
        Path to data directory
    month_tag : str
        Month identifier e.g. 'apr2025'

    Returns
    -------
    pd.DataFrame
        Columns include demand_MW, forecast_MW, programmed_MW
    """
    data = _load_json(data_dir, f"demand_{month_tag}_hourly.json")

    series_map = {}
    for item in data.get("included", []):
        series_name = item["type"]
        values = item["attributes"]["values"]
        ts = {}
        for v in values:
            dt = pd.Timestamp(v["datetime"])
            ts[dt] = v["value"]
        series_map[series_name] = ts

    df = pd.DataFrame(series_map)
    df.index = pd.DatetimeIndex(pd.to_datetime(list(df.index), utc=True))
    df = df.sort_index()

    # Rename columns to standardized names
    rename = {}
    for col in df.columns:
        lower = col.lower()
        if "demand" in lower or "real" in lower:
            rename[col] = "demand_MW"
        elif "forecast" in lower or "prevista" in lower:
            rename[col] = "forecast_MW"
        elif "programm" in lower or "program" in lower:
            rename[col] = "programmed_MW"
    if rename:
        df = df.rename(columns=rename)

    # If no 'demand_MW' found, use first numeric column
    if "demand_MW" not in df.columns and len(df.columns) > 0:
        df = df.rename(columns={df.columns[0]: "demand_MW"})

    return df


def load_exchange_daily(
    data_dir: str, country: str, month_suffix: str
) -> pd.DataFrame:
    """
    Load daily interconnector exchange data.

    Parameters
    ----------
    data_dir : str
    country : str
        'france', 'portugal', or 'morocco'
    month_suffix : str
        'apr', 'mar', etc.

    Returns
    -------
    pd.DataFrame with columns 'exports', 'imports', 'net_flow'
    """
    data = _load_json(data_dir, f"exchange_{country}_{month_suffix}.json")

    series_map = {}
    for item in data.get("included", []):
        series_name = item["type"].lower()
        values = item["attributes"]["values"]
        ts = {}
        for v in values:
            dt = pd.Timestamp(v["datetime"])
            ts[dt] = v["value"]
        series_map[series_name] = ts

    df = pd.DataFrame(series_map)
    df.index = pd.DatetimeIndex(pd.to_datetime(list(df.index), utc=True))
    df = df.sort_index()

    # Standardize column names
    rename = {}
    for col in df.columns:
        if "export" in col.lower():
            rename[col] = "exports"
        elif "import" in col.lower():
            rename[col] = "imports"
        elif "saldo" in col.lower() or "balance" in col.lower():
            rename[col] = "net_flow"
    df = df.rename(columns=rename)

    if "exports" in df.columns and "imports" in df.columns and "net_flow" not in df.columns:
        df["net_flow"] = df["exports"] + df["imports"]

    return df


def load_prices_hourly(data_dir: str, month_suffix: str) -> pd.DataFrame:
    """
    Load hourly electricity prices.

    Parameters
    ----------
    data_dir : str
    month_suffix : str
        'apr', 'mar', etc.

    Returns
    -------
    pd.DataFrame with price columns
    """
    data = _load_json(data_dir, f"price_spot_{month_suffix}.json")

    series_map = {}
    for item in data.get("included", []):
        series_name = item["type"]
        values = item["attributes"]["values"]
        ts = {}
        for v in values:
            dt = pd.Timestamp(v["datetime"])
            ts[dt] = v["value"]
        series_map[series_name] = ts

    df = pd.DataFrame(series_map)
    df.index = pd.DatetimeIndex(pd.to_datetime(list(df.index), utc=True))
    df = df.sort_index()

    # Rename to include 'price' or 'spot' for discoverability
    if len(df.columns) > 0:
        first_col = df.columns[0]
        if "price" not in first_col.lower() and "spot" not in first_col.lower():
            df = df.rename(columns={first_col: f"spot_price_EUR_{first_col}"})

    return df


def build_daily_feature_matrix(data_dir: str) -> pd.DataFrame:
    """
    Build a comprehensive daily feature matrix combining all data sources.

    Returns a DataFrame with one row per day, columns are features:
    - Generation by technology (MWh)
    - Total generation, total demand
    - Renewable fraction, solar fraction, wind fraction
    - Interconnector net flows
    - Price statistics
    - Day of week, month
    """
    frames = []

    # Load generation for all available months
    gen_months = []
    for tag in ["jan2025", "feb2025", "mar2025", "apr2025", "may2025"]:
        try:
            g = load_generation_daily(data_dir, tag)
            gen_months.append(g)
        except FileNotFoundError:
            pass

    if gen_months:
        gen = pd.concat(gen_months)
        gen = gen[~gen.index.duplicated(keep="first")]
        gen = gen.sort_index()

        # Compute derived features
        gen["total_generation_MWh"] = gen.sum(axis=1)

        # Identify renewable vs synchronous
        renewable_cols = [
            c
            for c in gen.columns
            if any(
                r in c.lower()
                for r in ["solar", "wind", "hydro", "renewable", "biomass"]
            )
            and "total" not in c.lower()
        ]
        sync_cols = [
            c
            for c in gen.columns
            if any(s in c.lower() for s in ["nuclear", "coal", "gas", "combined", "cogeneration", "fuel"])
            and "total" not in c.lower()
        ]

        gen["renewable_MWh"] = gen[renewable_cols].sum(axis=1) if renewable_cols else 0
        gen["sync_gen_MWh"] = gen[sync_cols].sum(axis=1) if sync_cols else 0
        gen["renewable_fraction"] = gen["renewable_MWh"] / gen["total_generation_MWh"].replace(0, np.nan)

        solar_cols = [c for c in gen.columns if "solar" in c.lower()]
        wind_cols = [c for c in gen.columns if "wind" in c.lower()]
        gen["solar_MWh"] = gen[solar_cols].sum(axis=1) if solar_cols else 0
        gen["wind_MWh"] = gen[wind_cols].sum(axis=1) if wind_cols else 0
        gen["solar_fraction"] = gen["solar_MWh"] / gen["total_generation_MWh"].replace(0, np.nan)
        gen["wind_fraction"] = gen["wind_MWh"] / gen["total_generation_MWh"].replace(0, np.nan)
        gen["sync_fraction"] = gen["sync_gen_MWh"] / gen["total_generation_MWh"].replace(0, np.nan)

        frames.append(gen)

    # Load demand and compute daily aggregates
    demand_dfs = []
    for tag in ["jan2025", "feb2025", "mar2025", "apr2025", "may2025"]:
        try:
            d = load_demand_hourly(data_dir, tag)
            demand_dfs.append(d)
        except FileNotFoundError:
            pass

    if demand_dfs:
        demand = pd.concat(demand_dfs)
        demand = demand[~demand.index.duplicated(keep="first")]
        demand = demand.sort_index()
        col = "demand_MW" if "demand_MW" in demand.columns else demand.columns[0]
        daily_demand = demand[col].resample("D").agg(["mean", "max", "min", "std"])
        daily_demand.columns = [f"demand_{s}_MW" for s in ["mean", "max", "min", "std"]]
        frames.append(daily_demand)

    # Load exchanges
    for country in ["france", "portugal", "morocco"]:
        ex_dfs = []
        for suffix in ["jan", "feb", "mar", "apr"]:
            try:
                ex = load_exchange_daily(data_dir, country, suffix)
                ex_dfs.append(ex)
            except FileNotFoundError:
                pass
        if ex_dfs:
            ex_all = pd.concat(ex_dfs)
            ex_all = ex_all[~ex_all.index.duplicated(keep="first")]
            ex_all = ex_all.sort_index()
            ex_all = ex_all.rename(
                columns={c: f"{country}_{c}" for c in ex_all.columns}
            )
            frames.append(ex_all)

    # Load prices
    price_dfs = []
    for suffix in ["jan", "feb", "mar", "apr"]:
        try:
            p = load_prices_hourly(data_dir, suffix)
            price_dfs.append(p)
        except FileNotFoundError:
            pass

    if price_dfs:
        prices = pd.concat(price_dfs)
        prices = prices[~prices.index.duplicated(keep="first")]
        prices = prices.sort_index()
        # Daily price statistics
        daily_price = prices.iloc[:, 0].resample("D").agg(["mean", "min", "max", "std"])
        daily_price.columns = [f"price_{s}" for s in ["mean", "min", "max", "std"]]
        frames.append(daily_price)

    # Combine all
    if not frames:
        raise ValueError("No data loaded")

    # Normalize all indices to date-only for joining
    for i, f in enumerate(frames):
        frames[i].index = f.index.normalize()

    result = frames[0]
    for f in frames[1:]:
        result = result.join(f, how="outer", rsuffix="_dup")

    # Remove duplicate columns
    dup_cols = [c for c in result.columns if c.endswith("_dup")]
    result = result.drop(columns=dup_cols)

    # Add temporal features
    result["day_of_week"] = result.index.dayofweek
    result["month"] = result.index.month
    result["is_weekend"] = result["day_of_week"].isin([5, 6]).astype(int)

    return result


def compute_grid_stress_indicators(features: pd.DataFrame) -> pd.DataFrame:
    """
    Compute grid stress indicators from the daily feature matrix.

    These indicators capture conditions that correlate with blackout risk:
    - High renewable fraction with low synchronous backup
    - Large export flows reducing domestic reserves
    - Low demand relative to generation (excess supply)
    - High solar fraction during midday
    - Low price (indicates oversupply / low inertia dispatch)

    Parameters
    ----------
    features : pd.DataFrame
        Output of build_daily_feature_matrix

    Returns
    -------
    pd.DataFrame
        Stress indicator columns
    """
    stress = pd.DataFrame(index=features.index)

    # Renewable penetration fraction
    if "renewable_fraction" in features.columns:
        stress["renewable_fraction"] = features["renewable_fraction"]

    if "solar_fraction" in features.columns:
        stress["solar_fraction"] = features["solar_fraction"]

    if "sync_fraction" in features.columns:
        stress["sync_fraction"] = features["sync_fraction"]

    # Excess generation ratio
    if "total_generation_MWh" in features.columns and "demand_mean_MW" in features.columns:
        # Convert demand_mean_MW * 24 to approximate daily MWh
        stress["excess_gen_ratio"] = (
            features["total_generation_MWh"]
            / (features["demand_mean_MW"] * 24).replace(0, np.nan)
        )

    # Net export intensity (how much power leaving the system)
    export_cols = [c for c in features.columns if "net_flow" in c]
    if export_cols:
        stress["total_net_export_MWh"] = features[export_cols].sum(axis=1)
        if "total_generation_MWh" in features.columns:
            stress["export_fraction"] = (
                stress["total_net_export_MWh"].abs()
                / features["total_generation_MWh"].replace(0, np.nan)
            )

    # Price-based stress (low/negative prices indicate oversupply)
    if "price_min" in features.columns:
        stress["price_floor_EUR"] = features["price_min"]
        stress["has_negative_price"] = (features["price_min"] < 0).astype(int)

    if "price_mean" in features.columns:
        stress["price_mean_EUR"] = features["price_mean"]

    # Demand variability (high std suggests unstable load)
    if "demand_std_MW" in features.columns and "demand_mean_MW" in features.columns:
        stress["demand_cv"] = (
            features["demand_std_MW"]
            / features["demand_mean_MW"].replace(0, np.nan)
        )

    # Composite risk score (simple weighted sum of normalized indicators)
    risk_components = []
    if "renewable_fraction" in stress.columns:
        risk_components.append(stress["renewable_fraction"].fillna(0))
    if "solar_fraction" in stress.columns:
        risk_components.append(stress["solar_fraction"].fillna(0))
    if "sync_fraction" in stress.columns:
        risk_components.append(1 - stress["sync_fraction"].fillna(1))
    if "has_negative_price" in stress.columns:
        risk_components.append(stress["has_negative_price"].fillna(0) * 0.5)

    if risk_components:
        stress["composite_risk_score"] = sum(risk_components) / len(risk_components)

    return stress
