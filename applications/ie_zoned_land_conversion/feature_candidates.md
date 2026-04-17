# Feature Candidates: IE Zoned Land Conversion

## Features (computable from available data)

| # | Feature | Source | Justification |
|---|---------|--------|---------------|
| 1 | Residential permission applications per LA per year | National Planning Register | Direct outcome measure |
| 2 | Total applications per LA per year | National Planning Register | Broader measure of planning activity |
| 3 | Approval rate per LA per year | National Planning Register (granted/decided) | Regulatory permissiveness |
| 4 | Refusal rate per LA per year | National Planning Register (refused/decided) | Regulatory stringency |
| 5 | Median decision lag (days) per LA | National Planning Register (ReceivedDate → DecisionDate) | Processing speed / deterrent |
| 6 | One-off housing proportion per LA | National Planning Register (One-Off House field) | Infrastructure/urbanisation proxy |
| 7 | Mean units per application per LA | National Planning Register (NumResidentialUnits) | Application scale |
| 8 | Large scheme count (50+ units) per LA per year | National Planning Register | Market-led supply indicator |
| 9 | Apartment vs house proportion per LA | National Planning Register (description keywords) | Housing type mix |
| 10 | Zoned residential land area per LA (ha) | Goodbody 2024, allocated by population | Supply side |
| 11 | Zoned land per region (ha) | Goodbody 2024 | Regional supply |
| 12 | Median zoned land price per hectare | CSO RZLPA02 | Land cost signal |
| 13 | Property sale price (median) | CSO HPA09 | Revenue side of viability |
| 14 | Viability ratio (sale price / construction cost) | Computed | Development economics |
| 15 | Population per LA | CSO Census 2022 | Demand proxy |
| 16 | Population density per LA | Derived from Census | Urbanisation level |
| 17 | Year (time) | Calendar | Trend / policy regime |
| 18 | Quarter | Calendar | Seasonality |
| 19 | Pre/post RZLT announcement (2022) | Binary | Policy shock |
| 20 | Pre/post COVID (2020) | Binary | Exogenous shock |
| 21 | Dublin vs non-Dublin | Binary | Capital effect |
| 22 | Region (NUTS 3 → Goodbody) | Categorical | Regional fixed effect |
| 23 | Withdrawal rate per LA | National Planning Register | Planning system friction |
| 24 | Further Information request rate per LA | National Planning Register (FIRequestDate non-null) | Information cost |
| 25 | Extension of Duration count per LA | National Planning Register (Application Type) | Stalled project indicator |

## Features (not computable, require additional data)

| # | Feature | Required Data | Priority |
|---|---------|---------------|----------|
| 26 | Water infrastructure capacity per LA | Irish Water connection reports | High |
| 27 | Development contribution rates per LA | LA development contribution schemes | High |
| 28 | Landowner count per zoned hectare | Property registration data | High |
| 29 | Average parcel size of zoned land | GIS land parcel data | Medium |
| 30 | Construction cost index by region | SCSI/CSO | Medium |
| 31 | Mortgage drawdown rates by LA | Central Bank / BPFI | Medium |
| 32 | Net migration by LA | CSO intercensal estimates | Low |
| 33 | Employment density by LA | CSO QNHS | Low |
