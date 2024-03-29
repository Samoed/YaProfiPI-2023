# https://github.com/samuelcolvin/pydantic/blob/master/Makefile
.DEFAULT_GOAL := all
isort = isort src/
black = black src/
mypy = mypy src/
flake8  = flake8 src/
pyupgrade = pyupgrade --py310-plus

.PHONY: install-linting
install-linting:
	poetry add flake8 black isort mypy pyupgrade -G dev

.PHONY: install
install: install-linting
	pre-commit install
	@echo 'installed development requirements'

.PHONY: lint
lint: install-linting
	$(isort) --df --check-only
	$(black) --diff --check
	$(flake8)

.PHONY: format
format:
	$(pyupgrade)
	$(isort)
	$(black)
	# $(mypy)
	$(flake8)

.PHONY: export-dependencies
export-dependencies:
	poetry export -f requirements.txt --output requirements/requirements.txt
	poetry export -f requirements.txt --output requirements/requirements-dev.txt --with=dev
	poetry export -f requirements.txt --output requirements/requirements-test.txt --with=dev --with=test

.PHONY: database
database:
	docker run --name postgresql -e POSTGRES_USER=myusername -e POSTGRES_PASSWORD=mypassword -p 5432:5432 -d postgres

.PHONY: test
test:
	docker compose -f docker-compose.test.yaml up --build

.PHONY: migrate
migrate:
	python -m alembic revision --autogenerate

.PHONY: downgrade
downgrade:
	python -m alembic downgrade -1

.PHONY: upgrade
upgrade:
	python -m alembic upgrade +1

.PHONY: all
all: format export-dependencies
