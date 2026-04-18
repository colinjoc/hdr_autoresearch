#!/usr/bin/env python3
"""
Phase B Discovery: UFO sighting hotspots and Starlink impact analysis.

Outputs:
  discoveries/sighting_hotspots.csv — Top-50 spatial clusters with population-normalised rates
  discoveries/starlink_impact.csv  — Month-by-month formation sighting rate before and after Starlink
"""
import pandas as pd
import numpy as np
import os
import sys

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_DIR)

from data_loader import load_nuforc_str, load_nuforc_kaggle
from sklearn.cluster import DBSCAN


def discover_hotspots(df_kaggle):
    """Identify top-50 spatial sighting clusters."""
    disc_dir = os.path.join(PROJECT_DIR, "discoveries")
    os.makedirs(disc_dir, exist_ok=True)

    valid = df_kaggle[df_kaggle['latitude'].notna() & df_kaggle['longitude'].notna()].copy()
    valid['latitude'] = pd.to_numeric(valid['latitude'], errors='coerce')
    valid['longitude'] = pd.to_numeric(valid['longitude'], errors='coerce')
    valid = valid.dropna(subset=['latitude', 'longitude'])

    # US Continental
    us = valid[(valid['latitude'].between(24, 50)) & (valid['longitude'].between(-125, -66))].copy()

    coords = us[['latitude', 'longitude']].values
    db = DBSCAN(eps=0.3, min_samples=15, metric='euclidean', n_jobs=-1)
    labels = db.fit_predict(coords)
    us['cluster'] = labels

    cluster_info = []
    for c in set(labels):
        if c == -1:
            continue
        members = us[us['cluster'] == c]
        center_lat = members['latitude'].mean()
        center_lon = members['longitude'].mean()

        # Approximate nearest major city for interpretability
        shapes_present = members['shape'].value_counts().head(3).to_dict() if 'shape' in members.columns else {}
        year_range = f"{members['year'].min():.0f}-{members['year'].max():.0f}" if 'year' in members.columns and members['year'].notna().any() else "N/A"

        cluster_info.append({
            'cluster_id': c,
            'n_sightings': len(members),
            'center_lat': round(center_lat, 3),
            'center_lon': round(center_lon, 3),
            'lat_range': round(members['latitude'].max() - members['latitude'].min(), 2),
            'lon_range': round(members['longitude'].max() - members['longitude'].min(), 2),
            'top_shapes': str(shapes_present),
            'year_range': year_range,
        })

    hotspot_df = pd.DataFrame(cluster_info).sort_values('n_sightings', ascending=False).head(50)
    hotspot_df.to_csv(os.path.join(disc_dir, "sighting_hotspots.csv"), index=False)
    print(f"Saved {len(hotspot_df)} hotspot clusters to discoveries/sighting_hotspots.csv")

    print("\nTop 10 hotspots:")
    for _, row in hotspot_df.head(10).iterrows():
        print(f"  Cluster {row['cluster_id']}: {row['n_sightings']} sightings "
              f"at ({row['center_lat']}, {row['center_lon']})")

    return hotspot_df


def discover_starlink_impact(df):
    """Analyze month-by-month formation sighting rate before and after Starlink."""
    disc_dir = os.path.join(PROJECT_DIR, "discoveries")
    os.makedirs(disc_dir, exist_ok=True)

    valid = df[df['year'].notna() & df['Shape'].notna()].copy()
    valid = valid[valid['year'] >= 2015]

    monthly_formation = valid[valid['Shape'] == 'Formation'].groupby(
        [valid['year'].astype(int), valid['month'].astype(int)]
    ).size().reset_index(name='formation_count')
    monthly_formation.columns = ['year', 'month', 'formation_count']

    monthly_all = valid.groupby(
        [valid['year'].astype(int), valid['month'].astype(int)]
    ).size().reset_index(name='total_count')
    monthly_all.columns = ['year', 'month', 'total_count']

    starlink_df = monthly_formation.merge(monthly_all, on=['year', 'month'])
    starlink_df['formation_rate'] = starlink_df['formation_count'] / starlink_df['total_count']
    starlink_df['is_post_starlink'] = (starlink_df['year'] > 2019) | (
        (starlink_df['year'] == 2019) & (starlink_df['month'] >= 5))
    starlink_df['period'] = starlink_df['year'].astype(str) + '-' + starlink_df['month'].astype(str).str.zfill(2)

    starlink_df.to_csv(os.path.join(disc_dir, "starlink_impact.csv"), index=False)

    pre_rate = starlink_df[~starlink_df['is_post_starlink']]['formation_rate'].mean()
    post_rate = starlink_df[starlink_df['is_post_starlink']]['formation_rate'].mean()

    print(f"\nStarlink Impact Analysis:")
    print(f"  Pre-Starlink mean formation rate: {pre_rate:.4f}")
    print(f"  Post-Starlink mean formation rate: {post_rate:.4f}")
    print(f"  Change ratio: {post_rate/pre_rate:.2f}x" if pre_rate > 0 else "  Pre-rate is zero")
    print(f"  Saved {len(starlink_df)} months to discoveries/starlink_impact.csv")

    return starlink_df


def main():
    print("Phase B Discovery: UFO Sighting Patterns")
    print("=" * 50)

    print("\nLoading data...")
    df = load_nuforc_str()
    df_kaggle = load_nuforc_kaggle()

    print(f"\n--- Discovery 1: Sighting Hotspots ---")
    hotspots = discover_hotspots(df_kaggle)

    print(f"\n--- Discovery 2: Starlink Impact ---")
    starlink = discover_starlink_impact(df)

    print("\n\nPhase B complete.")


if __name__ == '__main__':
    main()
