# Scope Check v2 — Non-Markovian TUR Search

**Reviewer role:** grouchy stochastic-thermodynamics reviewer, Phase −0.5 round 2 of 3. Fresh sub-agent, no prior conversation context. Inputs: `proposal_v2.md` and the Phase −0.5 section of `program.md`.

## 1. Novelty of KUR-vs-TUR comparison on Skinner-Dunkel data

Genuinely narrow and, as far as I can tell, unclaimed. The Van Vu & Hasegawa KUR (2022–2024 series in *J. Phys. A* and *Phys. Rev. Research*) has been applied to toy Markov chains, to molecular-motor **models**, and to some electronic single-electron-box data (Pekola group, 2023). I am **not** aware of a published KUR evaluation on Skinner-Dunkel's own flagellar-motor or beating-flagellum time-series, nor on Berry-lab ribosome dwell-time traces. Closest competitors: (i) Ohga, Ito, Kolchinsky 2023 *PRL* — "thermodynamic bound with activity" on a chemical model, no biological data; (ii) Dechant & Sasa 2021 *PRX* — fluctuation response, different observable; (iii) Van der Meer et al. 2023 follow-up on trajectory σ-estimation. None publish the KUR/TUR ratio on Skinner-Dunkel's public traces. Novelty is real but **small** — this is a confirmatory empirical note, not a result. That matches PRE, not PRL.

## 2. Does the data-access gate actually protect the project?

Partially. The gate is stated as a hard pause at Phase 0.5 with a 2-week email window, which is fine in principle. In practice: Skinner is no longer at MIT (moved 2023), and Dunkel's lab does not routinely deposit per-trajectory data — the PNAS SI has cycle histograms, not raw traces. **Realistic failure mode: one email, no response in 2 weeks, project pauses indefinitely.** The proposal says "paused" but does not name a substitute. Add a fallback: if Skinner-Dunkel is dark, pivot to Pekola single-electron-box or Bustamante optical-trap DNA-unzipping data (both publicly deposited). Otherwise the gate is a polite way to die.

## 3. Falsifiability

Four binary outcomes, most clean:

- **O1 (data gate)** — feasibility, not falsifiability. Fine.
- **O2 (KUR ≤ TUR)** — **still partially tautological.** KUR ≤ TUR is a proven theorem for Markov jump processes with the same current. An empirical "violation" on a non-Markovian time-series most likely indicates (a) the σ estimator mis-specifies the generator, (b) coarse-graining changes the admissible bound class, or (c) the KUR instance used does not apply to the observable. Calling this "a major result" oversells a bug. Recommend rewording: O2 = *measure the ratio KUR/TUR; a ratio >1 triggers estimator diagnostics, not a Nature paper.*
- **O3 (F-scaling)** — clean: pre-registered ΔAIC ≥ 2 vs constant-ratio null. Good.
- **O4 (≥2 datasets)** — operational, not falsifiability. Fine.

So three of four are genuine; O2 needs rewording to drop the "violation = discovery" framing.

## 4. Venue fit

PRE is correct. A narrow empirical KUR/TUR check on one–two datasets with an F-regression fits PRE's "evaluations of stochastic-thermodynamics bounds" scope. JSTAT fallback is sensible. Do not attempt PRL.

## 5. Top three killer objections

1. **(MAJOR) Data-access single point of failure.** No response from Dunkel kills the project. **Mitigate:** name a concrete Phase 0.5 fallback dataset (Pekola single-electron box; Bustamante DNA unzipping) *in proposal v2 itself*, not after the gate triggers.
2. **(MAJOR) O2 still oversold.** Framing KUR>TUR as "publishable major result" misreads the theorem. **Mitigate:** rewrite O2 as a ratio measurement with diagnostic protocol for anomalies; move "violation = discovery" language out.
3. **(MINOR) F-Fano indicator may saturate or anti-correlate on the small number of datasets accessible.** With N=2 systems, the regression ΔAIC test has near-zero power. **Mitigate:** pre-register that with N<4 datasets the F-regression is descriptive only; claim shifts to the ratio itself.

Scope is now publishable-in-PRE if the two MAJORs are patched. They are patchable in one paragraph each.

VERDICT: REFRAME
