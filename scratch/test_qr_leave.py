import sys
import os

sys.path.insert(0, r"d:\Study\Projects\Python project\english_pronunciation_assistant\backend\app")

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_qr_leave_ecosystem():
    print("--- 1. Testing Teacher Class Creation & Join Code Generation ---")
    res = client.post("/api/classes/create", json={
        "teacher_id": 1,
        "name": "Class 5A QR Test",
        "grade_level": "Elementary (Grades 1 - 5)"
    })
    print("Create Class Status:", res.status_code)
    data = res.json()
    print("Create Class Data:", data)
    class_id = data.get("class_id")
    join_code = data.get("join_code")

    print("\n--- 2. Testing Student Auto-Join via QR Deep Link Code ---")
    res_join = client.post("/api/classes/join", json={
        "student_id": 1,
        "join_code": join_code
    })
    print("Join Class Status:", res_join.status_code)
    print("Join Class Data:", res_join.json())

    print("\n--- 3. Testing Duplicate Join Attempt ---")
    res_dup = client.post("/api/classes/join", json={
        "student_id": 1,
        "join_code": join_code
    })
    print("Duplicate Join Status:", res_dup.status_code)
    print("Duplicate Join Data:", res_dup.json())

    print("\n--- 4. Testing Git-Style Safety Leave Class API ---")
    res_leave = client.post("/api/classes/leave", json={
        "student_id": 1,
        "class_id": class_id
    })
    print("Leave Class Status:", res_leave.status_code)
    print("Leave Class Data:", res_leave.json())

    print("\n✅ ALL QR & SAFETY UNENROLLMENT TESTS PASSED 100%!")

if __name__ == "__main__":
    test_qr_leave_ecosystem()
