# Research Queue

## Format: ID | Hypothesis | Prior | Mechanism | Design Variable | Metric | Baseline | Status

### F1: Standard GR Baseline
H001 | WEC violation occurs for any v > 0 | 0.95 | Alcubierre T^00 formula is non-positive | v | min(G_00) | flat space G_00=0 | OPEN
H002 | NEC violation occurs for any v > c | 0.90 | Santiago-Visser theorem for Natario class | v | min(G_00+G_11) | subluminal NEC | OPEN
H003 | WEC violation magnitude scales as v^2 | 0.80 | T^00 proportional to v^2 | v | min(G_00) | v=0.5 baseline | OPEN
H004 | NEC is satisfied for v << 1 | 0.85 | Linearized regime respects NEC | v | min(G_00+G_11) | v=0.01 | OPEN
H005 | The v-threshold for WEC flip is v=0 | 0.90 | Any nonzero shift creates negative T^00 | v | G_00 sign | analytic | OPEN
H006 | Bubble wall region has most negative G_00 | 0.95 | Gradient of shape function maximized at wall | x_position | G_00(x) | center | OPEN
H007 | Increasing bubble thickness reduces |G_00| peak | 0.70 | Smoother gradient = less extreme curvature | delta | max|G_00| | delta=1 | OPEN
H008 | The fell-heisenberg proxy satisfies WEC at v=0.04 | 0.90 | Shell energy offsets negative G_00 | v | WEC satisfied | Alcubierre at v=0.04 | OPEN
H009 | NEC violation magnitude diverges as v->infinity | 0.75 | Higher v means more extreme curvature | v | min(G_00+G_11) | v=2 | OPEN
H010 | The minimum G_00 location is at r approximately 1 for Gaussian f | 0.85 | Max gradient of exp(-r^2) at r approximately 1 | x_position | argmin(G_00) | center | OPEN

### F2: 5D Kaluza-Klein
H011 | KK contribution (G_00^5D - G_00^4D) is nonzero for alpha != 0 | 0.95 | Extra dimension modulates curvature | alpha | G_00 difference | alpha=0 | OPEN
H012 | KK contribution can be positive for some alpha | 0.60 | Depends on sign of phi derivatives | alpha | sign(Delta_G00) | alpha=0 | OPEN
H013 | At v=1.5, exists alpha that makes total G_00 positive | 0.20 | Would require large KK correction | (v,alpha) | G_00>0 | v=1.5 alpha=0 | OPEN
H014 | KK contribution grows with |alpha| | 0.80 | Larger modulation = stronger correction | alpha | |Delta_G00| | alpha=0.1 | OPEN
H015 | KK contribution has same sign for alpha > 0 and alpha < 0 | 0.40 | Depends on whether phi^2 derivatives are even | alpha | sign(Delta_G00) | both signs | OPEN
H016 | Required alpha for G_00=0 at v=1.5 is physically unreasonable | 0.75 | Large alpha implies extra dim radius >> Planck | alpha_critical | |alpha_critical| | physical bounds | OPEN
H017 | KK helps more at lower v (closer to c) | 0.55 | Lower v needs less correction | v | alpha_critical(v) | v=3 | OPEN
H018 | 5D G_44 equation constrains alpha independently | 0.70 | Consistency of 5D Einstein equations | alpha | G_44=0 constraint | unconstrained | OPEN
H019 | KK correction is largest at bubble wall | 0.80 | phi gradient concentrated there | x_position | Delta_G00(x) | center | OPEN
H020 | Combined (v>1, alpha) WEC-satisfaction region is empty | 0.70 | Olum theorem applies in 4D projection | (v,alpha) | WEC region | full grid | OPEN

### F3: f(R) = R + alpha*R^2
H021 | f(R) correction adds both positive and negative contributions to G_00_eff | 0.80 | R*R_00 and R^2*g_00 have different signs | alpha_R2 | Delta_G00_fR | alpha_R2=0 | OPEN
H022 | f(R) correction is positive at bubble wall for positive alpha_R2 | 0.45 | Depends on relative magnitudes of R*R_00 vs R^2 | alpha_R2 | sign(Delta_G00_fR) | alpha_R2=0 | OPEN
H023 | At v=1.5, exists alpha_R2 that flips G_00_eff positive | 0.15 | Would contradict generalized no-go for modified gravity | (v,alpha_R2) | G_00_eff>0 | v=1.5 alpha_R2=0 | OPEN
H024 | f(R) correction magnitude grows with alpha_R2 | 0.90 | Linear in alpha_R2 at leading order | alpha_R2 | |Delta_G00_fR| | alpha_R2=0.1 | OPEN
H025 | Dolgov-Kawasaki stability requires f''(R) > 0, which is always satisfied for R+alpha*R^2 with alpha>0 | 0.95 | f''(R) = 2*alpha > 0 for alpha > 0 | alpha_R2 | f''(R) sign | analytic | OPEN
H026 | Required alpha_R2 to flip sign exceeds Starobinsky constraint | 0.80 | Cosmological constraints limit alpha_R2 | alpha_R2_critical | comparison | Starobinsky bound | OPEN
H027 | f(R) correction is negligible compared to standard G_00 for alpha_R2 < 1 | 0.60 | Leading-order correction may be small | alpha_R2 | ratio |Delta_G00|/|G_00| | v=1.5 | OPEN
H028 | f(R) correction changes sign across bubble | 0.65 | R and R_00 have different spatial profiles | x_position | sign(Delta_G00_fR)(x) | center | OPEN
H029 | f(R) warp drive still violates NEC even with correction | 0.85 | Santiago-Visser applies to geometric, not effective | (v,alpha_R2) | NEC for effective | standard NEC | OPEN
H030 | f(R) correction is second-order in curvature, so only significant near bubble wall | 0.75 | R^2 only large where curvature is large | x_position | Delta_G00_fR(x) | flat region | OPEN

### F4: Einstein-Cartan (Torsion)
H031 | Torsion contribution H_00 can be positive | 0.85 | DeBenedictis-Ilijic showed this | s_0 | sign(H_00) | s_0=0 | OPEN
H032 | Sufficient spin density exists to flip WEC for v=0.5 | 0.50 | Subluminal regime needs less correction | (v,s_0) | WEC satisfied | v=0.5 no spin | OPEN
H033 | Sufficient spin density exists to flip WEC for v=1.5 | 0.25 | Superluminal regime needs much more correction | (v,s_0) | WEC satisfied | v=1.5 no spin | OPEN
H034 | Required spin density scales as v^2 | 0.65 | Must offset v^2-scaling of G_00 violation | v | s_0_critical(v) | v=0.5 | OPEN
H035 | Required spin density exceeds nuclear spin density | 0.70 | Nuclear matter has s approximately 10^44 J/m^3 | s_0_critical | comparison | nuclear limit | OPEN
H036 | Torsion contribution is concentrated at bubble wall | 0.90 | S ~ gradient of f, peaks at wall | x_position | H_00(x) | center | OPEN
H037 | Torsion does not affect NEC independently of WEC | 0.55 | H_mu_nu modifies both G_00 and G_11 | s_0 | NEC check | WEC check | OPEN
H038 | EC torsion model with S ~ nabla f is self-consistent | 0.70 | Cartan equations relate S to spin density | model | self-consistency | N/A | OPEN
H039 | Varying torsion profile width sigma_S affects required s_0 | 0.75 | Narrower profile needs higher peak spin | sigma_S | s_0_critical | sigma_S=1 | OPEN
H040 | EC warp drive is stable against spin-fluid perturbations | 0.35 | Weyssenhoff fluid stability is unclear | s_0 | stability | unperturbed | OPEN

### F5: Braneworld (Randall-Sundrum)
H041 | Weyl projection E_00 can contribute positive energy density | 0.70 | E_mu_nu not constrained by brane matter | C_W | sign(-E_00) | C_W=0 | OPEN
H042 | Quadratic correction pi_00 is positive-definite | 0.90 | de Rham showed this for positive-energy matter | T_mu_nu | sign(pi_00) | GR limit | OPEN
H043 | Combined (Weyl + quadratic) correction can flip G_00_eff | 0.20 | E_00 must overcome both G_00 and pi_00 | C_W | G_00_eff sign | C_W=0 | OPEN
H044 | Required C_W for WEC satisfaction at v=1.5 is physically unreasonable | 0.75 | Needs tuned bulk geometry | C_W_critical | comparison | RS natural scale | OPEN
H045 | High brane tension suppresses both corrections | 0.80 | Both pi and E scale as 1/lambda | lambda | correction magnitude | lambda=infinity | OPEN
H046 | Low brane tension makes quadratic correction dominant | 0.85 | pi approximately rho^2/lambda dominates for rho>>lambda | lambda | pi/E ratio | high lambda | OPEN
H047 | Dark radiation term can mimic negative cosmological constant | 0.60 | E_mu_nu can act as effective cosmological term | C_W | E_mu_nu form | zero bulk | OPEN
H048 | Braneworld warp drive requires fine-tuning of bulk initial conditions | 0.80 | E_mu_nu depends on entire bulk evolution | initial conditions | sensitivity | natural bulk | OPEN
H049 | Combined braneworld + f(R) corrections add constructively | 0.35 | Independent mechanisms might cancel | both | combined G_00_eff | individual | OPEN
H050 | Braneworld corrections are negligible for lambda >> (TeV)^4 | 0.85 | Current experimental bound | lambda | correction magnitude | lambda_current | OPEN

### Cross-Framework
H051 | No framework achieves positive-energy superluminal warp | 0.75 | All no-go theorems have partial coverage | all | WEC+v>1 | F1 baseline | OPEN
H052 | Framework closest to positive-energy FTL is F4 (Einstein-Cartan) | 0.40 | Torsion directly addresses the gap in Olum's proof | all | min|alpha_needed| | comparison | OPEN
H053 | Framework closest to positive-energy FTL is F3 (f(R)) | 0.30 | f(R) modifies field equations but geometry still controls | all | min|alpha_needed| | comparison | OPEN
H054 | Combined F2+F3 outperforms either alone | 0.30 | KK + f(R) adds two independent corrections | (alpha,alpha_R2) | G_00_eff | individual | OPEN
H055 | Combined F4+F5 outperforms either alone | 0.25 | Torsion + Weyl add independently | (s_0,C_W) | G_00_eff | individual | OPEN
H056 | The gap between best framework and positive energy is > 10 orders of magnitude | 0.55 | Analogous to Casimir-warp gap | all | gap magnitude | zero | OPEN
H057 | Quantum inequalities block all classical loopholes | 0.70 | QIs apply in curved spacetime too | all | QI constraint | classical result | OPEN
H058 | CTC formation risk is universal across frameworks | 0.80 | FTL in any theory risks CTCs | all | CTC risk | N/A | OPEN
H059 | Mass/energy requirements scale similarly across frameworks | 0.50 | Each framework has different energy accounting | all | mass comparison | Alcubierre | OPEN
H060 | Stability analysis eliminates some candidate solutions | 0.65 | Dynamical instabilities are common | all | stability | static analysis | OPEN

### Detailed Parameter Studies
H061 | v-threshold scan: WEC flips at v=0 (any nonzero v violates) | 0.90 | T^00 formula | v | WEC flip point | analytic | OPEN
H062 | KK: alpha > 0 gives positive Delta_G00 | 0.45 | Sign depends on phi geometry | alpha | sign(Delta_G00) | analytic | OPEN
H063 | KK: alpha < 0 gives positive Delta_G00 | 0.45 | Opposite modulation | alpha | sign(Delta_G00) | analytic | OPEN
H064 | f(R): alpha_R2 = 1 changes G_00 by > 10% | 0.55 | Leading-order estimate | alpha_R2 | fractional change | alpha_R2=0 | OPEN
H065 | f(R): alpha_R2 = 10 changes G_00 by > 50% | 0.50 | Large correction regime | alpha_R2 | fractional change | alpha_R2=0 | OPEN
H066 | EC: s_0 = 10^10 is sufficient for v=0.5 | 0.30 | Order-of-magnitude estimate | s_0 | WEC satisfied | no spin | OPEN
H067 | EC: s_0 = 10^20 is sufficient for v=1.5 | 0.20 | Requires enormous spin density | s_0 | WEC satisfied | no spin | OPEN
H068 | RS: C_W = -5 flips G_00_eff for v=1 | 0.25 | Requires specific bulk geometry | C_W | WEC satisfied | C_W=0 | OPEN
H069 | RS: brane tension lambda < 10^8 needed for significant correction | 0.60 | Low tension enhances corrections | lambda | correction magnitude | high lambda | OPEN
H070 | All frameworks: minimum |G_00| scales linearly with v for v < 1 | 0.70 | Linearized regime | v | |G_00| scaling | v=0.1 | OPEN

### Physical Realizability
H071 | KK: required alpha corresponds to extra dim radius > 1mm (ruled out) | 0.50 | Depends on mapping alpha to physical radius | alpha_critical | physical radius | Planck scale | OPEN
H072 | f(R): required alpha_R2 violates CMB constraints | 0.65 | Starobinsky alpha approximately 10^9 for inflation, but different scale | alpha_R2_critical | CMB comparison | Starobinsky | OPEN
H073 | EC: required spin density exceeds neutron star matter | 0.60 | Neutron stars have highest known spin densities | s_0_critical | comparison | nuclear | OPEN
H074 | RS: required C_W violates AdS stability | 0.55 | Large Weyl tensor may destabilize bulk | C_W_critical | stability | small C_W | OPEN
H075 | No framework has a physically realizable parameter set for v > 1 | 0.80 | All loopholes require extreme parameters | all | realizability | physical bounds | OPEN

### Numerical Convergence and Methods
H076 | Grid resolution of 50 points is sufficient for WEC determination | 0.85 | Energy density is smooth | n_points | result stability | n_points=50 | OPEN
H077 | Off-axis sampling catches WEC violations missed on-axis | 0.60 | 3D curvature may differ from 1D | sampling | min(G_00) | on-axis only | OPEN
H078 | Symbolic simplification of R for warp metric converges in < 60s | 0.75 | EinsteinPy handles 4D well | time | computation time | timeout | OPEN
H079 | 5D Einstein tensor computation completes in < 300s | 0.65 | 5D is much more expensive | time | computation time | 4D time | OPEN
H080 | f(R) effective stress-energy requires Ricci scalar which is expensive | 0.70 | R involves second derivatives of metric | time | computation time | G_00 only | OPEN

### Interaction Effects
H081 | F2+F3 combined: KK modulation changes R, enhancing f(R) correction | 0.35 | KK alters curvature profile | (alpha,alpha_R2) | combined G_00 | individual | OPEN
H082 | F4+F3 combined: torsion in f(R) gravity has different field equations | 0.40 | f(R) with torsion is distinct theory | combined | field equations | individual | OPEN
H083 | F2+F5: KK in braneworld context (already extra dimensions) | 0.30 | Both modify 4D via higher dimensions | combined | consistency | individual | OPEN
H084 | F3+F5: f(R) on brane changes effective SMS equations | 0.35 | Modified gravity on brane | combined | effective equations | individual | OPEN
H085 | Any two-framework combination achieves positive-energy FTL | 0.10 | Would be a major result | any pair | WEC+v>1 | individual | OPEN

### Sensitivity and Robustness
H086 | Results are sensitive to shape function choice (Gaussian vs top-hat) | 0.60 | Different gradients = different energy profiles | shape | min(G_00) | Gaussian | OPEN
H087 | Results are insensitive to bubble size for fixed v | 0.70 | Rescaling argument | R_bubble | min(G_00) | R=1 | OPEN
H088 | Coordinate choice affects numerical but not qualitative results | 0.85 | Energy conditions are coordinate-invariant | coords | WEC yes/no | Cartesian | OPEN
H089 | Higher-order f(R) terms (R^3, R^4) do not qualitatively change results | 0.75 | Leading order dominates | f(R) form | sign(Delta_G00) | R+alpha*R^2 | OPEN
H090 | Torsion tensor form (gradient vs constant) affects required spin | 0.70 | Profile matters for local conditions | torsion form | s_0_critical | gradient form | OPEN

### Long-Shot Hypotheses (prior <= 0.3)
H091 | A specific (v>1, alpha) point exists where 5D is completely WEC-respecting | 0.10 | Would violate effective Olum | (v,alpha) | WEC | F1 | OPEN
H092 | f(R) = R + alpha*R^2 with alpha approximately 10^6 permits v=2c | 0.05 | Extreme correction needed | alpha_R2 | G_00_eff sign | standard | OPEN
H093 | Spin-2 torsion (not spin-1/2) creates stronger H_00 | 0.15 | Most EC theory uses spin-1/2 | spin type | H_00 magnitude | spin-1/2 | OPEN
H094 | Braneworld with negative brane tension allows positive-energy FTL | 0.10 | Negative tension brane is unstable | lambda sign | WEC | positive tension | OPEN
H095 | Warped extra dimension (not flat) changes KK results qualitatively | 0.20 | RS-type warping of extra dim | warp factor | Delta_G00 | flat extra dim | OPEN
H096 | Quantum effects generate effective torsion sufficient for warp | 0.05 | Spin-torsion coupling at quantum level | quantum | H_00 | classical | OPEN
H097 | Analog gravity provides experimental test of energy conditions | 0.15 | Acoustic metrics obey similar equations | analog | experimental | theory-only | OPEN
H098 | Casimir energy from KK modes is sufficient for subluminal warp | 0.10 | Obousy-Cleaver proposal | KK modes | Casimir energy | required energy | OPEN
H099 | Time-dependent torsion (pulsed) circumvents steady-state no-go | 0.15 | Dynamic solutions might differ | time dependence | WEC(t) | static | OPEN
H100 | Noncommutative geometry provides additional positive energy | 0.05 | Speculative theoretical framework | NC parameter | G_00_eff | commutative | OPEN
H101 | String theory landscape contains a warp-compatible vacuum | 0.05 | 10^500 vacua might include one | vacuum | energy conditions | standard | OPEN
H102 | Conformal gravity (Weyl-squared) permits positive-energy warp | 0.10 | Fourth-order theory with different structure | Weyl^2 | G_00_eff | Einstein | OPEN
H103 | Gravitational self-energy of warp bubble provides positive contribution | 0.20 | Back-reaction effect | self-energy | Delta_G00 | test-field | OPEN
H104 | Non-minimally coupled scalar field in warp geometry evades NEC | 0.15 | phi*R coupling changes energy conditions | coupling | effective NEC | minimal | OPEN
H105 | Topological effects (warp bubble as defect) change energy accounting | 0.10 | Non-trivial topology changes global energy | topology | total energy | trivial | OPEN
