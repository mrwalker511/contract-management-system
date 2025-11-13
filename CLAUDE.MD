Overview
You are a coding agent working on an internal contract management platform. Only one agent codes per session/prompt, but all agents share a common repository. This document defines the rules, directory structure, and phased steps for building the platform with maximum reliability and compatibility.

Repository Structure
/
├── backend/   # API server, DB models, integrations (Python/Node)
├── frontend/  # React+TS UI, components, assets
├── shared/    # OpenAPI spec, type schemas, test data
├── docs/      # Markdown docs, agent logs, design
├── scripts/   # Setup, migration, helper scripts
├── CLAUDE.md  # These instructions

Process & Protocol
Before coding: Always pull the latest repository, read /shared API/type schemas, and check /docs/AGENT_LOG.md for last agent's notes.
Working: Only code in your assigned directory (backend/ or frontend/). Use documented APIs/types from /shared.
Testing: Every new feature or change must include tests. Only move to the next phase when all tests pass.
Documentation: Update /docs as you work, noting feature completion, breaking changes, and next-step instructions.
After coding: Commit your changes, add a log to /docs/AGENT_LOG.md describing what you did, push before the next session.

Phased Build Steps

Phase 1: Foundation & MVP
Backend
- Scaffold service in /backend/ (FastAPI/Express), PostgreSQL DB for Contracts, Users, Templates.
- JWT/RBAC authentication, CRUD APIs for main models.
- DocuSign API (signature initiation only).
- Commit OpenAPI spec to /shared.
- Write tests for all endpoints using Pytest/Jest.

Frontend
- Scaffold /frontend/ (React/TypeScript).
- Use Ant Design or Material UI for base views (dashboard, contract list, detail modals).
- Connect to backend via /shared OpenAPI spec.
- Implement user/session management.
- Test major user flows.

Phase 2: Collaboration & Notification
Backend
- Contract status, version history, audit logging.
- SMTP email notifications, Teams integration via MS Graph.
- Templates and external document upload.

Frontend
- Dashboard widgets for contract status, reminders.
- Notification popovers, Teams integration (indicator/alerts).
- Document upload & template selector.

Phase 3: Vector Search
Backend
- Integrate Milvus or Qdrant for vector contract storage/search.
- Semantic search API, clause comparison, embeddings migration.

Frontend
- Semantic/vector search UI.
- Doc comparison view, advanced filters.

Phase 4: AI/NLP Integration
Backend
- Endpoints for NLP clause/obligation extraction.
- Risk/suggestion outputs.

Frontend
- Annotate clauses, display AI banners/risk highlights.
- Toggle for AI features.

Collaboration Principles
- Document every change or decision in /docs/AGENT_LOG.md.
- All features must be backward-compatible unless updating both frontend and backend together.
- Use pinned dependencies, modular code, and type safety everywhere.
- Use semantic commit messages (e.g., feat(backend): add email notifications).

Proactive Agent Workflow
- Review repository (especially /shared and /docs) before coding.
- When making/changing an API, update /shared specs before any frontend work.
- Leave precise TODOs and comments for the next agent.
- Prefer explicit code and tests over implied behaviors.

Follow these instructions step by step, verify all tests before advancing, and prioritize clear documentation and compatibility.
