# Data Acquisition — Practical Snippets

## Download one day of GH Archive

```bash
DAY=2023-04-15
for h in $(seq 0 23); do
  curl -sSL -o data/raw/${DAY}-${h}.json.gz https://data.gharchive.org/${DAY}-${h}.json.gz &
done
wait
```

## Parallel with xargs

```bash
printf "2023-04-15-%d.json.gz\n" $(seq 0 23) | \
  xargs -n1 -P8 -I{} curl -sSL -o data/raw/{} https://data.gharchive.org/{}
```

## Stream and filter events (no full decompress to disk)

```python
import gzip, json, urllib.request, io
from collections import Counter

URL = "https://data.gharchive.org/2023-04-15-14.json.gz"
WANT = {"PushEvent","PullRequestEvent","IssuesEvent","IssueCommentEvent",
        "WatchEvent","ForkEvent","ReleaseEvent","MemberEvent"}

commits_per_repo = Counter()
with urllib.request.urlopen(URL) as resp:
    with gzip.GzipFile(fileobj=io.BufferedReader(resp)) as gz:
        for line in gz:
            e = json.loads(line)
            if e["type"] not in WANT: continue
            if e["type"] == "PushEvent":
                commits_per_repo[e["repo"]["id"]] += e["payload"].get("distinct_size", 0)
```

## Bot filter

```python
BOT_SUFFIX = "[bot]"
KNOWN_BOTS = {"dependabot","renovate","renovate-bot","greenkeeper",
              "pre-commit-ci","github-actions","snyk-bot","allcontributors",
              "pyup-bot","imgbot","whitesource-bolt-for-github","mergify"}

def is_bot(login: str) -> bool:
    if not login: return True
    l = login.lower()
    return l.endswith(BOT_SUFFIX) or l in KNOWN_BOTS

def human_commits(push_event) -> int:
    return sum(1 for c in push_event["payload"].get("commits", [])
               if c.get("distinct") and not is_bot((c.get("author") or {}).get("name") or ""))
```

## GitHub REST fetch with rate handling

```python
import requests, time, os
S = requests.Session()
S.headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
S.headers["Accept"] = "application/vnd.github+json"

def gh(path, **params):
    while True:
        r = S.get(f"https://api.github.com{path}", params=params, timeout=30)
        if r.status_code == 202: time.sleep(5); continue
        if r.status_code == 403 and "rate limit" in r.text.lower():
            reset = int(r.headers.get("X-RateLimit-Reset", time.time()+60))
            time.sleep(max(1, reset - int(time.time()) + 2)); continue
        r.raise_for_status()
        return r.json()
```

## Libraries.io dump

```bash
curl -L -O "https://zenodo.org/records/3626071/files/libraries-1.6.0-2020-01-12.tar.gz"
# Extract just the repos file
tar -xzf libraries-1.6.0-2020-01-12.tar.gz \
    libraries-1.6.0-2020-01-12/repositories-1.6.0-2020-01-12.csv
```
