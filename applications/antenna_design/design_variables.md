# Antenna Design Variables

This document enumerates the design variables the HDR loop iterates on. Each entry gives typical ranges, the effect on gain / bandwidth / efficiency, and references (paper ids from `papers.csv`).

Symbols: `L` = length, `W` = width, `h` = substrate height, `epsilon_r` = relative permittivity, `tan(delta)` = loss tangent, `lambda_0` = free-space wavelength at centre frequency, `lambda_d` = guided wavelength in substrate.

---

## 1. Target Operating Point (required for all topologies)

| Variable | Symbol | Typical Range | Notes |
|----------|--------|---------------|-------|
| Centre frequency | f0 | 0.3--100 GHz (UHF to mmWave) | Primary design constraint |
| Fractional bandwidth | BW/f0 | 1% (narrowband patch) to 100%+ (UWB slot) | Depends on topology |
| Target gain | G | 2--30+ dBi | Patches 2--8; horns 10--25; arrays 15--30+ |
| Target S11 | S11_max | < -10 dB in-band | Equivalent to VSWR < 2:1 |
| Target impedance | Z0 | 50 ohm (default), 75 ohm (video/RF) | Feed-line match requirement |
| Polarisation | pol | linear (V or H), circular (LHCP/RHCP), elliptical | Axial ratio < 3 dB for CP |

---

## 2. Microstrip Patch Antenna

The rectangular patch resonant in the TM10 mode is the most parametrically simple topology and the default starting point for ML-surrogate studies [1, 13, 18, 94, 95].

| Variable | Symbol | Typical Range | Effect on Performance |
|----------|--------|---------------|-----------------------|
| Patch length | L | 0.3--0.49 lambda_d | Sets resonant frequency; L ~ lambda_d/2. Longer L -> lower f0. |
| Patch width | W | 0.5--1.5 lambda_0 | Affects radiation resistance and bandwidth. Wider W -> higher BW and gain, lower input impedance. |
| Substrate height | h | 0.003--0.05 lambda_0 | Thicker substrate -> wider BW and higher efficiency, but promotes surface waves at high h. |
| Substrate permittivity | epsilon_r | 2.2--10.2 (see table below) | Higher epsilon_r -> smaller patch but narrower BW and lower efficiency. |
| Loss tangent | tan(delta) | 0.0001--0.02 | Directly reduces eta_rad; critical above 1 GHz. |
| Inset-feed depth | y0 | 0--L/2 | Tunes input impedance from edge (~200--300 ohm) to centre (~0 ohm). Matches to 50 ohm typically at y0 ~ L/3. |
| Inset-feed width | W_f | 0.5--3 mm | Sets feed-line characteristic impedance. |
| Ground plane size | L_g, W_g | >= L+6h, W+6h (Balanis rule) | Finite ground reduces gain and shifts f0. |
| Patch-to-ground offset | --- | centred | Offset feeding introduces asymmetry and cross-pol. |

References: [1, 13, 18, 94, 95, 96, 120]

### 2.1 Derived / advanced patch variables

| Variable | Symbol | Effect |
|----------|--------|--------|
| Slot length (U-slot, E-slot) | L_s | Introduces second resonance -> wider BW or dual-band. |
| Slot width | W_s | Fine-tunes notch depth and bandwidth. |
| Stacked parasitic patch h2 | h2 | Adds resonance -> wider BW (10--25%). |
| Shorting pin radius, position | r_pin, (x, y) | Shrinks footprint (PIFA), adds tuning. |

---

## 3. Slot Antennas

Slot antennas realise wideband or multiband behaviour via aperture geometry [19, 22, 80, 81].

| Variable | Symbol | Typical Range | Effect |
|----------|--------|---------------|--------|
| Slot length | L_slot | 0.3--0.5 lambda_0 | Primary resonance |
| Slot width | W_slot | 0.01--0.1 lambda_0 | Controls impedance and BW |
| Slot position (x, y) | --- | within ground plane | Tunes coupling |
| Ground plane dimensions | L_g, W_g | 0.5--2 lambda_0 | Affects pattern and back-radiation |
| Annular slot radius | r_slot | 0.1--0.3 lambda_0 | Circular-polarisation ring-slot designs |
| Fractal iteration order | n_iter | 1--4 | Higher order -> more resonances, multiband |
| Feed type | --- | microstrip, CPW, stripline | Affects BW and fabrication complexity |

---

## 4. Array Antennas

Linear, planar, and conformal arrays require element-level and array-level design variables [4, 14, 22, 90].

| Variable | Symbol | Typical Range | Effect |
|----------|--------|---------------|--------|
| Number of elements | N | 2--256+ | Directivity scales as ~N (linear array); larger N -> higher gain, narrower main beam. |
| Element spacing | d | 0.4--0.9 lambda_0 | d = 0.5 lambda_0 minimises mutual coupling and avoids grating lobes for broadside arrays. |
| Element amplitude weights | a_n | Dolph-Chebyshev, Taylor, binomial | Tapering trades main-beam width against sidelobe level. |
| Element phase weights | phi_n | progressive or arbitrary | Steers beam; phased arrays use phi_n = -k d n sin(theta_0). |
| Array lattice | --- | rectangular, triangular, hexagonal | Triangular lattice needs fewer elements for same grating-lobe suppression. |
| Mutual coupling suppression | --- | EBG, DGS, decoupling networks | Target isolation > 25 dB for MIMO [22]. |
| Feed network type | --- | corporate, series, Butler matrix | Corporate = broader BW, series = simpler, Butler = fixed multi-beam. |
| Subarray grouping | --- | 1--16 elements per subarray | Trades RF-chain count against steering flexibility. |

---

## 5. Topology Choice (categorical design variable)

| Topology | Typical Gain | Typical BW | Typical Efficiency | Notes |
|----------|--------------|------------|--------------------|-------|
| Half-wave dipole | 2.15 dBi | 10% | > 95% | Canonical reference |
| Quarter-wave monopole (over GP) | 5.15 dBi | 10% | ~95% | Uses image theory |
| Patch (rect.) | 2--8 dBi | 1--5% | 80--95% | Planar, easy fab |
| Patch (wideband: U-slot, stacked) | 5--9 dBi | 10--25% | 80--90% | Wider via BW techniques |
| Slot (rectangular) | 3--6 dBi | 5--20% | 80--95% | Complementary to patch |
| Slot (fractal / UWB) | 4--10 dBi | 100%+ (13:1 demonstrated) | 85--95% | Super-wideband [19] |
| Horn (pyramidal, conical) | 10--25 dBi | 20:1 | 40--80% (aperture) | High-gain, bulky |
| Yagi-Uda | 6--12 dBi | 10% | > 90% | Directive, narrow BW |
| Helix (axial mode) | 10--15 dBi | 70% | 90% | Circular polarisation |
| Log-periodic dipole | 6--10 dBi | 10:1 | > 90% | Very broad BW |
| Dielectric resonator antenna (DRA) | 5--10 dBi | 10--20% | > 95% | No conductor loss; mmWave [20] |
| Metasurface antenna / RIS | 15--30 dBi | 10--20% | Varies | Reconfigurable, beam-steering [24, 46, 92] |
| Fractal (Koch, Sierpinski, Minkowski) | 2--6 dBi | multiband | > 85% | Miniaturisation + multiband [16, 97, 98, 99] |
| Meandered monopole | 2--4 dBi | 5--15% | 70--90% | Size reduction for IoT [125] |
| PIFA (inverted-F) | 2--5 dBi | 5--20% | 80--95% | Mobile-device staple |

---

## 6. Materials

### 6.1 Conductors

| Material | Conductivity (S/m) | Use |
|----------|--------------------|----|
| Copper | 5.8 x 10^7 | Default for patches, feeds |
| Silver | 6.3 x 10^7 | Highest sigma; expensive |
| Aluminium | 3.5 x 10^7 | Lightweight, aerospace |
| Gold | 4.1 x 10^7 | MMIC, corrosion resistance |
| Conductive ink | 10^6--10^7 | Printed/conformal antennas [23, 77, 78] |

### 6.2 Dielectric substrates (from literature review section 1.4)

| Material | epsilon_r | tan(delta) | Cost | Use Case |
|----------|-----------|------------|------|----------|
| FR4 | 4.2--4.7 | 0.02 | Low | Prototyping, sub-GHz |
| Rogers RT/duroid 5880 | 2.2 | 0.0009 | High | mmWave, low-loss |
| Rogers RO4003C | 3.38 | 0.0027 | Medium | General microwave |
| Rogers RO3010 | 10.2 | 0.0023 | High | Miniaturisation |
| Alumina (Al2O3) | 9.8 | 0.0001 | High | mmWave, DRA |
| Teflon (PTFE) | 2.1 | 0.0004 | Medium | Low-loss, flexible |
| Polyimide (Kapton) | 3.4 | 0.002 | Medium | Flexible/wearable |
| Air / foam | 1.0--1.1 | ~0 | Low | Widest BW, lowest epsilon |

References: [1, 3, 20, 40, 41]

---

## 7. Pixelated / Topology-Level Design Variables

For inverse design and topology optimisation the design variables become the binary (or continuous) occupancy of pixels in a design domain [34, 67, 68, 69, 70, 71].

| Variable | Typical Value | Notes |
|----------|---------------|-------|
| Grid resolution | 10x10 to 100x100 | 10x10 standard in ML surrogates [34, 71]; higher needs adjoint [65, 66, 67] |
| Pixel size | 0.02--0.1 lambda_0 | Smaller than feature of interest |
| Design domain extent | 0.5--2 lambda_0 per side | Constrained by overall footprint |
| Pixel state | binary (metal/substrate) or continuous [0, 1] | Continuous for SIMP; binary for BPSO/GA |
| Symmetry constraint | none, 1-axis, 2-axis, 4-fold | Reduces search space by 2x--8x |
| Min feature size | >= 2 pixels | Manufacturing constraint |

---

## 8. Miscellaneous Global Variables

| Variable | Typical Range | Effect |
|----------|---------------|--------|
| Operating temperature | -40 to +85 C | Shifts epsilon_r and conductor resistivity |
| Fabrication tolerance sigma | 10--100 um | Drives yield-aware optimisation [75, 76] |
| Encapsulation layer h_enc | 0--1 mm | Shifts f0; must be modelled for radomes |
| Feed connector type | SMA, MMCX, waveguide flange | Introduces discontinuity at feed point |

---

## 9. Variable Importance / Sensitivity (from literature)

Global sensitivity analysis studies [40, 76] consistently identify the following as the highest-leverage variables for microstrip patch designs:

1. Patch length L (dominates f0)
2. Substrate permittivity epsilon_r (dominates f0 and BW)
3. Substrate height h (dominates BW and eta_rad)
4. Feed position y0 (dominates S11 match)
5. Patch width W (secondary effect on BW and gain)

Insensitive parameters (ground plane size beyond Balanis rule, corner radius, dielectric above 3h from patch) are typically fixed during surrogate optimisation to reduce dimensionality [39, 40, 41].
