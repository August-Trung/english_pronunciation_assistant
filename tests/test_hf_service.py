import os
import pytest
import sys

# Ensure backend directory is in path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.hf_service import parse_flashcards_json, parse_json_safely

def test_parse_flashcards_json_clean():
    raw_response = '''
    [
        {
            "word": "resilient",
            "ipa": "rɪˈzɪl.jənt",
            "meaning": "kiên cường, có khả năng phục hồi nhanh",
            "example": "He is resilient in facing academic challenges.",
            "pronunciation_tip": "Nhấn trọng âm vào âm tiết thứ 2 /zɪl/."
        }
    ]
    '''
    cards = parse_flashcards_json(raw_response)
    assert len(cards) == 1
    assert cards[0]["word"] == "resilient"
    assert "ipa" in cards[0]
    assert "meaning" in cards[0]
    assert cards[0]["meaning"] == "kiên cường, có khả năng phục hồi nhanh"

def test_parse_flashcards_json_markdown_wrapped():
    raw_response = '''```json
    [
        {
            "word": "eloquent",
            "ipa": "ˈel.ə.kwənt",
            "meaning": "lưu loát, hùng biện",
            "example": "An eloquent speaker captured everyone's attention.",
            "pronunciation_tip": "Âm /el/ nhấn mạnh ở đầu từ."
        }
    ]
    ```'''
    cards = parse_flashcards_json(raw_response)
    assert len(cards) == 1
    assert cards[0]["word"] == "eloquent"

def test_parse_flashcards_json_object_wrapped():
    raw_response = '''
    {
        "cards": [
            {
                "word": "lucid",
                "ipa": "ˈluː.sɪd",
                "meaning": "rõ ràng, minh bạch",
                "example": "A lucid explanation of the problem.",
                "pronunciation_tip": "Âm /uː/ dài và tròn môi."
            }
        ]
    }
    '''
    cards = parse_flashcards_json(raw_response)
    assert len(cards) == 1
    assert cards[0]["word"] == "lucid"
