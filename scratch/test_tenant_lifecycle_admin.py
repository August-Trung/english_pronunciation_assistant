import sqlite3
import requests
import json
import os
import sys

# Add backend directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend', 'app'))
from main import app, init_db, DB_PATH, hash_password
from security import create_access_token
from fastapi.testclient import TestClient

client = TestClient(app)

def test_tenant_lifecycle_and_admin_updates():
    print("=== Testing Tenant Lifecycle, Quota & Admin Management ===")
    
    # 1. Prepare Super Admin Token
    login_res = client.post("/api/admin/login", json={"email": "superadmin@fluent.edu.vn", "password": "superadmin123"})
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    super_admin_token = login_res.json()["token"]
    headers = {"Authorization": f"Bearer {super_admin_token}"}
    
    # Setup a fresh test tenant in SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    test_tenant_id = "tenant_test_lifecycle_999"
    cursor.execute("DELETE FROM tenants WHERE id = ?", (test_tenant_id,))
    cursor.execute("DELETE FROM users WHERE tenant_id = ?", (test_tenant_id,))
    cursor.execute("DELETE FROM users WHERE email IN ('test_no_admin@school.com', 'test_admin_updated@school.com')")
    
    # Insert test tenant with NO admin_id
    cursor.execute("""
        INSERT INTO tenants (id, name, admin_id, status, license_seats, license_expiry, IsXoa)
        VALUES (?, 'Original Test Academy', NULL, 'active', 50, '2026-12-31', 0)
    """, (test_tenant_id,))
    conn.commit()
    conn.close()
    
    # Test 1: Verify invalid email is rejected
    res = client.post(
        f"/api/admin/tenants/{test_tenant_id}/lifecycle",
        headers=headers,
        json={
            "status": "active",
            "admin_email": "invalid-email-format"
        }
    )
    assert res.status_code == 400, f"Expected 400, got {res.status_code}: {res.text}"
    print("[PASS] Invalid email rejected.")

    # Test 2: Provision admin for tenant that previously had NO admin
    res = client.post(
        f"/api/admin/tenants/{test_tenant_id}/lifecycle",
        headers=headers,
        json={
            "status": "active",
            "school_name": "Olympia Academy Renamed",
            "license_seats": 200,
            "license_expiry": "2029-01-01",
            "admin_email": "test_no_admin@school.com",
            "admin_name": "Headmaster Olympia",
            "admin_password": "NewSecretPass@123"
        }
    )
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    data = res.json()
    assert data["school_name"] == "Olympia Academy Renamed"
    assert data["license_seats"] == 200
    assert data["admin_email"] == "test_no_admin@school.com"
    print("[PASS] Provisioned admin for tenant with no prior admin.")

    # Verify in DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, admin_id, license_seats FROM tenants WHERE id = ?", (test_tenant_id,))
    t_row = cursor.fetchone()
    assert t_row[0] == "Olympia Academy Renamed"
    assert t_row[1] is not None
    assert t_row[2] == 200
    new_admin_id = t_row[1]
    
    cursor.execute("SELECT email, name, role, tenant_id FROM users WHERE id = ?", (new_admin_id,))
    u_row = cursor.fetchone()
    assert u_row[0] == "test_no_admin@school.com"
    assert u_row[1] == "Headmaster Olympia"
    assert u_row[2] == "admin"
    assert u_row[3] == test_tenant_id
    conn.close()
    print("[PASS] Verified DB state for newly provisioned admin.")

    # Test 3: Update existing admin email & name & password
    res = client.post(
        f"/api/admin/tenants/{test_tenant_id}/lifecycle",
        headers=headers,
        json={
            "status": "trial",
            "school_name": "Olympia Academy Final",
            "license_seats": 250,
            "admin_email": "test_admin_updated@school.com",
            "admin_name": "Headmaster Updated",
            "admin_password": "AnotherPass@456"
        }
    )
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    print("[PASS] Updated existing admin email and credentials.")

    # Verify updated in DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT email, name FROM users WHERE id = ?", (new_admin_id,))
    u_row2 = cursor.fetchone()
    assert u_row2[0] == "test_admin_updated@school.com"
    assert u_row2[1] == "Headmaster Updated"
    conn.close()
    print("[PASS] Verified DB state for updated existing admin.")

    # Clean up
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tenants WHERE id = ?", (test_tenant_id,))
    cursor.execute("DELETE FROM users WHERE tenant_id = ?", (test_tenant_id,))
    cursor.execute("DELETE FROM users WHERE email IN ('test_no_admin@school.com', 'test_admin_updated@school.com')")
    conn.commit()
    conn.close()
    print("=== All Lifecycle & Admin update tests passed successfully! ===")

if __name__ == "__main__":
    test_tenant_lifecycle_and_admin_updates()
