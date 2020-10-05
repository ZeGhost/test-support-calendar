


docker-build: docker-clean
	docker build --tag test-support-calendar:latest .
.PHONY: docker-build

docker-clean:
	docker image rm test-support-calendar --force
.PHONY: docker-clean

docker-run:
	docker run test-support-calendar:latest
.PHONY: docker-run

docker-sh:
	docker run -it --mount type=bind,src=`pwd`,dst=/app test-support-calendar bash
.PHONY: docker-sh