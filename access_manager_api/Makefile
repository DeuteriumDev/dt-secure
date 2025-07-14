#!make
SHELL:=/bin/bash

include .env
export $(shell sed 's/=.*//' .env)

DJANGO=poetry run python manage.py
DB_CONNECTION="postgresql://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@$(POSTGRES_HOST):$(POSTGRES_PORT)/$(POSTGRES_DB)"

help: ## Show this help
	@echo "\nSpecify a command. The choices are:\n"
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[0;36m%-12s\033[m %s\n", $$1, $$2}'
	@echo ""
.PHONY: help

install:
	@asdf install
	@poetry install
.PHONY: install


migrations: ## run all migrations
	@$(DJANGO) makemigrations accounts
	@$(DJANGO) makemigrations access_control
	@$(DJANGO) migrate
.PHONY: migrations

init: migrations ## add admin user and add remix application JWT keys, see [.env](./.env) for admin pass
	@$(DJANGO) createsuperuser --no-input --email admin@admin.ca
.PHONY: init

seed: migrations init ## add test user and supporting data
	@$(DJANGO) seed
.PHONY: seed

seed-only: ## add test user and supporting data
	@$(DJANGO) seed
.PHONY: seed-only

clean:
	rm -rf **/migrations
.PHONY: clean


reset: clean ## Reset connected db
	@echo "drop schema public cascade;drop schema $(POSTGRES_SCHEMA) cascade ; create schema public; create schema $(POSTGRES_SCHEMA)" | psql $(DB_CONNECTION)
.PHONY: reset

dev: ## run the development server
	$(DJANGO) runserver_plus localhost:$(PORT)
.PHONY: dev

schema: ## generate the OpenAPI schema
	@$(DJANGO) spectacular --color --file schema.yml
	@sed -i '' -e 's/\/\/{id}/\/{id}\//' schema.yml
	@node ../cli_installation_tool/node_modules/prettier/bin/prettier.cjs schema.yml --write
.PHONY: schema

shell:
	@$(DJANGO) shell_plus --ipython
.PHONY: shell

services: ## run the supporting docker containers
	@docker compose -f ./docker-compose.yml --env-file .env up
.PHONY: services


scheduler: ## needs services running
	@poetry run celery -A django_api beat -l INFO  --scheduler django_celery_beat.schedulers:DatabaseScheduler
.PHONY: scheduler


worker: ## needs services running
	@poetry run celery -A django_api worker -l INFO
.PHONY: worker

tests:
	@$(DJANGO) test -p "test*"
.PHONY: tests

urls:
	@$(DJANGO) show_urls
.PHONY: urls
