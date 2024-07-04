migrations:
    poetry run python manage.py makemigrations

migrate:
    poetry run python manage.py migrate

up:
    docker-compose up -d
