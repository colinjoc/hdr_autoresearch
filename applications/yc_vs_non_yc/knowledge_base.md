# Knowledge Base — YC, Accelerators, and Startup Outcome Priors

Reference document for Phase 1+. All figures cite source papers or published statistics; where a cite is marked "industry" the number should be treated as descriptive, not causal.

## 1. Accelerator Program Mechanics

### 1.1 The seed-accelerator template
Following Cohen (2013), Cohen & Hochberg (2014), and Cohen, Fehder, Hochberg & Murray (2019, *Research Policy*), a seed accelerator has five defining features:

1. **Cohort entry.** Fixed-date batch admission; companies start and finish together.
2. **Fixed duration.** Typically 10–13 weeks (3 months).
3. **Equity-for-services/capital.** A small cash investment (~$100k–$500k) for ~5–10% equity. For YC specifically, $500k on a post-money SAFE for 7% equity (since 2022; previously $125k for 7% from 2014, evolving from $20k for 6% at founding).
4. **Demo Day / pitch event.** A curated investor audience at program end.
5. **Mentor/alumni network.** Structured access to founders, VCs, and corporate contacts.

### 1.2 Cohort sizes (YC specifically)
- S05 (first YC batch, Summer 2005): 8 companies
- Through 2010: 20–40 per batch
- 2014–2016 plateau: ~120 per batch
- 2018–2019 peak: ~200 per batch
- 2022 pandemic remote batches: ~250–400 per batch
- 2023–2024 recalibration: ~230 per batch (semi-annual W and S)

(yc-oss JSON self-reports 5,690 companies across all batches S05 → W24.)

### 1.3 Treatment intensity within the program
- Weekly group office hours (GOH) — run by YC partners, mandatory.
- Occasional 1-on-1 office hours — on request.
- Tuesday dinners with guest speakers (pre-pandemic; replaced by weekly talks).
- Bookface / internal alumni network.
- Demo Day at week ~10; investor-only audience.

### 1.4 Selection process
- Application → written form → video → interview (10 minutes with 2–3 partners).
- Reported admit rates: ~1–2% historically, ~1.5% in recent batches (industry reports, YC blog). No peer-reviewed study has observed the admission score.

## 2. YC Timeline (2005 → 2024)

| Era | Key facts |
|---|---|
| 2005–2007 | Founded by Paul Graham, Jessica Livingston, Robert Morris, Trevor Blackwell. Based in Cambridge MA summers, Mountain View winters. Tiny batches. |
| 2008–2010 | Moved permanently to Mountain View. Standard Deal: $20k for 6–7%. Reddit (S05), Loopt (S05), Airbnb (W09), Dropbox (S07), Stripe (S09) from this era. |
| 2011–2013 | Standard Deal raised to $150k total ($20k + $130k SAFE from Yuri Milner/SV Angel). YC Fellowship launched (later discontinued). |
| 2014–2016 | Sam Altman becomes president (Feb 2014). Batch sizes grow to 100+. YC Research founded. |
| 2017–2019 | Launched Startup School (online). YC China briefly (later discontinued). Messaging: "YC is the undergraduate for founders." |
| 2020–2021 | Remote batches during pandemic. Batch sizes balloon to 300–400. ZIRP-era deployments. |
| 2022 | Garry Tan becomes president. Standard Deal moves to $500k ($125k for 7% + $375k uncapped MFN SAFE). Batch sizes reduce. |
| 2023–2024 | Return to in-person in SF. Heavy AI skew (reportedly ~60% of W24 batch is AI). |

## 3. Seed-Round Market Statistics (Context for Form D Control Pool)

(Sources: Pitchbook industry reports, AngelList Annual Reports, Kauffman Indicators, Gornall & Strebulaev (2020), Ewens & Farre-Mensa (2020, *RFS*).)

| Year | US median seed raise | US median Series A raise | Notes |
|---|---|---|---|
| 2010 | ~$0.5M | ~$3M | Pre-AngelList era |
| 2014 | ~$1.0M | ~$6M | Unicorn boom begins |
| 2018 | ~$1.5M | ~$8M | Stable plateau |
| 2021 | ~$2.5M | ~$15M | ZIRP peak |
| 2023 | ~$2.0M | ~$9M | Post-ZIRP reset |

**Dilution norms:** seed rounds typically 15–25% dilution; Series A 20–25%. YC's 7% is *before* seed — YC companies usually then raise a seed round, compounding dilution to ~25–30% by post-seed.

**Post-money YC valuations:** YC's standard deal implies ~$7.1M post-money at YC itself (7% for $500k means $7.14M post). Graduating YC companies typically raise seed at $10M–$20M post (industry reports).

## 4. Outcome Base Rates (Reference Priors)

### 4.1 US startup survival (BLS Business Employment Dynamics)
- **2 years:** ~67% of new employer firms survive
- **5 years:** ~50% (Headd 2003; BLS 2024 release)
- **10 years:** ~30%

### 4.2 VC-backed survival (Puri & Zarutskie 2012, *JoF*)
- VC-financed firms grow to larger scale than matched non-VC firms.
- But 5-year survival difference is modest (~5–10 pp) in PSM-matched samples.
- **They are NOT more profitable** — this is the canonical null.

### 4.3 Seed-to-Series-A conversion (industry — CB Insights, Crunchbase aggregates)
- Overall US seed-funded: ~35–40% raise Series A within 3 years (hot years); ~25% in cold years.
- YC batches (industry reports): claimed ~55–65% raise a priced seed or Series A within ~18 months. *Note: this is raw and selection-contaminated; do NOT use as causal.*

### 4.4 Exit rates (Kaplan & Strömberg 2003, 2009; Ritter 2024)
- US VC-backed IPO rate (fraction of funded startups): ~5–10% of Series-A-funded.
- Acquisition rate: ~15–30% of funded startups.
- Shutdown/defunct: ~40–60% over 10 years.

### 4.5 Unicorn rates
- Industry: ~1 in 500 US seed-funded startups become unicorns.
- YC raw: ~5.8% of 2010–2015 cohorts (industry reports, not peer-reviewed). This is ~28× the base rate, which is roughly why selection must be taken seriously.

## 5. Typical Effect Sizes Observed in Prior Studies

| Source | Treatment | Outcome | Effect |
|---|---|---|---|
| Gonzalez-Uribe & Leatherbee 2018 | Start-Up Chile + schooling (RDD) | Prob. follow-on financing | **+21 pp** (1.5× to 2× baseline) |
| Gonzalez-Uribe & Leatherbee 2018 | Same | Capital raised | **3× increase** |
| Kerr, Lerner & Schoar 2014 | Angel funding (RDD) | Survival at 4y | **+10 to +20 pp** |
| Kerr, Lerner & Schoar 2014 | Same | Follow-on financing | **~0, not significant** |
| Gonzalez-Uribe & Reyes 2021 | Top-ranked accelerator applicants | Employment growth | **+40%** |
| Hallen, Cohen & Bingham 2020 | Top accelerators | Time to raise | Faster by ~25% |
| Yu 2020 | Accelerator participation | Survival (5y) | **~0** |
| Yu 2020 | Same | Time to outcome | **Faster both success & failure** |
| Assenova & Amit 2024 | Structured curriculum (heterogeneous) | VC funding prob. | **+24 pp for bachelor-or-less; ~0 for PhD** |
| Chan, Patel & Phan 2020 | Which accelerator | Revenue variance | **11–14% of variance** |
| Bernstein et al. 2016 | VC monitoring (flight time IV) | Innovation + exits | Significant positive |
| Puri & Zarutskie 2012 | VC vs matched non-VC | Scale | Larger |
| Puri & Zarutskie 2012 | Same | Profitability | **~0** |
| Gompers et al. 2010 | Serial founder prior success | Next venture success | +12 pp (30% vs 18%) |
| Hsu 2004 | High-reputation VC | Acceptance probability | **3× more likely** |

**Implication for this project's prior:** for YC specifically we expect, under honest identification, a treatment effect on *follow-on financing probability* of **+0 to +15 pp**, on survival of **~0 to +10 pp**, and on *unicorn-rate* we expect the raw effect to **shrink dramatically** once matched.

## 6. Form D Institutional Facts

- Regulation D filings: private-offering exemption under Rule 504/506.
- Filed within 15 days of first sale.
- XML (primary_doc.xml) contains: issuer name, CIK, state, industry group, total offering amount, minimum investment, type of filer (LLC, C-corp, LP, etc.), relatedPersons.
- Not all startup raises file Form D (some use Rule 506(c) variants, some use convertible notes that are not securities under narrow readings). Coverage of seed rounds is partial.
- **Bernstein, Giroud & Townsend (2016)** and **Ewens & Farre-Mensa (2020)** use Form D as primary data source — validates it as a research-grade control universe.
- **Kwon, Lowry & Qian (2020)** document growing late-stage private investments; relevant for outcome-stage measurement.

## 7. Key Confounders to Remember

1. **Geography:** YC is 95%+ Bay Area post-program; Form D is national. Chen, Gompers, Kovner & Lerner (2010) show Bay Area has mechanical raise-size and success-rate advantages.
2. **Sector mix:** YC over-indexes software/SaaS/fintech; Form D is all sectors.
3. **Time trends:** 2021 ZIRP raised all valuations; 2022–23 reset cut them. Gompers et al. 2022 (COVID) shows cohort-composition shocks.
4. **Founder education and prior success:** Gompers et al. 2020 survey shows team matters most in VC decisions; YC selects heavily on team. Must include founder covariates or acknowledge omitted-variable bias.
5. **Founder homophily:** Gompers, Huang & Wang (2022); Bengtsson & Hsu (2015) — ethnic/educational/gender homophily affects network access independently of treatment.
6. **Experimentation cost shock:** Ewens, Nanda & Rhodes-Kropf (2018) — 2005-era vs 2015-era startups face fundamentally different cost structures.

## 8. Practical Constants for the Project

- **Treated sample size (YC):** ~5,690 companies per yc-oss.
- **Form D universe per quarter:** ~10,000–15,000 filings in 2010s, ~20,000+ in 2020s.
- **Approximate matched-control pool at 1:5:** 28,450 controls.
- **Expected batch count:** ~40 (S05 through W24 inclusive, 2 per year).
- **Minimum cell size per batch × sector (for safe batch × sector interactions):** ~30.
