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
    print("=" * 60)
    print("RUNNING P1 SCHOOL ADMIN VERIFICATION SUITE")
    print("=" * 60)

    # Initialize / migrate db
    init_db()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Clean any previous test artifacts
    cursor.execute("DELETE FROM class_enrollments WHERE student_id IN (301, 302, 303)")
    cursor.execute("DELETE FROM classrooms WHERE teacher_id IN (211, 212, 213)")

    # Setup test fixtures
    # Tenant 1: Fluent English Academy (license_seats = 10)
    cursor.execute("""
        INSERT OR REPLACE INTO tenants (id, name, license_seats, license_expiry, IsXoa)
        VALUES ('1', 'Fluent English Academy', 10, '2028-12-31', 0)
    """)
    # Tenant 2: Other School (license_seats = 5)
    cursor.execute("""
        INSERT OR REPLACE INTO tenants (id, name, license_seats, license_expiry, IsXoa)
        VALUES ('2', 'Rival Academy', 5, '2028-12-31', 0)
    """)

    # Admin of Tenant 1
    admin_pwd_hash = hash_password("admin123")
    cursor.execute("""
        INSERT OR REPLACE INTO users (id, email, name, role, tenant_id, password_hash, status, IsXoa)
        VALUES (201, 'schooladmin1@fluent.edu.vn', 'School Admin One', 'admin', '1', ?, 'active', 0)
    """, (admin_pwd_hash,))

    # Admin of Tenant 2
    cursor.execute("""
        INSERT OR REPLACE INTO users (id, email, name, role, tenant_id, password_hash, status, IsXoa)
        VALUES (202, 'schooladmin2@rival.edu.vn', 'School Admin Two', 'admin', '2', ?, 'active', 0)
    """, (admin_pwd_hash,))

    # Teachers for Tenant 1
    t_pwd_hash = hash_password("teacher123")
    cursor.execute("""
        INSERT OR REPLACE INTO users (id, email, name, role, tenant_id, password_hash, status, IsXoa)
        VALUES (211, 'teacher_alpha@fluent.edu.vn', 'Teacher Alpha', 'teacher', '1', ?, 'active', 0)
    """, (t_pwd_hash,))
    cursor.execute("""
        INSERT OR REPLACE INTO users (id, email, name, role, tenant_id, password_hash, status, IsXoa)
        VALUES (212, 'teacher_beta@fluent.edu.vn', 'Teacher Beta', 'teacher', '1', ?, 'active', 0)
    """, (t_pwd_hash,))

    # Teacher for Tenant 2
    cursor.execute("""
        INSERT OR REPLACE INTO users (id, email, name, role, tenant_id, password_hash, status, IsXoa)
        VALUES (213, 'teacher_rival@rival.edu.vn', 'Teacher Rival', 'teacher', '2', ?, 'active', 0)
    """, (t_pwd_hash,))

    # Students
    s_pwd_hash = hash_password("student123")
    cursor.execute("""
        INSERT OR REPLACE INTO users (id, email, name, role, tenant_id, password_hash, status, IsXoa)
        VALUES (301, 'student1@test.com', 'Student One', 'student', '1', ?, 'active', 0)
    """, (s_pwd_hash,))
    cursor.execute("""
        INSERT OR REPLACE INTO users (id, email, name, role, tenant_id, password_hash, status, IsXoa)
        VALUES (302, 'student2@test.com', 'Student Two', 'student', '1', ?, 'active', 0)
    """, (s_pwd_hash,))
    cursor.execute("""
        INSERT OR REPLACE INTO users (id, email, name, role, tenant_id, password_hash, status, IsXoa)
        VALUES (303, 'student3@test.com', 'Student Three', 'student', NULL, ?, 'active', 0)
    """, (s_pwd_hash,))

    conn.commit()
    conn.close()

    # 1. Login School Admin 1
    res = client.post("/api/admin/login", json={"email": "schooladmin1@fluent.edu.vn", "password": "admin123"})
    assert res.status_code == 200, f"Login failed: {res.text}"
    token_admin1 = res.json()["token"]
    headers_admin1 = {"Authorization": f"Bearer {token_admin1}"}
    print("[PASS] 1. School Admin 1 Logged in & Token Issued")

    # Login School Admin 2
    res2 = client.post("/api/admin/login", json={"email": "schooladmin2@rival.edu.vn", "password": "admin123"})
    token_admin2 = res2.json()["token"]
    headers_admin2 = {"Authorization": f"Bearer {token_admin2}"}

    # 2. List Teachers for Tenant 1
    res = client.get("/api/admin/teachers", headers=headers_admin1)
    assert res.status_code == 200
    teachers = res.json()["teachers"]
    teacher_emails = [t["email"] for t in teachers]
    assert "teacher_alpha@fluent.edu.vn" in teacher_emails
    assert "teacher_beta@fluent.edu.vn" in teacher_emails
    assert "teacher_rival@rival.edu.vn" not in teacher_emails, "Cross-tenant leak!"
    print("[PASS] 2. School Admin retrieves strictly isolated teachers")

    # 3. Create Classroom by School Admin 1
    res = client.post("/api/admin/classes/create", headers=headers_admin1, json={
        "name": "IELTS Band 7.5 Intensive",
        "grade_level": "Advanced",
        "teacher_id": 211
    })
    assert res.status_code == 200, f"Create class failed: {res.text}"
    class_id_1 = res.json()["class_id"]
    join_code_1 = res.json()["join_code"]
    print(f"[PASS] 3. School Admin created class ID {class_id_1} (Join Code: {join_code_1})")

    # 4. Cross-tenant teacher assignment blocked
    res = client.post("/api/admin/classes/create", headers=headers_admin1, json={
        "name": "Illegal Class",
        "grade_level": "Grade 10",
        "teacher_id": 213 # Teacher Rival from Tenant 2
    })
    assert res.status_code == 403, f"Expected 403 for cross-tenant teacher, got: {res.status_code}"
    print("[PASS] 4. Cross-tenant teacher assignment blocked upon creation (403)")

    # 5. Reassign Class to Teacher Beta
    res = client.post(f"/api/admin/classes/{class_id_1}/assign-teacher", headers=headers_admin1, json={
        "teacher_id": 212
    })
    assert res.status_code == 200, f"Assign teacher failed: {res.text}"
    # Verify in classes list
    res = client.get("/api/admin/classes", headers=headers_admin1)
    target_cls = next(c for c in res.json()["classes"] if c["id"] == class_id_1)
    assert target_cls["teacher_name"] == "Teacher Beta"
    print("[PASS] 5. School Admin reassigned class teacher successfully")

    # 6. Cross-tenant class modification blocked
    res = client.post(f"/api/admin/classes/{class_id_1}/assign-teacher", headers=headers_admin2, json={
        "teacher_id": 213
    })
    assert res.status_code == 403, f"Expected 403 for foreign admin, got: {res.status_code}"
    print("[PASS] 6. School Admin 2 blocked from modifying School Admin 1's class (403)")

    # 7. Archive & Unarchive Classroom
    res = client.post(f"/api/admin/classes/{class_id_1}/toggle-archive", headers=headers_admin1)
    assert res.status_code == 200
    assert res.json()["is_archived"] is True
    print("[PASS] 7a. Classroom successfully archived")

    # 8. Student cannot join archived class
    res = client.post("/api/classes/join", json={"student_id": 301, "join_code": join_code_1})
    assert res.status_code == 400, f"Expected 400 for archived class, got: {res.status_code}"
    assert "archived" in res.json()["detail"].lower()
    print("[PASS] 8. Student joining archived class rejected (400)")

    # Unarchive class
    res = client.post(f"/api/admin/classes/{class_id_1}/toggle-archive", headers=headers_admin1)
    assert res.status_code == 200
    assert res.json()["is_archived"] is False
    print("[PASS] 7b. Classroom restored to active state")

    # 9. Student joins active class
    res = client.post("/api/classes/join", json={"student_id": 301, "join_code": join_code_1})
    assert res.status_code == 200
    print("[PASS] 9. Student successfully joined unarchived class")

    # Create second class in Tenant 1
    res = client.post("/api/admin/classes/create", headers=headers_admin1, json={
        "name": "TOEIC Masterclass",
        "grade_level": "Intermediate",
        "teacher_id": 212
    })
    class_id_2 = res.json()["class_id"]
    join_code_2 = res.json()["join_code"]

    # 10. Student 302 joins class 1
    res = client.post("/api/classes/join", json={"student_id": 302, "join_code": join_code_1})
    assert res.status_code == 200

    # 11. Test License Seat Quota Limit
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # Count current unique active students in Tenant 1 (including any prior seeds + 301 + 302)
    cur.execute("SELECT COUNT(DISTINCT student_id) FROM class_enrollments WHERE tenant_id = '1' AND (IsXoa IS NULL OR IsXoa = 0)")
    active_count = cur.fetchone()[0]
    # Artificially set Tenant 1's seats to active_count (quota full)
    cur.execute("UPDATE tenants SET license_seats = ? WHERE id = '1'", (active_count,))
    conn.commit()
    conn.close()

    # Quota is full at active_count.
    # Student 301 (already in Tenant 1) should still be able to join Class 2 without consuming an extra seat!
    res = client.post("/api/classes/join", json={"student_id": 301, "join_code": join_code_2})
    assert res.status_code == 200, f"Existing student failed to join second class: {res.text}"
    print("[PASS] 10a. Existing student in school joins second class without extra seat consumption")

    # Student 303 (new student not in Tenant 1) attempts to join -> Should be blocked because quota is full!
    res = client.post("/api/classes/join", json={"student_id": 303, "join_code": join_code_1})
    assert res.status_code == 403, f"Expected 403 quota exceeded, got: {res.status_code}"
    assert "seat quota exceeded" in res.json()["detail"].lower()
    print("[PASS] 10b. License seat quota strictly enforced (new student blocked at quota limit)")

    # 12. Check Class Roster API
    res = client.get(f"/api/admin/classes/{class_id_1}/roster", headers=headers_admin1)
    assert res.status_code == 200
    roster = res.json()
    assert roster["total_students"] == 2
    student_ids = [s["id"] for s in roster["students"]]
    assert 301 in student_ids and 302 in student_ids
    print("[PASS] 11. Class Roster API returned accurate student membership & stats")

    # 13. Transfer Student 302 from Class 1 to Class 2
    res = client.post(f"/api/admin/classes/{class_id_1}/transfer-student", headers=headers_admin1, json={
        "student_id": 302,
        "to_class_id": class_id_2
    })
    assert res.status_code == 200, f"Transfer failed: {res.text}"

    # Verify Roster 1 now only has 1 student
    res = client.get(f"/api/admin/classes/{class_id_1}/roster", headers=headers_admin1)
    assert res.json()["total_students"] == 1
    # Verify Roster 2 now has students 301 and 302
    res = client.get(f"/api/admin/classes/{class_id_2}/roster", headers=headers_admin1)
    assert res.json()["total_students"] == 2
    print("[PASS] 12. Student transferred between classes within school successfully")

    # 14. Revoke Student Seat (Remove Student 302 from Class 2)
    res = client.post(f"/api/admin/classes/{class_id_2}/revoke-student/302", headers=headers_admin1)
    assert res.status_code == 200
    # Verify student 302 is no longer in Class 2
    res = client.get(f"/api/admin/classes/{class_id_2}/roster", headers=headers_admin1)
    assert res.json()["total_students"] == 1
    print("[PASS] 13. Student seat revoked and student un-enrolled from classroom")

    # With 302 revoked from all classes, now only 301 is active in Tenant 1.
    # Therefore, Student 303 should now be able to join since 1 seat was released!
    res = client.post("/api/classes/join", json={"student_id": 303, "join_code": join_code_1})
    assert res.status_code == 200, f"Expected 303 to succeed after seat released, got: {res.status_code}: {res.text}"
    print("[PASS] 14. Released seat immediately available for new student enrollment")

    # 15. Teacher Suspension & Login Block
    # Create token for Teacher Alpha
    teacher_token = create_access_token(211, "teacher_alpha@fluent.edu.vn", "teacher", "1")
    headers_teacher = {"Authorization": f"Bearer {teacher_token}"}
    
    # Verify teacher can access classes
    res = client.get("/api/classes/teacher/211", headers=headers_teacher)
    assert res.status_code == 200

    # School Admin suspends Teacher Alpha
    res = client.post("/api/admin/teachers/211/toggle-status", headers=headers_admin1)
    assert res.status_code == 200
    assert res.json()["new_status"] == "suspended"

    # Suspended teacher now rejected with 403
    res = client.get("/api/classes/teacher/211", headers=headers_teacher)
    assert res.status_code == 403, f"Expected 403 for suspended teacher, got: {res.status_code}"
    print("[PASS] 15a. Teacher account suspended and access immediately blocked (403)")

    # School Admin reactivates Teacher Alpha
    res = client.post("/api/admin/teachers/211/toggle-status", headers=headers_admin1)
    assert res.status_code == 200
    assert res.json()["new_status"] == "active"
    # Access restored
    res = client.get("/api/classes/teacher/211", headers=headers_teacher)
    assert res.status_code == 200
    print("[PASS] 15b. Teacher account reactivated and access restored")

    # 16. Reset Teacher Password
    res = client.post("/api/admin/teachers/211/reset-password", headers=headers_admin1, json={
        "new_password": "NewSecretPassword2026!"
    })
    assert res.status_code == 200
    # Verify new password hash in DB
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT password_hash FROM users WHERE id = 211")
    new_hash = cur.fetchone()[0]
    conn.close()
    assert verify_password("NewSecretPassword2026!", new_hash)
    print("[PASS] 16. Teacher password reset with verified PBKDF2 hash")

    # 17. Seat Summary API
    res = client.get("/api/admin/seats-summary", headers=headers_admin1)
    assert res.status_code == 200
    summary = res.json()
    print("DEBUG summary:", summary, "active_count:", active_count)
    assert summary["license_seats"] == active_count
    assert summary["used_seats"] == active_count
    assert summary["available_seats"] == 0
    assert summary["active_classes"] >= 2
    print("[PASS] 17. Seat Summary API verified with accurate metrics")

    # 18. Audit Log recorded all administrative events
    res = client.get("/api/admin/audit-logs", headers=headers_admin1)
    assert res.status_code == 200
    logs = res.json()["logs"]
    actions = [l["action"] for l in logs]
    assert "CREATE_CLASSROOM" in actions
    assert "ASSIGN_TEACHER" in actions
    assert "ARCHIVE_CLASSROOM" in actions
    assert "TRANSFER_STUDENT" in actions
    assert "REVOKE_STUDENT_SEAT" in actions
    assert "SUSPEND_TEACHER" in actions
    assert "RESET_TEACHER_PASSWORD" in actions
    print(f"[PASS] 18. Audit log captured {len(logs)} administrative events in Tenant 1")

    print("=" * 60)
    print("RESULTS: ALL 18 P1 SCHOOL ADMIN TESTS PASSED (100%)")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
