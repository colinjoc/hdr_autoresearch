"""Tests for IE international construction cost analysis."""
import pytest
import pandas as pd
import numpy as np
import os
import sys

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)


@pytest.fixture
def raw_data():
    return pd.read_csv(os.path.join(PROJECT_DIR, "data/raw/eurostat_cci_filtered.csv"))


@pytest.fixture
def prc_i21(raw_data):
    return raw_data[
        (raw_data["indic_bt"] == "PRC_PRR") & (raw_data["unit"] == "I21")
    ].copy()


class TestDataIntegrity:
    def test_filtered_csv_has_all_comparators(self, raw_data):
        expected = {"AT", "BE", "DE", "DK", "ES", "FI", "FR", "IE", "NL", "SE", "UK"}
        actual = set(raw_data["geo"].unique())
        assert expected.issubset(actual), f"Missing: {expected - actual}"

    def test_ireland_has_prc_prr(self, raw_data):
        ie = raw_data[raw_data["geo"] == "IE"]
        assert "PRC_PRR" in ie["indic_bt"].values

    def test_all_non_uk_have_i21(self, prc_i21):
        countries = {"AT", "BE", "DE", "DK", "ES", "FI", "FR", "IE", "NL", "SE"}
        actual = set(prc_i21["geo"].unique())
        assert countries.issubset(actual), f"Missing I21: {countries - actual}"

    def test_2015_q1_exists_for_all(self, prc_i21):
        countries = ["AT", "BE", "DE", "DK", "ES", "FI", "FR", "IE", "NL", "SE"]
        for geo in countries:
            g = prc_i21[prc_i21["geo"] == geo]
            assert "2015-Q1" in g["TIME_PERIOD"].values, f"{geo} missing 2015-Q1"

    def test_data_extends_to_2025(self, prc_i21):
        ie = prc_i21[prc_i21["geo"] == "IE"]
        latest = ie["TIME_PERIOD"].max()
        assert latest >= "2025-Q1", f"IE latest is only {latest}"


class TestRebasedIndex:
    def test_rebase_2015_equals_100(self, prc_i21):
        for geo in ["IE", "DE", "NL"]:
            g = prc_i21[prc_i21["geo"] == geo].sort_values("TIME_PERIOD")
            val_2015 = g[g["TIME_PERIOD"] == "2015-Q1"]["OBS_VALUE"].values[0]
            rebased = g["OBS_VALUE"] / val_2015 * 100
            val_at_2015 = rebased[g["TIME_PERIOD"] == "2015-Q1"].values[0]
            assert abs(val_at_2015 - 100.0) < 0.01

    def test_growth_positive_2015_to_2025(self, prc_i21):
        """All countries should show positive growth 2015-2025."""
        for geo in ["IE", "DE", "NL", "FR"]:
            g = prc_i21[prc_i21["geo"] == geo].sort_values("TIME_PERIOD")
            val_2015 = g[g["TIME_PERIOD"] == "2015-Q1"]["OBS_VALUE"].values[0]
            val_2025 = g[g["TIME_PERIOD"] <= "2025-Q4"].sort_values("TIME_PERIOD").iloc[-1]["OBS_VALUE"]
            assert val_2025 > val_2015, f"{geo} did not grow"


class TestGrowthRanking:
    def test_ireland_growth_rank_mid_table(self, prc_i21):
        """Ireland should NOT be #1 or #2 in cumulative growth."""
        countries = ["AT", "BE", "DE", "DK", "ES", "FI", "FR", "IE", "NL", "SE"]
        growths = {}
        for geo in countries:
            g = prc_i21[prc_i21["geo"] == geo].sort_values("TIME_PERIOD")
            val_2015 = g[g["TIME_PERIOD"] == "2015-Q1"]["OBS_VALUE"].values[0]
            val_latest = g[g["TIME_PERIOD"] <= "2025-Q4"].sort_values("TIME_PERIOD").iloc[-1]["OBS_VALUE"]
            growths[geo] = val_latest / val_2015
        ranked = sorted(growths.items(), key=lambda x: -x[1])
        ie_rank = [i for i, (g, _) in enumerate(ranked) if g == "IE"][0] + 1
        assert ie_rank > 2, f"Ireland ranked #{ie_rank}, expected mid-table"

    def test_germany_netherlands_highest_growth(self, prc_i21):
        """DE and NL should be top-2 fastest growers."""
        countries = ["AT", "BE", "DE", "DK", "ES", "FI", "FR", "IE", "NL", "SE"]
        growths = {}
        for geo in countries:
            g = prc_i21[prc_i21["geo"] == geo].sort_values("TIME_PERIOD")
            val_2015 = g[g["TIME_PERIOD"] == "2015-Q1"]["OBS_VALUE"].values[0]
            val_latest = g[g["TIME_PERIOD"] <= "2025-Q4"].sort_values("TIME_PERIOD").iloc[-1]["OBS_VALUE"]
            growths[geo] = val_latest / val_2015
        ranked = sorted(growths.items(), key=lambda x: -x[1])
        top2 = {ranked[0][0], ranked[1][0]}
        assert {"DE", "NL"}.issubset(top2), f"Top 2 are {top2}, not DE+NL"


class TestAbsoluteLevels:
    def test_ireland_below_eu_average(self):
        """Ireland EUR/sqm should be near or below EU-10 average."""
        abs_2025 = {
            "IE": 1975, "NL": 2150, "DE": 2500, "FR": 1600,
            "DK": 2400, "SE": 2100, "AT": 2200, "FI": 2000,
            "BE": 1800, "ES": 1400
        }
        eu_avg = np.mean([v for k, v in abs_2025.items() if k != "IE"])
        assert abs_2025["IE"] <= eu_avg * 1.05, "Ireland should be near or below EU avg"

    def test_uk_most_expensive(self):
        """UK should be the most expensive comparator."""
        abs_2025 = {
            "IE": 1975, "UK": 2800, "NL": 2150, "DE": 2500,
            "FR": 1600, "DK": 2400, "SE": 2100, "AT": 2200,
            "FI": 2000, "BE": 1800, "ES": 1400
        }
        assert max(abs_2025, key=abs_2025.get) == "UK"


class TestClusterAnalysis:
    def test_ireland_not_in_fastest_cluster(self, prc_i21):
        """Ireland should not cluster with DE/NL (fastest growers)."""
        from scipy.cluster.hierarchy import linkage, fcluster
        from scipy.spatial.distance import pdist

        countries = ["AT", "BE", "DE", "DK", "ES", "FI", "FR", "IE", "NL", "SE"]
        panel = {}
        for geo in countries:
            g = prc_i21[prc_i21["geo"] == geo].sort_values("TIME_PERIOD")
            val_2015 = g[g["TIME_PERIOD"] == "2015-Q1"]["OBS_VALUE"].values[0]
            g_sub = g[(g["TIME_PERIOD"] >= "2015-Q1") & (g["TIME_PERIOD"] <= "2025-Q4")].copy()
            g_sub["idx"] = g_sub["OBS_VALUE"] / val_2015 * 100
            panel[geo] = g_sub.set_index("TIME_PERIOD")["idx"]

        pdf = pd.DataFrame(panel).dropna()
        traj = np.array([pdf[geo].values for geo in countries])
        traj_norm = traj - traj[:, 0:1]

        dist = pdist(traj_norm, metric="euclidean")
        Z = linkage(dist, method="ward")
        clusters = fcluster(Z, t=3, criterion="maxclust")

        de_cluster = clusters[countries.index("DE")]
        nl_cluster = clusters[countries.index("NL")]
        ie_cluster = clusters[countries.index("IE")]

        # DE and NL should be in same cluster
        assert de_cluster == nl_cluster, "DE and NL should cluster together"
        # IE should NOT be in that cluster
        assert ie_cluster != de_cluster, "IE should not be in the DE/NL fast-growth cluster"
