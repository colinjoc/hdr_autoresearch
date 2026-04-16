# Design variables — ABP decision-time project

This project is primarily descriptive-analytical (Option A data, not Option B simulation). The "design variables" are the levers we explore in Phase 2 to understand the data's structure. In Phase B, they become the scenario knobs.

## Data-cut levers (Phase 2 KEEP/REVERT space)

- **L01 temporal window**: {2015-2024, 2018-2024, 2019-2024, 2015-2019 pre-crisis, 2022-2024 post-crisis}
- **L02 case-type filter**: {all, normal-planning-appeals-only, SHD-only, SID-only, LRD-only, exclude-LA-own-development, exclude-referrals}
- **L03 outlier handling**: {raw, winsorise-top-1%, winsorise-top-5%, median-instead-of-mean}
- **L04 disposal-type filter**: {all-disposed, formal-only, exclude-otherwise-disposed}
- **L05 COVID handling**: {include, exclude-2020, exclude-2020-2021}
- **L06 board-crisis handling**: {include-2022-2024, exclude-2022-2023}
- **L07 case-complexity weight**: {uniform, weight-by-type-fixed-effects, weight-by-units-for-SHD}

## Model-specification levers

- **M01 model family**: {year-fixed-effects OLS, interrupted time series, capacity-queueing, M/M/1, M/G/1, case-type-FE panel OLS}
- **M02 intercept knots**: {2017 (SHD start), 2018 (Plean-IT), 2020 (COVID), 2022 (board crisis), Jul-2022 (Heather Hill), Nov-2022 (P&E List), Jun-2025 (ACP)}
- **M03 regressors**: {intake only, intake + FTE, intake + FTE + board-seats, intake + FTE + board-seats + JR-lag1, + case-type share}
- **M04 noise model**: {iid, AR(1), heteroskedastic}

## Phase B scenario levers

- **S01 staffing**: {status-quo 290 FTE, +20% = 348, +40% = 406}
- **S02 intake shock**: {-10% from 2024, 0%, +10%, +20%}
- **S03 case mix**: {2024-mix-frozen, shift-toward-LRD (housing policy), shift-toward-SID (infrastructure policy)}
- **S04 legislative effects**: {P&D-Act-2024-effective, partial, not-effective}

All levers are structured to be one-at-a-time changes, with interaction-sweep follow-ups.
