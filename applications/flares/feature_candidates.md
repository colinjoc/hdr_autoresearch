# Feature Candidates

Domain quantities mapped to computable features from available data.

## Currently Used

| Feature | Source | Type | Notes |
|---------|--------|------|-------|
| AREA | Raw | Numerical | AR area in MSH |
| Longitude_extent | Raw | Numerical | Longitudinal extent in degrees |
| No_sunspots | Raw | Numerical | Sunspot count |
| MAGTYPE | Raw | Categorical → ordinal | Hale magnetic class, ordinal by complexity |
| McIntosh (zurich) | Derived | Categorical → codes | First letter of McIntosh |
| McIntosh (penumbral) | Derived | Categorical → codes | Second letter of McIntosh |
| McIntosh (compact) | Derived | Categorical → codes | Third letter of McIntosh |

## High-Value Candidates

| Feature | Derivation | Mechanism | Priority |
|---------|-----------|-----------|----------|
| log(AREA+1) | log transform | Linearizes 3-OOM range; better separates distributions (Hayes Fig 14) | HIGH |
| log(No_sunspots+1) | log transform | Same rationale | HIGH |
| AREA * MAGTYPE_ord | interaction | Large + complex = dangerous; requires 2 splits for tree | HIGH |
| |Latitude| | abs(Latitude) | Distance from equator; butterfly diagram physics | LOW |
| |Longitude| | abs(Longitude) | Central meridian distance; limb projection effects | MEDIUM |
| McIntosh full one-hot | one-hot(McIntosh) | Preserves 3-way interactions between sub-components | MEDIUM |
| MAGTYPE one-hot | one-hot(MAGTYPE) | Non-monotonic complexity relationships | MEDIUM |
| Zurich ordinal | A=0,B=1,...H=6 | Size/complexity ordering within Zurich class | MEDIUM |

## From AR_flare_ml_23_24_evol.csv (if dataset switched)

| Feature | Description | Priority |
|---------|-------------|----------|
| flared_yesterday | Binary: did this AR flare in previous 24h | HIGH |
| McIntosh_evolution | How McIntosh class changed from yesterday | HIGH |
| Previous day AR properties | Yesterday's area, sunspots etc. | MEDIUM |

## Literature-Sourced Candidates (computable from current data)

| Feature | Derivation | Mechanism | Source | Priority |
|---------|-----------|-----------|--------|----------|
| Zurich ordinal (A<B<...<F, H between A-B) | ordinal map | Size/complexity ordering; McIntosh 1990 | McIntosh 1990 | MEDIUM |
| Penumbral ordinal (X<R<S<A<H<K) | ordinal map | Penumbral area ordering; K=most complex | McIntosh 1990 | MEDIUM |
| Compactness ordinal (X<O<I<C) | ordinal map | Spot distribution compactness | McIntosh 1990 | LOW |
| Flare-history decay (Cdec) | sum(exp(-dt/tau)) per AR | Persistence/clustering of flare activity | Jonas 2018 | HIGH |
| AR age (days observed) | cumcount per noaa_ar | Young vs mature AR behavior | Falconer 2011 | MEDIUM |
| Area change rate | diff(AREA) per AR per day | Growing ARs more likely to flare | McCloskey 2018 | HIGH |
| Sunspot change rate | diff(No_sunspots) per AR | Evolution signals | McCloskey 2018 | MEDIUM |
| McIntosh evolution flag | McIntosh_today != McIntosh_yesterday | Upward evolution = higher rates | McCloskey 2018 | HIGH |
| log(Longitude_extent+1) | log transform | Same rationale as log(AREA) | Hayes 2021 | LOW |
| No_sunspots * MAGTYPE_ord | interaction | More spots + complex = more free energy | Toriumi & Wang 2019 | MEDIUM |

## From External Sources (not in dataset)

| Feature | Source | Priority |
|---------|--------|----------|
| SHARP magnetic parameters | SDO/HMI | HIGH (but not available) |
| GOES X-ray background | NOAA | MEDIUM |
| CME history | CDAW catalog | LOW |
| F10.7 radio flux | Solar cycle proxy | LOW |
