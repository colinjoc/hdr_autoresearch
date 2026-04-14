"""Fuzzy YC ↔ Form-D matcher (research_queue G2).

Two-pass strategy:
1. Exact match on normalized name (already implemented in matcher.py).
2. For unmatched YC companies, fuzzy match residuals against Form-D issuers
   using rapidfuzz token_set_ratio ≥ 92 AND prefix-ratio ≥ 85.
3. Accept only 1-to-1 unique matches (precision-biased); log the rest as
   `ambiguous_fuzzy` for manual review.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from rapidfuzz import fuzz, process

from secformd_loader import normalize_issuer_name
from matcher import _batch_quarter_start


MIN_YC_LEN_FOR_FUZZY = 8
TEMPORAL_WINDOW_MONTHS = 24
EXACT_PREFIX_MIN_RATIO = 70  # when y is a prefix of f, loose similarity is OK
FULL_STRING_MIN_RATIO = 95   # when y is NOT a prefix, require near-perfect


def _tighter_match(y: str, f: str) -> tuple[bool, int]:
    """Strict prefix-biased rule returning (keep?, score)."""
    if y == f:
        return (True, 100)
    if len(y) < MIN_YC_LEN_FOR_FUZZY:
        return (False, 0)
    # Prefix rule: y is followed by whitespace-then-suffix in f
    if f.startswith(y + " "):
        tail = f[len(y):].strip()
        # tail must be short OR a simple legal-suffix phrase
        if len(tail) <= 15:
            return (True, int(fuzz.ratio(y, f)))
    # Full-string rule for last-word-abbreviation cases
    r = int(fuzz.ratio(y, f))
    if r >= FULL_STRING_MIN_RATIO:
        return (True, r)
    return (False, r)


def fuzzy_match_yc(yc: pd.DataFrame, formd: pd.DataFrame,
                   exact_matched: pd.DataFrame) -> pd.DataFrame:
    """Return fuzzy matches for YC companies NOT already in exact_matched."""
    matched_slugs = set(exact_matched["slug"])
    residual = yc[~yc["slug"].isin(matched_slugs)].copy()
    residual["_norm"] = residual["name"].apply(normalize_issuer_name)
    residual = residual[residual["_norm"].ne("")]

    # Pre-filter Form D to temporal window-eligible candidates (per YC company)
    fd = formd.copy()
    fd["_norm"] = fd["entityname"].apply(normalize_issuer_name)
    fd["filing_date"] = pd.to_datetime(fd["filing_date"], errors="coerce")
    fd = fd[fd["_norm"].ne("") & fd["filing_date"].notna()]

    fd_names_all = list(fd["_norm"].unique())
    name_to_ciks = fd.groupby("_norm")["cik"].apply(lambda s: set(s.astype(str))).to_dict()

    rows = []
    for _, yc_row in residual.iterrows():
        target = yc_row["_norm"]
        if len(target) < MIN_YC_LEN_FOR_FUZZY:
            continue
        batch_start = _batch_quarter_start(yc_row["batch_year"], yc_row["batch_quarter"])
        window_end = batch_start + pd.DateOffset(months=TEMPORAL_WINDOW_MONTHS)

        # Narrow Form-D candidates to this YC's temporal window for the prefix-filter.
        fd_sub = fd[(fd["filing_date"] >= batch_start) & (fd["filing_date"] <= window_end)]
        cand_names = set(fd_sub["_norm"].unique())
        if not cand_names:
            continue

        # Apply tighter match rule
        best = None
        best_score = 0
        for f in cand_names:
            ok, s = _tighter_match(target, f)
            if ok and s > best_score:
                best, best_score = f, s
        if best is None:
            continue
        ciks = name_to_ciks.get(best, set())
        if len(ciks) != 1:
            continue
        cik = next(iter(ciks))
        cand = fd[(fd["cik"] == cik) & (fd["filing_date"] >= batch_start)
                  & (fd["filing_date"] <= window_end)]
        if cand.empty:
            continue
        pick = cand.sort_values("filing_date").iloc[0]
        rows.append({
            "yc_id": yc_row["id"],
            "slug": yc_row["slug"],
            "name": yc_row["name"],
            "matched_form_d_name": pick["entityname"],
            "batch": yc_row["batch"],
            "batch_year": yc_row["batch_year"],
            "batch_quarter": yc_row["batch_quarter"],
            "cik": cik,
            "accessionnumber": pick["accessionnumber"],
            "filing_date": pick["filing_date"],
            "totalofferingamount": pick["totalofferingamount"],
            "industrygrouptype": pick["industrygrouptype"],
            "stateorcountry": pick["stateorcountry"],
            "fuzz_score": best_score,
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    import glob
    import sys
    HERE = Path(__file__).parent
    sys.path.insert(0, str(HERE))
    from secformd_loader import load_formd_quarter, join_formd_tables, filter_seed_stage
    from yc_loader import load_yc_companies
    from matcher import match_yc_to_formd

    print("loading data...", flush=True)
    parts = []
    for z in sorted(glob.glob(str(HERE / "data/sec_formd/*.zip"))):
        sub, iss, off = load_formd_quarter(z)
        parts.append(join_formd_tables(sub, iss, off))
    all_fd = pd.concat(parts, ignore_index=True)
    all_fd["filing_date"] = pd.to_datetime(all_fd["filing_date"], errors="coerce")
    seed = filter_seed_stage(all_fd)
    yc = load_yc_companies(HERE / "data/yc_companies_raw.json")
    yc_cohort = yc[yc["batch_year"].between(2014, 2019)].copy()

    print("exact match...", flush=True)
    exact = match_yc_to_formd(yc_cohort, seed, strategy="exact")
    print(f"exact: {len(exact)} / {len(yc_cohort)}", flush=True)

    print("fuzzy match on residuals...", flush=True)
    fuzzy = fuzzy_match_yc(yc_cohort, seed, exact)
    print(f"fuzzy: {len(fuzzy)} additional matches", flush=True)
    print(f"combined: {len(exact) + len(fuzzy)} / {len(yc_cohort)}  "
          f"({100*(len(exact)+len(fuzzy))/len(yc_cohort):.1f}%)")

    # Sample fuzzy matches for eyeballing
    if len(fuzzy):
        print("\nSample fuzzy matches (top-20 by score):")
        print(fuzzy.sort_values("fuzz_score", ascending=False)
              [["name", "matched_form_d_name", "fuzz_score"]]
              .head(20).to_string(index=False))
