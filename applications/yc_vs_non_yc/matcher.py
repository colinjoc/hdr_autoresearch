"""Match YC companies to SEC Form D filings by normalized issuer name.

Phase 0.5 matcher is precision-biased: ambiguous multi-CIK names are dropped
rather than tie-broken. Fuzzy matching (rapidfuzz / TF-IDF / embeddings) is
a Phase-2 experiment in research_queue.md, not in scope here.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Literal

import pandas as pd

from secformd_loader import normalize_issuer_name


def build_name_index(formd: pd.DataFrame) -> dict[str, set[str]]:
    """Normalized issuer name -> set of CIKs filing under that name."""
    idx: dict[str, set[str]] = defaultdict(set)
    for name, cik in zip(formd["entityname"], formd["cik"]):
        norm = normalize_issuer_name(name)
        if not norm:
            continue
        idx[norm].add(str(cik))
    return dict(idx)


def _batch_quarter_start(batch_year: int, batch_quarter: int) -> pd.Timestamp:
    month = {1: 1, 2: 4, 3: 7, 4: 10}[int(batch_quarter)]
    return pd.Timestamp(year=int(batch_year), month=month, day=1)


def match_yc_to_formd(yc: pd.DataFrame, formd: pd.DataFrame,
                      strategy: Literal["exact"] = "exact") -> pd.DataFrame:
    """Return one row per YC company with a unique CIK match.

    Dropped cases:
    - YC company name normalises to empty string
    - No Form D issuer matches the normalised name
    - >1 distinct CIK matches the normalised name (ambiguous)
    - No Form D filing on or after the batch-start date
    """
    if strategy != "exact":
        raise ValueError(f"unsupported strategy: {strategy}")
    idx = build_name_index(formd)
    fd = formd.copy()
    fd["_norm"] = fd["entityname"].apply(normalize_issuer_name)
    fd["filing_date"] = pd.to_datetime(fd["filing_date"], errors="coerce")

    rows = []
    for _, yc_row in yc.iterrows():
        nm = normalize_issuer_name(yc_row["name"])
        if not nm:
            continue
        ciks = idx.get(nm)
        if not ciks or len(ciks) != 1:
            continue
        cik = next(iter(ciks))
        batch_start = _batch_quarter_start(yc_row["batch_year"], yc_row["batch_quarter"])
        cand = fd[(fd["cik"] == cik) & (fd["filing_date"] >= batch_start)]
        if cand.empty:
            continue
        pick = cand.sort_values("filing_date").iloc[0]
        rows.append({
            "yc_id": yc_row["id"],
            "slug": yc_row["slug"],
            "name": yc_row["name"],
            "batch": yc_row["batch"],
            "batch_year": yc_row["batch_year"],
            "batch_quarter": yc_row["batch_quarter"],
            "cik": cik,
            "accessionnumber": pick["accessionnumber"],
            "filing_date": pick["filing_date"],
            "totalofferingamount": pick["totalofferingamount"],
            "industrygrouptype": pick["industrygrouptype"],
            "stateorcountry": pick["stateorcountry"],
        })
    return pd.DataFrame(rows)
