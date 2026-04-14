"""Tests for SEC DERA Form D TSV loader.

SEC DERA publishes pre-parsed quarterly Form D ZIPs at
`https://www.sec.gov/files/structureddata/data/form-d-data-sets/{yyyy}q{q}_d.zip`.

Each ZIP contains FORMDSUBMISSION.tsv, ISSUERS.tsv, OFFERING.tsv,
RELATEDPERSONS.tsv, RECIPIENTS.tsv, SIGNATURES.tsv — joined by ACCESSIONNUMBER.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from secformd_loader import (
    load_formd_quarter,
    join_formd_tables,
    filter_seed_stage,
    normalize_issuer_name,
)

HERE = Path(__file__).resolve().parents[1]
Q1_2019 = HERE / "data" / "sec_formd" / "2019q1_d.zip"


def test_zip_present():
    assert Q1_2019.exists(), "2019Q1 Form D ZIP must be cached first"


def test_load_formd_quarter_returns_three_frames():
    sub, iss, off = load_formd_quarter(Q1_2019)
    assert isinstance(sub, pd.DataFrame)
    assert isinstance(iss, pd.DataFrame)
    assert isinstance(off, pd.DataFrame)
    assert len(sub) > 10_000  # 2019Q1 has ~12k
    assert len(iss) >= len(sub)  # multi-issuer filings allowed


def test_join_formd_produces_one_row_per_primary_issuer():
    sub, iss, off = load_formd_quarter(Q1_2019)
    joined = join_formd_tables(sub, iss, off)
    # primary-issuer filter must collapse multi-issuer filings to one row
    assert joined["accessionnumber"].is_unique
    assert len(joined) >= 10_000
    for col in ("cik", "entityname", "filing_date", "stateorcountry",
                "industrygrouptype", "totalofferingamount", "totalamountsold",
                "yearofinc_value_entered"):
        assert col in joined.columns, f"missing {col}"


def test_filter_seed_stage_keeps_tech_ranges():
    sub, iss, off = load_formd_quarter(Q1_2019)
    df = join_formd_tables(sub, iss, off)
    before = len(df)
    seed = filter_seed_stage(df)
    assert 0 < len(seed) < before
    amts = pd.to_numeric(seed["totalofferingamount"], errors="coerce")
    assert amts.dropna().between(100_000, 50_000_000).all()
    assert (seed["industrygrouptype"].str.contains("Technology|Internet|Software|Manufacturing|Health Care|Biotech|Telecom",
                                                    case=False, na=False)).any()


@pytest.mark.parametrize("raw,norm", [
    ("Airbnb, Inc.", "airbnb"),
    ("Stripe, Inc", "stripe"),
    ("Dropbox LLC", "dropbox"),
    ("The Dropbox Corporation", "dropbox"),
    ("OpenAI, L.P.", "openai"),
    ("DoorDash Holdings, Inc.", "doordash holdings"),  # "holdings" kept — not a suffix
    ("GitLab Inc.", "gitlab"),
])
def test_normalize_issuer_name_strips_legal_suffixes(raw, norm):
    assert normalize_issuer_name(raw) == norm


def test_normalize_handles_none_and_empty():
    assert normalize_issuer_name(None) == ""
    assert normalize_issuer_name("") == ""
    assert normalize_issuer_name("   ") == ""
