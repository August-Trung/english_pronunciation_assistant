import io
import os
import sys
import unittest
import wave
from pathlib import Path
from unittest.mock import Mock, patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend' / 'app'))
import audio_storage as storage

class AudioStorageTests(unittest.TestCase):
    def setUp(self):
        b = io.BytesIO()
        with wave.open(b, 'wb') as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000); w.writeframes(b'\0\0' * 160)
        self.content = b.getvalue()
        self.env = patch.dict(os.environ, {'AUDIO_STORAGE_URL': 'https://media.example.test/store_audio.php',
            'AUDIO_PUBLIC_BASE_URL': 'https://media.example.test/audio', 'AUDIO_STORAGE_TOKEN': 'test-only'})
        self.env.start(); self.addCleanup(self.env.stop)

    def run_upload(self, downloaded=None, post_status=200, get_status=200):
        response = Mock(status_code=post_status)
        response.json.return_value = {'status': 'success'}
        saved = Mock(status_code=get_status)
        saved.iter_content.return_value = [self.content if downloaded is None else downloaded]
        context = Mock(); context.__enter__ = Mock(return_value=saved); context.__exit__ = Mock(return_value=False)
        with patch.object(storage.requests, 'post', return_value=response) as post, patch.object(storage.requests, 'get', return_value=context):
            url = storage.store_submission_audio(self.content)
            self.assertFalse(post.call_args.kwargs['allow_redirects'])
            self.assertEqual(post.call_args.kwargs['headers']['Content-Type'], 'audio/wav')
            return url

    def test_verified_recording_returns_owned_random_url(self):
        url = self.run_upload()
        self.assertRegex(url, r'^https://media.example.test/audio/[0-9a-f]{64}\.wav$')

    def test_corrupt_remote_bytes_never_return_success(self):
        with self.assertRaises(storage.AudioStorageError): self.run_upload(downloaded=b'corrupt')

    def test_failed_upload_never_returns_success(self):
        with self.assertRaises(storage.AudioStorageError): self.run_upload(post_status=503)

    def test_redirected_download_never_returns_success(self):
        with self.assertRaises(storage.AudioStorageError): self.run_upload(get_status=302)

    def test_invalid_audio_or_missing_configuration_is_rejected(self):
        with self.assertRaises(storage.AudioStorageError): storage.store_submission_audio(b'not audio')
        with patch.dict(os.environ, {'AUDIO_STORAGE_TOKEN': ''}):
            with self.assertRaises(storage.AudioStorageError): storage.store_submission_audio(self.content)
