# Antigravity Project Rules

## UX & Safety Rules
- **Mandatory Confirmation for Risky Actions:** All destructive or session-altering actions (such as Sign Out / Log Out, Delete Classroom, Delete Assignment, Delete User, Delete Tenant, Remove Student, Clear History, etc.) MUST display a confirmation dialog before executing. Never perform state modifications directly without user confirmation.

## Code Style & Language Policy
- Always write clean modern Vue 3 / JavaScript.
- Standardize all Vietnamese text to UTF-8 accented Vietnamese.
- **System-Wide UI**: All general UI elements (buttons, badges, headers, navigation, tables) MUST remain in 100% Academic English.
- **FLUENT AI ASSISTANT Language Policy**: The **FLUENT AI ASSISTANT** chat responses priority is **VIETNAMESE** by default for maximum usability and friendliness. English is used ONLY when:
  1. The user explicitly requests to chat/speak in English.
  2. The user initiates an interactive Voice Roleplay scenario (e.g. Hotel receptionist speaking roleplay).

## Deployment Architecture
- **Frontend (`frontend/dist/`)**: Deployed exclusively to **123host** web hosting (`fluent.augusttrung.com`). Never deploy frontend files to HuggingFace.
- **Backend (`backend/app/`)**: Deployed to **HuggingFace Space** (`aorse-fluent-english-backend.hf.space`).
