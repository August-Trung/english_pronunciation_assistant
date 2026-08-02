# Project Rules

## General
- Follow the existing code style and patterns.
- Use npm for running project commands.
- Keep code in JavaScript unless migration is required.

## Stack
- Framework: Vue 3 + Vite
- UI Library: Vuetify
- Enabled Features: Base setup

## UX & Safety Rules
- **Confirmation Required for High-Risk Actions:** All destructive or session-altering actions (Sign Out / Log Out, Delete, Remove) MUST require an explicit confirmation modal before executing.
- **Language Policy:** Entire UI MUST be in 100% Academic English.

## Deployment Architecture
- **Frontend (`frontend/dist/`)**: Uploaded to **123host** (`fluent.augusttrung.com`). Do NOT deploy static frontend files to HuggingFace.
- **Backend API**: Hosted separately on **HuggingFace Space** (`aorse-fluent-english-backend.hf.space`).
