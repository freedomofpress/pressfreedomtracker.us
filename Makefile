.PHONY: ops-aws-dockersetup
ops-aws-dockersetup:
	./devops/scripts/docker-aws-setup.sh

.PHONY: ops-aws-docker-ssh
ops-aws-docker-ssh:
	docker-machine ssh aws-sandbox-${USER}

.PHONY: ops-aws-docker-forward
ops-aws-docker-forward:
	docker-machine ssh aws-sandbox-${USER} -NL 4443:aws-sandbox-${USER}:4443

.PHONY: ops-localprod
ops-localprod:
	./devops/scripts/go.sh
