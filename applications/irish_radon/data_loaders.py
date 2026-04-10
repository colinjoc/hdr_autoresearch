"""Data loaders for Irish radon prediction.

Loads real EPA and GSI data, performs spatial joins, and produces
a clean feature matrix for modelling.

Data sources (all real, publicly available):
- EPA Radon Grid Map: 10km grid with % homes > 200 Bq/m3
- GSI Bedrock Geology 500K: lithology + age
- EPA National Subsoils: quaternary sediment types
- EPA County Boundaries: for spatial CV grouping
- EPA County Radon Stats: from 63,914 home measurements
- GSI Tellus Airborne Radiometrics: eU, eTh, K GeoTIFF rasters
"""
import os
import json
import warnings
from collections import Counter

import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.transform import rowcol
from shapely.geometry import shape, Point

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def load_radon_grid() -> gpd.GeoDataFrame:
    """Load EPA 10km radon grid map.

    Returns GeoDataFrame with columns:
    - pct_above_rl: % homes above 200 Bq/m3 reference level
    - centroid_x, centroid_y: grid square centroid in ITM (EPSG:2157)
    - geometry: grid square polygon
    """
    path = os.path.join(DATA_DIR, "epa_radon", "radon_grid_map.geojson")
    with open(path) as f:
        data = json.load(f)

    records = []
    geometries = []
    for feat in data["features"]:
        props = feat["properties"]
        pct = props["PERCENT_"]
        geom = shape(feat["geometry"])
        records.append({
            "pct_above_rl": pct,
            "radon_text": props.get("RadonText", ""),
        })
        geometries.append(geom)

    gdf = gpd.GeoDataFrame(records, geometry=geometries)
    # The EPA data uses Irish National Grid (TM75, EPSG:29902) based on coordinate ranges
    gdf = gdf.set_crs("EPSG:29902")

    # Filter invalid values (-999 = missing)
    gdf = gdf[gdf["pct_above_rl"] >= 0].copy()
    gdf = gdf[gdf["pct_above_rl"] <= 100].copy()

    # Compute centroids
    gdf["centroid_x"] = gdf.geometry.centroid.x
    gdf["centroid_y"] = gdf.geometry.centroid.y

    gdf = gdf.reset_index(drop=True)
    return gdf


def join_bedrock_features(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Spatially join bedrock geology to radon grid squares.

    For each grid square, finds the dominant (largest area) bedrock unit
    and age bracket from the GSI 500K bedrock geology.
    """
    shp_path = os.path.join(
        DATA_DIR, "gsi_bedrock",
        "IE_GSI_GSNI_Bedrock_Geology_500k_IE32_ITM_MS.shp"
    )
    bedrock = gpd.read_file(shp_path)
    # Bedrock is in EPSG:2157 (ITM). Reproject radon grid to match.
    gdf_itm = gdf.to_crs("EPSG:2157")

    # Spatial overlay to find intersections
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        overlay = gpd.overlay(gdf_itm, bedrock, how="intersection")

    # Compute area of each intersection
    overlay["_area"] = overlay.geometry.area

    # For each radon grid square, find dominant bedrock unit by area
    dominant_unit = []
    dominant_age = []
    for idx in range(len(gdf)):
        mask = overlay.index.isin(
            overlay[overlay["pct_above_rl"] == gdf.iloc[idx]["pct_above_rl"]].index
        )
        # Use centroid matching instead
        pass

    # Simpler approach: join using centroid
    centroids = gdf_itm.copy()
    centroids["geometry"] = centroids.geometry.centroid

    joined = gpd.sjoin(centroids, bedrock, how="left", predicate="within")

    # Handle duplicates (centroid in multiple polygons) by taking first
    joined = joined[~joined.index.duplicated(keep="first")]

    gdf = gdf.copy()
    gdf["bedrock_dominant_unit"] = joined["UNITNAME"].values
    gdf["bedrock_dominant_age"] = joined["AGEBRACKET"].values

    # Extract simplified bedrock features
    gdf["bedrock_is_granite"] = gdf["bedrock_dominant_unit"].str.contains(
        "ranit|Granit", case=False, na=False
    ).astype(int)
    gdf["bedrock_is_limestone"] = gdf["bedrock_dominant_unit"].str.contains(
        "imestone|Limestone", case=False, na=False
    ).astype(int)
    gdf["bedrock_is_shale"] = gdf["bedrock_dominant_unit"].str.contains(
        "hale|Shale|slate|Slate|mudstone|Mudstone", case=False, na=False
    ).astype(int)
    gdf["bedrock_is_sandstone"] = gdf["bedrock_dominant_unit"].str.contains(
        "andstone|Sandstone", case=False, na=False
    ).astype(int)
    gdf["bedrock_is_carboniferous"] = gdf["bedrock_dominant_age"].str.contains(
        "arboniferous", case=False, na=False
    ).astype(int)
    gdf["bedrock_is_devonian"] = gdf["bedrock_dominant_age"].str.contains(
        "evonian", case=False, na=False
    ).astype(int)
    gdf["bedrock_is_ordovician_silurian"] = gdf["bedrock_dominant_age"].str.contains(
        "rdovician|ilurian", case=False, na=False
    ).astype(int)

    return gdf


def join_subsoil_features(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Spatially join subsoil/quaternary geology to radon grid squares."""
    # Try merged file first (original + till), fall back to original
    merged_path = os.path.join(DATA_DIR, "gsi_quaternary", "subsoils_merged.geojson")
    orig_path = os.path.join(DATA_DIR, "gsi_quaternary", "subsoils.geojson")
    path = merged_path if os.path.exists(merged_path) else orig_path
    if not os.path.exists(path):
        gdf = gdf.copy()
        gdf["subsoil_dominant_category"] = np.nan
        return gdf

    subsoils = gpd.read_file(path)
    # Subsoils from EPA WFS are in EPSG:29902
    if subsoils.crs is None:
        subsoils = subsoils.set_crs("EPSG:29902")

    gdf_proj = gdf.copy()
    if gdf_proj.crs != subsoils.crs:
        gdf_proj = gdf_proj.to_crs(subsoils.crs)

    # Use centroid join
    centroids = gdf_proj.copy()
    centroids["geometry"] = centroids.geometry.centroid

    joined = gpd.sjoin(centroids, subsoils[["CATEGORY", "DESCRIPT", "PAR_MAT", "TEXTURE", "geometry"]],
                       how="left", predicate="within")
    joined = joined[~joined.index.duplicated(keep="first")]

    gdf = gdf.copy()
    gdf["subsoil_dominant_category"] = joined["CATEGORY"].values
    gdf["subsoil_dominant_descript"] = joined["DESCRIPT"].values
    gdf["subsoil_dominant_parmat"] = joined["PAR_MAT"].values
    gdf["subsoil_dominant_texture"] = joined.get("TEXTURE", pd.Series([np.nan]*len(joined))).values

    # Binary subsoil features
    gdf["subsoil_is_till"] = gdf["subsoil_dominant_category"].str.contains(
        "Till", case=False, na=False
    ).astype(int)
    gdf["subsoil_is_peat"] = gdf["subsoil_dominant_category"].str.contains(
        "Peat", case=False, na=False
    ).astype(int)
    gdf["subsoil_is_alluvium"] = gdf["subsoil_dominant_category"].str.contains(
        "Alluvium", case=False, na=False
    ).astype(int)
    gdf["subsoil_is_gravel"] = gdf["subsoil_dominant_category"].str.contains(
        "Gravel|Sand", case=False, na=False
    ).astype(int)

    # Till-specific features (till description reveals parent rock, important for radon)
    desc = gdf["subsoil_dominant_descript"].fillna("")
    gdf["till_is_granite"] = desc.str.contains("Granite", case=False).astype(int)
    gdf["till_is_limestone"] = desc.str.contains("Limestone", case=False).astype(int)
    gdf["till_is_shale"] = desc.str.contains("Shale", case=False).astype(int)
    gdf["till_is_sandstone"] = desc.str.contains("Sandstone", case=False).astype(int)
    gdf["till_is_metamorphic"] = desc.str.contains("Metamorphic", case=False).astype(int)

    return gdf


def assign_counties(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Assign each grid square to a county for spatial CV."""
    path = os.path.join(DATA_DIR, "county_boundaries", "counties.geojson")
    counties = gpd.read_file(path)

    if counties.crs is None:
        counties = counties.set_crs("EPSG:29902")

    gdf_proj = gdf.copy()
    if gdf_proj.crs != counties.crs:
        gdf_proj = gdf_proj.to_crs(counties.crs)

    centroids = gdf_proj.copy()
    centroids["geometry"] = centroids.geometry.centroid

    joined = gpd.sjoin(centroids, counties[["Label", "geometry"]],
                       how="left", predicate="within")
    joined = joined[~joined.index.duplicated(keep="first")]

    gdf = gdf.copy()
    gdf["county"] = joined["Label"].values

    return gdf


def sample_tellus_radiometrics(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Sample Tellus airborne radiometric rasters at grid square centroids.

    Adds eU_mean, eTh_mean, K_mean (and derived features) by sampling
    the GSI Tellus Merge 2022 GeoTIFFs in ITM (EPSG:2157).

    For each 10km grid square, samples at the centroid and also at
    a 3x3 sub-grid to compute statistics (mean, std, p90).
    """
    tellus_dir = os.path.join(DATA_DIR, "gsi_tellus", "RAD_MERGE_2022", "TIFF")
    eu_path = os.path.join(tellus_dir, "TELLUS_RAD_U_MERGE_2022_COAST.tif")
    eth_path = os.path.join(tellus_dir, "TELLUS_RAD_TH_MERGE_2022_COAST.tif")
    k_path = os.path.join(tellus_dir, "TELLUS_RAD_K_MERGE_2022_COAST.tif")

    if not all(os.path.exists(p) for p in [eu_path, eth_path, k_path]):
        warnings.warn("Tellus GeoTIFFs not found; skipping radiometric features.")
        gdf = gdf.copy()
        for col in ["eU_mean", "eTh_mean", "K_mean", "eU_std", "eU_p90",
                     "eU_eTh_ratio", "total_dose_rate", "log_eU"]:
            gdf[col] = np.nan
        return gdf

    # Reproject centroids to ITM (EPSG:2157) for sampling
    gdf_itm = gdf.to_crs("EPSG:2157")

    def _sample_raster_pseudo(raster_path, geometries):
        """Sample RGB raster, convert to pseudo-radiometric using R-B.

        The Tellus GeoTIFFs are color-mapped RGB images (uint8 x 3 bands).
        The color ramp goes from blue (low value, R=0 B=247) to red
        (high value, R=247 B=0). The R-B difference provides a monotonic
        pseudo-radiometric index from -247 to +247. We rescale to 0-1.
        White (255,255,255) pixels are sea/nodata.
        """
        with rasterio.open(raster_path) as src:
            r_band = src.read(1).astype(np.float32)
            b_band = src.read(3).astype(np.float32)
            g_band = src.read(2).astype(np.float32)
            transform = src.transform

            # Pseudo-value: (R - B) rescaled to [0, 1]
            # White pixels (R=G=B=255) are nodata (sea)
            is_white = (r_band == 255) & (g_band == 255) & (b_band == 255)
            pseudo = (r_band - b_band + 247.0) / 494.0  # scale to [0, 1]
            pseudo[is_white] = np.nan

            means = []
            stds = []
            p90s = []
            for geom in geometries:
                cx, cy = geom.centroid.x, geom.centroid.y
                # Sample at 5x5 sub-grid (offsets of ~2km around centroid)
                offsets = [-4000, -2000, 0, 2000, 4000]
                vals = []
                for dx in offsets:
                    for dy in offsets:
                        try:
                            row, col = rowcol(transform, cx + dx, cy + dy)
                            if 0 <= row < pseudo.shape[0] and 0 <= col < pseudo.shape[1]:
                                v = pseudo[row, col]
                                if not np.isnan(v):
                                    vals.append(float(v))
                        except Exception:
                            continue
                if vals:
                    means.append(np.mean(vals))
                    stds.append(np.std(vals))
                    p90s.append(np.percentile(vals, 90))
                else:
                    means.append(np.nan)
                    stds.append(np.nan)
                    p90s.append(np.nan)
        return means, stds, p90s

    eu_mean, eu_std, eu_p90 = _sample_raster_pseudo(eu_path, gdf_itm.geometry)
    eth_mean, _, _ = _sample_raster_pseudo(eth_path, gdf_itm.geometry)
    k_mean, _, _ = _sample_raster_pseudo(k_path, gdf_itm.geometry)

    gdf = gdf.copy()
    gdf["eU_mean"] = eu_mean
    gdf["eU_std"] = eu_std
    gdf["eU_p90"] = eu_p90
    gdf["eTh_mean"] = eth_mean
    gdf["K_mean"] = k_mean

    # Derived features
    eu = gdf["eU_mean"]
    eth = gdf["eTh_mean"]
    k = gdf["K_mean"]
    gdf["eU_eTh_ratio"] = np.where(eth > 0, eu / eth, np.nan)
    gdf["total_dose_rate"] = 0.0417 * k + 0.604 * eu + 0.310 * eth
    gdf["log_eU"] = np.log1p(np.clip(eu, 0, None))

    return gdf


def load_county_radon_stats() -> pd.DataFrame:
    """Load county-level radon measurement statistics from EPA data.

    Source: EPA radon results by county (63,914 homes measured through Dec 2019).
    """
    # Hard-coded from EPA website - this IS the real data, just at county level
    data = [
        ("Carlow", 1364, 262, 18.8, 2300),
        ("Cavan", 509, 18, 3.5, 900),
        ("Clare", 4598, 599, 13.0, 3500),
        ("Cork", 6469, 820, 12.7, 4500),
        ("Donegal", 1784, 92, 5.2, 3400),
        ("Dublin", 4627, 256, 5.5, 1400),
        ("Galway", 8776, 1861, 21.2, 5200),
        ("Kerry", 4562, 770, 16.9, 49000),
        ("Kildare", 1600, 69, 4.3, 1100),
        ("Kilkenny", 1823, 242, 13.2, 2400),
        ("Laois", 659, 25, 3.8, 600),
        ("Leitrim", 462, 32, 6.9, 1600),
        ("Limerick", 1652, 123, 7.4, 1900),
        ("Longford", 354, 42, 11.9, 900),
        ("Louth", 1397, 141, 10.1, 1900),
        ("Mayo", 5076, 895, 17.7, 6200),
        ("Meath", 1250, 93, 7.4, 900),
        ("Monaghan", 372, 20, 5.4, 800),
        ("Offaly", 858, 20, 2.3, 800),
        ("Roscommon", 825, 93, 11.3, 1400),
        ("Sligo", 2698, 671, 24.9, 5600),
        ("Tipperary", 2907, 356, 12.3, 3400),
        ("Waterford", 2840, 561, 19.6, 9700),
        ("Westmeath", 965, 80, 8.3, 1100),
        ("Wexford", 2803, 446, 15.9, 4100),
        ("Wicklow", 2683, 435, 16.3, 16400),
    ]
    df = pd.DataFrame(data, columns=[
        "county", "homes_measured", "homes_above_rl", "pct_above_rl", "max_bqm3"
    ])
    return df


def build_dataset():
    """Build complete feature matrix, target, and group labels.

    Returns:
        X: feature DataFrame
        y: target Series (pct_above_rl)
        groups: county Series for spatial CV
    """
    # 1. Load radon grid
    gdf = load_radon_grid()

    # 2. Join bedrock
    gdf = join_bedrock_features(gdf)

    # 3. Join subsoils
    gdf = join_subsoil_features(gdf)

    # 3.5 Sample Tellus radiometrics
    gdf = sample_tellus_radiometrics(gdf)

    # 4. Assign counties
    gdf = assign_counties(gdf)

    # Note: county-level radon stats (homes_measured, max_bqm3) are NOT used
    # as features because they are derived from the target variable and would
    # constitute data leakage. They are available via load_county_radon_stats()
    # for analysis/reporting only.

    # 5.5 Add interaction features
    if "eU_mean" in gdf.columns and "bedrock_is_granite" in gdf.columns:
        gdf["eU_x_granite"] = gdf["eU_mean"] * gdf["bedrock_is_granite"]
        gdf["eU_x_limestone"] = gdf["eU_mean"] * gdf["bedrock_is_limestone"]
        gdf["eU_x_shale"] = gdf["eU_mean"] * gdf["bedrock_is_shale"]
        gdf["eU_x_peat"] = gdf["eU_mean"] * gdf["subsoil_is_peat"]
        gdf["eU_x_gravel"] = gdf["eU_mean"] * gdf["subsoil_is_gravel"]
        gdf["eU_x_till"] = gdf["eU_mean"] * gdf["subsoil_is_till"]
        gdf["granite_x_till"] = gdf["bedrock_is_granite"] * gdf["subsoil_is_till"]
        gdf["limestone_x_gravel"] = gdf["bedrock_is_limestone"] * gdf["subsoil_is_gravel"]

    # Define target
    y = gdf["pct_above_rl"].copy()

    # Define groups
    groups = gdf["county"].copy()

    # Define features (exclude target, text, geometry)
    drop_cols = [
        "pct_above_rl", "radon_text", "geometry",
        "county",  # used as group, not feature
        "bedrock_dominant_unit", "bedrock_dominant_age",  # categorical - use encoded versions
        "subsoil_dominant_category", "subsoil_dominant_descript",
        "subsoil_dominant_parmat", "subsoil_dominant_texture",
    ]

    # One-hot encode bedrock unit (top N most common)
    if "bedrock_dominant_unit" in gdf.columns:
        top_units = gdf["bedrock_dominant_unit"].value_counts().head(15).index
        for unit in top_units:
            safe_name = "bedrock_unit_" + str(unit).replace(" ", "_").replace(",", "")[:40]
            gdf[safe_name] = (gdf["bedrock_dominant_unit"] == unit).astype(int)

    if "bedrock_dominant_age" in gdf.columns:
        top_ages = gdf["bedrock_dominant_age"].value_counts().head(10).index
        for age in top_ages:
            safe_name = "bedrock_age_" + str(age).replace(" ", "_").replace(",", "")[:40]
            gdf[safe_name] = (gdf["bedrock_dominant_age"] == age).astype(int)

    X = gdf.drop(columns=[c for c in drop_cols if c in gdf.columns])

    # Drop rows where target or county is missing
    valid = y.notna() & groups.notna()
    X = X[valid].reset_index(drop=True)
    y = y[valid].reset_index(drop=True)
    groups = groups[valid].reset_index(drop=True)

    return X, y, groups
