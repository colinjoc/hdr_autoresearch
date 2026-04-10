"""Tests for data loading and preprocessing."""
import pytest
import pandas as pd
import numpy as np
import sys
sys.path.insert(0, '/home/col/generalized_hdr_autoresearch/applications/dublin_no2')


def test_load_ireland_daily():
    """Daily Ireland NO2 data loads and has expected structure."""
    from data_loaders import load_ireland_daily
    df = load_ireland_daily()
    assert len(df) > 50000, f"Expected >50k records, got {len(df)}"
    assert 'date' in df.columns
    assert 'NO2' in df.columns
    assert 'station' in df.columns
    assert df['date'].dtype == 'datetime64[ns]'


def test_load_key_stations():
    """Key Dublin/Cork stations have NO2 data."""
    from data_loaders import load_ireland_daily, KEY_STATIONS
    df = load_ireland_daily()
    for code in ['IE005AP', 'IE0098A', 'IE0131A', 'IE0036A', 'IE0090A']:
        station_data = df[(df['station'] == code) & (df['NO2'].notna())]
        assert len(station_data) > 100, f"Station {code} has too few NO2 records: {len(station_data)}"


def test_load_weather():
    """Dublin Airport weather data loads correctly."""
    from data_loaders import load_weather
    wx = load_weather()
    assert len(wx) > 70000, f"Expected >70k records, got {len(wx)}"
    assert 'datetime' in wx.columns
    assert 'temp' in wx.columns
    assert 'wdsp' in wx.columns
    assert 'wddir' in wx.columns


def test_merge_no2_weather():
    """NO2 and weather data merge on date correctly."""
    from data_loaders import load_merged_daily
    df = load_merged_daily(station='IE005AP')
    assert len(df) > 100
    assert 'NO2' in df.columns
    assert 'temp_mean' in df.columns
    assert 'wdsp_mean' in df.columns
    # No synthetic data — all values should be real measurements
    assert df['NO2'].notna().sum() > 100


def test_no_synthetic_data():
    """Verify data is real, not synthetic — check reasonable value ranges."""
    from data_loaders import load_ireland_daily
    df = load_ireland_daily()
    no2 = df['NO2'].dropna()
    # Real NO2 should be 0-200 µg/m³ typically
    assert no2.min() >= 0, "Negative NO2 is impossible"
    assert no2.max() < 500, "NO2 > 500 µg/m³ is implausible for Ireland"
    # Dublin traffic stations should have annual means 15-50
    winetavern = df[df['station'] == 'IE005AP']
    annual = winetavern.groupby(winetavern['date'].dt.year)['NO2'].mean()
    assert annual.max() > 25, "Winetavern should exceed 25 µg/m³ annually"
    assert annual.max() < 60, "Winetavern >60 µg/m³ is implausible"


def test_who_guideline_exceedance():
    """WHO 2021 guidelines: 10 µg/m³ annual, 25 µg/m³ 24-hour."""
    from data_loaders import load_ireland_daily, WHO_ANNUAL, WHO_24H
    assert WHO_ANNUAL == 10
    assert WHO_24H == 25
    df = load_ireland_daily()
    # Most Dublin stations should exceed annual WHO guideline
    winetavern = df[df['station'] == 'IE005AP']
    annual_mean = winetavern.groupby(winetavern['date'].dt.year)['NO2'].mean()
    assert (annual_mean > WHO_ANNUAL).all(), "Winetavern should exceed WHO annual limit every year"
    # Rural station should be below
    rural = df[df['station'] == 'IE0090A']
    rural_annual = rural.groupby(rural['date'].dt.year)['NO2'].mean()
    assert (rural_annual < WHO_ANNUAL).all(), "Lough Navar (rural) should be below WHO annual limit"


def test_covid_lockdown_signal():
    """COVID lockdown (Mar-Jun 2020) should show clear NO2 drop vs same period 2019."""
    from data_loaders import load_ireland_daily
    df = load_ireland_daily()
    for station in ['IE005AP', 'IE0131A', 'IE0036A']:
        sdf = df[df['station'] == station]
        lockdown_2020 = sdf[(sdf['date'] >= '2020-03-15') & (sdf['date'] <= '2020-06-30')]['NO2'].mean()
        same_period_2019 = sdf[(sdf['date'] >= '2019-03-15') & (sdf['date'] <= '2019-06-30')]['NO2'].mean()
        if pd.notna(lockdown_2020) and pd.notna(same_period_2019):
            assert lockdown_2020 < same_period_2019, \
                f"Station {station}: COVID lockdown NO2 ({lockdown_2020:.1f}) should be < 2019 ({same_period_2019:.1f})"
