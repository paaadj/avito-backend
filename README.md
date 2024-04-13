# Руководство запуска
0. Склонируйте репозиторий:
    ```bash
    git clone https://github.com/paaadj/avito-backend.git
    cd avito-backend
    ```
## Запуск проекта через Docker
1. Установите Docker, если он еще не установлен на Вашем компьютере.
2. Соберите и запустите контейнеры Docker:
   ```bash
   docker-compose up --build
   ```
3. После успешного запуска контейнеров, сервис будет доступен по адресу http://localhost:8000
4. Для проверки работоспособности сервиса,  по адресу http://localhost:8000/docs, доступен интерфейс
Swagger для ручного тестирования API

## Запуск проекта вручную
Если Вы хотите выполнить запуск проекта без использования Docker, то следуйте следующим шагам:

1. Убедитесь, что у Вас установлен Python 3.11+ и pip, PostgreSQL, Redis
2. Создайте виртуальное окружение(опционально):
```bash
python -m venv venv
source venv/bin/activate  # для Unix/Mac
venv/Scripts/activate     # для Windows
```
3. Установите зависимости:
```bash
pip install -r req.txt
```
4. Установите PostgreSQL и Redis на Ваш компьютер, если еще не установлены и запустите их.
5. Создайте базу данных Postgre с названием "avito-test".
6. Запустите обработчика Celery задач:
```bash
celery -A services.celery_tasks.celery worker —loglevel=info -P eventlet
```
7. Запустите интерфейс Celery(опционально):
```bash
celery -A services.celery_tasks.celery flower —port=5555
```
8. Запустите сервер приложения:
```bash
python app.py
```
9. Сервис доступен по адресу http://localhost:8000.
Для проверки работоспособности сервиса,  по адресу http://localhost:8000/docs, доступен интерфейс
Swagger для ручного тестирования API. Если вы выполнили п.7, то интерфейс с Celery задачами будет доступен по адресу 
http://localhost:5555  


# Вопросы
1. Написано, что тег и фича представляют собой число, и больше про их структуру ничего не сказано, поэтому я оставил просто как число, так как в API, кроме как с их ID мы никак не взаимодействуем
2. Написано, что фича и тег однозначно определяют баннер, но не сказано как должна вести себя программа при попытке добавить или обновить баннер так, что это определение нарушится. 
Я сделал проверку, что мы добавляем или обновляем баннер и он не нарушит это условие, если нарушает, то возвращается статус 400
3. На всякий случай добавил методы создания тегов, фич и регистрацию администратора, если кто-то решит проверить работоспособность в ручную :)

# Условие 5
Сделано с помощью Redis, ответ о баннере заносится в кеш и при дальнейшем запросе по этому же адресу
проверяется наличией информации в кеше, если она есть, то сразу отдается (если, конечно, use_last_revision=false)

# Доп.задания 
2. Провел нагрузочное тестирование с помощью Locust, через время, когда большая часть данных закешировалась, при RPS=500, время ответа=34. <br>
Также провел тестирование для запросов по случайным тегам и фичам, где получил такой результат:
<img src="/media/stress_test.jpg">
Из-за того что теги и фичи случайные процент Failures большой, так как я не создавал слишком много баннеров<br>
4. Для решения этой задачи, сервис использует Celery, пользователь отправляет запрос на удаление по фиче или тегу и 
направляет задачу в асинхронную очередь, где уже обрабатывается удаление баннеров
5. Добавил тесты остальных сценариев в файле /test/test_admin_banner <br>
6. Конфигурация линтера в файле .flake8


# Примеры запросов
### Создание баннера
#### Запрос
```curl
curl -X 'POST' \
  'http://127.0.0.1:8000/banner' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InVzZXJuYW1lIiwiaXNfYWRtaW4iOnRydWV9.2QC1JT0iRTnGHUyRxOcUfGXPzecy8kb_m-CoTp65iLA' \
  -H 'Content-Type: application/json' \
  -d '{
  "tag_ids": [
    1
  ],
  "feature_id": 1,
  "content": {"title": "some_title", "text": "some_text", "url": "some_url"},
  "is_active": true
}'
```
#### Успешный Ответ
```http
HTTP 200 OK
{
  "banner_id": 1
}
```

#### Ответы с ошибкой

```http
HTTP 403 FORBIDDEN
{
    "detail": "Not authenticated"
}
```

```http
HTTP 400 BAD REQUEST
{
    "detail": "Некорректные данные."
}
```

### Получение баннера
#### Запрос
```curl
curl -X 'GET' \
  'http://127.0.0.1:8000/user_banner?tag_id=1&feature_id=1&use_last_revision=false' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InVzZXJuYW1lIiwiaXNfYWRtaW4iOnRydWV9.2QC1JT0iRTnGHUyRxOcUfGXPzecy8kb_m-CoTp65iLA'
```

#### Ответ
```http
{
  "content": {
    "title": "some_title",
    "text": "some_text",
    "url": "some_url"
  }
}
```
