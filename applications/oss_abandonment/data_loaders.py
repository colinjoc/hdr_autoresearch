"""
GH Archive loader + feature engineering for OSS abandonment prediction.

Scope: given a list of hourly GH Archive URLs, stream + filter the events of
interest, aggregate per (repo, day) counts, and label abandonment at a
configurable horizon.

Real data only — no synthetic generation (per `real data first` rule).
"""

from __future__ import annotations

import gzip
import io
import json
import os
import sys
import urllib.request
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Bot filter
# ---------------------------------------------------------------------------

BOT_SUFFIX = "[bot]"
KNOWN_BOTS: frozenset[str] = frozenset({
    "dependabot", "dependabot-preview", "renovate", "renovate-bot",
    "greenkeeper", "pre-commit-ci", "github-actions", "snyk-bot",
    "allcontributors", "pyup-bot", "imgbot",
    "whitesource-bolt-for-github", "mergify", "codeclimate-bot",
    "coveralls", "codecov", "sonarcloud", "stale",
})


def is_bot(login_or_name: str | None) -> bool:
    """Return True if the given GitHub login or commit-author name looks like a bot."""
    if not login_or_name:
        return True
    s = login_or_name.lower()
    return s.endswith(BOT_SUFFIX) or s in KNOWN_BOTS


def human_distinct_commits(push_event: dict) -> int:
    """Count distinct human-authored commits in a PushEvent payload."""
    commits = push_event.get("payload", {}).get("commits", []) or []
    n = 0
    for c in commits:
        if not c.get("distinct"):
            continue
        author = (c.get("author") or {})
        if not is_bot(author.get("name") or author.get("email", "")):
            n += 1
    return n


# ---------------------------------------------------------------------------
# GH Archive URL enumeration + streaming
# ---------------------------------------------------------------------------

WANTED_TYPES: frozenset[str] = frozenset({
    "PushEvent", "PullRequestEvent", "PullRequestReviewEvent",
    "PullRequestReviewCommentEvent", "IssuesEvent", "IssueCommentEvent",
    "WatchEvent", "ForkEvent", "ReleaseEvent", "CreateEvent",
    "DeleteEvent", "MemberEvent",
})


def gharchive_url(dt: datetime) -> str:
    """Build the GH Archive URL for a given hour (UTC)."""
    # UNPADDED hour: ...-14.json.gz, not ...-14.json.gz
    return f"https://data.gharchive.org/{dt:%Y-%m-%d}-{dt.hour}.json.gz"


def hour_range(start_utc: datetime, end_utc: datetime) -> Iterable[datetime]:
    """Yield UTC datetimes one hour apart in [start, end)."""
    t = start_utc
    while t < end_utc:
        yield t
        t += timedelta(hours=1)


def download_hour(dt: datetime, cache_dir: Path) -> Path:
    """Download one hourly file to cache_dir if not already present. Return path."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    fn = cache_dir / f"{dt:%Y-%m-%d}-{dt.hour}.json.gz"
    if fn.exists() and fn.stat().st_size > 1024:  # non-empty
        return fn
    url = gharchive_url(dt)
    req = urllib.request.Request(url, headers={"User-Agent": "oss-abandonment/0.1"})
    with urllib.request.urlopen(req, timeout=120) as resp, open(fn, "wb") as w:
        while True:
            chunk = resp.read(1 << 20)
            if not chunk:
                break
            w.write(chunk)
    return fn


def iter_events(path: Path) -> Iterable[dict]:
    """Yield parsed event dicts from one hourly gzipped NDJSON file.

    Silently stops at the first truncated/corrupted region — some archived
    files are partially downloaded or corrupt; we prefer to continue with
    the events we could parse rather than raising.
    """
    try:
        with gzip.open(path, "rt", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue
    except (EOFError, OSError):
        # Truncated gzip or IO failure — stop yielding, keep whatever we got.
        return


# ---------------------------------------------------------------------------
# Aggregation: repo-day panel from one or more hourly files
# ---------------------------------------------------------------------------

@dataclass
class RepoDayAgg:
    """Per-(repo_id, date_utc) aggregate of signals we care about."""
    repo_id: int
    repo_name: str = ""
    date: str = ""  # yyyy-mm-dd UTC
    human_commits: int = 0
    bot_commits: int = 0
    distinct_authors: set[str] = field(default_factory=set)
    issues_opened: int = 0
    issues_closed: int = 0
    issue_comments: int = 0
    prs_opened: int = 0
    prs_closed: int = 0
    prs_merged: int = 0
    pr_review_comments: int = 0
    stars: int = 0
    forks: int = 0
    releases: int = 0
    member_changes: int = 0


def aggregate_hour(path: Path, agg: dict[tuple, RepoDayAgg]) -> None:
    """Update agg in place with events from one hourly file."""
    for e in iter_events(path):
        etype = e.get("type")
        if etype not in WANTED_TYPES:
            continue
        repo = e.get("repo") or {}
        rid = repo.get("id")
        if rid is None:
            continue
        ts = e.get("created_at")
        if not ts:
            continue
        day = ts[:10]  # UTC yyyy-mm-dd
        key = (rid, day)
        r = agg.get(key)
        if r is None:
            r = RepoDayAgg(repo_id=int(rid), repo_name=repo.get("name", ""), date=day)
            agg[key] = r

        actor = (e.get("actor") or {})
        actor_login = actor.get("login")

        if etype == "PushEvent":
            payload = e.get("payload") or {}
            h = human_distinct_commits(e)
            b = max(0, (payload.get("distinct_size") or 0) - h)
            r.human_commits += h
            r.bot_commits += b
            if actor_login and not is_bot(actor_login):
                r.distinct_authors.add(actor_login)
            for c in payload.get("commits", []) or []:
                author = (c.get("author") or {})
                name = author.get("name") or author.get("email", "")
                if name and not is_bot(name):
                    r.distinct_authors.add(name.lower())
        elif etype == "IssuesEvent":
            action = (e.get("payload") or {}).get("action")
            if action == "opened":
                r.issues_opened += 1
            elif action == "closed":
                r.issues_closed += 1
        elif etype == "IssueCommentEvent":
            r.issue_comments += 1
        elif etype == "PullRequestEvent":
            payload = e.get("payload") or {}
            action = payload.get("action")
            if action == "opened":
                r.prs_opened += 1
            elif action == "closed":
                r.prs_closed += 1
                if (payload.get("pull_request") or {}).get("merged"):
                    r.prs_merged += 1
        elif etype == "PullRequestReviewCommentEvent":
            r.pr_review_comments += 1
        elif etype == "WatchEvent":
            r.stars += 1
        elif etype == "ForkEvent":
            r.forks += 1
        elif etype == "ReleaseEvent":
            r.releases += 1
        elif etype == "MemberEvent":
            r.member_changes += 1


def agg_to_dataframe(agg: dict[tuple, RepoDayAgg]) -> pd.DataFrame:
    """Flatten the aggregate dict to a pandas DataFrame."""
    rows = []
    for r in agg.values():
        rows.append({
            "repo_id": r.repo_id,
            "repo_name": r.repo_name,
            "date": r.date,
            "human_commits": r.human_commits,
            "bot_commits": r.bot_commits,
            "distinct_authors": len(r.distinct_authors),
            "issues_opened": r.issues_opened,
            "issues_closed": r.issues_closed,
            "issue_comments": r.issue_comments,
            "prs_opened": r.prs_opened,
            "prs_closed": r.prs_closed,
            "prs_merged": r.prs_merged,
            "pr_review_comments": r.pr_review_comments,
            "stars": r.stars,
            "forks": r.forks,
            "releases": r.releases,
            "member_changes": r.member_changes,
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Label generation
# ---------------------------------------------------------------------------

def label_abandonment(
    panel: pd.DataFrame,
    prediction_dates: list[str],
    horizon_days: int = 365,
    active_commits_threshold: int = 20,
    active_window_days: int = 180,
) -> pd.DataFrame:
    """Given a repo-day panel, generate (repo_id, T, label) rows for each T.

    label = 1 iff in [T, T+H) there are 0 human commits, conditional on
      ≥active_commits_threshold human commits in [T-active_window_days, T).
    Repos not meeting the activity precondition are dropped (not in output).
    """
    # Ensure date as datetime
    panel = panel.copy()
    panel["date_dt"] = pd.to_datetime(panel["date"])

    rows = []
    for T_str in prediction_dates:
        T = pd.Timestamp(T_str)
        T_minus = T - pd.Timedelta(days=active_window_days)
        T_plus = T + pd.Timedelta(days=horizon_days)

        # active window
        aw = panel[(panel["date_dt"] >= T_minus) & (panel["date_dt"] < T)]
        active_commits = aw.groupby("repo_id")["human_commits"].sum()
        active_repos = set(active_commits[active_commits >= active_commits_threshold].index)

        # forward window
        fw = panel[(panel["date_dt"] >= T) & (panel["date_dt"] < T_plus)]
        fwd_commits = fw.groupby("repo_id")["human_commits"].sum().to_dict()

        for rid in active_repos:
            future = fwd_commits.get(rid, 0)
            rows.append({
                "repo_id": rid,
                "T": T_str,
                "active_commits_prior_180d": int(active_commits[rid]),
                "future_human_commits_365d": int(future),
                "label_abandoned": int(future == 0),
            })
    return pd.DataFrame(rows)
