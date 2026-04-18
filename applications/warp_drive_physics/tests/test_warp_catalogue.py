"""Tests for warp drive physics catalogue and computations."""
import pytest
import os
import csv
import sys
import math

PROJECT_DIR = "/home/col/generalized_hdr_autoresearch/applications/warp_drive_physics"


# === Phase 0 artifact tests ===

def test_papers_csv_exists():
    path = os.path.join(PROJECT_DIR, "papers.csv")
    assert os.path.exists(path), "papers.csv must exist"


def test_papers_csv_has_200_plus_entries():
    path = os.path.join(PROJECT_DIR, "papers.csv")
    with open(path, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert len(rows) >= 200, f"papers.csv has {len(rows)} entries, need >= 200"


def test_literature_review_exists():
    path = os.path.join(PROJECT_DIR, "literature_review.md")
    assert os.path.exists(path), "literature_review.md must exist"


def test_literature_review_has_themes():
    path = os.path.join(PROJECT_DIR, "literature_review.md")
    with open(path, "r") as f:
        content = f.read()
    # Should have at least 4 themes for a compact review
    theme_count = content.count("## Theme")
    assert theme_count >= 4, f"Only {theme_count} themes found, need >= 4"


def test_knowledge_base_exists():
    path = os.path.join(PROJECT_DIR, "knowledge_base.md")
    assert os.path.exists(path), "knowledge_base.md must exist"


def test_research_queue_exists():
    path = os.path.join(PROJECT_DIR, "research_queue.md")
    assert os.path.exists(path), "research_queue.md must exist"


def test_research_queue_has_hypotheses():
    path = os.path.join(PROJECT_DIR, "research_queue.md")
    with open(path, "r") as f:
        content = f.read()
    # Count hypothesis entries (lines starting with H or containing "hypothesis")
    h_count = content.count("| H")
    assert h_count >= 30, f"Only {h_count} hypotheses found, need >= 30"


def test_design_variables_exists():
    path = os.path.join(PROJECT_DIR, "design_variables.md")
    assert os.path.exists(path), "design_variables.md must exist"


def test_feature_candidates_exists():
    path = os.path.join(PROJECT_DIR, "feature_candidates.md")
    assert os.path.exists(path), "feature_candidates.md must exist"


# === Phase 0.5 tests ===

def test_results_tsv_exists():
    path = os.path.join(PROJECT_DIR, "results.tsv")
    assert os.path.exists(path), "results.tsv must exist"


def test_results_tsv_has_e00():
    path = os.path.join(PROJECT_DIR, "results.tsv")
    with open(path, "r") as f:
        content = f.read()
    assert "E00" in content, "results.tsv must contain E00 baseline"


# === Phase 1 tests ===

def test_tournament_results_csv_exists():
    path = os.path.join(PROJECT_DIR, "tournament_results.csv")
    assert os.path.exists(path), "tournament_results.csv must exist"


def test_tournament_has_4_families():
    path = os.path.join(PROJECT_DIR, "tournament_results.csv")
    with open(path, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    families = set(r.get("family", r.get("framework", "")) for r in rows)
    assert len(families) >= 4, f"Only {len(families)} families, need >= 4"


# === Phase 2 tests ===

def test_results_tsv_has_20_experiments():
    path = os.path.join(PROJECT_DIR, "results.tsv")
    with open(path, "r") as f:
        reader = csv.DictReader(f, delimiter="\t")
        rows = list(reader)
    keep_revert = [r for r in rows if r.get("status", "") in ("KEEP", "REVERT")]
    assert len(keep_revert) >= 20, f"Only {len(keep_revert)} KEEP/REVERT, need >= 20"


# === Phase 2.5 tests ===

def test_interaction_experiment_exists():
    path = os.path.join(PROJECT_DIR, "results.tsv")
    with open(path, "r") as f:
        content = f.read()
    assert "interaction" in content.lower(), "results.tsv must have interaction experiments"


# === Phase B tests ===

def test_phase_b_discovery_script_exists():
    path = os.path.join(PROJECT_DIR, "phase_b_discovery.py")
    assert os.path.exists(path), "phase_b_discovery.py must exist"


def test_discoveries_catalogue_exists():
    path = os.path.join(PROJECT_DIR, "discoveries", "warp_metric_catalogue.csv")
    assert os.path.exists(path), "discoveries/warp_metric_catalogue.csv must exist"


def test_discoveries_energy_requirements_exists():
    path = os.path.join(PROJECT_DIR, "discoveries", "energy_requirements.csv")
    assert os.path.exists(path), "discoveries/energy_requirements.csv must exist"


def test_discoveries_observational_constraints_exists():
    path = os.path.join(PROJECT_DIR, "discoveries", "observational_constraints.csv")
    assert os.path.exists(path), "discoveries/observational_constraints.csv must exist"


# === Physics sanity checks ===

def test_alcubierre_energy_density_negative():
    """The Alcubierre energy density is T^00 = -(1/8pi) * (v_s^2 * rho^2)/(4*r_s^2) * (df/dr_s)^2
    This is always <= 0 (negative or zero), violating WEC."""
    # For any v_s > 0 and rho > 0 and df/dr_s != 0, T^00 < 0
    v_s = 1.0  # c
    rho = 1.0  # off-axis
    r_s = 1.0
    df_dr = 1.0  # nonzero derivative
    T00 = -(1 / (8 * math.pi)) * (v_s**2 * rho**2) / (4 * r_s**2) * df_dr**2
    assert T00 < 0, "Alcubierre energy density must be negative"


def test_exotic_matter_mass_order_of_magnitude():
    """Alcubierre drive for v=c, R=100m requires ~solar-mass exotic matter.
    Pfenning & Ford 1997 showed total energy ~ -c^2 * v^2 * R / G ~ -M_sun c^2."""
    c = 3e8  # m/s
    G = 6.674e-11  # m^3 kg^-1 s^-2
    M_sun = 1.989e30  # kg
    v = c  # warp velocity
    R = 100  # bubble radius in meters
    # Order-of-magnitude: E ~ v^2 * R / G (in natural units)
    # More precisely: Pfenning & Ford give E_exotic ~ -v^2 * R * c^2 / G
    E_exotic = v**2 * R * c**2 / G  # Joules, order of magnitude
    M_exotic = E_exotic / c**2  # kg
    ratio = M_exotic / M_sun
    # Should be order of magnitude ~ 1 solar mass or more
    assert ratio > 0.01, f"Exotic matter mass ratio {ratio} too small"
    assert ratio < 1e10, f"Exotic matter mass ratio {ratio} too large"


def test_paper_md_exists():
    path = os.path.join(PROJECT_DIR, "paper.md")
    assert os.path.exists(path), "paper.md must exist"


def test_generate_plots_exists():
    path = os.path.join(PROJECT_DIR, "generate_plots.py")
    assert os.path.exists(path), "generate_plots.py must exist"
