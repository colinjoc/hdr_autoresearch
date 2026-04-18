# Data sources — UFO-3 warp drive physics: energy conditions survey

## Primary (arXiv papers, extracted to text)

1. **Alcubierre (2000)** — review of the warp drive concept (`alcubierre_2000_review.txt`, 451 lines)
2. **Lentz (2021)** — "Introducing Physical Warp Drives" — proposed positive-energy warp solution (`lentz_2021.txt`, 1,310 lines)
3. **Bobrick & Martire (2021)** — classification of warp drive spacetimes (`bobrick_2021.txt`, 1,310 lines — same file as Lentz, need to re-fetch)
4. **Fell & Heisenberg (2024)** — "Constant Velocity Physical Warp Drive Solution" — subluminal, satisfies all energy conditions (`fell_2024_constant_v.txt`, 1,912 lines)
5. **Santiago, Schuster & Visser (2024)** — "Black Holes, Warp Drives, and Energy Conditions" (`santiago_2024_energy.txt`, 930 lines)
6. **Celmaster (2025)** — "Violations of the Weak Energy Condition for Lentz Warp Drives" — shows Lentz 2021 still violates WEC (`celmaster_2025_wec.txt`, 4,037 lines)
7. **Natário (2002)** — alternative warp drive without expansion/contraction (`natario_2002.txt`)
8. **Lobo (2007)** — wormhole review (`lobo_2007_wormholes.txt`)
9. **GWTC-3 (2021)** — LIGO/Virgo/KAGRA gravitational-wave catalogue (`gwtc3_summary.txt`) — for observational constraints

## Key concepts to catalogue

| Metric | Author(s) | Year | Superluminal? | Energy conditions |
|:---|:---|:---|:---|:---|
| Alcubierre warp | Alcubierre | 1994 | Yes | Violates WEC, NEC |
| Natário drive | Natário | 2002 | Yes | Violates WEC, NEC |
| Krasnikov tube | Krasnikov | 1998 | Yes (after construction) | Violates WEC |
| Morris-Thorne wormhole | Morris & Thorne | 1988 | Yes (traversable) | Requires exotic matter |
| Lentz "physical" warp | Lentz | 2021 | Subluminal initially | Claimed positive-energy; Celmaster 2025 disputes |
| Bobrick-Martire class | Bobrick & Martire | 2021 | Parametric | Classification framework |
| Fell-Heisenberg constant-v | Fell & Heisenberg | 2024 | No (subluminal) | Satisfies ALL energy conditions |
| Van Den Broeck | Van Den Broeck | 1999 | Yes | Reduces exotic matter mass |

## Observational constraints

- GWTC-3: 90 compact binary mergers → constrain exotic spacetime geometry
- NANOGrav 15-yr: stochastic GW background → constrains large-scale metric deformations
- Cosmic-ray energy spectrum: Greisen-Zatsepin-Kuzmin limit constrains Lorentz violation

## Smoke-test (2026-04-18)

- 9 arXiv papers fetched and extracted (30,772 lines total)
- Key claims extractable from text (energy condition statements, exotic matter mass estimates)
- This is a LITERATURE-HEAVY project — the "data" is the catalogue of exact solutions and their properties
