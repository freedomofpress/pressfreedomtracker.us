.PHONY: ops-aws-dockersetup
ops-aws-dockersetup:
	./devops/docker-aws-setup.sh

.PHONY: ops-localprod
ops-localprod:
	./devops/go.sh
