#!/usr/bin/env python3
"""Bounded read-only X/Bluesky search with provenance receipts.

X uses the VPS's configured xurl app/account. Bluesky uses its public API and
requires no credential. This script never posts, likes, follows, or mutates.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_QUERIES = ["Netwar Con", "Last Psyop", "psyop hackathon"]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def x_search(query: str, limit: int, app: str, username: str) -> dict[str, Any]:
    cmd = ["xurl", "--app", app, "--auth", "oauth2", "--username", username,
           "search", query, "-n", str(limit)]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    result = {"query": query, "app": app, "username": username,
              "command": "xurl search", "exit_code": p.returncode,
              "stdout": p.stdout, "stderr": p.stderr}
    try:
        result["json"] = json.loads(p.stdout)
    except json.JSONDecodeError:
        pass
    return result


def bluesky_search(query: str, limit: int) -> dict[str, Any]:
    params = urllib.parse.urlencode({"q": query, "limit": str(limit)})
    url = "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts?" + params
    result = {"query": query, "url": url}
    req = urllib.request.Request(url, headers={"User-Agent": "last-psyop-scouting/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result["http_status"] = response.status
            result["json"] = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        result["http_status"] = exc.code
        result["error"] = str(exc)
    except Exception as exc:  # preserve transport boundary in receipt
        result["error"] = repr(exc)
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", action="append", dest="queries")
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--skip-x", action="store_true")
    ap.add_argument("--skip-bluesky", action="store_true")
    ap.add_argument("--x-app", default="marvin-x")
    ap.add_argument("--x-username", default="marvin_panics")
    args = ap.parse_args()
    if args.limit < 1 or args.limit > 100:
        ap.error("--limit must be between 1 and 100")
    queries = args.queries or DEFAULT_QUERIES
    receipt = {"captured_at_utc": now_utc(), "scope": "bounded public search; read-only",
               "queries": queries, "limit": args.limit, "x": [], "bluesky": []}
    if not args.skip_x:
        for query in queries:
            receipt["x"].append(x_search(query, args.limit, args.x_app, args.x_username))
    if not args.skip_bluesky:
        for query in queries:
            receipt["bluesky"].append(bluesky_search(query, args.limit))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    summary = {
        "out": str(args.out),
        "captured_at_utc": receipt["captured_at_utc"],
        "x": [(r["query"], r["exit_code"], r.get("json", {}).get("data", []) and len(r["json"]["data"])) for r in receipt["x"]],
        "bluesky": [(r["query"], r.get("http_status"), len(r.get("json", {}).get("posts", []))) for r in receipt["bluesky"]],
    }
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main())
