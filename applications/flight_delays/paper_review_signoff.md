# Paper Review Signoff: Flight Delay Propagation

**Paper**: "When Your Flight Is Late: How Delays Ripple Through the US Aviation Network"
**Review date**: 2026-04-10
**Response date**: 2026-04-10
**Signoff date**: 2026-04-10

## Review Summary

| Severity | Count | Status |
|----------|-------|--------|
| Critical | 0 | N/A |
| Major | 18 | All addressed |
| Minor | 4 | All addressed |

## New Experiments Run

| Experiment | Result | Section |
|------------|--------|---------|
| SHAP TreeExplainer (20K sample) | Top: dest_arr_delay 20.4%, origin_dep_delay 15.4%, taxi-out 11.1%, turnaround 10.6% | 3.5, 4.2 |
| Calibration (Brier, ECE) | Brier 0.074, ECE 0.009 | 4.9 |
| Temporal robustness (per-month AUC) | Apr 0.920, May 0.921, Jun 0.919 (std 0.0008) | 4.9 |
| First-leg-of-day accuracy | AUC 0.880 (first-leg) vs 0.928 (non-first-leg) | 4.9 |
| Network centrality (degree, betweenness, PageRank) | 343 airports, 6536 routes; DFW #1 degree + propagation | 4.8 |

## Key Narrative Changes

1. **Feature importance story revised**: The original paper claimed rotation features account for "over 55% of total importance." SHAP analysis shows 28%. The paper now reports both gain and SHAP, treats SHAP as authoritative, and frames the finding as "airport congestion and rotation dynamics jointly dominate."

2. **Propagation score defined**: Formula now explicit in Section 4.6: delay_rate x mean_LateAircraftDelay x log(1 + n_flights).

3. **Causal -> observational**: All carrier-level claims rewritten with observational language. New limitations paragraph on causal inference.

4. **Bibliography doubled**: 14 -> 27 references, including EUROCONTROL, Lan et al. 2006, Dunbar et al. 2012, Henricksen & Olaya 2020, Lundberg & Lee 2017.

## Files Changed

- `paper.md` -- All sections revised
- `review_experiments.py` -- New: SHAP, calibration, temporal robustness, first-leg, network metrics
- `tests/test_review_experiments.py` -- New: 14 tests, all passing
- `generate_plots.py` -- Added SHAP plot, pinned random seed
- `plots/shap_importance.png` -- New plot
- `paper_review_response.md` -- New: detailed response to each finding
- Website summary -- Rewritten in journalism format

## Remaining Acknowledged Gaps

These were noted in the review and acknowledged in the paper but not experimentally addressed:

1. **Tail-number swap sensitivity**: Acknowledged in limitations; random chain-breaking sensitivity analysis left as future work.
2. **Passenger-hours impact**: Requires load factor data not in BTS.
3. **Summer/fall coverage**: Data covers Jan-Jun only. Noted in limitations.
4. **Deep literature review**: Bibliography expanded to 27 but a full 100+ citation review is beyond scope for this cycle.

## Signoff

All 18 MAJOR and 4 MINOR review findings have been addressed. New experiments confirm the model is well-calibrated, temporally stable, and degrades gracefully on first-leg flights. The SHAP analysis materially changed the paper's central importance claim (rotation features 28% not 55%), improving accuracy. The paper is ready for the next review cycle.
