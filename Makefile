.DEFAULT_GOAL := help

.PHONY: ci-go
ci-go:
	@molecule test -s ci

.PHONY: ci-tests
ci-tests:
	@molecule verify -s ci

.PHONY: dev-go
dev-go:
	./devops/scripts/dev.sh

.PHONY: dev-killapp
dev-killapp:
	docker kill pf_tracker_node pf_tracker_postgresql pf_tracker_django

.PHONY: dev-resetapp
dev-resetapp:
	molecule converge -s dev

.PHONY: dev-attach-node
dev-attach-node:
	docker attach --sig-proxy=false pf_tracker_node

.PHONY: dev-attach-django
dev-attach-django:
	docker attach --sig-proxy=false pf_tracker_django

.PHONY: dev-attach-postgresql
dev-attach-postgresql:
	docker attach --sig-proxy=false pf_tracker_postgresql

.PHONY: dev-createdevdata
dev-createdevdata:
	docker exec -it pf_tracker_django bash -c "./manage.py createdevdata"

.PHONY: dev-sass-lint
dev-sass-lint:
	./devops/scripts/dev-sasslint.sh

.PHONY: dev-import-db
dev-import-db:
	docker exec -it pf_tracker_postgresql bash -c "cat /django/import.db | sed 's/OWNER\ TO\ [a-z]*/OWNER\ TO\ tracker/g' | psql trackerdb -U tracker &> /dev/null"

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
