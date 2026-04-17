# Research Queue: IE Construction Cost Decomposition

## Status Key
- OPEN: Not yet tested
- RUN: Currently running
- KEEP: Tested, result kept
- REVERT: Tested, result reverted
- RETIRED: Cluster exhausted

## Hypotheses

| # | Hypothesis | Prior | Impact | Mechanism | Design Variable | Metric | Baseline | Status |
|---|-----------|-------|--------|-----------|----------------|--------|----------|--------|
| H01 | Concrete/cement CAGR > All-Materials CAGR | 0.70 | 7 | Non-tradeable, local demand driven | cement_cagr | CAGR % | 3.99% | KEEP (E01: 6.83%) |
| H02 | Steel CAGR highest among all materials | 0.60 | 7 | Globally traded, energy-intensive | steel_cagr | CAGR % | 3.99% | KEEP (E02: fabricated=8.20%) |
| H03 | Timber prices mean-revert after COVID spike | 0.65 | 6 | COVID oversupply correction | timber_cagr | post-peak % | 0% | KEEP (E03: -21%) |
| H04 | Insulation CAGR elevated by NZEB mandate | 0.75 | 8 | Regulatory demand shock | insulation_cagr | CAGR % | 3.99% | KEEP (E04: 2.31%, lower than expected) |
| H05 | Electrical fittings surge post-NZEB | 0.70 | 7 | Heat pump/solar mandate | electrical_cagr | CAGR % | 3.99% | KEEP (E05: 3.46%) |
| H06 | HVAC costs rising due to heat pump transition | 0.65 | 7 | Technology transition | hvac_cagr | CAGR % | 3.99% | KEEP (E06: 2.04%) |
| H07 | Plumbing costs above average | 0.50 | 5 | Import-dependent, exchange rate | plumbing_cagr | CAGR % | 3.99% | KEEP (E07: 4.08%) |
| H08 | Glass prices elevated by triple-glazing mandate | 0.60 | 7 | NZEB triple glazing | glass_cagr | CAGR % | 3.99% | KEEP (E08: 0.48%, surprise low) |
| H09 | Labour costs outpace materials 2015-2025 | 0.55 | 8 | Structural labour shortage | labour_cagr | CAGR % | 3.99% | KEEP (E09: 4.03%, near-parity) |
| H10 | Weekly hours declining (productivity signal) | 0.55 | 5 | Regulatory limits, gig shift | hours_change | % change | 0% | KEEP (E10: -1.1%) |
| H11 | Construction productivity declining | 0.60 | 7 | Employment vs output gap | emp_vs_output | ratio | 1.0 | KEEP (E11: 103% emp vs 9% output) |
| H12 | Materials grew faster than labour | 0.50 | 8 | Media narrative testing | mat_minus_lab | pp diff | 0 | KEEP (E12: -0.04pp, parity) |
| H13 | COVID caused >10% material price shock | 0.85 | 6 | Supply chain disruption | covid_peak | % change | 0% | KEEP (E13: +16%) |
| H14 | Ukraine shock exceeded COVID for cement | 0.60 | 6 | Energy price spike | ukraine_peak | % change | 0% | KEEP (E14: cement +32%) |
| H15 | Post-crisis costs are mean-reverting | 0.55 | 7 | Supply chain normalization | post_peak | % change | 0% | KEEP (E15: mixed) |
| H16 | Services trades are largest cost share | 0.70 | 6 | NZEB complexity | trade_share | % of total | - | KEEP (E16: mech+elec=24%) |
| H17 | Mechanical services largest single trade | 0.65 | 5 | Plumbing + HVAC complexity | largest_share | % | - | KEEP (E17: 14%) |
| H18 | Frame/steel dominates weighted contribution | 0.55 | 8 | High share x high inflation | weighted_contrib | pp | - | KEEP (E18: frame=0.57pp) |
| H19 | Top-5 materials explain >50% of inflation | 0.70 | 7 | Concentration risk | top5_share | % | - | KEEP (E19: 25%, below 50%) |
| H20 | NZEB adds >2pp excess inflation to affected materials | 0.75 | 9 | Regulatory demand shock | excess_pp | pp/yr | 0 | KEEP (E20: 2.3-5.1pp) |
| H21 | Materials-labour correlation > 0.8 | 0.60 | 5 | Shared demand drivers | pearson_r | correlation | 0 | OPEN |
| H22 | Energy-intensive materials hit harder by Ukraine | 0.80 | 6 | Energy cost transmission | ei_vs_ne | t-stat | 0 | KEEP (I02: not significant) |
| H23 | Copper pipes most volatile among pipe types | 0.55 | 4 | Global copper price | copper_vol | std dev | - | OPEN |
| H24 | Bituminous materials track oil prices | 0.70 | 5 | Oil derivative | oil_corr | correlation | 0 | OPEN |
| H25 | Precast concrete grew faster than ready-mix | 0.50 | 4 | Industrialisation trend | precast_vs_rmc | CAGR diff | 0 | OPEN |
| H26 | Sand/gravel prices stable (abundant local supply) | 0.65 | 3 | Domestic quarrying | sand_cagr | CAGR % | 3.99% | OPEN |
| H27 | Metal fittings CAGR above average | 0.55 | 4 | Import-dependent | metal_cagr | CAGR % | 3.99% | OPEN |
| H28 | Paint/varnish below average (competitive market) | 0.60 | 3 | Competitive supply | paint_cagr | CAGR % | 3.99% | OPEN |
| H29 | COVID affected timber more than any other material | 0.75 | 5 | Lumber supply chain | timber_covid | % change | 16% | OPEN |
| H30 | Seasonal patterns exist in material prices | 0.40 | 4 | Seasonal construction demand | seasonal_amp | amplitude | 0 | OPEN |
| H31 | VAR model outperforms univariate for price forecast | 0.50 | 6 | Cross-material dependencies | var_rmse | RMSE | ARIMA | OPEN |
| H32 | Granger causality: steel -> concrete | 0.45 | 5 | Input-output linkage | granger_p | p-value | 0.05 | OPEN |
| H33 | Material inflation peaks precede labour inflation peaks | 0.55 | 6 | Wage negotiation lag | lead_lag | months | 0 | OPEN |
| H34 | Dublin costs 10-15% above national average | 0.75 | 5 | Land + labour premium | dublin_premium | % | 0% | OPEN |
| H35 | Apartment costs > house costs by >30% | 0.70 | 5 | Structural complexity | apt_premium | % | 0% | OPEN |
| H36 | Substructure share declining over time | 0.40 | 3 | Standardisation | sub_trend | % change | 0% | OPEN |
| H37 | Services share increasing over time | 0.70 | 6 | NZEB complexity | svc_trend | % change | 0% | OPEN |
| H38 | Hardwood timber decoupled from softwood | 0.55 | 4 | Different markets | hw_sw_corr | correlation | 1.0 | OPEN |
| H39 | PVC pipes cheaper than copper (substitution) | 0.60 | 4 | Material substitution | pvc_vs_copper | CAGR diff | 0 | OPEN |
| H40 | Plaster CAGR driven by gypsum supply constraints | 0.50 | 4 | Supply concentration | plaster_driver | correlation | 0 | OPEN |
| H41 | All-Materials index tracks CPI + premium | 0.65 | 5 | General inflation plus sector premium | cpi_premium | pp | 0 | OPEN |
| H42 | Construction employment leads GDP by 1-2 quarters | 0.50 | 5 | Leading indicator | emp_gdp_lead | quarters | 0 | OPEN |
| H43 | Materials price volatility decreased post-2023 | 0.70 | 5 | Supply chain normalization | vol_change | std ratio | 1.0 | OPEN |
| H44 | Material price dispersion increased during COVID | 0.75 | 4 | Differential supply shock | disp_change | IQR ratio | 1.0 | OPEN |
| H45 | Ireland materials inflation > EU average post-Brexit | 0.45 | 6 | Supply chain disruption | ie_vs_eu | pp diff | 0 | OPEN |
| H46 | Construction output more volatile than overall GDP | 0.80 | 4 | Pro-cyclical sector | vol_ratio | std ratio | 1.0 | OPEN |
| H47 | Real materials costs (deflated) are flat | 0.50 | 6 | Inflation vs real cost | real_cagr | CAGR % | 0% | OPEN |
| H48 | Subcontracting rates exceed direct employment growth | 0.60 | 5 | Industry structure shift | subcont_ratio | growth % | 0% | OPEN |
| H49 | BCAR added >€3000 per dwelling in soft costs | 0.55 | 5 | Certification requirement | bcar_cost | EUR | 0 | OPEN |
| H50 | Part V obligation adds 5-10% to development cost | 0.60 | 5 | Social housing levy | part_v_pct | % | 0% | OPEN |
| H51 | Development levies increased faster than inflation | 0.55 | 4 | Local authority revenue | levy_cagr | CAGR % | CPI | OPEN |
| H52 | Finance costs rose with interest rate hikes 2022-2024 | 0.80 | 6 | ECB rate transmission | finance_change | pp | 0 | OPEN |
| H53 | Professional fees as % of cost are constant | 0.50 | 3 | Market competition | fees_trend | % change | 0% | OPEN |
| H54 | Modular construction reduces material cost variability | 0.40 | 5 | Factory production | modular_vol | std ratio | 1.0 | OPEN |
| H55 | BER A rating adds measurable cost premium | 0.65 | 6 | Energy specification | ber_premium | % | 0% | OPEN |
| H56 | Heat pump installation cost declining over time | 0.45 | 5 | Technology learning curve | hp_cost_trend | % change | 0% | OPEN |
| H57 | Solar PV material costs declining | 0.60 | 4 | Global scale economies | pv_trend | % change | 0% | OPEN |
| H58 | Timber frame houses have lower material cost variance | 0.45 | 4 | Standardised system | tf_vol | std ratio | 1.0 | OPEN |
| H59 | Block-build costs converging with timber frame | 0.40 | 4 | Insulation requirements levelling | convergence | CAGR diff | 0 | OPEN |
| H60 | Crane hire costs proxy for capacity utilisation | 0.50 | 4 | Demand indicator | crane_corr | correlation | 0 | OPEN |
| H61 | Concrete products more concentrated than steel | 0.55 | 4 | Market structure | hhi_diff | HHI ratio | 1.0 | OPEN |
| H62 | Weather affects seasonal construction output | 0.70 | 3 | Outdoor work dependency | weather_corr | correlation | 0 | OPEN |
| H63 | COVID construction site closures lasted >3 months | 0.80 | 4 | Policy documentation | closure_months | months | 0 | OPEN |
| H64 | Ukraine effect transmitted via energy not supply chain | 0.65 | 5 | Energy cost mechanism | energy_corr | correlation | 0 | OPEN |
| H65 | Post-2019 builds more expensive than pre-2019 (NZEB) | 0.75 | 6 | Regulatory step change | cost_step | % change | 0% | OPEN |
| H66 | EPC rating impacts resale value | 0.60 | 4 | Market valuation | epc_premium | % | 0% | OPEN |
| H67 | Labour productivity varies by trade | 0.70 | 5 | Specialisation effects | prod_by_trade | ratio | 1.0 | OPEN |
| H68 | Apprenticeship completions predict labour cost | 0.50 | 5 | Supply pipeline | app_corr | correlation | 0 | OPEN |
| H69 | Immigration affects construction labour supply | 0.60 | 5 | Labour supply shock | immig_corr | correlation | 0 | OPEN |
| H70 | Building commencements predict material demand | 0.65 | 4 | Demand leading indicator | commence_lead | months | 0 | OPEN |
| H71 | Planning permission volume predicts cost inflation | 0.50 | 5 | Demand pressure | perm_cost_corr | correlation | 0 | OPEN |
| H72 | Cement has lowest import penetration | 0.75 | 3 | Non-tradeable | import_pct | % | - | OPEN |
| H73 | Steel fabrication premium reflects labour intensity | 0.60 | 4 | Labour content | fab_premium | % | 0% | OPEN |
| H74 | Roofing costs dominated by timber + insulation | 0.65 | 3 | Trade composition | roof_comp | % | - | OPEN |
| H75 | Window costs dominated by glass (triple glazing) | 0.60 | 4 | Material intensity | window_comp | % | - | OPEN |
| H76 | Preliminary costs (site overhead) grew faster than trade costs | 0.50 | 4 | Compliance complexity | prelim_vs_trade | CAGR diff | 0 | OPEN |
| H77 | All-Materials index has unit root (non-stationary) | 0.80 | 4 | Trended price series | adf_p | p-value | 0.05 | OPEN |
| H78 | COVID shock was permanent for some materials | 0.55 | 6 | Hysteresis | perm_shift | % | 0% | OPEN |
| H79 | Materials with highest CAGR also have highest volatility | 0.60 | 4 | Risk-return relationship | cagr_vol_corr | correlation | 0 | OPEN |
| H80 | Concrete aggregate (sand/gravel + cement + RMC) largest cost group | 0.65 | 5 | Cost concentration | agg_share | % | - | OPEN |
| H81 | Cost decomposition varies by house type (terrace vs detached) | 0.55 | 5 | Specification differences | type_variation | % diff | 0% | OPEN |
| H82 | Regional cost variation > 15% nationally | 0.70 | 5 | Labour/transport differences | regional_spread | % | 0% | OPEN |
| H83 | Cost per sqm inversely related to house size | 0.65 | 4 | Fixed cost spreading | size_elasticity | coefficient | 0 | OPEN |
| H84 | Second-fix trades (finishes, fittings) grow slower than first-fix | 0.50 | 4 | Competitive supply | fix_comparison | CAGR diff | 0 | OPEN |
| H85 | Wet trades (plastering, concrete) grow faster than dry trades | 0.55 | 4 | Labour intensity | wet_vs_dry | CAGR diff | 0 | OPEN |
| H86 | Inflation transmission: cement -> concrete products (1-2 month lag) | 0.60 | 5 | Input-output chain | cement_concrete_lag | months | 0 | OPEN |
| H87 | Steel price mean-reverts faster than cement | 0.65 | 5 | Global vs local markets | reversion_speed | half-life | - | OPEN |
| H88 | Material price clustering: 3-4 groups with distinct dynamics | 0.55 | 6 | Factor structure | n_clusters | count | - | OPEN |
| H89 | PCA loadings identify energy-intensive vs labour-intensive groups | 0.60 | 6 | Factor interpretation | loading_groups | qualitative | - | OPEN |
| H90 | Weighted cost contribution rankings differ from CAGR rankings | 0.70 | 7 | Share x growth interaction | rank_diff | Spearman rho | 1.0 | OPEN |
| H91 | 2025 materials inflation below 2% (deceleration) | 0.65 | 4 | Supply normalization | 2025_yoy | % | 3.99% | OPEN |
| H92 | Labour cost acceleration post-2022 exceeds materials | 0.60 | 6 | Wage spiral | lab_accel | CAGR diff | 0 | OPEN |
| H93 | Construction is most pro-cyclical NACE sector | 0.70 | 4 | Business cycle sensitivity | beta | coefficient | 1.0 | OPEN |
| H94 | Site works cost share increasing (environmental requirements) | 0.50 | 3 | Environmental regulation | site_trend | % change | 0% | OPEN |
| H95 | Material cost forecasts from VAR outperform random walk | 0.45 | 5 | Forecasting value | forecast_skill | RMSE ratio | 1.0 | OPEN |
| H96 | Structural break at Brexit (Jan 2021 for traded materials) | 0.40 | 5 | Trade disruption | brexit_break | p-value | 0.05 | OPEN |
| H97 | COVID and Ukraine shocks are distinguishable in PCA space | 0.55 | 5 | Shock characterization | pc_separation | distance | 0 | OPEN |
| H98 | Apartment construction has different cost driver ranking | 0.60 | 5 | Building type variation | apt_ranking | Spearman rho | 1.0 | OPEN |
| H99 | Material substitution reduces cost (PVC for copper) | 0.50 | 4 | Substitution economics | subst_saving | % | 0% | OPEN |
| H100 | Total cost per dwelling increased faster than per-sqm cost | 0.55 | 5 | Size creep or specification | per_dwelling_cagr | CAGR diff | 0 | OPEN |
