# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ST-Agent is a full-stack AI travel guide and image generation platform. Backend is FastAPI + MySQL; frontend is Vue 3 + Pinia + Vite 7. AI models use SenseNova (sensenova-6.7-flash-lite for chat, sensenova-u1-fast for images via OpenAI SDK).

## Development Commands

### Backend
```bash
# Activate venv first
cd backend && source agent/bin/activate  # macOS/Linux

# Install dependencies (must use venv pip)
agent/bin/python -m pip install -r requirements.txt

# Run dev server (from backend/ dir, with venv activated)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run Alembic migrations (use venv python, NOT bare alembic command)
agent/bin/python -m alembic upgrade head

# Create new migration
agent/bin/python -m alembic revision --autogenerate -m "description"

# API docs at http://localhost:8000/docs (Swagger) or /redoc
```

### Frontend
```bash
cd frontend
npm install
npm run dev          # Dev server on http://localhost:5173
npm run build        # Type-check + production build (vue-tsc -b && vite build)
```

## Architecture

### Backend (FastAPI)

- **Config**: `app/config.py` — Settings class reads from env vars, cached via `lru_cache`. Database URL is a property that constructs the MySQL connection string.
- **Lifespan**: `app/main.py` runs `alembic upgrade head` on startup using `sys.executable -m alembic` (NOT bare `alembic` — must use venv Python).
- **API prefix**: All routes mounted at `/api/v1`. Static files at `/generated/` and `/uploads/`.
- **Auth**: JWT via `python-jose`. `get_current_user` dependency in `app/utils/security.py` validates Bearer token → extracts user_id from `sub` claim → loads User from DB. Token key in localStorage is `'token'` (NOT `'access_token'`).
- **Models** (`app/models/`): User, ChatHistory (soft-deleted via `is_deleted` + `deleted_at`), ReportHistory, ImageFavorite, Share (UUID token-based). All share a common `Base` from `database.py`.
- **Services** (`app/services/`): Thin layer between API and models. `ai_service.py` handles SenseNova API calls with retry logic. `chat_history_service.py` uses soft-delete pattern (all queries filter `is_deleted == False`). `export_service.py` uses weasyprint for PDF export.
- **Alembic**: Migrations in `alembic/versions/`. `env.py` imports all models and overrides `sqlalchemy.url` from app config. Migration numbering: 001_initial_schema, 002_soft_delete, 003_avatar_url, 004_favorites_and_shares.

### Frontend (Vue 3 + Pinia)

- **Two API service files**:
  - `services/auth.ts` — Dedicated auth API with axios instance (baseURL `/api/v1`). Returns `response.data` directly (no `.data` wrapper). Used by auth store.
  - `services/api.ts` — General API with axios instance (baseURL `/api/v1`). Returns full axios response (needs `.data`). Exports `authApi`, `chatApi`, `imageApi`, `travelApi`, `shareApi`, `downloadBlob`. SSE endpoints use `fetch()` directly (not axios) — returns raw Response for manual SSE parsing.
- **Stores**:
  - `stores/auth.ts` — JWT auth state, login/logout/checkAuth. localStorage key: `token`.
  - `stores/app.ts` — Theme (light/dark/system with DOM sync + transition animations), locale, user settings.
  - `stores/session.ts` — Session list, search, trash management. Uses `chatApi`.
- **Router**: Auth guard checks `localStorage.getItem('token')`. Routes with `meta: { noAuth }` bypass guard (only `/share/:token`).
- **Vite proxy**: `/api` → `http://localhost:8000` with rewrite to `/api/v1`; `/generated` → `http://localhost:8000/generated`.
- **TailwindCSS**: Dark mode via `class` strategy (toggle `dark` on `<html>`). Design language: amber/orange gradients.
- **SSE streaming**: Both `chatApi.streamChat` and `imageApi.streamGenerate` use native `fetch()` + manual SSE parsing (event types: `token`, `done`, `error`, `image_intent`, `image_progress`, `image_result`).

### Key Patterns

- **Soft delete**: ChatHistory uses `is_deleted` boolean + `deleted_at` timestamp. All service queries filter `is_deleted == False`. Trash API: `/chat/trash` (list), `/chat/trash/{id}/restore`, permanent delete, clear.
- **Token consistency**: Frontend localStorage always uses key `'token'`. Both `services/auth.ts` and `services/api.ts` read from this key.
- **CORS**: Configured for `http://localhost:5173` and `http://localhost:3000` via `CORS_ORIGINS` setting.
- **SSE response handling**: Backend sends `event:` + `data:` lines. Frontend reads with `ReadableStream` + `TextDecoder`, splits by newline, parses `event:` and `data:` separately.