# Feature candidates — ABP decision-time models

Every feature listed here is a candidate predictor or covariate in Phase 1/2 regressions. Each is accompanied by its expected sign and the mechanism argument.

| Feature | Unit | Source | Sign on W | Mechanism |
|---|---|---|---|---|
| intake_year | cases/yr | ABP Table 1 | + | Capacity-constrained; more intake ⇒ longer queue ⇒ longer W |
| backlog_start_year | cases | ABP Table 1 | + | Little's law: W = L/λ; bigger L ⇒ bigger W |
| fte_total | persons | ABP annual report | – | More throughput capacity ⇒ lower W |
| board_members | persons | ABP annual report | – | Decision nodes in the pipeline; fewer members ⇒ bottleneck |
| share_shd_in_disposed | frac 0-1 | ABP Table 2 | + | SHD cases are 2-3× slower than appeals |
| share_sid_in_disposed | frac 0-1 | ABP Table 2 | + | SID cases are 2× slower than appeals |
| share_lrd_in_disposed | frac 0-1 | ABP quarterly | – (for 2024+) | LRD cases run at 13-week cycle, pulling mean down |
| share_otherwise_disposed | frac 0-1 | ABP Table 3 | – | Withdrawals and invalidations dispose in weeks, not months |
| post_heather_hill | bool | P034 | ? | Locus-standi narrowing; hypothesis is ambiguous sign |
| post_pe_list | bool | P041 | – | P&E List reduces JR-remittal delay channel |
| post_acp | bool | P028 | – (aspirational) | ACP transition + new statutory timelines; effect expected 2026+ |
| jr_lodgement_rate_lag1 | frac | PL-2 JR tallies | + | JR pressure makes ABP write longer inspector reports |
| quarter_fe | factor | — | — | Seasonal effects in Q1/Q4 disposals |
| covid_year | bool | 2020-2021 | ? | Disposal mix shift |
| ρ_proxy | dimensionless | λ/μ | + | Kingman heavy-traffic: W explodes as ρ→1 |
| log_intake | log(cases) | — | + | Captures non-linear queueing effect |
| board_vacancy_rate | frac | annual report | + | Fewer board members ⇒ longer case-approval queue |
| inspector_count | persons | annual report | – | Capacity of case processing |

## Target variables

- **Primary**: mean weeks-to-dispose, all cases, year (2015-2024) — from ABP Table 2 "All" column.
- **Primary alt**: % SOP compliance, all cases, year — from ABP Table 1 line "Disposed of within statutory objective period".
- **Secondary**: case-type-specific mean weeks (Normal Planning Appeals, SID, SHD, All Other).
- **Tertiary (Phase B)**: predicted weeks-to-dispose 2026-2028 under scenarios.
