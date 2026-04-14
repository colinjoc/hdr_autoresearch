"""Load the yc-oss/api all.json dump into a tidy DataFrame with batch-parsed
columns suitable for matched-pair analysis against SEC Form D filings.

Design choices:
- Parse `batch` (e.g. "W19", "S23") into (year, season, quarter) at load time.
- Do not drop rows with unknown batch codes here; downstream code decides.
- LEAKY fields (`team_size`, `all_locations`) are kept verbatim so the leakage
  annotations in design_variables.md stay enforceable at feature-engineering time.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Tuple

import pandas as pd


BATCH_RE = re.compile(r"^(Winter|Spring|Summer|Fall) (\d{4})$")

SEASON_TO_QUARTER = {"Winter": 1, "Spring": 2, "Summer": 3, "Fall": 4}


def parse_batch(code: str) -> Tuple[int | None, str | None, int | None]:
    """Return (year, season_name, quarter_number) or triple of Nones.

    YC batch strings in the yc-oss mirror are "Winter 2022", "Summer 2021",
    "Fall 2025", "Spring 2025" — four seasons. Spring and Fall are recent
    additions (2024+) as YC expanded from two to four cohorts per year.
    """
    if not isinstance(code, str):
        return (None, None, None)
    m = BATCH_RE.fullmatch(code)
    if not m:
        return (None, None, None)
    season, year = m.group(1), int(m.group(2))
    return (year, season, SEASON_TO_QUARTER[season])


def load_yc_companies(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    with path.open() as fh:
        data = json.load(fh)
    df = pd.DataFrame(data)

    parsed = df["batch"].apply(parse_batch)
    df["batch_year"] = parsed.map(lambda t: t[0])
    df["batch_season"] = parsed.map(lambda t: t[1])
    df["batch_quarter"] = parsed.map(lambda t: t[2])

    return df


if __name__ == "__main__":
    import sys
    here = Path(__file__).parent
    df = load_yc_companies(here / "data" / "yc_companies_raw.json")
    print(f"Loaded {len(df)} YC companies")
    print(df[["batch", "batch_year", "batch_season", "status"]].value_counts().head(20))
