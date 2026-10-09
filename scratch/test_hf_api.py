import urllib.request
import json

urls_to_test = [
    'https://agrse-fluent-english-backend.hf.space/api/admin/login',
    'https://agrse-fluent-english-backend.hf.space/admin/login',
    'https://fluent.augusttrung.com/api/admin/login',
]

payload = json.dumps({"email": "superadmin@fluent.edu.vn", "password": "superadmin123"}).encode('utf-8')

for url in urls_to_test:
    print(f"Testing URL: {url}")
    try:
        req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            body = response.read().decode('utf-8')
            print(f"  [SUCCESS {response.status}]: {body[:200]}")
    except urllib.error.HTTPError as e:
        print(f"  [HTTP ERROR {e.code}]: {e.read().decode('utf-8')[:200]}")
    except Exception as ex:
        print(f"  [ERROR]: {str(ex)}")
