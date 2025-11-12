Makefile para atajos de desarrollo

Definición de variables

PROJECT_NAME := fastapi-single-service

--- Comandos Principales de Docker Compose ---

.PHONY: build
build: ## Construye las imágenes de Docker (API y DB)
docker compose build

.PHONY: up
up: build ## Levanta todos los servicios en modo detached (background)
docker compose up -d

.PHONY: down
down: ## Detiene y elimina los contenedores, redes y volúmenes (si se usa --volumes)
docker compose down

.PHONY: logs
logs: ## Muestra los logs de todos los contenedores
docker compose logs -f

--- Comandos para Pruebas ---

.PHONY: test
test: ## Ejecuta las pruebas Pytest dentro del contenedor 'api'
# Se usa el contenedor 'api' ya que tiene todas las dependencias instaladas.
# Se pasan variables de entorno de prueba para usar SQLite en memoria en lugar de Postgres.
docker compose run --rm api 

pytest /app/app/tests/

--- Otros Comandos Útiles ---

.PHONY: shell
shell: ## Abre un shell bash interactivo en el contenedor de la API
docker compose exec api bash

.PHONY: help
help: ## Muestra este mensaje de ayuda
@grep -E '^[a-zA-Z_-]+:.?## .$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-10s\033[0m %s\n", $$1, $$2}'