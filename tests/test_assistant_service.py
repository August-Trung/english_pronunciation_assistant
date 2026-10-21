from contextlib import closing
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend' / 'app'))
from assistant_service import handle_assistant

class AssistantTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.db = str(Path(self.tmp.name) / 'db.sqlite')
        with closing(sqlite3.connect(self.db)) as c, c:
            c.executescript("""
            CREATE TABLE classrooms(id INTEGER,name TEXT,teacher_id INTEGER,IsXoa INTEGER DEFAULT 0);
            CREATE TABLE users(id INTEGER,name TEXT,IsXoa INTEGER DEFAULT 0);
            CREATE TABLE class_enrollments(class_id INTEGER,student_id INTEGER,IsXoa INTEGER DEFAULT 0);
            CREATE TABLE assignments(id INTEGER,class_id INTEGER,title TEXT,due_date TEXT,status TEXT DEFAULT 'active',IsXoa INTEGER DEFAULT 0);
            CREATE TABLE submissions(id INTEGER,assignment_id INTEGER,student_id INTEGER,score REAL,score_override REAL,IsXoa INTEGER DEFAULT 0);
            CREATE TABLE weak_words(user_id INTEGER,word TEXT,error_count INTEGER,IsXoa INTEGER DEFAULT 0);
            INSERT INTO classrooms VALUES(1,'Lớp học 4A1',10,0),(2,'Lớp học 5A1',20,0);
            INSERT INTO users VALUES(1,'Lan',0),(2,'Nam',0),(3,'Other School',0);
            INSERT INTO class_enrollments VALUES(1,1,0),(1,2,0),(2,3,0);
            INSERT INTO assignments VALUES(1,1,'Already Done','2026-12-01','active',0),(2,1,'Pending Reading','2026-12-02','active',0),(3,1,'Closed','2026-12-01','closed',0),(4,2,'Other School Assignment','','active',0);
            INSERT INTO submissions VALUES(1,1,1,8,NULL,0),(2,1,2,4,5,0),(3,4,3,1,NULL,0);
            INSERT INTO weak_words VALUES(1,'think',2,0),(3,'secret-word',9,0);
            """)

    def ask(self, text, teacher=False):
        return handle_assistant(text, {'id':10 if teacher else 1,'role':'teacher' if teacher else 'student'}, self.db)

    def test_pending_excludes_submitted_closed_and_other_classes(self):
        text = self.ask('Bài tập nào tôi chưa nộp?')['reply']
        self.assertIn('Pending Reading', text)
        for value in ['Already Done','Closed','Other School']: self.assertNotIn(value, text)

    def test_teacher_stats_are_scoped_and_respect_threshold(self):
        text = self.ask('Thống kê học sinh điểm dưới 6 lớp 4A1', True)['reply']
        self.assertIn('Nam', text); self.assertIn('5.0/10', text)
        self.assertNotIn('Lan', text); self.assertNotIn('Other School', text)

    def test_unknown_requested_class_never_uses_latest_class(self):
        text = self.ask('Xem bảng điểm lớp 10A1', True)['reply']
        self.assertIn('không tìm thấy', text)
        self.assertNotIn('Lan', text)

    def test_create_request_does_not_insert_or_claim_success(self):
        result = self.ask('Tạo bài tập gia đình lớp 4A1', True)
        self.assertEqual(result['action'], 'open_teacher')
        self.assertIn('chưa giao', result['reply'])
        with closing(sqlite3.connect(self.db)) as c, c: self.assertEqual(c.execute('SELECT COUNT(*) FROM assignments').fetchone()[0],4)

    def test_student_cannot_create_class_assignment(self):
        result = self.ask('Giao bài tập cho lớp 4A1')
        self.assertNotEqual(result['action'], 'assignment_created')

    def test_weak_words_only_belong_to_current_student(self):
        result = self.ask('Tạo bài tập luyện từ yếu')['reply']
        self.assertIn('think', result); self.assertNotIn('secret-word', result)

    def test_teacher_pending_lists_correct_students(self):
        result = self.ask('Kiểm tra bài tập chưa nộp lớp 4A1', True)['reply']
        self.assertIn('Pending Reading: Lan', result); self.assertIn('Pending Reading: Nam', result)
        self.assertNotIn('Already Done: Lan', result)

    def test_teacher_weak_words_stay_in_class(self):
        text = self.ask('Các từ phát âm sai của lớp 4A1', True)['reply']
        self.assertIn('think', text); self.assertNotIn('secret-word', text)

    def test_voiced_th_is_not_unvoiced(self):
        result = self.ask('Cách phát âm /ð/?')['reply']
        self.assertIn('/ð/', result); self.assertIn('rung', result); self.assertNotIn('**/θ/**', result)

    def test_roleplay_does_not_always_choose_hotel(self):
        result = self.ask('Đóng vai ở nhà hàng')['reply']
        self.assertNotIn('Hotel Receptionist', result)

    def test_ambiguous_classes_require_selection(self):
        with closing(sqlite3.connect(self.db)) as c, c: c.execute("INSERT INTO classrooms VALUES(3,'Lớp học 4A2',10,0)")
        result = self.ask('Xem bảng điểm', True)['reply']
        self.assertIn('lớp nào', result)

    def test_generic_question_is_not_fake_data_response(self):
        self.assertIsNone(self.ask('Bạn có thể giải thích present perfect không?'))

    def client(self):
        import ast
        import json
        import assistant_service
        from fastapi import FastAPI, Depends, Header, HTTPException
        from fastapi.testclient import TestClient
        from pydantic import BaseModel
        app = FastAPI()
        def authenticate(authorization: str = Header(default='')):
            if authorization != 'Bearer student-test':
                raise HTTPException(status_code=401)
            return {'id':1,'role':'student'}
        tree = ast.parse(Path('backend/app/main.py').read_text(encoding='utf-8'))
        nodes = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in ('AgentChatRequest','agent_chat')]
        sys.modules['backend.app.assistant_service'] = assistant_service
        namespace = dict(__package__='backend.app',BaseModel=BaseModel,Depends=Depends,
                         get_current_authenticated_user=authenticate,HTTPException=HTTPException,
                         DB_PATH=self.db,sqlite3=sqlite3,json=json,app=app,get_groq_api_keys=lambda:[])
        exec(compile(ast.Module(body=nodes,type_ignores=[]),'assistant_routes','exec'),namespace)
        return TestClient(app)

    def test_chat_requires_authentication(self):
        response = self.client().post('/api/agent/chat',json={'message':'Xem điểm','user_id':10,'role':'teacher'})
        self.assertEqual(response.status_code,401)

    def test_body_cannot_spoof_teacher_or_another_student(self):
        response = self.client().post('/api/agent/chat',headers={'Authorization':'Bearer student-test'},
            json={'message':'Xem điểm','user_id':3,'role':'teacher'})
        self.assertEqual(response.status_code,200)
        self.assertIn('8.0/10',response.json()['reply'])
        self.assertNotIn('Other School',response.json()['reply'])

    def test_provider_unavailable_does_not_fake_success(self):
        response = self.client().post('/api/agent/chat',headers={'Authorization':'Bearer student-test'},
            json={'message':'Giải thích thì hiện tại hoàn thành'})
        self.assertEqual(response.json()['status'],'unavailable')
        self.assertIsNone(response.json()['action'])

    def test_empty_message_returns_validation_error(self):
        response = self.client().post('/api/agent/chat',headers={'Authorization':'Bearer student-test'},json={'message':'  '})
        self.assertEqual(response.status_code,400)
