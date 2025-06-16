.PHONY: build up down logs ps shell migrate collectstatic createsuperuser test

# Сборка контейнеров
build:
	docker-compose build

# Запуск всех сервисов
up:
	docker-compose up -d

# Остановка всех сервисов
down:
	docker-compose down

# Просмотр логов
logs:
	docker-compose logs -f

# Просмотр запущенных контейнеров
ps:
	docker-compose ps

# Запуск shell в контейнере web
shell:
	docker-compose exec web python myAfisha/manage.py shell

# Выполнение миграций
migrate:
	docker-compose exec web python myAfisha/manage.py migrate

# Сбор статических файлов
collectstatic:
	docker-compose exec web python myAfisha/manage.py collectstatic --no-input

# Создание суперпользователя
createsuperuser:
	docker-compose exec web python myAfisha/manage.py createsuperuser

# Запуск тестов
test:
	docker-compose exec web python myAfisha/manage.py test 