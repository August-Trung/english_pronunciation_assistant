import requests

BASE = 'https://agrse-fluent-english-backend.hf.space'
res = requests.post(f'{BASE}/api/admin/login', json={'email': 'superadmin@fluent.edu.vn', 'password': 'superadmin123'})
print('Login status:', res.status_code)
token = res.json().get('token')
headers = {'Authorization': f'Bearer {token}'}

tenants_res = requests.get(f'{BASE}/api/admin/tenants', headers=headers)
print('Tenants status:', tenants_res.status_code)
data = tenants_res.json()
print("Response type:", type(data))
if isinstance(data, dict):
    print("Keys:", data.keys())
    tenants = data.get('tenants', [])
else:
    tenants = data

print(f'Fetched {len(tenants)} tenants:')
for t in tenants:
    if isinstance(t, dict):
        admin_str = t.get('admin_email') or '[NONE]'
        print(f" - ID: {t.get('id')}, Name: {t.get('name')}, Admin: {admin_str}")

# Test Onboarding
print("\n--- Testing Onboard School on Live HF Space ---")
onboard_res = requests.post(f'{BASE}/api/admin/tenants/onboard', headers=headers, json={
    "school_name": "Test Live Academy",
    "admin_email": "admin.live@academy.edu.vn",
    "admin_name": "Dean Live",
    "license_seats": 120,
    "license_expiry": "2029-12-31",
    "status": "active"
})
print("Onboard status:", onboard_res.status_code, onboard_res.json().get('status'))
new_tid = onboard_res.json().get('tenant_id')

if new_tid:
    # Test Lifecycle & Admin Update
    print("\n--- Testing Lifecycle & Admin Update on Live HF Space ---")
    update_res = requests.post(f'{BASE}/api/admin/tenants/{new_tid}/lifecycle', headers=headers, json={
        "status": "trial",
        "school_name": "Test Live Academy Renamed",
        "admin_email": "dean.renamed@academy.edu.vn",
        "admin_name": "Dean Renamed",
        "license_seats": 250,
        "license_expiry": "2030-01-01"
    })
    print("Lifecycle update status:", update_res.status_code, update_res.json())
    
    # Clean up test tenant
    del_res = requests.delete(f'{BASE}/api/admin/tenants/{new_tid}', headers=headers)
    print("Delete test tenant status:", del_res.status_code)

print("\n=== Live HF Space Verification Complete! ===")
