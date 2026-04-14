# Research Queue — YC vs Non-YC

Hypotheses organised by theme. Each entry: ID, statement, falsifiable prediction, priority (P1/P2/P3), link to Phase 2 experiment.

Themes: A sample definition · B matching design · C outcome definition · D heterogeneity · E confound sensitivity · F temporal validity · G feature engineering · H hyperparameters · I calibration · J model family · K temporal CV (MANDATORY) · L interactions · M negative controls (MANDATORY).

---

## Theme A — Sample Definition

- **A1 (P1)** Use all YC batches S05–W24 as the treated universe — 5,690 companies per yc-oss. Prediction: sample size adequate for ±2 pp confidence interval on main ATE.
- **A2 (P1)** Restrict to YC companies for which we can verify an associated Form D filing (CIK lookup by name + delaware state). Prediction: ~60% match rate; keep only matched firms for primary analysis.
- **A3 (P2)** Compare effect using demo-day cohort (firms that reached demo day) vs nominal admits (includes drop-outs). Prediction: treatment effect larger for demo-day cohort (mechanically, more exposure).
- **A4 (P2)** Restrict to batches with stabilised program format: exclude S05 (pilot) and remote pandemic batches S20–S21. Prediction: effect stable to this exclusion.
- **A5 (P2)** Test whether restricting to US-domiciled YC firms (vs international) changes ATE. Prediction: ATE larger for US-only due to Form D control pool alignment.
- **A6 (P3)** Drop YC companies that are spin-outs of prior-known firms (e.g., OpenAI, Cruise). Prediction: marginal effect on ATE (<1 pp).
- **A7 (P2)** Decide stage bin: include only companies at pre-seed/seed stage at batch entry vs all. Prediction: effect concentrated in pre-seed.
- **A8 (P2)** Exclude companies whose status=Inactive within 6 months of batch end — these are treatment non-completers. Prediction: intent-to-treat vs treatment-on-treated differs by <3 pp.

## Theme B — Matching Design

- **B1 (P1)** Primary: 1-to-5 nearest-neighbour propensity matching on batch quarter, sector (2-digit SIC), state, log(totalOfferingAmount). Prediction: overlap adequate (>95% of treated on common support).
- **B2 (P1)** Robustness: Coarsened Exact Matching (Iacus-King-Porro 2012) with same covariates. Prediction: ATE within ±3 pp of PSM.
- **B3 (P1)** Robustness: Mahalanobis matching. Prediction: ATE within ±3 pp of PSM.
- **B4 (P2)** Caliper at 0.2 × SD of propensity; report % treated unmatched. Prediction: <5% unmatched.
- **B5 (P2)** With-replacement vs without-replacement matching. Prediction: point estimate stable, SE changes slightly.
- **B6 (P2)** Genetic matching (Sekhon 2011) as balance-optimising alternative. Prediction: improves balance on harder-to-match covariates.
- **B7 (P2)** Doubly-robust estimator (AIPW) using PSM + outcome regression. Prediction: more efficient; reports similar ATE with tighter CI.
- **B8 (P1)** Double ML (Chernozhukov et al. 2018) with random forest nuisance functions; compare to linear PSM. Prediction: similar point estimate; gives confidence that high-dim covariates don't move the answer.
- **B9 (P3)** Test common-support trimming (drop treated with propensity >0.95 or <0.05). Prediction: trimmed ATE within ±2 pp.
- **B10 (P2)** Exact-match on batch (quarter-year) before propensity on rest. Prediction: eliminates batch-era confounding.

## Theme C — Outcome Definition

- **C1 (P1)** Primary outcome: follow-on raise within T+3 years (binary). Prediction: YC effect +5 to +15 pp.
- **C2 (P1)** Secondary: survival (status ≠ Inactive/defunct) at T+5 years. Prediction: small or null effect; aligns with Yu (2020).
- **C3 (P1)** Secondary: acquired within T+7 years. Prediction: modest positive (+2 to +5 pp).
- **C4 (P1)** Secondary: IPO within T+10 years. Prediction: cell sizes small; use as sign test only.
- **C5 (P2)** Composite "successful outcome" = acquired ∨ IPO ∨ raised Series B+. Prediction: +5 to +10 pp.
- **C6 (P2)** Cumulative capital raised (log $) at T+3y. Prediction: significant positive; differ between Bay Area vs non-Bay Area.
- **C7 (P2)** Time-to-next-raise (survival analysis, Cox proportional hazards). Prediction: hazard ratio 1.2–1.5 for YC.
- **C8 (P3)** Unicorn (≥$1B valuation) outcome. Prediction: raw ~5.8% YC rate collapses to ~2× base rate after matching.
- **C9 (P2)** Discriminate "defunct" from "pivoted" by tracking issuer CIK continuation. Prediction: ~15% of apparent deaths are actually pivots.
- **C10 (P2)** Sensitivity to outcome-window length: repeat primary at T+2, T+3, T+5, T+7. Prediction: effect peaks at T+3, attenuates at T+7.

## Theme D — Heterogeneity

- **D1 (P1)** Effect by sector: SaaS vs fintech vs biotech vs hardware vs consumer. Prediction: largest in SaaS (where YC selects best); smallest in biotech.
- **D2 (P1)** Effect by batch size quintile (small early batches vs large late). Prediction: effect largest in smaller earlier batches (more attention per founder).
- **D3 (P1)** Effect by YC era: 2005–2012 (PG era), 2013–2019 (Altman era), 2020–2024 (pandemic + Tan era). Prediction: strongest in Altman era peak.
- **D4 (P2)** Effect by founder team size (1 vs 2 vs 3+). Prediction: effect strongest for 2-founder teams.
- **D5 (P2)** Effect by founder prior-startup experience (if extractable from long_description). Prediction: smaller effect for serial founders (ceiling).
- **D6 (P2)** Effect by raise size at batch entry (below vs above Form D median for sector). Prediction: larger effect for below-median entrants.
- **D7 (P2)** Effect by geography at founding (Bay Area vs other US vs international). Prediction: Bay Area shrinks effect due to ecosystem substitution.
- **D8 (P3)** Effect by industry newness (SaaS in 2007 vs SaaS in 2022). Prediction: larger effect in frontier sectors at their frontier moment.
- **D9 (P2)** Effect by founder demographic (solo-woman, all-female, multi-ethnic) where extractable. Prediction: larger effect for under-represented groups (consistent with Assenova & Amit 2024).
- **D10 (P2)** Causal forest CATE surface (Wager-Athey 2018). Prediction: identifiable leaves at sector × era × size.

## Theme E — Confound Sensitivity (MANDATORY)

- **E1 (P1)** Rosenbaum Γ bound for main ATE. Prediction: Γ = 1.3–1.8 (moderate robustness).
- **E2 (P1)** E-value (VanderWeele-Ding) for main ATE. Prediction: ~1.5–2.0.
- **E3 (P1)** Oster δ coefficient-stability bound. Prediction: δ > 1 (effect survives equal-selection assumption).
- **E4 (P1)** AET ratio (Altonji-Elder-Taber). Prediction: AET ratio > 1, supporting robustness.
- **E5 (P2)** Targeted sensitivity to single confounders (Bay Area concentration, founder ivy-league signal). Prediction: each explains at most 20% of ATE.
- **E6 (P1)** Report ATE with and without controls for unobserved ecosystem proxy (MSA VC density per Chen et al. 2010). Prediction: ATE drops by 20–40% when ecosystem controlled.
- **E7 (P2)** Placebo test: assign fake-YC status to random same-sector same-quarter Form D filers; should get null ATE. Prediction: placebo ATE < 2 pp and non-significant.
- **E8 (P2)** Bounds analysis à la Manski. Prediction: zero is excluded from bounds in primary spec but included in some heterogeneity subgroups.

## Theme F — Temporal Validity

- **F1 (P1)** Report ATE separately for era 2005–2012, 2013–2019, 2020–2024. Prediction: significant era differences (pattern per D3).
- **F2 (P2)** Test whether ATE correlates with VIX or VC-funding index contemporaneous with batch. Prediction: ATE larger in hot markets (selection intensifies).
- **F3 (P2)** Test stability across standard-deal regime shifts (2014 $120k, 2022 $500k). Prediction: effect stable — money is not the primary mechanism.
- **F4 (P2)** Leave-one-era-out: train on two eras, test on held-out era. Prediction: out-of-era performance drops ~30%.
- **F5 (P3)** Test effect on pre-AWS (2005–2008) vs post-AWS (2009+) batches. Prediction: effect larger post-AWS due to lower experimentation cost (Ewens-Nanda-Rhodes-Kropf 2018).

## Theme G — Feature Engineering

- **G1 (P1)** Embed YC long_description with sentence-BERT; use as covariate. Prediction: improves propensity model AUC by 2–4 pp.
- **G2 (P1)** Match Form D issuers by fuzzy company-name + state to YC roster; document match rate.
- **G3 (P2)** Founder LinkedIn signals (school rank, prior companies, seniority) — scrape only if TOS-permitted; else use proxies. LEAKY if scraped today; use only historical snapshot.
- **G4 (P2)** Tech-stack signal from website (via Wayback Machine snapshot at batch-start). Prediction: distinguishes SaaS sub-sectors.
- **G5 (P3)** Founder previous-company acquired/IPO flag. Prediction: strong covariate; reduces need for program treatment identification.
- **G6 (P2)** Form-D industryGroup → NAICS crosswalk. Prediction: adds 1–2 pp of propensity AUC.
- **G7 (P2)** Log of totalOfferingAmount — handle censoring at "Indefinite" flag.
- **G8 (P3)** Count of co-investors (from Form D relatedPersons). Prediction: proxies for syndicate strength.
- **G9 (P2)** MSA-level VC density (from Chen et al. 2010 or updated Pitchbook aggregates). Prediction: strongest single ecosystem confounder.
- **G10 (P3)** Founder twitter/X signal (pre-batch engagement). Prediction: leaky unless point-in-time snapshot.

## Theme H — Hyperparameters

- **H1 (P1)** Propensity score model: logistic vs gradient boosting vs random forest. Prediction: GBM has highest AUC but less interpretable balance; report all.
- **H2 (P2)** Caliper width sweep: {0.1, 0.2, 0.25, 0.5} × SD. Prediction: 0.2 is local minimum for bias+variance.
- **H3 (P2)** Number of neighbours: 1, 3, 5, 10. Prediction: 3–5 minimises MSE.
- **H4 (P2)** Trimming rules: drop top/bottom 1%, 5%, 10% of propensity. Prediction: 5% is standard and stable.
- **H5 (P2)** Outcome-regression specification: linear, random forest, gradient boosting. Prediction: AIPW estimates stable across these.
- **H6 (P2)** Causal forest hyperparameters (min-leaf size, subsample fraction) via honest-CV. Prediction: standard defaults acceptable.

## Theme I — Calibration

- **I1 (P1)** Calibration plot of propensity score vs realised treatment probability by decile. Prediction: well-calibrated in middle; over-confident tails.
- **I2 (P2)** Outcome model calibration (Platt, isotonic) before ATE reporting. Prediction: monotonic; small correction to ATE.
- **I3 (P2)** Report Brier score for outcome prediction on held-out sample. Prediction: ~0.15–0.20.
- **I4 (P3)** Test calibration by subgroup (sector, era) — is any subgroup miscalibrated? Prediction: biotech under-calibrated due to small cells.

## Theme J — Model Family

- **J1 (P1)** Logistic PSM as baseline.
- **J2 (P1)** Causal forest (grf) as ML alternative.
- **J3 (P2)** DoubleML with flexible nuisance.
- **J4 (P2)** Bayesian additive regression trees (BART) for CATE per Hill (2011).
- **J5 (P2)** Synthetic control for single batch × sector cells. Prediction: feasible for S12 tech (Coinbase/Instacart era) and similar distinct cells.
- **J6 (P3)** Entropy balancing (Hainmueller 2012) as a weighting alternative to matching.
- **J7 (P3)** Inverse-probability weighting (IPW) with stabilised weights. Prediction: higher variance than matching; used only as robustness.

## Theme K — Temporal Cross-Validation (MANDATORY)

- **K1 (P1)** Blocked time-series CV: train on 2005–2012, validate 2013–2015, test 2016–2019, report held-out 2020–2024. NEVER random k-fold.
- **K2 (P1)** Re-fit propensity model within each era; report era-specific ATE. Prediction: ATE drifts; reviewer will require this.
- **K3 (P1)** Out-of-time refutation: does treatment effect point estimate from 2005–2015 predict 2016–2024 ATE? Prediction: ~50% predictability.
- **K4 (P2)** Report era-specific propensity AUC to document distribution shift. Prediction: AUC varies 0.65–0.80 across eras.
- **K5 (P1)** Explicitly flag that 2022–2024 outcomes are partly right-censored; report both censored and imputed versions.

## Theme L — Interactions

- **L1 (P2)** Treatment × era interaction (paired with F1).
- **L2 (P2)** Treatment × sector interaction (paired with D1).
- **L3 (P2)** Treatment × founder experience (paired with D5).
- **L4 (P2)** Treatment × raise-size-at-entry (paired with D6).
- **L5 (P3)** Triple interaction: era × sector × treatment. Prediction: SaaS × 2015–2019 × YC is the peak cell.
- **L6 (P3)** Treatment × local-VC-density. Prediction: substitution (effect smaller in dense ecosystems).

## Theme M — Negative Controls (MANDATORY)

- **M1 (P1)** Pre-treatment outcome placebo: regress YC=1 on outcomes measured before batch start (e.g., founder's prior-company outcome). Should be null, or reveals selection.
- **M2 (P1)** Fake-treatment placebo: pick sector-and-quarter-matched Form D filers, assign them fake YC status, run full pipeline. Should produce null ATE. Prediction: ATE within ±2 pp of zero.
- **M3 (P1)** Alternative accelerator placebo: replace YC with another top accelerator (500 Startups, Techstars) using available public lists. Prediction: comparable ATE → effect is not YC-unique; different ATE → YC exceptional.
- **M4 (P2)** Rejected-from-YC proxy: identify companies that self-report YC rejection on Twitter/founder bios; treat them as "applied but untreated." LIMITATION: self-selection bias in who admits rejection.
- **M5 (P2)** Seasonal/geographic placebo: treat "founded in Bay Area same quarter" as the placebo treatment to check whether effect is just Bay Area.
- **M6 (P2)** Outcome placebo: use an outcome that should not be affected by YC (e.g., issuer state changes, filing-name typo rate). Prediction: null.
- **M7 (P1)** Randomisation inference: permute YC label across Form D-matched controls many times, compute ATE distribution, report p-value against realised ATE.

## Priority Summary
- **P1 (must do for any reportable result):** A1, A2, B1, B2, B3, B8, C1, C2, C3, C4, D1, D2, D3, E1, E2, E3, E4, E6, F1, G1, G2, H1, I1, J1, J2, K1, K2, K3, K5, M1, M2, M3, M7.
- **P2 (should do for reviewer):** most of B4–B10, C5–C10, D4–D10, E5, E7, E8, F2–F4, G3–G10, H2–H6, I2–I3, J3–J5, K4, L1–L4, M4–M6.
- **P3 (nice to have):** A6, D8, G5, G10, H-extensions, J6–J7, L5–L6, K-robustness.

Count: 95 hypotheses total across themes A–M.
