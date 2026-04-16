"""Phase B Discovery: JR tax estimates and counterfactual completions.

Outputs:
  discoveries/jr_tax_estimates.csv — lower/central/upper bound of housing-unit-months
  discoveries/counterfactual_completions.csv — annual completions under 18wk SOP vs observed
  discoveries/jr_cases_detail.csv — per-case breakdown with unit-months and holding costs
"""
from analysis import (
    compute_direct_delay,
    compute_indirect_delay,
    compute_counterfactual_completions,
    write_phase_b_discoveries,
    SHD_JR_CASES,
    HOLDING_COST_EUR_PER_UNIT_MONTH,
)


def main():
    print("Phase B Discovery — JR Tax on Housing Supply")
    print("=" * 60)

    # Write all discovery CSVs
    write_phase_b_discoveries()

    # Summarise
    direct = compute_direct_delay()
    indirect = compute_indirect_delay()
    cf = compute_counterfactual_completions()
    total_gap = sum(r.get("gap", 0) for r in cf)

    print(f"\n--- jr_tax_estimates.csv ---")
    print(f"Direct JR delay: {direct:,.0f} unit-months")
    print(f"Indirect (lower=0% JR):  {direct + indirect['lower']:,.0f} total unit-months")
    print(f"Indirect (central=25%):  {direct + indirect['central']:,.0f} total unit-months")
    print(f"Indirect (upper=50%):    {direct + indirect['upper']:,.0f} total unit-months")

    print(f"\n--- counterfactual_completions.csv ---")
    print(f"Cumulative completions gap 2018-2024: {total_gap:,} units")
    for row in cf:
        if row["year"] >= 2018:
            print(f"  {row['year']}: observed={row['observed']:,}, "
                  f"counterfactual={row['counterfactual_18wk']:,}, "
                  f"gap={row.get('gap', 0):,}")

    print(f"\n--- jr_cases_detail.csv ---")
    print(f"{len(SHD_JR_CASES)} cases written with per-case unit-months and holding costs")

    # Holding cost summary
    hc_total = direct * HOLDING_COST_EUR_PER_UNIT_MONTH
    print(f"\nTotal holding cost (finance only): EUR {hc_total:,.0f}")
    print(f"  at EUR {HOLDING_COST_EUR_PER_UNIT_MONTH}/unit/month")

    print(f"\n{'=' * 60}")
    print("Phase B complete. Discovery CSVs written to discoveries/")


if __name__ == "__main__":
    main()
