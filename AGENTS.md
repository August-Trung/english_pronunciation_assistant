# Antigravity Project Rules

## UX & Safety Rules
- **Mandatory Confirmation for Risky Actions:** All destructive or session-altering actions (such as Sign Out / Log Out, Delete Classroom, Delete Assignment, Delete User, Delete Tenant, Remove Student, Clear History, etc.) MUST display a confirmation dialog before executing. Never perform state modifications directly without user confirmation.

## Code Style
- Always write clean modern Vue 3 / JavaScript.
- Standardize all Vietnamese text to UTF-8 accented Vietnamese.
- All UI strings, badges, headers, and AI Agent widget labels MUST be in 100% Academic English.

## Deployment Architecture
- **Frontend (`frontend/dist/`)**: Deployed exclusively to **123host** web hosting (`fluent.augusttrung.com`). Never deploy frontend files to HuggingFace.
- **Backend (`backend/app/`)**: Deployed to **HuggingFace Space** (`aorse-fluent-english-backend.hf.space`).
