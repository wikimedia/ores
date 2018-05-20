.PHONY: build-image run shell stop test

docker-run = docker-compose run --rm --no-deps ores

build-image:
	docker build \
		-t ores/ores:latest \
		.

run:
	docker-compose up

shell:
	$(docker-run) sh

stop:
	docker-compose down --remove-orphans

test:
	$(docker-run) pytest
