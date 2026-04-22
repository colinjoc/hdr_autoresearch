# Scope check — Candidate 15: Criticality early-stopping signal

**Date:** 2026-04-21
**Reviewer:** Phase −0.5 scope-check agent (extension round)
**Target:** Candidate 15 (`candidate_ideas.md §Candidate 15`). Test whether `|σ_ℓ − 1|` (or `D(t)` from Wang arXiv:2604.16431) rises *before* val-loss degrades on deliberately-overfitting runs; if criticality leads val-loss, use it as an independent early-stop signal. Proposed: ~1 week, workshop paper.

**Verdict: REFRAME — PROCEED as a diagnostic-comparison section of Paper 3 (training dynamics), not as a standalone Paper 8.**

The direction is defensible and the compute is cheap, but as written the candidate (i) rides on an observable whose early-warning property is already published (Wang 2604.16431), (ii) conflates "overfitting" with "grokking" and "capacity saturation" without operational separation, (iii) leaves the lead-time statistic under-specified (as for Candidate 4), and (iv) under-budgets seeds. Fixable.

---

## 1. Novelty vs. Wang and 2024–2026 arXiv

### 1.1 Wang's observable already carries the early-warning claim

Wang 2604.16431 reports that `D(t)` separates grokked from ungrokked trajectories "some 100–200 epochs before the behavioural transition" (WebFetch of abstract, 2026-04-21). Candidate 4's scope-check already recorded that Wang 2604.16431 + 2604.04655 scoop the "criticality-observable-as-early-warning-of-grokking" slot. Candidate 15 cannot re-sell that under an "overfitting" banner.

*Partial salvage.* WebFetch confirms Wang frames `D(t)` as a physics observable, **not** as a proposed early-stopping criterion. A paper that asks "can this observable be operationalised as a drop-in early-stop rule that beats val-loss early-stop in practice" is a genuinely different contribution — engineering rather than phenomenology. That framing is defensible with pre-registered practical criteria (§3).

### 1.2 Is "overfitting" distinct from "grokking"? — yes, but not cleanly

Grokking is delayed generalisation (train converges early, val-loss stays high, then drops, with total budget 10²–10⁴× memorisation time; Power 2022, Nanda 2023, Liu 2022). Shakespeare overfitting is the opposite shape: val-loss bottoms ~step 3–6 K (Karpathy config, best val-loss ~1.47) then rises. Weight decay ≈ 0, no grokking regime. So the experiment *does* target a distinct phenomenon.

But "rising `|σ − 1|`" is not uniquely tied to overfitting. Competing drivers produce the same drift:

- **Capacity saturation** — effective dimension climbs as the net finishes fitting.
- **Edge-of-stability entry** (Damian-Nichani-Lee 2022, paper 3015) — Jacobian spectra self-regulate when the optimiser hits the EoS manifold; unrelated to overfit.
- **HTSR phase change** (Prakash-Martin 2506.04434) — ESD tail α drifts through training phases, tracking convergence / generalisation, not overfit specifically.
- **Schaeffer-style collapse**: σ, α, ρ collapse to mean-field-equivalent statistics (`promoted.md` §Methodological #2). A σ that "predicts" val-loss may just be rephrasing val-loss.

Positive-control (textbook overfit) and negative-control (no overfit, but EoS / HTSR drift still present) regimes are required; without them a positive result is uninterpretable.

### 1.3 Has any 2024–2026 paper used a stat-mech observable as an early-stop criterion?

WebSearch 2026-04-21: "physics-inspired early stopping", "criticality observable training diagnostic", "branching ratio early stopping", "HTSR alpha early stopping".

- **Dong et al. 2025 (2502.07547)** — per-example second-order-difference stopping; physics-inspired only in metaphor. Non-colliding.
- **WeightWatcher / HTSR α** (Prakash-Martin 2506.04434) — the occupied slot. α is a data-free diagnostic with "5+1 phases of training" framing; used in blog posts as an informal early-stop heuristic but no published head-to-head lead-time comparison against val-loss on LLMs. Any Candidate-15 execution omitting α as a comparator is incomplete in 2026.
- **Montanari-Urbani NeurIPS 2025 oral** — "feature learning precedes overfitting"; supports the premise but proposes no stopping rule.
- ScienceDirect 2023 correlation-based stopping, 2410.22594 Gaussian-derivative changepoint — adjacent, non-colliding.

**Gap.** No 2024–2026 paper runs a head-to-head early-stop-lead-time comparison of criticality observables (σ via MR, `D(t)`, HTSR α, ρ) against val-loss early-stop on a deliberately-overfit deep net. Gap is real but narrow; contribution is methodological / engineering.

## 2. Is the overfitting setup clean enough?

**Partially.** Three failure modes of the proposed 10 K-token nanoGPT Shakespeare substrate:

1. *Multiplicity of transitions.* Tiny-data nanoGPT shows memorisation, overfit onset, train-loss plateau, occasional late double-descent. σ-trajectory has multiple drifts; assignment needs independent registration.
2. *Tokenisation dependence.* Char-level vs small-BPE overfit at different steps; exponents depend on tokenisation via activation sparsity (`lit_ml.md` §7). Pre-register one.
3. *Saturation masking overfit.* On the tiny 6×384 default, capacity saturates before overfit — val-loss plateau rather than U-shape. No signal; both σ and val-loss flat.

**Mitigation.** Three regimes: (a) nanoGPT-small on 10 K tokens (proposed); (b) clearly-overparameterised 12×768 on ~100 K tokens where val-loss U-shape is textbook; (c) no-overfit control (weight decay + 10× data). 3 × 20 seeds × ≤ 20 min ≈ 20 GPU-hours — inside the ~1-week budget.

## 3. Operationalisation of "lead time" — under-specified

The same weakness flagged in Candidate 4's review (§2), with one favourable twist: overfitting gives a clean val-loss event (first derivative sign change), which grokking does not. Still required:

- **`t_val`.** Causal (no look-ahead) Bayesian online changepoint detector on val-loss first differences — `bayesian_changepoint_detection` package, geometric run-length prior (mean ≈ 500 steps), Gaussian observation model. Report detected step `t̂_val`.
- **`t_crit`.** Same detector applied to `|σ(t) − 1|`, `|D(t) − 1|`, α(t). σ is estimated per-checkpoint from finite batches; its noise can dominate detection, pushing `t̂_crit` in either direction. Pilot-run the SNR before committing.
- **`Δ = t̂_crit − t̂_val`** as a random variable over seeds. Report full distribution, sign, magnitude in steps, and fraction of budget. Candidate's "< 2 % = kill" threshold is concrete — good.
- **Seed count.** Candidate 4 review established that grokking-step variance is 20–40 % of the step itself; overfit-step variance likely similar. Detecting `E[Δ] = -0.05 × T` against null at Cohen's d ≈ 0.5 requires n ≥ 20 per regime, not 1–5.

## 4. Required controls

1. **Baselines for early-stop rule.** Compare σ/D/α-early-stop against (a) val-loss patience early-stop, (b) **WeightWatcher α early-stop** (primary baseline — occupied slot), (c) train-loss plateau. A rule that beats (a) but not (b) is reporting HTSR, not criticality.
2. **No-overfit regime.** Observable should *not* fire a stop. False-positive rate must be reported.
3. **Saturation regime.** Observable should *not* fire.
4. **Multi-seed.** n ≥ 20 per regime (§3).
5. **At-init baseline.** Record `σ(t=0)`; deviation `|σ(t) − σ(0)|` may have lower seed-variance than raw `|σ(t) − 1|`.
6. **Residual-stream confound.** Use the *contribution* `F_ℓ(h_ℓ)` branching definition, not raw residual-stream ratio (trivially ≈ 1; `promoted.md` §Methodological #1).

## 5. Bundling — is this "Paper 8"?

`promoted.md` lists Candidate 15 as "Paper 8 (training-regime)". Over-generous: contribution is narrow (one engineering question), dependent on Paper 3's per-step observable pipeline (σ / D / α / ρ through training), and publishable only as workshop / short note.

**Recommendation.** Fold Candidate 15 into Paper 3 as a dedicated practical-diagnostic section. Paper 3 is already "head-to-head of σ, D(t), HTSR α, O-info on common seeds" (Paper 3 bundles C3+C4). Adding an early-stopping-lead-time figure across the same observables on the Shakespeare-overfit substrate is a 1-week incremental. This also resolves the Wang-scoop problem: Paper 3's head-to-head engages Wang at the phenomenological level; Candidate 15 adds the operational-diagnostic level. One paper, two angles.

If Paper 3 is not commissioned, Candidate 15 should not stand alone.

## 6. Pre-registered kill — re-specified

Original kill ("criticality lags val-loss, or leads by < 2 % of training budget") is approximately posed but leaks across seeds and regimes. Tighter:

For each regime r ∈ {overfit-tiny, overfit-big, no-overfit, saturation}:

- `Δ_r = median over seeds of (t̂_crit − t̂_val) / T`.
- **Kill if** (i) `Δ_{overfit-tiny} ≥ −0.02`, OR (ii) false-positive rate on `no-overfit` > 0.1, OR (iii) σ / D lead-time is not statistically distinguishable from HTSR-α lead-time on the same runs (pairwise Mann-Whitney U, p > 0.1).

Pre-register thresholds and observation windows before runs.

## 7. Summary

**REFRAME — PROCEED** as a diagnostic-comparison section of Paper 3. Position the contribution as *operationalising* Wang's observable (and HTSR α, and σ) into a practical early-stop rule, not as *discovering* that criticality leads generalisation. Three regimes, 20 seeds each, pre-registered causal changepoint detection, HTSR α as primary baseline.

**Rubric.** D = 5 (standard training logs). N = 2 as written (Wang scoops), N = 4 as reframed (first practical head-to-head early-stop comparison). F = 4 once §3 tightened. C = 5 (≤ 1 week inside Paper 3). P = 4 as Paper 3 §N; P = 1 standalone.

**Action items.**

(i) Candidate 15 should not leave `pending` unless Paper 3 is commissioned.
(ii) Tighten `candidate_ideas.md §Candidate 15` per §3; re-cite Wang 2604.16431 so novelty is framed as engineering.
(iii) Add WeightWatcher α as a required comparator; add Dong et al. 2502.07547 and Prakash-Martin 2506.04434 to related work.
(iv) Update `promoted.md`: Candidate 15 folds into Paper 3; drop the "Paper 8" designation.

---

**Sources consulted:**

- [Wang 2026a, arXiv:2604.16431](https://arxiv.org/abs/2604.16431) — "100–200 epochs before behavioural transition"; framed as phenomenology, not diagnostic (WebFetch 2026-04-21).
- [Wang 2026b, arXiv:2604.04655](https://arxiv.org/abs/2604.04655)
- [Prakash-Martin 2025, arXiv:2506.04434](https://arxiv.org/abs/2506.04434) — occupied HTSR-α-as-progress-measure slot.
- [Dong et al. 2025, arXiv:2502.07547](https://arxiv.org/abs/2502.07547) — per-example second-order-difference stopping.
- [Damian-Nichani-Lee 2022 (paper 3015)](https://arxiv.org/abs/2209.15594) — EoS confound.
- Montanari-Urbani NeurIPS 2025 oral — "feature learning precedes overfitting"; premise support.
- Internal: `candidate_ideas.md §Candidate 15`; `knowledge_base.md §2`; `promoted.md` §Paper 3 and §Methodological findings 1, 2; `scope_checks/candidate_04_review.md` §2 (lead-time operationalisation, seed budget); `scope_checks/candidate_01_review.md` §Novelty (Wang adjacency framing).
