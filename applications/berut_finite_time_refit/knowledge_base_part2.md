# Knowledge base — Part 2 (Themes 3 and 4)

Stylised facts distilled from the literature review.

## F3.1 The overdamped Fokker–Planck slowest eigenvalue for a symmetric double well

At weak noise (Delta U >> k_B T), the slowest non-zero eigenvalue lambda_1 ~ 2 k_Kramers, where k_Kramers = (omega_well omega_barrier) / (2 pi gamma) exp(-Delta U / k_B T). This eigenvalue sets the inverse relaxation time for the bimodal-to-unimodal transition that Landauer erasure is. Source: Risken 1989 (T3_003), Hänggi-Talkner-Borkovec 1990 (T3_002).

## F3.2 The asymmetric Kramers prefactor

For asymmetric wells with depth ratio r, the forward and backward rates are not equal and the slowest eigenvalue picks up a geometric factor. For equal curvatures but unequal depths, the prefactor geometric factor is (1+r)²/(4r), with minimum 1 at r = 1. Source: Coffey-Kalmykov-Titov 2005 (T3_031), Hänggi-Talkner-Borkovec 1990 (T3_002).

## F3.3 The Schmiedl–Seifert variational optimal protocol for harmonic-trap shift

For shifting a 1D harmonic trap from x_0 to x_f in time tau, the minimum-work protocol has finite jumps at t = 0 and t = tau and excess-work W_diss - ΔF ≈ (gamma (x_f - x_0)² / tau) — scales as 1/tau. Source: Schmiedl-Seifert 2007 (T3_006).

## F3.4 The Wasserstein refined second law (Aurell 2011–2012)

For overdamped 1D Langevin dynamics, the mean dissipated work over a finite-time protocol of duration tau satisfies:

    ⟨W_diss⟩(tau) >= (k_B T / (tau D)) W²_2(rho_initial, rho_final)

where W_2 is the L² Wasserstein distance. This bound is tight in the fast-time limit. Source: Aurell-Mejía-Monasterio-Muratore-Ginanneschi 2011/2012 (T3_012, T3_013).

## F3.5 The Proesmans finite-time Landauer coefficient B = pi²

For a symmetric double-well with full dynamic control and perfect initial equilibrium, the mean dissipated heat in finite-time bit erasure is

    ⟨Q_diss⟩(tau) >= k_B T ln 2 + (pi² k_B T)/tau

valid in the regime where tau is long enough to allow thermalisation but short enough that the 1/tau correction is not negligible compared to ln 2. Source: Proesmans-Ehrich-Bechhoefer 2020 (T3_014, T3_015).

## F3.6 B = pi² is a lower bound, not a prediction

The bound is achievable only under idealised full-control of the potential (unrestricted U(x,t) landscape, no physical barrier to what the experimenter can command). Real experimental protocols typically dissipate more than the bound. The Bérut 2012 protocol is a specific, not-necessarily-optimal, protocol, so the empirical B will be >= π² by construction; a discrimination test asks whether it is **near** π² or whether it is substantially larger.

## F3.7 The Wasserstein distance for a bit erasure

For a system uniformly distributed over two wells of depth V_L and V_R (bit 0 and bit 1) and finally all in one well, the Wasserstein-2 distance depends on the inter-well separation L and the asymmetry. For equal-depth wells, W²_2 = L²/4. For asymmetric wells with initial occupancy proportional to exp(-V/kT), W²_2 has a geometric correction that generalises to give the predicted B(r) asymmetric factor (heuristic connection, not rigorously derived).

## F3.8 Kramers timescale vs Langevin relaxation timescale

The shortest relevant timescale in bit erasure is the Langevin relaxation within one well: t_relax ~ gamma / omega_well². The longest is the Kramers escape time: t_Kramers = 1 / (2 k_Kramers). For B k_B T / tau to dominate over ln 2 k_B T, we need B/tau > ln 2 ≈ 0.69, so tau < 14 seconds for B = π². The Bérut data go out to tau = 40 seconds, so the dataset spans both the dominant-1/τ and the dominant-ln 2 regimes. Source: Bérut 2012 (T3_046).

## F3.9 Boltzmann inversion bias at finite sample

For histogram-based Boltzmann inversion of the potential, the statistical bias at each bin scales as (k_B T)² / (N_effective bin_count). For N_eff ~ 10⁵ and bin_count ~ 50, the bias is ~ 0.01 k_B T per bin — small, but not zero. Source: Shoji et al. 2019 (T4_177), Bianchi et al. 2023 (T4_178).

## F3.10 Optimal protocol finite jumps

The Schmiedl-Seifert and Proesmans optimal protocols prescribe jumps in the control parameter at t = 0 and t = tau. In Bérut 2012 the protocol is a smooth lowering of the barrier; this is **not** the optimal protocol. Consequently the empirical B from the Bérut protocol should be larger than π².

## F3.11 The virtual-potential (feedback-trap) advantage

In a feedback trap the "potential" is constructed by software-applied feedback forces and is **known by construction**. This gives direct programmatic control over the asymmetry — r is not inferred, it is set. Source: Jun-Bechhoefer 2012 (T4_161), Bechhoefer feedback-trap series.

## F3.12 Bérut is NOT a virtual-potential trap

Bérut 2012 uses a time-shared actual double-well optical trap, not a virtual feedback trap. The trap potential U(x) is determined by (laser intensity × time at each focus) and must be inferred from the equilibrium position histogram — it is not set a priori. Source: Bérut 2012 Nature (T3_046), Bérut-Petrosyan-Ciliberto 2015 review (T3_048).

## F3.13 The Bérut published r

The Bérut authors do not publish r explicitly. They state the asymmetry is "reduced to ~0.1 k_B T" by tuning, which implies r values within ~ 0.8 to 1.2 of symmetric. The published U(x) polynomial is 6th-degree but the coefficients are not tabulated in the primary Nature paper or in the 2015 review. Source: Bérut-Petrosyan-Ciliberto 2015 (T3_048).

## F3.14 Bérut error bars

Dissipated heat has published error bar ± 0.15 k_B T, attributed to "reproducibility of measurement with same parameters" — this is a statistical estimate, not a fully propagated systematic uncertainty. Source: Bérut 2015 (T3_048).

## F3.15 The Bérut sample rate and N_effective

Data acquired at 502 Hz for ~ 50 minutes = 1.5 × 10⁶ points. Autocorrelation time of position in the trap ~ 3 ms, so N_effective ≈ 10⁵. Source: Bérut 2015 (T3_048).

## F3.16 The Gavrilov–Bechhoefer 2016 asymmetric-well result

In a virtual-potential feedback trap with *known* asymmetry, Gavrilov & Bechhoefer 2016 demonstrated that the **mean work** to erase can be less than k_B T ln 2 when the initial distribution is biased and the asymmetry is large. This is not a violation of Landauer — the dissipated heat (not mean work) is always bounded below by k_B T ln 2. But it means the mean work depends on the asymmetry in ways the Landauer bound does not constrain. Source: T3_053.

## F3.17 The Chiu–Lu–Jun 2022 asymmetric finite-time Landauer

In a feedback-trap-controlled asymmetric double well, Chiu-Lu-Jun 2022 directly tested the finite-time Landauer coefficient B at explicitly known r. Their result is the closest precedent for the asymmetric B(r) test but uses a different protocol class. Source: T3_089.

## F3.18 AOD diffraction asymmetry

A practical acousto-optic deflector does not deflect identically at different angles; typical asymmetry between nearby deflection positions is 5-10 percent in intensity. When deflector positions are used to time-share between two traps, this translates directly to a well-depth asymmetry in the effective potential. The Bérut 2012 trap uses AOD switching and does not report the measured diffraction-asymmetry. Source: Valentine et al. 2008 (T4_033), Serrao et al. 2024 (T4_146).

## F3.19 Time-sharing frequency limits on time-averaging

For time-shared dual traps, the switching rate must be >> the bead's inverse relaxation time for the bead to see an effective time-averaged potential. Bérut uses 10 kHz switching and bead relaxation ~ ms — this is on the edge of safety. Source: Chattopadhyay et al. 2013 (T4_036), Ranaweera & Bhattacharya 2010 (T4_039).

## F3.20 The Bérut potential height calibration

High-intensity barrier ~ 8 k_B T, low-intensity barrier ~ 2.2 k_B T. No explicit uncertainty. Polynomial fit is 6th degree. Source: T3_048.

## F3.21 Zulkowski-DeWeese Hellinger bound

Zulkowski-DeWeese 2014 gave an earlier finite-time erasure bound in terms of the squared Hellinger distance between initial and final distributions divided by tau. Tighter in the quasi-static limit, looser at finite tau than Proesmans. Source: T3_016.

## F3.22 Shortcut-to-adiabaticity

Using shortcut-to-adiabaticity protocols (Boyd-Patra-Jarzynski-Crutchfield 2022, T3_090), erasure can be accelerated below the naive Proesmans bound at extra dissipation cost. The asymmetric extension appears in the shortcut cost structure. Source: T3_090.

## F3.23 The Zhen et al. 2021 universal bit-reset bound

Zhen-Egloff-Modi-Dahlsten 2021 give a universal hardware-independent lower bound. In the zero-error, equal-initial-probability limit, the scaling is also B/tau, with a B-coefficient that matches Proesmans. Source: T3_060.

## F3.24 Thermodynamic uncertainty relation (TUR)

The TUR (Barato-Seifert 2015, T3_107) bounds current fluctuations by dissipation. For bit erasure, it gives a complementary bound to Proesmans in terms of final-state-error variance.

## F3.25 Identifiability of r from published Bérut

Without raw photodiode time series, r is estimable only from digitised U(x) plots. 95 percent CI on r is roughly 0.7–1.5 (high barrier) and 0.5–2 (low barrier).

## F3.26 Sensitivity of B(r) = π²(1+r)²/(4r) near r = 1

(1+r)²/(4r) evaluated at r = 1 has derivative 0 (it's a minimum). A ±50 percent CI on r near r = 1 maps to only ~ 5 percent uncertainty on B(r). Consequence: the Bérut dataset cannot discriminate B(r) from B = π² for realistic r values.

## F3.27 Bérut protocol is NOT the optimal Schmiedl-Seifert protocol

Bérut's erasure protocol is a smooth linear lowering of the barrier. The optimal protocol has finite jumps at t=0 and tau. So empirical B > π² is expected simply from protocol-suboptimality.

## F3.28 No rigorous derivation of B(r) = π²(1+r)²/(4r)

The formula B(r) = π²(1+r)²/(4r) is a heuristic that inherits the asymmetric Kramers-prefactor structure. It has not been rigorously derived from the Aurell-Proesmans Wasserstein optimal-transport framework. This is flagged by Phase 0.25.

## F3.29 Dago 2024 reliability-operation-cost curves

Dago-Ciliberto-Bellon 2024 (T3_058) give measured erasure-cost curves in cyclic underdamped erasure as a function of asymmetry. These are the closest experimental comparator for B(r) in a physical (non-virtual) double well.

## F3.30 Calibration uncertainty budget

For a Bérut-style reconstruction using PSD + Boltzmann inversion, the dominant uncertainty contributions are: (i) PSD sensitivity factor ± 3 percent; (ii) Boltzmann-inversion statistical ± 0.02 k_B T per bin; (iii) AOD diffraction asymmetry ± 5-10 percent; (iv) laser-power drift over 50 min acquisition ± 3-5 percent. Total uncertainty on well-depth asymmetry ± 10-15 percent. This is the irreducible uncertainty floor on r for the Bérut published data.
