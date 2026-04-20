# Scope check — proposal_v2.md (Phase −0.5, round 2 of 3)

Reviewer role: grouchy physics referee, Phase 0.25 five-point checklist applied forward at proposal stage because v2 already names comparators and pre-registered tolerances.

---

## 1. Novelty taxonomy

**Category: Synthesis + Application**, not *Genuinely new*. v2 is honest about this, which helps.

The first-class Gaussianity test at each η is a measurement protocol that is largely a repackaging of work that already exists in the ML-dynamics literature — what is arguably new is only the *coupling* of that per-η Gaussianity measurement to a pre-registered Jarzynski validation on the same gridded η. Close comparators:

- **Simsekli, Sagun, Gurbuzbalaban (ICML 2019), "A Tail-Index Analysis of Stochastic Gradient Noise in Deep Neural Networks."** Directly measures the non-Gaussianity of per-example SGD gradient noise and argues α-stable tails dominate, which already establishes that Jarque–Bera-style tests reject Gaussianity at non-trivial η on real networks. v2 does not cite this paper; it should. The "first-class Gaussianity test at each η" is not new as a *measurement*; what is new is only using it as a gating criterion for a downstream Jarzynski check.
- **Panigrahi, Somani, Goyal, Netrapalli (2019), "Non-Gaussianity of Stochastic Gradient Noise."** Reaches the same qualitative conclusion via CLT-violation tests — also missing from v2's comparator list.
- **Xie, Sato, Sugiyama (ICLR 2021), "A Diffusion Theory For Deep Learning Dynamics."** Explicitly characterises when the Gaussian-diffusion approximation to SGD breaks, by batch size, η, and network depth. Overlaps the proposed Gaussianity-boundary map.

Verdict on 1: the Langevin-validity Gaussianity measurement is a known measurement type; v2 must either (a) cite these three papers and position itself as the first *pre-registered* combination of Gaussianity + Jarzynski at matched η — a defensible synthesis claim — or (b) concede that the Gaussianity axis is previously-measured and the novelty is confined to the Jarzynski + T_SGD_GNS consistency test.

---

## 2. Falsifiability

Four kill-outcomes in §4 are mostly genuinely binary, but three problems remain.

- **Gaussianity boundary — partially tautological.** The kill clause "OR the transition is undetectable at the tested sample size" is a free pass. "Either result is publishable" guarantees a publication but does *not* guarantee falsifiability. You must pre-register the minimum detectable effect: at what n per η is the Jarque-Bera test powered against a Mardia-skewness ≥ some specific value? Without that, the "undetectable" escape hatch renders the outcome unfalsifiable.
- **Jarzynski Tier-1 — the 2σ tolerance self-widens.** σ_log_R at n_traj = 10⁴ can be large if the work distribution is heavy-tailed (a direct consequence of non-Gaussian gradient noise — see point 3). "|log R| / σ_log_R ≤ 2.0" can be passed trivially by the thing failing. This is not tolerance-gaming by the author — it is a structural property of the test — but it *is* a tolerance that widens precisely when the null is most wrong. Fatal in present form; see mitigation.
- **T_SGD consistency — acceptable.** The [0.9, 1.1] ratio with a bootstrap-95 %-CI σ_W agreement is genuinely binary and not trivially passed. This is the cleanest of the four.
- **Regime-boundary transfer — acceptable but weak.** "To within one order of magnitude" is a binary claim but a very loose one; if η* on the quadratic is 10⁻³ you will declare "transfer" for any MNIST η* in [10⁻⁴, 10⁻²], which is almost the whole tested grid. That is tolerance-gaming. Tighten to half an order of magnitude or pre-register a specific MNIST η* prediction.

---

## 3. Load-bearing parameters

**The single number that makes the Jarzynski measurement uninformative is n_traj = 10⁴.**

Jarzynski estimator variance is notorious: σ̂²_log_R ∝ e^{var(βW)} / n_traj for Gaussian W, and is catastrophically worse for heavy-tailed W (Jarzynski 2006; Rohwer, Pastor-Satorras, Tavitian 2015). At large η — exactly the regime where v2's Gaussianity test is expected to *fail* — the variance of βW grows, σ̂_log_R explodes, and the Tier-1 criterion |log R| / σ_log_R ≤ 2.0 becomes satisfiable by noise alone. The interaction with §4 Tier-1 is the problem: the very condition the paper claims to detect (Langevin breakdown at large η) is the condition that makes its primary kill-threshold most permissive. The Tier-2 |log R| ≤ 0.1 threshold does not rescue this — at heavy-tailed W, log R itself is a biased estimator, not just a noisy one (Jarzynski bias goes like var(βW)/2n).

Mitigation required at Phase 0.25: pre-register a minimum effective-sample-size criterion, e.g. n_eff ≥ 1000 computed from the exponential-average weight distribution. If n_eff falls below that threshold at any η, declare the Jarzynski test uninformative at that η rather than "passing". Also pre-register n_traj scaling: 10⁴ for η ≤ 10⁻³, 10⁵ for η ∈ {10⁻², 10⁻¹} or declare n_eff saturation and stop.

---

## 4. Venue fit

**PRE is borderline for the reframed paper; JSTAT is a better fit.**

v2 has been reframed as a measurement-validation paper at perceptron scale with a single N~10⁵ boundary probe. PRE does publish this class (stochastic-thermodynamics validations at controlled scale — e.g. Bérut 2012, Koski et al. 2014) but it demands that the *thermodynamic object being measured* is interesting to the stat-mech readership on its own terms. "Does the Langevin approximation to SGD obey Jarzynski on a 50-D quadratic" is interesting to a stat-mech-meets-ML subfield but niche for PRE proper; the PRE editor will likely ask "what generic principle of stochastic thermodynamics does this advance?" and the honest answer is "none — we are validating an approximation's regime of applicability."

That is exactly the kind of paper **JSTAT short** publishes. JSTAT's stochastic-thermodynamics section regularly takes "here is the measured boundary of an approximation's validity" papers that PRE would desk-reject for being too methodological. The scope-restriction v2 accepts (§5e, §7) is JSTAT-sized, not PRE-sized.

Recommendation: swap the venue order. JSTAT primary, PRE fallback. This is consistent with v2's own honest scope restriction.

---

## 5. Top three killer objections

### Objection A — **FATAL**: the Tier-1 threshold self-widens at the regime it is meant to detect.

Stated above (§3). A reviewer at either PRE or JSTAT will flag this in the first page. Mitigation: pre-register n_eff ≥ 1000 as a *prerequisite for the test being informative at a given η*; declare "Jarzynski uninformative, Gaussianity breakdown confirmed" as a fifth kill-outcome distinct from "Jarzynski satisfied" and "Jarzynski violated". This is achievable with one paragraph of rewrite; without it the paper is not publishable.

### Objection B — **MAJOR**: Gaussianity measurement novelty is oversold.

Simsekli 2019, Panigrahi 2019, and Xie 2021 have all measured per-example gradient non-Gaussianity as a function of training regime. v2 positions this as "first-class", implying first-of-its-kind; it is not. Mitigation: cite the three comparators explicitly in §5 and reposition the Gaussianity test as "applied at the matched-η Jarzynski grid for the first time" — which is true and defensible. One-paragraph rewrite.

### Objection C — **MAJOR**: the Gibbs-distribution ΔF definition (§2d) is circular in the regime where the paper's own test expects it to fail.

The a-priori ΔF is computed from π_∞ ∝ exp(−L/T_SGD_GNS). T_SGD_GNS is derived from the Mandt 2017 formula, which itself assumes Langevin validity. In the large-η regime where Langevin breaks (the interesting regime), T_SGD_GNS is mis-estimated, so ΔF is mis-estimated, so the Jarzynski ratio test is testing two mis-estimated quantities against each other. v2 admits this in §7 but does not resolve it. Mitigation: pre-register that a Tier-1 failure at η*_Gauss accompanied by a T_SGD ratio outside [0.9, 1.1] is declared "framework breakdown confirmed" rather than "Jarzynski violated" — which is the scientifically honest outcome and is actually a *more publishable* result than what v2 currently frames as the success case.

---

## Verdict reasoning

v2 made real progress on v1's four flags: Gaussianity is now measured, thresholds are now theory-tied rather than arbitrary, scope is honestly restricted, and perceptron limits are acknowledged. The remaining objections are all addressable with ≤ 1 page of proposal rewrite — none require re-scoping the question or changing the testbed. This is a normal "tighten and proceed" situation, not a "reframe and come back" situation.

However, Objection A is fatal-as-stated and the n_eff mitigation has not yet been incorporated into the pre-registration. Per program.md, "any fatal objection without a clear mitigation plan makes the verdict REFRAME." A mitigation *path* exists and is short, but it is not in v2.

This is round 2 of 3. A round-3 non-PROCEED is auto-KILL. Given that (a) v2 already absorbed v1's four structural flags, (b) the remaining fatal objection has a one-paragraph fix, (c) the two major objections are both rewrites of existing sections rather than re-scopings, and (d) the venue swap (JSTAT primary) is a one-line change — the correct call is to proceed *conditional on* those three fixes being incorporated at Phase 0.25 rather than forcing a full round-3 rewrite.

Under a strict reading of program.md ("any fatal objection without a clear mitigation plan makes the verdict REFRAME"), the verdict is REFRAME. I take the strict reading. The author has demonstrated capacity to absorb feedback in one pass; a v3 with the three fixes above is cheap.

VERDICT: REFRAME

