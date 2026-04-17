"""Tests for parse_data.py — TDD: these were written first."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import pandas as pd
from parse_data import parse_wpm28, parse_ehq03, parse_bea04


class TestParseWPM28:
    def test_returns_dataframe(self):
        df = parse_wpm28()
        assert isinstance(df, pd.DataFrame)

    def test_expected_columns(self):
        df = parse_wpm28()
        for col in ["date", "material_code", "material_label", "index_value", "mom_pct", "yoy_pct"]:
            assert col in df.columns, f"Missing column: {col}"

    def test_40_materials(self):
        df = parse_wpm28()
        assert df["material_code"].nunique() == 40

    def test_117_months(self):
        df = parse_wpm28()
        assert df["date"].nunique() == 117

    def test_row_count(self):
        df = parse_wpm28()
        assert df.shape[0] == 40 * 117  # 4680

    def test_base_year_2015(self):
        """All materials should be ~100 in Jan 2015."""
        df = parse_wpm28()
        jan_2015 = df[df["date"] == "2015-01-01"]
        all_mat = jan_2015[jan_2015["material_code"] == "-"]
        assert len(all_mat) == 1
        assert abs(all_mat["index_value"].iloc[0] - 100.0) < 1.0

    def test_date_range(self):
        df = parse_wpm28()
        assert df["date"].min() == pd.Timestamp("2015-01-01")
        assert df["date"].max() == pd.Timestamp("2024-09-01")


class TestParseEHQ03:
    def test_returns_dataframe(self):
        df = parse_ehq03()
        assert isinstance(df, pd.DataFrame)

    def test_has_date(self):
        df = parse_ehq03()
        assert "date" in df.columns

    def test_has_employment(self):
        df = parse_ehq03()
        assert "EHQ03C01" in df.columns  # Employment

    def test_has_hourly_labour_cost(self):
        df = parse_ehq03()
        assert "EHQ03C08" in df.columns  # Average Hourly Total Labour Costs

    def test_quarterly_data(self):
        df = parse_ehq03()
        assert df.shape[0] >= 40  # at least 10 years of quarters


class TestParseBEA04:
    def test_returns_dataframe(self):
        df = parse_bea04()
        assert isinstance(df, pd.DataFrame)

    def test_has_residential(self):
        df = parse_bea04()
        assert "111" in df["sector_code"].values  # Residential building

    def test_year_range(self):
        df = parse_bea04()
        assert df["year"].min() == 2000
        assert df["year"].max() == 2024
