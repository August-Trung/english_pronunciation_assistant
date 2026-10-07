import os
import sys
import json
import time
import requests

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BACKEND_URL = "https://agrse-fluent-english-backend.hf.space"
FRONTEND_URL = "https://myhanh.augusttrung.com"

def log_test(test_id, name, status, details=""):
    icon = "[PASS]" if status else "[FAIL]"
    print(f"{icon} {test_id}: {name}")
    if details:
        print(f"       -> {details}")

def test_backend_health():
    try:
        start = time.time()
        res = requests.get(f"{BACKEND_URL}/api/health", timeout=15)
        elapsed = round((time.time() - start) * 1000, 1)
        if res.status_code == 200:
            data = res.json()
            log_test("TC-HLT-01", "Backend Health & Status", True, f"HTTP {res.status_code} in {elapsed}ms | Status: {data.get('status', 'ok')}")
            return True
        else:
            log_test("TC-HLT-01", "Backend Health & Status", False, f"HTTP {res.status_code}")
            return False
    except Exception as e:
        log_test("TC-HLT-01", "Backend Health & Status", False, str(e))
        return False

def test_leaderboard():
    try:
        start = time.time()
        res = requests.get(f"{BACKEND_URL}/api/leaderboard", timeout=15)
        elapsed = round((time.time() - start) * 1000, 1)
        if res.status_code == 200:
            data = res.json()
            users = data if isinstance(data, list) else data.get("leaderboard", data.get("users", []))
            count = len(users)
            details = f"Retrieved {count} ranked students in {elapsed}ms."
            if count > 0:
                top1 = users[0]
                name = top1.get('name', 'N/A')
                score = top1.get('best_score') or top1.get('avg_score') or top1.get('score', 0)
                details += f" Top 1: '{name}' with score {score}."
            log_test("TC-LDB-01", "Leaderboard Podium & Rankings Data", True, details)
            return True
        else:
            log_test("TC-LDB-01", "Leaderboard Podium & Rankings Data", False, f"HTTP {res.status_code}")
            return False
    except Exception as e:
        log_test("TC-LDB-01", "Leaderboard Podium & Rankings Data", False, str(e))
        return False

def test_shadowing_ai_sentence():
    levels = ["easy", "medium", "hard"]
    all_passed = True
    for lvl in levels:
        try:
            start = time.time()
            res = requests.get(f"{BACKEND_URL}/api/generate-sentence?level={lvl}", timeout=25)
            elapsed = round((time.time() - start) * 1000, 1)
            if res.status_code == 200:
                data = res.json()
                text = data.get("text", "")
                ipa = data.get("ipa", "")
                meaning = data.get("meaning", "")
                log_test(f"TC-SHD-02-{lvl.upper()}", f"AI Sentence Generation ({lvl.title()})", True, f"'{text}' (IPA: /{ipa}/, Nghĩa: '{meaning}') [{elapsed}ms]")
            else:
                log_test(f"TC-SHD-02-{lvl.upper()}", f"AI Sentence Generation ({lvl.title()})", False, f"HTTP {res.status_code}")
                all_passed = False
        except Exception as e:
            log_test(f"TC-SHD-02-{lvl.upper()}", f"AI Sentence Generation ({lvl.title()})", False, str(e))
            all_passed = False
    return all_passed

def test_frontend_routing_and_assets():
    try:
        res = requests.get(FRONTEND_URL, timeout=10)
        has_index = res.status_code == 200 and "fluent" in res.text.lower()
        log_test("TC-INT-01", "Frontend Deployment & Single Page App", has_index, f"HTTP {res.status_code} | Host: {FRONTEND_URL}")
        return has_index
    except Exception as e:
        log_test("TC-INT-01", "Frontend Deployment", False, str(e))
        return False

def generate_wav_file(filename="scratch/test_voice.wav"):
    import wave
    import math
    import struct
    # Generate 2 seconds of a simulated audio tone
    sample_rate = 16000
    duration = 2.0
    num_samples = int(sample_rate * duration)
    with wave.open(filename, "w") as wav_file:
        wav_file.setnchannels(1) # mono
        wav_file.setsampwidth(2) # 16-bit
        wav_file.setframerate(sample_rate)
        for i in range(num_samples):
            # 440Hz sine wave
            sample = int(32767.0 * 0.3 * math.sin(2.0 * math.pi * 440.0 * i / sample_rate))
            wav_file.writeframes(struct.pack("<h", sample))
    return os.path.abspath(filename)

def test_speaking_analyze_endpoint():
    wav_path = generate_wav_file()
    try:
        start = time.time()
        with open(wav_path, "rb") as f:
            files = {"audio": ("test_voice.wav", f, "audio/wav")}
            data = {
                "topic": "Technology helps us learn faster",
                "mode": "reading",
                "target_text": "Technology helps us learn faster",
                "user_id": "1"
            }
            res = requests.post(f"{BACKEND_URL}/api/analyze", files=files, data=data, timeout=30)
        elapsed = round((time.time() - start) * 1000, 1)
        if res.status_code == 200:
            result = res.json()
            score = result.get("score") or result.get("overall_score") or result.get("similarity_score", "N/A")
            log_test("TC-SPK-02", "Speaking /api/analyze Evaluation Pipeline", True, f"HTTP {res.status_code} in {elapsed}ms | Whisper Pipeline Output: Score: {score}")
            return True
        else:
            log_test("TC-SPK-02", "Speaking /api/analyze Evaluation Pipeline", False, f"HTTP {res.status_code} | {res.text[:200]}")
            return False
    except Exception as e:
        log_test("TC-SPK-02", "Speaking /api/analyze Evaluation Pipeline", False, str(e))
        return False

def main():
    print("=====================================================================")
    print("RUNNING LIVE COMPREHENSIVE TESTS FOR FLUENT / MYHANH PROJECT")
    print(f"Backend Target : {BACKEND_URL}")
    print(f"Frontend Target: {FRONTEND_URL}")
    print("=====================================================================\n")

    t1 = test_backend_health()
    t2 = test_frontend_routing_and_assets()
    t3 = test_leaderboard()
    t4 = test_shadowing_ai_sentence()
    t5 = test_speaking_analyze_endpoint()

    print("\n=====================================================================")
    all_ok = all([t1, t2, t3, t4, t5])
    if all_ok:
        print("[SUCCESS] ALL CORE SERVICES & TESTCASES PASSED PERFECTLY!")
    else:
        print("[WARNING] SOME TESTS ENCOUNTERED NOTICES - CHECK LOGS ABOVE")
    print("=====================================================================")

if __name__ == "__main__":
    main()
