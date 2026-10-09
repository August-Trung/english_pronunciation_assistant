import sys
import os
import json
sys.path.insert(0, os.path.abspath("."))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from backend.app.hf_service import (
    generate_picture_scenario,
    evaluate_picture_speaking
)

def test_multimodal_scenario_generation():
    print("=== TEST 1: AI Image Generation Mode with Custom Prompt ===")
    prompt = "A family having a picnic in the park with a golden retriever"
    sc_ai = generate_picture_scenario(topic=prompt, level="intermediate", mode="ai_gen")
    
    print("Title:", sc_ai.get("title"))
    print("Image URL:", sc_ai.get("image_url"))
    print("Fallback Image URL:", sc_ai.get("fallback_image_url"))
    print("Guiding questions:", sc_ai.get("guiding_questions"))
    print("Keywords:", sc_ai.get("keywords"))
    print("Sample response:", sc_ai.get("sample_response"))
    
    assert "pollinations.ai" in sc_ai.get("image_url", "")
    assert len(sc_ai.get("guiding_questions", [])) == 4
    assert len(sc_ai.get("keywords", [])) >= 5
    assert len(sc_ai.get("sample_response", "")) > 20
    print("-> PASS: Mode ai_gen works properly!\n")

    print("=== TEST 2: Real Photography Search Mode ===")
    sc_search = generate_picture_scenario(topic="Airport Terminal", level="intermediate", mode="search")
    print("Title:", sc_search.get("title"))
    print("Image URL:", sc_search.get("image_url"))
    print("Guiding questions:", sc_search.get("guiding_questions"))
    assert "http" in sc_search.get("image_url", "")
    assert len(sc_search.get("guiding_questions", [])) >= 3
    print("-> PASS: Mode search works properly!\n")

    print("=== TEST 3: Custom Upload Mode ===")
    upload_url = "/uploads/picture_practice/sample_exam_pic.jpg"
    sc_upload = generate_picture_scenario(topic="Medical consultation with patient", level="intermediate", mode="upload", custom_image_url=upload_url)
    print("Title:", sc_upload.get("title"))
    print("Image URL:", sc_upload.get("image_url"))
    print("Keywords:", sc_upload.get("keywords"))
    assert sc_upload.get("image_url") == upload_url
    assert len(sc_upload.get("guiding_questions", [])) >= 3
    print("-> PASS: Mode upload works properly!\n")

    print("=== TEST 4: Speech Evaluation Pipeline ===")
    transcription = "In this picture, I can see a happy family having a picnic on the green grass. Next to them is a golden retriever dog resting on the checkered blanket."
    eval_res = evaluate_picture_speaking(
        transcription=transcription,
        topic=prompt,
        keywords=sc_ai.get("keywords", []),
        guiding_questions=sc_ai.get("guiding_questions", [])
    )
    print("Evaluation Score:", eval_res.get("score"))
    print("Matched keywords:", eval_res.get("matched_keywords"))
    print("AI Feedback:", eval_res.get("feedback"))
    assert eval_res.get("score") > 0
    print("-> PASS: Speech evaluation works properly!\n")

    print("==================================================")
    print(" ALL 4 BACKEND MULTIMODAL TESTCASES PASSED 100%! ")
    print("==================================================")

if __name__ == "__main__":
    test_multimodal_scenario_generation()
