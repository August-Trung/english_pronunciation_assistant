"""
Automated Verification Suite for P2: Educator & Teacher Operations & Insights
Covers:
1. Teacher Authentication & Access Token Issuance (PBKDF2 hash)
2. Classroom Ownership & Access Gate (Teacher isolation)
3. Assignment Lifecycle (Create, Update, Delete)
4. Cross-Teacher Ownership Protection (Teacher B cannot edit/delete Teacher A's class/assignment - 403)
5. Assignment Duplication (same class and across classes)
6. Cross-Teacher Duplication Gate (cannot clone into unowned class - 403)
7. Assignment Re-open & Deadline Extension
8. Missing Submissions Identification & Reminder Alert Dispatch
9. Class Analytics Engine (KPIs, Completion Rate, Weak Phonemes, At-Risk Students)
10. Gradebook CSV Export with UTF-8 BOM & Summary Row
11. Class Noticeboard CRUD & Student Notifications Integration
12. Suspended Teacher Immediate Lockout (403)
13. Multi-Tenant Admin Isolation (Admin A can manage; Admin B blocked - 403)
"""

import sys
import os
import json
import sqlite3
import random
import time
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "app")))
from fastapi.testclient import TestClient
import main
from main import app, DB_PATH
from security import hash_password, create_access_token

client = TestClient(app)

def run_test(name, condition, details=""):
    if condition:
        print(f"[PASS] {name}")
    else:
        print(f"[FAIL] {name}: {details}")
        assert False, f"Test failed: {name} - {details}"

print("=" * 60)
print("RUNNING P2 TEACHER OPERATIONS & INSIGHTS VERIFICATION SUITE")
print("=" * 60)

# Setup Test Data in SQLite
conn = sqlite3.connect(DB_PATH, timeout=20.0)
cursor = conn.cursor()

# 1. School 1 (Tenant 1) & School 2 (Tenant 2)
cursor.execute("INSERT OR IGNORE INTO tenants (id, name, license_seats) VALUES ('1', 'Fluent English Academy', 100)")
cursor.execute("INSERT OR IGNORE INTO tenants (id, name, license_seats) VALUES ('2', 'Global Language Institute', 100)")

# 2. Teacher 1 (School 1)
cursor.execute("SELECT id FROM users WHERE email = 'teacher1_p2@fluent.edu.vn'")
r = cursor.fetchone()
if not r:
    cursor.execute("""
        INSERT INTO users (email, name, role, tenant_id, status, password_hash)
        VALUES ('teacher1_p2@fluent.edu.vn', 'Prof. Arthur Pendelton', 'teacher', '1', 'active', ?)
    """, (hash_password("teachpass123"),))
    t1_id = cursor.lastrowid
else:
    t1_id = r[0]

# 3. Teacher 2 (School 1)
cursor.execute("SELECT id FROM users WHERE email = 'teacher2_p2@fluent.edu.vn'")
r = cursor.fetchone()
if not r:
    cursor.execute("""
        INSERT INTO users (email, name, role, tenant_id, status, password_hash)
        VALUES ('teacher2_p2@fluent.edu.vn', 'Dr. Beatrice Wright', 'teacher', '1', 'active', ?)
    """, (hash_password("teachpass123"),))
    t2_id = cursor.lastrowid
else:
    t2_id = r[0]

# 4. School Admin 1 (School 1) & School Admin 2 (School 2)
cursor.execute("SELECT id FROM users WHERE email = 'admin1_p2@fluent.edu.vn'")
r = cursor.fetchone()
if not r:
    cursor.execute("""
        INSERT INTO users (email, name, role, tenant_id, status, password_hash)
        VALUES ('admin1_p2@fluent.edu.vn', 'Admin School 1', 'admin', '1', 'active', ?)
    """, (hash_password("adminpass123"),))
    admin1_id = cursor.lastrowid
else:
    admin1_id = r[0]

cursor.execute("SELECT id FROM users WHERE email = 'admin2_p2@global.edu.vn'")
r = cursor.fetchone()
if not r:
    cursor.execute("""
        INSERT INTO users (email, name, role, tenant_id, status, password_hash)
        VALUES ('admin2_p2@global.edu.vn', 'Admin School 2', 'admin', '2', 'active', ?)
    """, (hash_password("adminpass123"),))
    admin2_id = cursor.lastrowid
else:
    admin2_id = r[0]

# 5. Students in School 1
cursor.execute("SELECT id FROM users WHERE email = 'std_alice_p2@fluent.edu.vn'")
r = cursor.fetchone()
if not r:
    cursor.execute("""
        INSERT INTO users (email, name, role, tenant_id, status, password_hash)
        VALUES ('std_alice_p2@fluent.edu.vn', 'Alice Johnson', 'student', '1', 'active', ?)
    """, (hash_password("student123"),))
    alice_id = cursor.lastrowid
else:
    alice_id = r[0]

cursor.execute("SELECT id FROM users WHERE email = 'std_bob_p2@fluent.edu.vn'")
r = cursor.fetchone()
if not r:
    cursor.execute("""
        INSERT INTO users (email, name, role, tenant_id, status, password_hash)
        VALUES ('std_bob_p2@fluent.edu.vn', 'Bob Smith', 'student', '1', 'active', ?)
    """, (hash_password("student123"),))
    bob_id = cursor.lastrowid
else:
    bob_id = r[0]

conn.commit()
conn.close()

# Generate Auth Tokens
t1_token = create_access_token(t1_id, "teacher1_p2@fluent.edu.vn", "teacher", "1")
t2_token = create_access_token(t2_id, "teacher2_p2@fluent.edu.vn", "teacher", "1")
admin1_token = create_access_token(admin1_id, "admin1_p2@fluent.edu.vn", "admin", "1")
admin2_token = create_access_token(admin2_id, "admin2_p2@global.edu.vn", "admin", "2")

t1_headers = {"Authorization": f"Bearer {t1_token}"}
t2_headers = {"Authorization": f"Bearer {t2_token}"}
admin1_headers = {"Authorization": f"Bearer {admin1_token}"}
admin2_headers = {"Authorization": f"Bearer {admin2_token}"}

# TEST 1: Teacher Login with salted PBKDF2 hash
res = client.post("/api/teacher/login", json={"email": "teacher1_p2@fluent.edu.vn", "password": "teachpass123"})
run_test("1. Teacher Login Success & Token Issuance", res.status_code == 200 and "token" in res.json(), res.text)

# TEST 2: Teacher 1 Creates Classroom
res = client.post("/api/classes/create", headers=t1_headers, json={
    "name": "IELTS Academic Pronunciation 6A",
    "grade_level": "High School & IELTS (Grades 10 - 12)"
})
run_test("2. Teacher 1 Created Classroom", res.status_code == 200, res.text)
c1_data = res.json()
class1_id = c1_data["class_id"]

# Enroll Alice and Bob in Class 1
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("INSERT OR IGNORE INTO class_enrollments (class_id, student_id, tenant_id, IsXoa) VALUES (?, ?, '1', 0)", (class1_id, alice_id))
c.execute("INSERT OR IGNORE INTO class_enrollments (class_id, student_id, tenant_id, IsXoa) VALUES (?, ?, '1', 0)", (class1_id, bob_id))
conn.commit()
conn.close()

# TEST 3: Teacher 1 Creates Assignment 1
res = client.post("/api/assignments/create", headers=t1_headers, json={
    "class_id": class1_id,
    "title": "Module 1: Dental Fricatives /θ/ & /ð/",
    "topic_sentence": "I think this healthy mouth produces perfect English rhythm.",
    "target_ipa": "/θɪŋk/ /ðɪs/ /ˈhel.θi/ /maʊθ/",
    "due_date": "2026-10-25"
})
run_test("3. Teacher 1 Created Assignment 1", res.status_code == 200, res.text)
asg1_id = res.json()["assignment_id"]

# TEST 4: Teacher 2 Blocked from Modifying Teacher 1's Assignment (HTTP 403)
res = client.post(f"/api/assignments/{asg1_id}/update", headers=t2_headers, json={
    "title": "Hacked Title by Teacher 2",
    "topic_sentence": "Malicious modification",
    "target_ipa": "",
    "due_date": "2026-11-01"
})
run_test("4. Teacher 2 Blocked from Modifying Teacher 1's Assignment (403)", res.status_code == 403, res.text)

# TEST 5: Teacher 2 Blocked from Deleting Teacher 1's Assignment (HTTP 403)
res = client.delete(f"/api/assignments/{asg1_id}", headers=t2_headers)
run_test("5. Teacher 2 Blocked from Deleting Teacher 1's Assignment (403)", res.status_code == 403, res.text)

# TEST 6: Teacher 2 Blocked from Accessing Teacher 1's Gradebook (HTTP 403)
res = client.get(f"/api/classes/{class1_id}/gradebook", headers=t2_headers)
run_test("6. Teacher 2 Blocked from Accessing Teacher 1's Gradebook (403)", res.status_code == 403, res.text)

# TEST 7: Teacher 1 Updates Assignment 1
res = client.post(f"/api/assignments/{asg1_id}/update", headers=t1_headers, json={
    "title": "Module 1: Dental Fricatives (Updated)",
    "topic_sentence": "I think this healthy mouth produces perfect English rhythm.",
    "target_ipa": "/θɪŋk/ /ðɪs/ /ˈhel.θi/ /maʊθ/",
    "due_date": "2026-10-26"
})
run_test("7. Teacher 1 Updated Assignment 1", res.status_code == 200, res.text)

# TEST 8: Teacher 1 Duplicates Assignment (Clone to same class)
res = client.post(f"/api/assignments/{asg1_id}/duplicate", headers=t1_headers, json={
    "new_title": "Module 1 Practice: Dental Fricatives Drill B",
    "new_due_date": "2026-11-02"
})
run_test("8. Teacher 1 Duplicated Assignment to Same Class", res.status_code == 200, res.text)
asg2_id = res.json()["new_assignment_id"]

# TEST 9: Teacher 1 Blocked from Duplicating to Unowned Class (HTTP 403)
# Create class owned by Teacher 2
res = client.post("/api/classes/create", headers=t2_headers, json={"name": "Teacher 2 Class", "grade_level": "Elementary"})
class2_id = res.json()["class_id"]
res = client.post(f"/api/assignments/{asg1_id}/duplicate", headers=t1_headers, json={
    "target_class_id": class2_id
})
run_test("9. Teacher 1 Blocked from Duplicating to Teacher 2's Class (403)", res.status_code == 403, res.text)

# TEST 10: Teacher 1 Re-opens / Extends Deadline for Assignment 1
res = client.post(f"/api/assignments/{asg1_id}/reopen", headers=t1_headers, json={
    "new_due_date": "2026-11-15",
    "extension_note": "Extended by request of student study group."
})
run_test("10. Teacher 1 Re-opened / Extended Deadline", res.status_code == 200 and res.json().get("new_due_date") == "2026-11-15", res.text)

# Simulate Alice Submits Assignment 1 (Bob does NOT submit)
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("""
    INSERT INTO submissions (assignment_id, student_id, student_name, transcribed_text, score, ipa_json, audio_url, IsXoa)
    VALUES (?, ?, 'Alice Johnson', 'I think this healthy mouth produces perfect English rhythm.', 8.8, '{\"confidence\": 0.95}', 'https://example.com/audio1.mp3', 0)
""", (asg1_id, alice_id))
# Add weak word for Bob
c.execute("INSERT OR REPLACE INTO weak_words (user_id, word, ipa, error_count, IsXoa) VALUES (?, 'mouth', '/maʊθ/', 3, 0)", (bob_id,))
conn.commit()
conn.close()

# TEST 11: Teacher Reminds Non-Submitters (Bob should be detected and notified)
res = client.post(f"/api/assignments/{asg1_id}/remind", headers=t1_headers, json={
    "custom_message": "Bob and peers, please submit your audio recording before the deadline!"
})
run_test("11. Teacher Dispatched Reminder to Non-Submitters", res.status_code == 200, res.text)
remind_data = res.json()
run_test("11b. Reminder identified exactly 1 non-submitter (Bob)", remind_data.get("reminded_count") == 1 and remind_data["reminded_students"][0]["id"] == bob_id, str(remind_data))

# TEST 12: Class Analytics Engine
res = client.get(f"/api/classes/{class1_id}/analytics", headers=t1_headers)
run_test("12. Class Analytics Retrieved Successfully", res.status_code == 200, res.text)
analytics = res.json()
run_test("12a. Analytics Summary Metrics Accurate", analytics["summary"]["total_students"] == 2 and analytics["summary"]["total_assignments"] >= 2, str(analytics["summary"]))
run_test("12b. Weak Phonemes Identified Trouble Spots", len(analytics["weak_phonemes"]) > 0 and any(p["symbol"] == "θ" for p in analytics["weak_phonemes"]), str(analytics["weak_phonemes"]))
run_test("12c. At-Risk Students Flagged Non-Submitter Bob", any(st["id"] == bob_id for st in analytics["at_risk_students"]), str(analytics["at_risk_students"]))

# TEST 13: Gradebook CSV Export with UTF-8 BOM
res = client.get(f"/api/classes/{class1_id}/export-gradebook", headers=t1_headers)
run_test("13. Gradebook CSV Export HTTP 200", res.status_code == 200, res.text)
run_test("13b. CSV Header Content-Type text/csv", "text/csv" in res.headers.get("content-type", ""), res.headers.get("content-type"))
csv_bytes = res.content
run_test("13c. CSV Starts with UTF-8 BOM", csv_bytes.startswith(b'\xef\xbb\xbf'), "Missing UTF-8 BOM")
csv_text = csv_bytes.decode('utf-8')
run_test("13d. CSV Contains Student Names & Scores", "Alice Johnson" in csv_text and "Bob Smith" in csv_text and "CLASS AVERAGE" in csv_text, csv_text[:300])

# TEST 14: Class Noticeboard CRUD
# Create Announcement
res = client.post(f"/api/classes/{class1_id}/announcements", headers=t1_headers, json={
    "title": "Welcome to Semester 1",
    "content": "Please practice IPA symbols daily in the Learning Studio.",
    "announcement_type": "general"
})
run_test("14a. Posted Class Noticeboard Announcement", res.status_code == 200, res.text)
ann_id = res.json()["announcement_id"]

# Fetch Announcements
res = client.get(f"/api/classes/{class1_id}/announcements", headers=t1_headers)
run_test("14b. Retrieved Announcements for Class", res.status_code == 200 and len(res.json()["announcements"]) >= 2, res.text)

# Student Notifications Endpoint
res = client.get(f"/api/notifications/student/{bob_id}")
run_test("14c. Student Notifications Delivered to Bob", res.status_code == 200 and len(res.json()["notifications"]) >= 2, res.text)

# Delete Announcement
res = client.delete(f"/api/classes/{class1_id}/announcements/{ann_id}", headers=t1_headers)
run_test("14d. Deleted Class Announcement Successfully", res.status_code == 200, res.text)

# TEST 15: Suspended Teacher Immediately Blocked (HTTP 403)
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("UPDATE users SET status = 'suspended' WHERE id = ?", (t1_id,))
conn.commit()
conn.close()

res = client.get(f"/api/classes/{class1_id}/gradebook", headers=t1_headers)
run_test("15a. Suspended Teacher Blocked from Gradebook (403)", res.status_code == 403, res.text)
res = client.post("/api/assignments/create", headers=t1_headers, json={"class_id": class1_id, "title": "Test", "topic_sentence": "Test"})
run_test("15b. Suspended Teacher Blocked from Creating Assignment (403)", res.status_code == 403, res.text)

# Reactivate Teacher 1
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("UPDATE users SET status = 'active' WHERE id = ?", (t1_id,))
conn.commit()
conn.close()

# TEST 16: School Admin Governance & Cross-Tenant Isolation
# School Admin 1 (same tenant) can access Teacher 1's class gradebook and analytics
res = client.get(f"/api/classes/{class1_id}/gradebook", headers=admin1_headers)
run_test("16a. School Admin 1 Permitted to Access School 1 Gradebook", res.status_code == 200, res.text)

# School Admin 2 (different tenant) is strictly blocked (HTTP 403)
res = client.get(f"/api/classes/{class1_id}/gradebook", headers=admin2_headers)
run_test("16b. School Admin 2 Blocked from Accessing School 1 Gradebook (403)", res.status_code == 403, res.text)

res = client.get(f"/api/classes/{class1_id}/analytics", headers=admin2_headers)
run_test("16c. School Admin 2 Blocked from Accessing School 1 Analytics (403)", res.status_code == 403, res.text)

print("=" * 60)
print("RESULTS: ALL 16 P2 TEACHER TEST SCENARIOS PASSED (100%)")
print("=" * 60)
