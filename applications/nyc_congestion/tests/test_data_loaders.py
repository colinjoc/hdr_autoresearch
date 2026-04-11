"""Tests for NYC congestion charge data loaders — TDD first."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# ---------------------------------------------------------------- taxi zone lookup
class TestTaxiZoneLookup:
    def test_load_zones(self):
        from data_loaders import load_taxi_zones
        zones = load_taxi_zones()
        assert isinstance(zones, pd.DataFrame)
        assert len(zones) > 250
        assert "Borough" in zones.columns
        assert "Zone" in zones.columns
        assert "LocationID" in zones.columns

    def test_cbd_zones_identified(self):
        from data_loaders import get_cbd_zone_ids
        cbd_ids = get_cbd_zone_ids()
        assert isinstance(cbd_ids, set)
        assert len(cbd_ids) > 30  # Manhattan below 60th St has many zones
        assert len(cbd_ids) < 100

    def test_borough_zones(self):
        from data_loaders import load_taxi_zones
        zones = load_taxi_zones()
        boroughs = zones["Borough"].unique()
        for b in ["Manhattan", "Bronx", "Brooklyn", "Queens", "Staten Island"]:
            assert b in boroughs


# ---------------------------------------------------------------- traffic volume
class TestTrafficVolume:
    def test_load_traffic_counts(self):
        from data_loaders import load_traffic_counts
        df = load_traffic_counts()
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 1000
        for col in ["boro", "date", "hour", "vol", "street"]:
            assert col in df.columns
        assert df["vol"].dtype in [np.int64, np.float64, int, float]

    def test_traffic_has_pre_and_post(self):
        from data_loaders import load_traffic_counts
        df = load_traffic_counts()
        assert df["date"].min() < pd.Timestamp("2025-01-05")
        assert df["date"].max() >= pd.Timestamp("2025-01-05")

    def test_aggregate_daily_volume(self):
        from data_loaders import load_traffic_counts, aggregate_daily_volume
        df = load_traffic_counts()
        daily = aggregate_daily_volume(df)
        assert "date" in daily.columns
        assert "vol" in daily.columns
        assert "boro" in daily.columns
        assert len(daily) > 100


# ---------------------------------------------------------------- MTA ridership
class TestMTARidership:
    def test_load_mta_ridership(self):
        from data_loaders import load_mta_ridership
        df = load_mta_ridership()
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 500
        assert "date" in df.columns
        assert "subway_ridership" in df.columns
        assert "bus_ridership" in df.columns

    def test_mta_has_pre_and_post(self):
        from data_loaders import load_mta_ridership
        df = load_mta_ridership()
        assert df["date"].min() < pd.Timestamp("2025-01-01")
        assert df["date"].max() >= pd.Timestamp("2025-01-05")

    def test_mta_weekly_aggregation(self):
        from data_loaders import load_mta_ridership, aggregate_mta_weekly
        df = load_mta_ridership()
        weekly = aggregate_mta_weekly(df)
        assert "week_start" in weekly.columns
        assert "subway_ridership" in weekly.columns
        assert len(weekly) > 50


# ---------------------------------------------------------------- TLC trips
class TestTLCTrips:
    def test_load_tlc_summary(self):
        from data_loaders import load_tlc_summary
        df = load_tlc_summary()
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        for col in ["period", "cbd_pickups", "cbd_dropoffs",
                     "outer_pickups", "outer_dropoffs"]:
            assert col in df.columns

    def test_tlc_has_pre_and_post(self):
        from data_loaders import load_tlc_summary
        df = load_tlc_summary()
        periods = set(df["period"].values)
        assert "pre" in periods
        assert "post" in periods


# ---------------------------------------------------------------- master dataset
class TestMasterDataset:
    def test_build_master(self):
        from data_loaders import build_master_dataset
        df = build_master_dataset()
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 100
        assert "week_start" in df.columns
        assert "post_charge" in df.columns  # binary indicator

    def test_master_has_required_features(self):
        from data_loaders import build_master_dataset
        df = build_master_dataset()
        required = ["week_start", "boro", "daily_vol_mean", "post_charge",
                     "subway_ridership", "bus_ridership"]
        for col in required:
            assert col in df.columns, f"Missing column: {col}"

    def test_post_charge_label(self):
        from data_loaders import build_master_dataset
        df = build_master_dataset()
        pre = df[df["post_charge"] == 0]
        post = df[df["post_charge"] == 1]
        assert len(pre) > 0
        assert len(post) > 0
