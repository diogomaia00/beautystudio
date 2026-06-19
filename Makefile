DC = docker-compose

.PHONY: run build down logs \
        migrate makemigrations shell \
        test lint

# ── Stack ──────────────────────────────────────────────────────────────────────

run:
	$(DC) up

build:
	$(DC) build

down:
	$(DC) down

logs:
	$(DC) logs -f

# ── Django ─────────────────────────────────────────────────────────────────────

migrate:
	$(DC) exec backend python manage.py migrate

makemigrations:
	$(DC) exec backend python manage.py makemigrations

shell:
	$(DC) exec backend python manage.py shell

# ── Tests ──────────────────────────────────────────────────────────────────────

test:
	$(DC) exec backend python manage.py test
	$(DC) exec frontend npm test -- --passWithNoTests

# ── Lint ───────────────────────────────────────────────────────────────────────

lint:
	$(DC) exec backend ruff check .
	$(DC) exec backend black --check .
	$(DC) exec frontend npm run lint
