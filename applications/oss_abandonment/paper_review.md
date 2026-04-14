# Phase 2.75 Adversarial Results Review

Independent reviewer, blind to author's conclusions except via `paper.md`, `results.tsv`, `research_queue.md`, `knowledge_base.md`, and source.

## P0 — blocking issues

- **P0-1/P0-2**: No temporal holdout. 25% random split mixes 2024-prior + 2025-forward events across train/test. A prior-date-based holdout was feasible and not attempted.
- **P0-3**: E17 "+7.6pp ROC" headline is not supported by a ROC-AUC bootstrap CI. Only PR-AUC CIs were computed. E11 and E17 PR-AUC CIs overlap at [0.9692, 0.9703]. The 0.005 ROC margin of E17 over E11 is likely inside bootstrap noise.
- **P0-4**: E17 gain confounded between cohort (E11) and relabel. Relabel-on-E00 (E04) was WORSE than baseline. Relabel-on-E02 (E09) gave a similar ~0.049 gain. The cohort × relabel interaction is unpacked incompletely.
- **P0-5**: Negative controls M1–M5 not run. A classifier reporting PR-AUC 0.97 at an 82% base rate MUST pass a permutation test; it hasn't been shown to.
- **P0-6**: `archived` flag and Libraries.io Status join are in `knowledge_base.md` §1 target definition but never implemented. The operational target diverges from the spec'd target.

## P1 — must-address

- Label-noise lower bound not measured. 3-day forward windows are very sparse; real repos with weekly-not-daily cadence can be falsely labelled abandoned ~30-40% of the time.
- 22/120 pre-registered hypotheses executed (18%). High-prior families entirely skipped: survival (G4, J6–J8), truck/bus factor (B3–B4), dependency-network (F1–F10), response time (C1–C12 — the single most-cited family), sentiment (D1–D10), calibration (H4), temporal CV (K1), interactions (L1–L10), and M1–M5 negative controls.
- PR-AUC at 94.6% base rate is ~base-rate for any log-commits ranker; abstract should not lead with 0.9810.
- Seed stability unverified. `train_baseline` sets the split seed but not XGBoost's internal RNG. Two reruns may drift 0.003–0.008 ROC, larger than the E17-over-E11 margin.
- E21 collapses to ROC 0.77 at ≥50-commit cohort. The "monotone gain" story in §6 is more honestly "plateau from ≥10 onwards."

## Mandatory follow-up experiments (BLOCKING for Phase 3.5)

| ID | Purpose |
|---|---|
| E23 | Label-permutation test — PR-AUC must collapse to base rate |
| E24 | Seed stability across 5 seeds — measure σ(ROC) |
| E25 | Paired ROC-AUC bootstrap CI, E11 vs E17 |
| E26 | Relabel-on-E02 control (decompose cohort vs relabel effects) |
| E31 | Isotonic calibration on E17 |
| E32 | Response-time features (most-cited literature family) |
| E33 | Truck-factor features (B3 family, prior 70%) |
| E35 | Permutation test family-wide |

## Paper revisions required

- Abstract: stop leading with PR-AUC 0.9810; lead with ROC-AUC. Replace "+7.6pp ROC over E00" with "+7.2pp from cohort (E11), +0.005 from relabel (E17, within bootstrap noise)." Demote "champion E17" to "keep candidate."
- §2 "Temporal holdout not feasible" is incorrect — rewrite as "deferred; see limitations."
- §4 table: add ROC CI where computed; annotate E17 margin as within noise.
- §6: remove base-rate-approaches-literature claim (horizons differ).
- §7 Contribution 2: scope to "the 17-feature GH-Archive aggregate space tested"; add that survival/network/response-time/sentiment families remain untested.
- §8: add the 7 limitations from the P1 list.

---

## Status: P19 PAUSED after Phase 2.75

Date: 2026-04-14.

The reviewer-mandated experiments E23–E35 were executed. Key blocking findings:

- **E25**: paired ROC-AUC delta E17 − E11 = −0.0003, 95% CI [−0.0024, +0.0020]. E17 is NOT a champion; the +0.005 was inside noise.
- **E24**: σ(ROC) across 5 seeds = 0.0047 > claimed E17-over-E11 margin (0.005).
- **E28**: temporal holdout (train 2024-04-01/03, test 2024-04-05) ROC = 0.5376 — near chance. Random-split ROC of 0.88 was largely same-window autocorrelation leakage.
- **E23 / E35**: permutation tests pass (PR collapses to base rate, ROC to 0.5) — no same-split label leakage, but temporal leakage is the bigger problem.
- **E31**: isotonic calibration works (Brier 0.134 → 0.072), so the model is calibratable even though the ranking isn't reliable under temporal validation.
- **E32 / E33**: response-time and author-concentration features land at ROC ~0.86 — within noise of E17. Feature breadth added; no change in conclusion.

Decision: **do not finalise or publish this paper.** The 3-day sample window is too thin to support the question. Resume requires either:
1. A denser GH-Archive pull (180d prior + 365d forward ≈ 300–500 GB), OR
2. GitHub API `/stats/commit_activity` on a smaller 2–5k-repo cohort with one year of weekly commits each.

All code, data, and 31 experiment rows are retained in `applications/oss_abandonment/` for future resumption.
