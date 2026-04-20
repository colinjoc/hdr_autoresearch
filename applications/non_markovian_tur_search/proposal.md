**Target**: publication — primary venue: Physical Review Letters, fallback venue: Physical Review X

# Does any biomolecular system empirically violate the thermodynamic uncertainty relation? A search in single-molecule datasets

## 1. Question

The standard thermodynamic uncertainty relation (Barato–Seifert 2015) holds for Markovian processes in non-equilibrium steady state. In the `thermodynamic_info_limits` predecessor paper's RV05 experiment, a semi-Markov Erlang-10 process was shown to violate the standard TUR mathematically. Do any *real biological systems* — ribosomes, ion channels, RNA polymerases — have non-Markovian dwell-time distributions with enough non-exponentiality to violate the standard TUR in published single-molecule experimental data?

## 2. Proposed contribution

**(a) Assemble published single-molecule dwell-time datasets.** Candidate sources: Wen et al. (2008, *Nature*) ribosome single-codon kinetics; Chen et al. (2013, 2014) ribosome elongation; Zeger et al. (2019) ion-channel patch-clamp; Greenleaf et al. (2009) single-molecule optical trapping of RNA polymerase; Blanchard et al. FRET-based ribosome. For each, extract the dwell-time distribution P(τ_dwell) and its empirical variance / mean.

**(b) Classify systems by non-Markovianity.** Compute the "shape parameter" k in a best-fit Erlang-k fit, or equivalently the Fano factor of the dwell-time distribution. Markovian (pure exponential) dwell times have k = 1 (Fano = 1). Biological systems with multiple conformational intermediates have k > 1.

**(c) Compute empirical TUR relative variance ε_obs = Var(N)/⟨N⟩² and compare to 2 k_B / σ.** N = number of completed cycles over observation time. σ = entropy-production rate per cycle, estimated from ATP hydrolysis / GTP hydrolysis known per step.

**(d) Identify any system with ε_obs < 2 k_B / σ.** This is a direct TUR violation. Per Van Vu & Hasegawa 2020, this is only possible for non-Markovian systems, so the correlation of violation with k (Erlang shape) should be monotonic.

## 3. Why now

Single-molecule biology has accumulated ~15 years of published dwell-time distributions since the TUR was derived in 2015. Nobody has systematically compared these distributions against the TUR. The RV05 finding in `thermodynamic_info_limits` that Erlang-k mathematically violates the TUR makes the empirical hunt sharp and specific.

## 4. Falsifiability

Four binary kill-outcomes:

- **Data availability.** Either five or more published single-molecule datasets with sufficient precision on dwell-time distributions are reachable from open sources, or the project is insufficiently empirical to proceed.
- **TUR hold for Markovian systems.** All extracted systems with k ≤ 1.5 either satisfy the TUR (ε_obs ≥ 2 k_B / σ), or they violate it — a violation in a Markovian system would falsify the TUR itself (major result).
- **TUR violation in non-Markovian systems.** At least one system with k ≥ 5 either violates the TUR or does not. Either outcome is informative: violation confirms the mathematical prediction; non-violation implies real biological non-Markovianity is not strong enough to break the bound.
- **Correlation with Erlang-k.** The ratio ε_obs / (2 k_B / σ) either monotonically decreases with k, or it does not.

## 5. Named comparators and differentiation

- Barato & Seifert (2015), *PRL* — original TUR.
- Pietzonka, Barato, Seifert (2016), *PRE* — universal current-variance bound.
- Horowitz & Gingrich (2020), *Nat. Phys. review* — comprehensive TUR review.
- Van Vu & Hasegawa (2020) — non-Markovian extension.
- Proesmans, Falasco, Esposito (2021) — TUR bounds under time-dependent driving.

No prior work has attempted a systematic empirical hunt for TUR-violating biomolecular systems using published single-molecule data.

## 6. Target venue

**PRL** — if a TUR violation in a Markovian system is found (very high-impact, unlikely). **PRX** — if a clear Erlang-k correlation is established. **PRE fallback** if the project produces a null result across all tested datasets.
