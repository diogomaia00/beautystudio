DC = docker-compose

.PHONY: run build down logs ps \
        migrate makemigrations shell seed seed-dev \
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

ps:
	$(DC) ps

# ── Django ─────────────────────────────────────────────────────────────────────
migrate:
	$(DC) exec backend python manage.py migrate

makemigrations:
	$(DC) exec backend python manage.py makemigrations

shell:
	$(DC) exec backend python manage.py shell

# ── Seed ───────────────────────────────────────────────────────────────────────
# Catalog + pricing only (idempotent; safe in any environment).
seed:
	$(DC) exec backend python manage.py seed_prices

# Full local dev dataset: catalog + admin + sample clients, schedules and
# appointments. Refuses to run unless DEBUG=True (see seed_dev).
seed-dev:
	$(DC) exec backend python manage.py seed_dev

# ── Tests ──────────────────────────────────────────────────────────────────────
test:
	$(DC) exec backend python manage.py test --settings=config.settings.test
	$(DC) exec frontend npm test -- --passWithNoTests

# ── Lint ───────────────────────────────────────────────────────────────────────
lint:
	$(DC) exec backend ruff check .
	$(DC) exec backend black --check .
	$(DC) exec frontend npm run lint

# ── Typecheck ───────────────────────────────────────────────────────────────────
typecheck:
	$(DC) exec frontend npm run type-check

# ── Zip ───────────────────────────────────────────────────────────────────────
zip:
	zip -r beautystudio.zip . -x '*/node_modules/*' '*/.next/*' '*/.swc/*' '*.tsbuildinfo' -x '*.DS_Store' '*/__pycache__/*' '*.pyc'

# ── Unzip ──────────────────────────────────────────────────────────────────────
unzip:
	unzip beautystudio.zip