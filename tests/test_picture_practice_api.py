import os
import sys
import pytest
from fastapi.testclient import TestClient

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.main import app

client = TestClient(app)

def test_picture_practice_flow():
    # 1. Create a scenario
    create_resp = client.post("/api/picture-practice/create-scenario", json={
        "topic": "Busy Coffee Shop",
        "level": "intermediate",
        "user_id": 1
    })
    assert create_resp.status_code == 200
    scenario = create_resp.json()
    assert scenario["status"] == "success"
    assert "scenario_id" in scenario
    assert "image_url" in scenario
    assert "keywords" in scenario
    assert len(scenario["keywords"]) > 0

    scenario_id = scenario["scenario_id"]

    # 2. List recent scenarios
    list_resp = client.get("/api/picture-practice/scenarios?user_id=1")
    assert list_resp.status_code == 200
    scenarios = list_resp.json()["scenarios"]
    assert any(s["scenario_id"] == scenario_id for s in scenarios)

    # 3. Evaluate candidate's speech response
    eval_resp = client.post("/api/picture-practice/evaluate", json={
        "scenario_id": scenario_id,
        "transcription": "In this picture, I can see a cozy coffee shop with customers sitting at wooden tables and enjoying their drinks in a warm atmosphere.",
        "user_id": 1
    })
    assert eval_resp.status_code == 200
    eval_data = eval_resp.json()
    assert eval_data["status"] == "success"
    assert "score" in eval_data
    assert "feedback" in eval_data
    assert eval_data["score"] > 0
    assert "sample_response" in eval_data

def test_picture_practice_evaluate_empty():
    eval_resp = client.post("/api/picture-practice/evaluate", json={
        "scenario_id": 999999,
        "transcription": "",
        "user_id": 1
    })
    assert eval_resp.status_code == 200
    eval_data = eval_resp.json()
    assert eval_data["score"] == 0
