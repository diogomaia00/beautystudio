# CODING STANDARDS

General code-quality rules for both packages. Naming lives in
`naming-conventions.md`; API-design rules in `backend.md`; layering in `ddd.md`.

## Cross-cutting principles

- Prefer clarity over cleverness; keep functions small and single-purpose.
- No dead code, commented-out blocks, or unused imports in committed code.
- Fail loudly: validate inputs at boundaries, never swallow exceptions silently.
- Keep business logic out of the framework edges (views, components).
- Every non-trivial change ships with tests (see `testing-strategy`).
- No secrets in code — use environment variables (see `infrastructure.md`).

## Backend (Python / Django / DRF)

### Style & tooling
- Target the Python version pinned in `requirements/base.txt`.
- Formatter: **Black**. Import sorting: **isort**. Linter: **Ruff** (or
  flake8). Type checking: **mypy** where practical.
- Follow PEP 8; max line length per Black default (88).
- Add type hints to function signatures and public functions.

### Django / DRF
- Reads through `selectors.py`, writes/business logic through `services.py`
  (see `ddd.md`). Views stay thin.
- Validate all input in serializers; never trust request data in views.
- Use `select_related` / `prefetch_related` to avoid N+1 queries.
- Wrap multi-step mutations in `transaction.atomic()` (booking, batches).
- Add DB indexes for fields used in filters/lookups; write explicit migrations.
- Never import another app's models directly — go through its service/selector.
- Keep migrations reviewed and reversible.

### Errors & logging
- Use DRF exception handling for consistent error envelopes and status codes.
- Define standard error codes/messages; don't leak internals to clients.
- Use structured logging with a request correlation ID across the workflow.
- Background tasks (Procrastinate): define explicit retry/timeout policies; make them idempotent.

## Frontend (TypeScript / Next.js / React)

### Style & tooling
- **TypeScript strict mode** on; avoid `any` (use `unknown` + narrowing).
- Formatter: **Prettier**. Linter: **ESLint** (Next.js config).
- Functional components with hooks only; no class components.

### Patterns
- Feature-based structure (see `frontend.md`): components, hooks, api client,
  containers per feature.
- Server state via **TanStack Query**; do not duplicate it in local state.
- All API calls go through the feature's `api.ts` / shared `lib/api.ts` —
  no inline `fetch` scattered in components.
- Co-locate component, its hooks, and styles; keep presentational and
  container concerns separated.
- Follow the design system tokens in `frontend.md` (spacing, colors, type).
- Handle loading, empty, error, and success states for every data view.

### Accessibility
- Semantic HTML, keyboard navigation, visible focus states, sufficient
  contrast, and adequate touch-target sizes (see `frontend.md`).

## Testing (summary)

- Backend: unit tests for services/selectors; integration tests for endpoints.
- Frontend: component tests for UI logic; integration tests for feature flows.
- API: a version-controlled **Bruno** collection (`.bru`) under
  `backend/tests/bruno/`, kept in sync with the documented endpoints (see
  `backend.md`). It complements — does not replace — DRF tests in CI.
- See the `engineering:testing-strategy` skill for designing test plans.

## Review & dependencies

- All changes go through PR review (see `git.md`).
- Keep PRs focused and small; one logical change per commit.
- Audit and update dependencies regularly; pin versions.
