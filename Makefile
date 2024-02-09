.PHONY: all
all: backend

.PHONY: backend
backend:
	docker-compose down
	docker-compose up -d --build
