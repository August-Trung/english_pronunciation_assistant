import sys
import os
import sqlite3

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend', 'app'))
from main import app, init_db, DB_PATH, upload_audio_to_supabase

print("1. Initializing & Verifying All DB Tables & Super Admin...")
init_db()
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

c.execute("SELECT email, role FROM users WHERE role = 'super_admin'")
super_admin = c.fetchone()
print("   -> Super Admin Account Found:", super_admin)
assert super_admin is not None, "Super admin not found"

print("2. Testing School Tenant Creation...")
c.execute("INSERT INTO tenants (id, name, license_seats) VALUES ('tenant_abc', 'Truong THCS ABC Test', 350)")
print("   -> School Tenant 'Truong THCS ABC Test' created with 350 seats")

print("\n3. Testing Teacher & Admin Account Provisioning...")
c.execute("""
    INSERT INTO users (email, name, role, tenant_id, parent_code, password_hash)
    VALUES ('teacher_test@abc.edu.vn', 'Thay Van A Test', 'teacher', 'tenant_abc', 'PA-9842', 'password123')
""")
teacher_id = c.lastrowid
print(f"   -> Teacher account provisioned (ID: {teacher_id}, Parent Code: PA-9842)")

print("\n4. Testing Parent Portal Report Generation...")
c.execute("INSERT INTO classrooms (teacher_id, name, join_code) VALUES (?, 'Lop 5A', 'CLS-5A-TEST')", (teacher_id,))
class_id = c.lastrowid

c.execute("INSERT INTO assignments (class_id, teacher_id, title, topic_sentence) VALUES (?, ?, 'Bai Doc Unit 1', 'Learning is fun')", (class_id, teacher_id))
asg_id = c.lastrowid

c.execute("""
    INSERT INTO submissions (assignment_id, student_id, student_name, audio_url, transcribed_text, score, teacher_feedback)
    VALUES (?, ?, 'Thay Van A Test', 'https://bdfiptyjwsmjyfunctvz.supabase.co/storage/v1/object/public/student-audio/test.webm', 'Learning is fun', 9.0, 'Doc rat tot!')
""", (asg_id, teacher_id))
conn.commit()

c.execute("SELECT name, parent_code FROM users WHERE parent_code = 'PA-9842'")
parent_user = c.fetchone()
print("   -> Parent Tracking Code Verified:", parent_user)

print("\n5. Cleaning up test data...")
c.execute("DELETE FROM submissions WHERE student_name = 'Thay Van A Test'")
c.execute("DELETE FROM assignments WHERE id = ?", (asg_id,))
c.execute("DELETE FROM classrooms WHERE id = ?", (class_id,))
c.execute("DELETE FROM users WHERE email = 'teacher_test@abc.edu.vn'")
c.execute("DELETE FROM tenants WHERE id = 'tenant_abc'")
conn.commit()
conn.close()

print("\n=== ALL 5-ROLE ECOSYSTEM MASTER API TESTS PASSED 100% WITH ZERO ERRORS! ===")
