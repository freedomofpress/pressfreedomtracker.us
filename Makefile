.PHONY: ci-go
ci-go:
	./devops/scripts/go.sh

.PHONY: ci-tests
ci-tests:
	./devops/scripts/go.sh only_tests
