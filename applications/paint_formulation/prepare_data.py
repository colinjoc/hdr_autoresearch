"""
prepare_data.py — build data/paint.csv from the Zenodo lacquer dataset.

Source: Borgert et al., "High-Throughput and Explainable Machine Learning
for Lacquer Formulations", Zenodo DOI 10.5281/zenodo.13742098.

The canonical consolidated file is at
  Evaluation/PURformance-Dataset.xlsx
inside the Evaluation.zip archive, with six sheets (cs, i1, i2, i3, i4, rdm)
one per experimental campaign.

Columns (German originals, English translations):
  Vernetzung           — Crosslink (relative amount of isocyanate crosslinker)
  HDI-IPDI             — Cyclic NCO percent (ratio of isophorone diisocyanate
                         to the sum of HDI + IPDI; 0 = pure aliphatic,
                         1 = pure cycloaliphatic)
  Mattierungsmittel    — Matting agent (silica) mass fraction
  Pigmentpaste         — Pigment paste mass fraction
  Schichtdicke [µm]    — Dry film thickness (micrometres)
  Erichsen-Tiefung     — Erichsen cupping test result (millimetres)
  Glanz 60°            — Gloss at 60 degrees (gloss units)
  Deckvermögen [%]     — Hiding power (percent contrast ratio)
  Kratzhärte [N]       — Scratch hardness (Newton)

All four composition variables are expressed on a normalised [0, 1] scale that
maps to physically sensible ranges via `tb.rezeptur_berechnen` in the original
source package. We keep that normalised scale for modelling and recover the
physical recipe in phase_b_discovery.py for cost/VOC calculation.

Usage:
    python prepare_data.py
Writes:
    data/paint.csv — 65 rows, 9 columns (all iterations merged)
"""
from __future__ import annotations

import zipfile
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
ZIP_PATH = DATA_DIR / "Evaluation.zip"
XLSX_INSIDE_ZIP = "Evaluation/PURformance-Dataset.xlsx"
OUT_CSV = DATA_DIR / "paint.csv"

COLUMN_MAP = {
    "Vernetzung": "crosslink",
    "HDI-IPDI": "cyc_nco_frac",
    "Mattierungsmittel": "matting_agent",
    "Pigmentpaste": "pigment_paste",
    "Schichtdicke [µm]": "thickness_um",
    "Erichsen-Tiefung": "cupping_mm",
    "Glanz 60°": "gloss_60",
    "Deckvermögen [%]": "hiding_power_pct",
    "Kratzhärte [N]": "scratch_hardness_N",
}

SHEETS = ["cs", "i1", "i2", "i3", "i4", "rdm"]


def extract_xlsx_if_needed() -> Path:
    local_xlsx = DATA_DIR / "Evaluation" / "PURformance-Dataset.xlsx"
    if local_xlsx.exists():
        return local_xlsx
    if not ZIP_PATH.exists():
        raise FileNotFoundError(
            f"Missing {ZIP_PATH}. Download with\n"
            f"  curl -L -o {ZIP_PATH} "
            f"https://zenodo.org/api/records/13742098/files/Evaluation.zip/content"
        )
    with zipfile.ZipFile(ZIP_PATH) as zf:
        zf.extract(XLSX_INSIDE_ZIP, DATA_DIR)
    return local_xlsx


def build_csv() -> pd.DataFrame:
    xlsx = extract_xlsx_if_needed()
    frames = []
    for sheet in SHEETS:
        df = pd.read_excel(xlsx, sheet_name=sheet)
        df = df.rename(columns=COLUMN_MAP)
        df["source_iteration"] = sheet
        frames.append(df)
    merged = pd.concat(frames, ignore_index=True)
    merged = merged.dropna(subset=["scratch_hardness_N", "gloss_60",
                                    "hiding_power_pct", "cupping_mm",
                                    "thickness_um"]).reset_index(drop=True)
    OUT_CSV.parent.mkdir(exist_ok=True)
    merged.to_csv(OUT_CSV, index=False)
    return merged


def main():
    df = build_csv()
    print(f"Wrote {OUT_CSV} with {len(df)} rows and {df.shape[1]} columns")
    print(df.describe().round(3))
    print(f"\nRows per iteration:")
    print(df["source_iteration"].value_counts().sort_index())


if __name__ == "__main__":
    main()
