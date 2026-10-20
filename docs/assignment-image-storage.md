# Durable assignment images

Generated images are downloaded immediately, validated as raster images, encoded
as WebP, and stored under a SHA-256 content name. Assignment records reference
that owned URL. Image generation/storage failures return HTTP 503 and do not
create an assignment or replace the previous scenario image. Pollinations is no
longer used for picture scenarios or redraws. Existing assignment/scenario images
are not automatically replaced on application startup.

## 123host configuration for the current deployment

Configure these values in the backend Space environment. Keep credentials in
Space Secrets, never in the repository or chat:

- `PICTURE_STORAGE_BACKEND=ftp`
- `PICTURE_FTP_HOST`, `PICTURE_FTP_USER`, `PICTURE_FTP_PASSWORD`: use the existing
  local configuration in `scratch/deploy_to_myhanh.py`.
- `PICTURE_FTP_PORT=21` (optional default).
- `PICTURE_FTP_DIRECTORY=/domains/myhanh.augusttrung.com/public_html/uploads/assignment-images`
- `PICTURE_PUBLIC_BASE_URL=https://myhanh.augusttrung.com/uploads/assignment-images`

The directory has been created and an upload/download smoke check passed with
verified FTPS and HTTPS. The backend uses encrypted FTPS data transfer, verifies
the certificate, and publishes each completed file by renaming a temporary file.
No dependency beyond the existing Pillow and Python standard library is needed.

The optional default `supabase` backend requires `SUPABASE_URL` and
`SUPABASE_SECRET_KEY`; it uses the `assignment-images` bucket. The current local
Supabase host fails DNS, so use the verified 123host configuration above.

## Deploy and verify

Deploy `app/main.py`, `app/hf_service.py`, and **`app/picture_storage.py`** together.
If the deployment has a root `hf_service.py`, sync it with `app/hf_service.py`.
Deploy the frontend build to the MyHanh directory on 123host.

Changing Space environment or deploying code may restart its ephemeral container.
Preserve the current online database and referenced local media first. Do not
publish raw account snapshots or password hashes in a public repository. A
destructive database restore needs the user's explicit confirmation.

Verify a successful FLUX generation returns a URL beneath the configured owned
storage prefix. Assign it, reload the teacher/student lists and verify they show
the same image. Simulate a generation failure and verify that no Pollinations URL
or error image replaces the prior picture. Old expired external images cannot be
recovered automatically; regenerate or upload their replacements explicitly.

Local checks:

```powershell
python -m unittest discover -s tests -p test_picture_storage.py -v
python -m unittest discover -s tests -p test_homework_regressions.py -v
cd frontend
npm run build
```
