"""SEC DERA Form D TSV loader.

Pulls a quarterly Form D ZIP, loads the three core tables (FORMDSUBMISSION,
ISSUERS, OFFERING), joins on ACCESSIONNUMBER keeping only the primary issuer
row per filing, and filters to seed/early-stage tech raises for matching
against the YC cohort.
"""
from __future__ import annotations

import re
import zipfile
from pathlib import Path
from typing import Tuple

import pandas as pd


SEC_HEADERS = {"User-Agent": "HDR research col@example.com"}

_LEGAL_SUFFIXES = re.compile(
    r"""
    \b(
        inc(?:orporated)? |
        corp(?:oration)? |
        corporation |
        co(?:mpany)? |
        llc |
        l\.?l\.?c\.? |
        ltd |
        limited |
        lp |
        l\.?p\.? |
        llp |
        plc |
        gmbh |
        sa |
        s\.?a\.? |
        pty |
        ag |
        bv |
        ab
    )\b\.?
    """,
    re.IGNORECASE | re.VERBOSE,
)

_STOPWORDS_LEADING = re.compile(r"^(the)\s+", re.IGNORECASE)

_SEED_INDUSTRIES = re.compile(
    r"Technology|Internet|Software|Computer|Manufacturing|Health\s*Care|Biotech|"
    r"Pharmaceutical|Telecom|Energy|Retail|Business\s*Services|Services-Other|"
    r"Restaurants|Real\s*Estate|Agriculture|Environmental",
    re.IGNORECASE,
)


def load_formd_quarter(zip_path: str | Path) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Open a Form D quarterly ZIP; return (submission, issuers, offering)."""
    zip_path = Path(zip_path)
    with zipfile.ZipFile(zip_path) as z:
        # DERA uses `{YYYYQn}_d/` prefix
        names = z.namelist()
        prefix = next(n for n in names if n.endswith("FORMDSUBMISSION.tsv"))
        prefix = prefix.rsplit("/", 1)[0] + "/"
        sub = pd.read_csv(z.open(prefix + "FORMDSUBMISSION.tsv"),
                          sep="\t", dtype=str, on_bad_lines="warn")
        iss = pd.read_csv(z.open(prefix + "ISSUERS.tsv"),
                          sep="\t", dtype=str, on_bad_lines="warn")
        off = pd.read_csv(z.open(prefix + "OFFERING.tsv"),
                          sep="\t", dtype=str, on_bad_lines="warn")
    # normalise column names to lowercase for downstream sanity
    sub.columns = [c.lower() for c in sub.columns]
    iss.columns = [c.lower() for c in iss.columns]
    off.columns = [c.lower() for c in off.columns]
    return sub, iss, off


def join_formd_tables(sub: pd.DataFrame, iss: pd.DataFrame, off: pd.DataFrame) -> pd.DataFrame:
    """Inner-join submission + primary issuer + offering on ACCESSIONNUMBER."""
    primary = iss[iss["is_primaryissuer_flag"].str.upper().isin({"Y", "YES"})].copy()
    # dedupe defensively if a filing lists two primary issuers (rare data bug)
    primary = primary.drop_duplicates(subset="accessionnumber", keep="first")
    df = sub.merge(primary, on="accessionnumber", how="inner", suffixes=("", "_iss"))
    df = df.merge(off, on="accessionnumber", how="inner", suffixes=("", "_off"))
    return df


def filter_seed_stage(df: pd.DataFrame,
                      min_usd: float = 100_000,
                      max_usd: float = 50_000_000) -> pd.DataFrame:
    """Keep filings plausibly corresponding to seed/Series-A startup raises."""
    amt = pd.to_numeric(df["totalofferingamount"], errors="coerce")
    tech = df["industrygrouptype"].fillna("").apply(
        lambda s: bool(_SEED_INDUSTRIES.search(s))
    )
    # Exclude pooled investment funds (these are VC funds themselves)
    is_fund = df["ispooledinvestmentfundtype"].str.upper().eq("Y") if "ispooledinvestmentfundtype" in df.columns else False
    keep = amt.between(min_usd, max_usd) & tech & ~is_fund
    return df[keep].copy()


def normalize_issuer_name(name: str | None) -> str:
    """Lowercase; strip legal suffixes and leading 'The'; collapse whitespace."""
    if not isinstance(name, str):
        return ""
    s = name.strip()
    if not s:
        return ""
    s = _STOPWORDS_LEADING.sub("", s)
    # remove trailing punctuation and suffixes repeatedly
    for _ in range(3):
        s2 = _LEGAL_SUFFIXES.sub("", s).strip(" ,.")
        if s2 == s:
            break
        s = s2
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s
