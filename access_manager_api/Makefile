#!make
SHELL:=/bin/bash

include .env
export $(shell sed 's/=.*//' .env)

DJANGO=poetry run python manage.py

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

init: ## add admin user and add remix application JWT keys, see [.env](./.env) for admin pass
	@$(DJANGO) createsuperuser --no-input --email admin@admin.ca
	@$(DJANGO) createapplication --client-id $(CLIENT_ID) --client-secret $(CLIENT_SECRET) --algorithm HS256 --name remix_frontend confidential password
.PHONY: init

seed: migrations init ## add test user and supporting data
	@$(DJANGO) seed
	@$(DJANGO) createinitialrevisions
.PHONY: seed

dev: ## run the development server
	@$(DJANGO) runserver
.PHONY: dev

schema: ## generate the OpenAPI schema
	@$(DJANGO) spectacular --color --file schema.yml
	@node ../remix_frontend/node_modules/prettier/bin/prettier.cjs schema.yml --write
.PHONy: schema

shell:
	@$(DJANGO) shell
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


revisions: 
	@$(DJANGO) createinitialrevisions
.PHONY: revisions

DB_CONNECTION="postgresql://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@$(POSTGRES_HOST):$(POSTGRES_PORT)/$(POSTGRES_DB)"
reset: ## Reset connected db
	@echo "drop schema public cascade; create schema public;" | psql $(DB_CONNECTION)
.PHONY: reset

tests:
	@$(DJANGO) test -p "test*"
.PHONY: tests