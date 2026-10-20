import ast
import io
import json
import random
import ftplib
import re
import unittest
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

from PIL import Image
from backend.app import picture_storage as storage


class PictureStorageTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict('os.environ', {
            'SUPABASE_URL': 'https://review.supabase.co', 'SUPABASE_SECRET_KEY': 'test-only-key',
            'PICTURE_STORAGE_BACKEND': 'supabase'})
        self.env.start()
        self.addCleanup(self.env.stop)
        raw = io.BytesIO()
        Image.new('RGB', (128, 96), 'blue').save(raw, format='PNG')
        self.png = raw.getvalue()

    def response(self, status=200, data=None, content=None, headers=None):
        response = MagicMock()
        response.status_code = status
        response.json.return_value = data or {}
        response.headers = headers or {}
        response.iter_content.return_value = [content or self.png]
        response.__enter__.return_value = response
        return response

    @patch.object(storage.requests, 'post')
    @patch.object(storage.requests, 'get')
    def test_flux_download_becomes_content_addressed_project_object(self, get, post):
        get.side_effect = [self.response(), self.response()]
        post.return_value = self.response(200)
        result = storage.persist_picture_url('https://black-forest-labs-flux-1-schnell.hf.space/gradio_api/file=/tmp/scene.png')
        self.assertTrue(storage.is_stored_picture(result))
        self.assertNotIn('.hf.space', result)
        payload = post.call_args.kwargs['data']
        with Image.open(io.BytesIO(payload)) as image:
            self.assertEqual(image.size, (128, 96))
            self.assertEqual(image.format, 'WEBP')
        self.assertNotIn('Authorization', get.call_args_list[0].kwargs)

    @patch.object(storage.requests, 'post')
    @patch.object(storage.requests, 'get')
    def test_existing_content_is_reused_without_overwrite(self, get, post):
        get.return_value = self.response()
        post.return_value = self.response(400, {'statusCode': '409'})
        result = storage.store_picture_bytes(self.png)
        self.assertTrue(storage.is_stored_picture(result))
        self.assertEqual(post.call_args.kwargs['headers']['x-upsert'], 'false')
        before = get.call_count
        self.assertEqual(storage.persist_picture_url(result), result)
        self.assertEqual(get.call_count, before)

    @patch.object(storage.requests, 'get')
    def test_error_page_and_pollinations_are_not_saved(self, get):
        with self.assertRaises(storage.PictureStorageError):
            storage.store_picture_bytes(b'<html>Quota exceeded</html>')
        with self.assertRaises(storage.PictureStorageError):
            storage.persist_picture_url('https://image.pollinations.ai/prompt/scene')
        get.assert_not_called()

    @patch.object(storage.requests, 'get')
    def test_untrusted_redirect_is_not_followed(self, get):
        get.return_value = self.response(302, headers={'Location': 'http://127.0.0.1/private'})
        with self.assertRaises(storage.PictureStorageError):
            storage.persist_picture_url('https://black-forest-labs-flux-1-schnell.hf.space/scene.png')
        self.assertEqual(get.call_count, 1)

    @patch.object(storage.requests, 'post')
    @patch.object(storage.requests, 'get')
    def test_storage_failure_does_not_return_temporary_url(self, get, post):
        get.side_effect = [self.response(), self.response()]
        post.return_value = self.response(503)
        with self.assertRaises(storage.PictureStorageError):
            storage.persist_picture_url('https://black-forest-labs-flux-1-schnell.hf.space/scene.png')

    @patch.object(storage.ftplib, 'FTP_TLS')
    def test_123host_storage_publishes_complete_file_and_reuses_owned_url(self, factory):
        ftp = factory.return_value.__enter__.return_value
        ftp.size.side_effect = ftplib.error_perm('550 File not found')
        with patch.dict('os.environ', {
            'PICTURE_STORAGE_BACKEND': 'ftp', 'PICTURE_FTP_HOST': 'ftp.example.test',
            'PICTURE_FTP_USER': 'test-user', 'PICTURE_FTP_PASSWORD': 'test-only',
            'PICTURE_FTP_DIRECTORY': '/owned/uploads/assignment-images',
            'PICTURE_PUBLIC_BASE_URL': 'https://images.example.test/uploads/assignment-images'
        }):
            url = storage.store_picture_bytes(self.png)
            self.assertTrue(storage.is_stored_picture(url))
            self.assertEqual(storage.persist_picture_url(url), url)
            ftp.prot_p.assert_called_once()
            ftp.storbinary.assert_called_once()
            ftp.rename.assert_called_once()
            self.assertTrue(ftp.rename.call_args.args[0].endswith('.tmp'))
            self.assertEqual(ftp.rename.call_args.args[1], url.rsplit('/', 1)[1])
            self.assertEqual(factory.call_count, 1)

    def generator(self, result):
        tree = ast.parse(Path('backend/app/hf_service.py').read_text(encoding='utf-8'))
        node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'generate_picture_scenario')
        g = {'Dict': Dict, 'Any': Any, 'random': random, 're': re,
             'generate_flux_image_hf': Mock(return_value=result),
             'persist_picture_url': Mock(return_value='https://review.supabase.co/stored.webp'),
             'call_llm_json_with_retry': Mock(return_value={'title': 'Pets', 'image_gen_prompt': 'Pets', 'guiding_questions': ['Q1', 'Q2', 'Q3', 'Q4'], 'keywords': ['cat', 'dog', 'tree']})}
        exec(compile(ast.Module(body=[node], type_ignores=[]), 'picture_generator', 'exec'), g)
        return g

    def test_no_pollinations_fallback_in_either_generation_mode(self):
        for mode in ('ai_gen', 'search'):
            with self.subTest(mode=mode):
                g = self.generator(None)
                with self.assertRaisesRegex(RuntimeError, 'FLUX'):
                    g['generate_picture_scenario']('Pets', mode=mode)
                g['persist_picture_url'].assert_not_called()

    def test_all_successful_generation_modes_persist_before_returning(self):
        for mode in ('ai_gen', 'search', 'upload'):
            with self.subTest(mode=mode):
                g = self.generator('temporary-flux-url')
                result = g['generate_picture_scenario']('Pets', mode=mode, custom_image_url='uploaded-image')
                self.assertEqual(result['image_url'], 'https://review.supabase.co/stored.webp')
                g['persist_picture_url'].assert_called_once()


if __name__ == '__main__':
    unittest.main()
