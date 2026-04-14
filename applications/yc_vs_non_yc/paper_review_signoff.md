# Phase 3.5 Blind Reviewer Signoff — Final

## Verdict

VERDICT: NO FURTHER BLOCKING ISSUES

## Revision verification

| # | Suggestion | Addressed? | Observation |
|---|---|---|---|
| 1 | n_treated 117 vs 116 reconciliation | yes | The masthead now reads "n_treated = 117 exact-matched (primary spec uses 116 after one common-support drop; see §3.1)" and §2.3 states explicitly that one treated row drops on common-support pruning in M3_real, with n=116 quoted in §3.1–§4. |
| 2 | RV04 p = 0.327 logged | yes | `data/rv04_permutation.log` exists, records p = 0.3267 (98/300), and §3.4 explicitly references the sidecar log path. |
| 3 | §3.5 PR-AUC framing | yes | §3.5 now cites the test-set base rate (≈0.102) explicitly and states LightGBM's 0.124 is "~22% above random," replacing the prior "below random" wording. |
| 4 | Fehder 2024 comparison softening | yes | §5 row notes the outcome variables differ (Form-D follow-on raise vs ecosystem-quality outcomes) and frames the comparison as "suggestive only — the comparison is not a refutation of Fehder." |
| 5 | Fuzzy match n reconciliation | yes | §2.3 now spells out "combined exact+fuzzy cohort reached n = 136 pre-PSM (n = 134 post-match)" with deduping/batch-date filter mentioned; the 117 → 134 path is traceable. |
| 6 | Bootstrap design + caliper units | yes | §4 specifies "linear logit of the estimated PS; caliper = 0.2 × σ(PS) on the linear-logit scale" and includes a parenthetical noting the bootstrap treats matched rows as independent rather than clustering on matched set or CIK. |
| 7 | §2.4 PR-AUC exp_id citation | yes | §2.4 cites "rows `E01-L1`..`E01-LB` in `results.tsv`" for the tournament. |

## Re-verified claims

1. Primary ATT +6.03 pp, CI [−3.10, +15.17], n_t=116, n_c=580 → `RV01-M3_real` matches (+0.0603 [−0.0310, +0.1517]). ✓
2. Unconditional RD −0.08 pp, CI [−7.9, +8.4], n_t=117 → `E00a` matches (−0.0008 [−0.0789, +0.0841]). ✓
3. Lookalike placebo −21.5 pp, CI [−26.0, −16.5], n_t=117, n_c=31,607 → `RV06-alt` matches (−0.2153 [−0.2596, −0.1645]). ✓
4. Cox HR 0.786, CI [0.565, 1.093] → `RV07` matches (0.7858 [0.5647, 1.0935]). ✓
5. M2_size ladder row +1.71 pp, CI [−7.0, +10.8], n=117 → `RV01-M2_size` matches (+0.0171 [−0.0701, +0.1077]). ✓

Additionally cross-checked: RV04 observed ATT +0.0431 with null bounds [−0.0781, +0.0885] reconciles between `results.tsv` and the new `rv04_permutation.log`; RV02 fuzzy panel n=134 post-match matches §2.3.

## Test suite

`python -m pytest tests/ -x --tb=short` → **33 passed in 2.21s**, 0 failures.

## Final assessment

The author addressed all seven non-blocking suggestions from the prior conditional signoff with substantive — not cosmetic — edits: the headline n discrepancy is now reconciled in the masthead and §2.3, the RV04 permutation has a verifiable sidecar log, the PR-AUC framing in §3.5 is now numerically correct against the test-set base rate, and the Fehder comparison no longer overclaims a refutation. The methodological clarifications in §4 (linear-logit caliper, bootstrap independence assumption) and the §2.4 exp_id citation tighten reproducibility. All five spot-checked numerical claims still reconcile against `results.tsv`, and the full pytest suite is green. The paper is ready to publish as an honestly-reported, appropriately-hedged null/suggestive finding. **Final rigour: 8.5/10.**
