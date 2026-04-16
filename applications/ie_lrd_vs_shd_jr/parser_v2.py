"""Corrected parser for OPR Appendix-2 raw text.

Key fixes vs. the original parser in analysis.py:
  (a) Case boundary regex uses multiline ^ anchor, avoiding spurious matches.
  (b) Decision year is extracted from the neutral citation [YYYY] IEHC/IESC/IECA,
      NOT from the DD/MM/YYYY date column. The date column often wraps across
      two text lines in pdftotext output, and in multi-column PDF rows a 4-digit
      Record-No year leaks into the date-capture group (see case #99 Crekav:
      date 31/07/2020 but Record-No 2018 — old parser used 2018).
  (c) Outcome classifier is whitespace-tolerant. The OPR outcome column wraps
      across multiple text lines (e.g. "Application\\n...\\ndismissed"), so we
      collapse whitespace before keyword matching.
  (d) Special cases:
      - "set aside" counts as quashing.
      - "upheld" / "allow the appeal and uphold" on appeal cases = state wins.
      - conceded takes priority over quashed when both signals present
        (typical pattern: ABP concedes, court then grants certiorari).
"""
from __future__ import annotations
import re


def parse_cases(text: str) -> list[dict]:
    """Return one dict per numbered row in the Appendix-2 table.

    Keys: num (int), decision_year (int|None), body (str).
    """
    starts: list[tuple[int, int]] = []
    for m in re.finditer(r"(?m)^\s*(\d{1,3})\.\s+\d{1,2}/\d{1,2}/", text):
        starts.append((int(m.group(1)), m.start()))

    out = []
    for i, (num, s) in enumerate(starts):
        e = starts[i + 1][1] if i + 1 < len(starts) else len(text)
        body = text[s:e]
        # Neutral citation "[YYYY] IEHC/IESC/IECA N" — but in the pdftotext
        # output, "[YYYY]" and "IEHC" are in different table columns and may
        # be separated by the case-name text. So we require [YYYY] *and* the
        # presence of IEHC/IESC/IECA somewhere in the body (within the first
        # row header area — first ~500 chars).
        neut = None
        header = body[:800]
        for m in re.finditer(r"\[\s*(20\d{2})\s*\]", header):
            if re.search(r"\b(IEHC|IESC|IECA)\b", header):
                neut = m
                break
        year = int(neut.group(1)) if neut else None
        # Fallback: case #94 Protect East Meath has a malformed row with no
        # well-formed neutral citation on the same line. Hard-code the
        # decision year from the raw text: it reads "[2020] IEHC 294".
        if year is None and num == 94 and "IEHC" in body:
            year = 2020
        out.append({"num": num, "decision_year": year, "body": body})
    return out


def is_shd(body: str) -> bool:
    """A case is SHD-related if the body mentions the SHD regime."""
    return ("SHD" in body) or ("strategic housing" in body.lower())


def _flat(body: str) -> str:
    """Collapse all whitespace to single spaces; lowercase."""
    return re.sub(r"\s+", " ", body).lower().strip()


def classify_outcome(body: str) -> str:
    """Return one of: quashed, conceded, refused, dismissed, upheld, other.

    Priority order:
        upheld (appeal win by ABP/state)
      > conceded
      > quashed / certiorari granted / set aside
      > refused
      > dismissed
      > other
    """
    low = _flat(body)

    # Appeal outcomes (Supreme Court / Court of Appeal): "allow the appeal and
    # uphold the validity of the ABP decision" = ABP wins on appeal.
    # The outcome column often has column-text leakage, so we tolerate
    # arbitrary text between "allow the appeal" and "uphold".
    if re.search(r"allow the appeal.{0,300}?uphold", low):
        return "upheld"
    if re.search(r"uphold.{0,40}?validity of (?:the )?(?:abp|board)", low) and "appeal" in low:
        return "upheld"

    conceded = (
        "challenge conceded" in low
        or "abp conceded" in low
        or "board conceded" in low
        or "conceded by abp" in low
        or "abp conceded;" in low
    )

    quashed = (
        bool(re.search(r"\bquash(?:ed|ing|es)?\b", low))
        or "grant order of certiorari" in low
        or "grant certiorari" in low
        or "granted certiorari" in low
        or re.search(r"\bset aside\b", low) is not None
    )
    # Guard: "certiorari refused" / "quashing refused" are NOT quashes.
    if "certiorari refused" in low and "grant" not in low.split("certiorari refused")[0][-40:]:
        quashed = False
    if "quashing refused" in low:
        quashed = False

    refused = (
        "application refused" in low
        or "certiorari refused" in low
        or "leave refused" in low
        or "leave to seek judicial review refused" in low
        or "extension of time refused" in low
    )

    dismissed = (
        "application dismissed" in low
        or "proceedings dismissed" in low
        or "application/ challenge dismissed" in low
        or "application/challenge dismissed" in low
        or "dismissed as being out of time" in low
        or "dismissed for being out of time" in low
        # Column text can insert noise between "dismissed" and "out of time"
        # (see case 110 O'Riordan: "dismissed as being dublin 9. out of time").
        or bool(re.search(r"dismissed.{0,60}?out of time", low))
        # Case 137: flattened body has "application ... dismissed" with the
        # two words separated by case-name / record-no column noise.
        or (re.search(r"\bapplication\b", low) and re.search(r"\bdismissed\b", low)
            and "refused" not in low and "conceded" not in low
            and not re.search(r"\bquash", low))
    )

    if conceded:
        return "conceded"
    if quashed:
        return "quashed"
    # "dismissed ... out of time" is a statute-of-limitations dismissal —
    # outranks a mere "extension of time refused" follow-on.
    if dismissed and ("out of time" in low or "extension of time" in low):
        return "dismissed"
    if refused:
        return "refused"
    if dismissed:
        return "dismissed"
    return "other"
