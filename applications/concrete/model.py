"""
Concrete mix design: prediction + discovery.

THIS IS THE ONLY FILE THE AUTORESEARCH AGENT MODIFIES.
"""

import itertools
import numpy as np
import pandas as pd
import xgboost as xgb

RAW_FEATURES = ["cement", "slag", "fly_ash", "water", "superplasticizer",
                 "coarse_agg", "fine_agg", "age"]


class ConcreteModel:

    def __init__(self):
        self.model = None
        self.feature_names = None

    def featurize(self, df):
        X = df[RAW_FEATURES].copy()
        self.feature_names = list(X.columns)
        y = df["strength"].values.astype(np.float32)
        return X.values.astype(np.float32), y

    def featurize_single(self, mix_dict):
        vals = [mix_dict.get(f, 0) for f in self.feature_names]
        return np.array(vals, dtype=np.float32)

    def train(self, X, y):
        dtrain = xgb.DMatrix(X, label=y)
        params = {
            "objective": "reg:squarederror",
            "max_depth": 6,
            "learning_rate": 0.05,
            "min_child_weight": 3,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "verbosity": 0,
        }
        self.model = xgb.train(params, dtrain, num_boost_round=300)

    def predict(self, X):
        return self.model.predict(xgb.DMatrix(X))

    def generate_candidates(self):
        """Generate candidate mix designs for multi-objective screening.

        Explores the 8D mix space systematically, focusing on:
        - High-SCM mixes (low CO2)
        - High-cement mixes (high strength)
        - Pareto-interesting combinations
        """
        candidates = []

        # Ranges for each component (kg/m³), based on dataset statistics
        cement_range = [150, 200, 250, 300, 350, 400, 450, 500]
        slag_range = [0, 50, 100, 150, 200]
        fly_ash_range = [0, 50, 100, 150, 200]
        water_range = [140, 160, 180, 200]
        sp_range = [0, 5, 10, 15]
        coarse_range = [800, 900, 1000, 1050]
        fine_range = [600, 700, 800]
        age_values = [28]  # standard 28-day strength

        # Strategy 1: Systematic grid on key variables (cement, slag, fly_ash, water)
        for c in cement_range:
            for s in [0, 100, 200]:
                for fa in [0, 100, 200]:
                    for w in water_range:
                        candidates.append({
                            "cement": c, "slag": s, "fly_ash": fa,
                            "water": w, "superplasticizer": 8,
                            "coarse_agg": 950, "fine_agg": 700,
                            "age": 28, "source": "grid",
                        })

        # Strategy 2: Ultra-low-cement mixes (push CO2 down)
        for s in [150, 200, 250, 300]:
            for fa in [100, 150, 200]:
                for c in [100, 120, 150]:
                    candidates.append({
                        "cement": c, "slag": s, "fly_ash": fa,
                        "water": 160, "superplasticizer": 12,
                        "coarse_agg": 950, "fine_agg": 700,
                        "age": 28, "source": "low_cement",
                    })

        # Strategy 3: High-performance mixes (push strength up)
        for c in [450, 500, 540]:
            for sp in [10, 15, 20]:
                for w in [130, 140, 150, 160]:
                    candidates.append({
                        "cement": c, "slag": 0, "fly_ash": 0,
                        "water": w, "superplasticizer": sp,
                        "coarse_agg": 1000, "fine_agg": 750,
                        "age": 28, "source": "high_strength",
                    })

        return candidates
