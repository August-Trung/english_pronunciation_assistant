import os
import sys
import json
import sqlite3

# Ensure app directory is in path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "app"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from main import app, init_db, DB_PATH
from security import hash_password, verify_password, create_access_token

client = TestClient(app)

def run_tests():
    print("=" * 65)
    print("RUNNING P3 SUPER ADMIN GOVERNANCE & OPERATIONS VERIFICATION SUITE")
    print("=" * 65)

    init_db()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Clean test fixtures
    cursor.execute("DELETE FROM users WHERE email LIKE '%olympia%' OR email LIKE '%test_p3%'")
    cursor.execute("DELETE FROM tenants WHERE id LIKE '%olympia%' OR name LIKE '%Olympia%'")
    
    # Ensure Super Admin exists
    cursor.execute("SELECT id FROM users WHERE role = 'super_admin'")
    sa_row = cursor.fetchone()
    if not sa_row:
        sa_hash = hash_password("superadmin123")
        cursor.execute("""
            INSERT INTO users (email, name, role, password_hash, status)
            VALUES ('superadmin@fluent.edu.vn', 'Super Admin (Owner)', 'super_admin', ?, 'active')
        """, (sa_hash,))
        sa_id = cursor.lastrowid
    else:
        sa_id = sa_row[0]
        # Ensure password is known
        sa_hash = hash_password("superadmin123")
        cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (sa_hash, sa_id))
    
    conn.commit()
    conn.close()

    total_passed = 0
    total_failed = 0

    def assert_test(cond, title):
        nonlocal total_passed, total_failed
        if cond:
            print(f"  [PASS] {title}")
            total_passed += 1
        else:
            print(f"  [FAIL] {title}")
            total_failed += 1

    # Test 1: Super Admin Login
    print("\n--- TEST GROUP 1: SUPER ADMIN AUTHENTICATION ---")
    login_res = client.post("/api/admin/login", json={
        "email": "superadmin@fluent.edu.vn",
        "password": "superadmin123"
    })
    assert_test(login_res.status_code == 200, f"Super Admin login succeeds with HTTP 200 (got {login_res.status_code})")
    sa_token = login_res.json().get("token")
    sa_headers = {"Authorization": f"Bearer {sa_token}"}
    assert_test(bool(sa_token), "Super Admin JWT token received")
    assert_test(login_res.json().get("user", {}).get("role") == "super_admin", "Super Admin role confirmed")

    # Test 2: Atomic School Onboarding
    print("\n--- TEST GROUP 2: ATOMIC SCHOOL ONBOARDING ---")
    onboard_payload = {
        "school_name": "Olympia International Academy",
        "admin_email": "admin.olympia@fluent.edu.vn",
        "admin_name": "Principal Dr. Vance Olympia",
        "admin_password": "OlympiaAdmin@2026",
        "license_seats": 250,
        "license_expiry": "2028-09-30",
        "status": "active"
    }
    onboard_res = client.post("/api/admin/tenants/onboard", headers=sa_headers, json=onboard_payload)
    assert_test(onboard_res.status_code == 200, f"Onboarding school succeeds with HTTP 200 (got {onboard_res.status_code})")
    onboard_data = onboard_res.json()
    new_tenant_id = onboard_data.get("tenant_id")
    new_admin_id = onboard_data.get("admin_id")
    assert_test(bool(new_tenant_id), f"Generated tenant ID: {new_tenant_id}")
    assert_test(bool(new_admin_id), f"Generated admin user ID: {new_admin_id}")
    assert_test(onboard_data.get("tenant_status") == "active", "Initial tenant status is 'active'")

    # Duplicate admin email rejection
    dup_res = client.post("/api/admin/tenants/onboard", headers=sa_headers, json=onboard_payload)
    assert_test(dup_res.status_code == 400, "Rejects duplicate admin email with HTTP 400")

    # Test 3: Newly Onboarded School Admin Login
    print("\n--- TEST GROUP 3: ONBOARDED SCHOOL ADMIN CREDENTIALS & ACCESS ---")
    adm_login = client.post("/api/admin/login", json={
        "email": "admin.olympia@fluent.edu.vn",
        "password": "OlympiaAdmin@2026"
    })
    assert_test(adm_login.status_code == 200, f"Onboarded School Admin can sign in with new credentials (got {adm_login.status_code})")
    adm_token = adm_login.json().get("token")
    adm_headers = {"Authorization": f"Bearer {adm_token}"}
    adm_user = adm_login.json().get("user", {})
    assert_test(adm_user.get("role") == "admin", "User role is 'admin'")
    assert_test(str(adm_user.get("tenant_id")) == str(new_tenant_id), "User tenant_id matches onboarded school")

    # School Admin can access their own overview
    adm_overview = client.get("/api/admin/overview", headers=adm_headers)
    assert_test(adm_overview.status_code == 200, "School Admin can access their overview")
    assert_test(adm_overview.json().get("license_seats") == 250, "Overview reports correct 250 seat quota")

    # Test 4: Deep Multi-Tenant Metrics Aggregation
    print("\n--- TEST GROUP 4: DEEP MULTI-TENANT METRICS AGGREGATION ---")
    metrics_res = client.get("/api/admin/tenants", headers=sa_headers)
    assert_test(metrics_res.status_code == 200, "Super Admin can fetch deep tenant metrics")
    tenants_list = metrics_res.json().get("tenants", [])
    assert_test(len(tenants_list) >= 2, f"Total schools reported: {len(tenants_list)}")
    
    olympia_metric = next((t for t in tenants_list if t["id"] == new_tenant_id), None)
    assert_test(olympia_metric is not None, "Olympia school found in deep metrics directory")
    if olympia_metric:
        assert_test(olympia_metric["admin_email"] == "admin.olympia@fluent.edu.vn", "School Admin email correctly linked")
        assert_test(olympia_metric["license_seats"] == 250, "Metrics report accurate 250 seat licenses")
        assert_test(olympia_metric["status"] == "active", "Metrics report status as 'active'")
        assert_test("audio_storage_mb" in olympia_metric, "Audio storage metric present")
        assert_test("class_count" in olympia_metric, "Classrooms count metric present")

    # School Admin cannot access Super Admin deep metrics
    adm_metrics_res = client.get("/api/admin/tenants", headers=adm_headers)
    assert_test(adm_metrics_res.status_code == 403, "School Admin blocked from GET /api/admin/tenants with HTTP 403")

    # Test 5: Tenant Lifecycle Management - Suspension & Platform-Wide Lockout
    print("\n--- TEST GROUP 5: TENANT SUSPENSION & IMMEDIATE LOCKOUT ---")
    suspend_res = client.post(f"/api/admin/tenants/{new_tenant_id}/lifecycle", headers=sa_headers, json={
        "status": "suspended"
    })
    assert_test(suspend_res.status_code == 200, "Super Admin updates tenant lifecycle status to 'suspended'")
    assert_test(suspend_res.json().get("tenant_status") == "suspended", "Response confirms status 'suspended'")

    # Immediate Lockout Check: School Admin makes request
    locked_overview = client.get("/api/admin/overview", headers=adm_headers)
    assert_test(locked_overview.status_code == 403, "Suspended school admin immediately receives HTTP 403 Forbidden")
    assert_test("suspended" in locked_overview.json().get("detail", "").lower(), "Error detail explicitly cites suspension")

    # Suspended school users cannot fetch classrooms
    locked_classes = client.get("/api/admin/classes", headers=adm_headers)
    assert_test(locked_classes.status_code == 403, "Classrooms access also blocked with HTTP 403 Forbidden")

    # Test 6: Support / Inspection Mode ("View As")
    print("\n--- TEST GROUP 6: SUPPORT & INSPECTION MODE ('VIEW AS') ---")
    impersonate_res = client.post(f"/api/admin/impersonate-tenant/{new_tenant_id}", headers=sa_headers)
    assert_test(impersonate_res.status_code == 200, "Super Admin can generate Support / Inspection token")
    support_data = impersonate_res.json()
    support_token = support_data.get("token")
    assert_test(bool(support_token), "Support inspection token received")
    assert_test(support_data.get("user", {}).get("is_support_mode") is True, "Inspection mode flag present")
    
    # Super Admin can inspect suspended school using Support Mode token!
    support_headers = {"Authorization": f"Bearer {support_token}"}
    support_overview = client.get("/api/admin/overview", headers=support_headers)
    assert_test(support_overview.status_code == 200, "Super Admin in Support Mode can inspect suspended school data (HTTP 200)")

    # Test 7: Tenant Lifecycle Management - Reactivation
    print("\n--- TEST GROUP 7: TENANT REACTIVATION ---")
    reactivate_res = client.post(f"/api/admin/tenants/{new_tenant_id}/lifecycle", headers=sa_headers, json={
        "status": "active",
        "license_seats": 300
    })
    assert_test(reactivate_res.status_code == 200, "Super Admin reactivates school with 300 seats")
    assert_test(reactivate_res.json().get("tenant_status") == "active", "Status updated to 'active'")

    # School Admin can immediately use platform again
    restored_overview = client.get("/api/admin/overview", headers=adm_headers)
    assert_test(restored_overview.status_code == 200, "School Admin immediately regains access after reactivation (HTTP 200)")
    assert_test(restored_overview.json().get("license_seats") == 300, "New seat quota (300) reflected")

    # Test 8: Filterable & Searchable Audit Logs
    print("\n--- TEST GROUP 8: AUDIT LOGS SEARCH & FILTERING ---")
    # All audit logs
    all_logs_res = client.get("/api/admin/audit-logs", headers=sa_headers)
    assert_test(all_logs_res.status_code == 200, "Audit logs retrieved successfully")
    
    # Filter by action ONBOARD_TENANT
    action_logs_res = client.get("/api/admin/audit-logs?action=ONBOARD_TENANT", headers=sa_headers)
    assert_test(action_logs_res.status_code == 200, "Filter by action=ONBOARD_TENANT succeeds")
    action_logs = action_logs_res.json().get("logs", [])
    assert_test(all(l["action"] == "ONBOARD_TENANT" for l in action_logs), "All returned logs match ONBOARD_TENANT")

    # Filter by search string "Olympia"
    search_logs_res = client.get("/api/admin/audit-logs?search=Olympia", headers=sa_headers)
    assert_test(search_logs_res.status_code == 200, "Search audit logs succeeds")
    search_logs = search_logs_res.json().get("logs", [])
    assert_test(len(search_logs) > 0, "Found audit entries mentioning Olympia")

    # Multi-tenant isolation for audit logs
    school_logs_res = client.get("/api/admin/audit-logs", headers=adm_headers)
    assert_test(school_logs_res.status_code == 200, "School Admin can view audit logs")
    school_logs = school_logs_res.json().get("logs", [])
    assert_test(all(str(l["tenant_id"]) == str(new_tenant_id) for l in school_logs), "School Admin logs are 100% isolated to their own school")

    # Test 9: Database Backup Snapshot Export
    print("\n--- TEST GROUP 9: DATABASE BACKUP SNAPSHOT EXPORT ---")
    backup_res = client.get("/api/admin/backup-snapshot", headers=sa_headers)
    assert_test(backup_res.status_code == 200, "Super Admin can export backup snapshot")
    backup_data = backup_res.json()
    assert_test(backup_data.get("status") == "success", "Backup status is 'success'")
    assert_test("tenants" in backup_data.get("data", {}), "Tenants table in snapshot")
    assert_test("users" in backup_data.get("data", {}), "Users table in snapshot")
    
    # Sensitive password hashes masked in backup
    user_records = backup_data.get("data", {}).get("users", [])
    assert_test(all(u.get("password_hash") == "[PROTECTED_PBKDF2_HASH]" for u in user_records), "All user password hashes are protected/masked in snapshot")

    # School Admin blocked from backup export
    adm_backup_res = client.get("/api/admin/backup-snapshot", headers=adm_headers)
    assert_test(adm_backup_res.status_code == 403, "School Admin blocked from backup snapshot with HTTP 403")

    # Test 10: Tenant Cleanup / Delete
    print("\n--- TEST GROUP 10: TENANT ARCHIVE / CLEANUP ---")
    del_res = client.delete(f"/api/admin/tenants/{new_tenant_id}", headers=sa_headers)
    assert_test(del_res.status_code == 200, "Super Admin can soft delete/archive school tenant")

    # Summary
    print("\n" + "=" * 65)
    print(f"P3 SUPER ADMIN SUITE RESULTS: {total_passed} PASSED, {total_failed} FAILED")
    print("=" * 65)
    if total_failed == 0:
        print(">>> ALL P3 TESTS PASSED PERFECTLY! <<<")
    else:
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
