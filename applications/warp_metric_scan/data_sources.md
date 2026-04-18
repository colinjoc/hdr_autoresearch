# Data sources — WARP-SCAN: generalised FTL metric scan

## This project is COMPUTATIONAL, not observational

The "data" is the output of symbolic tensor algebra (EinsteinPy) applied to parameterised metric ansätze. No external datasets are downloaded.

## Tools

- **EinsteinPy 0.4.0** — symbolic metric → Christoffel → Riemann → Ricci → Einstein tensor (verified working in 4D and 5D)
- **SymPy 1.13.1** — symbolic algebra backend, simplification, evaluation
- **Custom modules** (to be built):
  - `src/energy_conditions.py` — WEC/NEC/SEC/DEC checker given a stress-energy tensor
  - `src/metric_ansatze.py` — parameterised metric families for each framework
  - `src/field_equations.py` — framework-specific field equations (standard GR, f(R), Einstein-Cartan)
  - `src/kk_reduction.py` — Kaluza-Klein 5D→4D dimensional reduction
  - `src/parameter_scan.py` — numerical grid scan over parameter space

## Frameworks to scan

| # | Framework | Metric dims | Field equations | Olum applies? |
|:---|:---|:---|:---|:---|
| F1 | Standard 4D GR | 4×4 | G_μν = 8πT_μν | Yes (baseline) |
| F2 | 5D Kaluza-Klein | 5×5 → 4D projection | 5D Einstein → effective 4D | Not directly |
| F3 | f(R) modified gravity | 4×4 | f'(R)R_μν - ½f(R)g_μν + ... = 8πT_μν | Not directly |
| F4 | Einstein-Cartan (torsion) | 4×4 + torsion tensor | G_μν + torsion terms = 8πT_μν | Not directly (assumes torsion-free) |
| F5 | Braneworld (Randall-Sundrum) | 5×5 bulk → 4D brane | Gauss-Codazzi + junction conditions | Not directly |

## Predecessor

- UFO-3 warp drive physics paper at `warp_drive_physics/paper.md`
- Catalogue at `warp_drive_physics/discoveries/warp_metric_catalogue.csv`

## Verification strategy

- F1 (standard GR) MUST reproduce the Olum result (WEC violation for v>c) — this validates the tooling
- Each subsequent framework is compared against F1 to quantify the "extra terms" from the extension
- Numerical evaluation at grid points when symbolic simplification stalls
