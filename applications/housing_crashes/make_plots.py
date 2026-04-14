"""Headline plot: the apparent PR-AUC lift and its dissolution under
honest-inference diagnostics. Built for paper.md and website summary.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).parent
plt.style.use("seaborn-v0_8-whitegrid")

# From results.tsv
diagnostics = [
    ("Headline L2\n(PR-AUC 0.044)", 0.0439, 0.0439, 0.0439, "#2b8cbe",
     "4.7× base rate"),
    ("Metro-clustered\nbootstrap CI", 0.0439, 0.0145, 0.1146, "#555555",
     "CI lower = 1.6×"),
    ("Single-feature\nmomentum", 0.0758, 0.0758, 0.0758, "#2ca25f",
     "strictly > L2"),
    ("LOMO:\nremove Clarksdale", 0.0266, 0.0266, 0.0266, "#e34a33",
     "−39% drop"),
    ("LOMO:\nremove 2 metros", 0.0197, 0.0197, 0.0197, "#e34a33",
     "−55% drop"),
    ("Metro-block\npermutation null", 0.0533, 0.0533, 0.0533, "#c44e52",
     "p = 0.493"),
]

fig, ax = plt.subplots(figsize=(10, 5.5))
ys = list(range(len(diagnostics)))[::-1]
base_rate = 0.00934

for y, (label, point, lo, hi, color, annot) in zip(ys, diagnostics):
    if lo != hi:
        # CI bar
        ax.plot([lo, hi], [y, y], color=color, lw=3, alpha=0.6)
        ax.plot([lo, lo], [y - 0.1, y + 0.1], color=color, lw=2)
        ax.plot([hi, hi], [y - 0.1, y + 0.1], color=color, lw=2)
    ax.scatter(point, y, s=120, color=color, zorder=3, edgecolor="white", linewidth=1.5)
    ax.annotate(annot, xy=(point, y), xytext=(max(0.12, hi + 0.005), y),
                fontsize=9, color=color, va="center")

ax.axvline(base_rate, color="black", linestyle="--", linewidth=1, alpha=0.7,
           label=f"Test base rate ({100*base_rate:.2f}%)")
ax.axvline(2 * base_rate, color="grey", linestyle=":", linewidth=1, alpha=0.5,
           label="2× base rate")

ax.set_yticks(ys)
ax.set_yticklabels([d[0] for d in diagnostics], fontsize=10)
ax.set_xlabel("PR-AUC (test set, 2022-07 → 2023-12)", fontsize=10)
ax.set_xlim(0, 0.19)
ax.set_title("The apparent crash-prediction signal dissolves under honest inference",
             fontsize=12)
ax.legend(loc="lower right", fontsize=9)
plt.tight_layout()

for p in [HERE / "plots" / "headline_dissolution.png",
          Path.home() / "website" / "site" / "content" / "hdr" / "results"
          / "housing-crashes" / "plots" / "headline_dissolution.png"]:
    p.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(p, dpi=140, bbox_inches="tight")
    print(f"wrote {p}")
plt.close()

# Second plot: the 19 crashing metros (population-vs-row-count, highlighting
# that they're tiny rural micropolitans not Sun Belt metros)
metros = [
    ("Clarksdale, MS", 16),
    ("Johnstown, PA", 9),
    ("Beeville, TX", 8),
    ("Kennett, MO", 8),
    ("Natchez, MS-LA", 8),
    ("McComb, MS", 7),
    ("Zapata, TX", 6),
    ("Opelousas, LA", 4),
    ("Huron, SD", 4),
    ("DeRidder, LA", 4),
    ("Boise City, ID", 3),
    ("Ukiah, CA", 3),
]
metros = sorted(metros, key=lambda x: x[1])
fig, ax = plt.subplots(figsize=(9, 5))
colors = ["#2b8cbe" if m[0] in ("Boise City, ID",) else "#c44e52" for m in metros]
ax.barh(range(len(metros)), [m[1] for m in metros], color=colors)
ax.set_yticks(range(len(metros)))
ax.set_yticklabels([m[0] for m in metros], fontsize=10)
ax.set_xlabel("Positive rows contributed (overlapping 12-month windows)", fontsize=10)
ax.set_title('Of the 19 metros that crossed −10% in 12 months, all but Boise are '
             'small rural "secular-decline" markets',
             fontsize=11)
plt.tight_layout()
for p in [HERE / "plots" / "crashing_metros.png",
          Path.home() / "website" / "site" / "content" / "hdr" / "results"
          / "housing-crashes" / "plots" / "crashing_metros.png"]:
    p.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(p, dpi=140, bbox_inches="tight")
    print(f"wrote {p}")
plt.close()
