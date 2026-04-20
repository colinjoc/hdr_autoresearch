**Target**: publication — primary venue: Physical Review E, fallback venue: Biophysical Journal

# Does *E. coli* chemotaxis saturate the kinetic uncertainty relation? A re-analysis of the Lan 2012 energy-speed-accuracy dataset

## 1. Question

Lan, Sartori, Neumann, Sourjik & Tu (2012, *Nature Physics*) measured the energy-speed-accuracy trade-off in *E. coli* chemotactic adaptation: dissipation rate σ_phys, adaptation-accuracy precision ε, and adaptation time τ_adapt as independent quantities across a range of signalling-network perturbations. Does their dataset saturate the kinetic uncertainty relation (Van Vu–Hasegawa 2022) combined with the housekeeping-entropy decomposition (Esposito–Van den Broeck 2010) — and if so, is the combined KUR–housekeeping bound a *better* predictor of chemotactic efficiency than the Landauer-Bennett "cost per bit" framework that currently dominates the biophysics literature?

## 2. Proposed contribution

**(a) Extract the Lan 2012 dissipation-precision data.** Their Fig. 3 reports σ_phys (J/s per molecule) vs ε (adaptation-accuracy variance) at several signalling-network perturbation strengths. Digitise the full curve; normalise to per-molecule and per-cell quantities.

**(b) Compute the INT09 / KUR-plus-housekeeping bound** from the `thermodynamic_info_limits` predecessor paper at the Lan 2012 operating point. Use the housekeeping fraction φ extracted from Kempes et al. 2017 for *E. coli*.

**(c) Saturation test.** Report the ratio observed-ε / KUR-predicted-ε across the Lan 2012 perturbation scan. Saturation (ratio → 1) would mean chemotactic hardware is operating *at* the thermodynamic floor — a major biophysics result. Loose bound (ratio >> 1) is the "thermodynamic headroom" narrative.

**(d) Comparison with Landauer-Bennett cost.** Compute the corresponding Landauer-Bennett cost per bit for the same data. Which bound is tighter? Which tracks the actual variation across the Lan perturbation set?

## 3. Why now

Lan et al. 2012 is 14 years old but its data has never been compared against modern stochastic-thermodynamic bounds (the KUR was only published in 2022). The predecessor paper `thermodynamic_info_limits` has an INT09 bound but no empirical biological validation. This closes the gap with a freely available published dataset.

## 4. Falsifiability

Three binary kill-outcomes:

- **Bound consistency.** Either the Lan 2012 data is everywhere below the KUR-housekeeping bound (bound holds), or it is above it somewhere (bound fails — major result).
- **Saturation.** Either the ratio observed / bound is < 3 at the tightest point (approximate saturation), or it is > 10 everywhere (loose).
- **Bound tightness vs Landauer-Bennett.** Either the KUR-housekeeping bound correlates with observed performance across perturbations with r² > 0.5, or it does not (null result).

## 5. Named comparators and differentiation

- Lan, Sartori, Neumann, Sourjik, Tu (2012), *Nature Physics* 8, 422–428 — dataset.
- Van Vu & Hasegawa (2022), *J. Phys. A* — KUR.
- Esposito & Van den Broeck (2010), *PRL* — housekeeping decomposition.
- Kempes, Wolpert, Cohen, Pérez-Mercader (2017), *Phil. Trans. Roy. Soc. A* — biological φ estimates.
- Hartich, Barato, Seifert (2014), NESS-efficiency biological signalling — prior TUR application to chemotaxis, without KUR or housekeeping.

No prior work combines KUR + housekeeping + Lan 2012 data for a direct saturation test.

## 6. Target venue

**Physical Review E** — publishes biophysics-flavored tests of stochastic-thermodynamics bounds. **Fallback: Biophysical Journal** if the biological framing dominates the physics.
