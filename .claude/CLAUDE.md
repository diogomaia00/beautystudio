# Claude Code Configuration — Beauty Studio

Beauty Studio is an aesthetic single-clinic booking web app plus a back office, built as a SaaS-ready monorepo. 
This file is the entry point; detailed rules live in `.claude/rules/`.

## Behavioral Rules

- NEVER implement something by guessing (logic or tech stack) — ask when unsure.
- NEVER commit secrets, credentials, or `.env` files.
- Follow the rule files in `.claude/rules/` (see index below) and keep them in sync when decisions change.
- Develop on feature/fix branches off `dev`, using Conventional Commits (see `rules/git.md`).
- When a feature/flow is finished, add/update its flow doc under `docs/flows/` (see `rules/flow-doc.md`).

## Guardrails (safety)

Hard rules — never violate these, even if asked:

- **Never** delete, drop, or truncate the **production** database or any production data, and never run destructive/irreversible DB operations (`DROP`, `TRUNCATE`, unscoped `DELETE`/`UPDATE`) against production.
- **Never** commit secrets, credentials, or `.env` files.
- **Never** force-push, delete branches, or rewrite shared history on `main`/`dev`.
- Treat real/production data as **read-only** unless explicitly authorized for a specific, scoped change.

Always **stop and ask for explicit confirmation** before any critical or hard-to-reverse change, including:

- schema or data migrations against a non-local database;
- deleting files, tables, or data, or bulk edits across many files;
- changing authentication, permissions, or secrets handling;
- deployment, infrastructure, or **major** dependency version changes.

When in doubt, prefer the reversible option, show the plan/diff first, and ask.

## Frontend topology reminders

The client app and BO are **one Next.js app** with `(client)`/`(bo)` route groups
(ADR 0005). Two consequences to keep in mind:

- **Code-split by route group.** Lean on route-level code-splitting and dynamic
  imports so back-office code never bloats the client bundle.
- **Shared blast radius.** It's a single deployable — a build error in the BO
  blocks shipping a client fix (and vice versa). Keep the build green before
  deploying.

## App-Specific Terms and Entities

Always use these exact terms — never "customer", "worker", "user" (in product copy), or other synonyms.

- **admin** — the developer with total app control.
- **staff** — workers who provide services and control their prices and services.
- **clients** — people who book appointments for a specific service at a specific date and time.

> "BO" = Back Office (the staff/admin app). See `rules/frontend.md`.

## Project Layout

This is a **monorepo** (`backend/`, `frontend/`, `infra/`). 
Do NOT use a flat `/src` layout at the repo root — source lives inside each package.

- `backend/` — Django + DRF + Procrastinate (see `rules/backend.md`)
- `frontend/` — Next.js client app + back office (see `rules/frontend.md`)
- `infra/` — NGINX, Postgres, scripts (see `rules/infrastructure.md`)

Within each package: tests live in a `tests/` dir, environment-specific configuration in `config/`, and documentation in `docs/`.

## Rules Index (`.claude/rules/`)

- `overview.md` — project goal, tech stack, monorepo root structure.
- `architecture.md` — architecture decisions + ADR process.
- `coding-standards.md` — backend/frontend coding standards.
- `naming-conventions.md` — code-level naming (Python, TS, DB, API, files).
- `ddd.md` — domain-driven design guidelines and layering.
- `database.md` — time-based scheduling data model and Postgres column types.
- `backend.md` — backend stack, app list, domain structure, REST practices.
- `frontend.md` — frontend structure, design system, BO app.
- `infrastructure.md` — Docker, NGINX, Makefile, deployment.
- `auth.md` — authentication and authorization.
- `business-rules.md` — booking limits, waitlist, scheduling, roadmap.
- `background-jobs.md` — background jobs and scheduled reports (Procrastinate).
- `git.md` — branching, Conventional Commits, git practices.
- `flow-doc.md` — per-feature PlantUML flow docs in `docs/flows/`.

## Development Roadmap

Dev tasks and their status live in `docs/roadmap.md`. 
When a task is built, tested, and merged:
    1. flip its Status to `developed` 
    2. create a `.puml` file in `docs\flows` (see `docs/flows/`).
Architecture decisions are recorded in `docs/adr/`.
