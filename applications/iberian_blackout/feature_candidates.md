# Feature Candidates: Iberian Blackout Cascade Prediction

## Physics-Informed Proxies

### 1. System Inertia Proxy
- **Formula**: H_proxy = (nuclear + gas + coal + 0.7*hydro) / total_generation
- **Physics**: Synchronous machines provide rotational inertia; higher inertia = slower frequency deviation after perturbation
- **Expected effect**: Lower inertia correlates with higher risk, but ENTSO-E report says not primary cause
- **Source**: REE generation by technology

### 2. Voltage Stress Proxy
- **Formula**: V_stress = mean(solar_fraction, excess_gen_ratio_norm, neg_price_indicator, export_fraction)
- **Physics**: Lightly loaded transmission lines have higher voltage; high solar = capacitive injection; exports remove load
- **Expected effect**: Higher voltage stress = higher overvoltage cascade risk (PRIMARY mechanism)
- **Source**: REE generation, demand, exchange, prices

### 3. Reactive Power Gap Proxy
- **Formula**: Q_gap = (1 - sync_fraction) * solar_fraction - 0.3 * wind_fraction * (1 - sync_fraction)
- **Physics**: Solar in fixed PF mode provides no dynamic Q support; wind (DFIG) provides partial Q support
- **Expected effect**: Larger gap = less voltage control authority
- **Source**: REE generation by technology

### 4. Demand-Generation Mismatch
- **Formula**: excess_gen = total_generation / (demand * 24)
- **Physics**: Oversupply = low dispatch of voltage-supporting thermal units
- **Source**: REE generation + demand

### 5. Export Intensity
- **Formula**: export_fraction = |net_exports| / total_generation
- **Physics**: Heavy exports = power flowing through transmission corridors = reactive power losses; weakens voltage profile
- **Source**: REE interconnector flows

### 6. Price Floor Indicator
- **Formula**: Binary: price_min < 0
- **Physics**: Negative prices indicate extreme oversupply; market dispatches cheapest (non-synchronous) units; thermal units shut down or reduce output, removing inertia and voltage support
- **Source**: REE market prices

### 7. Interaction Features
- **solar_x_low_sync**: voltage_stress * (1 - inertia_proxy) — captures joint risk
- **reactive_x_export**: reactive_gap * export_fraction — captures Q deficit amplified by exports

## Temporal Features
- Day of week (weekend/weekday affects demand pattern)
- Month (seasonal solar resource intensity)

## Derived Statistical Features
- Rolling 7-day average of renewable fraction
- Rate of change in solar fraction (how fast is penetration increasing?)
- Demand coefficient of variation (CV) — unstable loads
- Price volatility (rolling std)

## Features NOT Available Without Enhanced Data
- Sub-second frequency measurements
- Transmission line loading (%)
- Reactive power flows (MVAr)
- Generator excitation state (over/under)
- Protection relay settings
- Shunt reactor connection status
