#!/usr/bin/env python3
"""Rate-limited YouTube -> ElevenLabs Scribe queue worker.

The worker is intentionally single-threaded. It stores queue state in SQLite,
keeps transcript JSON/receipts, and deletes downloaded media after each bounded
attempt so the VPS does not become a small, sad video warehouse.
"""
from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import json
import os
import re
import sqlite3
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any

import requests
try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    YouTubeTranscriptApi = None

ROOT = Path(os.environ.get("TRANSCRIBER_ROOT", "/var/lib/last-psyop-transcriber"))
DB = ROOT / "queue.sqlite3"
MEDIA = ROOT / "media"
OUT = ROOT / "transcripts"
RECEIPTS = ROOT / "receipts"
LOCK = ROOT / "worker.lock"
YT_SLEEP = float(os.environ.get("YTDLP_SLEEP_SECONDS", "8"))
ELEVEN_SLEEP = float(os.environ.get("ELEVENLABS_MIN_INTERVAL_SECONDS", "10"))
MAX_ATTEMPTS = int(os.environ.get("TRANSCRIBER_MAX_ATTEMPTS", "3"))
YTDLP = os.environ.get("YTDLP_BIN", "yt-dlp")
RETRY_STATUSES = {429, 500, 502, 503, 504}


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def db() -> sqlite3.Connection:
    ROOT.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.executescript("""
    CREATE TABLE IF NOT EXISTS jobs (
      id TEXT PRIMARY KEY,
      video_url TEXT UNIQUE NOT NULL,
      video_id TEXT,
      title TEXT,
      status TEXT NOT NULL,
      attempts INTEGER NOT NULL DEFAULT 0,
      next_attempt_at REAL NOT NULL DEFAULT 0,
      error TEXT,
      transcript_path TEXT,
      receipt_path TEXT,
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
    """)
    return con


def video_id(url: str) -> str | None:
    m = re.search(r"(?:v=|youtu\.be/|/shorts/|/embed/)([A-Za-z0-9_-]{6,})", url)
    return m.group(1) if m else None


def enqueue(con: sqlite3.Connection, url: str, title: str | None = None) -> str:
    jid = str(uuid.uuid4())
    ts = now()
    try:
        con.execute("INSERT INTO jobs(id,video_url,video_id,title,status,created_at,updated_at) VALUES(?,?,?,?,?,?,?)",
                    (jid, url, video_id(url), title, "queued", ts, ts))
        con.commit()
        return jid
    except sqlite3.IntegrityError:
        row = con.execute("SELECT id FROM jobs WHERE video_url=?", (url,)).fetchone()
        return row["id"]


def enqueue_channel(con: sqlite3.Connection, channel_url: str, limit: int) -> int:
    cmd = [YTDLP, "--flat-playlist", "--playlist-end", str(limit),
           "--dump-single-json", "--skip-download", channel_url]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if p.returncode:
        raise RuntimeError(f"yt-dlp channel enumeration failed: {p.stderr[-1000:]}")
    data = json.loads(p.stdout)
    added = 0
    for entry in data.get("entries", []):
        if not entry or not entry.get("id"):
            continue
        url = f"https://www.youtube.com/watch?v={entry['id']}"
        before = con.execute("SELECT 1 FROM jobs WHERE video_url=?", (url,)).fetchone()
        enqueue(con, url, entry.get("title"))
        added += int(before is None)
    return added


def set_status(con: sqlite3.Connection, jid: str, status: str, **fields: Any) -> None:
    fields.update(status=status, updated_at=now())
    assignments = ",".join(f"{k}=?" for k in fields)
    con.execute(f"UPDATE jobs SET {assignments} WHERE id=?", (*fields.values(), jid))
    con.commit()


def claim(con: sqlite3.Connection) -> sqlite3.Row | None:
    row = con.execute("SELECT * FROM jobs WHERE status IN ('queued','retry') AND next_attempt_at<=? ORDER BY created_at LIMIT 1", (time.time(),)).fetchone()
    if not row:
        return None
    cur = con.execute("UPDATE jobs SET status='downloading',attempts=attempts+1,updated_at=? WHERE id=? AND status IN ('queued','retry')", (now(), row["id"]))
    con.commit()
    return con.execute("SELECT * FROM jobs WHERE id=?", (row["id"],)).fetchone() if cur.rowcount else None


def download(job: sqlite3.Row) -> tuple[Path, dict[str, Any]]:
    MEDIA.mkdir(parents=True, exist_ok=True)
    stem = MEDIA / job["id"]
    template = str(stem) + ".%(ext)s"
    cmd = [YTDLP, "--no-cache-dir", "--no-playlist", "--format", "bestaudio/best",
           "--extract-audio", "--audio-format", "mp3", "--audio-quality", "5",
           "--sleep-requests", "1", "--sleep-interval", "5", "--max-sleep-interval", "12",
           "--retries", "3", "--fragment-retries", "3", "--socket-timeout", "30",
           "--no-overwrites", "--write-info-json", "--output", template, job["video_url"]]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    if p.returncode:
        raise RuntimeError(f"yt-dlp download failed: {p.stderr[-1500:]}")
    files = list(MEDIA.glob(job["id"] + ".mp3"))
    if not files:
        raise RuntimeError("yt-dlp reported success but no MP3 was produced")
    metadata = {}
    info = MEDIA / (job["id"] + ".info.json")
    if info.exists():
        metadata = json.loads(info.read_text())
    return files[0], metadata


def fetch_captions(video_id_value: str | None) -> dict[str, Any] | None:
    if not video_id_value or YouTubeTranscriptApi is None:
        return None
    try:
        fetched = YouTubeTranscriptApi().fetch(video_id_value, languages=["en"])
    except Exception:
        return None
    snippets = [{"text": s.text, "start": s.start, "duration": s.duration} for s in fetched.snippets]
    return {"source": "youtube_caption_track", "language_code": fetched.language_code, "text": " ".join(s["text"] for s in snippets), "snippets": snippets}


def provider_wait(con: sqlite3.Connection) -> None:
    row = con.execute("SELECT value FROM meta WHERE key='last_elevenlabs_request' ").fetchone()
    if row:
        remaining = ELEVEN_SLEEP - (time.time() - float(row["value"]))
        if remaining > 0:
            time.sleep(remaining)
    con.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('last_elevenlabs_request',?)", (str(time.time()),))
    con.commit()


def _provider_request(**kwargs: Any) -> tuple[dict[str, Any], int]:
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        raise RuntimeError("ELEVENLABS_API_KEY is not configured")
    response = requests.post(
        "https://api.elevenlabs.io/v1/speech-to-text",
        headers={"xi-api-key": key, "User-Agent": "last-psyop-transcriber/1.0"},
        timeout=1800,
        **kwargs,
    )
    status = response.status_code
    if status >= 400:
        raise ProviderError(status, response.text[:500])
    return response.json(), status


def transcribe(con: sqlite3.Connection, media: Path) -> tuple[dict[str, Any], int]:
    with media.open("rb") as fh:
        return _provider_request(
            files={"file": (media.name, fh, "audio/mpeg")},
            data={"model_id": "scribe_v2", "diarize": "true", "tag_audio_events": "true", "timestamps_granularity": "word"},
        )


def transcribe_source_url(con: sqlite3.Connection, url: str) -> tuple[dict[str, Any], int]:
    return _provider_request(
        data={"source_url": url, "model_id": "scribe_v2", "diarize": "true", "tag_audio_events": "true", "timestamps_granularity": "word"},
    )


class ProviderError(RuntimeError):
    def __init__(self, status: int, detail: str):
        super().__init__(f"ElevenLabs HTTP {status}: {detail}")
        self.status = status


def persist_result(job: sqlite3.Row, result: dict[str, Any], status: int, metadata: dict[str, Any], started: str, acquisition: str, acquisition_error: str | None = None, provider: str = "elevenlabs", model: str = "scribe_v2", estimated_cost: float | None = None) -> tuple[Path, Path]:
    OUT.mkdir(parents=True, exist_ok=True); RECEIPTS.mkdir(parents=True, exist_ok=True)
    transcript_path = OUT / f"{job['id']}.json"
    receipt_path = RECEIPTS / f"{job['id']}.json"
    transcript_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    duration = result.get("audio_duration_secs")
    receipt = {"job_id": job["id"], "video_url": job["video_url"], "video_id": metadata.get("id") or job["video_id"], "title": metadata.get("title") or job["title"], "provider": provider, "model": model, "http_status": status, "audio_duration_secs": duration, "estimated_api_cost_usd": estimated_cost if estimated_cost is not None else round(float(duration or 0) / 3600 * 0.22, 4), "acquisition": acquisition, "acquisition_error": acquisition_error, "started_at_utc": started, "completed_at_utc": now(), "media_deleted_after_success": True}
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    return transcript_path, receipt_path


def process_one(con: sqlite3.Connection, job: sqlite3.Row) -> None:
    media = None
    result: dict[str, Any] = {}
    status = 0
    started = now()
    try:
        captions = fetch_captions(job["video_id"])
        if captions:
            transcript_path, receipt_path = persist_result(job, captions, 200, {"id": job["video_id"], "title": job["title"]}, started, "youtube_caption_track", provider="youtube", model="caption_track", estimated_cost=0.0)
            set_status(con, job["id"], "completed", transcript_path=str(transcript_path), receipt_path=str(receipt_path), error=None)
            print(json.dumps({"job_id": job["id"], "status": "completed", "acquisition": "youtube_caption_track", "caption_snippets": len(captions["snippets"])}))
            return
        try:
            media, metadata = download(job)
            acquisition = "vps_download"
            acquisition_error = None
        except Exception as download_exc:
            detail = str(download_exc)
            if "Sign in to confirm" not in detail and "not a bot" not in detail:
                raise
            # YouTube has challenged this VPS. Do not add cookies, proxies, or
            # retries; use ElevenLabs' documented public source_url fetch once.
            metadata = {"id": job["video_id"], "title": job["title"]}
            acquisition = "elevenlabs_source_url_fallback"
            acquisition_error = "youtube_download_blocked"
            set_status(con, job["id"], "transcribing", error=acquisition_error)
            provider_wait(con)
            result, status = transcribe_source_url(con, job["video_url"])
        if media is not None:
            set_status(con, job["id"], "transcribing", title=metadata.get("title") or job["title"], video_id=metadata.get("id") or job["video_id"])
            provider_wait(con)
            result, status = transcribe(con, media)
        transcript_path, receipt_path = persist_result(job, result, status, metadata, started, acquisition, acquisition_error)
        duration = result.get("audio_duration_secs")
        set_status(con, job["id"], "completed", transcript_path=str(transcript_path), receipt_path=str(receipt_path), error=None)
        print(json.dumps({"job_id": job["id"], "status": "completed", "duration": duration, "acquisition": acquisition}))
    except ProviderError as exc:
        if exc.status in RETRY_STATUSES and job["attempts"] < MAX_ATTEMPTS:
            delay = min(900, 30 * (3 ** max(0, job["attempts"] - 1)))
            set_status(con, job["id"], "retry", next_attempt_at=time.time() + delay, error=str(exc))
            print(json.dumps({"job_id": job["id"], "status": "retry", "http_status": exc.status, "retry_after_seconds": delay}))
        else:
            set_status(con, job["id"], "failed", error=str(exc))
            print(json.dumps({"job_id": job["id"], "status": "failed", "http_status": exc.status}))
    except Exception as exc:
        if job["attempts"] < MAX_ATTEMPTS:
            delay = min(900, 30 * (3 ** max(0, job["attempts"] - 1)))
            set_status(con, job["id"], "retry", next_attempt_at=time.time() + delay, error=str(exc))
            print(json.dumps({"job_id": job["id"], "status": "retry", "error": str(exc), "retry_after_seconds": delay}))
        else:
            set_status(con, job["id"], "failed", error=str(exc))
            print(json.dumps({"job_id": job["id"], "status": "failed", "error": str(exc)}))
    finally:
        # Remove the audio, metadata, and any partial download even when
        # yt-dlp failed before returning a media path.
        for path in MEDIA.glob(job["id"] + ".*"):
            try: path.unlink()
            except FileNotFoundError: pass


def status(con: sqlite3.Connection) -> None:
    rows = con.execute("SELECT status,COUNT(*) n FROM jobs GROUP BY status ORDER BY status").fetchall()
    print(json.dumps({r["status"]: r["n"] for r in rows}, sort_keys=True))


def run(con: sqlite3.Connection, poll: int) -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    with LOCK.open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        while True:
            job = claim(con)
            if job: process_one(con, job); continue
            time.sleep(poll)


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("enqueue"); p.add_argument("urls", nargs="+")
    p = sub.add_parser("enqueue-channel"); p.add_argument("url"); p.add_argument("--limit", type=int, default=10)
    sub.add_parser("status")
    p = sub.add_parser("run"); p.add_argument("--poll-seconds", type=int, default=30)
    args = ap.parse_args(); con = db()
    if args.cmd == "enqueue":
        for url in args.urls: print(json.dumps({"job_id": enqueue(con, url)}))
    elif args.cmd == "enqueue-channel": print(json.dumps({"added": enqueue_channel(con, args.url, args.limit)}))
    elif args.cmd == "status": status(con)
    else: run(con, args.poll_seconds)
    return 0

if __name__ == "__main__": sys.exit(main())
