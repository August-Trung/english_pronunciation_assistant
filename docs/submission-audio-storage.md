# Durable homework recordings

Configure backend secrets AUDIO_STORAGE_TOKEN, AUDIO_STORAGE_URL (HTTPS receiver),
and AUDIO_PUBLIC_BASE_URL (same HTTPS origin). Receiver accepts POST audio/mpeg with
Bearer authentication and filename query: 64 random hex characters plus .mp3.
It must validate MP3 audio (and keep legacy WAV playback), limit to 64 MB, publish atomically, disable directory
listing/execution, and return JSON {"status":"success"}. Never commit credentials.

Backend grades the original WAV, then encodes an MP3 mono 64 kbps archive and uploads it and downloads the published
object to verify its SHA-256 and length before inserting the submission and saved
assessment. Failure returns 503 without a submission row; the existing frontend
keeps its in-memory recording draft for retry while the page remains open. There
is no successful fallback to ephemeral Hugging Face disk. Input limit is 64 MB.

Deploy app/audio_storage.py with app/main.py after receiver/configuration is ready.
Preserve live database and media before any container restart. Do not publish raw
account snapshots in a public repository. This does not migrate earlier temporary
recordings or recover files already lost. URL filenames are unguessable but anyone
holding the URL can play it; they contain no student identifiers.

The compressed archive is about 0.48 MB/minute. AI assessment continues to use
the original WAV before compression. Earlier WAV objects are retained unchanged.
FFmpeg with libmp3lame (already used by the backend audio pipeline) is required.
