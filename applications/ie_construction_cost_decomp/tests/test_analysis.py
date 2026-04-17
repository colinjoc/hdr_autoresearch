"""Tests for the analysis pipeline — TDD verification."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import pandas as pd
import numpy as np


PROJECT = Path(__file__).parent.parent


class TestResultsTSV:
    def test_exists(self):
        assert (PROJECT / "results.tsv").exists()

    def test_has_header(self):
        df = pd.read_csv(PROJECT / "results.tsv", sep="\t")
        assert "experiment_id" in df.columns
        assert "status" in df.columns

    def test_at_least_20_rows(self):
        df = pd.read_csv(PROJECT / "results.tsv", sep="\t")
        assert len(df) >= 20, f"Only {len(df)} rows, need >= 20"

    def test_has_e00_baseline(self):
        df = pd.read_csv(PROJECT / "results.tsv", sep="\t")
        assert "E00" in df["experiment_id"].values

    def test_has_tournament_entries(self):
        df = pd.read_csv(PROJECT / "results.tsv", sep="\t")
        t_entries = df[df["experiment_id"].str.startswith("T")]
        assert len(t_entries) >= 4, f"Only {len(t_entries)} tournament entries"

    def test_has_interaction_entries(self):
        df = pd.read_csv(PROJECT / "results.tsv", sep="\t")
        i_entries = df[df["experiment_id"].str.startswith("I")]
        assert len(i_entries) >= 1

    def test_all_keep_status(self):
        df = pd.read_csv(PROJECT / "results.tsv", sep="\t")
        assert all(df["status"] == "KEEP"), "All experiments should be KEEP for decomposition"


class TestTournamentCSV:
    def test_exists(self):
        assert (PROJECT / "tournament_results.csv").exists()

    def test_at_least_4_families(self):
        df = pd.read_csv(PROJECT / "tournament_results.csv")
        assert len(df) >= 4, f"Only {len(df)} tournament families"


class TestPhase0Artifacts:
    def test_papers_csv_exists(self):
        assert (PROJECT / "papers.csv").exists()

    def test_papers_csv_200_plus(self):
        df = pd.read_csv(PROJECT / "papers.csv")
        assert len(df) >= 200, f"Only {len(df)} citations"

    def test_literature_review_exists(self):
        assert (PROJECT / "literature_review.md").exists()

    def test_knowledge_base_exists(self):
        assert (PROJECT / "knowledge_base.md").exists()

    def test_research_queue_exists(self):
        assert (PROJECT / "research_queue.md").exists()

    def test_feature_candidates_exists(self):
        assert (PROJECT / "feature_candidates.md").exists()

    def test_design_variables_exists(self):
        assert (PROJECT / "design_variables.md").exists()


class TestPhaseBDiscoveries:
    def test_cost_driver_ranking_exists(self):
        assert (PROJECT / "discoveries" / "cost_driver_ranking.csv").exists()

    def test_regulatory_cost_burden_exists(self):
        assert (PROJECT / "discoveries" / "regulatory_cost_burden.csv").exists()

    def test_cost_driver_has_rows(self):
        df = pd.read_csv(PROJECT / "discoveries" / "cost_driver_ranking.csv")
        assert len(df) >= 10

    def test_regulatory_has_rows(self):
        df = pd.read_csv(PROJECT / "discoveries" / "regulatory_cost_burden.csv")
        assert len(df) >= 4


class TestPlots:
    def test_headline_plot_exists(self):
        assert (PROJECT / "plots" / "headline_material_trajectories.png").exists()

    def test_feature_importance_exists(self):
        assert (PROJECT / "plots" / "feature_importance_cagr_ranking.png").exists()

    def test_pred_vs_actual_exists(self):
        assert (PROJECT / "plots" / "pred_vs_actual_materials_labour.png").exists()

    def test_covid_ukraine_exists(self):
        assert (PROJECT / "plots" / "covid_ukraine_impact.png").exists()

    def test_regulatory_exists(self):
        assert (PROJECT / "plots" / "regulatory_excess_inflation.png").exists()

    def test_pca_exists(self):
        assert (PROJECT / "plots" / "pca_variance_explained.png").exists()


class TestPaperMD:
    def test_exists(self):
        assert (PROJECT / "paper.md").exists()

    def test_has_abstract(self):
        text = (PROJECT / "paper.md").read_text()
        assert "## Abstract" in text

    def test_has_detailed_baseline(self):
        text = (PROJECT / "paper.md").read_text()
        assert "## Detailed Baseline" in text

    def test_has_detailed_solution(self):
        text = (PROJECT / "paper.md").read_text()
        assert "## Detailed Solution" in text

    def test_has_methods(self):
        text = (PROJECT / "paper.md").read_text()
        assert "## Methods" in text

    def test_has_results(self):
        text = (PROJECT / "paper.md").read_text()
        assert "## Results" in text

    def test_has_discussion(self):
        text = (PROJECT / "paper.md").read_text()
        assert "## Discussion" in text

    def test_has_conclusion(self):
        text = (PROJECT / "paper.md").read_text()
        assert "## Conclusion" in text

    def test_has_references(self):
        text = (PROJECT / "paper.md").read_text()
        assert "## References" in text

    def test_no_reviewer_language(self):
        text = (PROJECT / "paper.md").read_text()
        for forbidden in ["reviewer", "sub-agent", "Phase 2.75", "Phase 3.5"]:
            assert forbidden.lower() not in text.lower(), f"Found forbidden term: {forbidden}"

    def test_references_plots(self):
        text = (PROJECT / "paper.md").read_text()
        assert "plots/" in text

    def test_at_least_30_citations(self):
        text = (PROJECT / "paper.md").read_text()
        # Count bracketed references [N]
        import re
        refs = re.findall(r'\[(\d+)\]', text)
        unique_refs = set(refs)
        assert len(unique_refs) >= 30, f"Only {len(unique_refs)} unique citations"
