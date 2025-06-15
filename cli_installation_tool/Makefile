#!make
SHELL:=/bin/bash

include .env
export $(shell sed 's/=.*//' .env)


install: ## instal deps & libs
	@yarn set version stable
	@yarn install
.PHONY: install

test: ## run the unit tests
	@echo "test this somehow..."
.PHONY: test