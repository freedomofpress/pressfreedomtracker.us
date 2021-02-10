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
	docker-compose exec django /bin/bash -ec \
		"coverage run --source='.' ./manage.py test --noinput --keepdb; \
		coverage html --skip-empty --omit='*/migrations/*.py,*/tests/*.py'; \
		coverage report -m --fail-under=85 --skip-empty --omit='*/migrations/*.py,*/tests/*.py'"

.PHONY: dev-jest-tests
dev-jest-tests: ## Run django tests against developer environment
	docker-compose exec node npm test

.PHONY: compile-pip-dependencies
compile-pip-dependencies: ## Uses pip-compile to update requirements.txt
# It is critical that we run pip-compile via the same Python version
# that we're generating requirements for, otherwise the versions may
# be resolved differently.
	docker run -v "$(DIR):/code" -w /code -it python:3.7-slim \
		bash -c 'apt-get update && apt-get install gcc -y && \
	pip install pip-tools && \
		pip-compile --generate-hashes --no-header --output-file requirements.txt requirements.in && \
		pip-compile --generate-hashes --no-header --allow-unsafe --output-file dev-requirements.txt dev-requirements.in'

.PHONY: upgrade-pip
upgrade-pip: ## Uses pip-compile to update requirements.txt for upgrading a specific package
# It is critical that we run pip-compile via the same Python version
# that we're generating requirements for, otherwise the versions may
# be resolved differently.
	docker run -v "$(DIR):/code" -w /code -it python:3.7-slim \
		bash -c 'apt-get update && apt-get install gcc -y && \
	pip install pip-tools && \
		pip-compile --generate-hashes --no-header --upgrade-package $(PACKAGE) --output-file requirements.txt requirements.in && \
		pip-compile --generate-hashes --no-header --allow-unsafe --upgrade-package $(PACKAGE) --output-file dev-requirements.txt dev-requirements.in'


.PHONY: update-pip-dev
update-pip-dev: ## Uses pip-compile to update dev-requirements.txt for upgrading a specific package
# It is critical that we run pip-compile via the same Python version
# that we're generating requirements for, otherwise the versions may
# be resolved differently.
	docker run -v "$(DIR):/code" -w /code -it python:3.7-slim \
		bash -c 'apt-get update && apt-get install gcc -y && \
	pip install pip-tools && \
		pip-compile --generate-hashes --no-header --allow-unsafe --upgrade-package $(PACKAGE) --output-file dev-requirements.txt dev-requirements.in'


.PHONY: upgrade-pip-tools
upgrade-pip-tools: ## Update the version of pip-tools used for other pip-related make commands
	docker run -v "$(DIR):/code" -w /code -it python:3.7-slim \
		bash -c 'pip install pip-tools && \
		pip-compile --generate-hashes --no-header --allow-unsafe --upgrade-package pip-tools --output-file pip-tools-requirements.txt pip-tools-requirements.in'


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

.PHONY: lint
lint: flake8

.PHONY: flake8
flake8: ## Runs flake8 linting in Python3 container.
	@docker run -v $(PWD):/code -w /code --name fpf_www_flake8 --rm \
			python:3.7-slim \
			bash -c "pip install -q flake8 && flake8"

.PHONY: check-migrations
check-migrations: ## Check for ungenerated migrations
	docker-compose exec -T django /bin/bash -c "./manage.py makemigrations --dry-run --check"

.PHONY: bandit
bandit: ## Runs bandit static code analysis in Python3 container.
	@docker run -it -v $(PWD):/code -w /code --name fpf_www_bandit --rm \
		python:3.7-slim \
		bash -c "pip install -q --upgrade bandit && bandit --recursive . -ll --exclude devops,node_modules,molecule,.venv"

.PHONY: npm-audit
npm-audit: ## Checks NodeJS NPM dependencies for vulnerabilities
	@docker-compose run --entrypoint "/bin/ash -c" node 'npm install && $$(npm bin)/npm-audit-plus --ignore 803'

.PHONY: ci-npm-audit
ci-npm-audit:
	@mkdir -p test-results # Creates necessary test-results folder
	@docker-compose run --entrypoint "/bin/ash -c" node 'npm ci && $$(npm bin)/npm-audit-plus --xml --ignore 803 > test-results/audit.xml'

.PHONY: safety
safety: ## Runs `safety check` to check python dependencies for vulnerabilities
# Upgrade safety to ensure we are using the latest version.
	pip install --upgrade safety && ./scripts/safety_check.py

.PHONY: prod-push
prod-push: ## Publishes prod container image to registry
	docker tag $(REMOTE_IMAGE):latest $(REMOTE_IMAGE):$(GIT_REV)-$(GIT_BR)
	docker push $(REMOTE_IMAGE):latest
	docker push $(REMOTE_IMAGE):$(GIT_REV)-$(GIT_BR)
