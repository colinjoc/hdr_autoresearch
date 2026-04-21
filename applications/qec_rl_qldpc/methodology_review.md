# Phase 2.75 Methodology Review — qec_rl_qldpc

Reviewer: fresh blind sub-agent, no prior conversation. Inputs: README, proposal_v2,
publishability_review, proposal_v3, phase_0_5_findings, results.tsv, scripts
`e00_per1_profile.py` / `e00_per1_probe.py` / `e01_proxy_profile.py` / `e02_pareto_bb.py`,
data_sources, research_queue (PER-1..PER-3 + hypotheses).

## 1. Scope-shift audit

The claim the paper now proposes — "nauty-based Tanner-graph autgroup order is a
tractable proxy for the transversal-Clifford-rank reward" — is a **scope retreat
dressed as a scope adjustment**, and the author even acknowledges it in
`phase_0_5_findings.md` §"Implication for proposal — draft v4 amendment" (line 72
"no longer directly achievable... on consumer hardware under the available tooling").

Proposal v2 §2 and v3 §2 both frame the headline as a *Pareto-front study*
(multi-code dominance claim, structural-novelty criterion, Kill #3 "Dominance
kill"). proposal_v3 §2 adds the correction that the reward must be the *rank of
induced logical Clifford group*, explicitly not raw automorphism count — a
correction motivated by H-TG-1 (research_queue line 337-343) precisely to avoid
reward-hacking on symmetric-but-logically-trivial codes.

The Phase 0.5 findings now propose exactly that forbidden metric: nauty returns
the order of the Tanner-graph automorphism group (an upper bound on the
stabilizer-preserving subgroup, and therefore a *further* upper bound on the
induced-logical-Clifford-rank). This is the *raw-count* metric in a graph-theoretic
disguise. The author's own PER-2 / H-TG-1 pre-registration said this is wrong.

`phase_0_5_findings.md` line 76 argues "the reward *metric* changes; the
*research question* does not". That is not the correct bar. The pre-registered
kill condition for proposal_v3 PER-1 (proposal_v3 §4 item 1) was: "swap the
reward to a cheaper proxy (fold-transversal-count OR permutation-subgroup-size
OR precomputed family tables)." Tanner-graph-autgroup-order is none of those
three. It is a **fourth** proxy not on the pre-registered fallback list.

**Verdict:** the change is substantive enough that a fresh Phase 0.25 re-review
is warranted. The specific question "does the nauty proxy recover the rank
signal well enough that the Pareto-dominance claim (proposal v3 §2) survives"
has not been tested and is the load-bearing assumption of the new central claim.

## 2. PER-1 interpretation

The GAP+GUAVA results in `results.tsv` lines 2-9 are internally consistent:
3.02 s at n=12 (includes cold-start), 0.04 s at n=20, 0.11 s at n=30, then
TIMEOUT at n=40 and all larger. The 60 s timeout is a *subprocess wall
timeout*, not a GAP-internal timeout, so we do not know whether the n=40 call
would have returned in 61 s or 10⁶ s. That matters — the proposal v3 §4 Kill #1
rule is "exceeds 50% of a typical 0.5 s RL step budget" which is triggered
already at n=30 (0.11 s ≈ 22% of step budget, uncomfortably close) and almost
certainly at n=40.

**Is this a methodological issue or a fundamental limit?** Three concerns
against a fundamental-limit reading:

(a) `e00_per1_probe.py` line 42 uses a generic polynomial family
`BBCode({x:pd, y:qd}, x + y + y**2, y + x + x**2)` for non-gross codes, but
only `BBCode({x:12, y:6}, x**3 + y + y**2, y**3 + x + x**2)` for the gross
code. These are not matched — the same polynomial family was not tried at
n=40/50/48/72. The generic family may have much larger automorphism groups
than the Bravyi gross polynomials, and GAP time is driven by group size, not
n. The profile does not disentangle "GAP doesn't scale in n" from "these
particular polynomials have enormous autgroups that GAP can't finish".

(b) `qldpc.circuits.get_transversal_automorphism_group` has known
subprocess-launch overhead (the 3.02 s at n=12 is mostly the cold GAP
start, as noted in line 13 of phase_0_5_findings). The profile calls it
once per code with no caching. A realistic RL use would amortise cold-start
over thousands of episodes.

(c) No attempt was made at `get_transversal_ops` (which was the second
function profiled in `e00_per1_profile.py` line 79, under `local_gates={"S",
"H", "SQRT_X", "SWAP"}`). The probe script dropped that function entirely,
so we only have autgroup wall-clocks. The rank-metric proper is in
`get_transversal_ops`, not in the autgroup enumeration.

**Conclusion on PER-1:** The GAP+GUAVA pipeline does time out at n≥40 under
the specific conditions tested, but the test is too narrow to claim "fundamental
limit on consumer hardware". It shows a limit under (one polynomial family ×
no caching × subprocess cold-start × 60 s hard wall). The v3 §4 Kill #1 clause
actually requires testing "at any tested n ∈ {20, 30, 50}" — n=50 under the
*gross-polynomial* family was never attempted. PER-1 is a partial FAIL that has
been written up as a total FAIL; fixing it requires one more hour of
probing at n=40–50 with the gross polynomials + subprocess warm-start.

## 3. Proxy ↔ reward correlation

The proxy is: order of the 3-coloured (qubit / X-check / Z-check) Tanner-graph
automorphism group via `pynauty.autgrp` (`e01_proxy_profile.py` lines 36-63).
This is **provably an upper bound** on the transversal-Clifford rank (which is
what the reward needs), but the gap between upper bound and true value is
unbounded — a code with a large symmetric Tanner graph but no stabilizer-lifting
of those symmetries gives proxy = large, reward = trivial. This is the exact
reward-hacking failure mode that H-TG-1 (research_queue line 337) was designed
to exclude.

From `results.tsv` line 10: BB_small_3x3 at n=18, k=8 has autgroup order 2592.
From line 32: BB_pd3qd3 at n=18, k=12 has proxy 1.045×10¹⁴. Both are n=18,
same polynomial family, just different coefficient choices. Proxy spreads by
**eleven orders of magnitude across one (p,q)=(3,3) cell.** Without a reward
↔ rank correlation measurement at small n, we have no idea whether the
1.045×10¹⁴ code has correspondingly richer logical Clifford action or just a
pathologically symmetric Tanner graph that lifts trivially.

**Load-bearing:** the Phase 1 plan in `phase_0_5_findings.md` line 80 lists
"validate proxy ↔ rank correlation on small codes (n ≤ 30) where GAP is
tractable" as item (1) of next steps. **This is not yet done.** The proxy is
adopted as the reward signal (line 74, primary reward of proposal v4) with no
measured correlation. Acceptable only as a staged roll-out: validation MUST
precede any Phase 1 training, and the validation protocol needs pre-registration
now, not after training results exist. Recommended protocol: for every BB code
at n ∈ {12, 18, 20, 30} with k>0, compute (nauty-order, `get_transversal_ops`
Clifford rank) pair. Report Kendall τ and Spearman ρ. If τ < 0.5 the proxy
should be redesigned (e.g., add a stabilizer-lift check before scoring) or
abandoned for the cheaper-pre-registered alternatives (fold-transversal-count).

## 4. Brute-force Pareto data quality

`e02_pareto_bb.py` line 62 sweeps (p,q) ∈ {(3,3), (4,4), (5,5), (6,4), (6,6)}.
Line 72 caps polynomial sampling to 40 per cell via `random.sample` with
seed 42. Line 76 truncates polynomial *pairs* to the first 60 via
`itertools.islice(itertools.product(polys_sample, repeat=2), 60)` — this is a
cap of **60 pair evaluations per cell**, not 40×40=1600. Of those 60,
anything with k=0 is discarded (line 81).

The results.tsv summary line 17 reports "48codes_8Pareto". The 20 kept rows
at lines 18-37 are **all at n=18** (the (3,3) cell — 2·3·3=18), none at n=32
((4,4) → 32), n=50 ((5,5)), n=48 ((6,4)), or n=72 ((6,6)). Either (a) no
non-zero-k codes were found in the larger cells from 60 random pairs each, or
(b) they were found but only the first 20 rows were written to TSV (line 125
`results[:20]`). The script's own stdout would distinguish these, but is not
saved.

A read of `e02_pareto_bb.py` line 125 confirms: the TSV is truncated to the
first 20 results. So the n=72 Pareto point in phase_0_5_findings.md is
**not** in results.tsv and is un-auditable from disk. The summary row says
"48 codes, 8 Pareto" — but we see no evidence of the other 28 codes or the 8
Pareto points beyond the n=18 rows.

**Concerns:**

1. Random sampling of 60 pairs per cell is a tiny slice of the BB polynomial
   space at (p,q)=(5,5) (10×10 3-term monomial space has
   ~C(25,3)²=2300² ≈ 5M pairs). Claiming a Pareto front from 60 samples at
   n=50 would be indefensible, and indeed no such points appear.
2. The (4,4), (5,5), (6,4), (6,6) cells likely *do* produce k=0 codes often
   — BB codes at generic polynomials tend to have k=0 unless the polynomials
   have common factors / specific algebraic structure. But this needs to be
   reported, not assumed.
3. The Pareto table in phase_0_5_findings (referenced as 8 points at n=18
   or n=72) is too coarse to claim a "Pareto-front study" contribution. A BB
   sweep with 8 points, mostly co-located at two n-values, is a smoke test,
   not a scientific artefact.

**Verdict on §4:** the brute-force infrastructure works (nauty returns
sensible numbers at <6 ms per call), but the enumeration is under-powered.
Before claiming a Pareto contribution, the sweep needs (a) to log every
surviving code, not just the first 20; (b) to exhaust the small cells
((3,3), (4,4)) fully; (c) to properly sample (at least 10k pairs) the (5,5)
and (6,6) cells or use a seeded-enumeration strategy targeting known-k-positive
coefficient configurations.

## 5. Reward-hacking risk for the proxy

The reward-hacking risk is that automorphisms counted by nauty may have
trivial logical action — this is (by construction) the failure mode H-TG-1
was designed against. `phase_0_5_findings.md` line 50-53 proposes two mitigations:

(a) Separate Hx-only and Hz-only proxies to quantify CSS-duality contribution.
(b) Structural-novelty post-check against reference families.

Neither has been measured. (a) is flagged as "Phase 1 work" in line 52; (b)
requires the equivalence-check code (PER-2) which per research_queue line
25 has a pre-registered default ("Pauli-equivalence under qubit permutation +
local Clifford") but no implementation in-repo. Neither of the four scripts
reviewed (`e00_per1_profile.py`, `e00_per1_probe.py`, `e01_proxy_profile.py`,
`e02_pareto_bb.py`) implements (a) or (b).

**The claim "the nauty proxy is a tractable proxy for transversal-Clifford
rank" is currently unfalsifiable from the artefacts on disk.** It is an
unverified *upper bound*; the gap between upper bound and true rank is
precisely the reward-hacking channel. Without at minimum a correlation
measurement at small n (§3) or the Hx/Hz split (a), the claim in the central
proposal is not defensible.

## 6. Is this still an RL paper?

It is not. Nothing in `results.tsv`, `e00*.py`, `e01*.py`, or `e02*.py`
references an RL loop. There is no PPO implementation, no `qdx` fork, no
policy update, no training curve. `phase_0_5_findings.md` line 68 says "a
custom PPO implementation on top of qldpc + nauty may prove simpler" —
meaning, plainly, not-yet-written. `proposal_v3` §3 commits to `qdx` + PPO +
`qldpc-org/qldpc` back-end; Phase 0.5 has implemented only the
back-end-profiling half.

Three possible paper framings, in decreasing defensibility:

- **(A) Methodology / infrastructure paper:** "PER-1 profile + nauty proxy
  design + correlation with rank at n ≤ 30 + a brute-force enumeration of BB
  codes at n ≤ 72". Venue: short-method note, possibly Quantum (journal) or
  a software paper in SciPost Codebases. No RL is needed. Requires the
  correlation study (§3) as a first-class result.

- **(B) Proxy-introduction paper:** claim is "nauty autgroup order correlates
  with transversal-Clifford rank, is O(n log n) in practice, and admits
  efficient RL reward computation at n=288." Same artefacts as (A) plus a
  demonstration that a toy RL loop using the proxy actually discovers known
  BB-family Pareto-optimal points. Requires: a minimal PPO or evolutionary
  local-search over BB polynomial coefficients, reported in one ablation.

- **(C) Pareto-front study (proposal v2/v3 headline):** not defensible on
  current artefacts. No RL run; no reference-set comparison; no
  structural-novelty check implemented; Pareto table is 8 points at
  two n-values.

The paper that is *actually* supported by the artefacts on disk is (A).
Writing (A) + (B) together is the cleanest path. Continuing to claim the v3
headline without substantial additional experiments (full RL training,
rank-vs-proxy correlation, structural-novelty check against 9 reference
families) would be overclaiming.

**Venue consequence:** npj Quantum Information (proposal v3 §8 primary)
expects a code-discovery contribution with at least one novel code. (A) is
not that paper. Quantum or npj Q Info-methods would accept (A)+(B); if the
author wants to preserve npj QI as target venue, they must restore the RL
loop and at least one Pareto-optimal discovered code.

## 7. Top three revisions before paper draft

1. **Run the rank-vs-proxy correlation study at n ≤ 30.** For every BB code
   with k > 0 at (p,q) ∈ {(2,3), (2,5), (3,3), (3,5)} where GAP is confirmed
   tractable per results.tsv (≤ 0.11 s), compute (nauty proxy, rank from
   `qc.get_transversal_ops`). Report Kendall τ and Spearman ρ between the
   two. Pre-register: if τ < 0.5, proxy is unusable and must be redesigned
   (e.g., add Hx-only / Hz-only split now, not "Phase 1 later").

2. **Re-run `e00_per1_probe.py` with gross-family polynomials at n=40, 48,
   50, 72, and with warm-started GAP (re-use the same process).** Current
   probe uses a generic family and fresh subprocess per call; the PER-1 FAIL
   claim rests on these two confounders. One afternoon of probing with
   (a) the gross polynomial family `x³+y+y²` / `y³+x+x²` at each n, (b) a
   single GAP process kept warm, (c) a 300 s timeout rather than 60 s.
   If the warm/gross variant still times out at n=40, the FAIL is robust
   and the proxy adoption is justified. If not, PER-1 must be re-verdicted.

3. **Pre-register the paper's revised scope and equivalence relation before
   any further experiments.** Either downgrade to (A) / (B) from §6 with
   npj QI replaced by Quantum / SciPost; or commit now to the additional RL
   work needed to restore proposal v3's Pareto-front headline. In either
   case, produce the `equivalence.py` Pauli-equivalence-under-permutation+LC
   module (PER-2 deliverable) and commit its git hash before any Phase 1 RL
   training starts (H-EQ-6 reinforcement). The current state — claiming v3's
   structural-novelty criterion while having no implementation in-repo — is
   the exact gap that would land a major-revision at npj QI.

## VERDICT: MAJOR-REVISIONS

The Phase 0.5 profiling work is competent within its scope, and nauty is
genuinely useful. But the project's central claim has silently migrated from
"RL-discovered Pareto-front qLDPC codes with rank-of-induced-logical-Clifford
reward" (v3) to "nauty proxy for Tanner-graph autgroup is useful", without
either (i) a correlation study that justifies the proxy, (ii) the RL loop
that the v2/v3 headline promised, or (iii) the structural-novelty
implementation that three published reviewer-pre-empts (PER-1/2/3) all
depend on. The PER-1 FAIL verdict itself rests on narrow testing that does
not rule out methodological fixes. The proxy is an upper bound on the
rewarded quantity and the gap is the exact reward-hacking failure mode
pre-registered as forbidden in H-TG-1. None of these alone is fatal, but
their combination requires substantive revision before paper draft: at
minimum the correlation study (§3), the re-tested PER-1 probe (§7.2), and
the explicit scope commitment (§6, §7.3). Proceed to paper draft only after
those three revisions.
