"""Unit tests for the OSS abandonment data loaders."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from data_loaders import (
    is_bot, human_distinct_commits, aggregate_hour,
    agg_to_dataframe, RepoDayAgg, gharchive_url,
)
from datetime import datetime


class TestIsBot:
    def test_bracket_bot_suffix(self):
        assert is_bot("dependabot[bot]")
        assert is_bot("github-actions[bot]")
        assert is_bot("codecov[bot]")

    def test_known_bot_logins(self):
        assert is_bot("dependabot")
        assert is_bot("renovate")
        assert is_bot("mergify")

    def test_case_insensitive(self):
        assert is_bot("Dependabot")
        assert is_bot("GITHUB-ACTIONS")

    def test_none_and_empty(self):
        assert is_bot(None)
        assert is_bot("")

    def test_human(self):
        assert not is_bot("torvalds")
        assert not is_bot("alice@example.com")


class TestHumanDistinctCommits:
    def _push(self, commits):
        return {"type": "PushEvent", "payload": {"distinct_size": len(commits),
                                                  "commits": commits}}

    def test_all_human(self):
        e = self._push([
            {"distinct": True, "author": {"name": "alice"}},
            {"distinct": True, "author": {"name": "bob"}},
        ])
        assert human_distinct_commits(e) == 2

    def test_skip_bot(self):
        e = self._push([
            {"distinct": True, "author": {"name": "alice"}},
            {"distinct": True, "author": {"name": "dependabot[bot]"}},
        ])
        assert human_distinct_commits(e) == 1

    def test_skip_non_distinct(self):
        e = self._push([
            {"distinct": True, "author": {"name": "alice"}},
            {"distinct": False, "author": {"name": "alice"}},
        ])
        assert human_distinct_commits(e) == 1

    def test_empty(self):
        assert human_distinct_commits(self._push([])) == 0


class TestGHArchiveURL:
    def test_padding(self):
        # Zero-hour must NOT be zero-padded
        dt = datetime(2024, 4, 9, 0)
        url = gharchive_url(dt)
        assert url.endswith("2024-04-09-0.json.gz")

    def test_double_digit_hour(self):
        dt = datetime(2024, 4, 9, 14)
        assert gharchive_url(dt).endswith("2024-04-09-14.json.gz")


class TestAggregateHour:
    def test_accumulates_push_event(self, tmp_path):
        import gzip, json
        p = tmp_path / "fake.json.gz"
        events = [
            {"type": "PushEvent", "repo": {"id": 1, "name": "a/b"},
             "created_at": "2024-04-01T10:00:00Z", "actor": {"login": "alice"},
             "payload": {"distinct_size": 2, "commits": [
                 {"distinct": True, "author": {"name": "alice"}},
                 {"distinct": True, "author": {"name": "alice"}},
             ]}},
            {"type": "WatchEvent", "repo": {"id": 1, "name": "a/b"},
             "created_at": "2024-04-01T11:00:00Z", "actor": {"login": "watcher"},
             "payload": {"action": "started"}},
            {"type": "IssuesEvent", "repo": {"id": 1, "name": "a/b"},
             "created_at": "2024-04-01T12:00:00Z", "actor": {"login": "alice"},
             "payload": {"action": "opened"}},
        ]
        with gzip.open(p, "wt") as fh:
            for e in events:
                fh.write(json.dumps(e) + "\n")

        agg = {}
        aggregate_hour(p, agg)
        assert (1, "2024-04-01") in agg
        r = agg[(1, "2024-04-01")]
        assert r.human_commits == 2
        assert r.stars == 1
        assert r.issues_opened == 1


class TestAggToDataframe:
    def test_round_trip(self):
        agg = {(1, "2024-04-01"): RepoDayAgg(
            repo_id=1, repo_name="a/b", date="2024-04-01",
            human_commits=5, stars=2, issues_opened=1,
        )}
        df = agg_to_dataframe(agg)
        assert len(df) == 1
        r = df.iloc[0]
        assert r["repo_id"] == 1
        assert r["human_commits"] == 5
        assert r["stars"] == 2
