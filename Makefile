.PHONY: ops-aws-dockersetup
ops-aws-dockersetup:
	./devops/scripts/docker-aws-setup.sh

.PHONY: ops-localprod
ops-localprod:
	./devops/scripts/go.sh
