# Literature Review — Do YC Companies Outperform Non-YC at the Same Stage?

## (i) What is Settled

1. **Accelerators are a distinct institutional form.** Cohen (2013), Cohen & Hochberg (2014), and Cohen, Fehder, Hochberg & Murray (2019, *Research Policy*) establish that seed accelerators are cohort-based, fixed-duration, equity-for-services programs. They are not incubators (no cohort, no demo day) and not angel investors (no education component). This terminology is now universal.
2. **Accelerators correlate with regional VC supply.** Fehder & Hochberg (2014) show that when an accelerator enters a region, seed- and early-stage VC activity rises. The directionality is uncontested; magnitude is debated.
3. **Selection dominates raw comparisons.** Every serious study from Yu (2020, *Management Science*) through Assenova & Amit (2024, *SMJ*) concludes that naive YC-vs-non-YC comparisons are contaminated by selection. Pre-acceleration founders who are admitted to top programs were already differentially capable (Fehder 2024, *ASQ*; Kaplan, Sensoy & Strömberg 2009). This is the single strongest methodological consensus.
4. **Founder quality persists across ventures.** Gompers, Kovner, Lerner & Scharfstein (2010) show serial entrepreneurs with prior success succeed at ~30% vs ~18% for first-timers. YC selects disproportionately on founder signals (Gompers, Gornall, Kaplan & Strebulaev 2020), so any YC treatment effect must be identified *net* of founder persistence.
5. **Most VC return variation is luck** (Korteweg & Sorensen 2017), so excess outcomes at YC alumni are not automatically attributable to program quality.
6. **Cost-of-experimentation shock matters.** Ewens, Nanda & Rhodes-Kropf (2018) date the rise of the seed/accelerator model to the AWS-era collapse in fixed experimentation costs (~2005–2010). This is why YC emerged when it did and why cross-era YC comparisons are delicate.

## (ii) What is Contested — with Treatment-Effect Ranges

### Does accelerator participation causally improve outcomes?

| Study | Effect size reported | Identification strategy | Sign |
|---|---|---|---|
| Gonzalez-Uribe & Leatherbee (2018, *RFS*) | +21 pp prob. follow-on financing; 3× capital raised | RDD at Start-Up Chile admission threshold | + (only with schooling; basic services alone = 0) |
| Gonzalez-Uribe & Reyes (2021, *JFE*) | +40% employment for top applicants | RDD at admission score | + (concentrated in gazelles; 0 elsewhere) |
| Hallen, Cohen & Bingham (2020, *Organization Science*) | Accelerated faster fundraising & traction; only for top programs | Matched pair using near-admits | + (top programs only) |
| Yu (2020, *Management Science*) | Faster exit AND faster failure | Matched comparison | 0 on survival, + on speed |
| Fehder (2024, *ASQ*) | Effect attenuates after controlling for founding ecosystem | Ecosystem fixed effects | ~0 net of ecosystem |
| Assenova & Amit (2024, *SMJ*) | +24 pp VC funding prob. for less-educated founders; ~0 for PhDs | Coarsened exact match on 8,580 startups | Heterogeneous |
| Chan, Patel & Phan (2020, *SEJ*) | 11–14% of performance variance attributable to *which* accelerator | Variance decomposition | Heterogeneous |
| Winston-Smith & Hannigan (2015, DRUID) | Top accelerators push variance up both tails | Matched | + variance, mixed mean |

**Bottom line of the contested range:** mean treatment effect on follow-on financing probability is somewhere in **0 to +25 percentage points** depending on program, founder type, and identification strategy. Effects concentrate in **top programs** and in **under-resourced founders**. Survival effects are **not robustly positive**.

### Is YC specifically exceptional?

No peer-reviewed causal study of YC-the-single-program exists. The closest public-data studies are:
- A recent 2025 arXiv preprint on founder backgrounds at YC (non-causal, descriptive).
- Industry reports (CB Insights, Institutional Investor) showing high raw unicorn rates (~5.8% of 2010–2015 batches), but these have no counterfactual.

This is a genuine literature gap and the primary justification for the current project.

### Does VC value-add exist at all, or is it just selection?

- **For** value-add: Bernstein, Giroud & Townsend (2016, *JoF*) — exogenous flight-time variation increases monitoring and exits.
- **For** value-add: Hellmann & Puri (2002, *JoF*) — VC-backed firms professionalize faster.
- **Against** causal value-add: Sorensen (2007, *JoF*) — most measured VC effect is two-sided matching (better VCs to better startups).
- Network studies (Hochberg, Ljungqvist & Lu 2007) find real network effects but entangled with selection.

This background matters because the YC effect is a compound of **certification** (like VC reputation, Hsu 2004, *JoF*), **monitoring/mentorship** (Bernstein et al. 2016), and **network access** (Hochberg et al. 2007).

### The sceptical/null side (MUST take seriously)

- **Kerr, Lerner & Schoar (2014, *RFS*)** — the closest analogue: in angel financing RDD, outcomes improve on survival/employment but *no significant effect on follow-on financing around the discontinuity*. Follow-on funding is the most commonly claimed YC outcome; this paper is a direct caveat.
- **Yu (2020)** finds accelerators *accelerate failure* as well as success, so the reward function matters: if "survival at 5 y" is the outcome, YC may net zero.
- **Fehder (2024)** concludes that once ecosystem-of-origin is controlled, accelerator effects attenuate dramatically. For YC, ecosystem = "San Francisco Bay Area tech," which overlaps heavily with the strongest regional VC supply.
- **Puri & Zarutskie (2012, *JoF*)** show VC-backed firms are *not more profitable* than matched non-VC firms — larger, yes; better, no. This sets a strong sceptical prior against "YC firms are just better."
- **Meta-analyses** (Del Sarto & Di Minin 2020; Sharma & Arya 2025) find small effect sizes (Cohen's d ≈ 0.2) that shrink once selection controls are imposed.
- **Bertoni & Tykvová (2015)** and **Brander, Du & Hellmann (2015)** show that government accelerators/VCs *underperform*, which tells us the accelerator form alone is not magic.

**The sceptical prior the reviewer will apply:** if we claim a large positive YC effect, we must explain why we believe it when (a) the closest RCT-style paper (Kerr–Lerner–Schoar) finds null on follow-on financing, (b) Yu finds net-zero on survival, (c) Fehder finds ecosystem confounding is severe, and (d) most accelerator effects concentrate in founders YC does *not* select (lower-educated, less-networked) per Assenova & Amit (2024).

## (iii) What is Open — Gaps This Project Can Address

1. **No public-data causal study of Y Combinator specifically.** All causal accelerator studies use Start-Up Chile, Techstars-like programs, or pools of many accelerators. The question "is YC exceptional among accelerators, or typical?" is open.
2. **Matched Form-D control has not been applied to the full 2005–2024 YC universe.** Form D filings give us raise size and quarter for the entire US private-capital universe — a natural control pool for YC never attempted in the peer-reviewed literature.
3. **Temporal heterogeneity.** Early YC (2005–2012) when it was ~2% admit-rate and Demo Day was small vs late YC (2018–2024) at ~250 companies per batch is essentially two different programs. No study addresses this.
4. **Outcome definition sensitivity.** Prior studies split on survival vs follow-on raise vs acquisition vs IPO. We can report all four and reveal which effect the story hinges on.
5. **Sectoral heterogeneity.** YC over-indexes SaaS; the same treatment effect may not apply to biotech or hardware. Prior studies do not decompose by sector.
6. **Founder-cohort heterogeneity in a non-curriculum accelerator.** YC's treatment is light on structured curriculum (vs Start-Up Chile which was curriculum-heavy). Assenova & Amit (2024) predicts YC's structure should benefit *less* from the curriculum channel — so any YC effect must come from network/signal, not education.

## (iv) Methodological Priors

### Which design is appropriate?

| Design | Applicable? | Why |
|---|---|---|
| **RCT** | No | YC does not randomise admission. |
| **RDD on admission score** | No | Admission scores are not public. |
| **Instrumental variable** | Weak | No compelling instrument for YC admission that satisfies exclusion. Fehder & Hochberg use regional accelerator entry as an instrument for *regional* effects, not firm-level. Not applicable here. |
| **Propensity Score Matching** | **Yes, primary** | Treatment (YC = 1) observed; rich covariates (sector, quarter, stage, geography, raise size band via Form D). Standard method given data. |
| **Coarsened Exact Matching** | **Yes, robustness** | King-Nielsen (2019) critique: PSM can *increase* imbalance. CEM (Iacus-King-Porro 2012) is more robust; should be used as primary check. |
| **Mahalanobis matching** | Yes, robustness | Standard second check. |
| **DiD** | Limited | No pre-treatment outcome observable for most YC firms; founding date ≈ YC admission for many. |
| **Synthetic Control** | Yes, batch-level | We can treat a specific YC batch as a unit and synthesize from non-YC firms matched on batch-year covariates. Good for batch-era heterogeneity. |
| **Double ML** | Yes, robustness | Chernozhukov et al. (2018) — permits high-dim covariates (industry codes, description embeddings) while keeping root-n inference on ATE. |
| **Causal forest** | Yes, heterogeneity | Wager-Athey (2018) — for estimating CATE by sector/era/founder type. |

### Confound sensitivity — MANDATORY

1. **Rosenbaum Γ** (Rosenbaum 1987, 2002): report how large an unobserved confounder would have to be to overturn the result.
2. **E-value** (VanderWeele-Ding 2017): more communicable bound.
3. **Oster δ** (Oster 2019): coefficient-stability bound.
4. **Altonji-Elder-Taber ratio** (AET 2005): selection-on-unobservables-equals-selection-on-observables test.

### Negative controls — MANDATORY

The reviewer will ask for at least one of:
- **Fake treatment**: a pool of companies that applied to YC but were rejected, if any proxy exists (e.g., self-reported YC rejection in Crunchbase; LinkedIn-claimed "applied to YC"). If unavailable, document unavailability.
- **Pre-treatment outcome placebo**: regress YC=1 on outcomes measured *before* founding. Should be null.
- **Alternative accelerator placebo**: replace YC-treatment with a matched non-YC accelerator (e.g., 500 Startups, Techstars) to see whether the effect is "any top accelerator" or "YC specifically."

### Temporal CV — MANDATORY

Because seed-market regimes shift (2008 crash, 2014–15 unicorn boom, 2021 ZIRP spike, 2022–23 rates reset), all effect estimates **must** be reported with time-blocked cross-validation, not random folds. Report effect by era: 2005–2012, 2013–2019, 2020–2024.

### Inference

- Cluster standard errors at **batch** (Abadie et al. 2017). With ~40 batches, use wild-cluster bootstrap (Cameron, Gelbach & Miller 2008).
- Additional clustering at **sector** recommended.

### What NOT to do

- Report a single PSM ATE without CEM and Mahalanobis robustness — King & Nielsen (2019) critique demands this.
- Use random k-fold CV — violates temporal validity.
- Drop ambiguous outcomes (e.g., treat "status=Inactive" differently from "defunct") without a sensitivity analysis.
- Interpret raw YC alumni unicorn rate (~5.8%) as causal. The literature consensus since 2014 makes this indefensible.

## Summary Position

The literature supports a **prior of modest positive effect (0 to +15 pp on follow-on financing, smaller or null on survival) concentrated in top programs**, with strong heterogeneity by founder type and severe ecosystem confounding. The project's contribution is to test whether this prior holds when YC-specifically is the treatment and SEC Form D is the control. We should *expect* to find small or null effects once selection is properly addressed; a large positive effect requires extraordinary evidence and sensitivity-robustness.
