"""Email-free learner identities, authenticated by a high-entropy recovery key."""
from contextlib import closing
import hashlib
import re
import sqlite3
import threading
import time

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


_login_failures = {}
_login_lock = threading.Lock()


def student_account(db_path, username, password, name, hash_password, verify_password, register=False, scope='local'):
    username = username.strip().lower()
    if not re.fullmatch(r'[a-z0-9][a-z0-9._-]{2,29}', username):
        raise HTTPException(400, 'Use a username of 3–30 letters, numbers, dots, underscores or hyphens.')
    if not 8 <= len(password) <= 128:
        raise HTTPException(400, 'Use a password of 8–128 characters.')
    email = username + '@students.invalid'
    limit_key = (scope, username)
    now = time.monotonic()
    with _login_lock:
        attempts = [t for t in _login_failures.get(limit_key, []) if now-t < 300]
        if len(attempts) >= 6:
            raise HTTPException(429, 'Too many sign-in attempts. Please try again in five minutes.')
    with closing(sqlite3.connect(db_path, timeout=20)) as conn:
        conn.execute('BEGIN IMMEDIATE')
        row = conn.execute("SELECT id,email,name,role,tenant_id,password_hash,COALESCE(IsXoa,0) FROM users WHERE email=?", (email,)).fetchone()
        if register:
            if row:
                raise HTTPException(409, 'This username is already taken. Sign in or choose a different username.')
            display = ' '.join(name.split()) or username
            if len(display) > 80:
                raise HTTPException(400, 'Full name must be at most 80 characters.')
            encoded = hash_password(password)
            result = conn.execute("INSERT INTO users(email,name,role,password_hash) VALUES(?,?,'student',?)", (email,display,encoded))
            conn.commit()
            row = (result.lastrowid,email,display,'student',None,encoded,0)
        elif not row or row[6] or row[3] != 'student' or not verify_password(password,row[5]):
            with _login_lock:
                if len(_login_failures) > 4096:
                    expired = [key for key,times in _login_failures.items() if not times or now-times[-1]>=300]
                    for key in expired: _login_failures.pop(key,None)
                    if len(_login_failures)>4096: _login_failures.pop(next(iter(_login_failures)))
                _login_failures[limit_key] = attempts + [now]
            raise HTTPException(401, 'Username or password is incorrect.')
    with _login_lock:
        _login_failures.pop(limit_key,None)
    return {'id':row[0], 'email':row[1], 'username':username, 'name':row[2], 'role':'student', 'tenant_id':row[4], 'avatar':''}
