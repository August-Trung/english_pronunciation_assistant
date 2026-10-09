import sys
import os
import json
import sqlite3

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "app"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from main import app, DB_PATH, init_db

init_db()
client = TestClient(app)

def run_tests():
    print("=" * 60)
    print("RUNNING P0 SECURITY & RBAC VERIFICATION SUITE")
    print("=" * 60)
    passed = 0
    total = 0

    def assert_test(name, condition, details=""):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f"[PASS] {name}")
        else:
            print(f"[FAIL] {name}: {details}")

    # TEST 1: Super Admin Login
    res1 = client.post("/api/admin/login", json={"email": "superadmin@fluent.edu.vn", "password": "superadmin123"})
    assert_test("1. Super Admin Login Success", res1.status_code == 200 and "token" in res1.json())
    super_token = res1.json().get("token", "")
    super_role = res1.json().get("user", {}).get("role")
    assert_test("1b. Super Admin Role Verified", super_role == "super_admin")

    # TEST 2: School Admin Login
    res2 = client.post("/api/admin/login", json={"email": "admin@fluent.edu.vn", "password": "admin123"})
    assert_test("2. School Admin Login Success", res2.status_code == 200 and "token" in res2.json())
    admin_token = res2.json().get("token", "")
    admin_tenant = res2.json().get("user", {}).get("tenant_id")
    assert_test("2b. School Admin Tenant Isolated", str(admin_tenant) == "1")

    # TEST 3: Educator Login
    res3 = client.post("/api/teacher/login", json={"email": "teacher@fluent.edu.vn", "password": "teacher123"})
    assert_test("3. Educator Login Success", res3.status_code == 200 and "token" in res3.json())

    # TEST 4: Wrong Password Rejection
    res4 = client.post("/api/admin/login", json={"email": "admin@fluent.edu.vn", "password": "WrongPassword999!"})
    assert_test("4. Wrong Password Rejection (401)", res4.status_code == 401)

    # TEST 5: Backdoor Elimination (Fake email rejection)
    res5 = client.post("/api/admin/login", json={"email": "hacker@evil.com", "password": "superadmin123"})
    assert_test("5. Fake User Rejection (401)", res5.status_code == 401)

    # TEST 6: Unauthenticated Request Blocked
    res6 = client.get("/api/admin/overview")
    assert_test("6. Request Without Token Blocked (401)", res6.status_code == 401)

    # TEST 7: Tampered Token Rejected
    res7 = client.get("/api/admin/overview", headers={"Authorization": "Bearer fake.tampered.token"})
    assert_test("7. Tampered Token Blocked (401)", res7.status_code == 401)

    # TEST 8: Super Admin Endpoint Protected against School Admin
    res8 = client.post(
        "/api/admin/tenants/create",
        json={"name": "Hacker Academy", "license_seats": 500},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert_test("8. Privilege Escalation Denied (403)", res8.status_code == 403)

    # TEST 9: Super Admin Can Create Tenant
    res9 = client.post(
        "/api/admin/tenants/create",
        json={"name": "High School Olympia", "license_seats": 250},
        headers={"Authorization": f"Bearer {super_token}"}
    )
    assert_test("9. Super Admin Tenant Creation (200)", res9.status_code == 200)
    new_tenant_id = res9.json().get("tenant_id")

    # TEST 10: Multi-Tenant Data Isolation Enforcement
    # School Admin attempts to query with tenant_id parameter for another school
    res10 = client.get(
        f"/api/admin/overview?tenant_id={new_tenant_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    # The backend MUST enforce School Admin's own tenant (tenant 1), ignoring client spoofing
    overview_data = res10.json()
    assert_test(
        "10. School Admin Strict Isolation",
        res10.status_code == 200 and str(overview_data.get("current_tenant", {}).get("id")) == "1"
    )

    # TEST 11: School Admin Cannot Elevate to Super Admin
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE role = 'student' LIMIT 1")
    s_row = c.fetchone()
    student_id = s_row[0] if s_row else None
    conn.close()

    if student_id:
        res11 = client.post(
            f"/api/admin/users/{student_id}/change-role",
            json={"new_role": "super_admin"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert_test("11. School Admin Promotion to Super Admin Blocked (403)", res11.status_code == 403)

    # TEST 12: Super Admin Global Audit Logs Retrieval
    res12 = client.get("/api/admin/audit-logs", headers={"Authorization": f"Bearer {super_token}"})
    assert_test(
        "12. Audit Logs Retrievable by Super Admin",
        res12.status_code == 200 and len(res12.json().get("logs", [])) > 0
    )

    # TEST 13: Salted PBKDF2 Password Hashes in SQLite
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT email, password_hash FROM users WHERE role IN ('super_admin', 'admin', 'teacher')")
    users = c.fetchall()
    conn.close()
    
    all_hashed = all(u[1] and u[1].startswith("pbkdf2:sha256:100000$") for u in users)
    assert_test("13. Zero Plaintext Passwords / 100% Salted PBKDF2", all_hashed and len(users) >= 3)

    print("=" * 60)
    print(f"RESULTS: {passed}/{total} TESTS PASSED ({round(passed/total*100)}%)")
    print("=" * 60)

    if passed == total:
        print(">>> ALL P0 SECURITY REQUIREMENTS FULLY VERIFIED! <<<")
        return 0
    else:
        print(">>> SOME TESTS FAILED! <<<")
        return 1

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
