.PHONY: verify verify-check format lint test type-check

# Default target
verify: format lint test type-check

# Check-only mode for CI
verify-check:
	poetry run ruff format --check route_listener tests
	poetry run ruff check --select I route_listener tests
	poetry run mypy route_listener tests
	poetry run pytest --log-level=WARNING
	poetry run ruff check route_listener tests

# Individual targets
format:
	poetry run ruff format route_listener tests

lint:
	poetry run ruff check route_listener tests

test:
	poetry run pytest --log-level=WARNING

type-check:
	poetry run mypy route_listener tests 