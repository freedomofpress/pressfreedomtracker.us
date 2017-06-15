.PHONY: ci-go
ci-go:
	./devops/scripts/go.sh

.PHONY: ci-tests
ci-tests:
	./devops/scripts/go.sh only_tests

.PHONY: dev-go
dev-go:
	./devops/scripts/dev.sh

.PHONY: dev-stop
dev-stop:
	docker kill node postgresql django

.PHONY: dev-attach-node
dev-attach-node:
	docker attach --sig-proxy=false node

.PHONY: dev-attach-django
dev-attach-django:
	docker attach --sig-proxy=false django

.PHONY: dev-attach-postgresql
dev-attach-postgresql:
	docker attach --sig-proxy=false postgresql

.PHONY: dev-sass-lint
dev-sass-lint:
	bash -c ". ./.docker_versions && docker run -it -v \"${PWD}:/lintme\" -w /lintme \"quay.io/freedomofpress/sasslinter@sha256:${SASSLINT_VER}\""

.PHONY: dev-import-db
dev-import-db:
	docker exec -it postgresql bash -c "cat /django/import.db | sed 's/OWNER\ TO\ [a-z]*/OWNER\ TO\ tracker/g' | psql trackerdb -U tracker &> /dev/null"

.PHONY: ci-devops-builder
ci-devops-builder:
	./devops/scripts/ci-django-build.sh
