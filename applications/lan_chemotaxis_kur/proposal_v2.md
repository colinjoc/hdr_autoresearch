**Target**: publication — primary venue: Biophysical Journal, fallback venue: Physical Review E

# Which stochastic-thermodynamic bound is tightest for *E. coli* chemotactic adaptation? A bound-tightness comparison on the Lan 2012 dataset with explicit uncertainty propagation

## 1. Question

Among the three stochastic-thermodynamic bounds most often invoked for cellular sensing — the thermodynamic uncertainty relation (TUR) of Barato–Seifert 2015, the kinetic uncertainty relation (KUR) of Van Vu–Hasegawa 2022, and the Landauer–Bennett cost-per-bit of Kempes et al. 2017 — which gives the tightest prediction when evaluated against the Lan, Sartori, Neumann, Sourjik & Tu 2012 energy-speed-accuracy dataset, and by how much? And — critically — does the KUR provide any tightening at all over the standard TUR on the steady-state chemotactic observables that dataset reports?

The v1 scope check correctly identified that the original "KUR saturation" framing was vulnerable to a lethal pre-objection: if TUR ≡ KUR on steady-state currents, the paper has no physics content. v2 makes that TUR-vs-KUR comparison the *first* deliverable, before any saturation claim. If KUR gives no numerical tightening, the paper narrows to a TUR-plus-housekeeping re-analysis with an honest scope.

## 2. Proposed contribution

**(a) Phase 0.5 gate: KUR-over-TUR tightness check.** Before any empirical claim, compute TUR and KUR at the Lan 2012 operating point analytically. For the specific class of bipartite biochemical sensing networks in Lan 2012 — adaptation via methylation dynamics coupled to receptor flux — determine whether the KUR's dynamical-activity factor gives strictly tighter bounds. If yes: proceed with three-way comparison (TUR, KUR, Landauer–Bennett). If no: pivot to TUR + housekeeping only, drop KUR from the headline.

**(b) Sartori 2014 differentiation.** Sartori, Granger, Lee, Horowitz, Tu & Wingreen (2014, *PLoS Comput. Biol.*) is the closest predecessor: they applied housekeeping entropy decomposition to sensory adaptation in bipartite-system form. Our contribution, if KUR passes (a): the three-way comparison (TUR, KUR, Landauer–Bennett) they did not do, on a specific dataset. If KUR fails (a): a tighter replication with explicit uncertainty propagation of φ through the Sartori 2014 housekeeping framework, which their paper did not quantify. Either path needs §2(a) to complete first.

**(c) Dataset extraction with preserved error bars.** The v1 reviewer flagged that digitising Fig. 3 of Lan 2012 "throws away the error bars." We commit to extracting the published error bars from the figure caption and supplementary (Lan 2012 reports ±SEM on every point, ∼10–15% on σ_phys, ∼20% on ε per point). Propagate these through every ratio we report. No claim is made without a 95% CI.

**(d) Proper uncertainty-propagated "tightness" definition.** Replace v1's arbitrary "ratio < 3" threshold with: a bound is **saturated** on a given data point if the bootstrap 95% CI of (observed σ·ε) contains the bound's numerical value. A bound **saturates across the Lan 2012 perturbation scan** if it is saturated at a majority of the 6–8 perturbation points. This is a non-gamed binary test.

**(e) Proper model-selection statistic.** Replace v1's "r² > 0.5" with pairwise ΔAIC between the three bounds as predictors of observed σ·ε across the perturbation scan. Report ΔAIC (with bootstrap CI) and which pair-wise comparisons are conclusive at the 2-log-likelihood-unit threshold. No "better correlation" hand-waving.

**(f) Housekeeping-fraction φ sensitivity analysis (the real headline risk).** Kempes 2017's φ carries >1 OOM uncertainty. Scan φ ∈ [10⁻³, 10⁻¹] and report how each of the three bounds moves. The paper's central finding *must* be stated in a form that is stable across this φ range, or the finding is not published.

## 3. Why now

Three developments make this tractable:
- **Van Vu & Hasegawa 2022** derived the kinetic uncertainty relation and explicitly compared to the TUR — but only on abstract Markov-chain models, not on published biological data.
- **Lan, Sartori, Neumann, Sourjik & Tu 2012** remains the canonical quantitative chemotaxis dataset; no full bound-tightness comparison has been published against it in the 14 years since.
- **Sartori et al. 2014** supplies the housekeeping-decomposition framework the comparison requires.

The v1 scope check's "already done by Sartori 2014" concern is specifically: Sartori et al. did housekeeping decomposition (yes), on bipartite systems (yes), with sensory-adaptation motivation (yes). But they did *not* compare TUR, KUR, and Landauer–Bennett on an empirical chemotactic dataset. That is the gap v2 closes.

## 4. Pre-registered binary kill-outcomes

- **(O1, gate) KUR > TUR tightness.** Analytical comparison yields either a strictly tighter KUR for Lan-2012-type observables (paper proceeds with three-way) or not (paper pivots to TUR + housekeeping only, drops KUR from title).
- **(O2) Dataset reachability.** The Lan 2012 Fig. 3 points and their published error bars are either extractable from open sources (arXiv preprint, supplementary, Lan-Tu 2016 review), or they are not. If not, the project is Phase 0.5 BLOCKED.
- **(O3) Bound saturation.** Each of the bounds that survives the gate in O1 either saturates (per §2(d) definition) across the perturbation scan, or does not. Each outcome is publishable.
- **(O4) Pairwise ΔAIC model selection.** The pairwise ΔAIC between the two or three surviving bounds either exceeds 2 log-likelihood units at the 95 % CI lower bound (selecting a winner), or does not (null result — data insufficient to discriminate). Each outcome is publishable.
- **(O5) φ sensitivity.** The headline claim either is stable across φ ∈ [10⁻³, 10⁻¹] to within a factor of 2, or it is not. If not, the headline is reformulated to name φ explicitly.

## 5. Named comparators and differentiation

- **Lan, Sartori, Neumann, Sourjik & Tu 2012 (*Nat. Phys.*)** — the dataset; no bound comparison.
- **Barato & Seifert 2015 (*PRL*)** — original TUR; no application to Lan 2012.
- **Van Vu & Hasegawa 2022 (*J. Phys. A*)** — KUR; abstract Markov chains only.
- **Hartich, Barato, Seifert 2014** — TUR-style on bipartite sensing; no KUR and no φ-uncertainty propagation.
- **Sartori, Granger, Lee, Horowitz, Tu & Wingreen 2014 (*PLoS Comput. Biol.*)** — **closest predecessor**, housekeeping decomposition on sensory adaptation, no three-way bound comparison and no empirical-dataset fit with proper uncertainty propagation. This paper is the one v1 missed; v2 cites it prominently.
- **Kempes, Wolpert, Cohen & Pérez-Mercader 2017 (*Phil. Trans. R. Soc. A*)** — Landauer-Bennett cost-per-bit estimates; cross-substrate; the φ source we use, with its known uncertainty.
- **Lan & Tu 2016 (*Rep. Prog. Phys.*) review** — if the 2016 review already compares bounds, the project is substantially redundant; Phase 0 lit review must read this review in full and pre-commit to the specific gap remaining.

The Phase 0 search terms will actively include the Sartori et al. 2014 paper, the Lan-Tu 2016 review, and the 2022–2026 Hasegawa / Van Vu / Horowitz / Dechant TUR-on-biology literature.

## 6. Target venue — Biophysical Journal primary

**Biophysical Journal** — publishes careful re-analyses of canonical biophysics datasets with rigorous uncertainty propagation. The v1 reviewer's specific recommendation; v2 adopts it.

**Fallback: PRE** — if the comparison produces a sharp new physics result (e.g., a novel saturation finding with falsifiable tolerance), PRE is defensible. If it produces a confirmatory or null result, PRE will desk-reject as incremental.

**NOT attempted:** PRL, Nature Physics — too narrow-scope for a bound comparison on one dataset.

## 7. Scope boundaries — what this paper is NOT

- NOT a new theorem. All bounds are used in published forms.
- NOT a measurement of new chemotactic data; we re-analyse Lan 2012.
- NOT a claim that chemotaxis "saturates the KUR" unless (O3) + the bootstrap CI support it explicitly. v1's pre-committed headline is withdrawn.
- NOT an extension to other biological substrates (ribosomes, CRISPR, transcription); the proposal is Lan-2012-specific.
- NOT a test of the `thermodynamic_info_limits` predecessor paper's INT09 bound in generality; INT09 is computed at the Lan operating point only as one data point in the three-way comparison.

## 8. Real-data rule (CLAUDE.md)

This project re-analyses real published experimental data (Lan et al. 2012). No synthetic data is generated at any stage. The real-data rule is satisfied by construction.
