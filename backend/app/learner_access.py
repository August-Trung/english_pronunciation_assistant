"""Email-free learner identities, authenticated by a high-entropy recovery key."""
from contextlib import closing
import hashlib
import re
import sqlite3

from fastapi import HTTPException


def invite_preview(db_path, code):
    with closing(sqlite3.connect(db_path)) as conn:
        row = conn.execute("SELECT id,name,grade_level,COALESCE(is_archived,0) FROM classrooms WHERE UPPER(join_code)=? AND COALESCE(IsXoa,0)=0", (code.strip().upper(),)).fetchone()
    if not row:
        raise HTTPException(404, 'Class link not found. Please ask your teacher for a new link.')
    if row[3]:
        raise HTTPException(400, 'This class is archived. Please contact your teacher.')
    if row[2] not in ('Elementary (Grades 1 - 5)', 'primary'):
        raise HTTPException(400, 'Email-free access is available for elementary classrooms only.')
    return {'class_id':row[0], 'class_name':row[1], 'grade_level':row[2]}


def learner_identity(db_path, secret, name, hash_password, verify_password, create=False):
    # Never identify learners by display name: two children may share a name.
    if not re.fullmatch(r'[a-f0-9]{64}', secret):
        raise HTTPException(400, 'Invalid Student Key. Please use the complete saved key.')
    email = 'learner_' + hashlib.sha256(secret.encode()).hexdigest() + '@learners.invalid'
    with closing(sqlite3.connect(db_path, timeout=20)) as conn:
        conn.execute('BEGIN IMMEDIATE')
        row = conn.execute("SELECT id,email,name,role,tenant_id,password_hash,COALESCE(IsXoa,0) FROM users WHERE email=?", (email,)).fetchone()
        if not row:
            if not create:
                raise HTTPException(401, 'Student profile not found. Use your class link or check your Student Key.')
            clean_name = ' '.join(name.split())
            if not 2 <= len(clean_name) <= 80 or any(ord(c)<32 for c in clean_name):
                raise HTTPException(400, 'Please enter your full name (2–80 characters).')
            stored_hash = hash_password(secret)
            cursor = conn.execute("INSERT INTO users(email,name,role,password_hash) VALUES(?,?,'student',?)", (email, clean_name, stored_hash))
            row = (cursor.lastrowid, email, clean_name, 'student', None, stored_hash)
            conn.commit()
        elif row[6] or row[3] != 'student' or not verify_password(secret, row[5]):
            raise HTTPException(401, 'Student Key is not valid for this profile.')
    return {'id':row[0], 'email':row[1], 'name':row[2], 'role':'student', 'tenant_id':row[4], 'avatar':''}
