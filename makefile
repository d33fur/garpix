SHELL := /bin/bash

.PHONY: all
all: rebuild start

.PHONY: build
build:
	@docker-compose build

.PHONY: rebuild
rebuild:
	@docker-compose build --force-rm

.PHONY: start
start:
	@docker-compose up -d

.PHONY: stop
stop:
	@docker-compose stop

.PHONY: restart
restart: stop start

.PHONY: logs
logs:
	@docker-compose logs -f --tail 100

.PHONY: clear
clear:
	@docker-compose kill  && \
	docker-compose rm -f 

.PHONY: db-cli
db-cli:
	@docker exec -it garpix_postgres psql -U useradmin -d gosts