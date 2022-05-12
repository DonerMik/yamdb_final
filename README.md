REST API для сервиса YaMDb — базы отзывов о фильмах, книгах и музыке.REST API для сервиса YaMDb — базы отзывов о фильмах, книгах и музыке.
1) http://51.250.29.12/api/v1/
2) http://51.250.29.12/admin
3) http://51.250.29.12/redoc
В данном проекте использовались след. технологии docker, django, django restframework

Структура файла .env:

DB_ENGINE - используемая база данных DB_NAME - название базы данных POSTGRES_USER - пользователь POSTGRES_PASSWORD - пароль DB_HOST - БД xост DB_PORT - БД порт

НАСТРОЙКА ПРОЕКТА:

Запуск проекта:

1)Клонировать репозиторий и перейти в него в командной строке:

git clone https://github.com/account_name/api_yamdb/

cd api_yamdb

2)запустите команду в корне проекта: docker-compose up -d --build 3)Выполнить следующие команды:

docker-compose exec web python manage.py migrate docker-compose exec web python manage.py createsuperuser docker-compose exec web python manage.py collectstatic --no-input

ПРОЕКТ ЗАПУЩЕН по адресу http://127.0.0.1:8000/redoс/

Отключение сервиса : docker-compose down -v

Автор: Микутайтис Денис. Почта: denismik92@gmail.com
![example workflow](https://github.com/DonerMik/yamdb_final/actions/workflows/yamdb_workflow/badge.svg)
