import sqlite3
import os

db_path = 'backend/app/app_data.db'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, email, name, role, tenant_id 
        FROM users 
        WHERE (IsXoa IS NULL OR IsXoa = 0)
    """)
    rows = cursor.fetchall()
    print("=== DATABASE USER ACCOUNTS SUMMARY ===")
    print(f"Total Active Users in DB: {len(rows)}\n")
    
    admins = [r for r in rows if r[3] in ('super_admin', 'admin')]
    teachers = [r for r in rows if r[3] == 'teacher']
    students = [r for r in rows if r[3] not in ('super_admin', 'admin', 'teacher')]
    
    print(f"ADMIN / SUPER ADMIN ({len(admins)} accounts):")
    for r in admins:
        print(f"   - ID: {r[0]} | Email: {r[1]} | Name: {r[2]} | Role: {r[3]}")
        
    print(f"\nTEACHER / EDUCATOR ({len(teachers)} accounts):")
    for r in teachers:
        print(f"   - ID: {r[0]} | Email: {r[1]} | Name: {r[2]} | Role: {r[3]}")
        
    print(f"\nSTUDENTS ({len(students)} accounts):")
    for r in students:
        print(f"   - ID: {r[0]} | Email: {r[1]} | Name: {r[2]} | Role: {r[3]}")
        
    conn.close()
