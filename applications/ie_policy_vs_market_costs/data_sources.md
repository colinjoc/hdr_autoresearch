# Data sources — C-2 policy-amenable vs market-driven costs

## Primary

1. **CSO WPM28 + EHQ03 + BEA04** — reuse from C-1 (material prices, labour costs, production index)
2. **Buildcost.ie H1 2025 cost guide** — trade-level EUR/sqm breakdown
3. **CSO RZLPA02** — zoned land prices by county (land cost component)

## Policy-set cost components (must be estimated/sourced from literature)

| Component | Typical range | Source |
|:---|:---|:---|
| Development contributions | €10k-30k/unit | LA development contribution schemes (each LA publishes its own) |
| Part V obligation | 20% of units at cost price | Planning & Development Act 2000 s.96 |
| VAT on new residential | 13.5% | Revenue Commissioners |
| BCAR compliance (assigned certifier + inspections) | €3k-8k/unit | RIAI/SCSI estimates |
| Planning application fees | €65 (single house) to €€ (large scheme) | SI 600/2001 |
| Fire safety certificate | ~€2k-5k | Local authority schedule |
| Disability access certificate | ~€1k-3k | Local authority schedule |
| Professional fees (architect, engineer, QS) | 10-15% of build cost | RIAI/Engineers Ireland fee scales |
| Finance cost | 7-10% on drawdown | Commercial bank rates |
| Developer margin | 15-20% | SCSI viability benchmark |

## Key calibration (from SCSI)

- Hard costs (materials + labour + site) = 53% nationally, 49% in Dublin
- Soft costs (land + policy + fees + finance + VAT + margin) = 47% nationally, 51% in Dublin
- For a €400k dwelling: hard ~€212k, soft ~€188k
- Policy-set costs (VAT + Part V + dev contribs + BCAR + planning fees) ≈ €60-80k/unit (15-20% of total)
- Market-driven costs (materials + labour + land + finance) ≈ €280-320k (70-80%)
- Developer margin (~15-20%) sits between the two — market-influenced but margin-squeezable

## Smoke-test (2026-04-18)

All CSO datasets confirmed loadable. Buildcost PDF extracted. Dev contribution rates will be hard-coded from LA published schedules (no single CSV source).
