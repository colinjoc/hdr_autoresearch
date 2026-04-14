"""Tests for the YC ↔ Form-D name matcher.

Matching strategy (Phase 0.5 baseline):
1. Exact match on normalized issuer name → CIK anchor
2. For multiple Form-D filings under one CIK, pick earliest post-batch filing
3. Rejected candidates with ambiguous matches (>1 CIK) are dropped
   conservatively (matching precision > recall for this stage)
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from matcher import (
    build_name_index,
    match_yc_to_formd,
)


def _mk_formd():
    return pd.DataFrame({
        "accessionnumber": ["A1", "A2", "A3", "A4"],
        "cik": ["1000", "2000", "3000", "1000"],
        "entityname": ["Stripe, Inc.", "Airbnb, Inc.",
                       "SomeRandom LLC", "Stripe, Inc."],
        "filing_date": ["2015-01-01", "2015-02-01",
                        "2016-03-01", "2016-06-01"],
        "totalofferingamount": ["2000000", "1500000", "500000", "30000000"],
        "industrygrouptype": ["Technology", "Internet", "Other", "Technology"],
        "stateorcountry": ["DE", "CA", "NY", "DE"],
    })


def _mk_yc():
    return pd.DataFrame({
        "id": [1, 2, 3],
        "slug": ["stripe", "airbnb", "nonexistent"],
        "name": ["Stripe", "Airbnb", "Nonexistent Corp"],
        "batch": ["Summer 2009", "Winter 2009", "Summer 2015"],
        "batch_year": [2009, 2009, 2015],
        "batch_quarter": [3, 1, 3],
    })


def test_build_name_index_groups_by_normalized_name():
    fd = _mk_formd()
    idx = build_name_index(fd)
    # stripe appears twice with same CIK 1000 → collapses to one CIK
    assert idx["stripe"] == {"1000"}
    assert idx["airbnb"] == {"2000"}


def test_build_name_index_multiple_ciks_retained():
    fd = _mk_formd().copy()
    # Add a duplicate name under a DIFFERENT CIK
    fd = pd.concat([fd, pd.DataFrame([{
        "accessionnumber": "A5", "cik": "9999",
        "entityname": "Stripe Inc", "filing_date": "2016-01-01",
        "totalofferingamount": "100000", "industrygrouptype": "Technology",
        "stateorcountry": "DE",
    }])], ignore_index=True)
    idx = build_name_index(fd)
    assert idx["stripe"] == {"1000", "9999"}


def test_match_yc_to_formd_exact_only():
    yc = _mk_yc()
    fd = _mk_formd()
    matched = match_yc_to_formd(yc, fd, strategy="exact")
    assert set(matched["slug"]) == {"stripe", "airbnb"}  # nonexistent unmatched
    # stripe -> CIK 1000
    stripe_row = matched[matched["slug"] == "stripe"].iloc[0]
    assert stripe_row["cik"] == "1000"
    # nonexistent is dropped (not kept with NaN CIK)
    assert "nonexistent" not in set(matched["slug"])


def test_match_yc_drops_ambiguous_multi_cik():
    yc = pd.DataFrame({"id": [1], "slug": ["acme"], "name": ["Acme"],
                       "batch": ["Winter 2017"], "batch_year": [2017], "batch_quarter": [1]})
    fd = pd.DataFrame({
        "accessionnumber": ["A1", "A2"],
        "cik": ["111", "222"],
        "entityname": ["Acme Inc", "Acme Corp"],
        "filing_date": ["2017-02-01", "2017-03-01"],
        "totalofferingamount": ["1000000", "1000000"],
        "industrygrouptype": ["Technology", "Technology"],
        "stateorcountry": ["DE", "DE"],
    })
    matched = match_yc_to_formd(yc, fd, strategy="exact")
    # Ambiguous → dropped
    assert len(matched) == 0


def test_match_yc_picks_earliest_post_batch_filing():
    yc = pd.DataFrame({"id": [1], "slug": ["stripe"], "name": ["Stripe"],
                       "batch": ["Summer 2009"], "batch_year": [2009], "batch_quarter": [3]})
    fd = _mk_formd()
    matched = match_yc_to_formd(yc, fd, strategy="exact")
    row = matched.iloc[0]
    # Earliest Stripe filing post-batch: A1 on 2015-01-01 (both A1 and A4 are post-batch)
    assert row["accessionnumber"] == "A1"
