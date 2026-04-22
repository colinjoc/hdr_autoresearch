# Phase −0.5 Scope-Check: Candidate 6 — Layer-depth gradient of branching ratio in pretrained transformers

**Proposer's thesis.** σ_ℓ varies systematically with layer depth across GPT-2 small/medium/large/XL, Pythia, LLaMA-open-reproductions, OLMo. Hypothesis: early layers supercritical (amplification), late layers subcritical (integration).

**Verdict: REFRAME.** Absorb as §4 figure-pair of Candidate 1, with a dedicated methodology subsection on residual-stream-aware σ_ℓ definitions. Promote to its own project only if the proposer commits to the dual-definition methodological contribution as the headline novelty, not the layer-profile result itself. Concerns: (a) the observable is definitionally a slice of C1 rather than a new axis; (b) the residual-stream confound requires causal-isolation machinery to define σ_ℓ meaningfully, and that methodology is itself the interesting contribution; (c) the proposed kill ("σ_ℓ flat across depth") cannot meaningfully fail.

---

## 1. Novelty check against papers.csv and adjacent literature

- **No entry computes layer-resolved branching ratio σ_ℓ on transformers.** `lit_ml §9` flags "layer-resolved criticality analysis is the right response" as open work.
- **Closest prior art — layer-resolved spectral/Jacobian analysis.** [3005 Pennington-Schoenholz-Ganguli 2017], [3003 Xiao 2018], [3053 Pilarski 2023 VERIFY]: per-layer Jacobian spectrum at init for MLPs/CNNs. Recent web-accessible work (e.g. arXiv 2510.21770, arXiv 2502.15801, Tuan 2025 KAIST-HCAI workshop) reports U-shaped spectral-norm profiles in trained transformers — attention blocks show sharper singular-value decay than MLPs, and there is a boundary-aggressive / middle-stable pattern. Gap: spectral-norm is not σ, and no trained-transformer work frames the depth profile as a criticality observable.
- **MI circuit decomposition.** [3030 Meng ROME], [3031 Goldowsky-Dill path patching], [3025 Wang IOI]. All three work at within-layer circuit granularity, not the layer profile of a physics observable. ROME localises factual recall to mid-layer MLPs; IOI uses 26 specific heads in a small layer subset; path patching isolates residual-stream pathways rather than computing layer-wise dynamical observables. These establish that layer heterogeneity is real and causally structured — a positive prior for σ_ℓ varying with ℓ — but none is a σ-profile paper.
- **Neuroscience precedent.** [1040 Seshadri 2018] reports scale-invariant avalanches across cortical layers in awake mouse auditory cortex. This gives the candidate a natural audience Candidate 1 does not directly address.

**Bottom line:** the specific observable σ_ℓ(ℓ/N) on pretrained transformers is unpublished. Novelty is real but narrow.

## 2. Definitional concern: branching ratio in a residual-stream transformer

This is the single largest weakness and must be solved before the candidate is worth even a figure.

The residual update is `h_{ℓ+1} = h_ℓ + F_ℓ(h_ℓ)`. A naive σ_ℓ estimator that correlates activity at ℓ with activity at ℓ+1 reads back σ_ℓ ≈ 1+ε trivially, because `h_{ℓ+1}` is algebraically `h_ℓ` plus a perturbation. Candidate 1's aggregate σ is partially protected by threshold definitions varying per layer; per-layer σ_ℓ is directly confounded.

Three candidate definitions, ranked by defensibility:

1. **σ_ℓ from the layer-ℓ contribution F_ℓ(h_ℓ).** Define an event as an above-threshold component of F_ℓ(h_ℓ), not of h_ℓ. Isolates what layer ℓ adds to the stream. Consistent with [3023 Elhage 2021]'s additive residual-stream semantics. One hook per block.
2. **σ_ℓ via path patching (causal).** Perturb an activation at layer ℓ, count above-threshold changes at ℓ+1, average over perturbations. This is [3031]'s machinery applied for counting rather than pathway isolation. Handles the residual-stream confound by construction: patch-baseline difference is zero under null pass-through. Cost: O(d_model) perturbations × N layers × prompts. Tractable on GPT-2 small; tight on GPT-2 XL.
3. **σ_ℓ via MR estimator layer-to-layer.** [1019 Wilting-Priesemann 2018]. Fits exp(−ℓ/τ) to autocorrelation of per-layer activity counts — yields a *global* σ, not σ_ℓ, and does not fit the candidate's hypothesis.

**Recommendation:** use (1) as baseline, (2) as causal robustness check, report both. (1) alone invites the "it's correlational co-firing, not causal branching" objection from any MI reviewer on round 1; (2) alone explodes cost. Reporting both is the methodological contribution that could upgrade the candidate to standalone status.

## 3. Dependence on Candidate 1

Candidate 6 is downstream of C1 in three ways:

- **Infrastructure.** Same model cache, threshold sweep, CSN pipeline, MR estimator.
- **Evidence bar per layer.** The eight-item bar [`knowledge_base.md §5`] must be met *per layer*. Per-layer bootstrap CIs are wider than whole-network (fewer samples per stratum), so "layer 3 is supercritical" is a more demanding claim than the whole-network version.
- **Interpretive dependence.** If C1 finds no criticality, C6 becomes "layer profile of a non-critical observable" — fine as description but no longer about criticality. If C1 finds marginal criticality, the layer profile is the *mechanism* and belongs in that paper. If C1 finds strong criticality, C6 is the "where" follow-up.

In all three branches, C6 fits most naturally as §4 of C1. The proposal concedes this: "Natural supplement to Candidate 1 but worth its own scope-check because it is architecturally informative on its own."

**Standalone only if:** the residual-stream σ-definition methodology in §2 is the paper's main contribution, not the layer profile itself.

## 4. Cross-architecture ambition

Targeting GPT-2 S/M/L/XL + Pythia + LLaMA-open-reproductions + OLMo is over-scoped for a 1-week extension and duplicates Candidate 7's scope on Pythia.

**Reframing:** scope to five models, one representative per family: {GPT-2 S, GPT-2 XL, Pythia-1.4B, TinyLLaMA-1.1B, OLMo-1B}. Answers the universality question — same qualitative σ_ℓ(ℓ/N) across five, or architecture-specific profiles — without duplicating C7.

## 5. Falsifiability — tighter kills

Proposed kill ("σ_ℓ flat across depth within CI") cannot meaningfully fail: (i) layer 0 ingests tokens and layer N−1 feeds unembedding, so edge effects are guaranteed even under a Griffiths-phase null; (ii) prior spectral-norm work already shows U-shaped profiles; (iii) the residual-stream definitional bias (§2) makes the naive estimator trivially non-flat.

Tighter conditions:

- **K6a.** σ_ℓ profile is *monotone* in ℓ/N (supercritical→subcritical, as hypothesised). Reject if best-fit is U, n, or non-monotonic.
- **K6b.** σ_ℓ profile *consistent across the five-model panel* (rank correlation > 0.5 between any two models). Reject if profiles are model-specific.
- **K6c.** Causal-patched σ_ℓ (def 2) agrees with contribution-based σ_ℓ (def 1) within CI. Reject if they diverge by > 0.2.

## 6. Required controls (per knowledge_base.md §5)

Per-layer versions of the eight-item bar:

1. CSN fit + bootstrap p-value per layer — feasible.
2. α ≈ 3/2 per layer or report the layer where it is met — feasible.
3. γ = (β−1)/(α−1) scaling relation per layer — **likely fails ≥2-decade requirement**; per-layer duration range is short. **Concede this up front.**
4. Shape collapse per layer — same concern; secondary.
5. σ_ℓ = 1 ± CI at the critical-layer (if any).
6. Threshold plateau per layer.
7. At-init control per layer — **mandatory**; random init gives architecture-determined σ_ℓ (χ_1 predictable from [3001, 3002]); the training-to-init difference is the signature.
8. Neutral-null rejection — [2037 Martinello 2017] Griffiths phases produce layer-varying α without criticality.

Primary: 1, 2, 5, 6, 7. Secondary: 3, 4 (flagged as under-powered per-layer). Mandatory: 7, 8.

## 7. Venue

- **Standalone (methodology-forward, dual definition, 5-model panel):** ICML Workshop on Mechanistic Interpretability; NeurIPS ATTRIB workshop (if causal-patching is foregrounded); *Entropy* (crackling-noise framing).
- **Absorbed into C1 (recommended):** same venue as C1.

## 8. Cost on RTX 3060

- Def (1) on five-model panel: ~3 days incl. threshold sweeps.
- Def (2) causal patching on GPT-2 S: ~3 days.
- At-init controls on all five: ~1 day.
- Figures + writing: ~2 days.

**Total:** ~1.5 weeks, matches the proposal's ~1 week if (2) is scoped to one model only. Single-GPU-feasible.

## 9. Unflagged risk: Chinchilla-optimality

Pythia and OLMo release non-Chinchilla-optimal checkpoints; GPT-2 is heavily under-Chinchilla. A cross-architecture comparison that mixes training regimes may attribute training-completion effects to architecture. C3 and C7 address this directly; C6 should fix checkpoint-depth-per-model in its pre-registration or cite this as an explicit confound.

## 10. Final verdict

**REFRAME to: §4 figure-pair of Candidate 1**, with a dedicated methodology subsection on residual-stream-aware σ_ℓ definitions (1 + 2 in §2), a scoped-down five-model panel {GPT-2 S, GPT-2 XL, Pythia-1.4B, TinyLLaMA-1.1B, OLMo-1B}, and tightened kill conditions K6a/K6b/K6c.

Promote to standalone project only if the proposer commits to the dual-definition methodological contribution as the headline novelty, not the layer profile itself. Otherwise it is a strong figure in a bigger paper and does not justify a separate `applications/entropy_<slug>/`.

**Tag for `promoted.md`:** REFRAME (absorb as §4 of C1 unless methodology-paper reframing is adopted).
