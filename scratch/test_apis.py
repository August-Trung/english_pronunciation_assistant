import sys
import os
import random
import sqlite3

# Ensure backend/app is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "app")))

from fastapi.testclient import TestClient
from main import app, DB_PATH

client = TestClient(app)

def run_tests():
    print("==================================================")
    print(" STARTING API SELF-TEST FOR TEACHER & ADMIN APIs ")
    print("==================================================")

    # 0. Setup test data in SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    rnd = random.randint(100000, 999999)
    join_code = f"CLS-TST-{rnd}"
    tenant_id = f"tenant_test_{rnd}"
    test_email = f"teacher_{rnd}@fluent.edu.vn"
    updated_email = f"updated_teacher_{rnd}@fluent.edu.vn"

    # Insert test classroom
    cursor.execute(
        "INSERT INTO classrooms (teacher_id, name, grade_level, join_code) VALUES (1, 'Test Class 101', 'Elementary (Grades 1 - 5)', ?)",
        (join_code,)
    )
    class_id = cursor.lastrowid

    # Insert test enrollment
    cursor.execute(
        "INSERT OR IGNORE INTO users (id, email, name, role) VALUES (999, 'student999@test.com', 'Test Student 999', 'student')"
    )
    cursor.execute(
        "INSERT INTO class_enrollments (class_id, student_id) VALUES (?, 999)", (class_id,)
    )

    # Insert test assignment
    cursor.execute(
        "INSERT INTO assignments (class_id, teacher_id, title, topic_sentence, due_date) VALUES (?, 1, 'Original Assignment Title', 'Original Reading Sentence', '2026-08-01')",
        (class_id,)
    )
    asg_id = cursor.lastrowid

    # Insert test tenant
    cursor.execute(
        "INSERT OR REPLACE INTO tenants (id, name, admin_id, license_seats, license_expiry) VALUES (?, 'Original School Name', 1, 100, '2026-12-31')",
        (tenant_id,)
    )

    # Insert test provisioned user
    cursor.execute(
        "INSERT INTO users (email, name, role, parent_code, password_hash) VALUES (?, 'Prof. Original Name', 'teacher', 'PA-9999', 'password123')",
        (test_email,)
    )
    user_id = cursor.lastrowid

    conn.commit()
    conn.close()

    results = []

    # 1. Test POST /api/classes/{class_id}/update
    res = client.post(f"/api/classes/{class_id}/update", json={
        "name": "Updated Class 101 Name",
        "grade_level": "Middle School (Grades 6 - 9)"
    })
    passed = res.status_code == 200 and res.json().get("name") == "Updated Class 101 Name"
    results.append(("POST /api/classes/{class_id}/update", passed, res.json()))

    # 2. Test POST /api/classes/{class_id}/remove-student
    res = client.post(f"/api/classes/{class_id}/remove-student", json={"student_id": 999})
    passed = res.status_code == 200 and res.json().get("status") == "success"
    results.append(("POST /api/classes/{class_id}/remove-student", passed, res.json()))

    # 3. Test POST /api/assignments/{assignment_id}/update
    res = client.post(f"/api/assignments/{asg_id}/update", json={
        "title": "Updated Assignment Title",
        "topic_sentence": "Updated Reading Sentence",
        "due_date": "2026-09-01"
    })
    passed = res.status_code == 200 and res.json().get("status") == "success"
    results.append(("POST /api/assignments/{assignment_id}/update", passed, res.json()))

    # 4. Test DELETE /api/assignments/{assignment_id}
    res = client.delete(f"/api/assignments/{asg_id}")
    passed = res.status_code == 200 and res.json().get("status") == "success"
    results.append(("DELETE /api/assignments/{assignment_id}", passed, res.json()))

    # 5. Test DELETE /api/classes/{class_id}
    res = client.delete(f"/api/classes/{class_id}")
    passed = res.status_code == 200 and res.json().get("status") == "success"
    results.append(("DELETE /api/classes/{class_id}", passed, res.json()))

    # 6. Test POST /api/admin/tenants/{tenant_id}/update
    res = client.post(f"/api/admin/tenants/{tenant_id}/update", json={
        "name": "Updated School Organization Name",
        "license_seats": 500,
        "license_expiry": "2028-01-01"
    })
    passed = res.status_code == 200 and res.json().get("name") == "Updated School Organization Name"
    results.append(("POST /api/admin/tenants/{tenant_id}/update", passed, res.json()))

    # 7. Test DELETE /api/admin/tenants/{tenant_id}
    res = client.delete(f"/api/admin/tenants/{tenant_id}")
    passed = res.status_code == 200 and res.json().get("status") == "success"
    results.append(("DELETE /api/admin/tenants/{tenant_id}", passed, res.json()))

    # 8. Test GET /api/admin/users
    res = client.get("/api/admin/users")
    passed = res.status_code == 200 and isinstance(res.json().get("users"), list)
    results.append(("GET /api/admin/users", passed, f"Users count: {len(res.json().get('users', []))}"))

    # 9. Test POST /api/admin/users/{user_id}/update
    res = client.post(f"/api/admin/users/{user_id}/update", json={
        "name": "Prof. Updated Name",
        "email": updated_email,
        "role": "admin",
        "password": "newpassword456"
    })
    passed = res.status_code == 200 and res.json().get("status") == "success"
    results.append(("POST /api/admin/users/{user_id}/update", passed, res.json()))

    # 10. Test DELETE /api/admin/users/{user_id}
    res = client.delete(f"/api/admin/users/{user_id}")
    passed = res.status_code == 200 and res.json().get("status") == "success"
    results.append(("DELETE /api/admin/users/{user_id}", passed, res.json()))

    # 11. Test GET /api/admin/settings & POST /api/admin/settings/update
    res = client.post("/api/admin/settings/update", json={"retention_days": 90})
    passed_update = res.status_code == 200 and res.json().get("retention_days") == 90

    res_get = client.get("/api/admin/settings")
    passed_get = res_get.status_code == 200 and res_get.json().get("retention_days") == 90
    results.append(("GET/POST /api/admin/settings", passed_update and passed_get, res_get.json()))

    # 12. Test GET /api/practice/recommended/{user_id}
    res_rec = client.get(f"/api/practice/recommended/{user_id}")
    passed_rec = res_rec.status_code == 200 and isinstance(res_rec.json().get("recommendations"), list)
    results.append(("GET /api/practice/recommended/{user_id}", passed_rec, f"Recommendations count: {len(res_rec.json().get('recommendations', []))}"))

    # 13. Test POST /api/agent/chat (Groq Multi-Role AI Agent Copilot)
    res_agent = client.post("/api/agent/chat", json={
        "user_id": user_id,
        "role": "teacher",
        "message": "Tạo bài tập 3 câu chủ đề Environment cho lớp"
    })
    passed_agent = res_agent.status_code == 200 and res_agent.json().get("status") == "success"
    results.append(("POST /api/agent/chat (Teacher)", passed_agent, f"Action: {res_agent.json().get('action')}"))

    res_agent_std = client.post("/api/agent/chat", json={
        "user_id": 999,
        "role": "student",
        "message": "Tự động tạo bài tập luyện các từ mình hay đọc sai"
    })
    passed_agent_std = res_agent_std.status_code == 200 and res_agent_std.json().get("status") == "success"
    results.append(("POST /api/agent/chat (Student)", passed_agent_std, f"Action: {res_agent_std.json().get('action')}"))

    # Print summary
    print("\n---------------- TEST SUMMARY RESULTS ----------------")
    all_passed = True
    for api_name, status, response in results:
        icon = "[PASS]" if status else "[FAIL]"
        if not status:
            all_passed = False
        print(f"{icon} | {api_name:<45} | Output: {response}")

    print("==================================================")
    if all_passed:
        print(" ALL 11 API ENDPOINTS PASSED SELF-TEST SUCCESSFULLY! ")
    else:
        print(" SOME API ENDPOINTS FAILED SELF-TEST! ")
    print("==================================================")
    return all_passed

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
