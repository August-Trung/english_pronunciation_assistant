# Describe Picture Studio Overhaul Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Overhaul the "Describe Picture" feature into an authentic, AI-driven multimodal speaking studio supporting dynamic AI prompt generation, real photo search, and custom image uploads for both students and teachers, with strictly grounded questions, flexible recording stopwatch, and zero image duplication on teacher assignments.

**Architecture:** Multimodal AI pipeline using dynamic image generation and vision-grounded prompt formulation in FastAPI backend (`backend/app/hf_service.py` & `backend/app/main.py`), combined with modern responsive Vue 3 + Vuetify studio views (`PicturePracticeView.vue`, `TeacherView.vue`, `StudentHomeworkView.vue`).

**Tech Stack:** Python 3.11, FastAPI, Groq LLM (llama-3.3-70b-versatile & vision), Whisper ASR, Pollinations/Unsplash APIs, Vue 3, Vite, Vuetify 3, Web Audio API.

**Spec:** `docs/superpowers/specs/2026-10-09-describe-picture-overhaul-design.md`

## Global Constraints
- System-Wide UI MUST remain in 100% Academic English (buttons, headers, navigation).
- Fluency AI chat/feedback remains in Vietnamese by default for usability.
- Teacher assignments must store `image_url` strictly once in `assignments.image_url`; student submissions must only store audio recordings and evaluations without duplicating image data.
- Deploy frontend to 123host FTP (`fluent.augusttrung.com`), never to Hugging Face.

---

### Task 1: Backend Multimodal Image Generation & Vision Grounding Services

**Files:**
- Modify: `backend/app/hf_service.py`
- Modify: `backend/app/main.py`
- Test: `scratch/test_picture_overhaul_backend.py`

**Interfaces:**
- Produces:
  - `generate_dynamic_scene(prompt: str, mode: str = "ai_gen", level: str = "intermediate") -> Dict[str, Any]`
  - `POST /api/picture-practice/create-scenario` (accepts `prompt`, `mode: "ai_gen" | "search" | "upload"`, `image_url`, `level`)
  - `POST /api/picture-practice/upload-image` (accepts multipart file, stores in `uploads/picture_practice/`, returns image URL)
  - `POST /api/picture-practice/evaluate` (evaluates student speech against visual scene elements)

- [ ] **Step 1: Write backend test script for dynamic image generation and grounding**
  Create `scratch/test_picture_overhaul_backend.py` testing:
  1. Generating an image scene from prompt `"A family having a picnic in the park with a golden retriever"`.
  2. Verifying the returned scene contains: `image_url`, `title`, 4 `guiding_questions`, 5+ `keywords`, and `sample_response`.
  3. Verifying that the guiding questions reference the actual prompt concepts (family, park, dog).

- [ ] **Step 2: Run test to confirm current behavior fails or is limited**
  Execute `python scratch/test_picture_overhaul_backend.py` and capture output.

- [ ] **Step 3: Implement dynamic scene generation in `backend/app/hf_service.py`**
  - Implement `generate_ai_scene_image(prompt: str) -> str`:
    Uses encoded URL with dynamic generation parameters:
    `https://image.pollinations.ai/prompt/{quote(clean_prompt)}?width=1024&height=680&nologo=true&seed={random_seed}`
    With resilient fallback to high-resolution Unsplash photo search based on extracted keywords.
  - Implement `generate_grounded_questions_from_scene(image_url: str, prompt_or_description: str, level: str) -> Dict[str, Any]`:
    Calls Groq LLM to analyze visual elements and construct the 4-step framework questions:
    1. Overview (Location, time, general setting).
    2. Central Subject & Actions (Who is there and what are they doing?).
    3. Details & Surroundings (Foreground, background, objects).
    4. Impressions & Feelings (Atmosphere, emotional tone).
    Extracts 5 target keywords and generates a Band 8+ sample speech.

- [ ] **Step 4: Update FastAPI routes in `backend/app/main.py`**
  - Add `POST /api/picture-practice/upload-image` with `UploadFile`.
  - Update `POST /api/picture-practice/create-scenario` to accept dynamic prompt, generation mode, and custom uploaded image URLs.
  - Ensure scenarios are persisted in `picture_scenarios` SQLite table.

- [ ] **Step 5: Run backend test script to verify passes**
  Run `python scratch/test_picture_overhaul_backend.py` to confirm all assertions pass.

- [ ] **Step 6: Commit Task 1 changes**
  Commit git changes with message: `feat(backend): implement multimodal picture generation and vision grounding pipeline`.

---

### Task 2: Student Describe Picture Studio Frontend Overhaul

**Files:**
- Modify: `frontend/src/views/PicturePracticeView.vue`

**Interfaces:**
- Consumes:
  - `POST /api/picture-practice/create-scenario`
  - `POST /api/picture-practice/upload-image`
  - `POST /api/picture-practice/evaluate`
- Produces:
  - Multi-tab Scenario Creator: Tab 1 "AI Generator" (Prompt input), Tab 2 "Search Photos" (Keyword search), Tab 3 "Upload Image" (File picker).
  - Flexible Recording Studio with Stopwatch (`MM:SS`), color-coded duration marks, and optional Exam Mode toggle.
  - Deep post-speech evaluation report with keyword detection chips and model response audio player.

- [ ] **Step 1: Build the Multi-mode Creation Modal**
  - In `frontend/src/views/PicturePracticeView.vue`, update `v-dialog v-model="showCreateModal"`:
    - Tab 1: **Generate with AI (Prompt)**: Textarea for custom prompt with prompt spark chips (e.g. "Airport boarding gate", "Family cooking pizza", "Doctor consulting patient").
    - Tab 2: **Search Real Photos**: Keyword search input returning high-res authentic photos.
    - Tab 3: **Upload My Image**: Drag-and-drop or click-to-upload custom file with immediate preview.
  - Add level selector (`Beginner`, `Intermediate`, `Advanced`).
  - Connect to backend `/api/picture-practice/create-scenario` and `/api/picture-practice/upload-image`.

- [ ] **Step 2: Upgrade Widescreen Practice Studio & Visual Canvas**
  - Enhance Left Column:
    - Display image with rounded corners, subtle shadow, and full-screen zoom preview.
    - Interactive 4-step Guiding Accordion/Cards (1. Overview, 2. People & Actions, 3. Details & Setting, 4. Impressions).
    - Target Keywords chip grid.
  - Enhance Right Column:
    - Replace rigid countdown with **Flexible Stopwatch**:
      - Large digital elapsed time display: `00:00`
      - Color-coded indicator: `< 30s` (Amber - Brief), `45s - 60s` (Green - Ideal duration), `> 75s` (Blue - Extended).
      - Optional toggle: "Exam Simulation Mode (45s TOEIC Limit)" for students wanting test-day pressure.
    - Live microphone volume meter animation while recording.
    - Buttons: "Start Speaking", "Pause", "Finish & Submit", "Retake".

- [ ] **Step 3: Upgrade Post-Evaluation Report & Model Shadowing Player**
  - Display AI evaluation score breakdown:
    - Content Coverage (did speech mention main scene elements?).
    - Spatial & Action Vocabulary (prepositions of place, present continuous tense).
    - Speech Rate & Pronunciation score.
  - Target Keywords Checklist: Visual checkmarks showing which keywords were successfully uttered.
  - **Model Sample Answer**: Band 8+ transcript with Web Speech API TTS player allowing students to listen and practice shadowing.

- [ ] **Step 4: Test frontend build**
  Run `npm --prefix frontend run build` to verify clean compilation with 0 syntax or bundle errors.

- [ ] **Step 5: Commit Task 2 changes**
  Commit git changes with message: `feat(picture-practice): overhaul student studio with multimodal prompt modal, flexible stopwatch, and model shadowing`.

---

### Task 3: Teacher Assignment Creation & Single-Image Distribution

**Files:**
- Modify: `frontend/src/views/TeacherView.vue`
- Modify: `backend/app/main.py`

**Interfaces:**
- Produces:
  - "Create Picture Assignment" dialog in Teacher Hub:
    - Teacher inputs prompt or uploads image.
    - AI generates preview of picture, guiding questions, keywords, and sample response.
    - Teacher can edit questions or keywords before confirming.
    - Teacher selects classroom(s) and submits.
  - Stores single image URL in `assignments.image_url`.

- [ ] **Step 1: Check existing Teacher Assignment creation logic**
  Inspect `frontend/src/views/TeacherView.vue` assignment creation section to locate existing modals and APIs.

- [ ] **Step 2: Add AI Picture Assignment Creator to `TeacherView.vue`**
  - Add button "New Picture Speaking Task" in Assignments tab.
  - Add modal allowing teachers to:
    1. Enter AI Prompt or upload an image.
    2. Click "Generate Preview".
    3. View the generated picture alongside generated questions and keywords.
    4. Select classroom and click "Assign to Class".
  - Connect to backend assignment creation endpoint.

- [ ] **Step 3: Ensure backend stores single `image_url` on `assignments`**
  Verify `POST /api/teacher/assignments` properly sets `type="picture"` and saves `image_url`, `prompt_guide`, and `keywords`.

- [ ] **Step 4: Verify teacher submissions table displays picture tasks cleanly**
  Ensure the teacher grading view shows the assignment's single image at the top, and displays student audio recordings below without duplicating image files.

- [ ] **Step 5: Commit Task 3 changes**
  Commit git changes with message: `feat(teacher): add AI Picture Assignment creator with preview and single-image relational storage`.

---

### Task 4: Student Homework Picture Practice View

**Files:**
- Modify: `frontend/src/views/StudentHomeworkView.vue`

**Interfaces:**
- Consumes:
  - `GET /api/homework/assignments`
  - `POST /api/homework/submit`
- Produces:
  - Dedicated Picture Speaking card in student homework list.
  - Interactive modal / view displaying teacher's assignment image, 4-step guiding questions, and recording studio.
  - Submits student audio recording and transcription to backend without altering assignment image.

- [ ] **Step 1: Inspect `StudentHomeworkView.vue` for assignment type handling**
  Review how `asg.type === 'picture'` is rendered.

- [ ] **Step 2: Implement full Picture Practice submission experience in `StudentHomeworkView.vue`**
  - Render teacher's assignment image cleanly.
  - Provide guiding questions and target keywords.
  - Allow recording with stopwatch timer and review playback before submission.
  - Submit audio and receive instant AI feedback.

- [ ] **Step 3: Commit Task 4 changes**
  Commit git changes with message: `feat(homework): render picture speaking assignments with shared image and interactive submission`.

---

### Task 5: End-to-End Verification & Production Deployment

**Files:**
- Modify/Create: `scratch/test_full_picture_overhaul.py`

- [ ] **Step 1: Run comprehensive end-to-end automated verification**
  Create and execute `scratch/test_full_picture_overhaul.py` testing:
  1. Dynamic AI scenario creation via prompt.
  2. Image upload and vision grounding.
  3. Student speech evaluation.
  4. Teacher assignment creation with single `image_url`.
  5. Student homework retrieval and submission.

- [ ] **Step 2: Build frontend distribution**
  Run `npm --prefix frontend run build`.

- [ ] **Step 3: Deploy to production host (`fluent.augusttrung.com`)**
  Run `python scratch/deploy_to_123host.py`.

- [ ] **Step 4: Verify live site**
  Confirm HTTP status 200 and test live endpoints.

- [ ] **Step 5: Final git commit & branch status review**
  Review git commit history on `feature/picture-practice-overhaul`.
