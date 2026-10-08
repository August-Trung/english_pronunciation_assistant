# Hugging Face Multimodal Learning (AI Flashcards, Visual Image Generation & Picture Description) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Mở rộng hệ thống FLUENT với 3 tính năng đa giác quan (multimodal) sử dụng Hugging Face: Bộ Flashcard học từ vựng tạo bằng LLM, Tạo ảnh AI minh họa trực quan cho từ vựng (Text-to-Image), và Phòng luyện nói "Describe the Picture" chuẩn format IELTS/TOEIC chấm điểm bằng Whisper + LLM.

**Architecture:** 
- **Backend (FastAPI on Hugging Face Spaces):** Tích hợp `huggingface_hub` `InferenceClient` để gọi Serverless Inference API cho LLM (`Qwen/Qwen2.5-72B-Instruct` hoặc `meta-llama/Llama-3.3-70B-Instruct`) và Text-to-Image (`black-forest-labs/FLUX.1-schnell` hoặc `ByteDance/SDXL-Lightning`). Hỗ trợ fallback sang Groq API cho LLM khi cần thiết. Quản lý thư mục static cache ảnh (`/uploads/flashcard_images`). Lưu dữ liệu cấu trúc vào SQLite (`flashcard_decks`, `flashcard_cards`, `picture_scenarios`).
- **Frontend (Vue 3 + Vuetify on 123host):** Nâng cấp `FlashcardsView.vue` với giao diện 2 tab (Weak Words & AI Vocabulary Decks), hiệu ứng lật thẻ 3D, hiển thị ảnh AI minh họa, phát âm mẫu native và ghi âm chấm điểm trực tiếp. Tạo view/component mới `PicturePracticeView.vue` hỗ trợ kịch bản luyện miêu tả tranh có đồng hồ đếm ngược, ghi âm câu trả lời và báo cáo phân tích phát âm + ngữ pháp đa chiều.

**Tech Stack:**
- Python 3.10+, FastAPI, SQLite (WAL mode), `huggingface_hub`, `Pillow`, `requests`, `openai-whisper`
- Vue 3, Vite, Vuetify 3, Material Design Icons (`@mdi/font`), Web Audio API / MediaRecorder

**Spec Document:** Design specification outlined below.

## Global Constraints
- **Language Policy - UI:** 100% Academic English cho toàn bộ buttons, headers, chips, navigation, badges, tabs.
- **Language Policy - AI Feedback/Tutor:** Tiếng Việt có dấu chuẩn UTF-8 thân thiện, dễ hiểu cho phần giải nghĩa, mẹo phát âm, và nhận xét bài nói.
- **Confirmation Modals:** Bắt buộc có hộp thoại xác nhận khi xóa bộ thẻ (Delete Deck) hoặc xóa thẻ (Delete Card).
- **Code Quality:** Không dùng anti-patterns (không check `length` trước khi lặp, ưu tiên optional chaining `?.`, dùng `??` cho fallback, không kiểm tra `typeof window !== 'undefined'`).
- **Resilience:** Xử lý fallback gracefully nếu `HF_TOKEN` chưa được cấu hình hoặc gặp rate limit (fallback sang Groq LLM và ảnh placeholder SVG có sẵn).

---

### Task 1: Hugging Face Service Module & Environment Configuration

**Files:**
- Create: `backend/app/hf_service.py`
- Modify: `backend/requirements.txt`
- Test: `tests/test_hf_service.py`

**Interfaces:**
- Produces:
  - `generate_deck_content(topic: str, level: str, count: int) -> List[Dict[str, str]]`
  - `generate_vocabulary_image(word: str, context: str) -> Optional[str]`
  - `generate_picture_prompt(topic: str) -> Dict[str, Any]`

- [ ] **Step 1: Write test for HF service in `tests/test_hf_service.py`**

```python
import os
import pytest
from unittest.mock import patch, MagicMock

def test_generate_deck_content_structure():
    from backend.app.hf_service import parse_flashcards_json
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
```

- [ ] **Step 2: Run test to verify failure**

Run: `pytest tests/test_hf_service.py -v`
Expected: FAIL with ModuleNotFoundError or import error.

- [ ] **Step 3: Update `backend/requirements.txt` and implement `backend/app/hf_service.py`**

Thêm `huggingface_hub` và `Pillow` vào `backend/requirements.txt`.
Tạo `backend/app/hf_service.py` chứa:
- Khởi tạo `InferenceClient(api_key=os.getenv("HF_TOKEN"))`
- Hàm `parse_flashcards_json` xử lý parse an toàn JSON từ LLM (strip markdown codeblocks ````json ... ````).
- Hàm `generate_deck_content` gọi `Qwen/Qwen2.5-72B-Instruct` (hoặc fallback Groq).
- Hàm `generate_vocabulary_image` gọi `black-forest-labs/FLUX.1-schnell` để sinh ảnh, nén JPEG và lưu vào thư mục `backend/app/uploads/flashcard_images`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_hf_service.py -v`
Expected: PASS.

- [ ] **Step 5: Commit changes**

```bash
git add backend/requirements.txt backend/app/hf_service.py tests/test_hf_service.py
git commit -m "feat: add Hugging Face service module with image and LLM helpers"
```

---

### Task 2: Flashcard Decks Database Migration & Backend APIs

**Files:**
- Modify: `backend/app/main.py:1630-1780` (Database schema & endpoints)
- Test: `tests/test_flashcards_api.py`

**Interfaces:**
- Consumes: `generate_deck_content` từ `backend/app/hf_service.py`
- Produces:
  - `POST /api/flashcards/generate` -> `{ status: "success", data: [...] }`
  - `POST /api/flashcards/decks` -> `{ status: "success", deck_id: int }`
  - `GET /api/flashcards/decks` -> `{ status: "success", decks: [...] }`
  - `GET /api/flashcards/decks/{deck_id}` -> `{ status: "success", deck: {...}, cards: [...] }`
  - `DELETE /api/flashcards/decks/{deck_id}` -> `{ status: "success" }`

- [ ] **Step 1: Write failing test for flashcard deck APIs**

```python
import pytest
from fastapi.testclient import TestClient

def test_flashcard_deck_crud():
    from backend.app.main import app
    client = TestClient(app)
    # Test listing decks (should return 200 with list)
    resp = client.get("/api/flashcards/decks?user_id=1")
    assert resp.status_code == 200
    data = resp.json()
    assert "decks" in data
```

- [ ] **Step 2: Run test to verify failure**

Run: `pytest tests/test_flashcards_api.py -v`
Expected: FAIL (404 Not Found vì endpoint chưa được khai báo).

- [ ] **Step 3: Add DB tables and endpoints in `backend/app/main.py`**

1. Khởi tạo bảng SQLite trong hàm init DB:
   - `flashcard_decks`: `id`, `user_id`, `title`, `topic`, `difficulty`, `card_count`, `created_at`, `IsXoa`
   - `flashcard_cards`: `id`, `deck_id`, `word`, `ipa`, `meaning`, `example_sentence`, `pronunciation_tip`, `image_url`, `created_at`, `IsXoa`
2. Tạo các endpoints CRUD và endpoint AI generation:
   - `POST /api/flashcards/generate`: Nhận `topic`, `difficulty`, `count`. Gọi `generate_deck_content`.
   - `POST /api/flashcards/decks`: Lưu toàn bộ deck và danh sách cards vào DB.
   - `GET /api/flashcards/decks`: Lấy danh sách decks của user (`IsXoa = 0`).
   - `GET /api/flashcards/decks/{deck_id}`: Lấy chi tiết deck và các cards thuộc deck.
   - `DELETE /api/flashcards/decks/{deck_id}`: Soft delete deck (`IsXoa = 1`).

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_flashcards_api.py -v`
Expected: PASS.

- [ ] **Step 5: Commit changes**

```bash
git add backend/app/main.py tests/test_flashcards_api.py
git commit -m "feat: add flashcard deck database tables and CRUD endpoints"
```

---

### Task 3: Text-to-Image Generation & Image Serving Endpoint

**Files:**
- Modify: `backend/app/main.py`
- Modify: `backend/app/hf_service.py`
- Test: `tests/test_image_gen_api.py`

**Interfaces:**
- Consumes: `generate_vocabulary_image` từ `hf_service.py`
- Produces:
  - `POST /api/ai/generate-image` -> `{ status: "success", image_url: str, cached: bool }`
  - Static endpoint: `/uploads/flashcard_images/{filename}`

- [ ] **Step 1: Write test for image generation endpoint**

```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

def test_generate_image_endpoint():
    from backend.app.main import app
    client = TestClient(app)
    with patch("backend.app.hf_service.generate_vocabulary_image", return_value="/uploads/flashcard_images/test.jpg"):
        resp = client.post("/api/ai/generate-image", json={"word": "astronomy", "context": "outer space"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert "/uploads/flashcard_images/" in data["image_url"]
```

- [ ] **Step 2: Run test to verify failure**

Run: `pytest tests/test_image_gen_api.py -v`
Expected: FAIL (404 Not Found).

- [ ] **Step 3: Implement endpoint in `backend/app/main.py`**

- Mount static directory: `app.mount("/uploads/flashcard_images", ...)`
- Endpoint `POST /api/ai/generate-image`:
  - Kiểm tra xem ảnh của từ vựng đã tồn tại trong cache chưa (dựa theo slug của từ).
  - Nếu chưa có, gọi `hf_service.generate_vocabulary_image`.
  - Cập nhật URL ảnh vào `flashcard_cards` nếu có truyền kèm `card_id`.
  - Trả về đường dẫn ảnh tương đối (e.g. `/uploads/flashcard_images/word_xxx.jpg`).

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_image_gen_api.py -v`
Expected: PASS.

- [ ] **Step 5: Commit changes**

```bash
git add backend/app/main.py backend/app/hf_service.py tests/test_image_gen_api.py
git commit -m "feat: add image generation endpoint and static serving cache"
```

---

### Task 4: Frontend Flashcards Studio Redesign & Multimodal Card Viewer

**Files:**
- Modify: `frontend/src/views/FlashcardsView.vue`
- Test: Manual browser validation & build verification

**Interfaces:**
- Consumes: `/api/flashcards/generate`, `/api/flashcards/decks`, `/api/ai/generate-image`, `/api/assess_pronunciation`

- [ ] **Step 1: Structure Dual-Tab UI in `FlashcardsView.vue`**

- **Tab 1: "Weak Words Review"** (Giữ nguyên tính năng review các từ phát âm lỗi hiện tại).
- **Tab 2: "AI Vocabulary Decks"**:
  - Thanh công cụ phía trên: Nút **"Generate AI Deck"** mở Dialog tạo bộ thẻ mới.
  - Bộ lọc Deck theo chủ đề hoặc độ khó (Beginner, Intermediate, Advanced).
  - Danh sách Decks hiển thị dưới dạng grid card (số thẻ, ngày tạo, nút Start Study, nút Delete có hộp thoại xác nhận).

- [ ] **Step 2: Implement "Generate AI Deck" Modal**

- Input: Topic (ví dụ: *IELTS Environment, Airport Travel, Job Interview* hoặc gợi ý nhanh dạng chips).
- Level Select: Beginner, Intermediate, Advanced.
- Card count: 5 hoặc 10 thẻ.
- Checkbox tùy chọn: *"Generate AI Visuals with FLUX.1"* (tự động tạo ảnh minh họa song song).
- Hiển thị loading skeleton / tiến trình sinh thẻ thông minh.

- [ ] **Step 3: Implement Multimodal Flashcard Study Studio**

- Mặt trước (Front Side):
  - Khung ảnh AI minh họa sắc nét (tỷ lệ 16:9 hoặc 1:1) kèm hiệu ứng hover zoom.
  - Từ vựng to rõ, phiên âm IPA chuẩn.
  - Nút phát âm Native Audio (Google TTS / Browser SpeechSynthesis).
  - Nút lật thẻ hoặc click trực tiếp vào thẻ để flip.
- Mặt sau (Back Side):
  - Nghĩa tiếng Việt chi tiết (UTF-8).
  - Câu ví dụ tiếng Anh + dịch nghĩa.
  - Mẹo phát âm khẩu hình miệng (Pronunciation Tip).
  - **Nút "Record & Test Pronunciation"**: Học sinh bấm micro nói từ vựng, hệ thống gửi đến endpoint Whisper chấm điểm ngay trên thẻ.
  - Nút "Regenerate AI Visual" nếu muốn AI vẽ lại bức ảnh khác.

- [ ] **Step 4: Verify frontend build**

Run: `cd frontend && npm run build`
Expected: Build thành công không có lỗi cú pháp.

- [ ] **Step 5: Commit changes**

```bash
git add frontend/src/views/FlashcardsView.vue
git commit -m "feat: enhance FlashcardsView with AI deck generator and multimodal cards"
```

---

### Task 5: "Describe the Picture" Speaking Studio Backend

**Files:**
- Modify: `backend/app/main.py`
- Modify: `backend/app/hf_service.py`
- Test: `tests/test_picture_practice_api.py`

**Interfaces:**
- Produces:
  - `POST /api/picture-practice/create-scenario` -> `{ scenario_id, image_url, title, prompt_guide, keywords, suggested_time_seconds }`
  - `POST /api/picture-practice/evaluate` -> `{ score, fluency, pronunciation, grammar_feedback, matched_keywords }`

- [ ] **Step 1: Write test for Picture Practice APIs**

```python
import pytest
from fastapi.testclient import TestClient

def test_picture_practice_scenario_flow():
    from backend.app.main import app
    client = TestClient(app)
    resp = client.post("/api/picture-practice/create-scenario", json={"topic": "Coffee shop scene", "level": "intermediate"})
    assert resp.status_code == 200
    data = resp.json()
    assert "scenario_id" in data
    assert "image_url" in data
    assert "keywords" in data
```

- [ ] **Step 2: Run test to verify failure**

Run: `pytest tests/test_picture_practice_api.py -v`
Expected: FAIL (404 Not Found).

- [ ] **Step 3: Implement DB table and endpoints in `backend/app/main.py` & `backend/app/hf_service.py`**

1. Khởi tạo bảng `picture_scenarios`:
   - `id`, `user_id`, `topic`, `image_url`, `title`, `prompt_guide`, `keywords_json`, `created_at`, `IsXoa`
2. Endpoint `POST /api/picture-practice/create-scenario`:
   - Dùng HF LLM sinh prompt miêu tả bức tranh sinh động kèm 4-5 từ vựng mục tiêu (keywords) và 3 câu hỏi gợi ý (guiding questions).
   - Dùng HF FLUX.1 tạo bức ảnh bối cảnh và lưu vào static folder.
   - Lưu scenario vào DB.
3. Endpoint `POST /api/picture-practice/evaluate`:
   - Nhận audio file + `scenario_id`.
   - Dùng Whisper transcribe bài nói của học sinh.
   - So sánh phiên âm và từ vựng mục tiêu đã xuất hiện.
   - Dùng LLM đánh giá độ trôi chảy (Fluency), độ chính xác ngữ pháp (Grammar), mức độ bao quát bức tranh và đưa ra lời nhận xét tiếng Việt chi tiết kèm câu nói gợi ý cải thiện.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_picture_practice_api.py -v`
Expected: PASS.

- [ ] **Step 5: Commit changes**

```bash
git add backend/app/main.py backend/app/hf_service.py tests/test_picture_practice_api.py
git commit -m "feat: add Describe the Picture speaking evaluation backend"
```

---

### Task 6: "Describe the Picture" Speaking Studio Frontend

**Files:**
- Create: `frontend/src/views/PicturePracticeView.vue`
- Modify: `frontend/src/router/index.js`
- Modify: `frontend/src/App.vue`
- Test: Manual browser testing & build check

**Interfaces:**
- Consumes: `/api/picture-practice/create-scenario`, `/api/picture-practice/evaluate`

- [ ] **Step 1: Create `frontend/src/views/PicturePracticeView.vue`**

Giao diện chia làm 2 cột hiện đại:
- **Cột trái (Visual Canvas):**
  - Khung ảnh tình huống chất lượng cao (fullscreen/zoom preview khi click).
  - Chip chủ đề & Bộ đếm thời gian gợi ý (ví dụ 60s đếm ngược).
  - Guiding Questions (e.g. *Where are they? What are people doing? What is in the background?*).
  - Target Keywords Chip Checklist (tự động tích xanh khi học sinh nói trúng từ).
- **Cột phải (Speaking Recorder & Feedback Card):**
  - Trạng thái chuẩn bị: Nút "Start 60s Speaking Challenge".
  - Trạng thái đang nói: Audio visualizer sóng âm động + Đồng hồ đếm giây + Nút Stop/Submit.
  - Trạng thái chấm điểm: Báo cáo điểm tổng quát (Overall Score / 100, Fluency, Pronunciation, Grammar), bảng so sánh từ vựng mục tiêu, và phân tích ngữ pháp nhận xét tiếng Việt chi tiết từ AI Tutor.

- [ ] **Step 2: Register route in `frontend/src/router/index.js` & navigation link in `frontend/src/App.vue`**

- Thêm route: `{ path: '/picture-practice', name: 'picture-practice', component: () => import('@/views/PicturePracticeView.vue') }`.
- Thêm navigation pill trên top bar của `App.vue`: nút **"Describe Picture"** kèm icon `mdi-image-filter-frames`.

- [ ] **Step 3: Run frontend build check**

Run: `cd frontend && npm run build`
Expected: Build thành công không có lỗi.

- [ ] **Step 4: Commit changes**

```bash
git add frontend/src/views/PicturePracticeView.vue frontend/src/router/index.js frontend/src/App.vue
git commit -m "feat: add Describe the Picture speaking studio frontend view and routing"
```

---

### Task 7: End-to-End Testing & Verification

**Files:**
- Create: `tests/test_e2e_multimodal.py`
- Test: Full integration test suite

- [ ] **Step 1: Write integration tests**

Kiểm tra luồng hoàn chỉnh:
1. Tạo Deck bằng HF LLM -> Lưu thành công vào DB.
2. Sinh ảnh cho từ vựng trong Deck bằng FLUX -> Nhận được đường dẫn ảnh tĩnh hợp lệ.
3. Tạo kịch bản Picture Practice -> Gửi audio giả lập -> Nhận điểm số và nhận xét phản hồi.

- [ ] **Step 2: Run all test suites**

Run: `pytest tests/ -v`
Expected: Tất cả bài test đều PASS.

- [ ] **Step 3: Test frontend build production asset check**

Run: `cd frontend && npm run build`
Expected: `dist/` directory được tạo đầy đủ, sẵn sàng triển khai lên 123host.

- [ ] **Step 4: Commit final verification**

```bash
git add tests/test_e2e_multimodal.py
git commit -m "test: add e2e integration tests for multimodal features"
```
