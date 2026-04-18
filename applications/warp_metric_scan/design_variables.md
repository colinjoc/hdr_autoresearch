# Design Variables

## Primary Design Variables

| Variable | Symbol | Range | Framework | Physical Meaning |
|----------|--------|-------|-----------|-----------------|
| Bubble velocity | v | 0.01 - 5.0 c | All | Warp bubble coordinate velocity |
| KK coupling | alpha | -2.0 to 2.0 | F2 | Extra-dimension radius modulation by bubble |
| f(R) coefficient | alpha_R2 | 0.01 to 10.0 | F3 | Starobinsky R^2 correction strength |
| Spin density | s_0 | 0 to 10^20 | F4 | Spin angular momentum density in bubble wall |
| Torsion profile width | sigma_S | 0.1 to 2.0 | F4 | Width of torsion concentration in bubble wall |
| Brane tension | lambda | 10^4 to 10^20 | F5 | RS brane tension (controls high-energy corrections) |
| Bulk Weyl amplitude | C_W | -10 to 10 | F5 | Amplitude of projected Weyl tensor contribution |
| Bubble wall thickness | delta | 0.1 to 2.0 | All | Width parameter of shape function gradient |

## Derived Quantities

| Quantity | Formula | Units |
|----------|---------|-------|
| G_00 minimum | min over bubble wall | dimensionless (geometric units) |
| Effective energy density rho_eff | G_00 / (8 pi G) | kg/m^3 |
| WEC satisfaction fraction | fraction of grid points with G_00 >= 0 | dimensionless |
| NEC violation magnitude | min(G_00 + G_11) | dimensionless |
| KK contribution | G_00(5D, alpha) - G_00(4D) | dimensionless |
| f(R) correction | Delta G_00 from R^2 terms | dimensionless |
| Torsion contribution | H_00 from spin density | dimensionless |
| Weyl projection | E_00 on brane | dimensionless |
