# Design Variables — JR Tax on Housing Supply

This is a synthesis/decomposition project (Option C). The design variables are the attribution shares and scenario parameters used to decompose the observed housing delay into JR-attributable and non-JR components.

## Primary Design Variables

| Variable | Range | Default | Source |
|----------|-------|---------|--------|
| JR attribution share (indirect) | 0.0 - 0.5 | 0.25 | Channel bounds from literature |
| Outcome weight (quashed/conceded) | 0.5 - 1.0 | 1.0 | Full delay for state losses |
| Outcome weight (refused/dismissed) | 0.0 - 0.5 | 0.5 | Partial delay (uncertainty) |
| Outcome weight (upheld) | 0.0 - 0.5 | 0.25 | Minimal delay (JR resolved quickly) |
| Imputed units (unstated cases) | 100 - 400 | 200 | SHD minimum to median grant size |
| Remittal time (months) | 12 - 24 | 18 | Typical re-application period |
| Holding cost (EUR/unit/month) | 300 - 2000 | 500 | Finance-only to full opportunity |
| Construction inflation (annual) | 0.04 - 0.10 | 0.07 | SCSI range 2018-2024 |
| Housing share of ABP cases | 0.30 - 0.50 | 0.40 | ABP case-type breakdown |
| Baseline SOP weeks | 16 - 20 | 18 | Pre-2018 ABP mean |

## Scenario Parameters (Phase B)

| Scenario | JR share | Imputed units | Holding cost |
|----------|----------|---------------|--------------|
| Lower bound | 0.0 | 100 | 300 |
| Central | 0.25 | 200 | 500 |
| Upper bound | 0.50 | 400 | 2000 |
