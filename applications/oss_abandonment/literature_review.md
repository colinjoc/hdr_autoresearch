# Literature Review: Predicting Open-Source Project Abandonment

**230 citations** in `papers.csv` across three tranches:
- **1–80**: peer-reviewed academic (ICSE/FSE/TSE/EMSE/MSR/ICPC + books)
- **101–180**: industry reports, surveys, datasets, and canonical incident disclosures
- **201–270**: methodological toolkit (survival analysis, GBDT, temporal point processes, calibration, CPD, imbalance)

---

## 1. What's settled

Decades of GitHub/GHTorrent/GH Archive data (Grigorik 2012 [129]; Gousios 2014 [25, 130]; Kalliamvakou 2014/2016 [26, 27]) have produced a reasonably well-instrumented prediction discipline. Settled findings:

1. **Contributor concentration is extreme**. Truck factors of 1–2 are the modal case (Avelino 2016 [1, 163]; Ferreira 2019 [13]). ~65% of 133 studied projects had TF ≤ 2.
2. **Commit-frequency decay + issue-response-time degradation** are the strongest numerical predictors of the unmaintained state (Coelho 2018/2020 [4, 5, 162]; Xia 2022 [80]).
3. **Most contributors are one-shot**. 48–60% of contributors make a single commit (Pinto 2016 [34]; Steinmacher 2018 [33]). Project-level survival depends on a tiny elite whose departures matter disproportionately (Wang 2020 [52]; Rigby 2016 [44]).
4. **Corporate sponsorship extends life but introduces single-sponsor cliff-risk** (Valiev 2018/2020 [6, 40]; Germonprez 2018 [41]; Corbet/Kroah-Hartman [133, 134]).
5. **Dependency networks propagate abandonment downstream** (Decan 2018/2019 [36, 37]; Mens 2019 [70]; Census III 2022 [57, 101]).

## 2. What's contested

- **Maintainer burnout and toxicity** — survey-based (Tidelift [108–112]; Bock 2022 [50]) and sentiment proxies (Raman 2020 [8]; Miller 2019 [7]) — but causal identification weak.
- **Star and fork predictive content** — contested (Borges 2016/2018 [28, 29]).
- **Bus-factor algorithms** — at least three competing definitions with different failure modes.
- **Bot confound** — Dey 2020 [35] shows bot activity inflates metrics; most abandonment models don't filter consistently.
- **Calibrated probabilities at ecosystem scale** — most models curated; no ecosystem-wide calibrated per-repo risks reported.

## 3. Industry/empirical observations that academia under-captures

- Burnout prevalence is the leading signal, not activity (Tidelift 2020–2024 [108–112]: 60% considered quitting, 44% burnout, under-26 share collapsed 25%→10%).
- Single-maintainer critical-package tail dominates systemic risk (Census II [102]; xz-utils CVE-2024-3094 [136–139]; Log4Shell [140]; event-stream [143–144]; left-pad [142]; colors.js [145–146]).
- Compensation is a causal lever (Linux kernel [133–135]; Overney 2020 [169] on donations; Tidelift subscriptions [168, 175]).

## 4. Open questions a prediction paper can move

A. Unified survival model combining commit-decay + bus-factor + response-time + sentiment at 6- and 12-month horizons on GH-Archive-scale.
B. Causal effect of first toxic interaction on exit (IV / RD).
C. Stars/forks predictive content *after* conditioning on commit velocity.
D. Match of Census III critical packages to data-driven abandonment rankings.
E. Dependency-cascade early-warning distinct from per-project signals.
F. Bot-filtered vs raw activity — which dominates?
G. Concept-drift rate 2015–2019 vs 2021–2024 (generative-AI bots, corporate influx).

## 5. Methodology recommendation — four-horse Phase 1 tournament

1. **GBDT on engineered features (primary)** — LightGBM + XGBoost on tsfresh + handcrafted (decay, Gini, entropy, PELT change-points, truck factor, centrality). Optuna+Hyperband. TreeSHAP. Grinsztajn 2022 [255] and Fernández-Delgado 2014 [254] predict this wins.
2. **Discrete-time survival** — Cox PH with TVC + RSF on repo-week panel. Calibrated hazards; competing risks via Fine-Gray [205].
3. **Neural TPP** — Transformer Hawkes [226] on raw event stream. Captures burstiness.
4. **Stacked ensemble + isotonic calibration** — raw GBDT scores miscalibrated for rare events; isotonic [234–235] essential.

Eval: **PR-AUC (primary)**, Brier, reliability diagrams, strict rolling-origin temporal holdout.

## 6. Negative / positive controls

- **Negative control**: CHAOSS Project repos (chaoss/*) and actively-maintained Apache Foundation projects should NOT score as abandoned.
- **Positive control**: projects already on Libraries.io `Status=Unmaintained`, or archived during our window, should score high.
- **Bot-only-activity repos**: must flip to abandoned when human-commit filter applied. Validates label definition.

## 7. Target-variable definition (final)

**Abandonment at horizon T+H**: no human-authored commit by any contributor in the forward window `[T, T+H)`, given the repo had ≥20 human-authored commits in the 180 days ending at T, and was not `archived=true` before T.

Horizon: **H = 365 days**.

Supplementary positive signal: `archived` transition or Libraries.io `Status` flip to Unmaintained/Deprecated within the window.
