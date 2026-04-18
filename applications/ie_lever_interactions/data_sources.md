# Data sources — INT-1 housing lever interaction multiplier analysis

## This project synthesises all predecessor findings — no new raw data needed

All inputs come from the 19 predecessor projects. The key parameters:

| Parameter | Value | Source | CI |
|:---|:---|:---|:---|
| Median pipeline duration | 962 days (32 months) | PL-1 | 959-966 |
| Finance rate | 7% on 60% drawdown | C-2 | 5-10% range |
| Total dev cost (Dublin 3-bed) | €592k | C-2 | — |
| Hard cost share | 53% nationally | SCSI / C-1 | 49-53% |
| Viability margin (Dublin houses) | -3.1% | U-2 | — |
| Viability margin (commuter belt) | -9 to -11% | U-2 | — |
| Viability–application correlation | r=0.91 | U-1 | — |
| Current residential applications | ~21,000/yr | U-1 | — |
| Approval rate | ~68% | National register | — |
| Build-yield | 59.6% | S-1 | 55-64% |
| HFA target | 50,500/yr | Housing for All | — |
| Current completions | ~35,000/yr | CSO | — |
| Construction capacity ceiling | ~35,000/yr | S-3 | — |
| Materials CAGR | 3.99%/yr | C-1 | — |
| Labour CAGR | 4.03%/yr | C-1 | — |
| Ireland construction PLI | 99.7 (EU avg) | C-3 / Eurostat | — |
| NZEB DiD | -4.0pp | C-1 | — |
| Policy cost share | 15.5% | C-2 | — |
| Lapse rate | 9.5% | PL-4 | 4.4-15.6% |
| ABP mean weeks | 42 (2024) | PL-3 | 40.6-43.4 |
| JR direct delay | 105k unit-months | S-2 | 85-150k |

## Levers to test in combination

1. **Duration reduction**: 0%, -25%, -33%, -50% of 962-day pipeline
2. **Modular construction**: 0%, -10%, -20%, -30% of hard costs
3. **VAT**: 13.5% (current), 9% (UK rate), 0%
4. **Part V**: 20% (current), 10%, 0%
5. **Development contributions**: current, halved, zeroed
6. **BCAR**: current, halved
7. **Land cost (CPO)**: market price, 50% discount, agricultural price
8. **Finance rate**: 7%, 5%, 3%
9. **Developer margin**: 15%, 10%, 6% (social housing rate)
10. **Construction workforce**: +0%, +20%, +50% (capacity ceiling lift)

## The feedback loop to model

```
Lever applied → Cost reduction → Viability margin improves
→ Application rate increases (r=0.91 elasticity)
→ More permissions granted (68% approval rate)
→ More completions (59.6% build-yield, capped at capacity ceiling)
→ Higher volume → potential scale economies → further cost reduction (third-order)
```

## Smoke-test

All parameters are from published predecessor projects. No new data download needed.
