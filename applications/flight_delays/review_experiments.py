"""
Experiments added during paper review cycle.

Addresses reviewer MAJOR findings:
1. SHAP analysis for feature attribution (replaces gain-only importance)
2. Temporal robustness: per-month AUC stability
3. First-leg-of-day accuracy breakdown
4. Network centrality metrics (betweenness, PageRank, degree)
5. Calibration analysis (reliability diagram, Brier score)
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from model import (
    prepare_enhanced_data, get_enhanced_feature_columns,
)
from prepare import load_clean, make_target


def compute_shap_values(months=None, sample_size=10000, year=2024):
    """
    Compute SHAP values for the XGBoost model.

    Uses TreeExplainer for exact SHAP on gradient-boosted trees.
    Subsamples to sample_size for computational tractability.

    Returns
    -------
    dict with keys:
        shap_values : np.ndarray of shape (n_samples, n_features)
        feature_names : list[str]
        mean_abs_shap : dict mapping feature_name -> mean(|SHAP|)
        X_sample : pd.DataFrame (the subsampled features for beeswarm)
    """
    import shap
    from xgboost import XGBClassifier

    if months is None:
        months = [1, 2, 3]

    df = prepare_enhanced_data(year, months)
    feature_cols = get_enhanced_feature_columns()
    feature_cols = [c for c in feature_cols if c in df.columns]

    X = df[feature_cols].fillna(-999)
    y = make_target(df)

    # Train model on full training data
    model = XGBClassifier(
        n_estimators=300, max_depth=6, learning_rate=0.1,
        subsample=0.8, colsample_bytree=0.8,
        eval_metric='logloss', verbosity=0, n_jobs=-1,
        tree_method='hist',
    )
    try:
        model.set_params(device='cuda')
        model.fit(X, y)
    except Exception:
        model.set_params(device='cpu')
        model.fit(X, y)

    # Subsample for SHAP computation
    if sample_size < len(X):
        idx = np.random.RandomState(42).choice(len(X), sample_size, replace=False)
        X_sample = X.iloc[idx]
    else:
        X_sample = X

    # TreeExplainer for exact SHAP
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_sample)

    # Mean absolute SHAP per feature
    mean_abs = np.abs(shap_values).mean(axis=0)
    mean_abs_shap = dict(zip(feature_cols, mean_abs))

    # Human-readable labels
    label_map = {
        'prev_delay_x_buffer': 'Previous delay x buffer',
        'log_prev_delay': 'Log previous delay',
        'prior_flight_arr_delay': 'Prior flight arrival delay',
        'prior_flight_late_aircraft': 'Prior late-aircraft code',
        'dest_arr_delay_mean_1h': 'Dest. arrival delay (hourly)',
        'TaxiOut': 'Taxi-out time',
        'turnaround_time': 'Turnaround time',
        'origin_dep_delay_mean_1h': 'Origin dep. delay (hourly)',
        'buffer_over_min': 'Buffer over minimum',
        'is_regional': 'Regional carrier',
        'origin_dep_delay_std_1h': 'Origin delay variability',
        'dest_flights_1h': 'Dest. traffic volume',
        'carrier_buffer_factor': 'Carrier buffer factor',
        'rotation_position': 'Rotation position',
        'origin_flights_1h': 'Origin traffic volume',
        'prior_flight_dep_delay': 'Prior flight dep. delay',
        'cumulative_delay': 'Cumulative delay',
        'origin_is_hub': 'Origin is hub',
        'dest_is_hub': 'Dest. is hub',
        'is_hub_to_hub': 'Hub-to-hub route',
        'morning_flight': 'Morning flight (6-9am)',
        'is_evening': 'Evening flight',
        'Distance': 'Route distance',
        'dep_hour_sin': 'Hour (sin)',
        'dep_hour_cos': 'Hour (cos)',
        'dow_sin': 'Day of week (sin)',
        'dow_cos': 'Day of week (cos)',
        'month_sin': 'Month (sin)',
        'month_cos': 'Month (cos)',
    }

    return {
        'shap_values': shap_values,
        'feature_names': feature_cols,
        'mean_abs_shap': mean_abs_shap,
        'X_sample': X_sample,
        'label_map': label_map,
    }


def plot_shap_summary(months=None, sample_size=10000, year=2024, top_n=15):
    """
    Generate a SHAP bar plot (mean |SHAP|) for the paper.

    Returns (fig, ax).
    """
    result = compute_shap_values(months=months, sample_size=sample_size, year=year)
    mean_abs = result['mean_abs_shap']
    label_map = result['label_map']

    # Sort by importance
    sorted_feats = sorted(mean_abs.items(), key=lambda x: -x[1])[:top_n]
    names = [label_map.get(f, f) for f, _ in sorted_feats]
    values = [v for _, v in sorted_feats]

    fig, ax = plt.subplots(figsize=(9, 6))

    # Color by category
    rotation_labels = {
        'Previous delay x buffer', 'Log previous delay',
        'Prior flight arrival delay', 'Prior late-aircraft code',
        'Turnaround time', 'Buffer over minimum', 'Carrier buffer factor',
        'Rotation position', 'Prior flight dep. delay',
        'Cumulative delay', 'Regional carrier',
    }
    colors = ['#b2182b' if n in rotation_labels else '#2166ac' for n in names]

    bars = ax.barh(range(len(names)), values, color=colors, edgecolor='white')
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names)
    ax.invert_yaxis()
    ax.set_xlabel('Mean |SHAP value| (impact on model output)')
    ax.set_title('SHAP feature importance: what drives delay propagation?\n'
                 'Red = rotation chain features, Blue = airport/temporal features')

    fig.tight_layout()
    return fig, ax


def monthly_auc_stability(train_months=None, test_months=None, year=2024):
    """
    Evaluate model AUC separately for each test month.

    Trains on train_months, evaluates on each month in test_months individually.
    This tests temporal robustness (review Missing Experiment #4).

    Returns
    -------
    dict with keys:
        per_month_auc : dict mapping month -> AUC
        mean_auc : float
        std_auc : float
    """
    from xgboost import XGBClassifier
    from sklearn.metrics import roc_auc_score

    if train_months is None:
        train_months = [1, 2, 3]
    if test_months is None:
        test_months = [4, 5, 6]

    # Train on full training set
    df_train = prepare_enhanced_data(year, train_months)
    feature_cols = get_enhanced_feature_columns()
    feature_cols = [c for c in feature_cols if c in df_train.columns]

    X_train = df_train[feature_cols].fillna(-999)
    y_train = make_target(df_train)

    model = XGBClassifier(
        n_estimators=300, max_depth=6, learning_rate=0.1,
        subsample=0.8, colsample_bytree=0.8,
        eval_metric='logloss', verbosity=0, n_jobs=-1,
        tree_method='hist',
    )
    try:
        model.set_params(device='cuda')
        model.fit(X_train, y_train)
    except Exception:
        model.set_params(device='cpu')
        model.fit(X_train, y_train)

    # Evaluate each test month separately
    per_month_auc = {}
    for m in test_months:
        df_test = prepare_enhanced_data(year, [m])
        # Ensure same feature columns
        X_test = df_test[feature_cols].fillna(-999)
        y_test = make_target(df_test)
        y_prob = model.predict_proba(X_test)[:, 1]
        auc = roc_auc_score(y_test, y_prob)
        per_month_auc[m] = auc
        print(f"  Month {m}: AUC={auc:.4f} (n={len(y_test):,})")

    aucs = list(per_month_auc.values())
    return {
        'per_month_auc': per_month_auc,
        'mean_auc': float(np.mean(aucs)),
        'std_auc': float(np.std(aucs)),
    }


def first_leg_accuracy(months=None, holdout_months=None, year=2024):
    """
    Measure model accuracy separately for first-leg-of-day flights
    (which have no rotation history) vs subsequent legs.

    This addresses review Missing Experiment #6.

    Returns
    -------
    dict with keys:
        first_leg_auc : float
        non_first_leg_auc : float
        first_leg_count : int
        non_first_leg_count : int
    """
    from xgboost import XGBClassifier
    from sklearn.metrics import roc_auc_score

    if months is None:
        months = [1, 2, 3]
    if holdout_months is None:
        holdout_months = [4]

    # Train
    df_train = prepare_enhanced_data(year, months)
    feature_cols = get_enhanced_feature_columns()
    feature_cols = [c for c in feature_cols if c in df_train.columns]

    X_train = df_train[feature_cols].fillna(-999)
    y_train = make_target(df_train)

    model = XGBClassifier(
        n_estimators=300, max_depth=6, learning_rate=0.1,
        subsample=0.8, colsample_bytree=0.8,
        eval_metric='logloss', verbosity=0, n_jobs=-1,
        tree_method='hist',
    )
    try:
        model.set_params(device='cuda')
        model.fit(X_train, y_train)
    except Exception:
        model.set_params(device='cpu')
        model.fit(X_train, y_train)

    # Evaluate on holdout, split by first-leg vs non-first-leg
    df_test = prepare_enhanced_data(year, holdout_months)
    X_test = df_test[feature_cols].fillna(-999)
    y_test = make_target(df_test)

    y_prob = model.predict_proba(X_test)[:, 1]

    first_leg_mask = df_test['rotation_position'] == 1
    first_idx = first_leg_mask.values
    non_first_idx = ~first_leg_mask.values

    first_leg_auc = roc_auc_score(y_test[first_idx], y_prob[first_idx])
    non_first_leg_auc = roc_auc_score(y_test[non_first_idx], y_prob[non_first_idx])

    print(f"  First-leg flights: AUC={first_leg_auc:.4f} (n={first_idx.sum():,})")
    print(f"  Non-first-leg:     AUC={non_first_leg_auc:.4f} (n={non_first_idx.sum():,})")

    return {
        'first_leg_auc': float(first_leg_auc),
        'non_first_leg_auc': float(non_first_leg_auc),
        'first_leg_count': int(first_idx.sum()),
        'non_first_leg_count': int(non_first_idx.sum()),
        'first_leg_delay_rate': float(y_test[first_idx].mean()),
        'non_first_leg_delay_rate': float(y_test[non_first_idx].mean()),
    }


def compute_network_metrics(months=None, year=2024):
    """
    Compute graph-theoretic network centrality metrics for airports.

    Builds a directed weighted graph from flight routes and computes:
    - Degree centrality
    - Betweenness centrality
    - PageRank
    - Weighted in/out-degree (by flight volume)

    This addresses review Scope vs Framing #3 (no network analysis).

    Returns
    -------
    dict with keys:
        airport_metrics : pd.DataFrame with columns [airport, degree_centrality,
            betweenness_centrality, pagerank, weighted_in_degree, weighted_out_degree]
        graph_stats : dict with n_nodes, n_edges, density, etc.
    """
    import networkx as nx

    if months is None:
        months = [1]

    df = load_clean(year, months)

    # Build weighted directed graph: edge weight = number of flights
    route_counts = df.groupby(['Origin', 'Dest']).size().reset_index(name='weight')

    G = nx.DiGraph()
    for _, row in route_counts.iterrows():
        G.add_edge(row['Origin'], row['Dest'], weight=row['weight'])

    # Compute centrality metrics
    degree_cent = nx.degree_centrality(G)
    betweenness = nx.betweenness_centrality(G, weight='weight', k=min(100, len(G.nodes)))
    pagerank = nx.pagerank(G, weight='weight')

    # Weighted degree
    weighted_in = dict(G.in_degree(weight='weight'))
    weighted_out = dict(G.out_degree(weight='weight'))

    airports = list(G.nodes)
    metrics_df = pd.DataFrame({
        'airport': airports,
        'degree_centrality': [degree_cent.get(a, 0) for a in airports],
        'betweenness_centrality': [betweenness.get(a, 0) for a in airports],
        'pagerank': [pagerank.get(a, 0) for a in airports],
        'weighted_in_degree': [weighted_in.get(a, 0) for a in airports],
        'weighted_out_degree': [weighted_out.get(a, 0) for a in airports],
    })

    # Sort by degree centrality
    metrics_df = metrics_df.sort_values('degree_centrality', ascending=False).reset_index(drop=True)

    graph_stats = {
        'n_nodes': G.number_of_nodes(),
        'n_edges': G.number_of_edges(),
        'density': nx.density(G),
        'avg_clustering': nx.average_clustering(G.to_undirected()),
    }

    print(f"Network: {graph_stats['n_nodes']} airports, {graph_stats['n_edges']} routes")
    print(f"  Density: {graph_stats['density']:.4f}")
    print(f"  Top 5 by degree centrality: {metrics_df.head()['airport'].tolist()}")

    return {
        'airport_metrics': metrics_df,
        'graph_stats': graph_stats,
    }


def calibration_analysis(months=None, holdout_months=None, year=2024, n_bins=10):
    """
    Compute calibration statistics for the binary delay classifier.

    Produces reliability diagram data and Brier score.
    Addresses review Missing Experiment #2.

    Returns
    -------
    dict with keys:
        calibration_bins : pd.DataFrame with columns [bin_center, mean_predicted,
            mean_actual, count]
        brier_score : float
        expected_calibration_error : float (ECE)
    """
    from xgboost import XGBClassifier
    from sklearn.metrics import brier_score_loss

    if months is None:
        months = [1, 2, 3]
    if holdout_months is None:
        holdout_months = [4]

    # Train
    df_train = prepare_enhanced_data(year, months)
    feature_cols = get_enhanced_feature_columns()
    feature_cols = [c for c in feature_cols if c in df_train.columns]

    X_train = df_train[feature_cols].fillna(-999)
    y_train = make_target(df_train)

    model = XGBClassifier(
        n_estimators=300, max_depth=6, learning_rate=0.1,
        subsample=0.8, colsample_bytree=0.8,
        eval_metric='logloss', verbosity=0, n_jobs=-1,
        tree_method='hist',
    )
    try:
        model.set_params(device='cuda')
        model.fit(X_train, y_train)
    except Exception:
        model.set_params(device='cpu')
        model.fit(X_train, y_train)

    # Predict on holdout
    df_test = prepare_enhanced_data(year, holdout_months)
    X_test = df_test[feature_cols].fillna(-999)
    y_test = make_target(df_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    # Brier score
    brier = brier_score_loss(y_test, y_prob)

    # Calibration bins
    bins = np.linspace(0, 1, n_bins + 1)
    bin_centers = (bins[:-1] + bins[1:]) / 2
    cal_rows = []

    ece = 0.0
    for i in range(n_bins):
        mask = (y_prob >= bins[i]) & (y_prob < bins[i + 1])
        if mask.sum() > 0:
            mean_pred = y_prob[mask].mean()
            mean_actual = y_test.values[mask].mean()
            count = int(mask.sum())
            cal_rows.append({
                'bin_center': bin_centers[i],
                'mean_predicted': mean_pred,
                'mean_actual': mean_actual,
                'count': count,
            })
            ece += abs(mean_pred - mean_actual) * count / len(y_test)

    cal_df = pd.DataFrame(cal_rows)

    print(f"  Brier score: {brier:.4f}")
    print(f"  Expected calibration error (ECE): {ece:.4f}")

    return {
        'calibration_bins': cal_df,
        'brier_score': float(brier),
        'expected_calibration_error': float(ece),
    }


def run_all_review_experiments():
    """Run all experiments needed for the review response."""
    print("=" * 60)
    print("REVIEW EXPERIMENT 1: SHAP Analysis")
    print("=" * 60)
    shap_result = compute_shap_values(months=[1, 2, 3], sample_size=20000)
    mean_abs = shap_result['mean_abs_shap']
    sorted_feats = sorted(mean_abs.items(), key=lambda x: -x[1])
    total_shap = sum(v for _, v in sorted_feats)
    print("\nTop 15 features by mean |SHAP|:")
    for f, v in sorted_feats[:15]:
        pct = 100 * v / total_shap
        label = shap_result['label_map'].get(f, f)
        print(f"  {label:35s}: {v:.4f} ({pct:.1f}%)")

    # Sum rotation features
    rotation_features = {
        'prev_delay_x_buffer', 'log_prev_delay', 'prior_flight_arr_delay',
        'turnaround_time', 'buffer_over_min', 'prior_flight_dep_delay',
        'cumulative_delay', 'prior_flight_late_aircraft',
        'carrier_buffer_factor',
    }
    rotation_shap = sum(v for f, v in sorted_feats if f in rotation_features)
    print(f"\nTotal rotation-chain SHAP: {100 * rotation_shap / total_shap:.1f}%")

    print("\n" + "=" * 60)
    print("REVIEW EXPERIMENT 2: Calibration Analysis")
    print("=" * 60)
    cal_result = calibration_analysis(months=[1, 2, 3], holdout_months=[4])

    print("\n" + "=" * 60)
    print("REVIEW EXPERIMENT 3: Temporal Robustness (Monthly AUC)")
    print("=" * 60)
    temporal_result = monthly_auc_stability(
        train_months=[1, 2, 3], test_months=[4, 5, 6]
    )
    print(f"  Mean AUC: {temporal_result['mean_auc']:.4f} +/- {temporal_result['std_auc']:.4f}")

    print("\n" + "=" * 60)
    print("REVIEW EXPERIMENT 4: First-Leg-of-Day Accuracy")
    print("=" * 60)
    first_leg_result = first_leg_accuracy(months=[1, 2, 3], holdout_months=[4])

    print("\n" + "=" * 60)
    print("REVIEW EXPERIMENT 5: Network Centrality Metrics")
    print("=" * 60)
    network_result = compute_network_metrics(months=[1, 2, 3, 4, 5, 6])
    print("\nTop 10 airports by betweenness centrality:")
    top_bc = network_result['airport_metrics'].nlargest(10, 'betweenness_centrality')
    for _, row in top_bc.iterrows():
        print(f"  {row['airport']:5s}: betweenness={row['betweenness_centrality']:.4f}, "
              f"pagerank={row['pagerank']:.4f}")

    print("\n" + "=" * 60)
    print("REVIEW EXPERIMENT 6: SHAP Summary Plot")
    print("=" * 60)
    fig, ax = plot_shap_summary(months=[1, 2, 3], sample_size=20000)
    outdir = os.path.join(os.path.dirname(__file__), 'plots')
    os.makedirs(outdir, exist_ok=True)
    fig.savefig(os.path.join(outdir, 'shap_importance.png'))
    plt.close(fig)
    print("  Saved: plots/shap_importance.png")

    return {
        'shap': shap_result,
        'calibration': cal_result,
        'temporal': temporal_result,
        'first_leg': first_leg_result,
        'network': network_result,
    }


if __name__ == '__main__':
    results = run_all_review_experiments()
