# Data Sources

## REE REData API (Red Electrica de Espana)
- **URL**: https://apidatos.ree.es/en/datos/
- **Size**: ~15 MB total across all endpoints
- **License**: Open government data (Spain)
- **Local path**: `data/*.json`
- **Download**: See `data_loader.py` which fetches from the API
- **Endpoints used**:
  - `generacion/estructura-generacion` — Generation by technology (daily)
  - `demanda/demanda-tiempo-real` — Real-time demand (hourly)
  - `intercambios/francia-frontera` — Spain-France interconnector flows
  - `intercambios/portugal-frontera` — Spain-Portugal interconnector flows
  - `intercambios/marruecos-frontera` — Spain-Morocco interconnector flows
  - `mercados/precios-mercados-tiempo-real` — Spot market prices

## ENTSO-E Final Report on Iberian Blackout
- **URL**: https://www.entsoe.eu/publications/blackout/28-april-2025-iberian-blackout/
- **Report PDF**: https://eepublicdownloads.blob.core.windows.net/public-cdn-container/clean-documents/Publications/2025/iberian-blackout/Final%20Report%20on%20the%20Grid%20Incident%20in%20Spain%20and%20Portugal%20on%2028%20April%202025.pdf
- **Size**: ~50 MB (472 pages)
- **License**: ENTSO-E public
- **Used for**: Technical details of cascade sequence, timeline, measurements
