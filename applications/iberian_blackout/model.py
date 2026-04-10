"""
Cascade risk prediction model for the Iberian Blackout project.

This implements the Option C (decomposition) approach: we decompose the
April 28 2025 blackout into component mechanisms and build physics-informed
proxies for each, then combine them into a cascade risk score.

The key insight from the ENTSO-E investigation: the blackout was NOT
primarily an inertia problem. It was a voltage/reactive power control
failure that cascaded through generation disconnections. The risk model
must capture:

1. INERTIA PROXY: Fraction of generation from synchronous machines
   (provides frequency stability and natural voltage regulation)

2. VOLTAGE STRESS PROXY: Conditions that lead to overvoltage —
   high solar penetration + low demand + high exports (light loading
   of transmission lines raises voltage)

3. REACTIVE POWER GAP PROXY: Mismatch between reactive power need
   and availability — when solar/wind operate in fixed power factor
   mode, reactive support drops with active power changes

4. CASCADE VULNERABILITY: How quickly generation loss propagates —
   high export dependency means perturbations are amplified
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

from data_loader import build_daily_feature_matrix, compute_grid_stress_indicators
from evaluate import label_blackout_risk


def compute_inertia_proxy(features: pd.DataFrame) -> pd.Series:
    """
    Compute a proxy for system inertia based on generation mix.

    System inertia H is proportional to the sum of rotating mass connected
    to the grid. Synchronous generators (nuclear, coal, gas, hydro with
    large turbines) contribute inertia. Solar PV and most wind (Type 4 DFIG)
    contribute zero or very little.

    We approximate: H_proxy = sync_generation / total_generation

    Lower values = lower inertia = higher frequency vulnerability.

    Parameters
    ----------
    features : pd.DataFrame
        Daily feature matrix from build_daily_feature_matrix

    Returns
    -------
    pd.Series
        Inertia proxy (0-1, higher = more inertia)
    """
    if "sync_fraction" in features.columns:
        return features["sync_fraction"].copy()

    # Fallback: compute from raw generation columns
    sync_cols = [
        c for c in features.columns
        if any(s in c.lower() for s in ["nuclear", "coal", "gas", "combined", "cogeneration"])
        and "total" not in c.lower()
        and "fraction" not in c.lower()
        and "_MWh" not in c  # avoid derived columns
    ]
    # Include hydro as partially synchronous
    hydro_cols = [c for c in features.columns if "hydro" in c.lower() and "fraction" not in c.lower() and "total" not in c.lower()]

    total_col = "total_generation_MWh"
    if total_col not in features.columns:
        return pd.Series(np.nan, index=features.index)

    sync_sum = features[sync_cols].sum(axis=1) if sync_cols else 0
    # Hydro contributes ~70% of its capacity as inertia (large turbines)
    hydro_sum = features[hydro_cols].sum(axis=1) * 0.7 if hydro_cols else 0

    inertia = (sync_sum + hydro_sum) / features[total_col].replace(0, np.nan)
    return inertia.clip(0, 1)


def compute_voltage_stress_proxy(features: pd.DataFrame) -> pd.Series:
    """
    Compute a proxy for voltage stress conditions.

    The ENTSO-E report found that overvoltage was the primary cascade
    mechanism. Conditions that promote overvoltage:

    1. Light loading of transmission lines (low demand relative to capacity)
    2. High solar generation (capacitive effect of long cable runs)
    3. High exports (power flowing out creates reactive power surplus)
    4. Low price (indicates market dispatching away from voltage-supporting units)

    We combine these into a single stress metric.

    Parameters
    ----------
    features : pd.DataFrame

    Returns
    -------
    pd.Series
        Voltage stress proxy (higher = more stressed)
    """
    components = []

    # Solar dominance factor
    if "solar_fraction" in features.columns:
        components.append(features["solar_fraction"].fillna(0))

    # Light loading: high generation relative to demand
    if "total_generation_MWh" in features.columns and "demand_mean_MW" in features.columns:
        gen_demand_ratio = features["total_generation_MWh"] / (features["demand_mean_MW"] * 24).replace(0, np.nan)
        # Normalize: typical ratio is ~1.0-1.5, stress above 1.5
        components.append((gen_demand_ratio.fillna(1) - 1).clip(0, 2) / 2)

    # Low price indicator
    if "price_min" in features.columns:
        # Negative or near-zero prices indicate oversupply
        price_stress = (-features["price_min"].fillna(50)).clip(0, 100) / 100
        components.append(price_stress)

    # Export intensity
    export_cols = [c for c in features.columns if "net_flow" in c]
    if export_cols and "total_generation_MWh" in features.columns:
        total_export = features[export_cols].sum(axis=1).abs()
        export_frac = total_export / features["total_generation_MWh"].replace(0, np.nan)
        components.append(export_frac.fillna(0).clip(0, 1))

    if not components:
        return pd.Series(0, index=features.index)

    # Weighted combination
    result = sum(components) / len(components)
    return result.clip(0, 1)


def compute_reactive_power_gap_proxy(features: pd.DataFrame) -> pd.Series:
    """
    Compute a proxy for reactive power gap.

    Without direct reactive power measurements, we estimate the gap as:
    reactive_gap ~ (1 - sync_fraction) * solar_fraction

    This captures the situation where:
    - High solar = generators in fixed power factor mode
    - Low synchronous = few machines providing dynamic reactive support
    - The product captures the worst case: many fixed-PF generators AND
      few dynamic reactive sources

    Parameters
    ----------
    features : pd.DataFrame

    Returns
    -------
    pd.Series
        Reactive power gap proxy (higher = larger gap)
    """
    sync_frac = features.get("sync_fraction", pd.Series(0.5, index=features.index))
    solar_frac = features.get("solar_fraction", pd.Series(0, index=features.index))

    # Reactive gap increases when sync is low AND solar is high
    gap = (1 - sync_frac.fillna(0.5)) * solar_frac.fillna(0)

    # Also factor in wind (Type 4 DFIG provides some reactive support)
    wind_frac = features.get("wind_fraction", pd.Series(0, index=features.index))
    # Wind provides ~30% of the reactive support of synchronous
    gap = gap - wind_frac.fillna(0) * 0.3 * (1 - sync_frac.fillna(0.5))

    return gap.clip(0, 1)


class CascadeRiskModel:
    """
    Cascade risk prediction model.

    Combines physics-informed proxy features with a machine learning
    classifier to predict grid states that are one perturbation away
    from cascading collapse.

    The model architecture:
    1. Compute physics proxies (inertia, voltage stress, reactive gap)
    2. Combine with raw grid features
    3. Train a classifier (default: gradient boosting with balanced weights)
    4. Output a calibrated risk score (0-1)
    """

    def __init__(self, model_type="logistic"):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        self.is_fitted = False

    def _build_features(self, features: pd.DataFrame) -> pd.DataFrame:
        """Build the complete feature matrix from raw daily features."""
        X = pd.DataFrame(index=features.index)

        # Physics proxies
        X["inertia_proxy"] = compute_inertia_proxy(features)
        X["voltage_stress"] = compute_voltage_stress_proxy(features)
        X["reactive_gap"] = compute_reactive_power_gap_proxy(features)

        # Grid stress indicators
        stress = compute_grid_stress_indicators(features)
        for col in stress.columns:
            if col not in X.columns:
                X[col] = stress[col]

        # Temporal
        X["day_of_week"] = features.index.dayofweek
        X["is_weekend"] = X["day_of_week"].isin([5, 6]).astype(int)

        # Interaction features (physics-informed)
        X["solar_x_low_sync"] = X["voltage_stress"] * (1 - X["inertia_proxy"].fillna(0.5))
        X["reactive_x_export"] = X["reactive_gap"] * X.get("export_fraction", pd.Series(0, index=X.index)).fillna(0)

        self.feature_names = X.columns.tolist()
        return X

    def fit(self, features: pd.DataFrame, labels: pd.Series = None):
        """
        Fit the cascade risk model.

        Parameters
        ----------
        features : pd.DataFrame
            Raw daily feature matrix
        labels : pd.Series, optional
            Binary risk labels. If None, computed automatically.
        """
        if labels is None:
            labels = label_blackout_risk(features)

        X = self._build_features(features)

        # Align and clean
        common_idx = X.index.intersection(labels.index)
        X = X.loc[common_idx]
        y = labels.loc[common_idx]
        valid = X.notna().all(axis=1) & y.notna()
        X = X[valid]
        y = y[valid]

        X_numeric = X.select_dtypes(include=[np.number])
        self.feature_names = X_numeric.columns.tolist()

        X_scaled = self.scaler.fit_transform(X_numeric)

        if self.model_type == "logistic":
            self.model = LogisticRegression(
                class_weight="balanced",
                max_iter=1000,
                random_state=42,
                C=1.0,  # HDR exp: C=1.0 gives AUC 0.952 vs C=0.1 AUC 0.948
            )
        elif self.model_type == "rf":
            self.model = RandomForestClassifier(
                n_estimators=100,
                class_weight="balanced",
                max_depth=3,
                random_state=42,
            )
        elif self.model_type == "gbm":
            # For small imbalanced datasets, be conservative
            n_pos = y.sum()
            scale = (len(y) - n_pos) / max(n_pos, 1)
            self.model = GradientBoostingClassifier(
                n_estimators=50,
                max_depth=2,
                learning_rate=0.1,
                random_state=42,
            )

        self.model.fit(X_scaled, y)
        self.is_fitted = True

    def predict(self, features: pd.DataFrame) -> pd.DataFrame:
        """
        Predict cascade risk for each day.

        Returns
        -------
        pd.DataFrame
            Columns: risk_score (0-1), risk_class (0 or 1)
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")

        X = self._build_features(features)
        X_numeric = X[self.feature_names].select_dtypes(include=[np.number])

        # Handle NaN by filling with training means
        X_filled = X_numeric.fillna(X_numeric.mean())
        X_scaled = self.scaler.transform(X_filled)

        risk_proba = self.model.predict_proba(X_scaled)[:, 1]
        risk_class = self.model.predict(X_scaled)

        return pd.DataFrame(
            {"risk_score": risk_proba, "risk_class": risk_class},
            index=features.index,
        )

    def feature_importance(self) -> pd.Series:
        """
        Get feature importance from the fitted model.

        Returns
        -------
        pd.Series
            Feature importances sorted descending
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted.")

        if hasattr(self.model, "coef_"):
            imp = pd.Series(
                np.abs(self.model.coef_[0]),
                index=self.feature_names,
            )
        elif hasattr(self.model, "feature_importances_"):
            imp = pd.Series(
                self.model.feature_importances_,
                index=self.feature_names,
            )
        else:
            imp = pd.Series(dtype=float)

        return imp.sort_values(ascending=False)
