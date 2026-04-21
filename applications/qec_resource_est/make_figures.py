"""
Generate headline figures for paper_v3 from results.tsv.

Figures:
  fig1_codecap_crossover.png: surface d=3..13 code-capacity GPU/CPU ratio vs H size
  fig2_bb_vs_surface.png: BB GPU BP+OSD vs 12x surface d=17 CPU MWPM per LQR
  fig3_iter_ablation.png: BP+OSD iter sweep on BB circuit-level
  fig4_regime_map.png: 2D map of GPU/CPU ratio as a function of H_rows × H_cols
"""

from __future__ import annotations
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).parent
TSV = HERE / "results.tsv"
FIG_DIR = HERE / "figures"
FIG_DIR.mkdir(exist_ok=True)


def load() -> list[dict]:
    rows = []
    with TSV.open() as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            rows.append(row)
    return rows


def fig1_codecap_crossover(rows):
    e00 = [r for r in rows if r["id"].startswith("E00_d") and "surface_code" in r["code"]]
    d = [int(r["distance"]) for r in e00]
    cpu = [float(r["cpu_bposd_us"]) for r in e00]
    gpu = [float(r["gpu_bposd_us"]) for r in e00]
    ratio = [g/c if c > 0 else 0 for g, c in zip(gpu, cpu)]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))
    ax1.semilogy(d, cpu, "o-", label="CPU ldpc BP+OSD", color="tab:blue")
    ax1.semilogy(d, gpu, "s-", label="GPU CUDA-Q QEC BP+OSD", color="tab:orange")
    ax1.set_xlabel("surface-code distance d (code capacity)")
    ax1.set_ylabel("μs per shot (log)")
    ax1.set_title("Per-shot wall-time — code-capacity surface")
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    ax2.plot(d, ratio, "D-", color="tab:red")
    ax2.axhline(1.0, linestyle="--", alpha=0.5, color="gray", label="GPU = CPU")
    ax2.set_xlabel("surface-code distance d (code capacity)")
    ax2.set_ylabel("GPU/CPU ratio (lower = GPU wins)")
    ax2.set_title("Crossover trend — extrapolates to d ≈ 15")
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    fig.tight_layout()
    path = FIG_DIR / "fig1_codecap_crossover.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def fig2_bb_vs_surface(rows):
    # Manually pull the v2 E05 row values
    bb_us = 3694.5
    surf_us = 187.8
    bb_lqr = bb_us / (12 * 12)
    surf_lqr = surf_us / (12 * 12)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
    bars1 = ax1.bar(["BB GPU BP+OSD", "12 × surface d=17 CPU MWPM"],
                     [bb_us, surf_us],
                     color=["tab:orange", "tab:blue"])
    ax1.set_ylabel("μs per shot")
    ax1.set_title(f"Per-shot wall-time (matched LER, SI1000 p=1e-3, 12 rounds)")
    ax1.bar_label(bars1, fmt="%.0f μs")
    for b in bars1:
        b.set_edgecolor("black")

    bars2 = ax2.bar(["BB GPU BP+OSD", "12 × surface d=17 CPU MWPM"],
                     [bb_lqr, surf_lqr],
                     color=["tab:orange", "tab:blue"])
    ax2.set_ylabel("μs per logical-qubit-round")
    ax2.set_title(f"Per-LQR — 19.7× surface advantage")
    ax2.bar_label(bars2, fmt="%.2f μs")
    for b in bars2:
        b.set_edgecolor("black")

    fig.suptitle(f"BB [[144,12,12]] vs matched-LER 12-patch surface d=17 (RTX 3060)")
    fig.tight_layout()
    path = FIG_DIR / "fig2_bb_vs_surface.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def fig3_iter_ablation():
    iters = [10, 30, 100]
    cpu_us = [463120, 463881, 522887]  # from E05 output

    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar([f"iter={i}" for i in iters], cpu_us, color="tab:blue")
    ax.set_ylabel("μs per shot (CPU ldpc BP+OSD)")
    ax.set_title("BP+OSD iteration-count ablation on BB [[144,12,12]] circuit-level")
    ax.bar_label(bars, fmt="%.0f")
    for b in bars: b.set_edgecolor("black")
    ax.grid(True, alpha=0.3, axis="y")
    fig.tight_layout()
    path = FIG_DIR / "fig3_iter_ablation.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def fig4_regime_map():
    # GPU/CPU ratio as a function of H size
    data = [
        # (H_rows * H_cols, GPU/CPU ratio, label)
        (8*9, 40.3, "surface d=3 code-cap"),
        (24*25, 19.1, "surface d=5 code-cap"),
        (48*49, 10.1, "surface d=7 code-cap"),
        (80*81, 6.9, "surface d=9 code-cap"),
        (120*121, 5.6, "surface d=11 code-cap"),
        (168*169, 2.6, "surface d=13 code-cap"),
        (144*144, 2.5, "BB d=12 code-cap"),
        (936*10512, 1/146, "BB d=12 circuit-level (GPU wins 146×)"),
    ]
    xs = [d[0] for d in data]
    ys = [d[1] for d in data]
    labels = [d[2] for d in data]

    fig, ax = plt.subplots(figsize=(10, 5))
    for (x, y, lbl) in data:
        ax.scatter(x, y, s=80, edgecolor="black")
        ax.annotate(lbl, (x, y), textcoords="offset points", xytext=(7, 5), fontsize=8)
    ax.axhline(1.0, linestyle="--", alpha=0.5, color="gray", label="GPU = CPU")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("H parity-matrix entries (rows × cols)")
    ax.set_ylabel("GPU/CPU BP+OSD wall-time ratio (log scale; <1 = GPU wins)")
    ax.set_title("Regime map — GPU vs CPU BP+OSD on RTX 3060")
    ax.grid(True, alpha=0.3, which="both")
    ax.legend()
    fig.tight_layout()
    path = FIG_DIR / "fig4_regime_map.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


if __name__ == "__main__":
    rows = load()
    for f in [fig1_codecap_crossover(rows), fig2_bb_vs_surface(rows),
              fig3_iter_ablation(), fig4_regime_map()]:
        print(f"wrote {f}")
