"""Model for Irish radon prediction.

Predicts % homes above 200 Bq/m3 reference level per 10km grid square
from geological, geographic, subsoil, and Tellus radiometric features.

Best model: XGBoost with full feature set (interactions + one-hot bedrock).
Phase 1 tournament winner: XGBoost (MAE=6.58, HRA_F1=0.47)
Phase 2 final: XGBoost full (MAE=6.42, HRA_F1=0.47)
"""
from xgboost import XGBRegressor
from sklearn.linear_model import Ridge


# --- Feature sets ---

BASELINE_FEATURES = [
    # Tellus radiometric (pseudo-values from color-mapped GeoTIFFs)
    "eU_mean", "eTh_mean", "K_mean",
    # Geographic
    "centroid_x", "centroid_y",
    # Bedrock binary features
    "bedrock_is_granite", "bedrock_is_limestone",
    "bedrock_is_shale", "bedrock_is_sandstone",
    "bedrock_is_carboniferous", "bedrock_is_devonian",
    "bedrock_is_ordovician_silurian",
    # Subsoil binary features
    "subsoil_is_till", "subsoil_is_peat",
    "subsoil_is_alluvium", "subsoil_is_gravel",
    # Till-specific features
    "till_is_granite", "till_is_limestone",
    "till_is_shale", "till_is_sandstone", "till_is_metamorphic",
]

ENHANCED_FEATURES = BASELINE_FEATURES + [
    # Tellus derived
    "eU_std", "eU_p90", "eU_eTh_ratio",
    "total_dose_rate", "log_eU",
]

INTERACTION_FEATURES = ENHANCED_FEATURES + [
    "eU_x_granite", "eU_x_limestone", "eU_x_shale",
    "eU_x_peat", "eU_x_gravel", "eU_x_till",
    "granite_x_till", "limestone_x_gravel",
]

FULL_FEATURES = INTERACTION_FEATURES + [
    # One-hot bedrock units (top 15)
    "bedrock_unit_64_Marine_shelf_facies;_Limestone_&_calc",
    "bedrock_unit_54_Continental_redbed_facies;_Sandstone_",
    "bedrock_unit_71_Fluvio-deltaic_&_basinal_marine_(Turb",
    "bedrock_unit_65_Marine_basinal_facies_(Tobercolleen_&",
    "bedrock_unit_49_Deep_marine_turbidite_sequence;_Mudst",
    "bedrock_unit_8_Granite_granodiorite",
    "bedrock_unit_62_Waulsortian_mudbank;_Pale-grey_massiv",
    "bedrock_unit_61_Marine_shelf_&_ramp_facies;_Argillace",
    "bedrock_unit_35_Deep_marine;_Slate_schist_&_minor_gre",
    "bedrock_unit_27_Argyll_Group;_Psammitic_&_pelitic_sch",
    "bedrock_unit_53_Continental_redbed_facies;_Sandstone_",
    "bedrock_unit_57_Marine_(Cork_Group)_(extends_into_the",
    "bedrock_unit_40_Marine_to_fluvial;_Greywacke_shale_sa",
    "bedrock_unit_29_Southern_Highland_Group;_Pelitic_&_ps",
    "bedrock_unit_66_Marginal_marine_(Mullaghmore_Downpatr",
    # One-hot bedrock ages (top 10)
    "bedrock_age_Palaeozoic_Carboniferous_Mississippian",
    "bedrock_age_Palaeozoic_Upper_Devonian_-_Carboniferou",
    "bedrock_age_Neoproterozoic_Dalradian_Supergroup",
    "bedrock_age_Palaeozoic_Carboniferous_Pennsylvanian",
    "bedrock_age_Palaeozoic_Silurian",
    "bedrock_age_Caledonian_(Silurian_-_Devonian)",
    "bedrock_age_Palaeozoic_Lower_-_Middle_Ordovician",
    "bedrock_age_Palaeozoic_Middle_-_Upper_Ordovician",
    "bedrock_age_Palaeozoic_Middle_Devonian",
    "bedrock_age_Neoproterozoic_(-Cambrian)_Dalradian_Sup",
]


def build_model():
    """Return (model, feature_names) for the Ridge baseline."""
    return Ridge(alpha=1.0), BASELINE_FEATURES


def build_xgb_model():
    """Return (model, feature_names) for XGBoost baseline."""
    model = XGBRegressor(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
    )
    return model, BASELINE_FEATURES


def build_xgb_enhanced():
    """Return (model, feature_names) for XGBoost with Tellus-derived features."""
    model = XGBRegressor(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
    )
    return model, ENHANCED_FEATURES


def build_best_model():
    """Return (model, feature_names) for the best model (Phase 2 final).

    XGBoost with full features: interactions + one-hot bedrock units/ages.
    """
    model = XGBRegressor(
        n_estimators=500,
        max_depth=6,
        learning_rate=0.03,
        subsample=0.8,
        colsample_bytree=0.7,
        reg_alpha=0.1,
        reg_lambda=1.0,
        min_child_weight=3,
        random_state=42,
        n_jobs=-1,
    )
    return model, FULL_FEATURES
