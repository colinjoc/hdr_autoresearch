"""Tests for plot generation — including annotation collision tests."""
import pytest
import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt


class TestPlotGeneration:
    """Test that all plots are generated without errors."""

    def test_hourly_delay_accumulation_plot(self):
        from generate_plots import plot_hourly_delay_accumulation
        fig, ax = plot_hourly_delay_accumulation()
        assert fig is not None
        assert ax is not None
        plt.close(fig)

    def test_carrier_propagation_plot(self):
        from generate_plots import plot_carrier_propagation
        fig, ax = plot_carrier_propagation()
        assert fig is not None
        assert ax is not None
        plt.close(fig)

    def test_propagation_depth_plot(self):
        from generate_plots import plot_propagation_depth
        fig, ax = plot_propagation_depth()
        assert fig is not None
        assert ax is not None
        plt.close(fig)

    def test_feature_importance_plot(self):
        from generate_plots import plot_feature_importance
        fig, ax = plot_feature_importance()
        assert fig is not None
        assert ax is not None
        plt.close(fig)

    def test_delay_cause_pie_plot(self):
        from generate_plots import plot_delay_cause_decomposition
        fig, ax = plot_delay_cause_decomposition()
        assert fig is not None
        assert ax is not None
        plt.close(fig)


class TestAnnotationCollisions:
    """Verify no overlapping annotations in plots."""

    def _get_text_bboxes(self, fig, ax):
        """Extract bounding boxes of all text annotations."""
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        bboxes = []
        for text in ax.texts:
            bb = text.get_window_extent(renderer=renderer)
            bboxes.append(bb)
        return bboxes

    def _check_no_collisions(self, bboxes, tolerance=2):
        """Check that no bounding boxes overlap more than tolerance pixels."""
        collisions = []
        for i in range(len(bboxes)):
            for j in range(i + 1, len(bboxes)):
                bb_i = bboxes[i]
                bb_j = bboxes[j]
                # Shrink each bbox by tolerance for near-miss detection
                overlap_x = (bb_i.x0 - tolerance < bb_j.x1) and (bb_j.x0 - tolerance < bb_i.x1)
                overlap_y = (bb_i.y0 - tolerance < bb_j.y1) and (bb_j.y0 - tolerance < bb_i.y1)
                if overlap_x and overlap_y:
                    collisions.append((i, j))
        return collisions

    def test_carrier_plot_no_annotation_collisions(self):
        from generate_plots import plot_carrier_propagation
        fig, ax = plot_carrier_propagation()
        bboxes = self._get_text_bboxes(fig, ax)
        collisions = self._check_no_collisions(bboxes)
        plt.close(fig)
        assert len(collisions) == 0, f"Found {len(collisions)} annotation collisions"

    def test_feature_importance_no_annotation_collisions(self):
        from generate_plots import plot_feature_importance
        fig, ax = plot_feature_importance()
        bboxes = self._get_text_bboxes(fig, ax)
        collisions = self._check_no_collisions(bboxes)
        plt.close(fig)
        assert len(collisions) == 0, f"Found {len(collisions)} annotation collisions"


class TestPlotSaving:
    """Test that plots save to files correctly."""

    def test_save_all_plots(self, tmp_path):
        from generate_plots import save_all_plots
        save_all_plots(str(tmp_path))
        expected_files = [
            'hourly_delay_accumulation.png',
            'carrier_propagation.png',
            'propagation_depth.png',
            'feature_importance.png',
            'delay_cause_decomposition.png',
        ]
        for fname in expected_files:
            fpath = os.path.join(str(tmp_path), fname)
            assert os.path.exists(fpath), f"Missing plot: {fname}"
            assert os.path.getsize(fpath) > 1000, f"Plot too small: {fname}"
