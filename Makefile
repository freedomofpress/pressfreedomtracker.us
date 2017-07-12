.DEFAULT_GOAL := help

.PHONY: ci-go
ci-go:
	./devops/scripts/go.sh

.PHONY: ci-tests
ci-tests:
	./devops/scripts/go.sh only_tests

.PHONY: dev-go
dev-go:
	./devops/scripts/dev.sh

.PHONY: dev-killapp
dev-killapp:
	docker kill node postgresql django

.PHONY: dev-resetapp
dev-resetapp:
	docker rm -f node django; ./devops/scripts/dev.sh

.PHONY: dev-attach-node
dev-attach-node:
	docker attach --sig-proxy=false node

.PHONY: dev-attach-django
dev-attach-django:
	docker attach --sig-proxy=false django

.PHONY: dev-attach-postgresql
dev-attach-postgresql:
	docker attach --sig-proxy=false postgresql

.PHONY: dev-createdevdata
dev-createdevdata:
	docker exec -it django bash -c "./manage.py createdevdata"

.PHONY: dev-sass-lint
dev-sass-lint:
	./devops/scripts/dev-sasslint.sh

.PHONY: dev-import-db
dev-import-db:
	docker exec -it postgresql bash -c "cat /django/import.db | sed 's/OWNER\ TO\ [a-z]*/OWNER\ TO\ tracker/g' | psql trackerdb -U tracker &> /dev/null"

.PHONY: ci-devops-builder
ci-devops-builder:
	./devops/scripts/ci-django-build.sh

.PHONY: help
help:
	@cat devops/scripts/help

.PHONY: dev-save-db
dev-save-db:
	./devops/scripts/savedb.sh

.PHONY: dev-restore-db
dev-restore-db:
	./devops/scripts/restoredb.sh
