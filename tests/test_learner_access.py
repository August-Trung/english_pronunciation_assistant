from contextlib import closing
import ast
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import Mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1] / 'backend' / 'app'))
from fastapi import HTTPException, Depends
from pydantic import BaseModel
from learner_access import learner_identity, invite_preview
from security import hash_password, verify_password, create_access_token
import learner_access

class LearnerAccessTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.db=str(Path(self.tmp.name)/'class.db')
        with closing(sqlite3.connect(self.db)) as c,c:
            c.executescript("""
                CREATE TABLE users(id INTEGER PRIMARY KEY,email TEXT UNIQUE,name TEXT,role TEXT,tenant_id TEXT,password_hash TEXT,IsXoa INTEGER DEFAULT 0);
                CREATE TABLE classrooms(id INTEGER,name TEXT,grade_level TEXT,join_code TEXT,tenant_id TEXT,is_archived INTEGER,teacher_id INTEGER,IsXoa INTEGER DEFAULT 0);
                CREATE TABLE class_enrollments(id INTEGER PRIMARY KEY,class_id INTEGER,student_id INTEGER,tenant_id TEXT,joined_at TEXT,IsXoa INTEGER DEFAULT 0);
                INSERT INTO classrooms VALUES(1,'Grade 4','Elementary (Grades 1 - 5)','CLS-TEST',NULL,0,10,0);
                INSERT INTO classrooms VALUES(2,'Old Class','primary','CLS-OLD',NULL,1,10,0);
                INSERT INTO classrooms VALUES(3,'High School','secondary','CLS-HIGH',NULL,0,10,0);
            """)
        self.key='a'*64
        self.namespace=dict(Depends=Depends,get_current_authenticated_user=Mock(),__package__='backend.app',BaseModel=BaseModel,DB_PATH=self.db,
            hash_password=hash_password,verify_password=verify_password,create_access_token=create_access_token,
            get_current_user_from_db=Mock(),sqlite3=sqlite3,HTTPException=HTTPException,
            get_teacher_quota_info=Mock(return_value=None),export_db_to_json=Mock())
        sys.modules['backend.app.learner_access']=learner_access
        names={'GoogleLoginRequest','google_login','LearnerInviteRequest','LearnerResumeRequest','JoinClassRequest','join_learner_invite','resume_learner','join_class'}
        nodes=[]
        for n in ast.parse(Path('backend/app/main.py').read_text(encoding='utf-8')).body:
            if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in names:
                if isinstance(n,ast.FunctionDef):n.decorator_list=[]
                nodes.append(n)
        exec(compile(ast.Module(body=nodes,type_ignores=[]),'learner_routes','exec'),self.namespace)

    def join(self,key=None,name='Nguyễn An',code='CLS-TEST'):
        req=self.namespace['LearnerInviteRequest'](student_key=key or self.key,name=name,join_code=code)
        return self.namespace['join_learner_invite'](req)

    def test_first_join_needs_no_email_and_returns_student_session(self):
        result=self.join()
        self.assertEqual(result['user']['role'],'student'); self.assertTrue(result['user']['token'])
        self.assertEqual(result['class_id'],1)
        with closing(sqlite3.connect(self.db)) as c:
            row=c.execute('SELECT password_hash FROM users').fetchone()
            self.assertNotEqual(row[0],self.key)
            self.assertEqual(c.execute('SELECT COUNT(*) FROM class_enrollments').fetchone()[0],1)

    def test_retry_and_return_visit_preserve_identity_and_enrollment(self):
        first=self.join();again=self.join(name='Changed text')
        resumed=self.namespace['resume_learner'](self.namespace['LearnerResumeRequest'](student_key=self.key))
        self.assertEqual(first['user']['id'],again['user']['id'])
        self.assertEqual(first['user']['id'],resumed['user']['id'])
        self.assertEqual(resumed['user']['name'],'Nguyễn An')
        with closing(sqlite3.connect(self.db)) as c:
            self.assertEqual(c.execute('SELECT COUNT(*) FROM users').fetchone()[0],1)
            self.assertEqual(c.execute('SELECT COUNT(*) FROM class_enrollments').fetchone()[0],1)

    def test_same_names_never_merge_children(self):
        a=self.join();b=self.join(key='b'*64)
        self.assertNotEqual(a['user']['id'],b['user']['id'])

    def test_bad_or_archived_invite_creates_no_account(self):
        for code in ['UNKNOWN','CLS-OLD','CLS-HIGH']:
            with self.assertRaises(HTTPException):self.join(code=code)
        with closing(sqlite3.connect(self.db)) as c:self.assertEqual(c.execute('SELECT COUNT(*) FROM users').fetchone()[0],0)

    def test_unknown_or_short_recovery_key_is_rejected(self):
        self.join()
        for key in ['x','b'*64]:
            with self.assertRaises(HTTPException):learner_identity(self.db,key,'',hash_password,verify_password)

    def test_deleted_profile_cannot_be_restored_or_recreated(self):
        self.join()
        with closing(sqlite3.connect(self.db)) as c,c:c.execute('UPDATE users SET IsXoa=1')
        with self.assertRaises(HTTPException):self.join()

    def test_preview_exposes_only_class_metadata(self):
        self.assertEqual(set(invite_preview(self.db,' cls-test ')),{'class_id','class_name','grade_level'})

    def test_existing_quota_check_is_not_bypassed(self):
        self.namespace['get_teacher_quota_info'].return_value={'teacher_type':'freelance','is_expired':False,'used_seats':3,'max_seats':3}
        with self.assertRaises(HTTPException) as error:self.join()
        self.assertEqual(error.exception.status_code,403)
        with closing(sqlite3.connect(self.db)) as c:self.assertEqual(c.execute('SELECT COUNT(*) FROM class_enrollments').fetchone()[0],0)

    def test_public_email_only_login_cannot_take_over_device_learner(self):
        user=self.join()['user']
        request=self.namespace['GoogleLoginRequest'](email=user['email'])
        with self.assertRaises(HTTPException) as error:self.namespace['google_login'](request)
        self.assertEqual(error.exception.status_code,401)

    def test_enrollment_cannot_spoof_another_student(self):
        req=self.namespace['JoinClassRequest'](student_id=123,join_code='CLS-TEST')
        with self.assertRaises(HTTPException) as error:self.namespace['join_class'](req,{'id':999,'role':'student'})
        self.assertEqual(error.exception.status_code,403)

    def test_suspended_profile_is_rejected_before_enrollment(self):
        self.namespace['get_current_user_from_db'].side_effect=HTTPException(403,'Suspended')
        with self.assertRaises(HTTPException):self.join()
        with closing(sqlite3.connect(self.db)) as c:self.assertEqual(c.execute('SELECT COUNT(*) FROM class_enrollments').fetchone()[0],0)
