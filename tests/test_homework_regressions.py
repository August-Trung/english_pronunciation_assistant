"""Route regressions with real temporary SQLite and mocked speech/cloud services.

Load route definitions without starting the production model or database startup.
"""
from contextlib import contextmanager
import ast
import asyncio
import io
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from fastapi import HTTPException, UploadFile


class HomeworkRegressions(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        db = Path(self.tmp.name) / 'test.db'
        self.db = str(db)
        with self.database() as conn:
            conn.executescript('''
                CREATE TABLE classrooms (id INTEGER, name TEXT, join_code TEXT, grade_level TEXT, IsXoa INTEGER DEFAULT 0);
                CREATE TABLE class_enrollments (class_id INTEGER, student_id INTEGER, IsXoa INTEGER DEFAULT 0);
                CREATE TABLE assignments (id INTEGER PRIMARY KEY, class_id INTEGER, title TEXT, topic_sentence TEXT, target_ipa TEXT, due_date TEXT,
                    assignment_type TEXT, image_url TEXT, guiding_questions TEXT, target_keywords TEXT, time_limit_seconds INTEGER, IsXoa INTEGER DEFAULT 0);
                CREATE TABLE submissions (id INTEGER PRIMARY KEY, assignment_id INTEGER, student_id INTEGER, student_name TEXT,
                    audio_url TEXT, audio_size_bytes INTEGER, transcribed_text TEXT, score REAL, ipa_json TEXT,
                    teacher_feedback TEXT, score_override REAL, IsXoa INTEGER DEFAULT 0);
                INSERT INTO classrooms VALUES (1, 'Grade 4', 'CLS-TEST', 'Elementary (Grades 1 - 5)', 0);
                INSERT INTO class_enrollments VALUES (1, 5, 0);
                INSERT INTO assignments VALUES (1, 1, 'Pets', 'I like cats.', '', '', 'sentence', '/uploads/cat.png', '[]', '["cat"]', 60, 0);
            ''')
        wav = Path(self.tmp.name) / 'input.wav'
        self.wav = wav
        self.g = dict(sqlite3=sqlite3, DB_PATH=str(db), json=json, os=os,
            HTTPException=HTTPException, UploadFile=UploadFile,
            RECORDINGS_DIR=self.tmp.name,
            convert_audio_to_wav=Mock(side_effect=lambda _: (wav.write_bytes(b'RIFF-test') and str(wav), 125.0)),
            transcribe_audio=Mock(return_value=('I like cats.', 0.95)),
            analyze_speech=Mock(return_value=(8.0, 'Feedback', {'Fluency': 1.6})),
            evaluate_reading_accuracy=Mock(return_value={'accuracy': 100, 'word_analysis': [{'word': 'cats', 'status': 'correct'}]}),
            analyze_topic_response_with_ai=Mock(return_value={'comments': {'advice': 'Practice'}}),
            evaluate_ipa_phonetics=Mock(return_value={'words_ipa': []}),
            evaluate_picture_speaking=Mock(return_value={'score': 86, 'feedback': 'Picture feedback'}),
            upload_audio_to_supabase=Mock(return_value=None), export_db_to_json=Mock())
        with self.database() as conn:
            for column in ['teacher_id INTEGER', 'tenant_id TEXT', 'status TEXT DEFAULT \'active\'', 'created_at TEXT']:
                conn.execute('ALTER TABLE assignments ADD COLUMN ' + column)
            conn.execute('ALTER TABLE submissions ADD COLUMN submitted_at TEXT')
            conn.executescript('''CREATE TABLE users (id INTEGER, name TEXT, email TEXT, avatar TEXT, IsXoa INTEGER DEFAULT 0);
                CREATE TABLE history (id INTEGER, user_id INTEGER, score REAL, IsXoa INTEGER DEFAULT 0);
                INSERT INTO users VALUES (5, 'Learner', 'review@example.test', '', 0);''')
        self.g.update(CreateAssignmentRequest=SimpleNamespace,
            verify_class_access=Mock(return_value={'id': 1, 'teacher_id': 2, 'tenant_id': None, 'name': 'Grade 4', 'grade_level': 'Elementary (Grades 1 - 5)', 'join_code': 'CLS-TEST', 'is_archived': False}),
            record_audit_log=Mock(), calculate_user_streak=Mock(return_value=0))
        names = {'submission_evaluation', 'get_student_assignments', 'submit_assignment', 'create_assignment', 'get_class_gradebook', 'get_leaderboard'}
        tree = ast.parse(Path('backend/app/main.py').read_text(encoding='utf-8'))
        nodes = []
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names:
                node.decorator_list = []
                node.args.defaults = []
                nodes.append(node)
        exec(compile(ast.Module(body=nodes, type_ignores=[]), 'homework_routes', 'exec'), self.g)

    @contextmanager
    def database(self):
        conn = sqlite3.connect(self.db)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def submit(self, student=5):
        upload = UploadFile(filename='recording.webm', file=io.BytesIO(b'webm audio'))
        return asyncio.run(self.g['submit_assignment'](1, student, 'Learner', upload))

    def test_created_picture_survives_both_teacher_and_student_read_paths(self):
        req = SimpleNamespace(class_id=1, teacher_id=2, title='Picnic', topic_sentence='Describe the picnic', target_ipa='', due_date='2026-10-25', assignment_type='picture', image_url='/uploads/picnic.png', guiding_questions=['Who is here?'], target_keywords=['picnic'], time_limit_seconds=0)
        teacher = {'id': 2, 'role': 'teacher'}
        created = self.g['create_assignment'](req, teacher)
        self.assertEqual(created['status'], 'success')
        gradebook = self.g['get_class_gradebook'](1, teacher)
        self.assertEqual(gradebook['assignments'][0]['image_url'], req.image_url)
        student = self.g['get_student_assignments'](5)['assignments'][0]
        self.assertEqual(student['image_url'], req.image_url)
        self.assertEqual(student['guiding_questions'], req.guiding_questions)
        self.assertEqual(student['time_limit_seconds'], 0)

    def test_leaderboard_ranks_average_then_practice_count(self):
        with self.database() as conn:
            conn.executescript("""INSERT INTO users VALUES (6, 'Other', '', '', 0);
                INSERT INTO history VALUES (1,5,10,0),(2,5,6,0),(3,6,9.4,0);""")
        rows = self.g['get_leaderboard']('freemium')
        self.assertEqual([r['user_id'] for r in rows], [6, 5])
        self.assertEqual(rows[1]['avg_score'], 8)
        self.assertEqual(rows[1]['best_score'], 10)

    def test_cloud_failure_keeps_playable_audio_and_complete_assessment(self):
        result = self.submit()
        self.assertTrue(result['audio_url'].startswith('/uploads/recordings/'))
        self.assertTrue((Path(self.tmp.name) / Path(result['audio_url']).name).exists())
        self.assertEqual(result['evaluation']['duration_seconds'], 125)
        self.assertEqual(result['score'], 10)
        restored = self.g['get_student_assignments'](5)['assignments'][0]
        self.assertEqual(restored['evaluation'], result['evaluation'])
        self.assertEqual(restored['audio_url'], result['audio_url'])
        self.assertEqual(restored['image_url'], '/uploads/cat.png')
        self.assertFalse(self.wav.exists())

    def test_picture_uses_actual_evaluator_score(self):
        with self.database() as conn:
            conn.execute("UPDATE assignments SET assignment_type = 'picture'")
        result = self.submit()
        self.assertEqual(result['score'], 8.6)
        self.assertEqual(result['evaluation']['picture_eval']['score'], 86)

    def test_unrecognized_speech_is_not_replaced_with_model_sentence(self):
        self.g['transcribe_audio'].return_value = ('', 0)
        with self.assertRaises(HTTPException) as error:
            self.submit()
        self.assertEqual(error.exception.status_code, 422)
        with self.database() as conn:
            self.assertEqual(conn.execute('SELECT COUNT(*) FROM submissions').fetchone()[0], 0)
        self.assertFalse(self.wav.exists())

    def test_latest_active_submission_and_educator_override(self):
        self.submit()
        self.submit()
        with self.database() as conn:
            conn.execute('UPDATE submissions SET score_override=7 WHERE id=2')
            conn.execute('INSERT INTO submissions (assignment_id, student_id, score, IsXoa) VALUES (1,5,1,1)')
        rows = self.g['get_student_assignments'](5)['assignments']
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['submission_id'], 2)
        self.assertEqual(rows[0]['score'], 7)
        self.assertEqual(rows[0]['ai_score'], 10)

    def test_unenrolled_student_cannot_submit(self):
        with self.assertRaises(HTTPException) as error:
            self.submit(999)
        self.assertEqual(error.exception.status_code, 404)
        self.g['transcribe_audio'].assert_not_called()

    def test_legacy_assessment_does_not_invent_breakdown(self):
        self.assertEqual(self.g['submission_evaluation']('broken'), {})
        self.assertEqual(self.g['submission_evaluation']('{"confidence": 0.8}'), {'confidence': 0.8})


if __name__ == '__main__':
    unittest.main()
