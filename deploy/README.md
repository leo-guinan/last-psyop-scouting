# Last Psyop bounded YouTube transcription worker

This is a manual-enqueue, single-worker pipeline for public YouTube videos.

## Safety and rate limits

- One queue worker; no concurrency.
- yt-dlp request sleep: 1 second, media-request sleep: 5–12 seconds, bounded retries.
- ElevenLabs calls are serialized with a persisted 10-second minimum interval.
- 429/5xx responses retry at 30s, 90s, 270s; maximum 3 attempts.
- No cookies, authenticated YouTube sessions, or private videos.
- Downloaded media is deleted after each job; transcript JSON and receipts remain.
- The systemd service polls an empty queue and performs no network work until jobs are explicitly enqueued.

## VPS paths

- Source: `/opt/last-psyop-transcriber/app/youtube_transcription_worker.py`
- State: `/var/lib/last-psyop-transcriber/queue.sqlite3`
- Transcripts: `/var/lib/last-psyop-transcriber/transcripts/`
- Receipts: `/var/lib/last-psyop-transcriber/receipts/`
- Secret: `/etc/last-psyop-transcriber/elevenlabs.env` (mode 0600, service user only)

## Operator commands

```bash
sudo -u lastpsyop /opt/last-psyop-transcriber/venv/bin/python \
  /opt/last-psyop-transcriber/app/youtube_transcription_worker.py status

sudo -u lastpsyop /opt/last-psyop-transcriber/venv/bin/python \
  /opt/last-psyop-transcriber/app/youtube_transcription_worker.py enqueue-channel \
  'https://www.youtube.com/@kat_the_vat/videos' --limit 5

systemctl status last-psyop-transcriber
journalctl -u last-psyop-transcriber -f
```

Do not enqueue a whole channel until a pilot has passed transcript-quality and cost review.
