"""Persist compressed submission recordings on durable HTTPS storage before database success."""
import hashlib
import io
import os
import secrets
import wave
from urllib.parse import urlsplit

import requests
from pydub import AudioSegment

MAX_AUDIO_BYTES = 64 * 1024 * 1024


class AudioStorageError(RuntimeError):
    pass


def store_submission_audio(content):
    error = 'Could not securely save your recording. Your submission was not completed. Please try again.'
    if not content or len(content) > MAX_AUDIO_BYTES:
        raise AudioStorageError('The recording exceeds the supported 64 MB size. Please record a shorter attempt.')
    try:
        with wave.open(io.BytesIO(content), 'rb') as recording:
            if recording.getcomptype() != 'NONE' or recording.getnframes() <= 0:
                raise ValueError('Invalid PCM recording')
    except (wave.Error, EOFError, ValueError) as exc:
        raise AudioStorageError('The recording could not be processed. Please record again.') from exc
    endpoint = os.getenv('AUDIO_STORAGE_URL', '').strip()
    base = os.getenv('AUDIO_PUBLIC_BASE_URL', '').strip().rstrip('/')
    token = os.getenv('AUDIO_STORAGE_TOKEN', '')
    parts = [urlsplit(endpoint), urlsplit(base)]
    if (not token or any(p.scheme != 'https' or not p.hostname or p.username or p.password or p.query or p.fragment for p in parts)
            or parts[0].netloc != parts[1].netloc):
        raise AudioStorageError('Permanent recording storage is not configured. Please contact the administrator.')
    # Speech assessment has already used the original WAV. Only the archive is lossy.
    try:
        recording = AudioSegment.from_file(io.BytesIO(content), format='wav').set_channels(1)
        encoded = io.BytesIO()
        recording.export(encoded, format='mp3', bitrate='64k', codec='libmp3lame',
                         parameters=['-map_metadata', '-1'])
        content = encoded.getvalue()
        if not content or len(content) > MAX_AUDIO_BYTES:
            raise ValueError('Invalid compressed recording')
    except Exception as exc:
        raise AudioStorageError('Could not prepare your recording for permanent storage. Please try again.') from exc
    filename = secrets.token_hex(32) + '.mp3'
    url = base + '/' + filename
    try:
        response = requests.post(endpoint, params={'filename': filename}, data=content,
                                 headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'audio/mpeg'},
                                 timeout=60, allow_redirects=False)
        if response.status_code != 200 or response.json().get('status') != 'success':
            raise AudioStorageError(error)
        # Verify the published bytes before persisting a successful submission.
        with requests.get(url, stream=True, timeout=45, allow_redirects=False) as saved:
            if saved.status_code != 200:
                raise AudioStorageError(error)
            digest = hashlib.sha256()
            size = 0
            for chunk in saved.iter_content(64 * 1024):
                size += len(chunk)
                if size > len(content):
                    raise AudioStorageError(error)
                digest.update(chunk)
            if size != len(content) or digest.digest() != hashlib.sha256(content).digest():
                raise AudioStorageError(error)
    except (requests.RequestException, ValueError) as exc:
        raise AudioStorageError(error) from exc
    return url
