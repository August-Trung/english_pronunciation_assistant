"""Store assignment images independently of temporary image-generation URLs."""
import hashlib
import io
import os
import ftplib
import ssl
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import requests
from PIL import Image, UnidentifiedImageError


BUCKET = 'assignment-images'
MAX_BYTES = 10 * 1024 * 1024
MAX_PIXELS = 20_000_000


class PictureStorageError(RuntimeError):
    pass


def storage_config():
    base = os.getenv('SUPABASE_URL', '').strip().rstrip('/')
    key = os.getenv('SUPABASE_SECRET_KEY', '').strip()
    if not base or not key:
        raise PictureStorageError('Permanent image storage is unavailable. Please contact the administrator.')
    return base, {'Authorization': f'Bearer {key}', 'apikey': key}


def store_picture_ftp(payload, filename):
    """Optional durable 123host storage, with credentials provided only by secrets."""
    host = os.getenv('PICTURE_FTP_HOST', '').strip()
    user = os.getenv('PICTURE_FTP_USER', '').strip()
    password = os.getenv('PICTURE_FTP_PASSWORD', '')
    directory = os.getenv('PICTURE_FTP_DIRECTORY', '').strip()
    public_base = os.getenv('PICTURE_PUBLIC_BASE_URL', '').strip().rstrip('/')
    if not all((host, user, password, directory, public_base)) or urlsplit(public_base).scheme != 'https':
        raise PictureStorageError('Permanent image storage is not configured. Please contact the administrator.')

    # Try direct HTTPS upload receiver on 123host (bypasses cloud container outbound port 21 firewalls)
    try:
        endpoint = f'{public_base}/store_image.php?filename={filename}'
        res = requests.post(
            endpoint,
            data=payload,
            headers={'Authorization': f'Bearer {password}', 'Content-Type': 'image/webp'},
            timeout=15
        )
        if res.status_code == 200 and res.json().get('status') == 'success':
            return f'{public_base}/{filename}'
    except Exception:
        pass

    try:
        with ftplib.FTP_TLS(timeout=30, context=ssl.create_default_context()) as ftp:
            ftp.connect(host, int(os.getenv('PICTURE_FTP_PORT', '21')))
            ftp.login(user, password)
            ftp.prot_p()
            ftp.cwd(directory)
            ftp.voidcmd('TYPE I')
            try:
                exists = ftp.size(filename) == len(payload)
            except ftplib.error_perm:
                exists = False
            if not exists:
                # Publish the finished file atomically; never expose a half-written picture.
                import uuid
                pending = filename + '.' + uuid.uuid4().hex + '.tmp'
                ftp.storbinary('STOR ' + pending, io.BytesIO(payload))
                ftp.rename(pending, filename)
    except (OSError, ftplib.Error, ValueError) as exc:
        raise PictureStorageError(f'Permanent image storage is temporarily unavailable: {exc}. Please try again.') from exc
    return f'{public_base}/{filename}'


def store_picture_bytes(content):
    """Validate/re-encode raster bytes, then save to durable project storage."""
    if not content or len(content) > MAX_BYTES:
        raise PictureStorageError('Please use an image smaller than 10 MB.')
    try:
        with Image.open(io.BytesIO(content)) as image:
            if image.width * image.height > MAX_PIXELS or min(image.size) < 64:
                raise PictureStorageError('The image dimensions are not supported.')
            image.load()
            output = io.BytesIO()
            image.convert('RGB').save(output, format='WEBP', quality=95)
            payload = output.getvalue()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise PictureStorageError('The service did not return a valid image. Please try again.') from exc
    filename = hashlib.sha256(payload).hexdigest() + '.webp'
    if os.getenv('PICTURE_STORAGE_BACKEND', 'supabase').lower() == 'ftp':
        return store_picture_ftp(payload, filename)
    base, headers = storage_config()
    try:
        bucket = requests.get(f'{base}/storage/v1/bucket/{BUCKET}', headers=headers, timeout=20)
        if bucket.status_code == 404:
            created = requests.post(f'{base}/storage/v1/bucket', headers=headers,
                                    json={'id': BUCKET, 'name': BUCKET, 'public': True}, timeout=20)
            if created.status_code not in (200, 201, 409):
                raise PictureStorageError('Could not initialize permanent image storage.')
        elif bucket.status_code != 200:
            raise PictureStorageError('Could not access permanent image storage.')
        elif bucket.json().get('public') is False:
            raise PictureStorageError('The assignment image bucket requires public image access. Please contact the administrator.')
        saved = requests.post(f'{base}/storage/v1/object/{BUCKET}/{filename}',
                              headers={**headers, 'Content-Type': 'image/webp', 'x-upsert': 'false'},
                              data=payload, timeout=30)
        # A content-addressed object already present is the same image.
        duplicate = False
        if saved.status_code in (400, 409):
            try:
                duplicate = saved.json().get('statusCode') in ('409', 409)
            except ValueError:
                pass
        if saved.status_code not in (200, 201) and not duplicate:
            raise PictureStorageError('Could not save the image. Please try again before assigning homework.')
    except requests.RequestException as exc:
        raise PictureStorageError('Permanent image storage is temporarily unavailable. Please try again.') from exc
    return f'{base}/storage/v1/object/public/{BUCKET}/{filename}'


def is_stored_picture(url):
    if os.getenv('PICTURE_STORAGE_BACKEND', 'supabase').lower() == 'ftp':
        base = os.getenv('PICTURE_PUBLIC_BASE_URL', '').strip().rstrip('/')
        prefix = urlsplit(base).path.rstrip('/') + '/'
    else:
        base = os.getenv('SUPABASE_URL', '').strip().rstrip('/')
        prefix = f'/storage/v1/object/public/{BUCKET}/'
    if not base:
        return False
    expected = urlsplit(base)
    actual = urlsplit(url)
    name = actual.path.removeprefix(prefix)
    return (actual.scheme == expected.scheme and actual.netloc == expected.netloc
            and actual.path.startswith(prefix) and not actual.query and not actual.fragment
            and len(name) == 69 and name.endswith('.webp')
            and all(c in '0123456789abcdef' for c in name[:-5]))


def generated_image_host(url):
    parsed = urlsplit(url)
    host = parsed.hostname or ''
    return (parsed.scheme == 'https' and not parsed.username and not parsed.password
            and (host == 'black-forest-labs-flux-1-schnell.hf.space'
                 or host == 'huggingface.co' or host.endswith('.huggingface.co')
                 or host.endswith('.hf.co')))


def persist_picture_url(url):
    """Accept owned objects, legacy local uploads, or trusted FLUX download URLs."""
    if is_stored_picture(url):
        return url
    if url.startswith('/uploads/picture_practice/'):
        root = (Path(__file__).parent / 'uploads' / 'picture_practice').resolve()
        image_path = (root / url.removeprefix('/uploads/picture_practice/')).resolve()
        if not image_path.is_relative_to(root) or not image_path.is_file():
            raise PictureStorageError('The uploaded image is no longer available. Please upload it again.')
        return store_picture_bytes(image_path.read_bytes())
    if not generated_image_host(url):
        raise PictureStorageError('Please generate a new FLUX image or upload a picture before assigning homework.')
    try:
        for _ in range(4):
            # Validate every redirect before requesting it; never send storage credentials here.
            if not generated_image_host(url):
                raise PictureStorageError('The image service returned an unsupported download location.')
            with requests.get(url, timeout=45, stream=True, allow_redirects=False) as response:
                if response.status_code in (301, 302, 303, 307, 308):
                    url = urljoin(url, response.headers.get('Location', ''))
                    continue
                if response.status_code != 200:
                    raise PictureStorageError('The generated image could not be downloaded. Please try again.')
                chunks = []
                size = 0
                for chunk in response.iter_content(64 * 1024):
                    size += len(chunk)
                    if size > MAX_BYTES:
                        raise PictureStorageError('The generated image exceeds the 10 MB limit.')
                    chunks.append(chunk)
                return store_picture_bytes(b''.join(chunks))
    except requests.RequestException as exc:
        raise PictureStorageError('The image service is temporarily unavailable. Please try again.') from exc
    raise PictureStorageError('The image service returned too many redirects.')
