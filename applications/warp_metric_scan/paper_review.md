# Blind Review: Systematic Test of FTL Warp Transport Without Exotic Matter

**Reviewer role**: External referee, no access to authors.

---

## Overall Assessment

The paper asks a well-defined question (do four GR extensions permit positive-energy FTL?) and arrives at a defensible negative answer. The honesty of the conclusion ("no physically realizable pathway") is commendable. However, several modelling choices need sharper disclosure, and the test suite does not adequately cover the two frameworks (F4, F5) that carry the paper's main claims.

---

## (a) Fell-Heisenberg Proxy (Section 2.1, metric_ansatze.py line 58-87)

**Issue**: The code adds a constant `shell_energy = 10` to G_00 and calls it a "Fell-Heisenberg proxy." The real Fell-Heisenberg (2024) paper constructs a specific matter shell with self-consistent stress-energy computed from the metric's boundary conditions. Adding a constant is not a proxy for that construction -- it is an independent toy model.

**Assessment**: The docstring in `metric_ansatze.py` does say "this is a proxy" and "the actual paper uses a specific shell construction." The paper (Section 2.1) says "Fell-Heisenberg proxy at v = 0.04 satisfies WEC (positive shell energy)" but does not explicitly flag this as a non-reproduction. The Fell-Heisenberg result is used only for pipeline validation, not as a main finding, which limits the damage.

**Required action**: Add an explicit sentence in Section 2.1: "Our Fell-Heisenberg test is a pipeline validation proxy (constant positive offset added to G_00) and does not reproduce the self-consistent shell construction of Fell and Heisenberg (2024)."

---

## (b) F4 Einstein-Cartan Torsion Model (Section 3.4)

**Issue**: The torsion contribution H_00 = s0^2 |grad f|^2 exp(-r^2/sigma_S^2) is presented as following DeBenedictis and Ilijic (2018) [P092]. However:

1. DeBenedictis-Ilijic derive the torsion contribution from a Weyssenhoff spin fluid in the Cartan field equations. Their result is H_00 proportional to s^2 (spin density squared), but the spatial profile comes from the metric-dependent spin-torsion coupling, not an independently chosen Gaussian envelope.

2. Our model uses an independent Gaussian torsion profile exp(-r^2/sigma_S^2) with sigma_S as a free parameter. This is an ad-hoc construction, not a derivation from the EC field equations.

3. The key EC references (Hehl et al. 1976 [P085]; DeBenedictis-Ilijic 2018 [P092]) are cited but the paper does not explain how our H_00 model departs from their derivations.

**Assessment**: The s0^2 scaling is physically motivated. The spatial profile is ad-hoc but plausible (torsion localised at the bubble wall). The paper should state: "Our torsion model captures the s0^2 scaling from EC theory but uses an ad-hoc Gaussian spatial profile rather than deriving H_00 self-consistently from the Cartan field equations."

**Required action**: Add a paragraph in Section 3.4 or Section 4.1 clarifying the ad-hoc nature of the spatial profile and citing Hehl et al. (1976) for the general EC spin-torsion coupling structure.

---

## (c) F5 Braneworld Weyl Projection (Section 3.5)

**Issue**: E_00 = C_W |grad f|^2 f^2 is modelled as a freely specifiable parameter. In the actual Shiromizu-Maeda-Sasaki (SMS) equations [P055], E_mu_nu is determined by the 5D bulk geometry via the Gauss-Codazzi equations. It is not a free function on the brane. Treating C_W as a tunable parameter is equivalent to asking "what if the bulk happened to produce exactly the right Weyl tensor?" -- this is not a physical prediction.

**Assessment**: Section 3.5 does acknowledge "C_W = -200 requires engineering a specific 5D anti-de Sitter bulk spacetime." Section 4.1 calls it a "formal loophole." This is reasonably honest but could be sharper.

**Required action**: Add to Section 2.1 (framework description): "E_mu_nu is treated as a free parameter to explore the space of possible bulk geometries. This is a best-case analysis: it asks whether any bulk geometry could produce the required Weyl projection, without demonstrating that such a geometry exists."

---

## (d) Grid Resolution Sensitivity

**Issue**: The numerical evaluation uses 50 points along x in [-2, 2] plus 25 off-axis points (75 total). For a Gaussian shape function, the key features (gradient extrema) are at r ~ 1/sqrt(2) ~ 0.71. The grid spacing is 4/50 = 0.08, which should resolve this.

**Required action**: Run a convergence test: evaluate F4 critical s0 at 75, 150, and 300 grid points. If the critical s0 changes by more than 5%, report the sensitivity. Add one sentence to Section 2.2 stating the convergence result.

---

## (e) "Tantalizingly Close" Framing

**Issue**: The paper does NOT use the phrase "tantalizingly close" in the current draft. The abstract says "The honest answer is: no extension of GR tested here provides a physically realizable pathway." Section 4.1 says "formal loophole, not physical." The conclusions say "Formal loophole, not physical" for both F4 and F5. The framing is honest and appropriately cautious.

**Assessment**: No change needed on this point. The paper correctly identifies the 16-order-of-magnitude gap for F4 and the absence of a bulk construction procedure for F5.

---

## (f) Test Coverage for F4 and F5

**Issue**: The test suite has 10 tests. Of these:
- 2 tests cover F4 (`test_einstein_cartan_torsion_adds_positive_contribution`, `test_einstein_cartan_large_spin_can_flip_wec`)
- 1 test covers F5 (`test_braneworld_weyl_contribution`)

However, no test directly validates the scan results reported in the paper:
- No test checks that F4 critical s0 at v=1.5 is approximately 4.3 (E12 result)
- No test checks that F5 at C_W=-100, v=1.5 gives min_eff approximately -0.074 (E14 result)
- No test checks grid convergence
- No test for the F4+F5 interaction (E22)

**Required action**: Add at least 3 tests:
1. F4 critical s0 at v=1.5 is in [3, 6] (validates E12)
2. F5 at C_W=-100, v=1.5 has negative min_eff (validates E14 -- WEC still violated)
3. Grid convergence test: F4 critical s0 changes by <5% when grid doubled

---

## Mandated Experiments Summary

1. **Grid convergence test** (concern d): Run F4 WEC check at 75, 150, 300 grid points
2. **Three new tests** (concern f): F4 critical s0, F5 scan validation, grid convergence
3. **Paper text edits** (concerns a, b, c, d): Four disclosure paragraphs

---

## Verdict

**Conditional accept** -- the science is sound, the conclusion is honest, but the modelling assumptions for F4 and F5 need sharper disclosure, and the test suite needs to cover the main quantitative claims.
