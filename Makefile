.PHONY: all
all: backend

.PHONY: backend
backend:
	docker-compose down
	docker-compose up -d --build

.PHONY: create-admin
create-admin:
	docker-compose run --rm api ./admin_cli.py create-admin admin admin

.PHONY: reset-admin
reset-admin:
	docker-compose run --rm api ./admin_cli.py reset-password admin admin
