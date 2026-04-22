"""Generate paper figures from `results/e01_anchor_gpt2.tsv`.

Figures:
1. σ(layer) for trained vs random-init GPT-2-small (headline).
2. α vs θ threshold plateau at one middle layer (methodology).
3. Subspace σ_K vs ambient σ per layer (Fontenele arm).
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def figure_sigma_vs_layer(df: pd.DataFrame, outpath: Path) -> None:
    """σ_ambient(layer) for trained vs random-init at θ = 2.0."""
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    sub = df[df.threshold == 2.0].copy()
    for random_init, colour, label in [
        (False, "C0", "Pretrained GPT-2-small"),
        (True, "C3", "Random-init control"),
    ]:
        d = sub[sub.random_init == random_init]
        ax.plot(d.layer, d.sigma_ambient_MR, "o-", color=colour, label=label)
    ax.axhline(1.0, color="gray", ls="--", lw=1, label="σ = 1 (critical)")
    ax.axhline(0.98, color="gray", ls=":", lw=1, label="σ = 0.98 (Ma 2019)")
    ax.set_xlabel("Layer index")
    ax.set_ylabel("MR branching ratio σ (ambient)")
    ax.set_title("Training pulls activation σ toward the reverberating regime")
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    fig.savefig(outpath, dpi=300)
    plt.close(fig)


def figure_alpha_vs_threshold(df: pd.DataFrame, outpath: Path) -> None:
    """α(θ) threshold plateau at a representative middle layer."""
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    mid_layer = int(df.layer.max() // 2)
    sub = df[df.layer == mid_layer]
    for random_init, colour, label in [
        (False, "C0", "Pretrained"),
        (True, "C3", "Random-init"),
    ]:
        d = sub[sub.random_init == random_init].sort_values("threshold")
        ax.plot(d.threshold, d.alpha, "o-", color=colour, label=label)
    ax.axhline(1.5, color="gray", ls="--", lw=1, label="α = 3/2 (mean-field DP)")
    ax.set_xlabel("z-score threshold θ (σ-units)")
    ax.set_ylabel(f"Power-law exponent α (layer {mid_layer})")
    ax.set_title("Threshold plateau of avalanche-size exponent")
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    fig.savefig(outpath, dpi=300)
    plt.close(fig)


def figure_subspace_vs_ambient(df: pd.DataFrame, outpath: Path) -> None:
    """σ_subspace vs σ_ambient per layer — Fontenele arm."""
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    sub = df[df.threshold == 2.0].copy()
    for random_init, marker, colour, label in [
        (False, "o", "C0", "Pretrained"),
        (True, "s", "C3", "Random-init"),
    ]:
        d = sub[sub.random_init == random_init]
        ax.scatter(d.sigma_ambient_MR, d.sigma_subspace_MR,
                   marker=marker, color=colour, label=label, s=50)
    lims = [0.85, 1.15]
    ax.plot(lims, lims, "k--", lw=1, alpha=0.6, label="σ_ambient = σ_subspace")
    ax.axvline(1.0, color="gray", ls=":", lw=0.7)
    ax.axhline(1.0, color="gray", ls=":", lw=0.7)
    ax.set_xlabel("σ_ambient (MR, ambient residual stream)")
    ax.set_ylabel("σ_subspace (MR, top-K-PC reconstructed scalar)")
    ax.set_title("Fontenele subspace vs ambient branching ratio")
    ax.set_xlim(lims)
    ax.set_ylim(lims)
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    fig.savefig(outpath, dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    df = pd.read_csv(ROOT / "results" / "e01_anchor_gpt2.tsv", sep="\t")
    figs = ROOT / "figures"
    figs.mkdir(exist_ok=True)
    figure_sigma_vs_layer(df, figs / "fig1_sigma_vs_layer.png")
    figure_alpha_vs_threshold(df, figs / "fig2_alpha_vs_threshold.png")
    figure_subspace_vs_ambient(df, figs / "fig3_subspace_vs_ambient.png")
    print("wrote 3 figures to", figs)
