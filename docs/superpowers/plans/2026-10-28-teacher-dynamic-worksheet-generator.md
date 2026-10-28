# Teacher Dynamic Worksheet & Exercise Generator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an end-to-end AI-powered Dynamic Worksheet & Assignment Generator for Teachers on Fluent, allowing educators to input target vocabulary, select pedagogical exercise formats (Listening, Reading, Writing), generate auto-graded exercises with British English (`en-GB`) voice, assign them to classrooms, and enable interactive completion and auto-scoring for students.

**Architecture:**
- **Backend (FastAPI + Groq Llama 3.3 70B + SQLite)**: Schema migrations for `assignments.content_json` and `submissions.answers_json`. High-speed structured JSON prompt generator for 12 pedagogical exercise types. Automated grading engine on submission.
- **Accent Priority (British English `en-GB`)**: All audio listening prompts, sample voice buttons, and TTS defaults across the entire Fluent platform are standardized to British English (`en-GB`).
- **Frontend (Vue 3 + Vuetify 3)**:
  - Teacher: 3-step dynamic worksheet creator & interactive preview editor in `TeacherDashboard.vue`.
  - Student: Interactive multi-format worksheet solver in `StudentHomeworkView.vue` with instant visual feedback and `en-GB` audio playback.
  - Gradebook/Review: Question-by-question evaluation breakdown in `SubmissionEvaluation.vue`.

**Tech Stack:** FastAPI, Python 3.10+, Groq API (Llama 3.3 70B Versatile), SQLite3, Vue 3, Vuetify 3, Web Speech Synthesis API (`en-GB`).

**Spec & Pedagogical Formats (12 Types):**
1. `listen_and_number`: Audio sequence, student numbers pictures/words in order of hearing.
2. `listen_and_circle`: Audio plays word/sentence, student circles/selects matching choice.
3. `listen_and_tick`: Audio plays statement, student ticks correct option.
4. `listen_and_match`: Left column has audio clips, right column has text/images; student pairs them.
5. `listen_and_tick_or_cross`: Audio statement paired with image/sentence; student chooses ✓ (True) or ✗ (False).
6. `read_and_match`: Match word to definition/collocation/Vietnamese meaning.
7. `read_and_fill_in_the_blank`: Sentence with missing word + word bank or fill-in.
8. `read_and_circle`: Reading comprehension / multiple-choice option selection.
9. `read_and_number`: Reorder sentences/events chronologically (1, 2, 3, 4).
10. `write_the_missing_word`: Cloze spelling exercise where student types the missing target word.
11. `unscramble_words`: Interactive clickable word tiles to unscramble a complete sentence.
12. `answer_the_question`: Target vocabulary question with guided short-answer or choice response.

## Global Constraints
- **Accent Rule**: British English (`en-GB`) MUST be the first priority and default everywhere voice is used. If no selector is available, voice MUST strictly default to `en-GB`.
- **UI Language Policy**: 100% International Academic English for all system UI elements.
- **Confirmation Requirement**: Risky actions (delete assignment, reset answers) require confirmation dialog.
- **Code Standards**: Modern Vue 3 Composition API, Vuetify components, no redundant condition checks.

---

## File Structure

```
backend/app/
├── main.py                          # Add worksheet endpoints, DB migrations, submission grading
└── test_worksheet_engine.py         # Unit tests for worksheet schema & generation
frontend/src/
├── components/
│   ├── TeacherDashboard.vue         # Add Worksheet format in Assign Homework modal + preview editor
│   ├── SubmissionEvaluation.vue     # Add Worksheet submission review & question-by-question report
│   └── PracticeTab.vue              # Standardize default accent to British English (en-GB)
├── views/
│   ├── StudentHomeworkView.vue      # Add Interactive Worksheet Player (all 12 formats)
│   ├── ShadowingView.vue            # Standardize default accent to British English (en-GB)
│   └── PicturePracticeView.vue      # Standardize default accent to British English (en-GB)
└── utils/
    └── tts.js                       # Reusable British English (en-GB) Web Speech helper
```

---

## Task Breakdown

### Task 1: System-Wide British English (`en-GB`) Accent Standardization

**Files:**
- Create: `frontend/src/utils/tts.js`
- Modify: `frontend/src/components/PracticeTab.vue`
- Modify: `frontend/src/views/ShadowingView.vue`
- Modify: `frontend/src/views/PicturePracticeView.vue`

**Interfaces:**
- Produces: `speakBritishText(text, rate=0.9)` and `getPreferredBritishVoice()` in `frontend/src/utils/tts.js`.
- Updates `ttsAccent` default from `'en-US'` to `'en-GB'` in `PracticeTab.vue` and `ShadowingView.vue`.

- [ ] **Step 1: Create `frontend/src/utils/tts.js` with British English prioritization**
  - Implement voice detection preferring `en-GB` / `en_GB` / UK voices (e.g. "Google UK English Male", "Google UK English Female", "Microsoft George", "Microsoft Hazel").
  - Export `speakText(text, accent = 'en-GB', rate = 0.9)`.
  - Export `speakBritishText(text, rate = 0.9)`.

- [ ] **Step 2: Update `PracticeTab.vue` default accent**
  - Set default `ttsAccent = ref('en-GB')`.
  - Reorder accent toggles/chips so British English (`en-GB`) is listed first and selected by default.

- [ ] **Step 3: Update `ShadowingView.vue` and `PicturePracticeView.vue`**
  - Set default `ttsAccent = ref('en-GB')` in `ShadowingView.vue`.
  - Update `PicturePracticeView.vue` audio synthesis utterance to `en-GB`.

- [ ] **Step 4: Verify frontend builds and accent defaults to `en-GB`**
  - Run `npm run build` in `frontend/`.
  - Confirm zero compile errors.

---

### Task 2: Backend Database Migrations & Auto-Grading Logic

**Files:**
- Modify: `backend/app/main.py:1900-1920` (Database migrations)
- Modify: `backend/app/main.py:3342-3375` (CreateAssignmentRequest schema)
- Modify: `backend/app/main.py:4100-4250` (submit_assignment endpoint)
- Create: `backend/app/test_worksheet_engine.py`

**Interfaces:**
- Produces DB columns: `assignments.content_json TEXT DEFAULT ''`, `submissions.answers_json TEXT DEFAULT ''`.
- Produces `grade_worksheet_submission(exercises, submitted_answers) -> dict`.

- [ ] **Step 1: Write unit tests in `backend/app/test_worksheet_engine.py`**
  - Test auto-grading logic for all 12 exercise formats:
    - Multiple choice & circle: exact match.
    - Sequence & ordering: array order match.
    - Fill-in-the-blank / Spelling: case-insensitive stripped string match.
    - True/False (tick/cross): boolean match.
    - Matching: dictionary key-value match.
  - Run tests with `python backend/app/test_worksheet_engine.py` and verify failure before implementation.

- [ ] **Step 2: Add database migrations in `backend/app/main.py`**
  - Add `content_json TEXT DEFAULT ''` to `assignments`.
  - Add `answers_json TEXT DEFAULT ''` to `submissions`.
  - Update `CreateAssignmentRequest` and `UpdateAssignmentRequest` to include `content_json: Optional[str] = ''` or `exercises: Optional[List[dict]] = None`.

- [ ] **Step 3: Implement `grade_worksheet_submission` in `backend/app/main.py`**
  - Compute total score on scale 0.0 - 10.0.
  - Generate question-by-question result array with `is_correct`, `student_answer`, `correct_answer`, `explanation`.
  - Update `submit_assignment` endpoint to support `assignment_type == 'worksheet'` (accepting JSON payload of answers).

- [ ] **Step 4: Run unit tests and verify passing**
  - Run `python backend/app/test_worksheet_engine.py`.
  - Confirm 100% test pass.

---

### Task 3: AI Dynamic Worksheet Generation API Endpoint

**Files:**
- Modify: `backend/app/main.py`
- Modify: `backend/app/test_worksheet_engine.py`

**Interfaces:**
- Endpoint: `POST /api/teacher/worksheet/generate`
- Request body:
  ```json
  {
    "target_vocabulary": ["elephant", "giraffe", "monkey"],
    "exercise_types": ["listen_and_circle", "read_and_match", "unscramble_words"],
    "grade_level": "Grade 3",
    "accent": "en-GB"
  }
  ```
- Response body:
  ```json
  {
    "success": true,
    "title": "Vocabulary Worksheet: Animals",
    "exercises": [
      {
        "id": "ex_1",
        "type": "listen_and_circle",
        "instruction": "Listen to the audio and circle the correct word.",
        "audio_text": "Look at the tall giraffe eating leaves.",
        "accent": "en-GB",
        "options": ["monkey", "giraffe", "elephant"],
        "correct_answer": "giraffe",
        "points": 1
      }
    ]
  }
  ```

- [ ] **Step 1: Write integration test for generation endpoint**
  - Test payload validation, fallback grounding when LLM returns JSON, and correct format compliance.

- [ ] **Step 2: Implement prompt generator & LLM caller in `backend/app/main.py`**
  - Craft pedagogical system prompt for Groq Llama 3.3 70B specifying JSON schema for each of the 12 exercise types.
  - Enforce British English spelling and pronunciation phrasing (e.g. "colour", "favourite", UK sentence structure).
  - Add robust JSON parsing with auto-retry and deterministic fallback generator.

- [ ] **Step 3: Test generation endpoint directly**
  - Send mock request with sample vocab (`["apple", "banana", "orange"]`).
  - Verify returned exercises contain proper fields for each requested type.

---

### Task 4: Teacher Dashboard - Worksheet Creator & Preview Editor

**Files:**
- Modify: `frontend/src/components/TeacherDashboard.vue`

**Interfaces:**
- Adds `worksheet` option in `newAsgType` radio/toggle (`Dynamic Vocab Worksheet`).
- UI State:
  - `newAsgVocabList: ref('')`
  - `newAsgSelectedExerciseTypes: ref([...])`
  - `newAsgGradeLevel: ref('Grade 3')`
  - `generatedExercises: ref([])`
  - `isGeneratingExercises: ref(false)`

- [ ] **Step 1: Build Teacher Creator Controls in `TeacherDashboard.vue`**
  - In `showCreateAssignmentModal`, add 3rd toggle: `Dynamic Worksheet`.
  - Render target vocabulary input box with chip preview.
  - Render Exercise Type Selector grouped into 3 panels:
    - 🎧 Listening (5 types: Listen & Number, Listen & Circle, Listen & Tick, Listen & Match, Listen & Tick/Cross).
    - 📖 Reading (4 types: Read & Match, Fill in Blank, Read & Circle, Read & Number).
    - ✍️ Writing (3 types: Missing Word, Unscramble Sentence, Answer Question).
  - Default all listening exercises to British English (`en-GB`).
  - Add "Generate Exercises with AI" button with animated progress indicator.

- [ ] **Step 2: Build Interactive Exercise Preview & Editing Card List**
  - Render each generated exercise with an edit card:
    - Listen button to test British English audio utterance directly in the modal.
    - Editable question text, options, and correct answer selection.
    - Delete button to remove any unwanted question.
    - Reorder buttons (Move Up / Down).
  - Bind to `submitCreateAssignment` to save `assignment_type: 'worksheet'` and `content_json: JSON.stringify(generatedExercises)`.

- [ ] **Step 3: Add Worksheet indicators to Teacher Assignment List**
  - In the teacher assignment cards, show `Dynamic Worksheet` chip (`color="indigo"`).
  - Display number of exercises (e.g. `6 interactive exercises`).

---

### Task 5: Student Interactive Worksheet Studio

**Files:**
- Modify: `frontend/src/views/StudentHomeworkView.vue`

**Interfaces:**
- Renders `asg.assignment_type === 'worksheet'` assignments.
- State:
  - `studentAnswers: ref({})`
  - `isSubmittingWorksheet: ref(false)`
  - `submissionResult: ref(null)`

- [ ] **Step 1: Build Interactive Exercise Renderers in `StudentHomeworkView.vue`**
  - 🎧 **Listening Exercises**:
    - Large audio play button with wave animation and British English voice (`en-GB`).
    - Circle/Tick options: sleek selectable cards.
    - Tick/Cross: toggle buttons (✓ True / ✗ False).
    - Numbering: select 1, 2, 3... dropdown/chip.
    - Matching: two-column click-to-connect cards.
  - 📖 **Reading Exercises**:
    - Match: pair selection.
    - Fill-in-the-blank: inline text input with word bank chips.
    - Multiple choice: 4-card selection.
    - Numbering: sequence ordering.
  - ✍️ **Writing Exercises**:
    - Missing word: clean text box with immediate feedback hint.
    - Unscramble sentence: interactive clickable word tokens that hop into the constructed sentence line.
    - Answer question: short text input or options.

- [ ] **Step 2: Implement Progress Bar and Submission Workflow**
  - Stepper or sticky progress bar: `Question X of Y completed`.
  - Submit button with confirmation dialog.
  - On submit: POST to `/api/assignments/submit`.
  - Display instant celebratory modal / score breakdown (e.g. `8.5 / 10 - Excellent Job!`).

---

### Task 6: Teacher Gradebook & Detailed Submission Evaluation

**Files:**
- Modify: `frontend/src/components/SubmissionEvaluation.vue`
- Modify: `frontend/src/components/TeacherDashboard.vue`

**Interfaces:**
- When reviewing a worksheet submission, parses `answers_json` and displays question-by-question audit:
  - Question instruction & question text.
  - Audio replay button (`en-GB`).
  - Student's selected answer vs Correct answer.
  - Score per question (1/1 or 0/1).
  - Teacher feedback textarea to leave custom praise/notes.

- [ ] **Step 1: Update `SubmissionEvaluation.vue` to render worksheet results**
  - If submission has `answers_json`, render the detailed answer audit table.
  - Color-code correct (green) and incorrect (red) answers with explanation.

- [ ] **Step 2: Connect teacher review dialog from gradebook**
  - Ensure clicking a worksheet score in `TeacherDashboard.vue` opens `SubmissionEvaluation.vue` with full question details.

---

### Task 7: Comprehensive Verification & Quality Assurance

**Files:**
- Modify: `tests/test_worksheet_e2e.py`

- [ ] **Step 1: Run Backend Automated Tests**
  - Execute test suite: `python backend/app/test_worksheet_engine.py`.
  - Ensure all 12 formats validate, generate, and grade correctly.

- [ ] **Step 2: Build Frontend**
  - Run `cd frontend && npm run build`.
  - Verify zero lint/type errors and correct asset bundle creation.

- [ ] **Step 3: Verification of British English (`en-GB`) Audio**
  - Check that all speech synthesis instances default strictly to `en-GB`.
  - Verify no unintentional US accent fallbacks exist.

- [ ] **Step 4: End-to-End Walkthrough**
  - Create teacher assignment with 5 sample vocabulary words across 4 exercise types.
  - Complete the assignment as student.
  - Verify grade appears in Gradebook and detailed audit is accurate.
