# Phase −0.5 Scope-Check — Candidate 10

**Candidate.** Semantically-conditioned Lyapunov. Use ROME [3027: Meng 2022] rank-one edits along known causally-important directions to compute directional Lyapunov exponents. Do these track random-perturbation Lyapunov, or show task-conditional structure?

**Verdict.** **REFRAME**. The honest experiment is not "ROME direction vs random direction" (which is tautological) but "ROME direction vs matched-subspace / matched-norm random direction, across critical-vs-off-critical models, with the directional spectrum as the observable". In that form it survives; in the original form it does not.

---

## 1. The tautology problem (primary concern)

ROME directions are *defined* as the rank-one MLP write that maximally causally-mediates a target token prediction, obtained by solving an L2-minimal edit to flip a (subject, relation, object) triple [Meng 2022, `arXiv:2202.05262`]. By construction a ROME direction is the direction along which a rank-one perturbation maximally changes downstream logits on the target prompt family. Therefore: a perturbation along a ROME direction will, by construction, produce a larger logit-response than the expectation of a uniform random same-norm perturbation. Claiming that response as "directional Lyapunov > random Lyapunov" is circular — it restates the optimisation objective of the ROME solver in Lyapunov language. That is not a measurement of chaos or edge-of-chaos, it is a measurement that ROME worked.

The current candidate text ("If directional Lyapunov is independent of direction, the semantic-structure claim dies") inverts the falsifiability: the alternative hypothesis is the tautological one, and the null is the expected-but-uninteresting "ROME did its job". A paper built on this framing is publishable only as a "ROME replication with a spectral lens" — which nobody needs.

**Reframe that dissolves the tautology.** The interesting observables are:

- **Directional Lyapunov *spectrum* vs criticality.** For a fixed ROME direction, measure λ(ROME, input, layer) across many inputs and across models at different |σ − 1| (using the nanoGPT skip-connection sweep from Candidate 2). Prediction from criticality theory: λ(direction) is *compressed toward zero* near criticality regardless of direction choice. A ROME direction showing λ > 0 in an off-critical model and λ ≈ 0 in a near-critical model *is* a criticality claim; a ROME direction simply producing λ > 0 is not.
- **Matched-subspace / matched-norm random control.** The cleaner control is not "a fresh isotropic random perturbation" but "a perturbation sampled uniformly from the ||·||-matched shell of the ROME-direction's *subspace* — i.e. the same (u, v) rank-one structure but with u, v drawn from the MLP-column / token-embedding distributions rather than optimised" [cf. the standard "mean-ablation" and "random-rank-one-ablation" controls in the activation-patching literature, Zhang & Nanda 2024]. Without this, you are comparing an ℓ²-optimised direction to a Gaussian blob and will always see a gap.
- **Off-manifold ROME directions.** ROME solves per (subject, relation, object). A trained ROME direction for "Paris is the capital of France" should behave as a causally-important direction *only* on prompts that invoke the subject. Feed the same direction on unrelated prompts: does its Lyapunov response drop to the matched-random-baseline level? If yes, the "semantic conditioning" claim is operationalised as a (direction × prompt)-interaction effect, which is not circular. If no, the ROME direction is causally important in a prompt-agnostic way and the whole framing collapses into generic sensitivity.

This is the kernel of a defensible paper. The original framing is not.

## 2. 2024–2026 precedent — is this already done?

Three 2024–2026 arXiv papers touch the same space and bound the novelty claim:

1. **"Cognitive Activation and Chaotic Dynamics in Large Language Models", `arXiv:2503.13530`**. Introduces a "Quasi-Lyapunov Exponent" per layer, measures chaotic characteristics across layers, argues MLP contribution > attention contribution. Uses "minor initial value perturbations" — random-style, not ROME-directed, not task-conditional, no interpretability bridge. Direct competitor on the layer-resolved Lyapunov observable; non-overlapping on the ROME axis.
2. **"Structural Sensitivity in Compressed Transformers", `arXiv:2603.20991`**. Lyapunov-stability analysis of compression-induced perturbations across 117M–8B models; shows early-layer MLP up-projections are catastrophically sensitive while value projections are nearly free, residual connections contract errors. Directional, but "direction" here is "which weight matrix gets quantised", not "causally-important activation direction". Closely adjacent methodology; distinct substrate.
3. **"DIFFEQFORMER" (ICLR 2025)** applies Lyapunov exponents to transformer behaviour; "Lyapunov Exponent Analysis of Mamba and Mamba-2" (`arXiv:2406.00209`) derives bounds on SSM Lyapunov spectra. Neither uses ROME or interpretability-identified directions.

Nothing in the 2024–2026 window does the specific thing — directional Lyapunov along a *mechanistically identified* direction on a transformer. So the combination is still novel. But the competitor papers already cover "layer-resolved Lyapunov on LLMs" and "directional stability across weight matrices", so the reframed version must carry both the MI-direction + criticality bridge, otherwise it is a minor extension of 2503.13530.

## 3. Falsifiability, controls, cost

Reframed, the candidate's pre-registered kill becomes:

- **Primary kill.** If λ(ROME direction, model) − λ(matched-subspace-random direction, model) is statistically indistinguishable from zero after bootstrapping over ≥ 50 (subject, relation, object) triples and ≥ 10 seeds for the random-subspace control, the "directional Lyapunov carries semantic structure beyond what ROME's optimisation buys you" claim dies.
- **Secondary kill.** If λ(ROME direction) does not respond to the criticality knob (skip-connection sweep, or Pythia-scale sweep), the "bridge between MI and criticality" claim dies. A ROME direction that is equally λ > 0 at σ = 0.5, 1, 1.5 is evidence *against* a criticality-conditioned interpretation of MI primitives.
- **Tertiary kill.** If λ(ROME direction on on-topic prompts) ≈ λ(ROME direction on off-topic prompts) within bootstrap error, the "semantic conditioning" claim narrows to "rank-one edit sensitivity" — publishable as a cleaner sensitivity study but not as a criticality-MI bridge.

Controls required (beyond the minimum-evidence-bar in `knowledge_base.md §5`):

- Matched-subspace random baseline (not isotropic Gaussian).
- Matched-ℓ²-norm control.
- On-prompt × off-prompt factorial.
- At-init control (does the same ROME direction, recomputed at init, produce the same directional-Lyapunov gap? If yes, the training-conditional-criticality interpretation weakens).
- Neutral-null / Griffiths control (inherit from Candidate 12).
- Cross-basis consistency: compute directional Lyapunov on (raw-residual, SAE-feature) bases and check the conclusion is basis-invariant (inherit from Candidate 5).

**Cost.** The original 2 weeks is an under-estimate. ROME hook-wiring on GPT-2 is trivial on TransformerLens; the matched-subspace control, the 50-triple sweep, and the cross-model criticality axis push this to ~3 weeks on a 3060 including analysis. Add the at-init and SAE-basis controls: ~4 weeks. At the edge of the single-RTX-3060-in-four-weeks bar.

## 4. Strength vs Candidate 5 as an MI-to-criticality bridge

Candidate 5 (SAE features vs raw neurons) and Candidate 10 are the two MI-bridge candidates in the set. Side-by-side:

| Dimension | Candidate 5 (SAE basis) | Candidate 10 (ROME direction) |
|-----------|-------------------------|-------------------------------|
| Novelty | Moderate: basis-invariance of exponents is a known methodological concern, SAE angle is new | Moderate if reframed; low if run as originally stated |
| Tautology risk | Low. Bases are fixed *before* measurement. | **High in original framing.** ROME direction is optimised for exactly the observable you measure. |
| Control cleanliness | Clean: raw / PCA / random-projection / SAE are all geometrically defined, norm-preserving. | Requires non-trivial matched-subspace control. Easy to get wrong. |
| Falsifiability | Sharp: Δ-exponent < 0.1 across bases kills it. | Needs the on-prompt × off-prompt × criticality factorial to be sharp. |
| Infrastructure | Gemma-Scope weights + SAE Lens, off-the-shelf. | ROME re-implementation + TransformerLens hooks + triple-prompt harness. More code. |
| Cost | ~2 weeks, realistic. | ~3–4 weeks if done properly. |
| Venue | Anthropic / DeepMind workshop; ICML MechInterp. | Same venues. |
| Synergy with other candidates | Strong: feeds Candidate 1 basis control. | Moderate: depends on Candidate 2's skip-sweep for the criticality axis. |
| Fatal risk | "Basis invariance holds within CI" — a boring-but-publishable null. | "Directional λ > random λ (duh)" — a circular positive. |

**Verdict on the comparison.** Candidate 5 is the stronger MI-bridge candidate as proposals currently stand. It has a cleaner null, cheaper infrastructure, and no tautology risk. Candidate 10 is the *more ambitious* bridge — if the reframe works, a ROME-direction Lyapunov that compresses to zero near σ = 1 is a more interesting result than SAE-basis-exponent-equals-raw-exponent. But the reframe must hold, and it demands the extra controls above. Run Candidate 5 first; Candidate 10 becomes more valuable once the basis-invariance question is closed, because it then has a principled basis in which to compute directional Lyapunov.

## 5. Recommendations

1. **REFRAME.** Rewrite the candidate's observable as "directional Lyapunov *as a function of* |σ − 1|, with ROME-direction vs matched-subspace-random control, across on-prompt vs off-prompt factorial". The original "does direction Lyapunov match random Lyapunov?" framing is fatally circular.
2. **Add `arXiv:2503.13530` ("Cognitive Activation") and `arXiv:2603.20991` ("Structural Sensitivity in Compressed Transformers") to `papers_ml.csv` and `lit_ml.md §10`.** Both are direct precedent on "Lyapunov on LLMs" in the 2024–2026 window and must be cited as the baseline the reframed paper extends.
3. **Sequence after Candidate 5.** Candidate 10 gains sharpness once the basis-invariance question is settled — it then has a principled "directional Lyapunov in the SAE basis, along an SAE-identified feature" variant that fuses Candidates 5 and 10.
4. **Do not promote yet.** Scope-check outcome is conditional REFRAME: promote only if the reframe controls (matched subspace, on/off-prompt factorial, criticality-axis coupling) are specified in the promotion package. Otherwise KILL.

**Venue fit (reframed).** ICML 2026 MechInterp workshop; NeurIPS 2026 ATTRIB; Entropy journal for the methodology writeup. Not a top-tier main-conference paper on its own — workshop scope.

**Dependence.** Should follow Candidate 2 (for the criticality axis) and ideally Candidate 5 (for the basis control). Running standalone weakens all three kills.

---

*Length: ~1450 words.*
