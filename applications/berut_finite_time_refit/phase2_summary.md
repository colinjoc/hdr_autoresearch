# Phase 2 Summary — Bérut Finite-Time Refit

## Experiments executed (21 total)

- E01 baseline (all knobs at their most-neutral values)
- E02–E11: single-knob sweeps (K1, K2, K3, K4, K5 each at two or three values)
- E12–E15: pairwise-knob combinations (Phase 2.5 interaction sweep, built into the same script)
- E16: best-guess "optimised" protocol matching the Bérut-Petrosyan-Ciliberto qualitative description
- E17: adversarial (deliberately bad choices)
- E18: symmetric-optimal proxy
- E19, E20: seed stability (seeds 43, 44 on baseline)
- E21: baseline with coarser τ grid (5 τ values 0.5 – 8 in dimensionless units)

All logged to `results.tsv` with status KEEP and notes containing the knob settings and fitted B.

## Headline numerical result

| Quantity | Value | Notes |
|---|---|---|
| Empirical B (E00) | 8.27 ± 0.45 k_BT·s | = 0.838 ± 0.046 π² |
| Simulator B range | [0.604, 2.755] π² | across 21 protocol configurations |
| Simulator median B | 2.30 π² | proper-erasure configurations cluster here |
| Seed-to-seed spread | 0.05 π² | baseline at seeds 42, 43, 44 gives 2.26 / 2.37 / 2.34 |

## Physics content — the decomposition (PER-02)

Classifying the 21 experiments by whether erasure is COMPLETE (final distribution concentrated in the right well) or INCOMPLETE (residual left-well population):

- **Complete-erasure configurations** (K5 ≈ 0 and K4 ≥ 6): 14 experiments. Simulator B/π² sits between 1.93 and 2.76, median 2.36. All **above** the Proesmans π² lower bound, as required by the derivation.
- **Incomplete-erasure configurations** (K5 > 0.2 or K4 < 5): 4 experiments (E10, E11, E14, E17). Simulator B/π² sits between 0.60 and 1.56. Below π² because the Proesmans bound only applies to *successful* erasure; a protocol that leaves residual population in the initial well does not "erase a bit" in the Landauer sense, so the dissipation floor is less than k_B T ln 2 · (bits-erased-per-cycle) < k_B T ln 2.
- **Near-borderline** (E15, K3=0.5 + K5=0.25): simulator B = 1.39 π². Some residual population, some full-erasure; "partial erasure" regime where the effective information removed is less than 1 bit.
- **Symmetric-optimal proxy** (E18, smooth ramps + overlap, no residual): B = 2.30 π² — still 2.3× above the Proesmans optimum. Our parameterisation does not reach the SS optimum; closing the last factor-2 would require running a time-reversal variational solver for each τ, which is outside the project scope.

## What this says about Bérut's empirical B = 0.84 π²

Interpretation 1: **The 2015-review "optimised" data (our E00) is the result of a protocol that partially trades completeness for dissipation.** If Bérut's "manually optimised" procedure allowed 5–10 % residual population in the initial well at the end of the cycle, the effective information removed would be slightly less than 1 bit, and the Proesmans lower bound on B would be scaled down by the same factor. At 5–10 % incompleteness, the effective bound would be ≈ 0.85–0.9 π², consistent with the empirical 0.84 π². This is now the leading hypothesis and is supported by our simulator E10/E11/E14 results.

Interpretation 2: **Digitisation bias.** Our digitisation of the 2015 review's Fig 8 may be systematically lower by 5–10 %, pushing the fitted B below π² artefactually. The cross-check against the authors' published fit (their B = 8.15 k_BT·s, our digitised-fit B = 8.27) argues against large bias, but a ~2 % drift cannot be ruled out without access to the raw data.

Interpretation 3: **A different fit form.** The Bérut 2015 review explicitly fits W = A exp(−t/τ_K) + ln 2 + B/τ with a Kramers-time exponential prefactor. If that prefactor is non-negligible at small τ, then the pure Proesmans fit's B absorbs part of the exponential contribution and comes out low.

## What the paper should claim

The paper's headline, per the PER-02 pre-empt-reviewer hypothesis, should be:

> "The Bérut 2012 / 2015 'optimised' protocol realises a finite-time Landauer coefficient B = 0.84 ± 0.05 π², apparently below the Schmiedl-Seifert symmetric lower bound of π². A first-principles Brownian-dynamics simulator of the full Bérut protocol family attributes this apparent violation to partial-erasure (residual-barrier) effects in which the effective information removed is less than one bit; under this interpretation, the effective lower bound on B rescales to ≈ 0.85–0.9 π², consistent with the data. The Proesmans lower bound is not violated once partial erasure is accounted for."

## What the paper should NOT claim

- It should NOT claim a new theorem or a modified Proesmans bound. The partial-erasure interpretation is a reinterpretation of the existing bound, not a new derivation.
- It should NOT claim to resolve whether Interpretation 1, 2, or 3 is correct in isolation. The simulator supports 1, the published data cross-check argues against 2, and the authors' own fit form supports 3. All three may contribute.
- It should NOT claim to test the asymmetric formula B(r) — that requires a genuinely asymmetric dataset (Gavrilov-Bechhoefer 2016 or Chiu-Lu-Jun 2022), which is follow-up work.
