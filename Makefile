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
	docker run -it -v "${PWD}:/lintme" -w /lintme quay.io/freedomofpress/sasslinter
