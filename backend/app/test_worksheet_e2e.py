import os
import sys
import json
import sqlite3

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import (
    generate_ai_worksheet,
    grade_worksheet_submission,
    DB_PATH
)

def run_end_to_end_test():
    print("=== Step 1: Testing Worksheet AI Generation ===")
    vocab = ["giraffe", "monkey", "elephant"]
    types = ["listen_and_circle", "read_and_fill_in_the_blank", "unscramble_words"]
    gen_result = generate_ai_worksheet(
        target_vocabulary=vocab,
        exercise_types=types,
        grade_level="Grade 4",
        accent="en-GB",
        custom_title="Wild Safari Vocabulary"
    )
    assert gen_result["success"] is True
    exercises = gen_result["exercises"]
    assert len(exercises) >= 3
    print(f"Generated {len(exercises)} exercises. Title: {gen_result['title']}")

    # Verify British English en-GB is used
    for ex in exercises:
        if "audio_text" in ex or ex.get("type", "").startswith("listen_"):
            assert ex.get("accent") == "en-GB", f"Expected en-GB accent, got {ex.get('accent')}"
            print(f"Verified British English accent for {ex['type']}: '{ex.get('audio_text')}'")

    print("\n=== Step 2: Testing Database Insertion (Simulating Teacher Assigning Homework) ===")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Find or create a test classroom
    cursor.execute("SELECT id, teacher_id FROM classrooms WHERE COALESCE(IsXoa, 0) = 0 LIMIT 1")
    cls_row = cursor.fetchone()
    if cls_row:
        class_id, teacher_id = cls_row
    else:
        cursor.execute("INSERT INTO classrooms (name, grade_level, teacher_id, join_code) VALUES ('Class 3A', 'Grade 3', 1, 'TEST-3A')")
        class_id = cursor.lastrowid
        teacher_id = 1

    # Insert assignment
    content_json_str = json.dumps(exercises)
    cursor.execute("""
        INSERT INTO assignments 
        (class_id, teacher_id, title, topic_sentence, target_ipa, due_date, status, assignment_type, image_url, guiding_questions, target_keywords, time_limit_seconds, content_json)
        VALUES (?, ?, 'Unit 4 Safari Animals Quiz', 'giraffe, monkey, elephant', '', '2026-12-31', 'active', 'worksheet', '', '[]', '[]', 0, ?)
    """, (class_id, teacher_id, content_json_str))
    asg_id = cursor.lastrowid
    conn.commit()
    print(f"Created worksheet assignment ID {asg_id} for class {class_id}")

    print("\n=== Step 3: Simulating Student Answering and Auto-Grading ===")
    # Construct student answers (answer 2 correctly, 1 incorrectly)
    submitted_answers = {}
    for idx, ex in enumerate(exercises):
        ex_id = ex["id"]
        if idx == 0:
            # Correct
            submitted_answers[ex_id] = ex["correct_answer"]
        elif idx == 1:
            # Correct
            submitted_answers[ex_id] = ex["correct_answer"]
        else:
            # Incorrect
            submitted_answers[ex_id] = "completely_wrong_answer"

    grading = grade_worksheet_submission(exercises, submitted_answers)
    assert grading["total_points"] >= 3
    assert grading["earned_points"] >= 2
    assert 5.0 <= grading["score"] <= 10.0
    print(f"Auto-Grading Result: Score {grading['score']}/10 ({grading['earned_points']}/{grading['total_points']} pts)")
    print(f"Question Details count: {len(grading['details'])}")

    print("\n=== Step 4: Simulating Submission Record Storage ===")
    # Student ID (use 1 or 2)
    student_id = 1
    transcribed_text = f"Worksheet completed: {grading['earned_points']}/{grading['total_points']} questions correct"
    answers_json_str = json.dumps(grading)
    eval_json_str = json.dumps({
        "version": 1,
        "score": grading["score"],
        "transcribed_text": transcribed_text,
        "worksheet_result": grading,
        "score_method": "worksheet_auto_grade"
    })

    cursor.execute("""
        INSERT INTO submissions
        (assignment_id, student_id, student_name, audio_url, audio_size_bytes, transcribed_text, score, ipa_json, answers_json)
        VALUES (?, ?, 'Test Student', '', 0, ?, ?, ?, ?)
    """, (asg_id, student_id, transcribed_text, grading["score"], eval_json_str, answers_json_str))
    sub_id = cursor.lastrowid
    conn.commit()
    print(f"Recorded submission ID {sub_id} with score {grading['score']}")

    print("\n=== Step 5: Querying Gradebook Record ===")
    cursor.execute("""
        SELECT a.id, a.assignment_type, a.content_json, s.score, s.answers_json
        FROM assignments a
        JOIN submissions s ON s.assignment_id = a.id
        WHERE a.id = ? AND s.id = ?
    """, (asg_id, sub_id))
    row = cursor.fetchone()
    assert row is not None
    assert row[1] == "worksheet"
    parsed_content = json.loads(row[2])
    assert len(parsed_content) == len(exercises)
    parsed_answers = json.loads(row[4])
    assert parsed_answers["score"] == grading["score"]
    print("Gradebook query confirmed 100% matched!")

    # Cleanup test assignment and submission
    cursor.execute("DELETE FROM submissions WHERE id = ?", (sub_id,))
    cursor.execute("DELETE FROM assignments WHERE id = ?", (asg_id,))
    conn.commit()
    conn.close()
    print("\n Cleaned up test data. E2E verification test completed successfully!")

if __name__ == "__main__":
    run_end_to_end_test()
