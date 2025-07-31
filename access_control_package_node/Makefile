#!make
SHELL:=/bin/bash

include .env
export $(shell sed 's/=.*//' .env)

help: ## Show this help
	@echo "\nSpecify a command. The choices are:\n"
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[0;36m%-12s\033[m %s\n", $$1, $$2}'
	@echo ""
.PHONY: help

install: ## instal deps & libs
	@asdf install
	@yarn set version stable
	@yarn install
.PHONY: install

tests: ## run the unit tests
	@yarn vitest
.PHONY: test

clean: $(wildcard ./dist)
	@rm -rf dist

build: clean ## build the lib
	@yarn build
.PHONY: build
