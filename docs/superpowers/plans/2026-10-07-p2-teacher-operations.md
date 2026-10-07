# P2 Teacher Operations & Class Insights Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement end-to-end P2 Educator operations: class analytics & pronunciation trouble-spot insights, non-submitter reminder alerts, assignment re-opening & deadline extension, assignment duplication, gradebook CSV export, class announcements noticeboard, and robust teacher RBAC ownership security.

**Architecture:** 
- Backend (FastAPI + SQLite): Enhance security guards with classroom & assignment ownership verification. Add analytics engine aggregating submissions & phoneme error metrics. Add announcement & reminder tables. Generate downloadable RFC 4180 CSV with UTF-8 BOM.
- Frontend (Vue 3 + Vuetify): Add Analytics & Insights tab, Class Noticeboard tab, assignment action suite (Duplicate, Re-open, Remind, Edit, Delete), and instant CSV gradebook export. Strict compliance with academic English and mandatory confirmation dialogs for risky operations.

**Tech Stack:** FastAPI, SQLite, Python, Vue 3, Vite, Vuetify 3, Material Design Icons.

---

## Global Constraints
- System-Wide UI: 100% Academic English for all teacher interface labels, buttons, dialogs, badges, and tables.
- Mandatory Confirmation Dialogs for all risky operations (re-open assignment, send reminder alert, delete assignment, remove student, delete announcement, sign out).
- Code Style: Clean modern Vue 3 / JavaScript; no redundant checks or anti-patterns; flat layouts without nested cards.
- Dual Deployment: Frontend to 123host (`fluent.augusttrung.com`), Backend to HuggingFace Space (`agrse/fluent-english-backend`).

---

### Task 1: Database Migration & Schema Extensions
**Files:**
- Modify: `backend/app/main.py:1630-1820`
- Tables: `class_announcements` (new), `assignments` (new columns: `status`), `submissions`

- [ ] **Step 1:** Create `class_announcements` table in `init_db()` (`id`, `class_id`, `teacher_id`, `title`, `content`, `announcement_type`, `assignment_id`, `created_at`, `IsXoa`).
- [ ] **Step 2:** Add migration in `init_db()` for `assignments.status` defaulting to `'active'`.
- [ ] **Step 3:** Verify SQLite schema migration runs cleanly on existing database.

---

### Task 2: Backend Security & Ownership Verification
**Files:**
- Modify: `backend/app/main.py:1920-1950` and endpoints `2395-2770`

- [ ] **Step 1:** Implement `verify_class_access(class_id, current_user, require_write)` helper checking teacher ownership, tenant admin boundaries, and suspended user status.
- [ ] **Step 2:** Implement `verify_assignment_access(assignment_id, current_user, require_write)` helper verifying class ownership.
- [ ] **Step 3:** Protect existing endpoints (`create_class`, `update_class`, `delete_class`, `remove_student_from_class`, `get_class_gradebook`, `create_assignment`, `update_assignment`, `delete_assignment`) with `require_educator_or_admin` and ownership verification.

---

### Task 3: P2 Core Endpoints (Analytics, Reminders, Reopen, Duplicate, Export)
**Files:**
- Modify: `backend/app/main.py`

- [ ] **Step 1:** Implement `GET /api/classes/{class_id}/analytics` calculating completion rate, avg score, per-assignment statistics, at-risk students, and class weak phonemes breakdown.
- [ ] **Step 2:** Implement `POST /api/assignments/{assignment_id}/remind` identifying non-submitters, creating reminder announcement, and logging audit trail.
- [ ] **Step 3:** Implement `POST /api/assignments/{assignment_id}/reopen` updating due date, posting deadline announcement, and audit logging.
- [ ] **Step 4:** Implement `POST /api/assignments/{assignment_id}/duplicate` cloning assignment structure to target class.
- [ ] **Step 5:** Implement `GET /api/classes/{class_id}/export-gradebook` generating UTF-8 BOM CSV with student matrix and assignment columns.
- [ ] **Step 6:** Implement Class Announcements CRUD (`GET /api/classes/{class_id}/announcements`, `POST`, `DELETE`).
- [ ] **Step 7:** Implement `GET /api/notifications/student/{student_id}` for student-facing noticeboard.

---

### Task 4: Automated Verification Suite (`scratch/test_p2_teacher.py`)
**Files:**
- Create: `scratch/test_p2_teacher.py`

- [ ] **Step 1:** Write comprehensive test suite covering all 13+ test scenarios (Teacher auth, ownership isolation, assignment duplicate, reopen, reminder dispatch, analytics computation, CSV export, noticeboard CRUD, suspended teacher lockout, cross-tenant isolation).
- [ ] **Step 2:** Run test suite and confirm 100% pass rate.
- [ ] **Step 3:** Run P0 and P1 regression suites (`test_p0_security.py`, `test_p1_school_admin.py`) and confirm 0 regressions.

---

### Task 5: Frontend UI Integration (`TeacherDashboard.vue`)
**Files:**
- Modify: `frontend/src/components/TeacherDashboard.vue`

- [ ] **Step 1:** Add Tab 3: "Class Analytics & Insights" with KPI stat cards, top weak phonemes radar/breakdown, and at-risk students alert list.
- [ ] **Step 2:** Add Tab 4: "Class Noticeboard" with announcement feed, type badges, post form, and deletion confirmation.
- [ ] **Step 3:** In Tab 2: "Assignments", add action buttons and modals for "Remind Missing", "Duplicate", "Re-open / Extend Deadline", "Edit", and "Delete".
- [ ] **Step 4:** In Tab 1: "Gradebook Roster", connect "Export Gradebook (CSV)" to server endpoint / client matrix.
- [ ] **Step 5:** Verify all confirmation dialogs for destructive/risky actions.
- [ ] **Step 6:** Run `npm run build` to verify 0 frontend errors or lint warnings.

---

### Task 6: Dual Production Deployment & Live Verification
- [ ] **Step 1:** Deploy frontend production build to 123host FTP (`fluent.augusttrung.com`).
- [ ] **Step 2:** Push backend changes to HuggingFace Git repository (`agrse/fluent-english-backend`).
- [ ] **Step 3:** Poll HF Space until status is `RUNNING`.
- [ ] **Step 4:** Execute live healthcheck & endpoint verification.
- [ ] **Step 5:** Commit changes to local git repo and report final results to user.
