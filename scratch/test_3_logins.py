import urllib.request
import json
import time

time.sleep(3)

base_url = 'https://agrse-fluent-english-backend.hf.space'

test_cases = [
    {
        "role": "SUPER ADMIN",
        "url": f"{base_url}/api/admin/login",
        "email": "superadmin@fluent.edu.vn",
        "password": "superadmin123"
    },
    {
        "role": "SCHOOL ADMIN",
        "url": f"{base_url}/api/admin/login",
        "email": "admin@fluent.edu.vn",
        "password": "admin123"
    },
    {
        "role": "TEACHER / EDUCATOR",
        "url": f"{base_url}/api/teacher/login",
        "email": "teacher@fluent.edu.vn",
        "password": "teacher123"
    }
]

print("==================================================")
print("     LIVE HTTP LOGIN TEST FOR 3 ACCOUNTS")
print("==================================================\n")

all_passed = True
for test in test_cases:
    payload = json.dumps({"email": test["email"], "password": test["password"]}).encode('utf-8')
    req = urllib.request.Request(test["url"], data=payload, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data.get('status') == 'success':
                print(f"[PASS] {test['role']} LOGIN PASSED SUCCESSFULLY!")
                print(f"   - Email: {data['user']['email']}")
                print(f"   - Name: {data['user']['name']}")
                print(f"   - Role: {data['user']['role']}")
                print(f"   - User ID: {data['user']['id']}")
                print(f"   - Tenant ID: {data['user']['tenant_id']}\n")
            else:
                print(f"[FAIL] {test['role']} LOGIN FAILED: {data}\n")
                all_passed = False
    except Exception as e:
        print(f"[FAIL] {test['role']} HTTP ERROR: {e}\n")
        all_passed = False

if all_passed:
    print("ALL 3 ACCOUNTS PASSED LIVE HTTP LOGIN VERIFICATION 100%!")
else:
    print("SOME LOGIN TESTS FAILED!")
