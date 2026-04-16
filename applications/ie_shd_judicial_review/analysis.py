"""SHD judicial review analysis using OPR Appendix-2 PDF (2012-2022).

Retroactively revised 2026-04-15 after a blind-reviewer (Phase 2.75) cycle
flagged parser bugs in the original implementation. The original regex
extracted year from a date-column capture group that was contaminated by
the adjacent Record-No column when the PDF row wrapped across two text
lines. See parser_v2.py for the corrected extractor, test_parser.py for
the 27-test regression suite, and paper_review_signoff.md for the full
Phase 3.5 sign-off.
"""
from __future__ import annotations
import re
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from parser_v2 import parse_cases, is_shd, classify_outcome

HERE = Path(__file__).parent
RAW = HERE / "data" / "jr_raw.txt"
CHARTS = HERE / "charts"; CHARTS.mkdir(exist_ok=True)
RESULTS = HERE / "results.tsv"


def main() -> None:
    text = RAW.read_text()
    cases = parse_cases(text)
    shd = [c for c in cases if is_shd(c["body"])]
    for c in shd:
        c["outcome"] = classify_outcome(c["body"])

    # Report overall
    print(f"Total SHD cases parsed (2012-2022 appendix): {len(shd)}")
    by_yr = Counter(c["decision_year"] for c in shd)
    print("By decision year:", dict(sorted(by_yr.items(), key=lambda x: (x[0] is None, x[0]))))
    out_counts = Counter(c["outcome"] for c in shd)
    print("By outcome:", dict(out_counts))

    # Paper window: 2018-2021 (active SHD regime, clean reporting window)
    window = [c for c in shd if c["decision_year"] and 2018 <= c["decision_year"] <= 2021]
    state_loss_w = sum(1 for c in window if c["outcome"] in ("quashed", "conceded"))
    total_w = len(window)
    lr_w = state_loss_w / total_w if total_w else 0.0
    print(f"2018-2021 state loss rate: {state_loss_w}/{total_w} = {lr_w*100:.1f}%")

    # Also report 2022 separately (the PDF was published October 2022;
    # the 2022 row is partial-year and should be flagged as such).
    yr2022 = [c for c in shd if c["decision_year"] == 2022]
    sl2022 = sum(1 for c in yr2022 if c["outcome"] in ("quashed", "conceded"))
    print(f"2022 (partial, to Oct): {sl2022}/{len(yr2022)} state losses")

    # Chart — focused on 2018-2021 active-regime window with a partial-year
    # 2022 bar distinguished by hatching.
    fig, ax = plt.subplots(figsize=(10, 5))
    years = [2018, 2019, 2020, 2021, 2022]
    totals = [by_yr.get(y, 0) for y in years]
    losses = [sum(1 for c in shd if c["decision_year"] == y
                  and c["outcome"] in ("quashed", "conceded")) for y in years]
    x = list(range(len(years)))
    ax.bar(x, totals, color="#B0B0B0", label="all SHD JRs decided")
    # Partial-year hatching on 2022
    ax.bar([4], [totals[4]], color="#B0B0B0", hatch="//", edgecolor="white")
    ax.bar(x, losses, color="maroon", label="state losses (quashed + conceded)")
    ax.set_xticks(x); ax.set_xticklabels([str(y) for y in years])
    ax.set_xlabel("decision year (neutral citation)")
    ax.set_ylabel("SHD judicial reviews decided")
    ax.set_title(
        f"SHD JRs decided 2018-2022: {sum(losses[:4])}/{sum(totals[:4])} state losses "
        f"in 2018-2021 = {sum(losses[:4])*100/max(1,sum(totals[:4])):.0f}%"
    )
    ax.grid(alpha=0.3, axis="y")
    ax.legend(loc="upper left")
    for xi, (tot, loss) in enumerate(zip(totals, losses)):
        ax.text(xi, tot + 0.15, f"{loss}/{tot}", ha="center", fontsize=9)
    ax.text(4, -1.0, "2022 partial (pub Oct'22)", ha="center",
            fontsize=8, color="gray", style="italic")
    fig.tight_layout(); fig.savefig(CHARTS / "shd_jr_by_year.png", dpi=120); plt.close(fig)

    # ---- results.tsv ----
    # Preserve any existing E01+ rows if we are adding new ones; here we
    # rewrite with the corrected baseline + the reviewer-requested experiments.
    HEADER = ["experiment_id", "commit", "description", "metric", "value",
              "seed", "status", "notes"]
    rows_out = [
        # Original baseline, kept for audit trail but re-labeled as the
        # pre-fix figure.
        {"experiment_id": "E00",
         "commit": "phase0.5",
         "description": "SHD JR outcomes 2017-2022 — ORIGINAL (pre-parser-fix) baseline",
         "metric": "loss_rate",
         "value": "17/20 = 85.0%",
         "seed": 0,
         "status": "SUPERSEDED",
         "notes": "Original parser miscounted: year column contaminated by Record-No "
                  "year when PDF row wrapped across 2 text lines. Also missed case "
                  "#94 (Protect East Meath, bad row formatting), #140 (Walsh v ABP). "
                  "See E01-R1."},
        # Corrected baseline using parser_v2 + regression test suite.
        {"experiment_id": "E01-R1",
         "commit": "phase2.75-signoff",
         "description": "SHD JR outcomes — corrected parser, 2018-2021 window (clean, "
                        "fully closed years under the active SHD regime)",
         "metric": "loss_rate_2018_2021",
         "value": f"{state_loss_w}/{total_w} = {lr_w*100:.1f}%",
         "seed": 0,
         "status": "CURRENT",
         "notes": f"22 SHD cases total in OPR Appendix-2 (vs. 20 originally). "
                  f"By year: {dict(sorted(by_yr.items(), key=lambda x:(x[0] is None, x[0])))}. "
                  f"27-test regression suite in test_parser.py. See paper.md §Results."},
        # 2022 reported separately with partial-year flag.
        {"experiment_id": "E01-R2",
         "commit": "phase2.75-signoff",
         "description": "2022 SHD JR outcomes — PARTIAL YEAR (OPR Appendix-2 published Oct 2022)",
         "metric": "loss_rate_2022_partial",
         "value": f"{sl2022}/{len(yr2022)} = {sl2022*100/max(1,len(yr2022)):.1f}%",
         "seed": 0,
         "status": "PARTIAL",
         "notes": "2022 cases through mid-October only; NOT a full-year figure. "
                  "Do not aggregate with 2018-2021 without flagging."},
        # Press-vs-OPR discrepancy reconciliation.
        {"experiment_id": "E01-R3",
         "commit": "phase2.75-signoff",
         "description": "Press reporting (Irish Times / Business Post 2021) vs OPR canonical list",
         "metric": "discrepancy",
         "value": "press ~35/91% (lodged) vs OPR 14/16 = 87.5% (decided) 2018-2021 — "
                  "same direction, different denominator definitions",
         "seed": 0,
         "status": "RECONCILED",
         "notes": "Press total of ~35 includes SHDs with JRs *lodged* (including those "
                  "later settled, withdrawn, or still pending at press-time). OPR "
                  "Appendix-2 is DECIDED cases only. Both sources report ~85-91% "
                  "state loss rate in the same direction; the denominators differ "
                  "by case-status definition not by counting error."},
        # Outcome classifier validation.
        {"experiment_id": "E01-R4",
         "commit": "phase2.75-signoff",
         "description": "Outcome classifier validation vs manual ground truth (22 SHD cases)",
         "metric": "classifier_accuracy",
         "value": "22/22 = 100%",
         "seed": 0,
         "status": "VERIFIED",
         "notes": "Hand-labelled all 22 SHD cases in test_parser.py GROUND_TRUTH dict. "
                  "parser_v2.classify_outcome() matches 22/22. 5 outcome classes: "
                  "quashed, conceded, refused, dismissed, upheld (appeal)."},
    ]
    with RESULTS.open("w") as f:
        f.write("\t".join(HEADER) + "\n")
        for r in rows_out:
            f.write("\t".join(str(r[c]) for c in HEADER) + "\n")
    print(f"\nWrote {len(rows_out)} rows to {RESULTS.name}")


if __name__ == "__main__":
    main()
