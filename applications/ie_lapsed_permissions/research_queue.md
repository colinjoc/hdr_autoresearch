# Research Queue — lapsed permissions (100+ hypotheses)

Format: ID | hypothesis | prior (0-1) | mechanism | design variable | metric | baseline | status

H001 | Overall 2014-2019 residential PERMISSION lapse rate is 25-45% | 0.65 | broad real-options + post-crash credit constraint | cohort filter | share no BCMS match | 0 (null) | OPEN
H002 | Lapse rate is higher for 2014 grants than 2019 grants | 0.75 | 2014 cohort faced peak uncertainty + tighter credit | grant_year | Δ in lapse rate | same | OPEN
H003 | Lapse rate is higher for OUTLINE PERMISSION than PERMISSION | 0.85 | outline is not build-ready by design | app_type | lapse rate gap | same | OPEN
H004 | Lapse rate is lower for one-off houses than multi-unit | 0.70 | owner-occupier intent + low exercise cost | one_off flag | Δ | same | OPEN
H005 | Dublin LAs have lower lapse rate than non-Dublin | 0.60 | institutional PRS demand + Dublin market | dublin flag | Δ | same | OPEN
H006 | Largest LAs (DCC/FCC/SDCC/DLR) have lowest lapse | 0.55 | staff capacity + demand density | LA | rank | same | OPEN
H007 | Lapse rate varies by scheme-size band monotonically | 0.50 | fixed exercise costs | size band | shape | same | OPEN
H008 | SHD permissions lapse less than non-SHD in same years | 0.55 | self-selection of builder-ready projects | SHD flag | Δ | same | OPEN
H009 | Retention permissions lapse much more than PERMISSION | 0.80 | retention is remedial, not forward | app_type | rate | same | OPEN
H010 | Decision lag (Received→Decision) correlates with lapse | 0.50 | contested sites harder to build | lag | ρ | same | OPEN
H011 | Appealed permissions lapse less (selection bias) | 0.55 | appeal cost signal commitment | appeal flag | Δ | same | OPEN
H012 | Lapse rate for apartments > houses | 0.55 | higher capital intensity | land-use code | Δ | same | OPEN
H013 | Lapse rate bimodal by scheme size (tiny vs huge) | 0.35 | different frictions | size | bimodality | same | OPEN
H014 | Area-of-site predicts lapse beyond unit count | 0.45 | infra prerequisites | area | β | size alone | OPEN
H015 | Applicant-individual flag lowers lapse | 0.50 | self-build vs speculative | individual flag | Δ | same | OPEN
H016 | 2019 cohort shows right-censoring effect (lower observed lapse) | 0.70 | still has exercise window | grant_year | Δ | raw | OPEN
H017 | ExpiryDate-past-ETL cases are effectively 100% resolved | 0.75 | clock expired | expiry flag | Δ | same | OPEN
H018 | BCMS fuzzy-match adds 3-8pp | 0.60 | typos and format variants | string normaliser | Δ | exact | OPEN
H019 | Match rate higher for large schemes | 0.60 | better record-keeping | size | Δ match | same | OPEN
H020 | Refused cohort is ~0% BCMS-matched | 0.95 | no permission to build | decision | 0 | same | OPEN
H021 | Withdrawn applications rarely appear in BCMS | 0.95 | structurally impossible | status | ~0 | same | OPEN
H022 | Post-COVID grants show lower short-term commencement | 0.55 | supply-chain + cost shock | covid flag | Δ | same | OPEN
H023 | Pre-SHD vs SHD-era difference is small after controlling LA+size | 0.50 | regime matters less than site | sensitivity | regression | same | OPEN
H024 | Dublin apartment 50+ unit is lowest-lapse cell | 0.65 | institutional buyers | stratum | cell share | same | OPEN
H025 | Rural commuter-belt apartment permissions lapse heavily | 0.60 | no institutional demand | stratum | cell share | same | OPEN
H026 | Grant-to-commence distribution is right-skewed | 0.80 | most commence quickly once they start | time | skew | same | OPEN
H027 | Median time-to-commence is 18-30 months | 0.55 | planning+finance lead time | distribution | median | same | OPEN
H028 | 10% of eventually-commenced take >4 years | 0.60 | phased large schemes | distribution | P90 | same | OPEN
H029 | Large-scheme time-to-commence stochastically dominates small | 0.75 | infrastructure prerequisites | size | KS test | same | OPEN
H030 | 2015-16 grants have longest time-to-commence | 0.60 | post-crash recovery | year | median | same | OPEN
H031 | Weibull shape >1 (hazard increases with time) | 0.55 | as expiry approaches urgency rises | hazard | shape | same | OPEN
H032 | Cox proportional-hazards holds for large-scheme vs small | 0.40 | regime-switch at size threshold | stratified fit | PH test | same | OPEN
H033 | LA fixed effects explain 10-20% of lapse variance | 0.50 | LA enforcement heterogeneity | R² | share | 0 | OPEN
H034 | Size + type + LA + year explains >50% logit deviance | 0.50 | main structural predictors | deviance | ratio | 0 | OPEN
H035 | Gradient boosting beats logit by 2-5pp AUC | 0.55 | interactions matter | model | ΔAUC | logit | OPEN
H036 | Random forest beats GBM on small-N strata | 0.40 | bagging preferred when N small | model | ΔAUC | GBM | OPEN
H037 | Cox survival C-index >0.65 achievable | 0.50 | discriminable hazards | model | C-index | 0.5 | OPEN
H038 | Non-linear size effect: U-shaped (1-4 low, 5-49 high, 50+ low) | 0.35 | cost-structure regime | size | shape | monotone | OPEN
H039 | Grant-year linear in logit-lapse for 2014-2018 | 0.45 | smooth cycle | year | linearity | step | OPEN
H040 | Lapse rate discontinuous at 2020 due to COVID policy | 0.25 | policy extension granted? | year | break | smooth | OPEN
H041 | Lapse rate discontinuous at 2021 (LRD replaces SHD) | 0.20 | no direct mechanism | year | break | none | OPEN
H042 | DCC lapse rate < FCC lapse rate | 0.50 | DCC land is scarcer | LA pair | Δ | 0 | OPEN
H043 | Cork County lapse rate > Cork City | 0.55 | rural economics | LA pair | Δ | 0 | OPEN
H044 | Galway County highest lapse among Connacht | 0.45 | rural commuter-belt | LA | rank | same | OPEN
H045 | Donegal lapse rate > national | 0.55 | remote market | LA | Δ | same | OPEN
H046 | Wicklow lapse rate < national (Dublin spillover) | 0.50 | Dublin commuter demand | LA | Δ | same | OPEN
H047 | Meath and Kildare have low lapse | 0.55 | Dublin ring | LA | Δ | same | OPEN
H048 | Limerick and Waterford cities low lapse | 0.50 | revived urban centres | LA | Δ | same | OPEN
H049 | ABP-appealed permissions take longer to commence but rarely lapse | 0.50 | committed applicants | appeal flag | median-to-commence | unappealed | OPEN
H050 | Floor-area continuous predictor improves fit vs unit-count alone | 0.40 | area captures mix | feature | ΔAUC | none | OPEN
H051 | Forename-missing (corporate) has higher lapse for small schemes | 0.35 | speculative purchase | flag | Δ | with-forename | OPEN
H052 | Forename-missing (corporate) has lower lapse for large schemes | 0.45 | institutional builders | flag | Δ | same | OPEN
H053 | Applicant-surname frequency (large developer) predicts commencement | 0.55 | capacity | feature | ρ | none | OPEN
H054 | Withdrawals concentrated early (Received→Withdrawn < 6mo) | 0.70 | early pullout | time | distribution | 0 | OPEN
H055 | FI-request count correlates with longer time-to-commence | 0.55 | iterative fit | feature | ρ | none | OPEN
H056 | Land-use code "residential" vs other in permissions granted | 0.60 | many commercial-with-residential | code | Δ | same | OPEN
H057 | Permissions with 0 NumResidentialUnits are non-residential | 0.80 | data hygiene | filter | share | same | OPEN
H058 | Permissions with NumResidentialUnits=1 and one_off=No are ambiguous | 0.50 | data coding | feature | count | same | OPEN
H059 | Top 5% of permissions by size account for >50% of residential units | 0.75 | skewed stock | concentration | Lorenz | same | OPEN
H060 | Lapse rate in top-5% size stratum is decisive for aggregate units | 0.70 | big sites dominate | stratum | Δ | same | OPEN
H061 | Removing top-decile size changes aggregate lapse by <5pp | 0.35 | count vs units | filter | Δ | full | OPEN
H062 | Lapse rate in units-weighted terms differs from rate in applications-weighted | 0.85 | Simpson paradox possible | weighting | Δ | unweighted | OPEN
H063 | CSO BHQ15 granted-units (2019+) within 10% of national-register sum | 0.80 | double-count ok | cross-check | |Δ| | none | OPEN
H064 | CSO NDC02 commencements within 10% of BCMS-derived count | 0.70 | CSO draws from BCMS | cross-check | same | same | OPEN
H065 | Lapse rate stable under Wilson vs normal-approx CI | 0.95 | sample sizes large | CI | match | none | OPEN
H066 | Lapse rate stable under bootstrap sampling | 0.90 | large N | bootstrap | SE | param | OPEN
H067 | Logit coefficients stable under 5-fold CV | 0.85 | stable model | stability | SE | single split | OPEN
H068 | Cox coefficients pass proportional-hazards diagnostic | 0.40 | often fails in real data | diagnostic | Schoenfeld | none | OPEN
H069 | Size × Dublin interaction is significant | 0.60 | apartment PRS demand is Dublin-concentrated | interaction | p | none | OPEN
H070 | Size × app_type interaction is significant | 0.55 | OUTLINE large schemes disproportionately lapse | interaction | p | none | OPEN
H071 | Year × size interaction (2014 big schemes hardest hit) | 0.55 | post-crash big developers | interaction | p | none | OPEN
H072 | Year × LA interaction (Dublin recovers first) | 0.55 | heterogeneous cycle | interaction | p | none | OPEN
H073 | Non-Dublin 2014 grant × 50+ unit is highest-lapse cell | 0.65 | compound risk | stratum | rank | same | OPEN
H074 | Section 28 (2025) would have legalised >50% of unmatched | 0.45 | coverage of status-quo | subset | share | same | OPEN
H075 | If extension-granted dataset existed, extension rate ~30-50% | 0.55 | priors from practitioner reports | counterfactual | — | — | OPEN
H076 | No-BCMS-match for 2014 residential is ~35-50% | 0.55 | specific cohort | stat | value | — | OPEN
H077 | No-BCMS-match for 2019 residential is ~20-30% | 0.60 | specific cohort | stat | value | — | OPEN
H078 | Large-scheme lapse in 2014 > 50% | 0.50 | cyclical + capital-intensive | stratum | > threshold | — | OPEN
H079 | Large-scheme lapse in 2019 < 25% | 0.55 | institutional demand | stratum | < threshold | — | OPEN
H080 | Excluding one-offs raises aggregate lapse by 5-10pp | 0.70 | one-offs low-lapse | filter | Δ | full | OPEN
H081 | One-off lapse rate is 10-20% | 0.70 | personal circumstances | stratum | range | — | OPEN
H082 | Commence-before-grant events exist (BCMS match < Grant) | 0.25 | pre-permission groundworks | anomaly | count | 0 | OPEN
H083 | Commence-after-ExpiryDate matches indicate extension | 0.75 | must have been extended | derived | count | 0 | OPEN
H084 | E11 expiry-sensitive share (matched-after-expiry) = 5-15% | 0.55 | lower bound on extension rate | share | range | — | OPEN
H085 | County-level lapse rate correlates with population growth | 0.55 | demand pull | ecological | ρ | none | OPEN
H086 | County-level lapse rate correlates inversely with new-dwelling price | 0.55 | price = demand signal | ecological | ρ | none | OPEN
H087 | Top 10 applicant surnames account for 20%+ of 50+ unit permissions | 0.65 | concentration | concentration | share | — | OPEN
H088 | Repeat-applicant permissions lapse less | 0.55 | experienced builders | feature | Δ | first-time | OPEN
H089 | First-time applicant one-off lapse higher | 0.45 | amateur | stratum | Δ | same | OPEN
H090 | Planning fee waiver cases (housing body) lapse less | 0.60 | committed build | flag | Δ | same | OPEN
H091 | Decision "CONDITIONAL" vs "GRANT PERMISSION" has different lapse | 0.30 | label distinction minor | decision | Δ | none | OPEN
H092 | Permissions with Retention-code substring lapse differently | 0.40 | coding inconsistency | feature | Δ | same | OPEN
H093 | ITM coordinates presence predicts match (geocoded = more formal) | 0.40 | data-quality correlation | flag | Δ | same | OPEN
H094 | Eircode presence in BCMS predicts match to register | 0.50 | improved matching | method | Δ | — | OPEN
H095 | Cross-LA boundary projects (adjacent LAs) have higher lapse | 0.35 | coordination cost | feature | Δ | same | OPEN
H096 | Permissions in 2022-2024 inflation shock cohort will lapse heavily when observed in 2027+ | 0.55 | real-options forecast | forecast | range | — | OPEN
H097 | Phase B prediction: Dublin apartment 50-200u 2024 grant has commencement probability >0.7 | 0.60 | hot cell | stratum | P | — | OPEN
H098 | Phase B prediction: rural one-off one-unit has commencement probability >0.8 | 0.65 | owner-occupier | stratum | P | — | OPEN
H099 | Phase B prediction: non-Dublin 50+ unit apartment has commencement probability <0.5 | 0.55 | no institutional buyer | stratum | P | — | OPEN
H100 | Phase B prediction: OUTLINE large schemes have commencement probability <0.3 | 0.75 | structural | stratum | P | — | OPEN
H101 | Lookalike-placebo: top-propensity un-matched vs pool gap <5pp | 0.55 | channel check | diagnostic | pp | — | OPEN
H102 | Temporal split train 2014-2017 test 2018-2019 preserves C-index >0.6 | 0.55 | generalisation | temporal | C | — | OPEN
H103 | 2022 Amendment Act timing doesn't discontinue lapse hazard | 0.45 | no direct effect | event study | RDD | none | OPEN
H104 | Pre-2016 vs 2016+ PRS capital arrival shifts Dublin apartment rate | 0.55 | regime shift | event | Δ | smooth | OPEN
H105 | Appeal-status-finalised after grant delays commencement > appeal-not-lodged | 0.50 | cooling-off | feature | Δ median | same | OPEN
H106 | Conditions count (if parseable from description) predicts lapse | 0.35 | complex conditions | feature | ρ | none | OPEN
H107 | Development description length correlates with lapse | 0.30 | complex schemes | NLP | ρ | none | OPEN
H108 | Protected structure mentions correlate with longer times | 0.40 | heritage friction | NLP | Δ | none | OPEN
H109 | Site-Id reuse across permissions (multi-phase) predicts lower lapse | 0.55 | structural commit | feature | Δ | none | OPEN
H110 | Residential units bin 5-9 has highest lapse | 0.40 | awkward size | stratum | rank | same | OPEN
