"""
Evaluation harness for flight delay propagation prediction.

Fixed during HDR loop — only model.py changes.
"""
import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge, LogisticRegression
from sklearn.metrics import roc_auc_score, f1_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

from prepare import (
    load_clean, build_features, get_feature_columns,
    make_target, temporal_cv_splits
)


def _get_model(model_type, **kwargs):
    """Instantiate a model by type name."""
    if model_type == 'ridge':
        return LogisticRegression(max_iter=1000, C=1.0, solver='lbfgs')
    elif model_type == 'xgboost':
        from xgboost import XGBClassifier
        return XGBClassifier(
            n_estimators=kwargs.get('n_estimators', 200),
            max_depth=kwargs.get('max_depth', 6),
            learning_rate=kwargs.get('lr', 0.1),
            subsample=0.8,
            colsample_bytree=0.8,
            eval_metric='logloss',
            verbosity=0,
            n_jobs=-1,
            tree_method='hist',
            device=kwargs.get('device', 'cuda'),
        )
    elif model_type == 'lightgbm':
        from lightgbm import LGBMClassifier
        return LGBMClassifier(
            n_estimators=kwargs.get('n_estimators', 200),
            max_depth=kwargs.get('max_depth', 6),
            learning_rate=kwargs.get('lr', 0.1),
            subsample=0.8,
            colsample_bytree=0.8,
            verbosity=-1,
            n_jobs=-1,
            device=kwargs.get('device', 'gpu'),
        )
    elif model_type == 'extratrees':
        from sklearn.ensemble import ExtraTreesClassifier
        return ExtraTreesClassifier(
            n_estimators=kwargs.get('n_estimators', 200),
            max_depth=kwargs.get('max_depth', 20),
            n_jobs=-1,
        )
    else:
        raise ValueError(f"Unknown model type: {model_type}")


def train_and_evaluate(months, model_type='xgboost', holdout_months=None,
                       n_folds=3, year=2024, **model_kwargs):
    """
    Full train + evaluate pipeline with temporal CV.

    Parameters
    ----------
    months : list[int]
        Months to use for training/CV
    model_type : str
        One of 'ridge', 'xgboost', 'lightgbm', 'extratrees'
    holdout_months : list[int] or None
        If provided, train on all months and evaluate on holdout
    n_folds : int
        Number of temporal CV folds
    year : int
        Year of data

    Returns
    -------
    dict with keys: cv_auc, cv_f1, holdout_auc (if applicable),
                    feature_importances, per_fold_results
    """
    print(f"\n{'='*60}")
    print(f"Training {model_type} on {year} months {months}")
    print(f"{'='*60}")

    # Load and featurize training data
    df = load_clean(year, months)
    print(f"Loaded {len(df):,} flights")

    df = build_features(df)
    feature_cols = get_feature_columns(df)
    print(f"Features: {len(feature_cols)} columns")

    X = df[feature_cols].copy()
    y = make_target(df)
    print(f"Target: {y.mean():.1%} delayed (>= 15 min)")

    # Fill NaN features with -999 (tree models handle this; linear models get scaled)
    X = X.fillna(-999)

    # Temporal CV
    splits = temporal_cv_splits(df, n_folds=n_folds)
    fold_results = []

    for fold_i, (train_idx, test_idx) in enumerate(splits):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        if model_type == 'ridge':
            scaler = StandardScaler()
            X_train_s = scaler.fit_transform(X_train)
            X_test_s = scaler.transform(X_test)
            model = _get_model(model_type, **model_kwargs)
            model.fit(X_train_s, y_train)
            y_prob = model.predict_proba(X_test_s)[:, 1]
        else:
            model = _get_model(model_type, **model_kwargs)
            try:
                model.fit(X_train, y_train)
            except Exception:
                # Fall back to CPU if GPU not available
                if 'device' in model_kwargs:
                    model_kwargs_cpu = {**model_kwargs, 'device': 'cpu'}
                else:
                    model_kwargs_cpu = model_kwargs
                model = _get_model(model_type, **{**model_kwargs_cpu, 'device': 'cpu'})
                model.fit(X_train, y_train)
            y_prob = model.predict_proba(X_test)[:, 1]

        auc = roc_auc_score(y_test, y_prob)
        y_pred = (y_prob >= 0.5).astype(int)
        f1 = f1_score(y_test, y_pred)
        fold_results.append({'auc': auc, 'f1': f1, 'n_test': len(y_test)})
        print(f"  Fold {fold_i+1}: AUC={auc:.4f}, F1={f1:.4f}, n={len(y_test):,}")

    cv_auc = np.mean([r['auc'] for r in fold_results])
    cv_f1 = np.mean([r['f1'] for r in fold_results])
    print(f"  CV Mean: AUC={cv_auc:.4f}, F1={cv_f1:.4f}")

    # Get feature importances from final fold model
    feature_importances = {}
    if hasattr(model, 'feature_importances_'):
        for col, imp in zip(feature_cols, model.feature_importances_):
            feature_importances[col] = float(imp)
    elif hasattr(model, 'coef_'):
        for col, coef in zip(feature_cols, model.coef_[0]):
            feature_importances[col] = float(abs(coef))

    results = {
        'cv_auc': cv_auc,
        'cv_f1': cv_f1,
        'per_fold_results': fold_results,
        'feature_importances': feature_importances,
        'model_type': model_type,
        'n_features': len(feature_cols),
        'n_flights': len(df),
        'delay_rate': float(y.mean()),
    }

    # Holdout evaluation
    if holdout_months:
        print(f"\nHoldout evaluation on months {holdout_months}...")
        df_hold = load_clean(year, holdout_months)
        df_hold = build_features(df_hold)
        X_hold = df_hold[feature_cols].fillna(-999)
        y_hold = make_target(df_hold)

        # Retrain on all training data
        X_full = X.copy()
        y_full = y.copy()

        if model_type == 'ridge':
            scaler = StandardScaler()
            X_full_s = scaler.fit_transform(X_full)
            X_hold_s = scaler.transform(X_hold)
            model = _get_model(model_type, **model_kwargs)
            model.fit(X_full_s, y_full)
            y_prob_hold = model.predict_proba(X_hold_s)[:, 1]
        else:
            model = _get_model(model_type, **model_kwargs)
            try:
                model.fit(X_full, y_full)
            except Exception:
                model = _get_model(model_type, **{**model_kwargs, 'device': 'cpu'})
                model.fit(X_full, y_full)
            y_prob_hold = model.predict_proba(X_hold)[:, 1]

        hold_auc = roc_auc_score(y_hold, y_prob_hold)
        y_pred_hold = (y_prob_hold >= 0.5).astype(int)
        hold_f1 = f1_score(y_hold, y_pred_hold)
        results['holdout_auc'] = hold_auc
        results['holdout_f1'] = hold_f1
        print(f"  Holdout: AUC={hold_auc:.4f}, F1={hold_f1:.4f}")

    return results


def decompose_delay_variance(months, year=2024):
    """
    Decompose total delay variance into BTS cause categories.

    BTS reports 5 cause codes for delayed flights (>15 min):
    - CarrierDelay: maintenance, crew problems, aircraft cleaning, baggage
    - WeatherDelay: significant weather events
    - NASDelay: National Airspace System - ATC, airport operations, heavy traffic
    - SecurityDelay: security breaches, long lines, etc.
    - LateAircraftDelay: previous flight on same aircraft arrived late

    Returns fraction of total delay minutes attributable to each cause.
    """
    df = load_clean(year, months)

    # Only consider flights with delay cause data (flights delayed >= 15 min)
    cause_cols = ['CarrierDelay', 'WeatherDelay', 'NASDelay',
                  'SecurityDelay', 'LateAircraftDelay']
    delayed = df[df[cause_cols].notna().all(axis=1)].copy()

    total_delay = delayed[cause_cols].sum().sum()

    decomp = {
        'rotation': float(delayed['LateAircraftDelay'].sum() / total_delay),
        'weather': float(delayed['WeatherDelay'].sum() / total_delay),
        'carrier': float(delayed['CarrierDelay'].sum() / total_delay),
        'nas': float(delayed['NASDelay'].sum() / total_delay),
        'security': float(delayed['SecurityDelay'].sum() / total_delay),
    }

    print(f"\nDelay Variance Decomposition ({len(delayed):,} delayed flights):")
    for cause, frac in sorted(decomp.items(), key=lambda x: -x[1]):
        print(f"  {cause:12s}: {frac:6.1%}")

    return decomp


def measure_propagation_depth(months, year=2024):
    """
    Measure how far delays propagate through aircraft rotation chains.

    For each initially delayed flight, trace forward through the rotation chain
    and count how many subsequent flights on the same aircraft are also delayed.
    """
    df = load_clean(year, months)
    df = build_features(df)

    # Focus on flights where the aircraft's first flight of the day was delayed
    first_flights = df[df['rotation_position'] == 1].copy()
    delayed_first = first_flights[first_flights['ArrDelay'] >= 15]

    propagation_depths = []
    containment_count = 0

    for _, row in delayed_first.iterrows():
        tail = row['Tail_Number']
        date = row['FlightDate']

        # Get all subsequent flights for this tail on this day
        chain = df[(df['Tail_Number'] == tail) &
                   (df['FlightDate'] == date) &
                   (df['rotation_position'] > 1)].sort_values('CRSDepTime')

        if len(chain) == 0:
            containment_count += 1
            propagation_depths.append(1)
            continue

        # Count how many subsequent flights are also delayed
        depth = 1  # The initial delayed flight
        for _, sub_flight in chain.iterrows():
            if sub_flight['ArrDelay'] >= 15:
                depth += 1
            else:
                break  # Delay was absorbed

        propagation_depths.append(depth)
        if depth == 1:
            containment_count += 1

    depths = np.array(propagation_depths)
    total = len(depths)
    result = {
        'mean_depth': float(depths.mean()) if len(depths) > 0 else 0,
        'max_depth': int(depths.max()) if len(depths) > 0 else 0,
        'median_depth': float(np.median(depths)) if len(depths) > 0 else 0,
        'containment_rate': float(containment_count / total) if total > 0 else 0,
        'n_chains_analyzed': total,
        'depth_distribution': {
            int(d): int(c) for d, c in
            zip(*np.unique(depths, return_counts=True))
        } if len(depths) > 0 else {},
    }

    print(f"\nDelay Propagation Depth ({total:,} chains analyzed):")
    print(f"  Mean depth: {result['mean_depth']:.2f}")
    print(f"  Max depth: {result['max_depth']}")
    print(f"  Containment rate: {result['containment_rate']:.1%}")

    return result


if __name__ == '__main__':
    # Quick baseline run
    print("=" * 60)
    print("BASELINE: Ridge (linear) on Jan-Mar 2024, holdout Apr 2024")
    print("=" * 60)
    results = train_and_evaluate(
        months=[1, 2, 3],
        model_type='ridge',
        holdout_months=[4],
    )

    print("\n" + "=" * 60)
    print("DELAY VARIANCE DECOMPOSITION")
    print("=" * 60)
    decomp = decompose_delay_variance(months=[1, 2, 3])

    print("\n" + "=" * 60)
    print("PROPAGATION DEPTH ANALYSIS")
    print("=" * 60)
    prop = measure_propagation_depth(months=[1])
