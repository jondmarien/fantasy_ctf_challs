# FantasyCTF Hosting Plan: The Chronomancer's Portal

This plan outlines the steps to host the FantasyCTF challenges on `ctf.chron0.tech` with a custom frontend, automated challenge deployment, and robust flag submission via a headless CTFd backend.

## 🎯 Objective
Deploy a high-fantasy themed CTF platform at `ctf.chron0.tech`.
- **Frontend**: Custom React/Vite application (derived from `../ctfd-live-scoreboard`).
- **Backend**: CTFd instance serving as a headless API.
- **Challenges**: Dockerized network and LLM challenges.
- **Branch**: `feat/hosting`

---

## 🏗️ Architecture Overview

### 1. The Portal (Frontend)
- **Source**: The `/fantasy-ctf` route and components from `../ctfd-live-scoreboard`.
- **Customization**: The root path (`/`) will serve the Fantasy Tavern theme by default.
- **Hosting**: Vercel or a dedicated VPS container.
- **Integration**: Communication with the CTFd API via `/api` proxy.

### 2. The Guild Hall (Backend)
- **Engine**: CTFd (Headless).
- **Domain**: `api.ctf.chron0.tech`.
- **Logic**: Handles user registration, teams, dynamic scoring, and flag validation.

### 3. The Dungeons (Challenge Hosting)
- **Service Type**: Dockerized containers.
- **LLM Challenges**: Consolidated Gemini-based FastAPI server.
- **Prog Challenges**: Consolidated "Advanced" container + individual network challenges.
- **Reverse Proxy**: Traefik or Nginx with Let's Encrypt for SSL (`*.ctf.chron0.tech`).

---

## 🛠️ Implementation Phases

### Phase 1: Workspace & Frontend Migration
1. **Initialize `frontend/`**: Create a new directory and copy the core logic from `../ctfd-live-scoreboard`.
2. **Theme Swap**: 
   - Set `FANTASY_THEME` as the default in `ThemeContext.tsx`.
   - Update `App.tsx` to serve `FantasyCtfPage` at the root `/` path.
3. **Environment Sync**: Setup `.env` for the frontend to point to the production CTFd instance.

### Phase 2: Infrastructure & Docker Orchestration
1. **Production Compose**: Draft a `docker-compose.prod.yml` in the root that aggregates:
   - CTFd (Backend)
   - Redis/Postgres (CTFd Requirements)
   - LLM Challenge Server
   - Advanced Programming Server
   - Networked Crypto/Prog challenges
2. **Reverse Proxy Setup**: Configure Traefik to route:
   - `ctf.chron0.tech` -> Frontend
   - `api.ctf.chron0.tech` -> CTFd
   - `oracle.ctf.chron0.tech` -> LLM/Network challenges

### Phase 3: Challenge Synchronization (`ctfcli`)
1. **CLI Adaptation**: 
   - Use the existing `ctfcli` (installed in `.venv/Scripts/ctf.exe`).
   - Update `.ctf/config` with the new production URL and access token.
2. **Metadata Audit**: Run `ctf challenge verify` on all 22 challenges.
3. **Mass Sync**: Deploy and install all challenges to the new instance.

### Phase 4: CI/CD & Secret Management
1. **GitHub Actions**: Create a workflow to:
   - Build and push challenge Docker images to a registry.
   - Sync metadata on push to `main`.
2. **Secret Store**: Configure Gemini API keys, CTFd tokens, and DB credentials in GitHub Secrets.

---

## 🏃 Action Items for the Next Agent
1. **Branch Check**: Ensure you are on `feat/hosting`.
2. **Copy Scoreboard**: Use `xcopy` or `cp` to pull `../ctfd-live-scoreboard` into `frontend/` (exclude `node_modules`).
3. **Refactor Frontend**: 
   - Change `src/App.tsx` route from `/fantasy-ctf` to `/`.
   - Ensure `TavernBackground` and `Scoreboard` components are correctly linked.
4. **Draft Compose**: Create the production `docker-compose.yml` that includes CTFd and the consolidated challenge servers.
5. **Update Config**: Point `.ctf/config` to the future production endpoint.

---

## 📜 Metadata Reference
- **Challenges Root**: `./crypto`, `./prog`, `./llm`, `./osint`, `./rev`, `./misc`
- **CTFd Config**: `./.ctf/config`
- **Lore**: `./LORE.md`
