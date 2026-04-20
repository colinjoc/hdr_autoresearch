# Research Queue: Asset Correlation Regimes

25 hypotheses ordered approximately by how central each is to the project's core question. Each hypothesis has:

- **Prior**: a 0–1 Bayesian prior that the hypothesis will be supported when tested on our 2004–2026 real-data panel.
- **Mechanism**: the causal story under which the hypothesis is true.
- **Design variable**: what we must compute to test it.
- **Expected outcome**: what we'd see if the hypothesis is true.

---

### H1 — SPY-GLD 90-day correlation in 2024-2026 exceeds its 2004-2019 median

- **Prior:** 0.80
- **Mechanism:** Post-COVID inflation shock + fiscal dominance narrative has simultaneously driven gold (debasement hedge) and equities (nominal earnings repricing) higher in tandem.
- **Design variable:** rolling 90-day Pearson correlation of SPY and GLD log returns. Compute the full time series 2004–2026, take the median over the 2004–2019 sub-sample, compare to the 2024-01-01 through today mean.
- **Expected outcome:** 2024–2026 average rolling correlation > 0.15, 2004–2019 median ≈ 0.00 to −0.05.

### H2 — SPY-BTC 90-day correlation in 2024-2026 exceeds SPY-BTC correlation in 2014-2019

- **Prior:** 0.90 (strongly supported in industry research already)
- **Mechanism:** Spot BTC ETF approval (Jan 2024) moved BTC into traditional asset-manager risk-on allocations, co-moving with tech equities.
- **Design variable:** rolling 90-day correlation of SPY and BTC-USD. Compare 2014-2019 mean vs 2024-2026 mean.
- **Expected outcome:** Post-ETF mean > 0.4; 2014-2019 mean ≈ 0.0 to 0.1.

### H3 — NDX-BTC correlation is higher than SPY-BTC correlation in 2024-2026

- **Prior:** 0.75
- **Mechanism:** BTC treated as tech-adjacent risk-on asset; Nasdaq (NDX/QQQ) is more tech-heavy than SPY.
- **Design variable:** rolling correlations QQQ-BTC vs SPY-BTC, 2024-2026.
- **Expected outcome:** QQQ-BTC > SPY-BTC by ~0.05–0.10 on average.

### H4 — Conditional on Fed-cutting regime, SPY-GLD correlation is historically positive

- **Prior:** 0.65
- **Mechanism:** Fed cuts support real asset prices (gold via lower real rates) and risk-asset prices (equities via discount rate) at once.
- **Design variable:** classify Fed regime from change in effective fed funds rate over the last 6 months; condition SPY-GLD rolling correlation on {cutting, steady, hiking} regimes.
- **Expected outcome:** mean SPY-GLD correlation in cutting regime > 0.1; in hiking regime < 0.0.

### H5 — Under high-geopolitical-risk regime (GPR top quartile), SPY-GLD correlation is negative

- **Prior:** 0.55
- **Mechanism:** Classic flight-to-quality: real geopolitical shocks hurt equities, benefit gold.
- **Design variable:** Caldara–Iacoviello GPR index; condition correlation on GPR quartile.
- **Expected outcome:** mean SPY-GLD correlation in top-GPR quartile is significantly lower than in bottom-GPR quartile.

### H6 — High-CPI regime (CPI YoY > 4%) drives positive SPY-GLD correlation

- **Prior:** 0.70
- **Mechanism:** Both assets rally when real rates fall / both assets fall when real rates rise — inflation shocks dominate.
- **Design variable:** condition SPY-GLD rolling correlation on CPI YoY bucket.
- **Expected outcome:** mean correlation in high-inflation buckets (>4%) > 0.1; in low-inflation buckets (<2%) ≤ 0.

### H7 — DXY weakening regime (6-month ΔDXY < −3%) drives positive SPY-GLD correlation

- **Prior:** 0.75
- **Mechanism:** Weak-dollar regime drives both gold (inverse to USD) and risk assets (easy global dollar liquidity) upward — the debasement-trade signature.
- **Design variable:** condition SPY-GLD correlation on 6-month ΔDXY.
- **Expected outcome:** correlation in weak-DXY regime > 0.1; in strong-DXY regime ≤ 0.

### H8 — SPY-WTI correlation has been persistently positive since 2008

- **Prior:** 0.80 (strong prior from Tang-Xiong)
- **Mechanism:** Commodity financialisation — index investment made oil a risk-on asset.
- **Design variable:** rolling SPY-WTI 90-day correlation, full sample.
- **Expected outcome:** pre-2008 median ≈ 0; 2009-2019 median > 0.2; 2020-2026 median > 0.3.

### H9 — Bloomberg Commodity Index (BCOM via DBC or similar ETF) shows same structural break in equity correlation around 2008

- **Prior:** 0.75
- **Mechanism:** Same financialisation story applied to the broad commodity basket.
- **Design variable:** DBC-SPY 90-day rolling correlation (DBC launched 2006; use GSG as backup).
- **Expected outcome:** visible regime shift in 2008 Chow test or Markov-switching.

### H10 — 2024-2026 SPY-GLD regime is NOT unusual conditional on (high CPI, weak DXY, cutting Fed)

- **Prior:** 0.60
- **Mechanism:** Once you condition on the macro regime, the 2024-2026 correlation pattern is just what the regime predicts — it's the regime that is unusual, not the correlation relationship.
- **Design variable:** regression: SPY-GLD correlation ~ CPI + ΔDXY + FedSlope + GPR + dummy(post-2024); test dummy coefficient.
- **Expected outcome:** dummy(post-2024) coefficient is small or insignificant after conditioning.

### H11 — 2024-2026 SPY-BTC regime IS unusual even conditional on macro state

- **Prior:** 0.75
- **Mechanism:** ETF approval is a structural institutional-adoption break, not a macro-regime effect.
- **Design variable:** same regression as H10 but for SPY-BTC.
- **Expected outcome:** dummy(post-Jan-2024) coefficient is large, positive, and significant even after controls.

### H12 — DCC-GARCH α and β for SPY-GLD give β > 0.9

- **Prior:** 0.85
- **Mechanism:** Standard high persistence of conditional correlations.
- **Design variable:** fit Engle DCC(1,1) on SPY-GLD log returns 2004-2026.
- **Expected outcome:** β ≈ 0.92–0.97; α ≈ 0.01–0.05.

### H13 — Spearman and Kendall rank correlations tell the same regime story as Pearson

- **Prior:** 0.85
- **Mechanism:** Rank correlations are more robust to outliers but should track Pearson at monthly frequency.
- **Design variable:** compute all three rolling correlations; compute time-series correlation between them.
- **Expected outcome:** time-series correlation among the three > 0.9; any disagreement concentrated in extreme-return months.

### H14 — Forbes-Rigobon heteroskedasticity correction reduces the apparent 2024-2026 correlation jump

- **Prior:** 0.55
- **Mechanism:** Higher vol regime mechanically inflates rolling correlations.
- **Design variable:** compute both raw and FR-adjusted correlations; take the difference in 2024-2026 vs 2004-2019.
- **Expected outcome:** FR-adjusted 2024-2026 correlations are 5-15% lower than raw; the regime-difference attenuates but does not vanish.

### H15 — A 2-state Markov-switching model identifies a "high-correlation" state that is materially more frequent post-2020

- **Prior:** 0.70
- **Mechanism:** Regime-switching captures the discrete shift in correlation behaviour.
- **Design variable:** fit MSM on rolling-correlation time series; extract state-frequency time series.
- **Expected outcome:** fraction of post-2020 months in "high-correlation" state > 60%; pre-2020 < 30%.

### H16 — 250-day rolling correlation gives a qualitatively similar regime story to 90-day

- **Prior:** 0.85
- **Mechanism:** Signal is stronger at longer horizons, noise drops away.
- **Design variable:** 250-day rolling correlation, 2004-2026.
- **Expected outcome:** 250-day series is smoother and shows the same regime shifts as 90-day, with a 6-month lag.

### H17 — Gold-BTC 90-day correlation is positive and elevated in 2024 but diverges in 2025-2026

- **Prior:** 0.70 (CME 2025 and industry reports say this is already observed)
- **Mechanism:** Up to late 2024 both traded as debasement hedges; after BTC's ETF inflows plateaued and gold broke higher, the two decoupled.
- **Design variable:** GLD-BTC 90-day correlation time series.
- **Expected outcome:** 2024 correlation ~0.3; 2025-2026 correlation falls toward zero or turns negative for sustained periods.

### H18 — BTC-equity correlation is higher at high frequencies (daily) than low frequencies (monthly) post-2024

- **Prior:** 0.65
- **Mechanism:** Short-horizon flows dominate co-movement; long-horizon returns reflect different fundamentals.
- **Design variable:** compute daily and monthly rolling correlations over 2024-2026.
- **Expected outcome:** daily correlation > monthly correlation by 0.1+ on average.

### H19 — VIX and SPY-GLD correlation are positively correlated

- **Prior:** 0.55
- **Mechanism:** Under panic (high VIX), liquidity-driven cross-asset selling makes everything correlate.
- **Design variable:** scatter of (rolling SPY-GLD correlation) vs (contemporaneous VIX level); regression.
- **Expected outcome:** slope positive, R² > 0.1.

### H20 — Gold-USD (DXY) correlation is reliably negative and more stable than gold-equity correlation

- **Prior:** 0.80
- **Mechanism:** Gold is denominated in USD; the mechanical accounting plus weak-dollar hedging story gives a stable inverse.
- **Design variable:** rolling GLD-UUP correlation (UUP tracks DXY); compare stability to GLD-SPY.
- **Expected outcome:** GLD-UUP correlation has smaller stdev across the sample than GLD-SPY.

### H21 — Inverting the question: during decoupling episodes (SPY-GLD correlation < −0.2), what macro variable is the best predictor?

- **Prior:** (descriptive) — ranking hypothesis: "GPR spike" rather than "Fed-hiking" or "weak DXY" or "high CPI" will rank first.
- **Mechanism:** Classic flight-to-quality.
- **Design variable:** feature-importance ranking (logistic regression or random forest) predicting decoupling month indicator from macro features.
- **Expected outcome:** GPR top-1 importance; fed-funds surprise second; inflation third.

### H22 — The 2022 inflation shock is the canonical example where gold did NOT decouple from equities

- **Prior:** 0.70
- **Mechanism:** Aggressive Fed hiking + rising real rates crushed both equities and gold; only USD cash performed as safe haven.
- **Design variable:** SPY-GLD correlation in 2022 calendar year vs prior decade.
- **Expected outcome:** 2022 correlation ≥ 0.3, with both assets drawing down ≥ 15% peak-to-trough at some point in the year.

### H23 — SPY-BTC correlation is strongly positive only when the S&P 500 is in an uptrend (risk-on regime)

- **Prior:** 0.50
- **Mechanism:** BTC-as-risk-on story predicts asymmetric correlation: shared upside rallies but non-shared downside panics where BTC falls harder.
- **Design variable:** rolling SPY-BTC correlation conditional on SPY 200-day trend.
- **Expected outcome:** risk-on regime correlation > risk-off regime correlation by 0.1+; no full decoupling in risk-off.

### H24 — The "all assets correlate in crises" fact has gotten stronger over time

- **Prior:** 0.60
- **Mechanism:** Financialisation, globalised liquidity, and common-factor intermediary leverage increase co-movement.
- **Design variable:** average pairwise correlation across {SPY, GLD, BTC, WTI, BCOM, DXY} in drawdown months vs non-drawdown months, per decade.
- **Expected outcome:** crisis-correlation gap grows from 2000s to 2010s to 2020s.

### H25 — Under a probit/logit model, P(decoupling month | regime variables) is near-monotonically increasing in GPR and decreasing in fiscal-deficit/GDP

- **Prior:** 0.50
- **Mechanism:** Decoupling requires a genuine risk shock (GPR high) that is not of fiscal origin (deficit low, not high).
- **Design variable:** probit of decoupling indicator on (GPR, CPI, ΔDXY, fed funds slope, deficit/GDP).
- **Expected outcome:** positive significant coefficient on GPR, negative significant coefficient on deficit/GDP.
