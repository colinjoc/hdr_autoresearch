# Publishability Review (retroactive Phase 0.25)

**Reviewer role:** grouchy stochastic-thermodynamics reviewer at a top-tier journal (PRE / J. Stat. Mech. / NJP).
**Reviewer stance:** independent of the earlier internal-consistency signoff. The signoff audited whether the abstract matches Section 2.3; this review audits whether the paper would survive peer review.
**Date:** 2026-04-19

---

## Part 1 — Five-point checklist

### 1. Novelty taxonomy

**Taxonomy: Synthesis + Application, dressed in places as "genuinely new".**

Stripped to its primitives, this paper does three things:
1. Catalogues four known inequality families (Landauer, Crooks, TUR/KUR/Fisher, Margolus–Levitin / Mandelstam–Tamm) and labels them F1–F4.
2. Re-applies each to a single named observable (functional-information rate `dI_func/dt`) and evaluates the resulting bound at one biological parameter point (*E. coli*, *T*=300 K, *Q̇*=10⁻¹² W).
3. Combines pairs of existing single-framework "corrections" — all of which are lifted from the literature — and reports 10 pairwise min-or-product combinations in Table 3.

The core constituent results all exist in prior work the paper itself cites:

- **Landauer baseline (A1):** Landauer 1961 verified by Bérut 2012 and Jun/Gavrilov/Bechhoefer 2014. No new content.
- **Finite-time correction (A1′, E02):** the 1/τ scaling is from Proesmans–Ehrich–Bechhoefer 2020 and Schmiedl–Seifert 2007. The paper claims an "asymmetric barrier" extension `B(r) = π²(1+r)²/(4r)` as new but the "derivation" (§3.2) is a two-line heuristic eigenvalue match, not a proof.
- **Non-equilibrium ΔF correction (E05):** exactly the Esposito–Van den Broeck 2011 / Kolchinsky–Wolpert 2017 "non-equilibrium free energy" result with `k_BT·D_KL`. Unchanged.
- **Housekeeping decomposition (E11):** Esposito & Van den Broeck 2010, Dechant–Sasa 2018, Koyuk–Seifert 2019. The paper applies it to `dI_func/dt` but does not derive anything new about the decomposition itself.
- **Correlation tightening (E19):** a chain-rule entropy subtraction — elementary from Cover & Thomas Ch. 4; the 10% number is a plug-in.
- **KUR (E25):** Van Vu & Hasegawa 2022 verbatim, with a `tanh` factor.
- **Crooks, TUR, Fisher TUR, Margolus–Levitin, Mandelstam–Tamm:** all standard.
- **INT09 tightest bound:** `min(corrected-F1, corrected-F3)` with `φ` factored into both. This is arithmetic on two prior-literature inequalities.

**Closest prior work that this paper is competing with (comparators a real reviewer will cite):**

1. **Wolpert, "Stochastic thermodynamics of computation," J. Phys. A 52 (2019) 193001.** A survey that already unifies Landauer + finite-time + fluctuation-theorem corrections for information processing. Does not treat functional information specifically, but the framework and most of the corrections are there.
2. **Horowitz & Gingrich, Nature Physics 16 (2020) 15.** Comprehensive review of TURs, including extensions across regimes; covers most of F3 in this paper.
3. **Kempes, Wolpert, Cohen, Pérez-Mercader, Phil. Trans. R. Soc. A 375 (2017) 20160343.** Applies Landauer-type bounds to cellular translation across organism size. Directly in competition with §5.4 biological applications.
4. **Kolchinsky 2022 (preprint), "Thermodynamic threshold for Darwinian evolution."** Already derives a minimum-entropy-production floor for Darwinian evolution — the paper's E09 result is a rederivation.
5. **Van Vu & Hasegawa, J. Phys. A 55 (2022) 013001.** Unified thermodynamic–kinetic uncertainty relation. The paper's "tightest F3 correction" is this result, unmodified.

**Verdict on novelty:** the claimed contribution is "unified hierarchy of thermodynamic speed limits on functional information gain." Once one removes (a) the re-labelling of known bounds, (b) the well-known corrections that are retrieved from the literature, and (c) the pairwise min-combinations that are arithmetic, what remains is: (i) `B(r) = π²(1+r)²/(4r)` for asymmetric barriers (one paragraph, heuristic, no proof), (ii) the observation that consistent application of the housekeeping fraction φ to both F1 and F3 gives a min bound ≈ 1.5 bits/s at one biological point, and (iii) a numerical tournament table. A grouchy reviewer calls this a *synthesis-plus-application paper*, not a *genuinely new bound*. It is publishable, but only in a venue that publishes synthesis papers, and only if framed as such.

### 2. Falsifiability

**Headline claims and their kill-outcomes:**

| Claim | Could-be-falsified-by |
|---|---|
| "The tightest combined bound at biological parameters is approximately 1.5 bits/s." | An empirical measurement of `dI_func/dt` in any system exceeding this value would falsify the bound — but the bound's sensitivity to φ (8 OOM) means the claim is effectively untestable. At φ=0.1 the bound is already 146 bits/s; falsification requires measurement to exceed whatever φ is chosen post hoc. |
| "Biological evolution is not thermodynamically limited at current metabolic budgets." | Demonstration of an organism evolving with `dI_func/dt` above the Landauer ceiling `Q̇/(k_BT ln 2)` would falsify; this is several orders of magnitude above anything ever observed, so the claim is safe — but also trivial. |
| "The quantum crossover `T*` is at ≈ 3 mK for biological energies." | Measurement of biological information processing at `T` < `T*` showing classical scaling would falsify. Not a realistic test. |
| "Corrections combine synergistically within a framework but intersect across frameworks." | This is a structural claim about the math of the bounds, not an empirical prediction — it is a theorem if proven and untestable otherwise. |
| "`B(r) = π²(1+r)²/(4r)` for asymmetric barriers." | A direct numerical simulation of optimal erasure in an asymmetric double-well potential, measuring `B` and comparing, would falsify. **This is the one sharp falsifiable derivation in the paper, and the paper does NOT run this test.** |

**Unfalsifiable-in-disguise patterns:**

- "Biology operates far below the tightest bound": true but uninformative because the bound is chosen to be loose (φ floats over 8 OOM, so the bound can always be pushed above any observed rate).
- "Corrections tighten the bound by up to eight orders of magnitude": this is not a prediction, it is a restatement of the parameter choice.
- "Establishes a hierarchy of increasingly tight thermodynamic speed limits": ordered inequalities are logical consequences of how the corrections are defined, not empirical claims.

**Verdict on falsifiability:** The only cleanly falsifiable headline is `B(r) = π²(1+r)²/(4r)`, and the paper never tests it. Every other numerical claim is either (a) safe by construction (parameter spans), (b) a theorem not a prediction, or (c) trivially true (nothing saturates the Landauer limit). **This is the most serious structural weakness of the paper.** A real reviewer at PRE will ask "what experiment or simulation, if it came out differently, would make you retract this paper?" and the honest answer is "none, except maybe E02, which we didn't test."

### 3. Load-bearing parameters

The headline "≈1.5 bits/s" depends on:

| Parameter | Value used | Literature uncertainty | Headline scaling | Impact |
|---|---|---|---|---|
| Housekeeping fraction φ | 0.01 | 10⁻³ to 10⁻¹ (acknowledged in §6.4 as "poorly constrained"); some sources place it higher still for mammalian cells | `bound ∝ φ²` when F3 binds | **Headline spans 8 OOM as φ moves.** This is catastrophic for the claim "1.5 bits/s." |
| Precision ε (in TUR/KUR) | 1.0 | Observable-dependent; no independent biological measurement for `dI_func/dt` | `bound ∝ 1/ε` | Unknown uncertainty — ε is not measured, it is chosen. |
| Dynamical activity `a` | 10¹² s⁻¹ | Varies by 3+ OOM across enzymes, ribosomes, polymerases | `bound ∝ tanh(σ_ex/(2k_B a))` — mild scaling, but enters multiplicatively | Probably 1–2 OOM uncertainty. |
| Barrier asymmetry ratio `r` | 10 | Implicitly assumed; not independently measured for specific enzymes | `B ∝ r/4` at large `r` | 1 OOM uncertainty in `B`. |
| `D_KL` (distance from equilibrium) | 5 | 0 to 20+ depending on NESS state; effectively a free parameter | Enters denominator `ln 2 + D_KL` | 1 OOM of tightening, bounded by free-energy budget. |
| Process time τ (for finite-time) | 10⁻³ s | 3+ OOM across biomolecular processes | `bound ∝ 1/(ln 2 + B/τ)` | 1–2 OOM. |
| *E. coli* metabolic power `Q̇` | 10⁻¹² W (also 2×10⁻¹² W in §4.1) | Inconsistent across the paper — abstract & §2.3 use 10⁻¹², §4.1 uses 2×10⁻¹². | Linear | 2× inconsistency inside the paper itself. |
| Temperature | 300 K (abstract, §2.3) vs 310 K (§4.1) | Physiological temperature is 310 K; the paper mixes the two. | Linear | 3% inconsistency. |

**Flagged parameters:**

- **φ is fatal.** The headline is "≈1.5 bits/s" but φ's literature uncertainty (≥3 OOM) with quadratic headline scaling means the paper is actually claiming "the tightest bound is somewhere between 0.015 and 146 bits/s" — four orders of magnitude, and the midpoint lies far above the actual evolutionary rate it is being compared to. A real reviewer reads the abstract's "approximately 1.5 bits/s" and immediately writes "this is a point estimate with φ-uncertainty spanning the claim's significant figures."
- **ε is a choice, not a measurement.** It is not honest to write `dI_func/dt ≤ σ/(2k_B ε)` and then set ε = 1 without explaining what "precision 1" means for the functional-information current of a living cell.
- **The 300/310 K and 10⁻¹²/2×10⁻¹² inconsistency is careless.** The signoff caught a factor-of-2 inconsistency in the Landauer baseline; the underlying cause is this parameter drift.

### 4. Venue fit

The paper does not name a target venue in §1 or in `proposal.md` (nor does a proposal file exist in the project directory). Candidates consistent with scope:

1. **Physical Review E (PRE) — Statistical Physics section.**
   - *Fit:* PRE publishes mid-scope stochastic-thermodynamics framework papers with biological motivation.
   - *Typical objection:* "The derivations rely on heuristic interpolations (B(r) eigenvalue match, §3.2) and point-estimate numerical evaluations. PRE requires either a rigorous derivation of a new bound or a substantial new application with validation. The present manuscript lacks both — it is a synthesis of known results applied to a single observable at a single parameter point."

2. **Journal of Statistical Mechanics: Theory and Experiment (J. Stat. Mech.).**
   - *Fit:* J. Stat. Mech. is more tolerant of synthesis-style papers and publishes long-form surveys.
   - *Typical objection:* "Much of the content is a review of Proesmans–Ehrich–Bechhoefer, Van Vu–Hasegawa, Esposito–Van den Broeck, and Kolchinsky–Wolpert. The novel contribution is too thin to warrant a research article; consider reformatting as a review (with different formatting requirements and a different target)."

3. **New Journal of Physics (NJP).**
   - *Fit:* NJP explicitly publishes interdisciplinary synthesis papers; the evolution-thermodynamics framing fits their remit.
   - *Typical objection:* "The biological validation is a single two-state Gillespie simulation and a comparison to *E. coli*. NJP will ask for at least one cross-disciplinary validation — e.g., against the Bérut 2012 data, Lan et al. 2012 chemotaxis data, or a published DMS dataset — before the paper competes against domain papers in computational biology."

**Poorly-fit venues to avoid (and likely desk-rejects):**
- *PRL* — too long, synthesis, no single crisp novel result.
- *Nature Physics / Nature Communications* — insufficient novelty; the "hierarchy" framing reads as a review.
- *PNAS biological sciences* — biological validation is too thin.

**Verdict on venue fit:** Reasonable fit at NJP or J. Stat. Mech. if the paper is reframed as a "synthesis and numerical comparison." Borderline at PRE, where a real reviewer will push back on novelty. No reasonable path to a flagship venue without a new rigorous derivation or new experimental validation.

### 5. Top three killer objections

**Objection 1 (FATAL): The headline bound's parameter uncertainty swamps its significant figures.**
- *Specific form:* The abstract claims "the tightest combined bound is approximately 1.5 bits/s" at "biological parameters." But the paper itself (§6.4, RV06) states the bound spans 8 orders of magnitude over the plausible range of the housekeeping fraction φ. A reviewer reads "1.5 bits/s" in the abstract and an "8 orders of magnitude" caveat on p.12 and concludes the headline is not supported.
- *Mitigation:* Replace the point estimate in the abstract with a range: "the tightest combined bound lies between 0.015 and 146 bits/s across the plausible range φ ∈ [10⁻³, 10⁻¹]." Add a figure (sensitivity plot over φ) as the paper's central graphical result. Reframe §3.8, §6.2, §7 to treat the φ-dependence as a result, not a caveat. This is a *writing fix*, not a *science fix*: the underlying math is fine.

**Objection 2 (MAJOR): Novelty is weak — most content is extension/synthesis of prior work the paper cites.**
- *Specific form:* "The four frameworks, five corrections, and ten pairwise combinations are all reproductions or elementary extensions of cited prior work. The `B(r)` asymmetric-barrier formula is the only candidate for a new analytical result, and it is derived heuristically in one paragraph (§3.2) with no numerical verification. What is the single piece of new physics in this paper that would not already be known to a reader of Wolpert 2019 plus Van Vu–Hasegawa 2022?"
- *Mitigation:* Two options.
  - **(a) Reframe.** Retitle and rewrite as "A unified numerical comparison of thermodynamic speed limits on functional information gain in biological systems." Submit to NJP or J. Stat. Mech. as a synthesis paper. This loses no technical content and positions the paper where it can land.
  - **(b) Tighten and verify `B(r)`.** Do a real variational derivation (minutes of work if genuine) plus a direct Fokker–Planck simulation of optimal erasure in an asymmetric double-well at `r ∈ {1, 3, 10, 30}`. Show the measured `B` matches the formula. Now the paper has *one* genuinely new verified result — thin, but real — and the synthesis content is supporting material.

**Objection 3 (MAJOR): No empirical validation beyond a two-state Gillespie toy.**
- *Specific form:* The paper derives bounds that are meant to apply to *E. coli*, protein evolution, ribosomal proofreading, CRISPR, brains, and the biosphere (Table 4). The only validation is RV03: a two-state Markov model with hand-picked rates, `N_traj = 10⁴`, confirming "`dH/dt` is below the bound" in three regimes. This proves only that the bounds are not violated by a system that is by construction thermodynamically consistent. It does not validate the biological applications or the numerical values. The Bérut 2012 data, the Lan 2012 data, and existing DMS datasets are cited as motivation but never used as validation.
- *Mitigation:* Add one independent empirical check. The cheapest is a recalculation using the actual Bérut 2012 measured dissipations at multiple cycle times to extract `B` and verify the finite-time penalty (the paper already does this for one data point in §5.7 — extend to the full Bérut dataset). Alternatively, use the Lan 2012 chemotaxis energy-speed-accuracy data to check whether the KUR+housekeeping bound is respected or saturated. Either move elevates the paper from "theoretical synthesis" to "theoretical synthesis with one independent empirical anchor."

**Summary of the three killer objections:**

| # | Severity | Objection | Addressable? |
|---|---|---|---|
| 1 | **FATAL** | Headline 1.5 bits/s is a point estimate inside an 8-OOM band. | Yes — writing-level fix: abstract and §3.8 reframe. |
| 2 | MAJOR | Novelty is thin; synthesis framing not admitted. | Yes — either reframe to NJP/JSTAT as synthesis, or shore up `B(r)` with a simulation. |
| 3 | MAJOR | No real-data validation beyond a toy simulation. | Yes — add Bérut-2012 or Lan-2012 comparison. |

Fatal + mitigable → verdict is not KILL but is not PROCEED on the current text.

---

## Part 2 — Recommended paper.md edits

Edits below are listed in priority order within each band. Line numbers reference the current `paper.md` (506 lines).

### ESSENTIAL (must do before any submission)

**E1. Abstract — replace the point estimate with a range.** (Line 7, §Abstract.)
- Current text: *"…the tightest combined bound is approximately 1.5 bits/s (sensitive to the poorly constrained housekeeping fraction φ, spanning approximately eight orders of magnitude across φ ∈ [10⁻⁴, 1])…"*
- Proposed: *"…the tightest combined bound lies between approximately 0.015 bits/s (at φ = 10⁻³) and 146 bits/s (at φ = 10⁻¹) across the plausible range of the biological housekeeping fraction φ. A point value of 1.5 bits/s obtains at φ = 10⁻². This range spans six to ten orders of magnitude below the quasistatic Landauer baseline of 3.48 × 10⁸ bits/s, depending on φ."*
- **Why:** Fixes Objection 1 at source. A reviewer reading the revised abstract understands up-front that φ is the dominant uncertainty and cannot accuse the authors of hiding it.

**E2. Abstract — qualify "eight orders of magnitude" claim.** (Line 7.)
- Current: *"…eight orders of magnitude below the quasistatic Landauer baseline of 3.48 × 10⁸ bits/s at the estimated biological parameters."*
- Proposed: *"…at the chosen point φ = 10⁻², approximately eight orders of magnitude below the quasistatic Landauer baseline; the tightening factor itself ranges from ~10³ to ~10¹⁰ across φ ∈ [10⁻³, 10⁻¹]."*
- **Why:** Fixes the overclaim flagged by the signoff (§Overclaiming 1) and by Objection 1 in this review.

**E3. Resolve the `Q̇` / `T` inconsistency globally.** (Lines 7, 40, 162.)
- Abstract/§2.3 use `T = 300` K and `Q̇ = 10⁻¹²` W; §4.1 uses `T = 300` K but `Q̇ = 2 × 10⁻¹²` W; `knowledge_base.md` standardisation says `T = 310` K, `Q̇ = 2 × 10⁻¹²` W.
- Proposed: pick one parameter set and use it everywhere. Recommended: `T = 310` K, `Q̇ = 2 × 10⁻¹²` W, `L = 9.2 × 10⁶` bp, `t_gen = 1200` s. Recompute Landauer baseline (3.48×10⁸ → about 6.9×10⁸ bits/s at `Q̇ = 2×10⁻¹²`, `T = 310`; double-check the factor-of-two signoff issue after harmonisation). Update abstract, §2.3, Table 1, Table 4, §7 principal-findings list.
- **Why:** Addresses signoff MAJOR (Section 2.3 vs Table 1 mismatch) and Objection 1 concerning parameter discipline.

**E4. Qualify the novelty framing in the introduction and conclusion.** (Lines 17, 372.)
- Current §1 (line 17): *"The central contribution of this work is to derive, compare, and combine these bounds into a unified hierarchy of thermodynamic speed limits…"*
- Proposed: *"The central contribution of this work is a systematic comparison and combination of four families of previously derived thermodynamic inequalities, evaluated numerically at biologically relevant parameter regimes. The constituent frameworks (Landauer 1961, Crooks 1999, the thermodynamic uncertainty relation of Barato & Seifert 2015, and the Margolus–Levitin/Mandelstam–Tamm quantum speed limits) and the individual corrections we apply (finite-time Landauer, Proesmans–Ehrich–Bechhoefer 2020; non-equilibrium free energy, Esposito–Van den Broeck 2011 and Kolchinsky–Wolpert 2017; housekeeping decomposition, Esposito–Van den Broeck 2010 and Dechant–Sasa 2018; kinetic uncertainty, Van Vu–Hasegawa 2022) are all established in the literature; we do not claim novel derivations of the underlying bounds. Our contributions are: (i) the systematic application of each framework to the single observable `dI_func/dt`; (ii) an extension of the finite-time Landauer coefficient `B` to asymmetric double-well potentials; (iii) a numerical tournament and interaction sweep evaluating which bound is rate-limiting in biological regimes; and (iv) a set of biological case studies (§5.4) that quantify the gap between each bound and measured rates."*
- **Why:** Admits the synthesis framing up front, so reviewers cannot accuse the paper of overclaiming novelty. This is the single most important edit for surviving peer review at PRE.

**E5. Reframe `B(r)` derivation as heuristic and add either a proof or a simulation check.** (§3.2, lines 65–83.)
- Current text claims "we derive the asymmetric extension as follows" followed by an eigenvalue-matching heuristic.
- Proposed minimum fix (writing only): change "we derive" to "we propose, by heuristic extension of the Schmiedl–Seifert eigenvalue argument," and add the sentence *"A rigorous variational derivation or direct numerical test of this formula is not attempted here and is left to future work."*
- Proposed stronger fix: run a Fokker–Planck simulation of optimal erasure in asymmetric double wells at `r ∈ {1, 3, 10, 30}` and add a one-panel figure showing measured `B(r)` versus the formula. This converts the one candidate novel result from "claim" to "claim + verification" and directly addresses Objection 2.
- **Why:** Signoff MAJOR (§3 Reproducibility: "Asymmetric barrier derivation not shown") and Objection 2 (novelty needs one verifiable new piece).

**E6. Add a φ-sensitivity figure to §3.8.** (After line 133.)
- Insert as Figure 1 a log-log plot of `dI_func/dt` bound vs φ across φ ∈ [10⁻⁴, 1], showing the quadratic scaling regime and the F1-binding regime. Overlay the estimated range of biological φ (shaded). Caption should state that "the headline point of 1.5 bits/s is the value at φ = 10⁻²; the biological range spans ~4 OOM."
- **Why:** Fixes signoff MAJOR ("no sensitivity plot") and fixes Objection 1 at the figure level — a reviewer who reads only figures cannot miss the uncertainty.

**E7. Add simulation details for RV03 to §4.4.** (Lines 173–175 already give some but are thin.)
- The paper gives rates, `N_traj = 10⁴`, and `t_max = 100` s. Add: random seed, the specific metric used for `dH/dt` (empirical `p_B(t)` time series? Last 10% average?), and a link or citation to supplementary materials or a public repository where the code lives.
- **Why:** Signoff MAJOR flagged this. Basic reproducibility.

### STRONGLY RECOMMENDED (do if the effort is moderate)

**S1. Extend §5.7 Bérut validation to cover more of the Bérut 2012 dataset.** (§5.7, lines 281–283.)
- Currently cites two points: the quasistatic limit and `τ = 5` ms. The Bérut dataset has more points. Extract the full `Q_diss(τ)` curve, fit `k_BT ln 2 + Bk_BT/τ` to extract `B` empirically, compare to the symmetric `B = π²` prediction and to the paper's `B(r)` formula at known asymmetry of the Bérut setup. This gives the paper one real-data validation beyond a toy simulation — Objection 3.

**S2. Add one biological data check in §5.4 using Lan 2012.** (After line 255.)
- Lan, Sartori, Neumann, Sourjik & Tu (Nature Physics 2012) measured the energy-speed-accuracy trade-off in *E. coli* chemotaxis with numerical values for dissipation rate and adaptation precision. Plug these into the INT09 bound and report whether the bound is saturated, tight, or loose. This is a 1-paragraph addition that lands Objection 3.

**S3. Qualify "law of increasing functional information."** (Lines 13, 372, 401.)
- Multiple occurrences of "law" without qualifier. Change to "proposed law" or "conjectured principle" throughout (signoff MINOR #6). Two-minute global find-replace.

**S4. Rewrite §6.2 "The Gap to Biology" to acknowledge that the gap is an artefact of bound choice.** (Lines 301–305.)
- Current text asserts "the gap reflects the fact that evolution is not a thermodynamically limited process." This is defensible but overstrong given Objection 1: for some choices of φ, the bound approaches measured rates. Add a sentence: *"At the lower end of the plausible φ range (φ ≈ 10⁻³), the combined bound of 0.015 bits/s is only ~30 OOM above the measured *E. coli* evolutionary rate; at the upper end (φ ≈ 10⁻¹), the bound of 146 bits/s is ~35 OOM above. The gap to biology is therefore only weakly constrained by our analysis."*

**S5. Cite uncited references or remove them.** (References list, lines 376–506.)
- Signoff flagged ~19 uncited references. Pick: either cite them in context where relevant (Adami in §1, Frank in §5.5, Still in §3.4/§6.1 are direct and easy wins) or delete. An uncited reference list is a red flag to any reviewer.

**S6. Add a pre-empt-reviewer paragraph to §6.5 Limitations.** (Lines 326–340.)
- Add a sixth numbered limitation: *"**Synthesis framing**: the constituent inequalities and corrections used in this work are established in prior literature (references above). The contribution of this work is the systematic application, numerical comparison, and biological interpretation of these existing inequalities for the single observable `dI_func/dt`. No new underlying fluctuation theorem, TUR, or speed limit is derived."*
- This is the classic "pre-empt the reviewer by admitting the weakness" move. Shuts down Objection 2.

### NICE TO HAVE (polish)

**N1. Add a master experiment-ID table as an appendix.** Experiment labels `E02`, `RV06`, `INT09` etc. appear throughout the paper with no key. Supplementary table mapping each ID to description, parameters, and result would help reviewers replicate the chain of reasoning (signoff MINOR #10).

**N2. Add citations for the kinetic-proofreading numbers in §5.4.** Specifically the "20 k_BT per step" and "3.3 bits of accuracy gain" (signoff Overclaiming #3). Both are in Hopfield 1974 and Sartori–Pigolotti 2015 already cited — just add inline citations after the numbers.

**N3. Three-way interaction test.** §3.7 argues synergy within F1; a paragraph or table evaluating the triple E02+E11+E25 (finite-time + housekeeping + KUR) would concretely answer "could the tightest bound be even tighter?" Signoff MINOR #13.

**N4. Standardise reference format.** Some references have full page ranges, some only first pages; journal-name italicisation is inconsistent. Minor but noticeable.

**N5. Rewrite the first line of §1 to open with the research question, not the concept.** Compact openings are rewarded. Try: *"How fast can functional information accumulate in a physical system? This question sits at the intersection of stochastic thermodynamics (Seifert 2012; Peliti and Pigolotti 2021) and the proposed law of increasing functional information (Wong et al. 2023), yet no systematic treatment exists."*

---

## Verdict

VERDICT: REFRAME

**Reasoning.** The paper is honest in its body — the §3.8 caveats, the `pre-empt-reviewer` flag in §6.5, and the extensive `RV` audit trail all show the authors know where the weaknesses are. The mathematics is correct. The biological applications are reasonable. But the *framing* is misaligned with the *content*: the abstract and introduction sell "genuinely new hierarchy of speed limits" when the content is "a systematic numerical synthesis of four families of pre-existing bounds, with one candidate new analytical result (`B(r)`) that is not rigorously derived or verified." A real reviewer at PRE will send this back for major revisions on novelty grounds; a real reviewer at NJP or J. Stat. Mech. will accept it cheerfully *if* it is framed as a synthesis paper with a sensitivity analysis instead of a point-estimate headline. The ESSENTIAL edits above convert the existing manuscript from a "likely reject" at PRE to a "minor revisions" at NJP/J. Stat. Mech., with no new science required. One of the STRONGLY RECOMMENDED edits (S1 or S2) adds enough empirical anchoring to compete at PRE if the author wishes. The KILL verdict is not warranted because the underlying technical content is correct and publishable in the right venue with the right framing.

VERDICT: REFRAME
