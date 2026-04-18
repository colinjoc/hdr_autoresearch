"""
Phase B Discovery: AARO Case Resolution Analysis

Outputs:
  discoveries/aaro_structured_data.csv -- every quantitative figure from all AARO/ODNI reports
  discoveries/resolution_taxonomy.csv -- resolution categories with descriptions and counts
  discoveries/backlog_projection.csv -- 3-year backlog projection
  discoveries/bayesian_sensitivity.csv -- Bayesian posterior across prior range
"""

import os
import sys
import csv

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from extract_data import (
    generate_structured_data,
    generate_resolution_taxonomy,
    compute_backlog_growth,
    compute_bayesian_posterior,
    compute_resolution_rates,
    compute_base_rate_comparison,
    write_structured_csv,
    write_taxonomy_csv,
)

DISC_DIR = os.path.join(PROJECT_ROOT, "discoveries")
os.makedirs(DISC_DIR, exist_ok=True)


def write_backlog_projection():
    """Write 3-year monthly backlog projection."""
    bg = compute_backlog_growth()
    intake = bg["intake_rate_per_month"]
    resolution = bg["resolution_rate_per_month"]
    initial = bg["cumulative_open"]

    path = os.path.join(DISC_DIR, "backlog_projection.csv")
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["month", "projected_open_cases", "cumulative_intake", "cumulative_resolved"])
        for m in range(37):
            proj = initial + (intake - resolution) * m
            cum_intake = intake * m
            cum_resolved = resolution * m
            writer.writerow([m, round(proj), round(cum_intake), round(cum_resolved)])
    print(f"Written: {path}")
    return path


def write_bayesian_sensitivity():
    """Write Bayesian posterior sensitivity across prior range."""
    p_unresolved_prosaic = 444 / 757
    priors = [i / 100 for i in range(1, 26)]

    path = os.path.join(DISC_DIR, "bayesian_sensitivity.csv")
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["prior_pct", "posterior_pct", "likelihood_ratio", "interpretation"])
        for p in priors:
            p_unresolved = 1.0 * p + p_unresolved_prosaic * (1 - p)
            posterior = (1.0 * p) / p_unresolved
            lr = 1.0 / p_unresolved_prosaic
            interp = "low" if posterior < 0.1 else "moderate" if posterior < 0.2 else "notable"
            writer.writerow([
                round(p * 100, 1),
                round(posterior * 100, 2),
                round(lr, 3),
                interp,
            ])
    print(f"Written: {path}")
    return path


def print_key_findings():
    """Print the key findings summary."""
    print("\n" + "=" * 70)
    print("PHASE B KEY FINDINGS: AARO CASE RESOLUTION ANALYSIS")
    print("=" * 70)

    print("\n1. RESOLUTION RATE")
    rates = compute_resolution_rates()
    for r in rates:
        if r["resolution_rate"] is not None:
            print(f"   {r['period']}: {r['resolution_rate']*100:.1f}%")
    print("   -> 100% of resolved cases are prosaic")

    print("\n2. BACKLOG TREND")
    bg = compute_backlog_growth()
    print(f"   Intake: {bg['intake_rate_per_month']}/month")
    print(f"   Resolution: {bg['resolution_rate_per_month']}/month")
    print(f"   Ratio: {bg['intake_to_resolution_ratio']}x (backlog growing)")
    print(f"   Open cases: {bg['cumulative_open']}")
    print(f"   Data-insufficient: {bg['active_archive_data_insufficient']} ({bg['active_archive_data_insufficient']/757*100:.1f}%)")

    print("\n3. BASE-RATE FINDING")
    comp = compute_base_rate_comparison()
    print(f"   Blue Book: {comp['blue_book_id_rate']*100:.1f}% identified (5.6% unknown)")
    print(f"   Hendry: {comp['hendry_id_rate']*100:.1f}% identified (11.4% unknown)")
    print(f"   AARO: {comp['aaro_overall_resolution_rate']*100:.1f}% resolved, but 100% prosaic")
    print(f"   AARO IC-merit: 21 cases (2.8%) -- convergent with GEIPAN 3.5% Type D")

    print("\n4. BAYESIAN POSTERIOR")
    bp = compute_bayesian_posterior()
    print(f"   Prior: {bp['prior_anomalous']*100:.0f}%")
    print(f"   Posterior: {bp['posterior_anomalous']*100:.1f}%")
    print(f"   Likelihood ratio: {bp['likelihood_ratio']}")
    print(f"   -> {bp['interpretation']}")

    print("\n5. NUFORC COMPARISON")
    print(f"   NUFORC: {comp['nuforc_explained_rate']*100:.2f}% explained (no systematic investigation)")
    print(f"   AARO: {comp['aaro_overall_resolution_rate']*100:.1f}% resolved (multi-agency investigation)")
    print("   Shapes: both dominated by lights/orbs; Starlink emerging in both")
    print("   Geography: both show collection bias (military vs population/infrastructure)")

    print("\n6. HONEST ANSWER: IS THERE ANYTHING ANOMALOUS?")
    print("   The data CANNOT definitively answer this question.")
    print("   What we know:")
    print("   - 100% of cases AARO has resolved are prosaic")
    print("   - 58.7% of cases lack sufficient data to analyze")
    print("   - 2.8% merit further IC analysis (consistent with historical 3-6% residual)")
    print("   - The residual could be: (a) prosaic objects with insufficient data,")
    print("     (b) sensor artifacts not yet explained, (c) something genuinely novel")
    print("   - Historical programs (Blue Book, Hendry, GEIPAN) consistently find 94-97%")
    print("     prosaic when investigation is thorough")
    print("   - AARO's low resolution rate reflects data quality, not anomaly density")


if __name__ == "__main__":
    print("=== Phase B Discovery: AARO Case Resolution ===\n")

    # Generate all discovery outputs
    write_structured_csv(os.path.join(DISC_DIR, "aaro_structured_data.csv"))
    write_taxonomy_csv(os.path.join(DISC_DIR, "resolution_taxonomy.csv"))
    write_backlog_projection()
    write_bayesian_sensitivity()

    print_key_findings()

    print("\n\nDiscovery outputs:")
    for f in os.listdir(DISC_DIR):
        path = os.path.join(DISC_DIR, f)
        size = os.path.getsize(path)
        print(f"  {f}: {size:,} bytes")
