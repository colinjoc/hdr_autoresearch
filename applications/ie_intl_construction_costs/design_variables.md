# Design Variables: Irish International Construction Cost Comparison

This is an Option C (Decomposition-Based) project. The "design variables" are the dimensions along which we decompose and compare construction costs.

## Primary Design Variables

1. **Country** (categorical, 11 levels): AT, BE, DE, DK, ES, FI, FR, IE, NL, SE, UK
2. **Time period** (quarterly, 2015-Q1 to 2025-Q4): 44 quarters of observation
3. **Subperiod regime** (categorical, 4 levels): Pre-COVID, COVID, Ukraine/Energy, Recovery
4. **Index type** (categorical, 2 levels): PRC_PRR (producer prices) vs COST (input costs)
5. **Base year** (categorical, 2 levels): I15 (2015=100) vs I21 (2021=100)

## Decomposition Variables (for cost breakdown)

6. **Labour cost share** (continuous, ~30-45%): proportion of total cost from labour
7. **Material cost share** (continuous, ~40-50%): proportion from materials
8. **Regulatory compliance share** (continuous, ~5-15%): proportion from regulatory requirements
9. **Logistics/import premium** (continuous, ~0-8%): island/distance premium on materials
10. **Scale/productivity factor** (continuous): market size effect on unit costs

## Comparison Dimensions

11. **Absolute level (EUR/sqm)**: anchored to industry sources
12. **Growth rate (cumulative %)**: relative change from 2015
13. **PPP-adjusted level**: adjusted for general price levels
14. **Cost-to-income ratio**: affordability metric
15. **Trajectory shape**: clustering variable for pattern similarity

## Fixed Parameters

- **Base year for comparison**: 2015-Q1
- **Comparator set**: 10 EU countries + UK (data availability driven)
- **Index type used**: PRC_PRR (only one available for all countries including Ireland)
- **Clustering method**: Ward hierarchical, k=3
- **Structural break method**: PELT with L2 cost, penalty=10
