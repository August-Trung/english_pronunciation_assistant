import sys
import os
import sqlite3

# Ensure backend/app is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "app")))

from fastapi.testclient import TestClient
from main import app, DB_PATH

client = TestClient(app)

def run_roleplay_user_experience_tests():
    print("==========================================================================")
    print("  HUMAN ROLEPLAY SCENARIOS AUTOMATED TEST SUITE (TEACHER, STUDENT, FREEMIUM) ")
    print("==========================================================================")

    # Seed data in DB
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO weak_words (user_id, word, ipa, meaning, error_count) VALUES (1, 'environment', '/ɪnˈvaɪ.rən.mənt/', 'Môi trường', 5)")
    cur.execute("INSERT OR REPLACE INTO weak_words (user_id, word, ipa, meaning, error_count) VALUES (1, 'protect', '/prəˈtekt/', 'Bảo vệ', 3)")
    conn.commit()
    conn.close()

    scenarios = [
        # SCENARIO 1: CÔ HƯƠNG (GIẢNG VIÊN TIẾNG ANH)
        (
            "RP-T01",
            "Co Huong (Teacher)",
            "teacher",
            "Em ơi, tạo giúp cô bài tập đọc phát âm 3 câu về chủ đề Môi trường cho lớp 10A1, hạn nộp thứ 6 tuần sau nhé!",
            "assignment_created"
        ),
        (
            "RP-T02",
            "Co Huong (Teacher)",
            "teacher",
            "Xem giúp cô lớp 10A1 bạn nào điểm phát âm còn thấp để cô nhắc nhở.",
            "stats_queried"
        ),
        (
            "RP-T03",
            "Co Huong (Teacher)",
            "teacher",
            "Cho cô xem bảng điểm chung của cả lớp với.",
            "stats_queried"
        ),

        # SCENARIO 2: BẠN MINH (HỌC SINH LỚP 10A1)
        (
            "RP-S01",
            "Ban Minh (Class Student)",
            "student",
            "Cho mình hỏi cô Hương mới giao bài tập gì vậy AI?",
            "homework_checked"
        ),
        (
            "RP-S02",
            "Ban Minh (Class Student)",
            "student",
            "Bài tập nào sắp hết hạn vậy bạn?",
            "homework_checked"
        ),
        (
            "RP-S03",
            "Ban Minh (Class Student)",
            "student",
            "Tuần này mình hay phát âm sai những từ nào vậy?",
            "remedial_generated"
        ),

        # SCENARIO 3: BẠN LINH (HỌC SINH TỰ HỌC / KHÁCH)
        (
            "RP-I01",
            "Ban Linh (Freemium Learner)",
            "student",
            "Tự tạo cho mình một bài tập tự luyện từ các từ mình hay đọc sai nhé!",
            "remedial_generated"
        ),
        (
            "RP-I02",
            "Ban Linh (Freemium Learner)",
            "student",
            "Bây giờ bạn đóng vai lễ tân khách sạn, mình là khách thuê phòng, trò chuyện bằng tiếng Anh với mình nha!",
            None
        ),
        (
            "RP-I03",
            "Ban Linh (Freemium Learner)",
            "student",
            "Giải thích giúp mình cách đọc âm th /θ/ sao cho đúng với!",
            None
        )
    ]

    results = []

    for sc_id, actor, role, user_prompt, expected_action in scenarios:
        try:
            res = client.post("/api/agent/chat", json={
                "user_id": 1,
                "role": role,
                "message": user_prompt
            })
            if res.status_code == 200:
                data = res.json()
                action = data.get("action")
                reply = data.get("reply", "")

                passed = isinstance(reply, str) and len(reply) > 0
                if expected_action is not None:
                    passed = passed and (action == expected_action)

                # Format human readable summary
                snippet = reply.replace("\n", " ")[:70] + "..."
                results.append((sc_id, actor, action or "conversational_reply", passed, snippet))
            else:
                results.append((sc_id, actor, "error", False, f"HTTP Error {res.status_code}"))
        except Exception as e:
            results.append((sc_id, actor, "error", False, str(e)))

    # PRINT HUMAN SCENARIOS REPORT
    print("\n-------------------------------------------------------------------------------------------------------------------")
    print(f"{'ID':<7} | {'ACTOR':<26} | {'EXECUTED ACTION':<24} | {'RESULT':<6}")
    print("-------------------------------------------------------------------------------------------------------------------")
    all_passed = True
    for s_id, act_name, act_executed, status, snip in results:
        res_str = "[PASS]" if status else "[FAIL]"
        if not status:
            all_passed = False
        print(f"{s_id:<7} | {act_name:<26} | {act_executed:<24} | {res_str:<6}")

    print("==========================================================================")
    if all_passed:
        print(f" SUCCESS: ALL {len(results)} HUMAN ROLEPLAY SCENARIOS PASSED 100%! ")
    else:
        print(" SOME ROLEPLAY SCENARIOS FAILED! ")
    print("==========================================================================")
    return all_passed

if __name__ == "__main__":
    success = run_roleplay_user_experience_tests()
    sys.exit(0 if success else 1)
