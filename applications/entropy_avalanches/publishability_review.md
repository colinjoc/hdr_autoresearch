# Phase 0.25 Publishability Review — entropy_avalanches

**Reviewer.** Phase 0.25 sub-agent, 2026-04-21. Fresh — not the Phase 0 literature-review agent and not the Phase −0.5 scope-check agent.
**Mandate.** Answer the six review-contract questions. Be harsh. Recommend PROCEED / REFRAME / KILL.
**Artefacts read.** `README.md`, `literature_review.md` (~27 k words, 360 citations), `papers.csv` (360 entries), `../entropy_ideation/knowledge_base.md` (8-item evidence bar), `../entropy_ideation/candidate_ideas.md` §§1, 6, 8, 11, 12, 25, 28, and all seven Phase −0.5 `scope_checks/candidate_0{1,6,8,11,12,25,28}_review.md`.

---

## 1. Is the novelty claim defensible after the synthesis-round scope-checks?

**Yes, but narrowly — and only in the specific form the revised §1.1/§1.3 now states.** The original naive claim ("first avalanche statistics on trained transformers") is dead as of Wang 2604.16431 / 2604.04655, and `literature_review.md §1.2.1` + `scope_checks/candidate_08_review.md §3` both concede this. What survives is a *multi-predicate* claim:

> First measurement that simultaneously (i) computes `P(s), P(T), ⟨s⟩(T)` via the full CSN + `powerlaw` bootstrap pipeline, (ii) extracts α, β, γ independently and tests the Sethna crackling-noise relation γ = (β−1)/(α−1), (iii) reports MR-σ on ≥ 2 axes with Wilting–Priesemann subsampling correction, (iv) demonstrates a threshold plateau, (v) passes the Heap 2501.17727 random-init-SAE control, (vi) rejects the Martinello / di Santo neutral-null and Qu 2022 heavy-tailed Anderson Griffiths-phase null, and (vii) does all of this on **pretrained LLMs evaluated on natural text**, not toy modular-addition / XOR / cellular-automaton targets.

That conjunction is still novel. Each individual predicate is borrowed from an existing methodology (Clauset 2009, Sethna 2001, Wilting 2018, Heap 2501.17727, Martinello 2017), and each individual near-neighbour (Wang, Nakaishi, Yoneda, Zhang 2410.02536) clears some subset of them on some subset of targets. Nobody clears all seven on pretrained LLMs on natural text. The defensibility of the claim therefore rests entirely on **execution discipline**: if even one predicate is fudged, the residual novelty collapses onto whichever adjacent paper cleared the rest.

**Hostile-reviewer one-sentence kill attempt.** "Wang 2604.16431 already measured an avalanche-derived observable on trained transformers and recovered a dimensional-criticality signature at a phase transition; this paper is a methodologically ornate restatement on a different corpus whose headline numbers (α ≈ 3/2, γ scaling relation, shape collapse) are all *predicted* by directed-percolation mean-field theory and would be surprising only in their absence, so the contribution reduces to negative-results-would-be-news while positive results are over-determined."

**Counter.** (a) Wang's TDU-OFC cascade-dimension D is a *scalar* that conflates α, β, shape information — it is demonstrably less discriminating than the (α, β, γ) triple plus shape collapse when universality-class assignment matters (e.g., DP vs edge-of-synchronisation vs adaptive-Ising all predict D ≈ 1 near criticality but different γ-relation residuals). (b) Wang's target is grokking on modular arithmetic, not natural-text pretraining — the null hypothesis that pretraining on The Pile lands in the same universality class as modular-addition grokking is itself a non-trivial claim worth empirical test. (c) The random-init-SAE control (Heap 2501.17727) is load-bearing: if criticality signatures appear in random-init SAEs, half of the interpretability-community audience will read the paper as "SAEs generate apparent criticality as a compression artefact" — so the control, and its result, is a publishable contribution independent of the LLM outcome.

**Verdict:** novelty defensible, but the margin is now single-figure-percentage. One 2026 preprint from Wang's group or Nakaishi's group extending to pretrained LLMs on natural text collapses it. Ship-speed matters more than additional experiments.

---

## 2. Is the 8-item evidence bar internally consistent with the bundled candidates?

Crosswalk of `knowledge_base.md §5` (items 1–8) against the seven bundled candidates, as documented in README.md and the scope-checks:

| Evidence-bar item | C1 | C6 | C8 | C11 | C12 | C25 | C28 |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 1. `P(s)` via `powerlaw` + KS + LLR | ✓ | ✓ per-layer | reframe req. | ✓ (CIFAR-10 swap) | ✓ (re-uses C1) | — (d_β not CSN) | ✗ (dropped per C28 review §8.2) |
| 2. α ≈ 3/2 with 95 % CI | ✓ | partial | reframe req. | ✓ | ✓ | — | ✗ |
| 3. γ = (β−1)/(α−1) | ✓ | per-layer marginal | n/a | needs commitment | ✓ (C12 is *this* test) | — | ✗ |
| 4. Shape collapse | ✓ | secondary | n/a | needs commitment | ✓ (Martinello-shape) | — | ✗ |
| 5. σ = 1 ± 0.02 via MR ≥ 2 axes | partial → reframed to full | ✓ (layer axis) | ✓ (head axis under reframe) | partial | inherited | — | ✓ (head-level σ) |
| 6. Threshold plateau | ✓ | ✓ | reframe req. | needs commitment | inherited | — | needs commitment |
| 7. At-init control | ✓ | ✓ | ✓ (random-OV null per C28 §6) | ✓ | ✓ | ✓ | ✓ |
| 8. Neutral-null rejection | partial → C12 covers | partial | sparsity-matched null per reframe | ✗ → C12 | ✓ (this *is* the job) | Griffiths via Silva 2020 / Qu 2022 | null hierarchy per §6 |

**Which of the 8 items is NOT well-covered by any bundled candidate?** All eight are at least nominally covered once C1 is expanded to absorb C6 §4, C12 §5, and the C28/C8 head-level section per the scope-checks. **But there is a visible weakness on item 4 (shape collapse) and item 6 (threshold plateau) for the C11 ViT-Tiny arm** — `candidate_11_review.md` §5 explicitly flags both as "missing". If the ViT-Tiny arm is promoted as a first-class universality claim (a transformer architecture in a different modality), it must clear the same bar. README.md says ViT-Tiny replaces Fashion-MNIST per the scope-check, but does not confirm the bar-upgrade. Needs to be made explicit in Phase 0.5.

**Weakness on item 3 per-layer.** C6 reviewer explicitly concedes: "γ = (β−1)/(α−1) per layer *likely fails ≥2-decade requirement*" — so the per-layer crackling-noise cross-check is under-powered and the C6 deliverable has to fall back to global γ. That is a methodological note, not a failure, but must be stated in the paper.

**Consistency verdict:** the bar is internally covered in aggregate, but two items (3 per-layer, 4 + 6 on ViT-Tiny) have silent weaknesses that a reviewer can pick on. Fixable with one Phase 0.5 methodology memo.

---

## 3. Are the observables *operationally* well-defined across the bundled arms?

Five specific observable-definition questions to interrogate:

**(a) Residual-stream confound for σ_ℓ (C6).** `candidate_06_review.md §2` is explicit: naive layer-to-layer σ reads ≈ 1 tautologically because `h_{ℓ+1} = h_ℓ + F_ℓ(h_ℓ)`. The project has accepted the fix: use (i) σ_ℓ on the contribution F_ℓ(h_ℓ) (Elhage-2021 additive decomposition) and (ii) causal patching per Goldowsky-Dill. README.md line 13 says "path-patching causal definition (not naive residual-stream confound)". **Operationally defined.** The only residual concern is that F_ℓ vs path-patching σ_ℓ can diverge and neither is canonical; must be reported side-by-side with the K6c consistency check from the C6 scope review.

**(b) Causal-cascade reframe for attention-head criticality (C8).** `candidate_08_review.md §9` REFRAMES to "head-output ablation + residual-stream cascade measurement" (option 3), dropping the ill-posed "attention-pattern avalanche" (options 1 and 2). README.md line 14 commits to this reframe ("causal-cascade reframe"). **Operationally defined**, but with a live risk: the reframe collapses C8 into a circuit-seeded variant of C1, and C28 (head-distribution) now overlaps so heavily with C8 (circuit-specific) that `candidate_28_review.md §3` recommends merging them. Candidate bundle treats this correctly by co-scoping C8 + C28 in README.md lines 14 and 18.

**(c) Fontenele-subspace-σ.** This is the Fontenele 2024 (`papers.csv 4005`) low-dim-subspace observable raised in Phase 0 as the serious threat to ambient-basis negative results. `literature_review.md §2.5` and §1.2 discuss it. **The bundle does NOT include Candidate 29** (which is the Fontenele subspace replication), so a negative ambient-basis result has to be accompanied by the PCA-top-K + SAE-subspace basis sweep that C1 already commits to. That is partial coverage of Fontenele, not a full subspace-criticality test. A reviewer will ask why C29 is not in the bundle if the Fontenele motivation is explicit. **Gap.** Either commit to a Fontenele subspace analysis inside C1 (participation-ratio-chosen K, top-K PCA plus orthogonal-complement test) as a named paper section, or defer to the second paper and say so.

**(d) Crackling-noise cross-check (γ from β and α).** Standard, well-defined, in C1 §5.1 per the C12 scope review. Implementation uses Sethna 2001 formula, independent bootstrap for α, β, γ, and a scaling-residual test against the Martinello neutral-model fit. **Operationally defined.**

**(e) Basis-invariance battery across raw / PCA / random-projection / SAE / random-init-SAE.** README.md line 12 commits; `literature_review.md §1.5 line 1346` pre-registers all six bases. The random-init-SAE is the Heap control; Gemma-Scope SAEs give the trained SAE arm. **Operationally defined**, but with a feasibility qualifier: `literature_review.md §Feasibility` admits random-init-SAE training is ~1–3 GPU-days per layer on GPT-2-small and has been scoped to 3 layers, not all 12. A reviewer can ask "why those 3?" — the pre-registration must name them (probably layer 0, layer N/2, layer N−1 — early, middle, late).

**Operational-definition verdict:** four of five specific observables are defended. The Fontenele subspace coverage is the one exposure; the bundle needs an explicit "how we approximate the Fontenele protocol without Candidate 29" paragraph.

---

## 4. Is the venue target realistic?

The stated target is NeurIPS / ICLR main → *Entropy* fallback.

**Case for main-track acceptance.** The competitive landscape reviewer will compare against: Wang 2604.16431 (NeurIPS 2024 / workshop track, cascade-dimension, grokking), Zhang 2410.02536 (ICLR 2025, edge-of-chaos in ECA-pretrained LLMs), Halloran 2406.00209 (ICLR workshop, Mamba Lyapunov), Prakash-Martin 2506.04434 (NeurIPS spotlight plausible, HTSR anti-grokking phase). **The bar that cleared those venues is roughly: one clean empirical phenomenon + one statistical-physics framing + public code.** This paper's framing is the statistical-physics discipline itself, applied to pretrained LLMs on natural text, with eight-item methodology. Three independent selling points:

1. *Universality-class assignment for transformers* (Yoneda 2025 gave MLPs = mean-field, CNNs = DP; transformers = "?"). Nobody has closed this.
2. *Random-init-SAE as a first-class negative control* — directly addresses Heap 2501.17727 which was itself an ICLR 2025 highlight.
3. *Circuit-seeded causal-cascade distribution across heads* — bridges MI and statistical physics in a way Olsson 2022 and Wang 2023 IOI explicitly do not.

**Case against main-track.** (a) Reviewers on NeurIPS / ICLR MI track now expect causal-intervention machinery at path-patching-or-better granularity throughout; the paper must demonstrate it is not purely correlational. The C6/C8 reframes help but the weak-point is C1's core activation-avalanche which remains *correlational cascade across layers*. A hostile reviewer will call this "distributional statistics of a correlational observable". (b) Wang 2604.16431 + 2604.04655 already give a physics-trained NeurIPS reviewer a mental handle on "avalanche statistics on transformers"; the methodology-depth of this paper will read, in 400-word review space, as "an ornate replication with controls added". Main-track decisions turn on the *what's-new-in-one-sentence* test, not on the methodology depth. (c) `scope_checks/candidate_01_review.md §3` explicitly says "main-track realistic only if the paper is unusually clean (full 8-item bar + negative-result discipline)" — so the Phase −0.5 agent's own assessment is main-track-conditional.

**Honest target ranking.**

- **NeurIPS / ICLR main (25–35 % chance of acceptance given execution discipline):** achievable only if (i) all 8 bar items clear on at least one basis–threshold combination, (ii) the random-init-SAE control is clean, (iii) at least one of the seven candidates produces a *surprising* result (e.g., α ≠ 3/2, or basis-invariance fails, or induction-head σ is flat).
- **NeurIPS MechInterp / ATTRIB workshop (~70 % acceptance):** very high baseline likelihood given the MI-bridge framing and independent-researcher track record at these venues.
- ***Entropy* journal (~85 %):** natural fit, board includes Plenz/Beggs collaborators, specifically receptive to criticality-in-LLM papers.
- **TMLR (~60 %):** a realistic mid-tier option for "technically solid, incremental-but-clean" work that does not clear the main-track novelty bar.

**Recommendation:** target NeurIPS / ICLR main **with TMLR / Entropy as parallel fallbacks**, not sequential. Declaring TMLR as first-choice signalling mediocrity, but committing to main-track alone ships late and risks submission-deadline slippage. The workshop venues are concurrent-submittable to main-track in most cases.

---

## 5. Hostile-reviewer audit (≤ 400 words)

**Reviewer #2, hostile, credible, senior ML-theory PC member.**

> This paper measures activation-avalanche size distributions on pretrained transformers and reports α ≈ 3/2 with a full crackling-noise / shape-collapse / MR-σ battery. My review has three concerns the authors have not adequately addressed.
>
> **First: what is new?** The avalanche analysis on trained networks is not new (Wang 2604.16431, Yoneda 2025 PRR, Nakaishi 2406.05335). The methodological discipline — CSN, `powerlaw` package, Sethna relation, Capek shape collapse — is 25 years of cortical-avalanche canon applied verbatim. The contribution reduces to "we did the full pipeline on pretrained LLMs on natural text." That is a useful methodology paper, but the authors frame it as a universality-class discovery, which is overselling. If the answer is α ≈ 3/2 and γ = (β−1)/(α−1) within error, the result is *expected* from mean-field DP theory and does not update any prior. If the answer is different, the paper has no theory for *why*.
>
> **Second: the correlational-vs-causal problem is sidestepped, not solved.** The authors correctly flag the residual-stream confound for σ_ℓ and use path-patching for the layer-gradient. But the core observable — P(s) on residual-stream activations across layers — is a correlational cascade. The "avalanches" are sets of co-firing units, not causal descendants. The MI literature has moved past correlational analysis (Meng 2022 ROME, Goldowsky-Dill 2023 path patching); a 2026 paper making strong dynamical claims should do the same. The paper's causal discipline is front-loaded onto the head-level analysis (§X) but absent on the main avalanche distribution.
>
> **Third: the random-init-SAE control is under-powered.** 3 layers out of 12 on GPT-2-small is not a basis-invariance test, it is a three-point check. The authors cite Heap 2501.17727 as motivating the control but then do not meet Heap's own standard (which ran SAEs on all layers). The control may be partial evidence that criticality is not an SAE artefact, but not decisive.
>
> Recommendation: reject from main track. Encourage resubmission to the NeurIPS MechInterp workshop with clarified scope, or to TMLR once the causal-cascade definition is the headline observable and not §X.

**Is the counter convincing?** Partially.

- Concern 1 (what's new): counter is the multi-predicate novelty framework from §1 above. It is technically correct but weak — reviewer will read "methodology discipline" as faint praise. **Not fully convincing.**
- Concern 2 (correlational): the counter is that C8/C28 reframe is *specifically* the causal-cascade arm, and the paper can foreground that. If done, this absorbs the objection. **Convincing if the paper structure is reorganised.**
- Concern 3 (3-layer SAE): the counter is that the 3 layers are pre-registered (early/middle/late) and Gemma-Scope provides a denser SAE coverage on Gemma-2-2B, so the random-init-SAE is a lower-bound check rather than a full sweep. **Convincing if stated that way.**

Two of three defensible; concern 1 is the one that pushes to workshop / TMLR rather than main.

---

## 6. Decision gate

**Verdict: REFRAME.** Not KILL — the project clears a credible main-track / fallback-strong publication path. Not PROCEED-unchanged — the bundle has three load-bearing weaknesses the Phase 0 agent under-weighted.

**Specifically required reframes before Phase 1:**

1. **Add Candidate 29 (Fontenele subspace σ) as a first-class arm, or explicitly scope its absence.** The ambient-basis negative result is uninformative without a subspace test. A Fontenele-style participation-ratio-selected PCA-top-K + SAE-subspace σ analysis must be named in Paper 1's figure list, not left implicit in the basis-invariance battery. Cost: ~3 extra GPU-days, fits budget.

2. **Foreground the causal-cascade observable, not the correlational P(s).** Restructure the paper so the C8/C28 causal-cascade machinery is §2 (primary observable) and the raw activation-avalanche P(s) is §3 (correlational companion with the obvious limitation flagged). This inverts the reviewer's main attack axis.

3. **Widen random-init-SAE control from 3 layers to all layers on GPT-2-small.** 12 layers × ~1.5 GPU-days ≈ 18 GPU-days is infeasible as stated. Fix: drop random-init-SAE training on Pythia-2.8B / Gemma and concentrate the compute budget on GPT-2-small where the control actually needs to be dense. This is a 2-week Phase-0.5 budget re-plan.

4. **Kill the standalone-C25 scope (TRG d_β).** The scope-check is unambiguous: it is a 5–7-day appendix probe, not a standalone arm. README.md currently lists C25 as "appendix" — confirm this in the Phase 0.5 deliverable and do not treat it as a main-claim arm.

**Bundle composition after reframe:**
- **KEEP:** C1 (anchor), C6 (absorbed as §4), C8+C28 (merged as §X head-resolved causal), C11 (ViT-Tiny universality arm, with the 8-item bar upgrade), C12 (absorbed as §5).
- **ADD:** C29 (Fontenele subspace σ) as §6.
- **RESTRICT:** C25 to appendix only.

**Venue rewrite:** target NeurIPS / ICLR main + TMLR + NeurIPS MechInterp workshop in parallel, with *Entropy* as paper-2 venue. Do not declare *Entropy* as fallback for this paper if main-track submission is the real target — a reviewer sees the fallback-declaration as a confession.

---

**One-line justification:** The project is methodologically strong and novel-in-aggregate, but three specific weaknesses (Fontenele subspace coverage, correlational-vs-causal framing, random-init-SAE density) are load-bearing enough that a hostile NeurIPS reviewer can reach "reject to workshop" without unreasonable effort — so REFRAME the bundle to close those before Phase 1, not after Phase 2.75.

*Word count: ~2480.*
