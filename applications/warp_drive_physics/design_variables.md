# Design Variables: Warp Drive Physics

## Primary Design Variables

| Variable | Symbol | Range | Physical Meaning |
|:---|:---|:---|:---|
| Warp velocity | v_s | 0 to >> c | Speed of the warp bubble |
| Bubble radius | R | 1 m to 1000 m | Size of the warp region |
| Bubble wall thickness | sigma^{-1} | l_Planck to R | Transition region width |
| Shell mass | M | 0 to ~M_sun | ADM mass of matter shell |
| Inner radius | R_1 | 1 m to R | Passenger region radius |
| Outer radius | R_2 | R_1 to 10*R_1 | Shell outer boundary |
| Shape function | f(r_s) | [0, 1] | Top-hat profile for shift |
| Shift vector magnitude | beta^x | 0 to v_s | Frame-dragging component |
| Lapse function | alpha | 0 to 1 | Gravitational time dilation |

## Secondary Design Variables

| Variable | Symbol | Range | Physical Meaning |
|:---|:---|:---|:---|
| Spatial metric components | gamma_ij | delta_ij + perturbation | Non-flat spatial geometry |
| Density profile | rho(r) | 0 to rho_max | Matter distribution in shell |
| Pressure profile | P(r) | 0 to P_max | TOV equilibrium pressure |
| Anisotropy | P_tangential/P_radial | 0.1 to 10 | Hoop stress in shell |
| Smoothing parameter | s | 1 to 100 | Boundary regularisation |
| Cosmological constant | Lambda | -10^{-52} to 10^{-52} m^{-2} | Background curvature |

## Derived Quantities (Observables)

| Quantity | Formula/Method | Unit |
|:---|:---|:---|
| Eulerian energy density | E = (1/16piG)(K^2 - K_ij K^ij) | J/m^3 |
| Exotic matter mass | M_exotic = integral of E dV where E < 0 | kg |
| NEC evaluation | T_mu_nu k^mu k^nu for all null k | J/m^3 |
| WEC evaluation | T_mu_nu V^mu V^nu for all timelike V | J/m^3 |
| SEC evaluation | (T_mu_nu - T/2 g_mu_nu)V^mu V^nu | J/m^3 |
| DEC evaluation | -T^mu_nu V^nu is causal | dimensionless |
| Time delay | delta_t between counter-propagating light rays | seconds |
| ADM mass | M_ADM = surface integral at infinity | kg |
