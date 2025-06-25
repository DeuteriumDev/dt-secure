#!make
SHELL:=/bin/bash

include .env
export $(shell sed 's/=.*//' .env)


install: ## instal deps & libs
	@asdf install
	@yarn set version stable
	@yarn install
.PHONY: install

tests: ## run the unit tests
	@yarn vitest
.PHONY: test

