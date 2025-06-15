#### MISC ####

.PHONY: fix-imports
fix-imports:
	@uv run isort .

.PHONY: export-requirements
export-requirements:
	@uv export --no-hashes --no-header --no-annotate --no-dev --format requirements-txt > requirements.txt

.PHONY: setup-local
setup-local:
	@docker compose up -d --wait

.PHONY: stop-local
stop-local:
	@docker compose down --remove-orphans

.PHONY: run-app
run-app: setup-local migration-up
	@uv sync --locked --all-extras --dev
	@uv run uvicorn caipyra_ledger.main:app --host 0.0.0.0 --port 8000

#### TESTS ####

.PHONY: test-lint
test-lint:
	@uv tool run ruff check

.PHONY: test-typing
test-typing:
	@uv run mypy caipyra_ledger

.PHONY: test
test: test-lint test-typing

#### MIGRATION ####

.PHONY: migration-create
migration-create:
	@uv run alembic revision --autogenerate -m "$(MESSAGE)"

.PHONY: migration-up
migration-up:
	@uv run alembic upgrade head

.PHONY: migration-down
migration-down:
	@uv run alembic downgrade base
