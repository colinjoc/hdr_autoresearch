"""TDD tests for IE Housing Pipeline E2E synthesis project.

Sanity checks on the overall yield rate and pipeline stage metrics.
"""
import subprocess, sys, os, pathlib

PROJECT = pathlib.Path(__file__).resolve().parent.parent

def test_analysis_runs():
    """The analysis script must execute without error."""
    result = subprocess.run(
        [sys.executable, str(PROJECT / "analysis.py")],
        capture_output=True, text=True, timeout=600,
        cwd=str(PROJECT),
    )
    assert result.returncode == 0, f"analysis.py failed:\n{result.stderr[-3000:]}"

def test_results_tsv_exists():
    """results.tsv must exist after running analysis."""
    assert (PROJECT / "results.tsv").exists(), "results.tsv not found"

def test_overall_yield_sanity():
    """Overall yield (CCC-completions / permissions) must be 30%-90%."""
    import pandas as pd
    df = pd.read_csv(PROJECT / "results.tsv", sep="\t")
    e00 = df[df["experiment_id"] == "E00"]
    assert len(e00) == 1, f"Expected 1 E00 row, got {len(e00)}"
    val = float(e00.iloc[0]["value"])
    assert 0.30 <= val <= 0.90, f"Yield {val:.3f} outside [0.30, 0.90]"

def test_tournament_has_four_families():
    """Tournament must have >= 4 families."""
    import pandas as pd
    df = pd.read_csv(PROJECT / "results.tsv", sep="\t")
    tourney = df[df["experiment_id"].str.startswith("T")]
    assert len(tourney) >= 4, f"Only {len(tourney)} tournament rows"

def test_twenty_experiments():
    """Phase 2 must have >= 20 experiments (KEEP or REVERT)."""
    import pandas as pd
    df = pd.read_csv(PROJECT / "results.tsv", sep="\t")
    phase2 = df[df["status"].isin(["KEEP", "REVERT"])]
    assert len(phase2) >= 20, f"Only {len(phase2)} KEEP/REVERT rows"

def test_interaction_experiments():
    """Phase 2.5 must have >= 1 interaction experiment."""
    import pandas as pd
    df = pd.read_csv(PROJECT / "results.tsv", sep="\t")
    interactions = df[df["interaction"].astype(str).str.lower() == "true"]
    assert len(interactions) >= 1, f"No interaction experiments found"

def test_discoveries_exist():
    """Phase B discovery CSVs must exist."""
    disc = PROJECT / "discoveries"
    assert (disc / "pipeline_yield_by_stratum.csv").exists()
    assert (disc / "permissions_needed_for_hfa.csv").exists()

def test_phase_b_yield_stratum_sane():
    """Phase B yield strata must have rates in [0, 1]."""
    import pandas as pd
    df = pd.read_csv(PROJECT / "discoveries" / "pipeline_yield_by_stratum.csv")
    assert "yield_rate" in df.columns
    assert (df["yield_rate"] >= 0).all() and (df["yield_rate"] <= 1).all()

def test_paper_exists():
    """paper.md must exist."""
    assert (PROJECT / "paper.md").exists(), "paper.md not found"

def test_mandatory_phase0_artifacts():
    """Phase 0 artifacts must exist."""
    for f in ["papers.csv", "literature_review.md", "research_queue.md",
              "knowledge_base.md", "feature_candidates.md", "design_variables.md"]:
        assert (PROJECT / f).exists(), f"{f} not found"

def test_data_sources_md():
    """data_sources.md must exist."""
    assert (PROJECT / "data_sources.md").exists()

def test_tournament_results_csv():
    """tournament_results.csv must exist."""
    assert (PROJECT / "tournament_results.csv").exists()
