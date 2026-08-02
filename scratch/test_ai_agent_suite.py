import sys
import os
import sqlite3
import time

# Ensure backend/app is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "app")))

from fastapi.testclient import TestClient
from main import app, DB_PATH

client = TestClient(app)

def run_ai_agent_test_suite():
    print("==========================================================================")
    print("       GROQ AI AGENT COPILOT DEDICATED EXTENSIVE TEST SUITE (20 TEST CASES) ")
    print("==========================================================================")

    # Seed test weak word in DB
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO weak_words (user_id, word, ipa, meaning, error_count) VALUES (1, 'environment', '/ɪnˈvaɪ.rən.mənt/', 'Môi trường', 5)")
    conn.commit()
    conn.close()

    test_cases = [
        # --- TEACHER / ADMIN AGENT TEST CASES ---
        ("AG-T01", "Teacher", "teacher", "Tạo bài tập 3 câu chủ đề Environment cho lớp 10A1", "assignment_created"),
        ("AG-T02", "Teacher", "teacher", "Tạo bài tập phát âm chủ đề gia đình cho lớp", "assignment_created"),
        ("AG-T03", "Teacher", "teacher", "Thống kê danh sách học sinh điểm phát âm dưới 6", "stats_queried"),
        ("AG-T04", "Teacher", "teacher", "Cho tôi xem bảng điểm lớp học", "stats_queried"),
        ("AG-T05", "Teacher", "teacher", "Xem các từ phát âm sai nhiều nhất của lớp", "remedial_generated"),
        ("AG-T06", "Admin", "admin", "Thống kê danh sách trường học B2B", "stats_queried"),
        ("AG-T07", "Admin", "admin", "Cho tôi xem danh sách học sinh", "stats_queried"),
        ("AG-T08", "Teacher", "teacher", "Chào AI Agent, bạn có thể giúp gì cho tôi?", None),

        # --- CLASSROOM ENROLLED STUDENT AGENT TEST CASES ---
        ("AG-S01", "Classroom Student", "student", "Kiểm tra danh sách bài tập lớp học sắp hết hạn", "homework_checked"),
        ("AG-S02", "Classroom Student", "student", "Bài tập nào chưa nộp?", "homework_checked"),
        ("AG-S03", "Classroom Student", "student", "Hạn nộp bài tập là bao giờ?", "homework_checked"),
        ("AG-S04", "Classroom Student", "student", "Kiểm tra bài tập lớp học", "homework_checked"),
        ("AG-S05", "Classroom Student", "student", "Danh sách bài tập nộp", "homework_checked"),
        ("AG-S06", "Classroom Student", "student", "Chào bạn, mình cần giúp đỡ làm bài tập lớp", None),

        # --- INDEPENDENT / FREEMIUM LEARNER AGENT TEST CASES ---
        ("AG-I01", "Independent Learner", "student", "Tự động tạo bài tập luyện các từ mình hay đọc sai", "remedial_generated"),
        ("AG-I02", "Independent Learner", "student", "Luyện từ đọc sai", "remedial_generated"),
        ("AG-I03", "Independent Learner", "student", "Tạo bài tập tự luyện từ yếu", "remedial_generated"),
        ("AG-I04", "Independent Learner", "student", "Đóng vai đối thoại giao tiếp tiếng Anh với mình", None),
        ("AG-I05", "Independent Learner", "student", "Giải thích cách đọc từ biodiversity", None),
        ("AG-I06", "Independent Learner", "student", "Mẹo luyện phát âm âm th là gì?", None),
    ]

    results = []

    for tc_id, role_label, role, message, expected_action in test_cases:
        try:
            res = client.post("/api/agent/chat", json={
                "user_id": 1,
                "role": role,
                "message": message
            })
            if res.status_code == 200:
                data = res.json()
                action = data.get("action")
                reply = data.get("reply", "")
                
                # Verify HTTP 200 and reply text returned
                passed = isinstance(reply, str) and len(reply) > 0
                if expected_action is not None:
                    passed = passed and (action == expected_action)

                results.append((tc_id, role_label, message, action or "chat_reply", passed, reply[:60] + "..."))
            else:
                results.append((tc_id, role_label, message, "error", False, f"HTTP {res.status_code}"))
        except Exception as e:
            results.append((tc_id, role_label, message, "error", False, str(e)))
        time.sleep(1.0)

    # PRINT EXTENSIVE AGENT TEST REPORT
    print("\n-------------------------------------------------------------------------------------------------------------------")
    print(f"{'ID':<7} | {'ROLE':<20} | {'ACTION':<22} | {'RESULT':<6}")
    print("-------------------------------------------------------------------------------------------------------------------")
    all_passed = True
    for t_id, r_label, msg, act, status, snippet in results:
        res_str = "[PASS]" if status else "[FAIL]"
        if not status:
            all_passed = False
        print(f"{t_id:<7} | {r_label:<20} | {act:<22} | {res_str:<6}")

    print("==========================================================================")
    if all_passed:
        print(f" SUCCESS: ALL {len(results)} GROQ AI AGENT TEST CASES PASSED 100%! ")
    else:
        print(" SOME AI AGENT TEST CASES FAILED! ")
    print("==========================================================================")
    return all_passed

if __name__ == "__main__":
    success = run_ai_agent_test_suite()
    sys.exit(0 if success else 1)
