# 3D Pixar & Vibrant Cute Kids UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the Fluent frontend into a cute, vibrant, 3D Pixar-styled English learning studio tailored for primary school students (cấp 1).

**Architecture:** Create dedicated 3D cartoon image assets in `frontend/public/assets/kids/`, introduce a global kids styling layer with bouncy physics and candy gradients in `frontend/src/styles/kids-theme.scss`, and modernize key student touchpoints (`App.vue`, `StudentHomeworkView.vue`, `PracticeTab.vue`, `LeaderboardView.vue`, `AIAgentWidget.vue`).

**Tech Stack:** Vue 3, Vuetify 3, Vite, Sass/CSS3 (3D press shadows, spring transitions), SVG/WebP assets.

**Spec:** [`docs/superpowers/specs/2026-11-06-kids-vibrant-cute-ui-design.md`](file:///d:/Study/Projects/Python%20project/english_pronunciation_assistant/docs/superpowers/specs/2026-11-06-kids-vibrant-cute-ui-design.md)

## Global Constraints
- Target platform: Fluent (`fluent.augusttrung.com`) exclusively.
- All general UI labels MUST remain in 100% Academic English as per project rules.
- Confirmation dialogs MUST be maintained for destructive or session-altering actions.
- Rollback safety: Keep `codex/customer-exercise-feedback` completely intact.

---

### Task 1: Generate & Scaffold 3D Pixar Cartoon Assets

**Files:**
- Create directory: `frontend/public/assets/kids/`
- Create assets:
  - `frontend/public/assets/kids/icon-speaking-3d.webp`
  - `frontend/public/assets/kids/icon-shadowing-3d.webp`
  - `frontend/public/assets/kids/icon-homework-3d.webp`
  - `frontend/public/assets/kids/icon-leaderboard-3d.webp`
  - `frontend/public/assets/kids/icon-flashcards-3d.webp`
  - `frontend/public/assets/kids/icon-picture-3d.webp`
  - `frontend/public/assets/kids/badge-star-3d.webp`
  - `frontend/public/assets/kids/badge-fire-3d.webp`
  - `frontend/public/assets/kids/badge-gem-3d.webp`
  - `frontend/public/assets/kids/mascot-robot-3d.webp`

- [ ] **Step 1: Create assets directory and invoke image generation or provide high-fidelity 3D Pixar SVG/WebP assets**
- [ ] **Step 2: Verify all 10 assets exist and are accessible from `/assets/kids/<name>` in public directory**
- [ ] **Step 3: Commit assets**

---

### Task 2: Build Reusable Kids Theme Stylesheet & Bouncy Components

**Files:**
- Create: `frontend/src/styles/kids-theme.scss`
- Modify: `frontend/src/main.js` (import `kids-theme.scss`)

**Interfaces:**
- Produces: CSS utility classes `.kids-card`, `.kids-card-interactive`, `.kids-btn-3d`, `.kids-pill-badge`, `.kids-gradient-sky`, `.kids-gradient-gold`, `.kids-gradient-purple`, `.kids-gradient-coral`, `.kids-gradient-mint`.

- [ ] **Step 1: Write `kids-theme.scss` containing candy color tokens, 3D bottom-shadow buttons, bouncy click animations, and 20px card styles**
- [ ] **Step 2: Import `kids-theme.scss` in `frontend/src/main.js`**
- [ ] **Step 3: Verify build (`npm run build`) compiles cleanly without CSS errors**
- [ ] **Step 4: Commit style foundations**

---

### Task 3: Upgrade Navigation, Header & AI Mascot in `App.vue`

**Files:**
- Modify: `frontend/src/App.vue`
- Modify: `frontend/src/components/AIAgentWidget.vue`

- [ ] **Step 1: Replace Sidebar navigation flat MDI icons with 3D Pixar sticker images**
- [ ] **Step 2: Style Top Bar student chips (Streak 🔥, Stars ⭐, XP 💎) as candy pill badges**
- [ ] **Step 3: Update `AIAgentWidget.vue` avatar to use `mascot-robot-3d.webp` with playful chat styling**
- [ ] **Step 4: Verify navigation links, responsiveness, and drawer rail mode**
- [ ] **Step 5: Commit `App.vue` and `AIAgentWidget.vue`**

---

### Task 4: Upgrade Student Homework View (`StudentHomeworkView.vue`)

**Files:**
- Modify: `frontend/src/views/StudentHomeworkView.vue`

- [ ] **Step 1: Upgrade Homework Banner to playful 3D hero with `icon-homework-3d.webp` and vibrant purple-blue gradient**
- [ ] **Step 2: Style assignment mission cards with `.kids-card`, colorful status pills, and 3D action buttons**
- [ ] **Step 3: Style the interactive exercise questions and audio recorder with bouncy buttons**
- [ ] **Step 4: Verify assignment listing, recording, and submission flows**
- [ ] **Step 5: Commit `StudentHomeworkView.vue`**

---

### Task 5: Upgrade Practice Studio & Leaderboard

**Files:**
- Modify: `frontend/src/components/PracticeTab.vue`
- Modify: `frontend/src/views/LeaderboardView.vue`

- [ ] **Step 1: Upgrade Speaking Studio recording button with chunky 3D press physics and colorful soundwaves**
- [ ] **Step 2: Upgrade Leaderboard podium with 3D gold cup (`icon-leaderboard-3d.webp`) and vibrant candy tiers**
- [ ] **Step 3: Run Vite build (`npm run build`) and test frontend locally**
- [ ] **Step 4: Commit views and record verification evidence**
