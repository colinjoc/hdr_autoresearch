"""Irish emigration 2020-2025 destination analysis.

Retroactively revised 2026-04-15 following Phase 2.75 blind reviewer feedback
(see paper_review.md). Experiments E01-E06 added to results.tsv.
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).parent
CHARTS = HERE / "charts"
CHARTS.mkdir(exist_ok=True)
RESULTS = HERE / "results.tsv"

df = pd.read_csv(HERE / "data/migration_tidy.csv")
em = df[(df["sex"] == "Both sexes") & (df["flow"] == "Emigrants: All destinations")]
im = df[(df["sex"] == "Both sexes") & (df["flow"] == "Immigrants: All origins")]
net = df[(df["sex"] == "Both sexes") & (df["flow"] == "Net migration")]

# Total emigration trajectory
total = em[em["country"] == "All countries"].sort_values("year")
# Destination trajectories
dests = em[em["country"] != "All countries"].copy()
dest_map = {
    "EU14 excl Irl (countries in the EU pre 2004 excluding UK & Ireland)": "EU14 (Germany/FR/NL)",
    "EU15 to EU27 (accession countries joined post 2004)": "EU15-27 (Poland etc)",
    "United Kingdom (1)": "UK",
    "United States": "USA",
    "Other countries (23)": "Other (23)",
}
dests["dest"] = dests["country"].map(dest_map).fillna(dests["country"])

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
axes[0].plot(total["year"], total["value_thousands"], "o-", color="purple", linewidth=1.3)
axes[0].axvspan(2020, 2025, alpha=0.08, color="red")
# Annotate 2012 peak
peak_row = total.loc[total["value_thousands"].idxmax()]
axes[0].annotate(f"2012 peak: {peak_row['value_thousands']:.1f}k",
                 xy=(peak_row["year"], peak_row["value_thousands"]),
                 xytext=(peak_row["year"]-8, peak_row["value_thousands"]+1),
                 fontsize=8, arrowprops=dict(arrowstyle="->", lw=0.6))
axes[0].set_xlabel("year"); axes[0].set_ylabel("emigrants (thousands)")
axes[0].set_title("Irish emigration 1987-2025 (April estimate)")
axes[0].grid(alpha=0.3)

# Destination trajectories since 2010
recent = dests[dests["year"] >= 2010]
for d in recent["dest"].unique():
    sub = recent[recent["dest"] == d].sort_values("year")
    axes[1].plot(sub["year"], sub["value_thousands"], "o-", label=d, linewidth=1)
axes[1].set_xlabel("year"); axes[1].set_ylabel("emigrants (thousands)")
axes[1].set_title("Irish emigration by destination 2010-2025")
axes[1].legend(fontsize=7, loc="upper left"); axes[1].grid(alpha=0.3)
fig.tight_layout()
fig.savefig(CHARTS / "emigration_trajectories.png", dpi=120); plt.close(fig)

# --- Results ---
HEADER = ["experiment_id", "commit", "description", "metric", "value", "seed", "status", "notes"]
last = total.iloc[-1]
peak = total.loc[total["value_thousands"].idxmax()]
first_post = total[total["year"] == 2020].iloc[0]

# Convenience lookups
def emv(country, year):
    return em[(em["country"] == country) & (em["year"] == year)]["value_thousands"].iloc[0]

def imv(country, year):
    return im[(im["country"] == country) & (im["year"] == year)]["value_thousands"].iloc[0]

def netv(country, year):
    return net[(net["country"] == country) & (net["year"] == year)]["value_thousands"].iloc[0]

aus25, uk25 = emv("Australia", 2025), emv("United Kingdom (1)", 2025)
aus24, uk24 = emv("Australia", 2024), emv("United Kingdom (1)", 2024)
aus23, uk23 = emv("Australia", 2023), emv("United Kingdom (1)", 2023)
gap25 = aus25 - uk25
gap24 = aus24 - uk24
gap23 = aus23 - uk23
PRECISION = 2.5  # reviewer-cited ±2-3k precision band for CSO PEA18 small cells

rows = [
    {"experiment_id": "E00", "commit": "phase0.5",
     "description": "Irish emigration 2020-2025 CSO PEA18 trajectory",
     "metric": "emigration_2020_to_peak",
     "value": f"{first_post['value_thousands']:.1f}k → {peak['value_thousands']:.1f}k ({peak['year']:.0f})",
     "seed": 0, "status": "BASELINE",
     "notes": f"+{(peak['value_thousands']/first_post['value_thousands']-1)*100:.1f}% peak growth"},

    # E01 — "Australia overtook UK" under CSO precision band
    {"experiment_id": "E01-R1", "commit": "phase2.75",
     "description": "Australia vs UK 2025 gap vs CSO PEA18 ±2-3k precision band",
     "metric": "aus_minus_uk_2025_thousands",
     "value": f"{gap25:+.1f}",
     "seed": 0, "status": "CONFIRMED_WEAK",
     "notes": f"Gap {gap25:+.1f}k < precision band ±{PRECISION}k; tied within CI. "
              f"Downgrade 'structural shift' to 'statistical tie; Aus at top in 2025 only'."},
    {"experiment_id": "E01-R2", "commit": "phase2.75",
     "description": "Year-by-year Aus-UK gap 2023-2025",
     "metric": "aus_minus_uk_by_year",
     "value": f"2023:{gap23:+.1f} 2024:{gap24:+.1f} 2025:{gap25:+.1f}",
     "seed": 0, "status": "CLAIM_REVISED",
     "notes": "UK led by 9.9k (2023) and 4.6k (2024); Aus only ahead in 2025 (+0.9k). "
              "Paper's 'Since 2023 Australia has pulled ahead' is FALSE and must be rewritten."},

    # E02 — 2024→2025 drop
    {"experiment_id": "E02-R1", "commit": "phase2.75",
     "description": "2024 → 2025 total emigration change",
     "metric": "pct_change_2024_2025",
     "value": f"{(last['value_thousands']/69.9-1)*100:.1f}%",
     "seed": 0, "status": "RESOLVED",
     "notes": "69.9k → 65.6k (-6.1%). 2025 figure is PEA18 provisional and subject to revision; "
              "one-year dip does not by itself establish the wave has peaked."},

    # E03 — Net migration context
    {"experiment_id": "E03-R1", "commit": "phase2.75",
     "description": "Net migration and immigration 2020-2025",
     "metric": "imm_em_net_2025",
     "value": f"imm=125.3k em=65.6k net=+{netv('All countries',2025):.1f}k",
     "seed": 0, "status": "CONTEXT_ADDED",
     "notes": f"Ireland remained NET-RECEIVING every year 2020-2025. "
              f"Paper had +76k in the body — actual 2025 net is +{netv('All countries',2025):.1f}k (2024 was +79.3k)."},

    # E04 — 2012 peak now annotated on chart and added to table
    {"experiment_id": "E04-R1", "commit": "phase2.75",
     "description": "2012 post-war peak contextualisation",
     "metric": "peak_ratio_2024_to_2012",
     "value": f"{peak['value_thousands']:.1f}k (2012) vs 69.9k (2024) = {69.9/peak['value_thousands']*100:.1f}%",
     "seed": 0, "status": "CONFIRMED",
     "notes": "Peak now annotated on emigration_trajectories.png and stated in paper §What we found."},

    # E05 — Other-23 limitation
    {"experiment_id": "E05-R1", "commit": "phase2.75",
     "description": "'Other (23)' aggregate as ranking limitation",
     "metric": "other23_2025_thousands",
     "value": f"{emv('Other countries (23)', 2025):.1f}",
     "seed": 0, "status": "LIMITATION_ADDED",
     "notes": "11.1k across 23 unidentified countries rivals Aus/UK/EU14. Any single country "
              "inside Other-23 could rival top-4. Flagged as limitation in §What we cannot say."},

    # E06 — Title / scope mismatch (graduate)
    {"experiment_id": "E06-R1", "commit": "phase2.75",
     "description": "Title vs directory scope mismatch",
     "metric": "scope",
     "value": "PEA18 all-ages; not graduate-specific",
     "seed": 0, "status": "SCOPE_CLARIFIED",
     "notes": "Directory slug ie_graduate_emigration retained for history; paper §1 now "
              "states that graduate-specific analysis requires HEA GOS and is out of scope."},
]
with RESULTS.open("w") as f:
    f.write("\t".join(HEADER) + "\n")
    for r in rows:
        f.write("\t".join(str(r[c]) for c in HEADER) + "\n")

print("Wrote results.tsv and charts")
print(f"2020 → 2024 peak: {first_post['value_thousands']:.1f}k → 69.9k (+{(69.9/first_post['value_thousands']-1)*100:.1f}%)")
print(f"2025: {last['value_thousands']:.1f}k")
print(f"Aus-UK gap 2023/2024/2025: {gap23:+.1f} / {gap24:+.1f} / {gap25:+.1f} (precision band ±{PRECISION}k)")
print(f"2025 net migration: +{netv('All countries',2025):.1f}k")
