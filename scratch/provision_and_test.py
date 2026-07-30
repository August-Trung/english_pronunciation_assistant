import sqlite3
import urllib.request
import json
import os

# 1. Provision / Update SQLite Database
db_path = 'backend/app/app_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Ensure table schema
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    name TEXT,
    role TEXT DEFAULT 'student',
    tenant_id INTEGER,
    password_hash TEXT,
    IsXoa INTEGER DEFAULT 0
)
""")

accounts = [
    ("superadmin@fluent.edu.vn", "Super Admin", "super_admin", "superadmin123", 1),
    ("admin@fluent.edu.vn", "School Admin", "admin", "admin123", 1),
    ("teacher@fluent.edu.vn", "Educator Lead", "teacher", "teacher123", 1)
]

for email, name, role, password, tenant_id in accounts:
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    existing = cursor.fetchone()
    if existing:
        cursor.execute("""
            UPDATE users 
            SET name = ?, role = ?, password_hash = ?, tenant_id = ?, IsXoa = 0 
            WHERE email = ?
        """, (name, role, password, tenant_id, email))
        print(f"[DB PROVISIONED]: Updated {role} account -> {email}")
    else:
        cursor.execute("""
            INSERT INTO users (email, name, role, password_hash, tenant_id, IsXoa) 
            VALUES (?, ?, ?, ?, ?, 0)
        """, (email, name, role, password, tenant_id))
        print(f"[DB PROVISIONED]: Created new {role} account -> {email}")

conn.commit()
conn.close()

# Also sync app_data.db into scratch/hf_space_clone and hf_deploy if needed
print("\n--- SYNCING LOCAL DB WITH BACKEND DEPLOYMENT ---")
