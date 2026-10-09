import os
import sys
import pytest
from fastapi.testclient import TestClient

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.main import app

client = TestClient(app)

def test_flashcard_deck_crud():
    # 1. Create a flashcard deck
    deck_payload = {
        "user_id": 1,
        "title": "IELTS Academic Environment",
        "topic": "Environment",
        "difficulty": "intermediate",
        "cards": [
            {
                "word": "biodiversity",
                "ipa": "ˌbaɪ.oʊ.daɪˈvɜːr.sə.ti",
                "meaning": "đa dạng sinh học",
                "example": "Preserving biodiversity is crucial for ecosystem health.",
                "pronunciation_tip": "Nhấn trọng âm vào âm tiết thứ 4 /vɜːr/.",
                "image_url": ""
            },
            {
                "word": "deforestation",
                "ipa": "diːˌfɔːr.əˈsteɪ.ʃən",
                "meaning": "sự phá rừng",
                "example": "Deforestation threatens local wildlife species.",
                "pronunciation_tip": "Nhấn trọng âm chính vào /steɪ/.",
                "image_url": ""
            }
        ]
    }
    create_resp = client.post("/api/flashcards/decks", json=deck_payload)
    assert create_resp.status_code == 200
    create_data = create_resp.json()
    assert create_data["status"] == "success"
    deck_id = create_data["deck_id"]
    assert deck_id > 0

    # 2. Get list of decks
    list_resp = client.get(f"/api/flashcards/decks?user_id=1")
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert any(d["id"] == deck_id for d in list_data["decks"])

    # 3. Get single deck with cards
    detail_resp = client.get(f"/api/flashcards/decks/{deck_id}")
    assert detail_resp.status_code == 200
    detail_data = detail_resp.json()
    assert detail_data["deck"]["id"] == deck_id
    assert len(detail_data["cards"]) == 2
    assert detail_data["cards"][0]["word"] == "biodiversity"

    # 4. Delete deck
    del_resp = client.delete(f"/api/flashcards/decks/{deck_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["status"] == "success"

    # 5. Verify deleted deck is no longer returned
    list_after_resp = client.get(f"/api/flashcards/decks?user_id=1")
    decks_after = list_after_resp.json()["decks"]
    assert not any(d["id"] == deck_id for d in decks_after)
