# Phase 3.5 Paper Review — qec_rl_qldpc / paper_v2.md

## 1. One-paragraph assessment

The manuscript presents a wall-clock characterisation of the GAP+GUAVA-based transversal-Clifford reward pipeline for reinforcement-learning-driven qLDPC code discovery, and proposes a 3-coloured Tanner-graph automorphism-group-order proxy (computed via pynauty) as a tractable upper bound. The measurements are concrete: `get_transversal_automorphism_group` times out at n ≥ 40 on a 60 s budget, `get_transversal_ops` does not complete at 600 s even for n ≤ 30, while the proxy runs in 0.4 ms at the Bravyi [[144,12,12]] gross code. This is a genuine infrastructure observation with practical value. However, as written the paper cannot yet be published at Quantum or SciPost Physics Codebases: the central correctness claim — that the proxy is a useful surrogate for the transversal-Clifford rank — is not validated (§4.3 item 1 is explicit about this), the Pareto demonstration is described by the authors themselves as a smoke test of eight points at two n-values, and no RL training loop is implemented. The paper is honest about all of these limitations, which is laudable, but honesty does not by itself warrant publication. I recommend **major revisions**: the proxy–rank correlation must be measured on at least a handful of small codes, even if that requires offline multi-day GAP runs, before the proxy can be offered to the community as infrastructure.

## 2. Strengths

- The PER-1 measurement methodology (subprocess isolation, 60 s hard timeout, explicit cold/warm GAP separation) is cleanly reported, and the table in §3.1 is reproducible from the stated libraries and polynomial families.
- The 600-to-1 wall-clock jump between n = 30 and n = 40 is a genuinely useful data point for the community — it substantiates the in-code warning `"Attempting to compute an automorphism group with GAP, which may take a long time"` with numbers rather than folklore.
- The proxy's upper-bound relationship to the transversal-Clifford rank is stated correctly in §2.4 and §4.2, including the failure mode (Tanner automorphisms that do not preserve the stabilizer group).
- §4.3 enumerates four open items with named scripts and explicit remedies, and §4.4 includes a rare "Is / Is not" table that pre-empts over-claiming.
- Reward-hacking mitigation via an Hx/Hz split (§4.3 item 2) is a thoughtful design suggestion, even if unimplemented.

## 3. Major concerns

1. **The proxy–rank correlation is unmeasured.** §4.3 item 1 acknowledges that `e03_per1_rerun_and_correlation.py` failed to complete within its 600 s budget. The paper asks the reader to accept a proxy whose correlation with the true reward is zero-measured. *Fix:* run offline multi-day GAP (or MAGMA) computations of `get_transversal_ops` on 5–10 very small codes (n ≤ 20), report Spearman and Pearson correlations of log-proxy vs log-rank, and include at least one scatter plot. Without this, the "infrastructure paper" claim reduces to "here is a fast computation whose relevance to the target quantity is hypothesised but untested."

2. **The upper-bound claim in §2.4 is asserted, not proven.** The paper states "every stabilizer-preserving automorphism is a Tanner automorphism, but not conversely" without a citation or a short derivation. For a Codebases submission where the proxy is the central object, a formal statement and proof (or a pointer to Bravyi et al., Zhu–Breuckmann, or Sayginel et al.) is required. *Fix:* add a two-paragraph appendix with the precise inclusion and a worked example of a Tanner automorphism that fails to lift to a stabilizer automorphism.

3. **The "four orders of magnitude" speedup is comparing incomparable quantities.** At n ≥ 40 GAP times out and the proxy returns in milliseconds — the ratio is undefined rather than "four orders of magnitude". At n ≤ 30 the ratio is finite but the quantities computed differ (one is an upper bound, the other is the target). *Fix:* report speedup only at n ≤ 30 where both terminate, and replace the "four or more orders" language with "the proxy terminates on every tested code where the GAP pipeline times out, and is at least 10³× faster on codes where both terminate."

4. **Venue scope rests on precedent not cited.** §4.1 asserts that Quantum and SciPost Codebases "routinely accept infrastructure/tooling papers with clear validation plans" without naming a single prior paper at either venue. *Fix:* cite at least two precedents per venue (see §5 below).

5. **No RL run, yet the title advertises "RL-Driven qLDPC Code Discovery".** The title frames this as an RL-enabling contribution; §4.4 explicitly disowns it. *Fix:* rename to something like "A Tanner-Graph Automorphism Proxy for Transversal-Clifford Rewards: Profiling and Infrastructure."

## 4. Minor concerns

- §3.1 shows `k = 0` at n ∈ {20, 30, 40, 50, 48, 72} for generic polynomials. If almost all probed codes are trivial (k = 0), the GAP timings on non-trivial codes are underrepresented. At minimum, the text should flag this and indicate that warm-GAP-on-gross at these n-values is the missing control (§3.1 already notes this — promote it to a numbered open item).
- §3.3: the zero non-trivial density at (p_deg, q_deg) ∈ {(4,4), (5,5), (6,4)} suggests the sampler is mis-specified — almost all 3-term BB polynomial pairs violating CSS orthogonality A Bᵀ + B Aᵀ ≠ 0 mod 2 is expected, but 0 / 60 per cell without rejection sampling on the orthogonality constraint is a methodology bug, not a scientific finding. State this as such.
- §3.2: reporting autgroup order 144 at both n = 36 and n = 144 is curious. Is this a coincidence of the Bravyi gross construction or an artefact? A one-sentence remark would help.
- The abstract says "5.9 ms at n = 288" but §3.2 table says 0.0059 s. Consistent but mixing ms and s across abstract/body hurts readability.
- Library versions (`stim 1.16-dev`) mixing development and release versions should be pinned to a commit hash for a Codebases submission.
- §5 "Related work … unchanged" from v1 is not acceptable in a standalone manuscript — the reviewer has no access to v1.

## 5. Is the "infrastructure paper" framing defensible?

**Partially.** SciPost Physics Codebases explicitly accepts code/tooling submissions, and Quantum has accepted software-centred papers (for example, Stim by Gidney, Quantum 5 (2021) 497; PyMatching by Higgott, ACM Trans. Quantum Comput. 3 (2022), though not Quantum proper; and the qiskit-based decoder papers). The authors should cite these as venue precedents. The framing is defensible *if* the infrastructure actually works for its stated purpose — which loops back to major concern 1: a proxy whose correlation to the target reward is unmeasured is not yet infrastructure, it is a proposal for infrastructure. Compare with Stim, which was published alongside exhaustive benchmarks demonstrating correctness against analytical cases; the analogue here is proxy–rank correlation.

Specific precedents the authors should cite: Gidney, *Stim: a fast stabilizer circuit simulator*, Quantum 5, 497 (2021); Higgott & Gidney, *Sparse Blossom* (arXiv:2303.15933); any SciPost Codebases-published QEC tool in the last two years. Without these, §4.1 is an unsupported venue claim.

## 6. Honest caveat section audit

§4.3 lists four open items. Item 1 (correlation validation) is load-bearing — without it the proxy is unvalidated. Item 4 (end-to-end RL run) is the experiment that the original framing demanded. Items 2 and 3 are reasonable extensions.

The honesty is a *strength of character* but a *signal of prematurity*. A Codebases paper about a new tool normally ships with the tool's primary validation. Here the primary validation is in the "open work" list. The authors have identified the right experiment (§4.3 item 1) and the remedy (offline multi-day GAP, or MAGMA) — they should execute remedy (a) on 5–10 codes at n ≤ 16 before resubmission, even if each run takes 48 hours. This is the minimum viable evidence that the proxy tracks the target.

## 7. Open validation blocker severity

**High.** A reader cannot adopt the proxy as an RL reward without knowing whether it correlates with the transversal-Clifford rank. The proxy could, a priori, be an arbitrarily loose upper bound — for example, always returning n! for symmetric Tanner graphs while the true rank is 1. §4.2 acknowledges this failure mode ("A Tanner automorphism that swaps two qubits may fail to preserve the stabilizer group") without bounding its frequency. Any downstream RL practitioner who uses the proxy unvalidated risks reward-hacking in exactly the way §4.3 item 2 warns about.

The paper in its current form offers the proxy as a tool but asks the community to do the correctness check. That inversion is acceptable only if the authors have exhausted every path to the correctness check themselves — and the paper does not demonstrate this. A fresh GAP compile with `UseLibrary := true` and a multi-day wall budget, or a handful of hand-computed rank values from the Bravyi 2024 supplementary materials, would suffice.

## 8. Figures and tables

The manuscript contains two tables (§3.1 GAP timings, §3.2 proxy timings). There are **no figures**. For an infrastructure/Codebases paper I expect at minimum: (i) a log-log timing plot GAP-vs-proxy vs n, (ii) a scatter of log-proxy vs log-rank on whichever codes can be computed, (iii) a schematic of the 3-coloured Tanner graph construction. The repository mentions `make_figures.py` but no figures are embedded in the manuscript. For peer review, figures embedded in the PDF/markdown are expected.

The tables themselves are clean; the n = 40 timeout row lacks a k value, which is minor but makes the row harder to interpret.

## 9. Reproducibility

The Data and code availability section names five scripts and a `results.tsv`. Library versions are given to minor-version precision except stim (`1.16-dev`). Hardware is described generically ("AMD/Intel x86-64 CPU") — for wall-clock claims the exact CPU model matters (a Zen 4 at 5.7 GHz vs a Skylake at 2.4 GHz differ by ~3x). The GAP+GUAVA install path is given (`apt-get install gap gap-guava`), which pins to Ubuntu 24.04 repository versions; this is acceptable.

Missing: (i) random seed for the §3.3 polynomial sample, (ii) exact CPU model, (iii) commit hash for stim-dev, (iv) whether pynauty was built against the system nauty or the vendored one. A Codebases referee will flag all of these.

## 10. Verdict

**MAJOR REVISIONS.**

The infrastructure observation is real and worth publishing. The proxy proposal is principled. But the central correctness claim is unvalidated, the speedup comparison is partly against timeouts rather than completed computations, and the title still advertises an RL contribution the paper disowns. These are fixable with a focused revision rather than a new research programme.

## 11. Three specific actions before resubmission

1. **Execute §4.3 item 1 remedy (a) on 5–10 small codes (n ≤ 16).** Run offline GAP with a multi-day budget to obtain ground-truth transversal-Clifford rank, compute Spearman and Pearson correlations against the proxy, include a scatter plot. If the correlation is weak, report it honestly and reframe the proxy as a *structural* upper bound rather than a *reward* surrogate.

2. **Rename the paper and tighten the speedup claim.** New title should drop "RL-Driven qLDPC Code Discovery" in favour of an infrastructure framing. Replace "four or more orders of magnitude" with a precise statement at n ≤ 30 where both pipelines terminate, and separately report the qualitative observation that the proxy terminates at every n where GAP times out.

3. **Add a formal statement and proof of the upper-bound claim in §2.4**, along with venue-precedent citations in §4.1 (at least two prior QEC infrastructure papers at Quantum or SciPost Codebases), an embedded log-log timing figure, the missing reproducibility details (CPU model, seed, stim commit hash), and a standalone §5 Related Work that does not reference v1.
