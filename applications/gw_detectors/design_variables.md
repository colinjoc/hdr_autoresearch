# Design Variables — gw_detectors

**Status**: Phase 0 in progress. This catalogues every parameter of a Universal Interferometric Field Operator (UIFO) detector design, with physical interpretation, valid range, and the proxy used by Differometor. Target: 15+ design variables with physics justification per program.md Phase 0 quality gate.

---

## What gets optimised

A UIFO design is a graph of optical elements (nodes) connected by free spaces (edges). Each element exposes a small number of physical parameters that the optimiser can adjust. The full parameter space for a typical post-merger Zoo design has 100–400 free parameters; the count depends on element count and the number of properties exposed per element.

---

## Per-element parameter table

| Element type | Parameter | Range | Physical meaning | Units | Differometor field |
|---|---|---|---|---|---|
| Mirror | reflectivity | [0, 1] | Power reflection coefficient. R=0 → fully transparent, R=1 → perfect reflector | dimensionless | `reflectivity` |
| Mirror | loss | [0, 1] | Power loss per surface (absorption + scatter) | dimensionless | `loss` |
| Mirror | tuning | [0, 360°] | Microscopic position offset that sets the operating point of any cavity the mirror belongs to | degrees | `tuning` |
| Mirror (free mass) | mass | [0.1, 200+] | Mirror mass; sets the radiation-pressure noise floor and the optomechanical spring resonance | kg | `mass` (on the linked free_mass node) |
| Mirror | temperature | [4, 300] | Test mass temperature; lower → less coating thermal noise, more demanding cryogenics | K | `temperature` |
| Beamsplitter | reflectivity | [0, 1] | Power split ratio. 0.5 = symmetric Michelson | dimensionless | `reflectivity` |
| Beamsplitter | tuning | [0, 360°] | Operating-point microscopic offset | degrees | `tuning` |
| Directional beamsplitter | (no free properties in the bundled examples) | — | Used for one-way coupling | — | — |
| Laser | input power | [0, ~1000] | Laser input power; sets shot-noise floor (∝ 1/√P) and radiation-pressure floor (∝ √P) | W | `power` |
| Laser | wavelength | discrete | 1064 nm (current), 2 µm (Voyager), 1.55 µm (telecom) | m | `wavelength` |
| Squeezer | squeezing level | [0, 15] | Squeezing depth in the rotated quadrature; 0 dB = no squeezing, 10 dB = 10× variance reduction | dB | `squeezing` |
| Squeezer | squeezing angle | [0, 360°] | Quadrature angle of the squeezed state | degrees | `angle` |
| Photodetector | homodyne angle | [0, 360°] | Local-oscillator phase for balanced homodyne readout | degrees | `homodyne_angle` |
| Frequency node | frequency | discrete (1, by convention) | Reference for the simulation; not optimised | dimensionless | `frequency` |
| Free space (edge) | length | [10, 4000+] | Distance between connected components; arm cavities are typically 4 km | m | edge property |

---

## Derived quantities

These are not free parameters but are computed from the per-element parameters and matter for the physics interpretation.

### Arm cavity finesse
$$F = \frac{\pi \sqrt{R_{\rm ITM} R_{\rm ETM}}}{1 - R_{\rm ITM} R_{\rm ETM}}$$
- $R_{\rm ITM}$: input test mass reflectivity (typically near 1, e.g. 0.99)
- $R_{\rm ETM}$: end test mass reflectivity (typically very close to 1, e.g. 0.99996)
- For Voyager: $F \approx 3100$
- The Krenn et al. 2025 paper claims their best designs reach $F \sim 6000$+

### Standard quantum limit
$$h_{\rm SQL}(f) = \sqrt{\frac{8 \hbar}{M (2\pi f)^2 L^2}}$$
- $M$ = test mass mass, $L$ = arm length

### Optomechanical spring resonance
For a signal-recycled interferometer with mirror mass $M$ and effective optical spring constant $K$:
$$\omega_s = \sqrt{K / M}$$
- The optical spring constant $K$ depends on circulating power, detuning, and mirror reflectivities (Buonanno-Chen 2002, papers.csv id 12)

### Strain sensitivity
$$h(f) = \frac{S_n^{1/2}(f)}{|T_s(f)|}$$
- $S_n(f)$: total noise power spectral density (shot + radiation pressure + thermal + ...)
- $T_s(f)$: signal transfer function (response of the detector to a unit strain input)

---

## Categorisation: which parameters are critically tuned vs broad plateaus?

This is **the main question of the project**, not a known fact. Hypotheses (see `research_queue.md`):

| Parameter | Hypothesised regime | Hypothesised reason | Test |
|---|---|---|---|
| Arm cavity input mirror reflectivity | Sharp narrow peak | Impedance-matching at critical coupling | H02 sweep |
| Arm cavity end mirror reflectivity | Sharp (R must be ~1) | Light cannot leak from the cavity | H02 |
| Beamsplitter reflectivity | Broad plateau in [0.5, 0.8] | Tradeoff is smooth | H03 sweep |
| End-mirror mass | Sharp peak | Sets spring resonance frequency in target band | H06 |
| Squeezer level | Irrelevant (the 4 squeezers in sol00 carry <0.5 dB) | Optomechanical squeezing is doing the work | H05 |
| Homodyne readout angle | Broad / irrelevant | Symmetry of balanced homodyne | TBD |
| Tuning offsets | Sharp at zero / multiples of π | Operating-point physics | TBD |

These are starting hypotheses, not facts. They will be tested in Phase 1.

---

## The kat (Finesse) language used by the GWDetectorZoo

Each Zoo solution is stored as a PyKat-generated `.kat` file. The format is a small domain-specific language with these statement types (verified from `solutions/type8/sol00/CFGS_8_-85.46_120_*.txt`):

| Statement | Meaning | Example |
|---|---|---|
| `const paramXXXX <value>` | Define a named scalar parameter at top-of-file | `const param0133 131.498` |
| `m1 <name> <R> <loss> <tuning> <node1> <node2>` | Mirror with reflectivity / loss / tuning, two ports | `m1 ML_5_4 $param0016 5e-06 $param0017 nA nB` |
| `bs1 <name> <R> <loss> <tuning> <angle> <n1> <n2> <n3> <n4>` | Beamsplitter with four ports | `bs1 B1_1 $param0022 5e-06 0.0 -45.0 nB1_1d nB1_1l nB1_1u nB1_1r` |
| `dbs <name> <n1> <n2> <n3> <n4>` | Directional (Faraday-isolator-like) beamsplitter | `dbs B4_4 nB4_4d nB4_4l nB4_4u nB4_4r` |
| `l <name> <power> <freq> <phase> <node>` | Laser source | `l L_5_4 $param0015 0.0 0.0 nL_5_4` |
| `s <name> <length> <node1> <node2>` | Free space (edge) connecting two nodes | `s SL_5_4 1.0 nL_5_4 nML_5_4_laser` |
| `attr <name> mass <value>` | Set a property (typically `mass`) on a previously-defined component | `attr ML_5_3 mass $param0014` |
| `pd0 <name> <node>` | DC photodetector (carrier power) | `pd0 poutdc1 AtPD1` |
| `pd1 <name> <freq> <node>` | AC photodetector at a frequency | `pd1 poutf1 $fs AtPD1` |
| `qnoised <name> <order> <freq> <node>` | Quantum noise detector | `qnoised nodeFinalDet1 1 $fs AtPD1` |
| `qhd <name> <homodyne_angle> <node1> <node2>` | Quantum balanced-homodyne detector | `qhd nodeFinalDet 180.0 AtPD1 AtPD2` |
| `fsig <name> <target_component> <type> <amp> <phase> <freq>` | Signal injection on a free space (used to model gravitational-wave strain perturbation) | `fsig mUD_1_0sig mUD_1_0 phase 1.0 180.0 1.0` |
| `phase <int>` | Set carrier phase mode | `phase 2` |
| `maxtem off` | Higher-order mode tracking off | `maxtem off` |
| `yaxis lin re:im` / `xaxis ...` | Output formatting | `xaxis mUD_1_0sig f log` |

Parameter references are introduced with `$paramXXXX` and substituted at parse time.

## Component counts in type8/sol00 (canonical, from the Zoo README)

| Component type | Count |
|---|---|
| Lasers | 3 |
| Squeezers | **0** |
| Mirrors | 57 |
| Beam splitters | 13 |
| Faraday isolators | 1 |
| **Total free parameters** | **120** |

These are the authoritative numbers from `solutions/type8/sol00/README.md`. They contradict prior artifact-derived claims of "48 mirrors and 4 squeezers" — the truth is 57 mirrors and zero squeezers.
