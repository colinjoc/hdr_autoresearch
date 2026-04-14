# Literature Review — What Predicts Which Housing Markets Crash First?

## Scope

The question is metro-level, short-horizon (6-24 months), binary crash
prediction. Two natural evaluation eras: the 2006-2009 Great Financial
Crisis (GFC) and the 2022-2024 post-COVID cycle. Everything below has
to be consistent with both. Most of the literature is about the first.

Total citations in `papers.csv`: **350 rows** (exceeds 200-row floor).
Textbooks / book-length treatments: 17. Reviews: 15+. Papers with null
or negative results on crash prediction: 20.

---

## (i) What is settled

### 1. Price-to-income and price-to-rent ratios peak well before crashes
Shiller (2005, 2015), Case-Shiller (2003), Himmelberg-Mayer-Sinai
(2005), Davis-Lehnert-Martin (2008), Gallin (2006, 2008), Goodman-
Thibodeau (2008), Bogin-Doerner-Larson (2019). The classic Shiller 5.0
price-to-income heuristic captures the broad signal. The price-rent
ratio is stationary at the national level at a 5-7 year horizon
(Gallin 2008); deviations above 1.3-1.5× the long-run mean predict
subsequent corrections. These facts hold in both 2006-09 and 2022-24.

### 2. Household leverage and mortgage-credit expansion predict deeper busts
Mian-Sufi (2009, 2011, 2014, 2018), Mian-Sufi-Trebbi (2015), Mian-Rao-
Sufi (2013), Jordà-Schularick-Taylor (2015, 2016), Schularick-Taylor
(2012), Greenwood-Hanson-Shleifer-Sørensen (2022), Baron-Xiong (2017),
DiMaggio-Kermani (2017), Demyanyk-Van Hemert (2011). Counties with
faster 2002-05 credit growth experienced deeper 2007-10 price declines
and larger consumption drops. In long international panels, credit-
asset-price joint booms raise crisis probability to roughly 40% at a
3-year horizon.

### 3. Supply-elastic metros crash less deeply but shorter; supply-
inelastic crash deeper and longer
Glaeser-Gyourko-Saiz (2008), Saiz (2010), Glaeser-Gyourko (2005, 2018),
Paciorek (2013), Hilber-Vermeulen (2016). Boom-bust amplitudes in
supply-inelastic metros are measurably 2-3× those in elastic ones.

### 4. Inventory and days-on-market lead prices by 3-9 months
Genesove-Mayer (2001), Stein (1995), Head-Lloyd-Ellis-Sun (2014), Ngai-
Sheedy (2020), Piazzesi-Schneider-Stroebel (2020), Carrillo (2013),
Anenberg (2016), Anenberg-Bayer (2020), Andersen et al. (2022).
Inventory build-up, list-price reductions, and rising median days-on-
market are the most reliable *short-horizon* leading indicators.

### 5. Foreclosures are an amplification, not an origination, of crashes
Mian-Sufi-Trebbi (2015), Guren-McQuade (2020), Campbell-Giglio-Pathak
(2011), Anenberg-Kung (2014), Gerardi-Herkenhoff-Ohanian-Willen (2018),
Ganong-Noel (2020). Foreclosures account for ~1/3 of the peak-to-trough
decline *after* an initial price shock via a negative feedback loop.

### 6. Expectations are extrapolative
Case-Shiller (1988, 1990), Glaeser-Nathanson (2017), Armona-Fuster-
Zafar (2019), Bailey-Cao-Kuchler-Stroebel (2018), Bailey-Dávila-
Kuchler-Stroebel (2019), Greenwood-Shleifer (2014), Kuchler-Zafar
(2019), Burnside-Eichenbaum-Rebelo (2016). Homebuyer survey and social-
network evidence consistently show backward-looking extrapolation
dominates formation of price expectations. This creates the momentum
both forecasting models exploit and Shiller-style "irrational
exuberance" narratives emphasise.

---

## (ii) What is contested

### CONTESTED FINDING 1. Was the 2006-09 crash caused primarily by credit supply or by speculation/beliefs?

- **Credit-supply camp**: Mian-Sufi (2009, 2014, 2022), Favilukis-
  Ludvigson-Van Nieuwerburgh (2017), Justiniano-Primiceri-Tambalotti
  (2019), Corbae-Quintin (2015), Keys-Seru-Vig (2010, 2013), Griffin-
  Kruger-Maturana (2021), Kermani (2012). The 2000s credit expansion was
  concentrated among subprime / low-FICO borrowers and propagated
  through securitisation; remove the credit shock and the magnitude of
  the boom largely disappears.

- **Speculation/beliefs camp**: Adelino-Schoar-Severino (2016, 2018,
  2020), Albanesi-De Giorgi-Nosal (2022), Foote-Gerardi-Willen (2012),
  Glaeser-Gottlieb-Gyourko (2013), Greenwood-Nathanson (2017), Chinco-
  Mayer (2016), Gao-Sockin-Xiong (2020), DeFusco-Nathanson-Zwick (2022),
  Haughwout-Lee-Tracy-van der Klaauw (2011). Middle- and prime-FICO
  borrowers drove most of the absolute debt growth. Speculator /
  flipper / second-home-buyer shares track price runs at least as well
  as credit supply. Kaplan-Mitman-Violante (2020) attribute roughly
  half of the boom to belief shifts in a structural HANK model.

This matters because the two theories imply *different features for a
2022-24 prediction model*. Credit-supply says look at DTI, LTV,
subprime share, mortgage-product mix. Beliefs says look at flipping
share, non-occupant purchase share, price momentum, list-to-sale
ratios. The 2022-24 cycle happened with tight credit but strong
beliefs — closer to the Adelino-Schoar-Severino world. A model trained
on 2006-09 credit-supply features could fail on 2022-24.

### CONTESTED FINDING 2. Is supply elasticity a causal moderator of crashes, or correlated with demand?

- **Causal interpretation**: Glaeser-Gyourko-Saiz (2008), Saiz (2010),
  Paciorek (2013), Hilber-Vermeulen (2016). Supply-inelastic metros
  should crash harder because shocks cannot dissipate through quantity.

- **Critique**: Davidoff (2016) shows that the Saiz elasticity is
  correlated with essentially every important demand shifter
  (productivity, amenity value, demographic attractiveness). This
  undermines using elasticity as an instrument. Nathanson-Zwick (2018)
  argue the relationship is non-monotone: moderately elastic metros
  with land speculation had the most extreme cycles, not the most
  inelastic. Molloy-Nathanson-Paciorek (2022) show elasticities
  themselves have shifted over time, so using a 2005 Saiz elasticity
  for 2022-24 prediction is methodologically suspect.

This matters because supply elasticity is the single most-used cross-
metro moderator. If the coefficient on elasticity is contaminated by
demand factors, then metro-level heterogeneity attributed to
"elasticity" may not transfer across eras.

### CONTESTED FINDING 3. Can crashes be predicted out-of-sample at all?

- **Yes**: Greenwood-Hanson-Shleifer-Sørensen (2022), Jordà-
  Schularick-Taylor (2015), Bluwstein et al. (2023), Fouliard-Howell-
  Rey (2021), Alessi-Detken (2011). Joint credit-asset-price booms
  raise conditional crisis probability to ~40% at 3-year horizons; ML
  ensembles modestly improve AUC on long panels.

- **No / much weaker than claimed**: Schularick-Taylor (2012),
  Gourinchas-Obstfeld (2012), Reinhart-Rogoff (2008, 2009), Beutel-
  List-von Schweinitz (2019), Hand (2006), Holopainen-Sarlin (2017).
  Gourinchas-Obstfeld explicitly find that pre-2007 early-warning
  models performed poorly on the 2008 event. Beutel et al. find ML
  methods do *not* significantly outperform logit in out-of-sample
  banking-crisis prediction. Hand (2006) warns that classifier
  improvements routinely fail to generalise.

Our project lives inside this disagreement. We should report out-of-
sample AUC honestly, benchmark against both simple price-to-income
and against a regularised logit — not just against "no skill" — and
flag explicitly that many EW models have failed at exactly this task.

### CONTESTED FINDING 4. How much of the 2020-22 run-up was durable vs a temporary pandemic distortion?

- **Durable**: Mondragon-Wieland (2022), Gupta-Mittal-Peeters-Van
  Nieuwerburgh (2022), Brueckner-Kahn-Lin (2023), Delventhal-
  Parkhomenko (2023), Davis-Ghent-Gregory (2023). Remote-work-induced
  shifts in the bid-rent gradient are real equilibrium moves.

- **Temporary**: Heilbron-Sastry (2023), Bloom-Han-Liang (2024), FRB
  Dallas (Chen et al. 2022). Hybrid-work share has stabilised below
  initial estimates; much of the donut effect has partially reversed.
  Austin, Boise, Phoenix have already given back 15-22% of peak. Sun
  Belt price-growth shock was part-pandemic part-migration.

This affects the 2022-24 definition of "crash". A 20% decline from a
pandemic-bubble peak may be a return-to-trend, not a crash. The binary
label is sensitive to this.

### CONTESTED FINDING 5. Did "this time is different" ever hold? And related: is every housing bubble structurally similar?

- Reinhart-Rogoff (2009) and Kindleberger-Aliber (2011) argue bubbles
  share structural features across centuries.
- Adelino-Schoar-Severino (2018) and Glaeser-Nathanson (2017) argue the
  2006-09 crash had mechanism-specific features (MBS securitisation,
  subprime innovation) that make it non-representative.
- The 2022-24 cycle has *none* of the subprime structure but features
  strong remote-work demand, Fed-rate shock, and speculative momentum.

This matters: if each cycle is idiosyncratic, pooling 2006-09 and
2022-24 in training data may *degrade* out-of-sample performance.

---

## (iii) What is open

1. **Can a metro-level crash be predicted 6-12 months out-of-sample?**
   Most literature addresses national or cross-country crises. The
   metro-month panel has 50× more observations but weak individual-
   metro signal. Bork-Møller (2015) and Rapach-Strauss (2009) show
   state-level *return* forecasts have modest out-of-sample R², but no
   one has cleanly tested out-of-sample *binary crash prediction* at
   the metro-month level over both 2006-09 and 2022-24 windows.

2. **Which leading indicator fires first — inventory, days-on-market,
   list-price reductions, or price deceleration?** Theory (Genesove-
   Mayer; Stein; Carrillo) gives qualitative ordering but no tight
   quantitative timing estimate at the metro level.

3. **Do metros have *types* that systematically crash first?** Candidates:
   migration-gaining Sun Belt (Phoenix, Austin, Las Vegas, Boise)
   vs coastal-inelastic (SF, NYC). 2006-09 said both; 2022-24 says
   only the migration-gaining ones.

4. **What is the right crash threshold?** Shiller's 20% peak-to-trough
   is defined on eventual realisation and is not suited for real-time
   prediction. Rolling-window definitions (12m return ≤ −10%) are more
   suitable but the threshold is not pinned down.

5. **Regime-change detection**: Can an unsupervised indicator flag that
   a metro has *entered* a crash regime early enough for policy?
   Related to Sarlin (2013) on EW loss functions.

6. **Climate + insurance disruption channel**: Bakkensen-Barrage (2022),
   Baldauf-Garlappi-Yannelis (2020), Giglio et al. (2021). Post-2023
   property-insurance-market collapse in FL and CA is beginning to
   capitalise into prices. This is a novel mechanism absent from
   2006-09 models.

---

## (iv) Methodological priors

### Temporal CV is mandatory
Bergmeir-Benítez (2012), Cerqueira-Torgo-Mozetič (2020). Random-split
CV would leak future prices into training. We pre-commit to:
- Blocked rolling-origin CV with month-level folds
- Two designated holdout eras as *separate* test sets: 2006-09 and
  2022-24. Training folds never cross into either.
- No metro appears in both train and test in the same calendar month
  (to prevent metro-specific leakage via cross-sectional information).

### Metro fixed effects vs pooled
With ~500 metros and ~20 crash episodes in 2006-09, metro FE is
infeasible for most crash-probability targets. We will use metro-type
strata (supply-elasticity quartile; population-growth quartile) as
random effects instead.

### Early-warning threshold selection
Sarlin (2013): choose threshold to minimise a weighted sum of missed-
crisis and false-alarm costs, pre-specified. We pre-commit to equal
weights and also report a policymaker-favoured 2:1 miss:false-alarm
weighting.

### Model family
Start with penalised logit (interpretable baseline), compare to
LightGBM (Ke et al. 2017) with monotonicity constraints on sign-known
features (price-to-income ↑ → crash prob ↑), calibrate with Platt /
isotonic (Platt 1999, Niculescu-Mizil-Caruana 2005). Evaluate with
Brier score (Brier 1950) and proper scoring (Gneiting-Raftery 2007) —
AUC alone is not sufficient. Use SHAP (Lundberg-Lee 2017) for per-
metro attribution.

### Negative controls are mandatory
- Fake-crash placebo: shuffle crash labels across metros within year;
  model performance should collapse to chance.
- Metro-permutation test: permute metro identity at test time; model
  should not rely on metro-ID alone.
- Pre-crash placebo: predict 24 months before the actual 2006-09
  crash using the same framework; should show zero skill.

### Transfer / non-stationarity
Sugiyama-Kawanabe (2012), Lipton-Wang-Smola (2018), Pan-Yang (2010).
The 2006-09 → 2022-24 shift is covariate and label-prior shift
combined. We will explicitly evaluate:
- Train 2001-2011 only → test 2019-2024.
- Train 2001-2019 (excluding 2006-09 crash years) → test 2006-09.
- Train both eras with era dummy → test held-out last 12 months.

If the first two show ≥0.5 AUC loss vs the third, we have a transfer
problem and should report that as the headline, not a single AUC.

### Saturation check
After 350 citations, contributing-fetch rate is below 10%. New papers
in the queue are consolidation (foreign capital, investor activity,
climate) rather than adding new mechanisms. Calling Phase 0 saturated.
