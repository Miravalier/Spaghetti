.PHONY: all
all: backend

.PHONY: backend
backend:
	docker-compose down
	docker-compose up -d --build

.PHONY: create-admin
create-admin:
	docker-compose run --rm api ./create_admin.py admin
