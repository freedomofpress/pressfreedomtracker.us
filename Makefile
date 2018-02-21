.DEFAULT_GOAL := help
DIR := ${CURDIR}
WHOAMI := ${USER}
RAND_PORT := ${RAND_PORT}

.PHONY: ci-go
ci-go: ## Stands up a prod like environment under one docker container
	@molecule test -s ci

.PHONY: ci-tests
ci-tests: ## Runs testinfra against a pre-running CI container (useful for debugging)
	@molecule verify -s ci

.PHONY: dev-go
dev-go: ## Spin-up developer environment with three docker containers
	./devops/scripts/dev.sh converge

.PHONY: dev-chownroot
dev-chownroot: ## Chown root owned files caused from previous root-run containers
	sudo find $(DIR) -user root -exec chown -Rv $(WHOAMI):$(WHOAMI) '{}' \;

.PHONY: dev-clean
dev-clean: ## Completely wipes all developer containers
	./devops/scripts/dev.sh destroy && rm -rf node_modules

.PHONY: dev-stop
dev-stop: ## Stops all running developer containers.
	./devops/scripts/dev.sh side-effect

.PHONY: dev-attach-node
dev-attach-node: ## Provide a read-only terminal to attach to node spin-up
	docker attach --sig-proxy=false pf_tracker_node

.PHONY: dev-attach-django
dev-attach-django: ## Provide a read-only terminal to attach to django spin-up
	docker attach --sig-proxy=false pf_tracker_django

.PHONY: dev-attach-postgresql
dev-attach-postgresql: ## Provide a read-only terminal to attach to django spin-up
	docker attach --sig-proxy=false pf_tracker_postgresql

.PHONY: dev-createdevdata
dev-createdevdata: ## Inject development data into the postgresql database
	docker exec -it pf_tracker_django bash -c "./manage.py createdevdata"

.PHONY: dev-test
dev-test: ## Run application tests inside container
	docker exec -it pf_tracker_django bash -c "./manage.py test --noinput --keepdb"

.PHONY: dev-sass-lint
dev-sass-lint: ## Runs sass-lint utility over the code-base
	./devops/scripts/dev-sasslint.sh

.PHONY: dev-import-db
dev-import-db: ## Imports a database dump from file named ./import.db
	docker exec -it pf_tracker_postgresql bash -c "cat /django/import.db | sed 's/OWNER\ TO\ [a-z]*/OWNER\ TO\ tracker/g' | psql trackerdb -U tracker &> /dev/null"

.PHONY: ci-devops-builder

ci-devops-builder: ## Creates a container base for CI (not normally needed)
	./devops/scripts/ci-django-build.sh

.PHONY: update-pip-dependencies
update-pip-dependencies: ## Uses pip-compile to update requirements.txt
# It is critical that we run pip-compile via the same Python version
# that we're generating requirements for, otherwise the versions may
# be resolved differently.
	docker run -v "$(DIR):/code" -it quay.io/freedomofpress/ci-python \
		bash -c 'pip install pip-tools && \
		pip-compile -U --no-header --output-file /code/requirements.txt /code/requirements.in && \
		pip-compile -U --no-header --output-file /code/dev-requirements.txt /code/requirements.in /code/dev-requirements.in'

# Update the developer-focused reqs for local dev, testing, and CI.
	pip-compile -U --no-header --output-file devops/requirements.txt devops/requirements.in

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

.PHONY: dev-save-db
dev-save-db: ## Save a snapshot of the database for the current git branch
	./devops/scripts/savedb.sh

.PHONY: safety
safety: ## Runs `safety check` to check python dependencies for vulnerabilities
	@for req_file in `find . -type f -name '*requirements.txt'`; do \
		echo "Checking file $$req_file" \
		&& safety check --full-report -r $$req_file \
		&& echo -e '\n' \
		|| exit 1; \
	done

.PHONY: dev-restore-db
dev-restore-db: ## Restore the most recent database snapshot for the current git branch
	./devops/scripts/restoredb.sh


