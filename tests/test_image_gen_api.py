import os
import sys
import pytest
from fastapi.testclient import TestClient

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.main import app

client = TestClient(app)

def test_generate_image_endpoint():
    resp = client.post("/api/ai/generate-image", json={
        "word": "serendipity",
        "context": "finding valuable things unexpectedly"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "image_url" in data
    assert data["image_url"].startswith("/uploads/") or data["image_url"].startswith("http") or data["image_url"].startswith("data:image/") or data["image_url"].endswith(".png")

    # Verify static file is retrievable if local path
    if data["image_url"].startswith("/uploads/"):
        file_resp = client.get(data["image_url"])
        assert file_resp.status_code == 200
        assert "image" in file_resp.headers.get("content-type", "")

def test_generate_image_empty_word():
    resp = client.post("/api/ai/generate-image", json={"word": "   "})
    assert resp.status_code == 400
