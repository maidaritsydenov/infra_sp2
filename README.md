
### Описание
API сервиса Yamdb. Позволяет читать и добавлять отзывы о различных произведениях искусства: книгах, фильмах, музыке и не только.
Дает вызможность выставлять рейтинг произведениям и смотреть их текущий рейтинг на данном ресурсе.
Спсисок произведений расширяется администраторами.

### Технологии
- Python 3.7
- django 2.2.16
- PostgreSQL 13.0-alpine
- Nginx 1.21.3-alpine
- Docker version 20.10.21, build baeda1f
- Docker Compose version v2.12.2
- djangorestframework==3.12.4
- djangorestframework-simplejwt==5.2.0
- django-filter 21.1


### Запуск проекта в dev-режиме Docker-Compose:
1. В директории /infra_sp2/infra/ создайте файл .env. Добавьте в нее переменные окружения:
```
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
```
2. Разверните контейнеры Docker-compose:

- Для запуска необходимо выполнить команду из директории с файлом docker-compose.yaml:
``` docker-compose up ```

- Для пересборки контейнеров:
``` docker-compose up -d --build ```

3. Теперь в контейнере web нужно выполнить миграции, создать суперпользователя и собрать статику.
Выполните по очереди команды:
``` docker-compose exec web python manage.py migrate ```
``` docker-compose exec web python manage.py createsuperuser ```
``` docker-compose exec web python manage.py collectstatic --no-input ```

4. Следующим шагом создайте дамп (резервную копию) базы:
``` docker-compose exec web python manage.py dumpdata > fixtures.json ```

5. Теперь проект доступен по адресу http://localhost/


### Некоторые полезные команды:
- Локально создать образ с нужным названием и тегом:
``` docker build -t <username>/<imagename>:<tag> . ```

- Авторизоваться через консоль:
``` docker login ```

- А можно сразу указать имя пользователя
``` docker login -u <username> ```

- Запушить образ на DockerHub:
``` docker push <username>/<imagename>:<tag> ```

- Остановка всех контейнеров:
``` sudo docker-compose down ```

- Мониторинг запущенных контейнеров:
``` sudo docker stats ```

- Остановить и удалить все контейнеры со всеми зависимостями. Оставить только образы:
``` sudo docker-compose down -v ```

- Остановить проект сохранив данные в БД:
``` docker-compose down ```

- Остановить проект удалив данные в БД:
``` docker-compose down --volumes ```

- Удалить всё, что не используется (неиспользуемые образы, остановленные контейнеры, тома, которые не использует ни один контейнер, билд-кеш)
``` sudo docker system prune ```



### Запуск проекта в dev-режиме:
- Установите и активируйте виртуальное окружение
- Установите зависимости из файла requirements.txt
``` pip install -r requirements.txt ```

- Выполните миграции. В папке с файлом manage.py выполните команду:
``` python3.manage.py migtate (windows: py.manage.py migtate) ```

- Перенесите в базу данных тестовые данные из csv файлов, используя команду
``` python3.manage.py db_filling (windows: py.manage.py db_filling) ```

- Запустите сервер разработчика. В папке с файлом manage.py выполните команду:
``` python3 manage.py runserver (windows: py manage.py runserver) ```


### Администрирование и особенности
- Для администрирования проекта создайте суперпользователя. В папке с файлом manage.py выполните команду:
``` python3 manage.py createsuperuser (windows: py manage.py createsuperuser) ```

- Админ-зона расположена по относительному адреу /admin/
- Добавлений новых произведений (titles) доступно только суперпользователю и администраторам


### Работа с API
- Зарегистрируйте нового пользователя отправив post запрос на относительный эндпоинт api/v1/auth/signup/. В теле post запроса передайте параметры "username" и "email".
- На переданный email вы получите confirmation_code.
- Получите токен для пользователя отправив post запрос на относительный эндпоинт api/v1/auth/token/, передав username и confirmation_code.
```
curl --location --request POST 'http://127.0.0.1:8000/api/v1/auth/token/' \
--header 'Content-Type: application/json' \
--data-raw '{
    "username": "newuser",
    "confirmation_code": "****"
}'
```
- Примеры запросов для получения списка произведений/информации о конкретном произведении
```
curl --location --request GET 'http://127.0.0.1:8000/api/v1/titles/' \
--header 'Authorization: Bearer <ваш токен>' \
--data-raw ''
```
```
curl --location --request GET 'http://127.0.0.1:8000/api/v1/titles/1/' \
--header 'Authorization: Bearer <ваш токен>' \
--data-raw ''
```
- Пример post запроса для оставления отзыва о произведении
```
curl --location --request POST 'http://127.0.0.1:8000/api/v1/titles/1/review/' \
--header 'Authorization: Bearer <ваш токен>' \
--header 'Content-Type: application/json' \
--data-raw '{
    "text": "замечательное произведение",
    "score": 10
}'
```
- Полный список возможных эндпоинтов и видов запросов доступен по относительному эндпоинту redoc/

### Авторы в алфавитном порядке:
- Дмитрий Вдонин (Reviews, Comments)
- Дмитрий Мисюра (Регистрация и аутентификация, работа с токеном, e-mail подтверждение)
- Майдари Цыденов (Categories, Genres, Titles)
