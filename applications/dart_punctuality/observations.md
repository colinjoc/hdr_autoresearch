# Observations — DART Punctuality Cascade Prediction

## Data Observations

1. **The signal is mostly linear.** Ridge regression (CV AUC 0.983) outperforms XGBoost (0.971) and ExtraTrees (0.896) on cross-validation. The punctuality collapse is a clear structural break that linear models capture well. XGBoost recovers via interactions (post_change_x_wind) but the core signal is step-function-like.

2. **The positive class rate (47%) is near balanced.** Unlike the Iberian blackout project where excursion events were 0.9% of hours, DART bad days are common — especially post-September 2024. This means class imbalance is NOT a problem here, and scale_pos_weight adjustments have no effect.

3. **The synthetic data has a limitation: the timetable change date is a known input.** In the real world, the date of the change is known, so the model's reliance on post_timetable_change is legitimate. But in the synthetic data, the same variable controls both the generation of daily punctuality AND the prediction feature. This makes the prediction task easier than it would be with real GTFS-RT data where daily variation has additional unexplained noise.

4. **Feature ablation reveals collinearity.** Ablating the timetable features alone barely changes collapse-period predictions because the rolling punctuality features (which are target-lagged) already encode the regime shift. This is a data leakage concern for the lag features — they encode the same information the model is trying to predict.

5. **Morning punctuality is the strongest genuinely predictive feature.** Unlike lag features that encode past performance, morning_punct is a same-day leading indicator. In a real deployment, this would be the most operationally useful signal: "this morning was bad, expect a bad afternoon."

## Methodology Observations

6. **The 5-fold temporal CV is aggressive on small data.** With 1089 days split 6 ways, each fold has ~181 validation days. Fold 1 trains on only 181 days, which explains its lower AUC (0.891). The expanding window design means later folds are better calibrated.

7. **Feature importance is dominated by the structural break.** In a real prediction system, post_timetable_change would be a known constant (either 0 or 1 for the current regime). The operational model would need to predict within a regime, not across the regime change. This means the real operational challenge is harder than our CV numbers suggest.

8. **The 40-experiment Phase 2 is sufficient for this problem.** The research queue was exhausted after 40 experiments: 10 kept, 30 reverted. The last 15 experiments (H026-H040) were all near-zero delta or reverts, indicating saturation. With a linear signal and a known structural break, the hypothesis space is thin.

## Recommendations for Real Deployment

9. **Collect GTFS-RT data for 6+ months.** The NTA feed is available; what's missing is a collection pipeline. A daily cron job saving trip_updates snapshots would build the real historical dataset within months.

10. **Build a within-regime model.** Separate models for pre- and post-timetable-change regimes would test whether the operational signal (morning cascade, weather) is sufficient to predict bad days within a known timetable regime.

11. **Add fleet availability data.** Irish Rail's rolling stock issues (DART expansion deliveries delayed, older 8100-series reliability) are not captured in our features. Fleet availability would add a fourth competing explanation.

12. **Validate with actual delay minutes.** Our synthetic data uses punctuality (binary: on-time or not). Real GTFS-RT data provides actual delay in minutes per service, enabling richer analysis of delay propagation patterns through the network.
