.PHONY: build-image shell pytest

docker-run = docker run --rm -ti -p 8080:8080 ores/ores-service

build-image:
	docker build \
		-t ores/ores-service:latest \
		.

shell:
	$(docker-run) sh

pytest:
	$(docker-run) pytest
