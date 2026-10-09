import os
import sys
import requests
import json
import sqlite3

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend', 'app'))
from main import app, init_db, DB_PATH, hash_password
from fastapi.testclient import TestClient

def run_tests():
    init_db()
    client = TestClient(app)

    print("\n--- 1. Testing Super Admin Auth ---")
    res = client.post("/api/admin/login", json={"email": "superadmin@fluent.edu.vn", "password": "superadmin123"})
    assert res.status_code == 200, f"Login failed: {res.text}"
    sa_token = res.json()["token"]
    sa_headers = {"Authorization": f"Bearer {sa_token}"}
    print("   -> Super Admin Authenticated")

    print("\n--- 2. Setting up a dedicated test teacher ---")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Create or update a test teacher
    cursor.execute("SELECT id FROM users WHERE email = 'test_freelance_teacher@fluent.edu.vn'")
    row = cursor.fetchone()
    pwd = hash_password("freelance123")
    if row:
        t_id = row[0]
        cursor.execute("UPDATE users SET password_hash = ?, role = 'teacher', teacher_type = 'institutional' WHERE id = ?", (pwd, t_id))
    else:
        cursor.execute("INSERT INTO users (email, name, role, password_hash) VALUES (?, ?, ?, ?)",
                       ('test_freelance_teacher@fluent.edu.vn', 'Solo Tutor Dave', 'teacher', pwd))
        t_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # Teacher login
    res = client.post("/api/teacher/login", json={"email": "test_freelance_teacher@fluent.edu.vn", "password": "freelance123"})
    assert res.status_code == 200, f"Teacher login failed: {res.text}"
    t_token = res.json()["token"]
    t_headers = {"Authorization": f"Bearer {t_token}"}
    print(f"   -> Teacher Dave logged in (ID: {t_id})")

    print("\n--- 3. Testing Super Admin Update Teacher Plan (Freelance) ---")
    res = client.post(f"/api/admin/teachers/{t_id}/plan", json={
        "teacher_type": "freelance",
        "max_classes": 2,
        "max_seats": 2,
        "license_expiry": "2028-12-31"
    }, headers=sa_headers)
    assert res.status_code == 200, f"Update plan failed: {res.text}"
    plan_data = res.json()
    assert plan_data["quota"]["teacher_type"] == "freelance"
    assert plan_data["quota"]["max_classes"] == 2
    assert plan_data["quota"]["max_seats"] == 2
    print("   -> Successfully updated to Freelance: Max 2 classes, Max 2 seats")

    print("\n--- 4. Query Teacher Quota API ---")
    res = client.get(f"/api/teacher/{t_id}/quota", headers=t_headers)
    assert res.status_code == 200, f"Get quota failed: {res.text}"
    q = res.json()
    assert q["teacher_type"] == "freelance"
    assert q["used_classes"] == 0
    assert q["used_seats"] == 0
    print(f"   -> Quota verified: {q['used_classes']}/{q['max_classes']} classes, {q['used_seats']}/{q['max_seats']} seats")

    print("\n--- 5. Clean prior classes for clean testing ---")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM class_enrollments WHERE class_id IN (SELECT id FROM classrooms WHERE teacher_id = ?)", (t_id,))
    cursor.execute("DELETE FROM classrooms WHERE teacher_id = ?", (t_id,))
    conn.commit()
    conn.close()

    print("\n--- 6. Creating Class 1 (Should Pass) ---")
    res = client.post("/api/classes/create", json={"name": "IELTS Speaking Dave 1", "grade_level": "Adult"}, headers=t_headers)
    assert res.status_code == 200, f"Create class 1 failed: {res.text}"
    c1 = res.json()
    c1_code = c1["join_code"]
    c1_id = c1["class_id"]
    print(f"   -> Class 1 Created: ID {c1_id}, Code {c1_code}")

    print("\n--- 7. Creating Class 2 (Should Pass) ---")
    res = client.post("/api/classes/create", json={"name": "IELTS Speaking Dave 2", "grade_level": "Adult"}, headers=t_headers)
    assert res.status_code == 200, f"Create class 2 failed: {res.text}"
    c2 = res.json()
    c2_code = c2["join_code"]
    c2_id = c2["class_id"]
    print(f"   -> Class 2 Created: ID {c2_id}, Code {c2_code}")

    print("\n--- 8. Creating Class 3 (Should be BLOCKED by max_classes = 2) ---")
    res = client.post("/api/classes/create", json={"name": "IELTS Speaking Dave 3", "grade_level": "Adult"}, headers=t_headers)
    assert res.status_code == 403, f"Expected 403, got {res.status_code}: {res.text}"
    print(f"   -> Class 3 correctly blocked with 403: {res.json()['detail']}")

    print("\n--- 9. Creating test students ---")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    students = []
    for i in range(1, 4):
        cursor.execute("SELECT id FROM users WHERE email = ?", (f"fl_student_{i}@test.com",))
        r = cursor.fetchone()
        if r:
            s_id = r[0]
        else:
            cursor.execute("INSERT INTO users (email, name, role) VALUES (?, ?, 'student')", (f"fl_student_{i}@test.com", f"Student {i}"))
            s_id = cursor.lastrowid
        students.append(s_id)
    conn.commit()
    conn.close()

    print("\n--- 10. Student 1 joins Class 1 (Should Pass, Seats: 1/2) ---")
    res = client.post("/api/classes/join", json={"student_id": students[0], "join_code": c1_code})
    assert res.status_code == 200, f"Student 1 join failed: {res.text}"
    print("   -> Student 1 joined Class 1")

    print("\n--- 11. Student 1 joins Class 2 (Distinct De-duplication: should NOT consume extra seat) ---")
    res = client.post("/api/classes/join", json={"student_id": students[0], "join_code": c2_code})
    assert res.status_code == 200, f"Student 1 join class 2 failed: {res.text}"
    res_q = client.get(f"/api/teacher/{t_id}/quota", headers=t_headers).json()
    assert res_q["used_seats"] == 1, f"Expected 1 seat, got {res_q['used_seats']}"
    print(f"   -> Student 1 in 2 classes consumes exactly {res_q['used_seats']} / 2 seats")

    print("\n--- 12. Student 2 joins Class 1 (Should Pass, Seats: 2/2) ---")
    res = client.post("/api/classes/join", json={"student_id": students[1], "join_code": c1_code})
    assert res.status_code == 200, f"Student 2 join failed: {res.text}"
    res_q = client.get(f"/api/teacher/{t_id}/quota", headers=t_headers).json()
    assert res_q["used_seats"] == 2
    print(f"   -> Student 2 joined, used seats: {res_q['used_seats']} / 2 (FULL)")

    print("\n--- 13. Student 3 tries to join Class 1 (Should be BLOCKED: Quota Full 2/2) ---")
    res = client.post("/api/classes/join", json={"student_id": students[2], "join_code": c1_code})
    assert res.status_code == 403, f"Expected 403, got {res.status_code}: {res.text}"
    print(f"   -> Student 3 correctly blocked with 403: {res.json()['detail']}")

    print("\n--- 14. Teacher removes Student 2 (Seat Recycling) ---")
    res = client.post(f"/api/classes/{c1_id}/remove-student", json={"student_id": students[1]}, headers=t_headers)
    assert res.status_code == 200, f"Remove student failed: {res.text}"
    res_q = client.get(f"/api/teacher/{t_id}/quota", headers=t_headers).json()
    assert res_q["used_seats"] == 1, f"Expected 1 seat after removal, got {res_q['used_seats']}"
    print(f"   -> Student 2 removed. Seat recycled! Now used: {res_q['used_seats']} / 2 seats")

    print("\n--- 15. Student 3 can now join into recycled seat (Should Pass) ---")
    res = client.post("/api/classes/join", json={"student_id": students[2], "join_code": c1_code})
    assert res.status_code == 200, f"Student 3 join failed: {res.text}"
    res_q = client.get(f"/api/teacher/{t_id}/quota", headers=t_headers).json()
    assert res_q["used_seats"] == 2
    print(f"   -> Student 3 successfully filled the freed seat. Used: {res_q['used_seats']} / 2 seats")

    print("\n--- 16. Expiration Enforcement ---")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET license_expiry = '2020-01-01' WHERE id = ?", (t_id,))
    conn.commit()
    conn.close()

    res = client.post("/api/classes/create", json={"name": "Expired Attempt", "grade_level": "Adult"}, headers=t_headers)
    assert res.status_code == 403, f"Expected 403 expired, got {res.status_code}"
    print(f"   -> Expired teacher class creation blocked with 403: {res.json()['detail']}")

    print("\n--- 17. Cleanup Test Data ---")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM class_enrollments WHERE class_id IN (SELECT id FROM classrooms WHERE teacher_id = ?)", (t_id,))
    cursor.execute("DELETE FROM classrooms WHERE teacher_id = ?", (t_id,))
    cursor.execute("DELETE FROM users WHERE email LIKE 'fl_student_%@test.com'")
    cursor.execute("DELETE FROM users WHERE email = 'test_freelance_teacher@fluent.edu.vn'")
    conn.commit()
    conn.close()

    print("\n[SUCCESS] ALL 17 FREELANCE TEACHER QUOTA TESTS PASSED WITH 100% ACCURACY!")

if __name__ == "__main__":
    run_tests()
