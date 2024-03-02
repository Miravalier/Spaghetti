ADMIN_USERNAME ?= admin
ADMIN_PASSWORD ?= admin

.PHONY: all
all: backend

.PHONY: backend
backend:
	docker-compose down
	docker-compose up -d --build

.PHONY: create-admin
create-admin:
	docker-compose run --rm api ./admin_cli.py create-admin $(ADMIN_USERNAME) $(ADMIN_PASSWORD)

.PHONY: reset-admin
reset-admin:
	docker-compose run --rm api ./admin_cli.py reset-password $(ADMIN_USERNAME) $(ADMIN_PASSWORD)
