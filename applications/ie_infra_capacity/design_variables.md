# Design Variables: U-3 Infrastructure Capacity Blocks

This is a descriptive/decomposition project (Option C). The "design variables" are the analytical choices that affect the headline finding.

## Primary Design Variables

| Variable | Range | Default | Effect on Headline |
|----------|-------|---------|-------------------|
| AMBER classification | {blocked, available} | blocked | ±570 ha (12.1% vs 19.3% of zoned land) |
| Spatial aggregation level | {county, settlement} | county | 0 pp difference (validated E06) |
| Zoned land allocation method | {population-weighted, equal, regional} | population-weighted | Affects county-level estimates |
| Planning register scope | {all, residential only, multi-unit only} | residential only | Affects demand-side measures |
| Time window | {all years, 2015+, 2020+} | all years | Affects temporal trend analysis |
| One-off house treatment | {include, exclude} | include | Affects total application counts |
| County boundary matching | {exact, fuzzy} | exact via PA mapping | Minor edge effects |

## Secondary Design Variables

| Variable | Range | Default | Notes |
|----------|-------|---------|-------|
| Goodbody total zoned ha | {6329, 7911, 9493} | 7911 | ±20% sensitivity range |
| U-2 viability threshold | {0.73, 0.83, 0.93} | 0.83 | From U-2 sensitivity analysis |
| RED threshold for county classification | {20%, 30%, 50%} | varies by analysis | E02 uses 30% and 50% |
| Plant size classification | {D-prefix, PE>2000, PE>5000} | D-prefix | Proxy for UWWTD applicability |
| Constraint level bins | {<15%/<30%/<100%} | as specified | E04 grouping |

## Fixed Parameters

| Parameter | Value | Source |
|-----------|-------|--------|
| Total WWTPs | 1,063 | Uisce Éireann register |
| Counties covered | 29 | Register scope |
| National zoned ha | 7,911 | Goodbody 2021 |
| U-2 viability stranded pct | 83% | Predecessor study |
| U-1 apps per ha per yr | 4.8 | Predecessor study |
