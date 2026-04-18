# Knowledge Base: Warp Metric Scan

## Established Facts

1. **Alcubierre WEC violation is universal**: For any v > 0, the Eulerian energy density T^00 is non-positive in the bubble wall. This is a direct consequence of the metric form, not a coordinate artifact [P001, P020].
2. **Olum no-go theorem**: Superluminal travel in any globally hyperbolic spacetime with a complete achronal surface requires WEC violation. Assumptions: standard GR field equations, 4D, torsion-free [P009].
3. **Santiago-Schuster-Visser NEC no-go**: All Natario-class warp drives violate NEC. Assumptions: unit lapse, flat spatial metric, zero vorticity, torsion-free, 4D [P007].
4. **Fell-Heisenberg subluminal boundary**: Positive-energy warp drives exist at v < v_threshold (approximately 0.04c demonstrated), with a shell of approximately 2.365 Jupiter masses [P005].
5. **Quantum inequalities constrain exotic matter**: Ford-Roman QIs require bubble wall thickness of Planck scale if respected, driving energy requirements to approximately 10^62 kg c^2 [P020, P021].
6. **Casimir effect provides only approximately 10^-3 J/m^3**: The gap between available negative energy and warp drive requirements is approximately 60 orders of magnitude [P147, P148].
7. **f(R) gravity can support wormholes without exotic matter**: Lobo-Oliveira showed matter threading f(R) wormhole throats can satisfy all energy conditions [P077].
8. **Einstein-Cartan torsion can offset negative energy**: DeBenedictis-Ilijic showed torsion terms add positive contributions to effective G_00, potentially satisfying WEC [P092].
9. **Braneworld Weyl tensor is not constrained by brane matter**: E_mu_nu is determined by bulk geometry and can have either sign [P055, P056].
10. **KK induced matter from 5D vacuum**: A 5D vacuum can project to 4D spacetime with non-trivial effective stress-energy [P042, P043].
11. **Torsion does not propagate in EC theory**: S^lambda_mu_nu is algebraically determined by spin density, nonzero only inside matter [P085, P089].
12. **Braneworld quadratic corrections worsen energy violations**: pi_mu_nu is positive-definite for positive-energy matter [P116].
13. **Warp drives are semiclassically unstable**: Runaway particle creation at bubble wall [P028].
14. **FTL risks CTC formation**: Two opposing warp trajectories create Krasnikov-tube CTCs [P026, P031].
15. **Lentz positive-energy claim is erroneous**: Celmaster-Rubin identified derivation errors [P006].

## Known Pitfalls

1. **Coordinate-dependent energy density**: T^00 is observer-dependent; WEC requires positivity for ALL timelike observers, not just Eulerian [P007].
2. **Confusing geometric terms with matter terms**: In f(R) gravity, positive matter energy does not guarantee positive effective energy [P151, P152].
3. **Neglecting quantum back-reaction**: Classical positive-energy solutions may be destabilized by quantum effects [P028, P029].
4. **Assuming extra-dimensional effects are free**: KK and braneworld corrections are constrained by solar system tests [P046, P200].
5. **Tachyonic instabilities in f(R)**: Some f(R) models (e.g., 1/R) are unstable [P155]; must check Dolgov-Kawasaki criterion.
6. **Gregory-Laflamme instability in braneworlds**: Extended objects in higher-D can be unstable [P065].
7. **Spin density requirements may be unphysical**: DeBenedictis-Ilijic derived minimum spin densities but did not assess physical realizability [P092].
8. **Noncompactified KK theories are not experimentally validated**: The induced-matter interpretation is theoretically elegant but lacks direct experimental support [P042].

## What Works

- EinsteinPy for symbolic metric/tensor computation (verified in tests)
- Gaussian shape function f = exp(-r^2) as proxy for top-hat bubble
- Numerical grid evaluation of energy conditions at sample points
- Parameter scanning over (v, coupling) grids

## What Does Not Work

- Full symbolic simplification of R^2 corrections (combinatorial explosion)
- Exact analytical solutions for 5D Einstein equations with warp geometry
- Propagating torsion (EC torsion is algebraic, not dynamic)
