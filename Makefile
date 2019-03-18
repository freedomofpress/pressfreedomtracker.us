.DEFAULT_GOAL := help
DIR := ${CURDIR}
WHOAMI := ${USER}
UID := $(shell id -u)
RAND_PORT := ${RAND_PORT}
GIT_REV := $(shell git rev-parse HEAD | cut -c1-10)
GIT_BR := $(shell git rev-parse --abbrev-ref HEAD)
REMOTE_IMAGE := quay.io/freedomofpress/tracker.us

.PHONY: dev-init
dev-init: ## Initialize docker environment for developer workflow
	echo UID=$(UID) > .env

.PHONY: open-browser
open-browser: ## Opens a web-browser pointing to the compose env
	@./devops/scripts/browser-open.sh

.PHONY: dev-import-db
dev-import-db: ## Import a postgres export file located at import.db
	docker-compose exec -it postgresql bash -c "cat /django/import.db | sed 's/OWNER\ TO\ [a-z]*/OWNER\ TO\ postgres/g' | psql securedropdb -U postgres &> /dev/null"

.PHONY: save-db
dev-save-db: ## Export developer db to file
	./devops/scripts/savedb.sh

.PHONY: ci-go
ci-go: ## Stands up a prod like environment under one docker container
	@molecule test -s ci

.PHONY: ci-tests
ci-tests: ## Runs testinfra against a pre-running CI container (useful for debugging)
	@molecule verify -s ci

.PHONY: dev-tests
dev-tests: ## Run django tests against developer environment
	docker-compose exec django /bin/bash -c "./manage.py test --noinput --keepdb"

.PHONY: update-pip-dependencies
update-pip-dependencies: ## Uses pip-compile to update requirements.txt
# It is critical that we run pip-compile via the same Python version
# that we're generating requirements for, otherwise the versions may
# be resolved differently.
	docker run -v "$(DIR):/code" -it python:3.5-slim  \
		bash -c 'pip install pip-tools && apt-get update && apt-get install git -y && \
		pip-compile -U --no-header --output-file /code/requirements.txt /code/requirements.in && \
		pip-compile -U --no-header --output-file /code/dev-requirements.txt /code/dev-requirements.in'

# Explanation of the below shell command should it ever break.
# 1. Set the field separator to ": ##" to parse lines for make targets.
# 2. Check for second field matching, skip otherwise.
# 3. Print fields 1 and 2 with colorized output.
# 4. Sort the list of make targets alphabetically
# 5. Format columns with colon as delimiter.
.PHONY: help
help: ## Prints this message and exits
	@printf "Makefile for developing and testing Secure The News.\n"
	@printf "Subcommands:\n\n"
	@perl -F':\s+##\s+' -lanE '$$F[1] and say "\033[36m$$F[0]\033[0m : $$F[1]"' $(MAKEFILE_LIST) \
		| sort \
		| column -s ':' -t

.PHONY: flake8
flake8: ## Runs flake8 linting in Python3 container.
	@docker run -v $(PWD):/code -w /code --name fpf_www_flake8 --rm \
			python:3.5-slim \
			bash -c "pip install -q flake8 && flake8"

.PHONY: bandit
bandit: ## Runs bandit static code analysis in Python3 container.
	@docker run -it -v $(PWD):/code -w /code --name fpf_www_bandit --rm \
		python:3.5-slim \
		bash -c "pip install -q --upgrade bandit && bandit --recursive . -ll --exclude devops,node_modules,molecule,.venv"

.PHONY: safety
safety: ## Runs `safety check` to check python dependencies for vulnerabilities
	pip install --upgrade safety && \
		for req_file in `find . -type f -name '*requirements.txt'`; do \
			echo "Checking file $$req_file" \
			&& safety check --full-report -r $$req_file \
			&& echo -e '\n' \
			|| exit 1; \
		done

.PHONY: prod-push
prod-push: ## Publishes prod container image to registry
	docker tag $(REMOTE_IMAGE):latest $(REMOTE_IMAGE):$(GIT_REV)-$(GIT_BR)
	docker push $(REMOTE_IMAGE):latest
	docker push $(REMOTE_IMAGE):$(GIT_REV)-$(GIT_BR)
