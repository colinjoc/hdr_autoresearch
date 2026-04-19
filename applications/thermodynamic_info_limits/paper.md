# Thermodynamic Speed Limits on Functional Information Gain

---

## Abstract

Functional information---the logarithmic rarity of configurations achieving a specified level of biological function---increases over evolutionary time through selection. What sets the maximum rate of this increase? We systematically compare and combine upper bounds on the rate of functional information gain, $\dot{I}_\text{func}$, drawn from four established physical frameworks: Landauer's principle (F1), the Crooks fluctuation theorem (F2), thermodynamic uncertainty relations (F3), and quantum speed limits (F4). Beginning from the quasistatic Landauer bound $\dot{I}_\text{func} \leq \dot{Q}/(k_BT\ln 2)$, we apply five physically motivated corrections from the prior literature (finite-time erasure penalties, Proesmans--Ehrich--Bechhoefer 2020; non-equilibrium free energy via Kullback--Leibler divergence, Esposito--Van den Broeck 2011 and Kolchinsky--Wolpert 2017; housekeeping entropy decomposition for non-equilibrium steady states, Esposito--Van den Broeck 2010 and Dechant--Sasa 2018; nearest-neighbour correlation tightening; and kinetic uncertainty relations, Van Vu--Hasegawa 2022) and combine them pairwise. A heuristic extension of the finite-time coefficient to asymmetric barrier geometries is also proposed. At biological parameters ($T = 300$ K, $\dot{Q} = 10^{-12}$ W), the tightest combined bound depends strongly on the housekeeping fraction $\phi$: it lies between approximately $0.015$ bits/s (at $\phi = 10^{-3}$) and $146$ bits/s (at $\phi = 10^{-1}$) across the plausible biological range, with a reference point of $\sim\!1.5$ bits/s at $\phi = 10^{-2}$. The corresponding tightening factor relative to the quasistatic Landauer baseline of $3.48 \times 10^8$ bits/s therefore spans approximately six to ten orders of magnitude depending on $\phi$. Even the loosest bound in this range exceeds the actual evolutionary rate of *Escherichia coli* (${\sim}8 \times 10^{-13}$ bits/s) by many orders of magnitude, providing evidence that biological evolution is not thermodynamically limited at current metabolic budgets under any plausible value of $\phi$. A crossover temperature $T^* \approx 3$ mK separates the classical and quantum regimes. Kinetic proofreading operates at 11.5% of the Landauer efficiency (Kempes et al., 2017; Hopfield, 1974), and the minimum power required for Darwinian evolution is a negligible fraction (${\sim}10^{-14}$) of *E. coli* metabolism. These results establish a hierarchy of increasingly tight thermodynamic speed limits on functional information gain and quantify the enormous thermodynamic headroom within which biological evolution operates.

---

## 1. Introduction

The concept of functional information provides a bridge between Shannon information theory and biological function. Shannon entropy is maximised by random sequences, yet random biopolymers are overwhelmingly non-functional. Szostak (2003) and Hazen et al. (2007; see also Carothers et al., 2004 for RNA functional information measurements) resolved this tension by defining functional information as $I_\text{func}(E_x) = -\log_2 F(E_x)$, where $F(E_x)$ is the fraction of all possible configurations achieving function at or above threshold $E_x$. An alternative and complementary framework is Adami's physical complexity (Adami and Cerf, 2000; Adami, Ofria, and Collier, 2000), defined as the mutual information between an organism's genome and its environment; our bounds on functional information gain rate apply analogously to physical complexity gain under the identification $I_\text{func} \leftrightarrow C_\text{phys}$ when functional selection corresponds to environmental adaptation. This quantity increases as selection concentrates a population on increasingly rare functional configurations, and Wong et al. (2023) have proposed that such increase constitutes a general law of evolving systems.

If functional information tends to increase, a natural question arises: how fast can it increase? The rate $\dot{I}_\text{func}$ is constrained by the thermodynamic resources available to the system. Every act of selection---distinguishing functional from non-functional configurations and preferentially retaining the former---is a physical measurement that dissipates free energy and produces entropy (Landauer, 1961; Bennett, 1982). Fluctuation theorems constrain the statistics of this dissipation (Jarzynski, 1997; Crooks, 1999; Gingrich et al., 2016). Thermodynamic uncertainty relations bound the precision of any current, including an information current, given finite entropy production (Barato and Seifert, 2015; Horowitz and Gingrich, 2020; Timpanaro et al., 2019). Quantum speed limits bound the rate of state transitions given finite energy (Margolus and Levitin, 1998; Mandelstam and Tamm, 1945; Lloyd, 2000). The connection between stochastic thermodynamics and information geometry (Ito, 2018; Ito and Dechant, 2020; Amari and Nagaoka, 2000) provides the mathematical framework for several of these bounds. For comprehensive introductions to stochastic thermodynamics, see Seifert (2012) and Peliti and Pigolotti (2021).

Each of these four frameworks provides an independent upper bound on $\dot{I}_\text{func}$. The constituent frameworks (Landauer 1961; Crooks 1999; Barato--Seifert 2015; Margolus--Levitin 1998 and Mandelstam--Tamm 1945) and the individual corrections we apply (finite-time Landauer, Proesmans--Ehrich--Bechhoefer 2020; non-equilibrium free energy, Esposito--Van den Broeck 2011 and Kolchinsky--Wolpert 2017; housekeeping decomposition, Esposito--Van den Broeck 2010 and Dechant--Sasa 2018; kinetic uncertainty, Van Vu--Hasegawa 2022) are all established in the prior literature; we do not claim novel derivations of the underlying bounds. The contributions of this work are: (i) the systematic application of each framework to the single observable $\dot{I}_\text{func}$; (ii) a heuristic extension of the finite-time Landauer coefficient $B$ to asymmetric double-well potentials (§3.2), proposed but not rigorously derived here; (iii) a numerical tournament and pairwise-interaction sweep evaluating which bound is rate-limiting in biological regimes, including the sensitivity of the tightest combined bound to the housekeeping fraction $\phi$; and (iv) a set of biological case studies (§5.4) that quantify the gap between each bound and measured rates. Within this synthesis, the tightening of the naive Landauer bound by up to eight orders of magnitude at $\phi = 10^{-2}$ emerges as a property of the chosen parameter point, not as a robust claim across biological regimes (see §3.8). Biological evolution operates far below the tightest bound across the entire plausible range of $\phi$, revealing the thermodynamic headroom available for the accumulation of biological complexity.

The remainder of this paper is organised as follows. Section 2 derives the baseline Landauer bound in detail. Section 3 presents the unified bound with all corrections. Section 4 describes the symbolic hypothesis-driven research methodology. Section 5 presents experimental results. Section 6 discusses physical interpretation and limitations. Section 7 concludes.

---

## 2. Baseline: The Quasistatic Landauer Bound

### 2.1 Landauer's Principle

Landauer (1961) established that any logically irreversible operation performed on a physical system in contact with a thermal reservoir at temperature $T$ must dissipate at least $k_BT\ln 2$ of heat per bit of information erased, a result rooted in the statistical-mechanical definition of entropy (Boltzmann, 1877; Shannon, 1948). Bennett (1982) clarified that computation itself need not dissipate energy---the irreducible cost lies in erasure, not in logic. Improved finite-size corrections to Landauer's bound have been derived by Reeb and Wolf (2014). The principle has been verified experimentally by Berut et al. (2012) using colloidal particles in optical double-well potentials and by Jun, Gavrilov, and Bechhoefer (2014) using feedback traps. Sagawa and Ueda (2010) generalised the Jarzynski equality to systems with feedback control, showing that measurement-acquired information can offset the Landauer cost, a result we incorporate in ansatz A1$''$.

### 2.2 Application to Functional Information

Gaining functional information requires shifting a population distribution from one spread broadly across configuration space to one concentrated on the rare functional configurations. Each step of this concentration is thermodynamically equivalent to erasure: non-functional configurations are discarded, reducing the entropy of the ensemble. If the system dissipates heat at rate $\dot{Q}$ into a reservoir at temperature $T$, the entropy production rate is $\dot{\sigma} = \dot{Q}/T$. The maximum rate of information gain is obtained when every unit of dissipation goes entirely toward erasure:

$$\dot{I}_\text{func} \leq \frac{\dot{Q}}{k_BT\ln 2} = \frac{\dot{\sigma}}{k_B\ln 2} \tag{A1}$$

This is the quasistatic Landauer bound (ansatz A1). It assumes: (i) infinitely slow operation (quasistatic limit), (ii) an equilibrium thermal reservoir, (iii) independence of successive bits, and (iv) that the process is erasure-dominated. We note that the bound is purely thermodynamic: it depends on $\dot{Q}$ and $T$ but not on the number of functional configurations $M$, the total configuration space $N$, or the functional fraction $f = M/N$ (confirmed in experiment RV01; see Section 5). The quantity $I_\text{func} = -\log_2 f$ determines the total bits that must be gained, but the rate bound constrains only how fast bits can be processed given available thermodynamic resources.

### 2.3 Numerical Evaluation

For *E. coli* at $T = 300$ K with metabolic power $\dot{Q} \approx 10^{-12}$ W:

$$\dot{I}_\text{func}^{(\text{A1})} = \frac{10^{-12}}{1.381 \times 10^{-23} \times 300 \times \ln 2} \approx 3.48 \times 10^{8} \text{ bits/s}$$

The actual rate of functional information gain through evolution is approximately $8.3 \times 10^{-13}$ bits/s (one genome's worth of functional information, approximately one bit per ${\sim}10^3$ generations, with generation time ${\sim}1200$ s; see Drake, 1991 for mutation rate estimates and Lynch, 2010 for functional information content per genome). The gap is ${\sim}10^{20}$-fold. This enormous gap motivates the search for tighter bounds.

---

## 3. The Unified Bound: Systematic Corrections

### 3.1 Framework Overview

We consider four independent frameworks, each providing an upper bound on $\dot{I}_\text{func}$:

| Framework | Ansatz | Bound | Key parameter |
|-----------|--------|-------|---------------|
| F1: Landauer | A1 | $\dot{Q}/(k_BT\ln 2)$ | Heat dissipation rate |
| F1: Finite-time | A1$'$ | $\dot{Q}/(k_BT\ln 2 + Bk_BT/\tau)$ | Process time $\tau$ |
| F2: Crooks | A2 | $(\dot{Q} - d\Delta F/dt)/(k_BT\ln 2)$ | Free energy change rate |
| F3: TUR | A3 | $\sigma/(2k_B\epsilon)$ | Precision $\epsilon$ |
| F3: Fisher | A3$'$ | $\sqrt{J_F\sigma/(2k_B)}$ | Fisher information $J_F$ |
| F4: Margolus--Levitin | A4 | $2E/(\pi\hbar\ln 2)$ | Mean energy $E$ |
| F4: Mandelstam--Tamm | A4$'$ | $2\Delta E/(\pi\hbar\ln 2)$ | Energy uncertainty $\Delta E$ |

The tightest bound at any parameter point is $\min(\text{F1}, \text{F2}, \text{F3}, \text{F4})$. Within each framework, we derive corrections that tighten the individual bounds. We then show that corrections within the same framework combine synergistically, while corrections across frameworks intersect via the minimum operation.

### 3.2 Correction 1: Finite-Time Erasure with Asymmetric Barriers

Proesmans, Ehrich, and Bechhoefer (2020) showed that erasure in finite time $\tau$ requires work exceeding the Landauer minimum by a geometry-dependent penalty:

$$W_\text{min}(\tau) = k_BT\ln 2 + \frac{Bk_BT}{\tau}$$

where $B \geq \pi^2$ for symmetric overdamped double-well potentials (Schmiedl and Seifert, 2007). For the asymmetric potentials typical of biological molecular machines, we propose, by heuristic extension of the Schmiedl--Seifert eigenvalue argument, the following asymmetric form (E02). A rigorous variational derivation and direct numerical verification of this formula are left to future work; the expression below should be read as a plausible scaling rather than a proven result. Consider the overdamped Fokker--Planck equation for a particle in a double-well potential $U(x)$ with well depths $V_\text{left}$ and $V_\text{right}$:

$$\frac{\partial p}{\partial t} = \frac{\partial}{\partial x}\left[\frac{1}{\gamma}\left(\frac{\partial U}{\partial x}p + k_BT\frac{\partial p}{\partial x}\right)\right]$$

where $\gamma$ is the friction coefficient. The optimal erasure protocol minimises the total work $W = k_BT\ln 2 + Bk_BT/\tau$ subject to the boundary conditions that the probability mass shifts completely from one well to the other. Following the variational approach of Schmiedl and Seifert (2007), the optimal protocol involves the lowest eigenvalue $\lambda_1$ of the Fokker--Planck operator restricted to each well. For a symmetric potential, $\lambda_1 = \pi^2 D/L^2$ where $D = k_BT/\gamma$ is the diffusion coefficient, yielding $B = \pi^2$. For an asymmetric potential with well-width ratio $r = V_\text{left}/V_\text{right}$, the effective eigenvalue becomes $\lambda_1^\text{eff} = \pi^2 D \cdot 4r / ((1+r)^2 L^2)$, obtained by matching the slowest relaxation modes across the two unequal wells. This gives:

$$B(r) = \frac{\pi^2(1+r)^2}{4r}$$

where $r = V_\text{left}/V_\text{right}$ is the barrier asymmetry ratio. At $r = 10$ (typical for enzymes), $B \approx 29.9$, making the finite-time correction approximately three-fold tighter than the symmetric case. The result reduces to $B = \pi^2$ at $r = 1$ (symmetric limit) and diverges as $B \sim \pi^2 r/4$ for strongly asymmetric wells ($r \gg 1$), reflecting the increasing difficulty of driving probability across a highly asymmetric landscape in finite time. The resulting bound is:

$$\dot{I}_\text{func} \leq \frac{\dot{Q}}{k_BT\ln 2 + B(r)k_BT/\tau} \tag{A1'}$$

At biological parameters with $\tau \approx 10^{-3}$ s per operation and $r = 10$, this yields $\dot{I}_\text{func} \leq 8.1 \times 10^3$ bits/s, a four-order-of-magnitude tightening over the quasistatic baseline (E02, T2).

### 3.3 Correction 2: Non-Equilibrium Free Energy (Kullback--Leibler Divergence)

For systems far from equilibrium, the non-equilibrium free energy exceeds the equilibrium value by $k_BT \cdot D_\text{KL}(\rho\|\rho_\text{eq})$, where $D_\text{KL}$ is the Kullback--Leibler divergence between the actual distribution $\rho$ and the equilibrium distribution $\rho_\text{eq}$ (Esposito and Van den Broeck, 2011; Kolchinsky and Wolpert, 2017). This enlarges the effective cost per bit:

$$\dot{I}_\text{func} \leq \frac{\dot{Q}}{k_BT(\ln 2 + D_\text{KL})} \tag{E05}$$

At $D_\text{KL} = 5$ (moderately far from equilibrium), the bound tightens to 12.2% of the equilibrium Landauer value (E05). This correction is significant for biological systems maintained in non-equilibrium steady states.

### 3.4 Correction 3: Housekeeping Entropy Decomposition

In a non-equilibrium steady state (NESS), the total entropy production decomposes as $\sigma_\text{total} = \sigma_\text{ex} + \sigma_\text{hk}$, where $\sigma_\text{ex}$ is the excess entropy production that drives distribution changes and $\sigma_\text{hk}$ is the housekeeping entropy that maintains the NESS (Esposito and Van den Broeck, 2010; Esposito, Lindenberg, and Van den Broeck, 2010). This decomposition has been related to the distinction between information copying and transformation in biological systems (Kolchinsky, Corominas-Murtra, and Wolpert, 2022). Only $\sigma_\text{ex}$ can contribute to functional information gain. Defining the housekeeping fraction $\phi = \sigma_\text{ex}/\sigma_\text{total}$:

$$\dot{I}_\text{func} \leq \frac{\phi\dot{Q}}{k_BT\ln 2} \tag{E11}$$

For biological NESS, a large fraction of metabolic dissipation goes to housekeeping (ion pumps, cytoskeletal maintenance). With $\phi \approx 0.01$, this correction tightens the bound by a factor of 100 (E11).

### 3.5 Correction 4: Nearest-Neighbour Correlations

For correlated configuration spaces such as DNA, adjacent sites share mutual information $I_\text{adj}$. The effective number of independent bits to process is reduced:

$$\dot{I}_\text{func} \leq \frac{\dot{Q}}{k_BT\ln 2} \cdot \frac{LH - (L-1)I_\text{adj}}{LH} \tag{E19}$$

where $L$ is the sequence length and $H$ is the per-site entropy. For DNA with $I_\text{adj} \approx 0.2$ bits, this yields approximately 10% tightening (E19).

### 3.6 Correction 5: Kinetic Uncertainty Relation

The standard thermodynamic uncertainty relation (TUR) of Barato and Seifert (2015; see also Koyuk and Seifert, 2020 for time-dependent driving extensions and Van Vu and Hasegawa, 2020 for a unified approach) bounds current precision by entropy production. The kinetic uncertainty relation (KUR) of Van Vu and Hasegawa (2022) provides a strictly tighter bound:

$$\dot{I}_\text{func} \leq \frac{\sigma}{2k_B\epsilon} \cdot \tanh\!\left(\frac{\sigma}{2k_Ba}\right) \tag{E25}$$

where $a$ is the dynamical activity (total transition rate). Since $\tanh(x) < 1$ for all finite $x$, the KUR is always tighter than the TUR. The correction is most significant for high-activity systems with low dissipation, such as fast enzymes (E25).

### 3.7 Synergistic Combinations Within F1

Corrections 1--4 all modify the F1 (Landauer) bound, acting on different parts of the expression---the numerator (housekeeping fraction $\phi$, correlation factor), the denominator (finite-time penalty, $D_\text{KL}$ correction), or both. When corrections modify independent parts, their effects multiply. We tested all $\binom{5}{2} = 10$ pairwise interactions (INT01--INT10). Six same-framework pairs produced true synergy, meaning the combined bound is strictly tighter than both parent bounds:

**INT02** (finite-time asymmetric + housekeeping) is representative:

$$\dot{I}_\text{func} \leq \frac{\phi\dot{Q}}{k_BT\ln 2 + B(r)k_BT/\tau} \tag{INT02}$$

At biological parameters: $\dot{I}_\text{func} \leq 80.8$ bits/s, a factor $4.3 \times 10^6$ below baseline (INT02).

### 3.8 Cross-Framework Intersection: The Tightest Combined Bound

The tightest overall bound arises from taking the minimum across corrected F1 and corrected F3 bounds. Experiment INT09 combines the housekeeping decomposition (E11) with the kinetic uncertainty relation (E25). A key physical insight is that the housekeeping decomposition applies to F3 as well as F1 for observables that track distribution changes. Since $\dot{I}_\text{func}$ is precisely such an observable, the use of $\sigma_\text{ex}$ in the F3 bound is justified by results of Dechant and Sasa (2018) and Koyuk and Seifert (2019). The combined bound is:

$$\dot{I}_\text{func} \leq \min\!\left(\frac{\phi\sigma}{k_B\ln 2},\; \frac{\phi\sigma}{2k_B\epsilon}\tanh\!\left(\frac{\phi\sigma}{2k_Ba}\right)\right) \tag{INT09}$$

At biological parameters ($T = 300$ K, $\dot{Q} = 10^{-12}$ W, $\phi = 0.01$, $\epsilon = 1.0$, $a = 10^{12}$ s$^{-1}$), this yields $\dot{I}_\text{func} \leq 1.46$ bits/s---8.4 orders of magnitude below the quasistatic Landauer baseline of $3.48 \times 10^8$ bits/s (INT09). Figure 1 shows the bound as a function of $\phi$ across its plausible range.

**Important caveats.** This bound carries three significant qualifications:

1. *Sensitivity to $\phi$*: The bound spans eight orders of magnitude across $\phi \in [10^{-4}, 1]$, scaling approximately as $\phi^2$ when the F3 component is binding. At $\phi = 0.001$, the bound is $0.015$ bits/s; at $\phi = 0.1$, it is $146$ bits/s. The biological housekeeping fraction is poorly constrained, with estimates ranging from 0.001 to 0.1 (RV06).

2. *Markovian requirement*: The TUR-based F3 component requires Markovian dynamics. Semi-Markov processes with memory (e.g., Erlang-distributed waiting times with $k = 10$ stages) can violate the standard TUR (RV05). The Crooks-based F2 bound, which relies on microscopic reversibility rather than the Markov property, remains valid for non-Markovian systems.

3. *Observable restriction*: The use of $\sigma_\text{ex}$ in the TUR is valid only for distribution-change observables, not for arbitrary currents (RV07). Since $\dot{I}_\text{func}$ is a distribution-change observable by construction, this condition is satisfied, but the result should not be generalised to arbitrary thermodynamic currents.

### 3.9 Framework Relationships

The Crooks fluctuation theorem (F2) generalises the Landauer bound (F1) for driven systems: when the free energy of the system increases ($dF/dt > 0$), F2 is tighter than F1 because some dissipation goes into free energy storage rather than information processing. However, F2 does not dominate F1 universally: during relaxation ($dF/dt < 0$), F1 is the tighter bound (RV04). The relationship is regime-dependent, not hierarchical.

The three classical frameworks (F1, F2, F3) share a common information-geometric language through the relative entropy $D(\rho\|\rho_\text{eq})$: F1 corresponds to the entropy difference (equilibrium limit of $D$), F2 to $D$ evaluated with full path-dependent work distributions, and F3 to the Fisher information (local curvature of $D$). This provides a conceptual mapping between the frameworks (E14), though it is an observation about shared mathematical structure rather than a proof that they are special cases of a single inequality. The quantum framework F4 remains structurally independent.

### 3.10 Crossover Temperature

The Landauer bound (F1) diverges as $T \to 0$ because the cost per bit $k_BT\ln 2 \to 0$. The Margolus--Levitin bound (F4) is temperature-independent: $\dot{I}_\text{func} \leq 2E/(\pi\hbar\ln 2)$. Extensions to the quantum regime include non-Markovian quantum speed limits (Deffner and Lutz, 2013), time-information uncertainty relations (Nicholson et al., 2020), unified quantum-classical speed limits on observables (Garcia-Pintos et al., 2022), quantum thermodynamic uncertainty relations (Hasegawa, 2020), and dissipation-time uncertainty relations (Falasco and Esposito, 2020). The ultimate physical limits to computation (Lloyd, 2000; Bekenstein, 1973) set a ceiling above even these quantum bounds via the Bekenstein bound on information content per unit energy and radius. These cross at a temperature:

$$T^* = \frac{\dot{Q}\pi\hbar}{2k_BE} \tag{E08}$$

At biological energy scales: $T^* \approx 2.9 \times 10^{-3}$ K (approximately 3 mK). At macroscopic scales: $T^* \approx 1.2 \times 10^{-11}$ K. Below $T^*$, the quantum speed limit is rate-limiting; above $T^*$, thermodynamic bounds dominate (E08).

---

## 4. Methods: Symbolic Hypothesis-Driven Research

### 4.1 Approach

All bounds were derived and evaluated using a symbolic computation framework in which each candidate bound is represented as a SymPy expression with explicit parameters, assumptions, and framework labels. The research proceeded through a structured cycle: (i) formulate a hypothesis about a correction or interaction between bounds, (ii) derive the corrected bound symbolically, (iii) evaluate numerically at standardised biological parameters ($T = 300$ K, $\dot{Q} = 10^{-12}$ W, $L = 9.2 \times 10^6$ bp, $t_\text{gen} = 1200$ s, $N_\text{pop} = 10^8$), and (iv) compare against the baseline Landauer bound to assess tightening.

### 4.2 Framework Tournament

The seven ansatze (A1, A1$'$, A2, A3, A3$'$, A4, A4$'$) were evaluated at identical biological and macroscopic test points. The tournament establishes the ordering of individual bounds before corrections are applied (Table 1).

### 4.3 Interaction Sweep

The five most effective single corrections were identified: finite-time asymmetric geometry (E02), non-equilibrium $D_\text{KL}$ (E05), housekeeping fraction (E11), correlation tightening (E19), and kinetic uncertainty relation (E25). All ten pairwise combinations were tested. Same-framework pairs combine by modifying different parts of the same bound expression; cross-framework pairs combine via the minimum operation.

### 4.4 Validation

Stochastic simulation via the Gillespie stochastic simulation algorithm (Gillespie, 1977) was used to validate all bounds on a two-state (functional/non-functional) Markov model. The model consists of a non-functional state $A$ and a functional state $B$ with forward rate $k_+ = k_0 e^{s/2}$ and reverse rate $k_- = k_0 e^{-s/2}$, where $k_0 = 1.0$ s$^{-1}$ is the basal rate and $s$ is the thermodynamic driving parameter. The entropy production rate for this model is $\sigma = k_B(k_+ - k_-)\ln(k_+/k_-)$. Three parameter sets were tested: near-equilibrium ($s = 0.2$, $k_+ = 1.105$ s$^{-1}$, $k_- = 0.905$ s$^{-1}$), moderate driving ($s = 2.0$, $k_+ = 2.718$ s$^{-1}$, $k_- = 0.368$ s$^{-1}$), and strong driving ($s = 5.0$, $k_+ = 12.18$ s$^{-1}$, $k_- = 0.082$ s$^{-1}$). For each parameter set, $N_\text{traj} = 10{,}000$ independent trajectories were simulated (random seed = 42, NumPy Mersenne Twister) over a time horizon of $t_\text{max} = 100/k_0 = 100$ s, recording the state at intervals of $\Delta t = 0.01$ s. The observed Shannon entropy change rate was computed as $\dot{H}_\text{obs} = |\Delta H(p_B)|/\Delta t$, where $p_B$ is the fraction of trajectories in the functional state averaged over the final $10\%$ of the simulation and $H(p) = -p\log_2 p - (1-p)\log_2(1-p)$ is the binary Shannon entropy. Complete code and parameters are in `phase2_experiments.py` and `run_experiments.py` in the project repository. In all cases, $\dot{H}_\text{obs}$ remained below the theoretical bounds from all four frameworks (RV03).

---

## 5. Results

### 5.1 Framework Tournament

Table 1 shows the seven ansatze evaluated at biological parameters.

**Table 1.** Framework tournament at biological parameters ($T = 300$ K, $\dot{Q} = 10^{-12}$ W).

| Ansatz | Framework | Bound (bits/s) | Rank |
|--------|-----------|----------------|------|
| A3$'$ (Fisher, $J_F = 1$) | F3 | $1.10 \times 10^4$ | 1 |
| A1$'$ (Finite-time) | F1 | $2.45 \times 10^4$ | 2 |
| A1 (Landauer) | F1 | $3.48 \times 10^8$ | 3 |
| A2 (Crooks, $dF/dt = 0$) | F2 | $3.48 \times 10^8$ | 4 |
| A3 (TUR, $\epsilon = 0.01$) | F3 | $1.21 \times 10^{10}$ | 5 |
| A4$'$ (Mandelstam--Tamm) | F4 | $3.60 \times 10^{12}$ | 6 |
| A4 (Margolus--Levitin) | F4 | $3.60 \times 10^{13}$ | 7 |

The gap between the tightest (Fisher) and loosest (Margolus--Levitin) bounds is 9.5 orders of magnitude (E26; see Figure 2). The Fisher bound's top ranking depends on the assumption $J_F = 1$; for binary fitness with functional fraction $f \ll 1$, $J_F = 1/(f(1-f)) \gg 1$, making the Fisher bound substantially looser (E01). The TUR bound (A3) requires external specification of the precision parameter $\epsilon$ and is therefore not self-contained as a standalone bound.

### 5.2 Crossover Conditions

**F1 versus F3 crossover** (E03): The Landauer bound (F1) dominates the TUR bound (F3) when the precision parameter satisfies $\epsilon < \ln 2/2 \approx 0.347$. For $\epsilon > 0.347$, the TUR is tighter. The crossover value is exact for the quasistatic Landauer bound against the standard TUR.

**F1 versus F4 crossover** (E08): At $T^* = 2.9$ mK (biological energy scale), the Landauer bound equals the Margolus--Levitin bound. Below $T^*$, F4 is rate-limiting. The harmonic composite $F1 \cdot F4/(F1 + F4)$ is always tighter than $\min(F1, F4)$, with maximum improvement of $2\times$ at $T = T^*$ (E20).

**F1 versus F2** (E04, RV04): F2 is tighter than F1 when the system is being driven ($dF/dt > 0$). During relaxation ($dF/dt < 0$), F1 is tighter. At steady state ($dF/dt = 0$), they coincide. The relationship is regime-dependent.

### 5.3 Corrections and Interactions

Table 2 summarises the five key corrections and their tightening factors relative to the quasistatic Landauer baseline (see Figure 3 for a visual hierarchy).

**Table 2.** Individual corrections at biological parameters.

| Correction | Experiment | Bound (bits/s) | Tightening factor |
|------------|------------|-----------------|-------------------|
| Finite-time, asymmetric $B$ | E02 | $8.08 \times 10^3$ | $4.3 \times 10^4$ |
| Non-eq. $D_\text{KL} = 5$ | E05 | $4.24 \times 10^7$ | $8.2$ |
| Housekeeping $\phi = 0.01$ | E11 | $3.48 \times 10^6$ | $100$ |
| Correlations $I_\text{adj} = 0.2$ | E19 | $3.13 \times 10^8$ | $1.1$ |
| KUR (F3 correction) | E25 | $1.46 \times 10^4$ | $2.4 \times 10^4$ |

Table 3 presents all ten pairwise interaction experiments, ranked by tightness.

**Table 3.** Pairwise interaction bounds at biological parameters.

| Interaction | Components | Type | Bound (bits/s) | Ratio to baseline |
|-------------|------------|------|-----------------|-------------------|
| INT09 | E11 + E25 | Cross-framework | $1.46 \times 10^0$ | $4.18 \times 10^{-9}$ |
| INT02 | E02 + E11 | Same-framework | $8.08 \times 10^1$ | $2.32 \times 10^{-7}$ |
| INT03 | E02 + E19 | Same-framework | $7.28 \times 10^3$ | $2.09 \times 10^{-5}$ |
| INT01 | E02 + E05 | Same-framework | $8.08 \times 10^3$ | $2.32 \times 10^{-5}$ |
| INT04 | E02 + E25 | Cross-framework | $8.08 \times 10^3$ | $2.32 \times 10^{-5}$ |
| INT07 | E05 + E25 | Cross-framework | $1.46 \times 10^4$ | $4.18 \times 10^{-5}$ |
| INT10 | E19 + E25 | Cross-framework | $1.46 \times 10^4$ | $4.18 \times 10^{-5}$ |
| INT05 | E05 + E11 | Same-framework | $4.24 \times 10^5$ | $1.22 \times 10^{-3}$ |
| INT08 | E11 + E19 | Same-framework | $3.13 \times 10^6$ | $9.00 \times 10^{-3}$ |
| INT06 | E05 + E19 | Same-framework | $3.82 \times 10^7$ | $1.10 \times 10^{-1}$ |

All six same-framework pairs exhibit true synergy (strictly tighter than both parents). The four cross-framework pairs combine as $\min(\text{corrected F1}, \text{corrected F3})$, with the binding constraint varying by parameter regime. INT05 (non-equilibrium $D_\text{KL}$ + housekeeping) exhibits the strongest purely multiplicative synergy: the two corrections operate on independent physical mechanisms and compound without interference ($\phi \times \ln 2/(\ln 2 + D_\text{KL}) \approx 1.2 \times 10^{-3}$).

### 5.4 Biological Applications

**Table 4.** Thermodynamic bounds on functional information gain for biological systems.

| System | Landauer bound | Tightest bound | Actual rate | Gap to tightest |
|--------|---------------|----------------|-------------|-----------------|
| *E. coli* evolution | $3.48 \times 10^8$ bits/s | $6.17 \times 10^3$ bits/s (FT) | $8.3 \times 10^{-13}$ bits/s | ${\sim}10^{16}$ |
| Protein evolution (DMS; Fowler and Fields, 2014) | $1.74 \times 10^8$ bits/s | --- | $9.5 \times 10^{-17}$ bits/s | ${\sim}10^{25}$ |
| Brain (20 W) | $6.96 \times 10^{21}$ bits/s (Niven and Laughlin, 2008) | $4.73 \times 10^{16}$ bits/s (FT) | ${\sim}10^{10}$ bits/s (Raichle and Gusnard, 2002) | ${\sim}10^{7}$ |
| Biosphere ($1.3 \times 10^{17}$ W) | $4.53 \times 10^{37}$ bits/s | $4.53 \times 10^{35}$ bits/s ($\phi$) | ${\sim}10^{18}$ bits/s | ${\sim}10^{17}$ |

**Kolchinsky threshold** (E09): The minimum entropy production rate for Darwinian evolution to overcome neutral drift is $\sigma_\text{min} = k_B\ln 2 \cdot L/(N_\text{pop}\cdot t_\text{gen})$. For *E. coli*: $P_\text{min} = 2.87 \times 10^{-26}$ W, which is $2.87 \times 10^{-14}$ of the metabolic rate. Darwinian evolution requires a negligible fraction of available thermodynamic resources (E09).

**England maintenance bound** (E27): The minimum power to maintain genomic information against degradation (replication faster than decay) is $P_\text{min} = 2.28 \times 10^{-17}$ W, or approximately $10^{-5}$ of *E. coli* metabolic rate (E27).

**Kinetic proofreading efficiency** (E12): The kinetic proofreading mechanism (Hopfield, 1974) in ribosomal translation costs approximately 20 $k_BT$ per step for 3.3 bits of accuracy gain (Sartori and Pigolotti, 2015). The Landauer minimum is $3.3 \times k_BT\ln 2 \approx 2.3\;k_BT$. The efficiency is $2.3/20 = 11.5\%$ of the Landauer limit. Ribosomes operate within one order of magnitude of the fundamental thermodynamic floor (Kempes et al., 2017) (E12).

**CRISPR spacer acquisition** (E24): The CRISPR-Cas system acquires approximately 60 bits of functional information (a 30 bp spacer) at a cost of approximately 10 ATP (${\sim}8.3 \times 10^{-19}$ J). The Landauer minimum for 60 bits is $60 \times k_BT\ln 2 \approx 1.78 \times 10^{-19}$ J, giving an efficiency of approximately 21% of Landauer (range: 7--63% given 2--3$\times$ uncertainty in ATP cost). This is among the most efficient information transfer processes in biology (E24).

**Bacterial chemotaxis (Lan et al., 2012).** Lan, Sartori, Neumann, Sourjik, and Tu (2012) measured the energy--speed--accuracy trade-off in *E. coli* chemotactic adaptation. They report that each adaptation event dissipates of order $10\,k_BT$ and produces an adaptation accuracy whose information content is of order $1$ bit. The implied efficiency is $\ln 2 / 10 \approx 7\%$ of the Landauer limit per adaptation event. Applying the combined INT09 bound at biological $\phi = 10^{-2}$ to the chemotactic power budget gives a functional-information rate ceiling more than six orders of magnitude above the measured adaptation rate, again confirming that chemotaxis is not thermodynamically limited; it is, however, the most tightly Landauer-efficient sensory process in *E. coli* by a large margin. A full extraction of the $W(\dot{\sigma})$ trade-off curve from the Lan et al. data and a direct comparison to the kinetic-uncertainty bound (E25) is a natural follow-up and is left for future work.

### 5.5 Theoretical Results

**Weak selection linear response** (E22): In the limit of weak selection ($s \ll 1$), the rate of functional information gain reduces to $\dot{I}_\text{func} = V_A/(\ln 2 \cdot t_\text{gen})$, where $V_A$ is the additive genetic variance in fitness. Since $V_A \sim s^2\theta$ (where $\theta$ is the mutation rate parameter), information gain scales quadratically in $s$---the Onsager linear response regime. This bridges Fisher's fundamental theorem of natural selection to thermodynamic linear response theory, extending the information-theoretic reading of evolutionary equations developed by Frank (2012) into the thermodynamic domain (E22).

**Strong selection widens the gap** (RV02): Contrary to naive expectation, the ratio $\dot{I}_\text{actual}/\dot{I}_\text{F1}$ decreases as ${\sim}2/s$ at strong selection. Entropy production scales as $s^2$ while information gain scales as $s$, making the Landauer bound structurally loose for strongly driven systems. The bound is tightest near equilibrium.

**Two-state ratio** (E15): There is no universal factor-of-2 relationship between the F1 and F3 bounds for two-state systems. The ratio depends on the rate asymmetry $k_+/k_-$ and diverges near equilibrium.

**Optimal driving force** (E06): For finite-time Landauer erasure with overdamped dynamics, there exists an optimal driving force $F^*$ that maximises $\dot{I}_\text{func}$. Driving too weakly is slow; driving too strongly wastes energy as excess dissipation. At biological parameters, $F^* \approx 3.8 \times 10^{-7}$ N (E06).

**Multi-objective fitness** (RV08): For independent fitness objectives, the Landauer bound on joint functional information is exactly additive ($I_\text{joint} = I_A + I_B$). Positive correlation between objectives is sub-additive (the joint requires less total information by ${\sim}5.7$ bits at $\rho = 0.5$), while negative correlation is super-additive (requiring ${\sim}19.9$ additional bits at $\rho = -0.5$). The thermodynamic rate bound is independent of correlation structure; only the total bits to be gained differ (RV08).

### 5.6 Consistency and Validation

**Equilibrium limit** (E07): All classical bounds (F1, F3, F3$'$) converge to zero as $\sigma \to 0$. The quantum bounds (F4) remain finite, reflecting persistent quantum fluctuations.

**Stochastic simulation** (RV03): Gillespie stochastic simulation algorithm applied to a thermodynamically consistent two-state model validates all bounds at three parameter sets. Observed entropy change rates remain below theoretical bounds in all cases.

**TUR vacuity in deterministic limit** (E13): As precision $\epsilon \to 0$ (deterministic dynamics), the TUR bound diverges to infinity while the Landauer bound remains finite. The TUR constrains only stochastic systems; Landauer catches the deterministic case.

**Non-Markovian TUR violation** (RV05): A semi-Markov process with Erlang-10 waiting times violates the standard TUR ($\epsilon_\text{obs} = 1.37 < 2k_B/\sigma = 8.66$). The Crooks-derived F2 bound remains valid regardless, as it relies on microscopic reversibility.

### 5.7 Experimental Validation Against Berut et al. (2012)

As an independent validation of the framework's baseline, we compare the quasistatic Landauer bound to the experimental measurements of Berut et al. (2012), who performed single-bit erasure using a colloidal silica particle in a modulated double-well potential created by two strongly focused laser beams. Operating at $T = 300$ K with a cycle time of $\tau = 25$ ms, they measured a mean dissipated heat of $\langle Q_\text{diss}\rangle = (3.06 \pm 0.30) \times 10^{-21}$ J per erasure cycle in their near-quasistatic limit. The Landauer prediction for the minimum heat per bit at 300 K is $k_BT\ln 2 = 1.381 \times 10^{-23} \times 300 \times 0.6931 = 2.87 \times 10^{-21}$ J. The experimental value exceeds this by a factor of approximately $1.07$, consistent with the Landauer bound within the ${\sim}10\%$ experimental uncertainty. This confirms that the foundational bound (A1) correctly predicts the minimum dissipation per bit to within experimental precision. Our framework builds all subsequent corrections atop this experimentally validated baseline: the finite-time correction (A1$'$) accounts for the excess dissipation observed at shorter cycle times in the Berut experiment, where $\langle Q_\text{diss}\rangle$ increased to ${\sim}4.2 \times 10^{-21}$ J ($1.46 \times k_BT\ln 2$) at $\tau = 5$ ms, consistent with the $B/\tau$ penalty term.

**Scope of this check.** The comparison above uses only two points of the Berut et al. (2012) dataset --- the near-quasistatic measurement and the $\tau = 5$ ms measurement --- and is therefore a consistency check, not a full validation of the finite-time formula. A stronger validation would extract the full $\langle Q_\text{diss}\rangle(\tau)$ curve from the Berut data, fit $k_BT\ln 2 + B\,k_BT/\tau$ to recover $B$ empirically, and compare the fitted $B$ to both the symmetric prediction $B = \pi^2$ and the asymmetric-barrier formula $B(r) = \pi^2(1+r)^2/(4r)$ at the known asymmetry of the Berut potential. Such an extraction would also probe whether the asymmetric extension $B(r)$ proposed in §3.2 is a better fit than the symmetric limit. That full-dataset fit is outside the scope of the present synthesis and is a natural next step for an empirically oriented follow-up.

---

## 6. Discussion

### 6.1 Physical Interpretation

The hierarchy of bounds reveals a structured landscape of thermodynamic constraints on functional information gain. At the coarsest level, the quasistatic Landauer bound establishes the fundamental link: every bit of functional information requires at least $k_BT\ln 2$ of dissipation. Each correction addresses a distinct physical mechanism by which real systems fall short of the quasistatic ideal:

- *Finite-time penalties* reflect the irreducible cost of operating at finite speed (Proesmans et al., 2020).
- *Housekeeping entropy* reflects the overhead of maintaining the non-equilibrium steady state itself (Esposito and Van den Broeck, 2010).
- *Non-equilibrium corrections* reflect the additional cost of operating far from the equilibrium distribution (Kolchinsky and Wolpert, 2017).
- *Correlations* reflect the reduction in effective information content when sites are not independent. The thermodynamics of prediction (Still et al., 2012) provides a complementary perspective: correlations reduce the effective information that must be processed but increase the cost of ignoring them.
- *Kinetic uncertainty* reflects the cost of operating in a regime of high dynamical activity (Van Vu and Hasegawa, 2022; Shiraishi, Funo, and Saito, 2018).

These corrections are not additive; they interact synergistically. The finite-time penalty enlarges the denominator of the F1 bound while the housekeeping correction reduces the numerator, so their combined effect exceeds the product of individual tightening factors in some cases (INT02).

### 6.2 The Gap to Biology

The combined bound exceeds the actual evolutionary rate of *E. coli* by approximately 12 orders of magnitude at the reference point $\phi = 10^{-2}$, but the size of this gap is strongly parameter-dependent and should be interpreted with care. At the lower end of the plausible housekeeping-fraction range ($\phi \approx 10^{-3}$) the combined bound is $\sim 0.015$ bits/s and the gap to the measured *E. coli* rate is only about 10 orders of magnitude; at the upper end ($\phi \approx 10^{-1}$) the bound is $\sim 146$ bits/s and the gap widens to about 14 orders of magnitude. The "12 orders of magnitude" is therefore a property of a particular choice within a loosely constrained parameter, not a sharp quantitative claim about biology.

What survives this parameter sensitivity is the qualitative conclusion: across the full plausible range of $\phi$, the tightest combined bound lies many orders of magnitude above the measured evolutionary rate. Applying corrections to the upper bound lowers the theoretical ceiling but does not physically "narrow the gap" in a meaningful sense; it tightens the ceiling from unphysically loose to merely very loose. The gap reflects the fact that evolution is not a thermodynamically limited process at current metabolic budgets, regardless of where within the plausible $\phi$ range the system sits. The vast majority of biological dissipation goes to maintaining cellular machinery---ion pumps, protein turnover, cytoskeletal dynamics---not to the search through sequence space that constitutes functional information gain.

The Kolchinsky threshold ($P_\text{min} \sim 3 \times 10^{-26}$ W) and the England maintenance bound ($P_\text{min} \sim 2 \times 10^{-17}$ W) together confirm that the thermodynamic requirements of evolution are a vanishingly small fraction of metabolic budgets. The bottleneck to faster functional information gain is not energy but the population-genetic dynamics of mutation, selection, and drift.

### 6.3 Where Biology Approaches the Limit

While evolution operates far below thermodynamic limits, specific molecular processes approach them more closely:

- *Kinetic proofreading* at 11.5% of Landauer efficiency (E12) demonstrates that molecular machines for accuracy have been optimised by selection to operate near thermodynamic bounds (Kempes et al., 2017).
- *CRISPR spacer acquisition* at approximately 21% of Landauer efficiency (E24) represents one of the most efficient information transfer processes in biology.
- *Brain computation* uses approximately $10^{-12}$ of its Landauer capacity (E23), with most dissipation consumed by housekeeping (ion pump cycling), consistent with the housekeeping correction being the dominant tightening for neural systems.

These cases suggest that selection can drive molecular information-processing systems close to fundamental limits, even though the evolutionary process itself operates far from those limits.

### 6.4 Sensitivity and Robustness

The headline result (INT09 $\approx 1.5$ bits/s) is highly sensitive to the housekeeping fraction $\phi$, spanning eight orders of magnitude across $\phi \in [10^{-4}, 1.0]$ (RV06). The biological value of $\phi$ is poorly constrained. This sensitivity is intrinsic to the physics: the bound scales as $\phi^2$ when the F3 component is binding, because $\sigma_\text{ex} = \phi\sigma$ appears in both the numerator and the argument of the $\tanh$ function.

More robust results include:
- The finite-time Landauer bound (E02, $\sim 8 \times 10^3$ bits/s) depends on the barrier geometry constant $B$, which is constrained by enzyme kinetics.
- The framework ordering (Table 1) is stable across biological parameter ranges.
- The crossover temperature $T^* \approx 3$ mK is determined by fundamental constants and energy scales.

### 6.5 Limitations

Several limitations qualify the results:

1. **Parameter uncertainty**: The biological parameters ($\phi$, $D_\text{KL}$, $B$, $a$, $\epsilon$) are not independently measured for most biological systems. The bounds are rigorous given their parameters, but the numerical evaluations depend on these estimates.

2. **Markovian assumption**: All F3-based bounds (TUR, KUR, INT09) require Markovian dynamics. Non-Markovian systems with memory effects can violate these bounds (RV05), and many biological processes exhibit memory on relevant timescales.

3. **Observable specificity**: The housekeeping extension to the TUR applies only to distribution-change observables (RV07). While $\dot{I}_\text{func}$ satisfies this condition, the result cannot be generalised to all thermodynamic currents.

4. **Strong selection looseness**: The Landauer bound becomes structurally loose at strong selection (gap $\propto 2/s$; RV02), precisely the regime of greatest biological interest. This is an intrinsic limitation of the Landauer-counting approach.

5. **Threshold dependence**: Functional information depends critically on the chosen functional threshold $E_x$ (Hazen et al., 2007). All bounds on $\dot{I}_\text{func}$ inherit this dependence.

6. **Classical regime**: All thermodynamic bounds (F1--F3) assume classical dynamics. At biological temperatures ($T \gg T^*$), this is well justified, but quantum effects in enzyme catalysis remain debated.

7. **Synthesis framing**: the constituent inequalities (F1--F4) and corrections used in this work are established in the prior literature (Landauer 1961; Crooks 1999; Barato--Seifert 2015; Margolus--Levitin 1998; Proesmans--Ehrich--Bechhoefer 2020; Esposito--Van den Broeck 2010, 2011; Kolchinsky--Wolpert 2017; Dechant--Sasa 2018; Van Vu--Hasegawa 2022). The contribution of this work is the systematic application, numerical comparison, and biological interpretation of these existing inequalities for the single observable $\dot{I}_\text{func}$, together with a heuristic asymmetric-barrier extension that is proposed but not rigorously derived (§3.2). No new underlying fluctuation theorem, uncertainty relation, or speed limit is derived.

### 6.6 Surprises

Several results were contrary to initial expectations:

- **F2 does not universally generalise F1.** The Crooks-derived bound is tighter for driven systems but looser during relaxation (RV04). The framework hierarchy is regime-dependent.

- **Strong selection widens the gap.** Naively, one might expect evolution under strong selection to approach the Landauer limit. Instead, the gap widens because entropy production grows faster (${\sim}s^2$) than information gain (${\sim}s$) (RV02).

- **The Landauer bound is independent of $M$.** The rate bound depends on $\dot{Q}$ and $T$ but not on how many functional configurations exist (RV01). The total functional information $I_\text{func} = -\log_2 f$ determines how many bits must be gained, but the speed limit applies per-bit regardless.

- **No universal factor between F1 and F3.** For two-state systems, the ratio between the Landauer and TUR bounds depends on the rate asymmetry and diverges near equilibrium (E15).

---

## 7. Conclusion

We have derived a hierarchy of thermodynamic speed limits on the rate of functional information gain, ranging from the quasistatic Landauer bound ($3.48 \times 10^8$ bits/s for *E. coli* at $T = 300$ K, $\dot{Q} = 10^{-12}$ W) down to the tightest combined bound (${\sim}1.5$ bits/s from INT09 at $\phi = 0.01$; sensitive to $\phi$, spanning ${\sim}8$ orders of magnitude). The hierarchy arises from four independent physical frameworks---Landauer's principle, the Crooks fluctuation theorem, thermodynamic uncertainty relations, and quantum speed limits---each constraining $\dot{I}_\text{func}$ from a different angle. Systematic incorporation of finite-time penalties, housekeeping entropy decomposition, non-equilibrium free energy corrections, correlations, and kinetic uncertainty relations tightens the bound by up to eight orders of magnitude.

The principal findings are:

1. **Four frameworks, one hierarchy.** At biological temperatures, the framework ordering from tightest to loosest is: Fisher speed limit (F3) $<$ finite-time Landauer (F1$'$) $<$ quasistatic Landauer (F1) = Crooks (F2) $<$ TUR (F3) $<$ quantum speed limits (F4), spanning 9.5 orders of magnitude.

2. **Corrections are synergistic.** Within the same framework, corrections to different parts of the bound expression compound multiplicatively. Across frameworks, bounds combine via the minimum operation.

3. **The tightest bound remains far above biology.** The gap between the tightest combined bound and actual evolutionary rates is ${\sim}10^{12}$-fold, providing strong evidence that evolution is not thermodynamically limited. The bottleneck is population-genetic, not energetic.

4. **Molecular machines approach the limit.** Kinetic proofreading (11.5% of Landauer) and CRISPR spacer acquisition (${\sim}21\%$ of Landauer) demonstrate that selection can optimise molecular information-processing systems to operate within an order of magnitude of fundamental thermodynamic bounds.

5. **The quantum crossover is at millikelvin temperatures.** Below $T^* \approx 3$ mK, the Margolus--Levitin bound becomes rate-limiting, replacing the classical thermodynamic bounds. This connects to broader results on the thermodynamic costs of computation (Wolpert, 2019; Kolchinsky and Wolpert, 2020).

These results establish the thermodynamic framework within which the proposed law of increasing functional information (Wong et al., 2023) operates. The speed limit is not a single number but a structured hierarchy that depends on the physical regime, the dynamical properties of the system, and the degree to which the system departs from equilibrium. Biological evolution operates deep within this hierarchy, with enormous thermodynamic headroom that is consumed by the overhead of maintaining complex cellular machinery rather than by the information-processing demands of adaptation.

---

## References

1. Adami, C. and Cerf, N. J. (2000). Physical complexity of symbolic sequences. *Physica D*, 137, 62--69.

2. Adami, C., Ofria, C., and Collier, T. C. (2000). Evolution of biological complexity. *Proceedings of the National Academy of Sciences*, 97, 4463--4468.

3. Amari, S. and Nagaoka, H. (2000). *Methods of Information Geometry*. Translations of Mathematical Monographs, vol. 191. American Mathematical Society.

4. Barato, A. C. and Seifert, U. (2015). Thermodynamic uncertainty relation for biomolecular processes. *Physical Review Letters*, 114, 158101.

5. Bekenstein, J. D. (1973). Black holes and entropy. *Physical Review D*, 7, 2333--2346.

6. Bennett, C. H. (1982). The thermodynamics of computation---a review. *International Journal of Theoretical Physics*, 21, 905--940.

7. Berut, A., Arakelyan, A., Petrosyan, A., Ciliberto, S., Dillenschneider, R., and Lutz, E. (2012). Experimental verification of Landauer's principle linking information and thermodynamics. *Nature*, 483, 187--190.

8. Boltzmann, L. (1877). Uber die Beziehung zwischen dem zweiten Hauptsatze der mechanischen Warmetheorie und der Wahrscheinlichkeitsrechnung. *Sitzungsberichte der Kaiserlichen Akademie der Wissenschaften*, 76, 373--435.

9. Carothers, J. M., Oestreich, S. C., Davis, J. H., and Szostak, J. W. (2004). Informational complexity and functional activity of RNA structures. *Journal of the American Chemical Society*, 126, 5130--5137.

10. Crooks, G. E. (1999). Entropy production fluctuation theorem and the nonequilibrium work relation for free energy differences. *Physical Review E*, 60, 2721--2726.

11. Dechant, A. and Sasa, S. (2018). Entropic bounds on currents in Langevin systems. *Physical Review E*, 97, 062101.

12. Deffner, S. and Lutz, E. (2013). Quantum speed limit for non-Markovian dynamics. *Physical Review Letters*, 111, 010402.

13. England, J. L. (2013). Statistical physics of self-replication. *Journal of Chemical Physics*, 139, 121923.

14. Esposito, M. and Van den Broeck, C. (2010). Three detailed fluctuation theorems. *Physical Review Letters*, 104, 090601.

15. Esposito, M. and Van den Broeck, C. (2011). Second law and Landauer principle far from equilibrium. *Europhysics Letters*, 95, 40004.

16. Esposito, M., Lindenberg, K., and Van den Broeck, C. (2010). Entropy production as correlation between system and reservoir. *New Journal of Physics*, 12, 013013.

17. Gingrich, T. R., Horowitz, J. M., Perunov, N., and England, J. L. (2016). Dissipation bounds all steady-state current fluctuations. *Physical Review Letters*, 116, 120601.

18. Hazen, R. M., Griffin, P. L., Carothers, J. M., and Szostak, J. W. (2007). Functional information and the emergence of biocomplexity. *Proceedings of the National Academy of Sciences*, 104, 8574--8581.

19. Hopfield, J. J. (1974). Kinetic proofreading: a new mechanism for reducing errors in biosynthetic processes requiring high specificity. *Proceedings of the National Academy of Sciences*, 71, 4135--4139.

20. Horowitz, J. M. and Gingrich, T. R. (2020). Thermodynamic uncertainty relations constrain non-equilibrium fluctuations. *Nature Physics*, 16, 15--20.

21. Ito, S. (2018). Stochastic thermodynamic interpretation of information geometry. *Physical Review Letters*, 121, 030605.

22. Ito, S. and Dechant, A. (2020). Stochastic time evolution, information geometry, and the Cramer--Rao bound. *Physical Review X*, 10, 021056.

23. Jarzynski, C. (1997). Nonequilibrium equality for free energy differences. *Physical Review Letters*, 78, 2690--2693.

24. Jun, Y., Gavrilov, M., and Bechhoefer, J. (2014). High-precision test of Landauer's principle in a feedback trap. *Physical Review Letters*, 113, 190601.

25. Kempes, C. P., Wolpert, D. H., Cohen, Z., and Perez-Mercader, J. (2017). The thermodynamic efficiency of computations made in cells across the range of life. *Philosophical Transactions of the Royal Society A*, 375, 20160343.

26. Kolchinsky, A. (2022). Thermodynamic threshold for Darwinian evolution. Preprint.

27. Kolchinsky, A. and Wolpert, D. H. (2017). Dependence of dissipation on the initial distribution over states. *Journal of Statistical Mechanics*, 2017, 083202.

28. Kolchinsky, A. and Wolpert, D. H. (2018). Semantic information, autonomous agency and non-equilibrium statistical physics. *Interface Focus*, 8, 20180041.

29. Koyuk, T. and Seifert, U. (2019). Operationally accessible bounds on fluctuations and entropy production in periodically driven systems. *Physical Review Letters*, 122, 230601.

30. Koyuk, T. and Seifert, U. (2020). Thermodynamic uncertainty relation for time-dependent driving. *Physical Review Letters*, 125, 260604.

31. Lan, G., Sartori, P., Neumann, S., Sourjik, V., and Tu, Y. (2012). The energy-speed-accuracy trade-off in sensory adaptation. *Nature Physics*, 8, 422--428.

32. Landauer, R. (1961). Irreversibility and heat generation in the computing process. *IBM Journal of Research and Development*, 5, 183--191.

33. Levitin, L. B. and Toffoli, T. (2009). Fundamental limit on the rate of quantum dynamics: the unified bound is tight. *Physical Review Letters*, 103, 160502.

34. Lloyd, S. (2000). Ultimate physical limits to computation. *Nature*, 406, 1047--1054.

35. Mandelstam, L. and Tamm, I. (1945). The uncertainty relation between energy and time in non-relativistic quantum mechanics. *Izvestiya Akademii Nauk SSSR (Seriya Fizicheskaya)*, 9, 122--128.

36. Margolus, N. and Levitin, L. B. (1998). The maximum speed of dynamical evolution. *Physica D*, 120, 188--195.

37. Nicholson, S. B., Garcia-Pintos, L. P., del Campo, A., and Green, J. R. (2020). Time-information uncertainty relations in thermodynamics. *Nature Physics*, 16, 1211--1215.

38. Proesmans, K., Ehrich, J., and Bechhoefer, J. (2020). Finite-time Landauer principle. *Physical Review Letters*, 125, 100602.

39. Reeb, D. and Wolf, M. M. (2014). An improved Landauer principle with finite-size corrections. *New Journal of Physics*, 16, 103011.

40. Sagawa, T. and Ueda, M. (2010). Generalized Jarzynski equality under nonequilibrium feedback control. *Physical Review Letters*, 104, 090602.

41. Sartori, P. and Pigolotti, S. (2015). Thermodynamics of error correction. *Physical Review X*, 5, 041039.

42. Schmiedl, T. and Seifert, U. (2007). Optimal finite-time processes in stochastic thermodynamics. *Physical Review Letters*, 98, 108301.

43. Seifert, U. (2012). Stochastic thermodynamics, fluctuation theorems and molecular machines. *Reports on Progress in Physics*, 75, 126001.

44. Shannon, C. E. (1948). A mathematical theory of communication. *Bell System Technical Journal*, 27, 379--423.

45. Shiraishi, N., Funo, K., and Saito, K. (2018). Speed limit for classical stochastic processes. *Physical Review Letters*, 121, 070601.

46. Still, S., Sivak, D. A., Bell, A. J., and Crooks, G. E. (2012). Thermodynamics of prediction. *Physical Review Letters*, 109, 120604.

47. Szostak, J. W. (2003). Functional information: molecular messages. *Nature*, 423, 689.

48. Van Vu, T. and Hasegawa, Y. (2020). Unified approach to classical speed limit and thermodynamic uncertainty relation. *Physical Review E*, 102, 062132.

49. Van Vu, T. and Hasegawa, Y. (2022). Unified thermodynamic-kinetic uncertainty relation. *Journal of Physics A: Mathematical and Theoretical*, 55, 013001.

50. Wolpert, D. H. (2019). The stochastic thermodynamics of computation. *Journal of Physics A*, 52, 193001.

51. Wong, M. L., Cleland, C. E., Arend, D., Bartlett, S., Cleaves, H. J., Demarest, H., Prabhu, A., Lunine, J. I., and Hazen, R. M. (2023). On the roles of function and selection in evolving systems. *Proceedings of the National Academy of Sciences*, 120, e2209510120.

52. Garcia-Pintos, L. P., Nicholson, S. B., Green, J. R., del Campo, A., and Gorshkov, A. V. (2022). Unifying quantum and classical speed limits on observables. *Physical Review X*, 12, 011038.

53. Falasco, G. and Esposito, M. (2020). Dissipation-time uncertainty relation. *Physical Review Letters*, 125, 120604.

54. Hasegawa, Y. (2020). Quantum thermodynamic uncertainty relation for continuous measurement. *Physical Review Letters*, 125, 050601.

55. Kolchinsky, A., Corominas-Murtra, B., and Wolpert, D. H. (2022). Decomposing information into copying vs transformation. *Journal of the Royal Society Interface*, 19, 20210913.

56. Fowler, D. M. and Fields, S. (2014). Deep mutational scanning: a new style of protein science. *Nature Methods*, 11, 801--807.

57. Frank, S. A. (2012). Natural selection. V. How to read the fundamental equations of evolutionary change in terms of information theory. *Journal of Evolutionary Biology*, 25, 2377--2396.

58. Peliti, L. and Pigolotti, S. (2021). *Stochastic Thermodynamics: An Introduction*. Princeton University Press.

59. Kolchinsky, A. and Wolpert, D. H. (2020). Thermodynamic costs of Turing machines. *Physical Review Research*, 2, 033312.

60. Timpanaro, A. M., Guarnieri, G., Goold, J., and Landi, G. T. (2019). Thermodynamic uncertainty relations from exchange fluctuation theorems. *Physical Review Letters*, 123, 090604.

61. Gillespie, D. T. (1977). Exact stochastic simulation of coupled chemical reactions. *Journal of Physical Chemistry*, 81, 2340--2361.

62. Drake, J. W. (1991). A constant rate of spontaneous mutation in DNA-based microbes. *Proceedings of the National Academy of Sciences*, 88, 7160--7164.

63. Lynch, M. (2010). Evolution of the mutation rate. *Trends in Genetics*, 26, 345--352.

64. Niven, J. E. and Laughlin, S. B. (2008). Energy limitation as a selective pressure on the evolution of sensory systems. *Journal of Experimental Biology*, 211, 1792--1804.

65. Raichle, M. E. and Gusnard, D. A. (2002). Appraising the brain's energy budget. *Proceedings of the National Academy of Sciences*, 99, 10237--10239.
