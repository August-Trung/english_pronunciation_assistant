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
        self.encoded = b'ID3-test-mp3-payload'
        self.env = patch.dict(os.environ, {'AUDIO_STORAGE_URL': 'https://media.example.test/store_audio.php',
            'AUDIO_PUBLIC_BASE_URL': 'https://media.example.test/audio', 'AUDIO_STORAGE_TOKEN': 'test-only'})
        self.env.start(); self.addCleanup(self.env.stop)

    def run_upload(self, downloaded=None, post_status=200, get_status=200):
        response = Mock(status_code=post_status)
        response.json.return_value = {'status': 'success'}
        saved = Mock(status_code=get_status)
        saved.iter_content.return_value = [self.encoded if downloaded is None else downloaded]
        context = Mock(); context.__enter__ = Mock(return_value=saved); context.__exit__ = Mock(return_value=False)
        with patch.object(storage.AudioSegment, 'from_file') as encoder, patch.object(storage.requests, 'post', return_value=response) as post, patch.object(storage.requests, 'get', return_value=context):
            export = encoder.return_value.set_channels.return_value.export
            export.side_effect = lambda output, **kwargs: output.write(self.encoded)
            url = storage.store_submission_audio(self.content)
            self.assertEqual(post.call_args.kwargs['data'], self.encoded)
            self.assertEqual(export.call_args.kwargs['bitrate'], '64k')
            self.assertFalse(post.call_args.kwargs['allow_redirects'])
            self.assertEqual(post.call_args.kwargs['headers']['Content-Type'], 'audio/mpeg')
            return url

    def test_verified_recording_returns_owned_random_url(self):
        url = self.run_upload()
        self.assertRegex(url, r'^https://media.example.test/audio/[0-9a-f]{64}\.mp3$')

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

    def test_encoder_failure_prevents_upload(self):
        with patch.object(storage.AudioSegment, 'from_file', side_effect=RuntimeError('encoder failed')), patch.object(storage.requests, 'post') as post:
            with self.assertRaises(storage.AudioStorageError): storage.store_submission_audio(self.content)
            post.assert_not_called()

    def test_real_mp3_round_trip_is_mono_and_preserves_duration(self):
        from pydub.generators import Sine
        original = Sine(440).to_audio_segment(duration=2000).set_frame_rate(16000).set_channels(1)
        wav = io.BytesIO(); original.export(wav, format='wav')
        captured = {}
        def upload(*args, **kwargs):
            captured['bytes'] = kwargs['data']
            result = Mock(status_code=200); result.json.return_value = {'status': 'success'}
            return result
        def download(*args, **kwargs):
            result = Mock(status_code=200); result.iter_content.return_value = [captured['bytes']]
            context = Mock(); context.__enter__ = Mock(return_value=result); context.__exit__ = Mock(return_value=False)
            return context
        with patch.object(storage.requests, 'post', side_effect=upload), patch.object(storage.requests, 'get', side_effect=download):
            url = storage.store_submission_audio(wav.getvalue())
        decoded = storage.AudioSegment.from_file(io.BytesIO(captured['bytes']), format='mp3')
        self.assertEqual(decoded.channels, 1)
        self.assertLess(abs(len(decoded) - 2000), 50)
        self.assertLess(len(captured['bytes']), len(wav.getvalue()) * .4)
        self.assertTrue(url.endswith('.mp3'))
