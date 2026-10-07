import os
import requests
from dotenv import load_dotenv

load_dotenv("backend/.env")
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SECRET_KEY")
print("Supabase URL:", url)

upload_url = f"{url}/storage/v1/object/student-audio/test_sync.json"
headers = {
    "Authorization": f"Bearer {key}",
    "apiKey": key,
    "Content-Type": "application/json",
    "x-upsert": "true"
}

res = requests.post(upload_url, headers=headers, data='{"status": "ok", "test": 123}'.encode("utf-8"), timeout=10)
print("Upload status:", res.status_code, res.text)

if res.status_code in [200, 201]:
    download_url = f"{url}/storage/v1/object/public/student-audio/test_sync.json"
    res_down = requests.get(download_url, timeout=10)
    print("Download status:", res_down.status_code, res_down.text)
