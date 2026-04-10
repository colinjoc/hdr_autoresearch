# Data Sources

## SEAI BER Public Search — National BER Research Tool

- **Name**: SEAI Building Energy Rating (BER) Public Search Dataset
- **URL**: https://ndber.seai.ie/BERResearchTool/ber/search.aspx
- **Data.gov.ie listing**: https://data.gov.ie/dataset/ber-research-tool
- **Size**: ~268 MB compressed (ZIP), ~1.48 GB uncompressed (TSV), ~246 MB as Parquet
- **Records**: 1,366,752 domestic BER certificates (after skipping ~27,000 malformed rows from 1,393,710 total)
- **Columns**: 211 fields per certificate
- **License**: Creative Commons Attribution 4.0 (CC BY 4.0)
- **Local path**: `data/ber_raw.parquet` (processed from `data/BERPublicSearch.zip`)
- **Download command**: Run `python3 download_data.py` from project root
- **Checksum**: SHA256 of BERPublicSearch.zip to be recorded after download
- **Date downloaded**: 2026-04-10

### Key Fields Used

| Field | Description |
|-------|-------------|
| CountyName | Irish county/Dublin postal district |
| DwellingTypeDescr | House type (detached, semi-d, terrace, apartment, etc.) |
| Year_of_Construction | Year the dwelling was built |
| TypeofRating | Existing, Final, or Provisional |
| EnergyRating | BER letter grade (A1-G) |
| BerRating | Calculated primary energy in kWh/m2/yr (the DEAP number) |
| UValueWall/Roof/Floor/Window | Thermal transmittance of building envelope (W/m2K) |
| MainSpaceHeatingFuel | Primary heating fuel type |
| HSMainSystemEfficiency | Heating system main efficiency (%) |
| VentilationMethod | Natural or mechanical ventilation |
| TotalDeliveredEnergy | Total delivered energy (kWh) |
| DeliveredEnergyMainSpace | Delivered energy for space heating (kWh) |
| PrimaryEnergyMainSpace | Primary energy for space heating (kWh) |
| StructureType | Wall construction (masonry, timber frame, etc.) |
| LowEnergyLightingPercent | % of fixed lighting that is low-energy |
| ThermalBridgingFactor | Thermal bridging y-value (W/m2K) |

### Important Limitations

1. **BER = DEAP-calculated energy, NOT measured consumption.** The BER rating is an asset rating based on the Dwelling Energy Assessment Procedure (DEAP), Ireland's implementation of the EU EPBD methodology. It models standardised occupancy (2.5 people, 21C living room, 18C elsewhere, specific hot water demand). Actual energy use can differ by 2-3x due to occupant behaviour, the "prebound effect" (under-heating in inefficient homes), and the "rebound effect" (increased comfort in efficient homes).

2. **No measured energy data.** This dataset does not contain metered gas/electricity bills. The "energy gap" we analyse is between BER bands' *calculated* energy values, not between calculated and measured.

3. **Self-selection bias.** BER certificates are required for sale/rental. The sample over-represents recently built, transacted, and rental properties. Pre-1960 rural dwellings may be under-represented.

4. **Multiple certificates per dwelling.** A dwelling may have multiple BER certificates (before and after retrofit). We use all certificates, which allows retrofit analysis but means the dataset is not a simple cross-section of the housing stock.
