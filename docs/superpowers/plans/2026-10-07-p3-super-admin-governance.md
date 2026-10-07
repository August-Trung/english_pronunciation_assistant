# P3 Super Admin Governance & Platform Operations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement comprehensive P3 Super Admin platform governance: atomic school tenant onboarding with initial School Admin creation, full tenant lifecycle management (Active / Trial / Suspended / Expired) with instant login lockout on suspended/expired tenants, deep tenant usage and audio storage metrics, advanced searchable audit log viewer, "View As / Inspect School" support mode, and full UI integration in `AdminView.vue`.

**Architecture:** 
- Backend (FastAPI + SQLite): Add `tenants.status` column with automated migrations. Update `security.py` to enforce tenant lifecycle lockout (rejecting suspended/expired tenants with HTTP 403). Create `/api/admin/tenants/onboard` with atomic user & tenant creation. Add `/api/admin/tenants/{id}/lifecycle` and comprehensive metrics aggregation. Add filtered `/api/admin/audit-logs` and `/api/admin/impersonate-tenant/{id}`.
- Frontend (Vue 3 + Vuetify): Update `AdminView.vue` with tenant status chips (`ACTIVE`, `TRIAL`, `SUSPENDED`, `EXPIRED`), full metric counters, Onboard School modal, Lifecycle Management modal, "Inspect School" switcher, and searchable Audit Viewer.

**Tech Stack:** FastAPI, SQLite, Python, Vue 3, Vuetify 3, Material Design Icons.

---

## Global Constraints
- System-Wide UI: 100% Academic English across all Super Admin interfaces.
- Mandatory Confirmation Dialogs for risky actions (Suspend Tenant, Delete Tenant, Clear Audio, Change User Role, Sign Out).
- Dual Deployment: Frontend to 123host (`fluent.augusttrung.com`), Backend to HuggingFace Space (`agrse/fluent-english-backend`).

---

### Task 1: Database Migration & Security Guard Extensions
**Files:**
- Modify: `backend/app/main.py` (`init_db`)
- Modify: `backend/app/security.py` (`get_current_user_from_db`)

- [ ] **Step 1:** Add migration in `init_db()` for `ALTER TABLE tenants ADD COLUMN status TEXT DEFAULT 'active'`.
- [ ] **Step 2:** In `security.py:get_current_user_from_db`, verify tenant status if `user.role != 'super_admin'`: if `tenant.status == 'suspended'`, raise HTTP 403 Forbidden.
- [ ] **Step 3:** Verify existing tests still pass.

---

### Task 2: Core P3 Backend Endpoints
**Files:**
- Modify: `backend/app/main.py`

- [ ] **Step 1:** Implement `POST /api/admin/tenants/onboard` creating tenant and provisioning initial School Admin with PBKDF2 hash atomically.
- [ ] **Step 2:** Implement `POST /api/admin/tenants/{tenant_id}/lifecycle` for updating status (`active`, `trial`, `suspended`, `expired`), seats, and expiry date.
- [ ] **Step 3:** Implement `GET /api/admin/tenants` with deep usage metrics: students, teachers, classes, submissions, audio storage MB, last active timestamp.
- [ ] **Step 4:** Implement `POST /api/admin/impersonate-tenant/{tenant_id}` creating scoped inspection token for Super Admin.
- [ ] **Step 5:** Enhance `GET /api/admin/audit-logs` with filters (`tenant_id`, `action`, `search`, `limit`).
- [ ] **Step 6:** Implement `GET /api/admin/backup-snapshot` for platform database backup snapshot.

---

### Task 3: Automated Verification Suite (`scratch/test_p3_super_admin.py`)
**Files:**
- Create: `scratch/test_p3_super_admin.py`

- [ ] **Step 1:** Write comprehensive test suite covering all P3 scenarios:
  1. Super Admin login & auth check
  2. School onboarding with atomic admin creation
  3. School Admin of onboarded tenant logs in successfully
  4. Tenant lifecycle status update (Active -> Suspended)
  5. Suspended tenant immediate user lockout (HTTP 403)
  6. Reactivation of tenant & access restoration
  7. Tenant metrics aggregation accuracy
  8. Filtered Audit Logs retrieval
  9. Super Admin impersonation / inspect mode token
  10. Backup snapshot export
- [ ] **Step 2:** Run test suite and confirm 100% pass rate.
- [ ] **Step 3:** Run P0, P1, and P2 regression suites.

---

### Task 4: Frontend UI Integration (`AdminView.vue`)
**Files:**
- Modify: `frontend/src/views/AdminView.vue`

- [ ] **Step 1:** In Tenants Tab, add status badges (`ACTIVE`, `TRIAL`, `SUSPENDED`, `EXPIRED`) and metric columns (Seats, Teachers, Submissions, Audio MB, Last Active).
- [ ] **Step 2:** Add "+ Onboard School" modal with both School details and Admin credentials inputs.
- [ ] **Step 3:** Add "Lifecycle & Quota" modal for managing status, seats, expiry date.
- [ ] **Step 4:** Add "Inspect School" mode button and visual banner with "Exit Inspection".
- [ ] **Step 5:** In Audit Logs Tab, add filter chips, search input, and tenant dropdown.
- [ ] **Step 6:** Run `npm run build` and verify 0 errors.

---

### Task 5: Dual Production Deployment & Live Verification
- [ ] **Step 1:** Deploy frontend production build to 123host FTP.
- [ ] **Step 2:** Push backend changes to HuggingFace Space.
- [ ] **Step 3:** Poll HF Space until status is `RUNNING`.
- [ ] **Step 4:** Execute live healthcheck & endpoint verification.
- [ ] **Step 5:** Commit local git repo changes and report final results to user.
