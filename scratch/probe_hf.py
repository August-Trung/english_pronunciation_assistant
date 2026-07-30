import urllib.request
import json

base = 'https://agrse-fluent-english-backend.hf.space'
endpoints = [
    ('/', 'GET'),
    ('/docs', 'GET'),
    ('/openapi.json', 'GET'),
    ('/api/leaderboard', 'GET'),
    ('/api/admin/login', 'POST'),
    ('/api/teacher/login', 'POST'),
]

for ep, method in endpoints:
    url = base + ep
    print(f"Testing {method} {url}")
    try:
        data = json.dumps({"email": "superadmin@fluent.edu.vn", "password": "superadmin123"}).encode('utf-8') if method == 'POST' else None
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'} if data else {})
        req.get_method = lambda: method
        with urllib.request.urlopen(req) as response:
            print(f"  --> STATUS {response.status}")
            if ep == '/openapi.json':
                open_api = json.loads(response.read().decode('utf-8'))
                print("  --> AVAILABLE API PATHS IN OPENAPI:")
                for path in open_api.get('paths', {}):
                    print("     ", path)
    except urllib.error.HTTPError as e:
        print(f"  --> HTTP ERROR {e.code}")
    except Exception as ex:
        print(f"  --> ERROR: {str(ex)}")
