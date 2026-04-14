# Knowledge Base — Housing Crash Prediction

Established facts assembled from `papers.csv`. Each fact includes a
primary citation (paper id from papers.csv).

## 1. Canonical crash magnitudes

### 1.1 The 2006-2012 Great Financial Crisis cycle (peak-to-trough, Case-Shiller metro)
- Las Vegas: −60% (peak 2006-08, trough 2012-03)
- Phoenix: −56% (peak 2006-06, trough 2011-09)
- Miami: −51% (peak 2006-12, trough 2011-04)
- Tampa: −48%
- San Diego: −42%
- San Francisco: −46% (peak 2006-05, trough 2011-03)
- Los Angeles: −42%
- Washington DC: −34%
- Boston: −20%
- New York: −27%
- Dallas (control metro): approximately flat, −3% peak-to-trough
- Denver: approximately flat
- **National Case-Shiller**: −27% (2006-07 peak to 2012-02 trough)

Citations: Shiller (2015) paper 3; Case-Shiller methodology (4);
Glaeser-Gyourko-Saiz (8) for cross-sectional variation; Mian-Sufi
(14) for magnitudes and credit interaction.

### 1.2 The 2021-2024 post-COVID cycle (peak-to-trough as of 2024-Q4)
- Austin TX: −22% (peak 2022-05)
- Boise ID: −18% (peak 2022-06)
- Phoenix AZ: −15% (peak 2022-06)
- Sacramento CA: −12%
- Las Vegas NV: −11%
- San Francisco: −14% (peak 2022-04)
- San Jose: −10%
- Seattle: −11%
- **US national**: modest 2022 decline then rebound; peak-to-trough
  ~ −4% on Case-Shiller national, far smaller than metro-level
  magnitudes.

The 2020-2022 run-up was concentrated in Sun Belt / remote-work-
friendly / migration-gaining metros. The subsequent decline followed
the same pattern. Citations: Heilbron-Sastry (45), Ramani-Bloom (46),
Haslag-Weagley (50), Rosen-Clancy-Ponchione (51), Mondragon-Wieland
(49), Gupta et al. (48).

## 2. Timing of leading indicators

### 2.1 Inventory build-up
- Active listings typically rise 3-9 months before the price decline
  onset in the metro concerned.
- In 2006-09: inventory began rising in Phoenix / Las Vegas / Miami in
  late 2005 / early 2006, 6-9 months before price peak.
- In 2022: active listings in Austin / Boise rose from early 2022,
  2-4 months before peak — a *shorter* lead because the Fed-rate
  shock was faster than the 2006-09 credit-driven downturn.
- Citations: Genesove-Mayer (24), Stein (26), Piazzesi-Schneider-
  Stroebel (25), Head-Lloyd-Ellis-Sun (66), Anenberg (145).

### 2.2 Days on market
- Median DOM doubles from roughly 25 to 50 days in about 6 months
  around the peak.
- Citations: Carrillo (147), Anenberg-Bayer (142), Merlo-Ortalo-Magné
  (146).

### 2.3 List-price reductions
- Share of active listings with a price reduction rises from baseline
  of 20% to 35-45% in the 3 months before the aggregate price peak.
- Citations: Carrillo (147).

### 2.4 Price acceleration
- A deceleration of month-on-month ZHVI growth from positive to flat
  typically occurs 2-4 months before the first outright month-on-month
  decline.
- This is a faster signal than inventory but less robust because noise
  is much larger at the metro-month level.

## 3. Price-level thresholds

### 3.1 Shiller 5.0 price-to-income threshold
- Shiller (2015) proposes 5.0× median metro household income as a
  rough bubble threshold for metro-level price medians.
- Pre-2006: Phoenix hit 5.8, Las Vegas 5.2, Miami 6.1, SF 9.4, Boston
  6.7. All crashed.
- Pre-2022: Boise hit 7.2, Austin 5.6, Phoenix 6.3, Sacramento 6.8. All
  crashed. SF, NY, LA had even higher ratios but did not decline as
  deeply — inconsistent with a pure price-to-income story.
- Thus: high price-to-income is necessary-ish but not sufficient.

### 3.2 Price-to-rent threshold
- Himmelberg-Mayer-Sinai (20): price-to-rent adjusted for user cost
  near 22-25 is a warning zone.
- Pre-2006: coastal metros 30-35, Phoenix/Vegas 28-32.
- Pre-2022: Phoenix 28, Austin 26, Boise 30.

### 3.3 Case-Shiller + Shiller (2005) 20% peak-to-trough
- Historical definition of a crash. Realised in 2006-09 in approximately
  30 of top-100 metros.

## 4. Supply-elasticity classification (Saiz 2010 tertiles)

**Inelastic (Saiz elasticity 0.5-1.0)**: LA, NY, SF, San Diego, Boston,
Miami, Seattle, DC, Portland. Prone to long cycles and deep peaks.

**Medium (1.0-2.0)**: Denver, Phoenix 2.5 (near-elastic), Chicago, Tampa.
Phoenix is interesting — high elasticity yet deep 2006-09 crash;
Nathanson-Zwick (22) explain via land-speculation mechanism.

**Elastic (2.0-4.0)**: Dallas, Houston, Atlanta, Indianapolis, Kansas
City. Minimal 2006-09 crash; also minimal 2021-22 run-up.

Key: Austin (2.1) and Boise (2.5) are *elastic* yet had large 2022
crashes — breaking the Saiz classification for this cycle.
Citations: Saiz (9), Glaeser-Gyourko-Saiz (8), Molloy-Nathanson-
Paciorek (121), Nathanson-Zwick (22), Davidoff (323) critique.

## 5. Household leverage / credit thresholds

### 5.1 Mian-Sufi ZIP-level threshold analysis
- ZIP codes in top quartile of 2002-05 subprime credit expansion saw
  2007-11 default rates 3× the bottom quartile and price declines
  1.5-2× larger. Citation: Mian-Sufi (13, 14).

### 5.2 Debt-to-income in 2022-24 cycle
- Post-Dodd-Frank QM rule caps DTI at 43%. Non-QM loans <10% of
  origination. Therefore Mian-Sufi-style subprime mechanism is weak in
  2022-24. The crash is not leverage-driven. Citation: Fuster-Hizmo-
  Lambie-Hanson (311).

### 5.3 Mortgage-rate delta
- 2004-06: 30-year fixed rose from 5.2% → 6.8% (+160 bp). Prices
  peaked shortly after.
- 2021-23: 30-year fixed rose from 2.7% → 7.8% (+510 bp). Price
  deceleration was faster and more synchronised across metros.
- The *rate of change* of mortgage rates is itself a predictor.
- Citations: Glaeser-Gottlieb-Gyourko (29), Bernanke-Kuttner (30),
  Aastveit-Anundsen (123).

## 6. Investor / speculation shares

- Non-occupant buyer share rose from 6% (1999) to 18% (2005) pre-GFC.
- Short-term flip share (resale <12 months) hit 8% in Phoenix 2005.
- 2021-22 investor-buyer share: 24% nationally (institutional +
  individual), peaked 28% in Atlanta, Phoenix, Las Vegas.
- Citations: Bayer-Geissler-Mangum-Roberts (27), Gao-Sockin-Xiong
  (28), Haughwout et al. (62), Chinco-Mayer (61), DeFusco-Nathanson-
  Zwick (318), Mills-Molloy-Zarutskie (315), Lambie-Hanson-Li-
  Slonkosky (317).

## 7. Dampening controls

- Dallas, Houston, Austin (pre-2019), Atlanta, Indianapolis: elastic
  supply, modest price runs, modest declines pre-2022.
- Detroit: distinct story — population decline rather than supply
  elasticity. Crashed in 2006-09 for different reasons (deindustrial-
  isation, population loss).
- Glaeser-Gyourko (6) durable-housing model: shrinking metros have
  *persistently* low prices not boom-bust cycles.

## 8. Foreclosure amplification

- Guren-McQuade (143): foreclosure feedback amplifies the initial
  price shock by roughly 25-45%.
- Campbell-Giglio-Pathak (144): foreclosed homes sell at ~27% discount
  to comparable non-distressed sales.
- Mian-Sufi-Trebbi (16): foreclosures account for ~1/3 of the 2007-10
  peak-to-trough decline.

## 9. 2022-24 cycle: what's different

- No subprime overhang; borrower FICO distribution much tighter.
- Major driver was remote-work demand shock + Fed rate shock, not
  credit-standard loosening.
- Property-insurance-market collapse in FL and coastal CA (2023-24)
  is a new mechanism not present in 2006-09. Citation: Mastrobuoni-
  Weinberg (335).
- Supply-elastic metros (Austin, Boise) experienced large booms and
  crashes — the Saiz classification is less informative in this cycle.
- Implication: a 2006-09-trained model without cycle dummy may over-
  weight credit features and underweight migration/remote-work features.

## 10. Published early-warning performance (baselines for our numbers)

- Jordà-Schularick-Taylor (101): joint credit-property-price boom → 40%
  conditional 3-year crisis probability. Baseline rate ~5%.
- Greenwood et al. (100): R-zone (credit+asset-price boom) → ~45%
  3-year crisis probability.
- Bluwstein et al. (208): ML AUC ~0.75 for banking crises. Logit AUC
  ~0.72. ML improvement modest.
- Beutel-List-von Schweinitz (207): ML *does not* significantly beat
  logit out-of-sample. This is the honest baseline.
- Fouliard-Howell-Rey (209): ensemble ML AUC ~0.78 at 3-year horizon.

We should report AUC and Brier on our held-out eras, *not* simulated
overall AUC, because the two held-out eras represent the substantive
generalisation question.

## 11. Data infrastructure facts

- Zillow ZHVI: ~900 metros, monthly, 2000-01 onward.
- Realtor.com inventory: ~500 metros, monthly, **2016-07 onward**.
  This means the Realtor.com inventory signal is unavailable for
  2006-09 — a critical methodological constraint. We can only test
  inventory signals on the 2022-24 cycle directly.
- Case-Shiller 20-city: monthly 1987-onward, full 2006-09 coverage.
- FRED 30-year fixed mortgage: weekly 1971-onward.
- Census ACS median income: 5-year rolling MSA estimates 2009-onward.
  For 2006-09 income denominators we will use Census 2000 + ACS 2006-10.

## 12. Pitfalls to avoid (documented in literature)

- **Look-ahead leakage in peak-to-trough definition** — defining
  "crash" using data not available at time t is the most common error.
- **Metro-identity leakage** — a model that memorises "Phoenix always
  crashes" will fail on Boise.
- **Synthetic momentum in Zillow smoothing** — ZHVI uses a 3-month
  trailing smoother. Using the smoothed series as a feature and as the
  crash definition leaks up to 3 months of future information.
- **2009 ACS availability** — incomes for 2006 are not in ACS 5-year
  tables (which start at 2009). Use Census 2000 + inter-census
  interpolation.
- **FHFA vs Case-Shiller vs ZHVI disagreement** — metros can disagree
  by 5-10% in peak-to-trough. We pre-commit to ZHVI as primary and use
  other two as robustness.
- **Repeated "this time is different" fallacy** — Reinhart-Rogoff (38),
  Kindleberger-Aliber (171). Do not exclude 2006-09 from training just
  because "it was a different mechanism".
