"""Generate the covariate-ladder headline plot for the website summary."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).parent

# Data from results.tsv
ladder = [
    ("M0 (raw)", -0.0008, -0.0789, 0.0841),
    ("M1 (year + qtr + sector + state)", 0.0615, -0.0240, 0.1522),
    ("M2 (+ log offering)", 0.0171, -0.0701, 0.1077),
    ("M3 (broken — reviewer bug)", 0.0222, -0.0650, 0.1128),
    ("M3 (real ecosystem)", 0.0603, -0.0310, 0.1517),
    ("M4 (+ VIX)", 0.0431, -0.0448, 0.1328),
]
lookalike = ("Lookalike placebo\n(measurement-channel bias)", -0.2153, -0.2596, -0.1645)

fig, ax = plt.subplots(figsize=(9, 5.5))
ys = list(range(len(ladder) + 1))[::-1]
labels = [x[0] for x in ladder] + [lookalike[0]]
atts = [x[1] for x in ladder] + [lookalike[1]]
los = [x[2] for x in ladder] + [lookalike[2]]
his = [x[3] for x in ladder] + [lookalike[3]]

colors = ["#555555"] * 6 + ["#c44e52"]
# Highlight the bug-fixed M3 real row in teal
colors[4] = "#2b8cbe"

for y, att, lo, hi, c, lab in zip(ys, atts, los, his, colors, labels):
    ax.errorbar(att, y, xerr=[[att - lo], [hi - att]], fmt="o",
                color=c, capsize=5, markersize=8, linewidth=2)

ax.axvline(0, color="black", linestyle="-", linewidth=0.7)
ax.set_yticks(ys)
ax.set_yticklabels(labels, fontsize=10)
ax.set_xlabel("Average Treatment Effect on the Treated (ATT)\n"
              "5-year follow-on raise rate, YC − matched non-YC", fontsize=10)
ax.set_title("Covariate ladder + placebo: the Phase 2.75 bug fix flipped the story", fontsize=12)
ax.set_xlim(-0.30, 0.25)

# Annotations
ax.annotate("Bug: M3 covariates\nwere empty",
            xy=(0.0222, ys[3]), xytext=(0.07, ys[3] + 0.35),
            fontsize=9, color="#555555",
            arrowprops=dict(arrowstyle="->", color="#555555"))
ax.annotate("Fixed M3: estimate\nmoves UP, not toward 0",
            xy=(0.0603, ys[4]), xytext=(0.09, ys[4] + 0.3),
            fontsize=9, color="#2b8cbe", weight="bold",
            arrowprops=dict(arrowstyle="->", color="#2b8cbe"))
ax.annotate("High-PS lookalikes skip Form D\n→ control pool systematically\nunder-raises (biases ATT toward 0)",
            xy=(-0.2153, ys[-1]), xytext=(-0.28, ys[-1] - 0.1),
            fontsize=9, color="#c44e52", weight="bold",
            arrowprops=dict(arrowstyle="->", color="#c44e52"),
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#ffeeed", edgecolor="#c44e52"))

ax.grid(True, alpha=0.25, linestyle=":")
plt.tight_layout()

# Save to both website and project
for p in [HERE / "plots" / "covariate_ladder.png",
          Path.home() / "website" / "site" / "content" / "hdr" / "results" /
          "yc-vs-non-yc" / "plots" / "covariate_ladder.png"]:
    p.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(p, dpi=140, bbox_inches="tight")
    print(f"wrote {p}")
plt.close()
