# 3D Pixar & Vibrant Cute Kids UI Design for Fluent

## 1. Overview & Objectives

**Target Audience:** Primary school students (Cấp 1, ages ~6–11) learning English pronunciation and speaking.  
**Core Goal:** Transform the Fluent frontend from a dry, formal academic dashboard into a joyful, vibrant, cute, and gamified English learning studio (inspired by Duolingo, Khan Academy Kids, and Babilala).  
**Platform Scope:** Applied exclusively to the Fluent platform (`fluent.augusttrung.com`) on the dedicated development branch `feat/kids-cute-ui`.  
**Safety & Rollback:** The previous working branch `codex/customer-exercise-feedback` remains untouched. Restoring the prior UI requires only switching branches and running `deploy_to_123host.py`.

---

## 2. Art Direction & Visual Aesthetics

### 2.1 Aesthetic Principles
- **Chunky & Bouncy**: Soft 3D bevels, tactile depth, bouncy active state (`translateY(3px)`).
- **Candy Cheerful Palette**: High-contrast, friendly hues that spark delight without overwhelming readability.
- **Pixar-Style 3D Cartoon Assets**: High-resolution, transparent 3D illustrations with expressive, cute character design to replace plain/flat vector icons in major navigation and feature headers.
- **Clear Information Density**: Large, readable typography with clean borders (`border: 2px solid`) ensuring effortless navigation for young learners.

### 2.2 Color Tokens & Gradients
- **Sky & Ocean (Primary)**: `#29B6F6` (base), `#0288D1` (shade/depth), Gradient: `linear-gradient(135deg, #00E5FF 0%, #0288D1 100%)`
- **Sunshine Gold (Joy & Streak)**: `#FFD54F` (base), `#FF8F00` (shade), Gradient: `linear-gradient(135deg, #FFE082 0%, #FF8F00 100%)`
- **Coral & Bubblegum (Action & Energy)**: `#FF6E40` / `#FF4081` (base), `#D81B60` (shade), Gradient: `linear-gradient(135deg, #FF8A80 0%, #FF1744 100%)`
- **Fresh Mint & Lime (Success & Progress)**: `#00E676` (base), `#00A152` (shade), Gradient: `linear-gradient(135deg, #69F0AE 0%, #00B248 100%)`
- **Magic Purple (AI & Homework)**: `#AB47BC` (base), `#6A1B9A` (shade), Gradient: `linear-gradient(135deg, #CE93D8 0%, #6A1B9A 100%)`
- **Background**: Soft cream-white `#F8FAFC` with playful, subtle rounded card containers `#FFFFFF`.

### 2.3 Shapes & Interactive Physics
- **Border Radius**:
  - Cards & Panels: `20px – 24px` (`border-radius: 20px`)
  - Badges & Pills: `9999px` (`border-radius: 9999px`)
  - Buttons: `16px – 20px` or full pill
- **Chunky 3D Button Physics**:
  ```css
  .kids-btn-3d {
    border-radius: 16px;
    font-weight: 800;
    text-transform: none;
    box-shadow: 0 4px 0 var(--btn-shadow-color, #0288D1), 0 8px 16px rgba(0,0,0,0.08);
    transition: transform 0.1s ease, box-shadow 0.1s ease;
  }
  .kids-btn-3d:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 0 var(--btn-shadow-color, #0288D1), 0 10px 20px rgba(0,0,0,0.12);
  }
  .kids-btn-3d:active {
    transform: translateY(3px);
    box-shadow: 0 1px 0 var(--btn-shadow-color, #0288D1), 0 2px 6px rgba(0,0,0,0.08);
  }
  ```

---

## 3. 3D Cartoon Asset Manifest

All assets will be generated in transparent PNG/WebP format and saved to `frontend/public/assets/kids/`:

1. **`icon-speaking-3d.webp`**: Cute 3D astronaut microphone with cartoon eyes & cheerful smile.
2. **`icon-shadowing-3d.webp`**: 3D pastel candy headphones with colorful musical notes.
3. **`icon-homework-3d.webp`**: 3D magic storybook opening with glowing golden stars.
4. **`icon-leaderboard-3d.webp`**: Shiny 3D golden championship cup with a friendly smiling face.
5. **`icon-flashcards-3d.webp`**: 3D magical treasure/card box with glowing cards.
6. **`icon-picture-3d.webp`**: 3D colorful retro camera with big cute lens eyes.
7. **`badge-star-3d.webp`**: Cheerful 3D golden star with rosy cheeks.
8. **`badge-fire-3d.webp`**: Animated-style 3D friendly flame (Streak icon).
9. **`badge-gem-3d.webp`**: Sparkling 3D purple/cyan crystal gem (XP / Reward icon).
10. **`mascot-robot-3d.webp`**: Friendly little companion robot / astronaut for the AI Assistant.

---

## 4. Component & View Transformation

### 4.1 Global Layout (`frontend/src/App.vue`)
- **Navigation Drawer / Sidebar**:
  - Replace flat MDI icons in navigation items with the 3D sticker icons (`28px x 28px`).
  - Active item indicator styled with bouncy candy background and soft glow.
  - Sidebar brand header features the cute mascot along with the vibrant "FLUENT" logo.
- **Top Header Bar**:
  - Student status pills (Streak 🔥, Stars ⭐, Level 🚀) styled as chunky candy pill badges.
  - Friendly greeting with student name.
- **Floating AI Assistant Widget (`AIAgentWidget.vue`)**:
  - Mascot avatar updated to `mascot-robot-3d.webp`.
  - Chat bubble styled with playful rounded edges and cheerful header.

### 4.2 Student Homework Studio (`frontend/src/views/StudentHomeworkView.vue`)
- **Homework Hero Banner**:
  - Gradient purple-blue theme with `icon-homework-3d.webp` floating on the left.
  - Motivating headline: *"FUN HOMEWORK MISSIONS"* with clear deadline tags.
- **Assignment Cards**:
  - Bubbly white cards with 2px soft pastel border and hover elevation.
  - Status badges ("To Do", "Submitted", "Great Job!") styled as candy pills with stars.
  - Recording & submission buttons transformed into chunky 3D press buttons.

### 4.3 Speaking & Practice Studios (`frontend/src/components/PracticeTab.vue`, `ShadowingView.vue`)
- **Hero / Controls**:
  - Chunky 3D microphone recording button with playful pulsing glow when active.
  - Real-time audio waveform styled with vibrant rainbow/candy bars.
  - Scoring results display cheerful 3D stars (1 to 3 stars) based on pronunciation accuracy.

### 4.4 Leaderboard Studio (`frontend/src/views/LeaderboardView.vue`)
- **Podium**:
  - 1st, 2nd, and 3rd rank podium blocks styled with 3D gold, silver, and bronze candy colors.
  - `icon-leaderboard-3d.webp` at the top of the podium.

---

## 5. Implementation Strategy

1. **Phase 1: Asset Creation**: Generate all 10 high-quality 3D Pixar-style assets into `frontend/public/assets/kids/`.
2. **Phase 2: Global Kids Theme CSS**: Define reusable classes (`.kids-card`, `.kids-btn-3d`, `.kids-pill`, `.kids-gradient-*`) in a dedicated stylesheet `frontend/src/styles/kids-theme.scss`.
3. **Phase 3: Core App Integration**: Upgrade `App.vue` navigation, top status pills, and AI Assistant widget.
4. **Phase 4: Student Views Polish**: Upgrade `StudentHomeworkView.vue`, `PracticeTab.vue`, and `LeaderboardView.vue`.
5. **Phase 5: Build & Verification**: Run Vite build, inspect visual hierarchy, and test on local development server.

---

## 6. Rollback & Deployment Protocol
- **Live Deployment**: Built using `npm run build` and deployed strictly via `python scratch/deploy_to_123host.py` to `fluent.augusttrung.com`.
- **Zero Risk Rollback**: If client requests the previous UI, simply execute:
  ```bash
  git checkout codex/customer-exercise-feedback
  npm run build
  python scratch/deploy_to_123host.py
  ```
  This immediately restores the exact previous state in under 1 minute.
