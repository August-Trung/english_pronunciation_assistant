import os
import sys
import pytest
from fastapi.testclient import TestClient

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.main import app

client = TestClient(app)

def test_full_multimodal_e2e_lifecycle():
    """End-to-end test covering flashcard AI generation, image synthesis, deck storage, and picture practice."""
    
    # 1. AI Flashcards Generation
    gen_resp = client.post("/api/flashcards/generate", json={
        "topic": "Renewable Energy",
        "difficulty": "intermediate",
        "count": 3
    })
    assert gen_resp.status_code == 200
    gen_data = gen_resp.json()
    assert gen_data["status"] == "success"
    cards = gen_data["data"]
    assert len(cards) >= 1
    sample_word = cards[0]["word"]

    # 2. Save Deck to SQLite
    deck_resp = client.post("/api/flashcards/decks", json={
        "user_id": 1,
        "title": "Renewable Energy Set",
        "topic": "Renewable Energy",
        "difficulty": "Intermediate",
        "cards": cards
    })
    assert deck_resp.status_code == 200
    deck_id = deck_resp.json()["deck_id"]

    # 3. Text-to-Image Generation for the first card
    img_resp = client.post("/api/ai/generate-image", json={
        "word": sample_word,
        "context": "clean solar panels and wind turbines"
    })
    assert img_resp.status_code == 200
    img_data = img_resp.json()
    assert img_data["status"] == "success"
    assert "image_url" in img_data

    # 4. Fetch Deck details and verify cards
    detail_resp = client.get(f"/api/flashcards/decks/{deck_id}")
    assert detail_resp.status_code == 200
    deck_detail = detail_resp.json()
    assert deck_detail["deck"]["title"] == "Renewable Energy Set"
    assert len(deck_detail["cards"]) == len(cards)

    # 5. Create Describe the Picture scenario
    scenario_resp = client.post("/api/picture-practice/create-scenario", json={
        "topic": "Renewable Energy Farm",
        "level": "intermediate",
        "user_id": 1
    })
    assert scenario_resp.status_code == 200
    scenario_data = scenario_resp.json()
    scenario_id = scenario_data["scenario_id"]
    assert "image_url" in scenario_data

    # 6. Evaluate candidate speech on scenario
    eval_resp = client.post("/api/picture-practice/evaluate", json={
        "scenario_id": scenario_id,
        "transcription": "In this picture, vast solar panels and modern wind turbines generate clean electricity under a blue sunny sky.",
        "user_id": 1
    })
    assert eval_resp.status_code == 200
    eval_data = eval_resp.json()
    assert eval_data["status"] == "success"
    assert eval_data["score"] > 0
    assert len(eval_data["feedback"]) > 0

    # 7. Clean up (Soft Delete Deck)
    del_resp = client.delete(f"/api/flashcards/decks/{deck_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["status"] == "success"
