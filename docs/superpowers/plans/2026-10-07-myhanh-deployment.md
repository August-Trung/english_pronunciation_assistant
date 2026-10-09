# MyHanh Domain Limited Mode & Deployment Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Configure domain-based feature toggling for `myhanh.augusttrung.com` to restrict navigation to only Speaking, Shadowing, and Leaderboard while keeping `fluent.augusttrung.com` 100% intact with full features, build the frontend, and deploy to `/domains/myhanh.augusttrung.com/public_html` on 123host.

**Architecture:** 
- In Vue 3 frontend (`App.vue` & `router/index.js`), dynamically detect domain using `window.location.hostname.includes('myhanh') || window.location.search.includes('mode=myhanh')`.
- Conditionally render navigation items: only Speaking, Shadowing, and Leaderboard when in My Hanh mode.
- Add navigation guard in `router/index.js` to redirect unpermitted routes on `myhanh` to `/`.
- Add deployment script `scratch/deploy_to_myhanh.py` to upload the build dist to `/domains/myhanh.augusttrung.com/public_html` via FTP.

**Tech Stack:** Vue 3, Vite, Vuetify, Python ftplib

---

### Task 1: Add domain-based feature toggling to frontend
**Files:**
- Modify: `frontend/src/App.vue`
- Modify: `frontend/src/router/index.js`

- [x] **Step 1:** In `frontend/src/App.vue`:
  - Define `isMyHanhDomain` computed property.
  - In Desktop nav pills, wrap Homework, History Log, Teacher Hub, and Admin Console in `v-if="!isMyHanhDomain"`.
  - In Mobile bottom nav, wrap Analytics and Profile in `v-if="!isMyHanhDomain"`, and label `/leaderboard` as `Leaderboard`.
  - In Avatar dropdown, wrap `Weak Words Flashcards` in `v-if="!isMyHanhDomain"`.
  - In `isStandalonePortalRoute`, return `false` if `isMyHanhDomain.value`.

- [x] **Step 2:** In `frontend/src/router/index.js`:
  - Add `router.beforeEach` to redirect routes other than `/`, `/shadowing`, `/leaderboard`, `/profile` back to `/` when `isMyHanh` is active.

---

### Task 2: Add deploy script for myhanh.augusttrung.com
**Files:**
- Create: `scratch/deploy_to_myhanh.py`
- Modify: `frontend/package.json`

- [x] **Step 1:** Create `scratch/deploy_to_myhanh.py` pointing `REMOTE_BASE` to `/domains/myhanh.augusttrung.com/public_html`.
- [x] **Step 2:** Add `"deploy:myhanh": "vite build && python ../scratch/deploy_to_myhanh.py"` in `frontend/package.json`.

---

### Task 3: Build frontend and deploy to 123host
**Files:**
- Output: `frontend/dist`
- Target: `/domains/myhanh.augusttrung.com/public_html`

- [x] **Step 1:** Run `npm run build` in `frontend/` and confirm build passes with no errors.
- [x] **Step 2:** Run `python scratch/deploy_to_myhanh.py` to upload to 123host.
- [x] **Step 3:** Verify deployment success.
