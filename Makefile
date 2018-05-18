define docker-run =
	docker run --rm -ti \
		ores/ores-service
endef

build-image:
	docker build \
		-t ores/ores-service:latest \
		.

shell:
	$(docker-run) sh

pytest:
	$(docker-run) pytest
