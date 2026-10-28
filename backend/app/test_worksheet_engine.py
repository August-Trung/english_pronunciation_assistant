import os
import sys
import json
import pytest

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import grading engine function
from main import grade_worksheet_submission

def test_grade_multiple_choice_and_circle():
    exercises = [
        {
            "id": "ex1",
            "type": "listen_and_circle",
            "options": ["cat", "dog", "elephant"],
            "correct_answer": "dog",
            "points": 1
        },
        {
            "id": "ex2",
            "type": "read_and_circle",
            "options": ["red", "blue", "green"],
            "correct_answer": "blue",
            "points": 1
        }
    ]
    # 1 correct, 1 wrong
    submitted = {
        "ex1": "dog",
        "ex2": "red"
    }
    result = grade_worksheet_submission(exercises, submitted)
    assert result["total_points"] == 2
    assert result["earned_points"] == 1
    assert result["score"] == 5.0
    assert result["details"][0]["is_correct"] is True
    assert result["details"][1]["is_correct"] is False

def test_grade_fill_in_the_blank_and_spelling():
    exercises = [
        {
            "id": "ex3",
            "type": "read_and_fill_in_the_blank",
            "correct_answer": "banana",
            "points": 1
        },
        {
            "id": "ex4",
            "type": "write_the_missing_word",
            "correct_answer": "giraffe",
            "points": 1
        }
    ]
    # Case-insensitive and trimmed spaces
    submitted = {
        "ex3": "  Banana ",
        "ex4": "GIRAFFE"
    }
    result = grade_worksheet_submission(exercises, submitted)
    assert result["earned_points"] == 2
    assert result["score"] == 10.0
    assert result["details"][0]["is_correct"] is True
    assert result["details"][1]["is_correct"] is True

def test_grade_tick_or_cross():
    exercises = [
        {
            "id": "ex5",
            "type": "listen_and_tick_or_cross",
            "correct_answer": "tick", # or True
            "points": 1
        },
        {
            "id": "ex6",
            "type": "listen_and_tick_or_cross",
            "correct_answer": "cross",
            "points": 1
        }
    ]
    submitted = {
        "ex5": "tick",
        "ex6": "cross"
    }
    result = grade_worksheet_submission(exercises, submitted)
    assert result["score"] == 10.0
    assert result["details"][0]["is_correct"] is True

def test_grade_unscramble_words():
    exercises = [
        {
            "id": "ex7",
            "type": "unscramble_words",
            "correct_answer": "This is a big elephant.",
            "points": 1
        }
    ]
    # Accept string or list of tokens
    submitted_str = {"ex7": "This is a big elephant."}
    res_str = grade_worksheet_submission(exercises, submitted_str)
    assert res_str["score"] == 10.0

    submitted_list = {"ex7": ["This", "is", "a", "big", "elephant."]}
    res_list = grade_worksheet_submission(exercises, submitted_list)
    assert res_list["score"] == 10.0

def test_grade_matching():
    exercises = [
        {
            "id": "ex8",
            "type": "read_and_match",
            "correct_answer": {
                "cat": "meow",
                "dog": "bark"
            },
            "points": 2
        }
    ]
    submitted = {
        "ex8": {
            "cat": "meow",
            "dog": "bark"
        }
    }
    result = grade_worksheet_submission(exercises, submitted)
    assert result["earned_points"] == 2
    assert result["score"] == 10.0

def test_grade_numbering():
    exercises = [
        {
            "id": "ex9",
            "type": "listen_and_number",
            "correct_answer": ["apple", "banana", "orange", "grape"],
            "points": 1
        }
    ]
    submitted = {
        "ex9": ["apple", "banana", "orange", "grape"]
    }
    result = grade_worksheet_submission(exercises, submitted)
    assert result["score"] == 10.0

if __name__ == "__main__":
    test_grade_multiple_choice_and_circle()
    test_grade_fill_in_the_blank_and_spelling()
    test_grade_tick_or_cross()
    test_grade_unscramble_words()
    test_grade_matching()
    test_grade_numbering()
    print("All worksheet grading tests passed!")
