# PayLinker

## Описание задачи

Необходимо реализовать асинхронное веб-приложение в парадигме REST API. 

### Стек технологий:
- **База данных:** PostgreSQL
- **ORM:** SQLAlchemy
- **Веб-фреймворк:** Sanic
- **Контейнеризация:** Docker Compose

### Сущности:
1. **Пользователь**
2. **Администратор**
3. **Счет** - имеет баланс, привязан к пользователю
4. **Платеж (пополнение баланса)** - хранит уникальный идентификатор и сумму пополнения счета пользователя

### Функциональные требования:
#### Пользователь:
- Авторизация по email/password
- Получение данных о себе (id, email, full_name)
- Получение списка своих счетов и балансов
- Получение списка своих платежей

#### Администратор:
- Авторизация по email/password
- Получение данных о себе (id, email, full_name)
- Создание/Удаление/Обновление пользователя
- Получение списка пользователей и списка их счетов с балансами

### Работа с платежами:
Реализовать роут для обработки вебхука от сторонней платежной системы. Структура JSON-объекта:
- `transaction_id` - уникальный идентификатор транзакции в сторонней системе
- `account_id` - уникальный идентификатор счета пользователя
- `user_id` - уникальный идентификатор пользователя
- `amount` - сумма пополнения счета пользователя
- `signature` - подпись объекта

Подпись (`signature`) формируется через SHA256 хеш для строки, состоящей из конкатенации значений объекта в алфавитном порядке ключей и секретного ключа, хранящегося в конфигурации проекта (`{account_id}{amount}{transaction_id}{user_id}{secret_key}`).

Пример JSON:
```json
{
  "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
  "user_id": 1,
  "account_id": 1,
  "amount": 100,
  "signature": "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"
}
```

## Установка и запуск

#### Инструкции по запуску через Docker

1. Клонируйте репозиторий:

    ```bash
    git clone https://github.com/lolevan/PayLinker.git
    cd PayLinker
    ```

2. Запустите контейнеры:

    ```bash
    docker-compose up --build
    ```
3. Можете перейти в API: `http://localhost:8000/docs`

#### Инструкции по запуску без Docker

1. Клонируйте репозиторий:

    ```bash
    git clone https://github.com/lolevan/PayLinker.git
    cd PayLinker
    ```

2. Установите и активируйте виртуальное окружение:

    ```bash
    python -m venv venv
    source venv/Scripts/activate или source venv/bin/activate
    ```
3. Установите зависимости:

    ```bash
    pip install -r requirements.txt
    ```
4. Создайте файл .env с необходимыми переменными окружения:

    ```bash
    POSTGRES_DB=your_db
    POSTGRES_USER=your_user
    POSTGRES_PASSWORD=your_password
    SECRET_KEY=your_secret_key
    ```

5. Примените миграции для создания необходимых таблиц и данных:

    ```bash
    python app/migrations/001_initial.py
    ```
6. Запустите приложение:

    ```bash
    python main.py
    ```

## Тестовые учетные записи

- Тестовый пользователь:
  - Email: `user@example.com`
  - Пароль: `password`
- Тестовый администратор:
  - Email: `admin@example.com`
  - Пароль: `password`

# Тестирование API с помощью curl

### Авторизация и получение токена

#### Пользователь
```bash
curl -X POST http://localhost:8000/auth -H "Content-Type: application/json" -d '{
  "email": "user@example.com",
  "password": "password"
}'
```
#### Администратор
```bash
curl -X POST http://localhost:8000/auth -H "Content-Type: application/json" -d '{
  "email": "admin@example.com",
  "password": "password"
}'
```

#### Получение данных о себе
```bash
curl -X GET http://localhost:8000/user/{user_id} -H "Authorization: Bearer $USER_TOKEN"

```
#### Получение списка своих счетов и балансов
```bash
curl -X GET http://localhost:8000/user/{user_id}/accounts -H "Authorization: Bearer $USER_TOKEN"
```
#### Получение списка своих платежей
```bash
curl -X GET http://localhost:8000/user/{user_id}/transactions -H "Authorization: Bearer $USER_TOKEN"

```
#### Создание нового пользователя (Администратор)
```bash
curl -X POST http://localhost:8000/admin/user -H "Content-Type: application/json" -H "Authorization: Bearer $ADMIN_TOKEN" -d '{
  "email": "newuser@example.com",
  "password": "newpassword",
  "full_name": "New User"
}'
```

#### Обновление данных пользователя (Администратор)
```bash
curl -X PUT http://localhost:8000/admin/user/{user_id} -H "Content-Type: application/json" -H "Authorization: Bearer $ADMIN_TOKEN" -d '{
  "email": "updateduser@example.com",
  "password": "updatedpassword",
  "full_name": "Updated User"
}'
```
#### Удаление пользователя (Администратор)
```bash
curl -X DELETE http://localhost:8000/admin/user/{user_id} -H "Authorization: Bearer $ADMIN_TOKEN"
```
#### Получение списка пользователей (Администратор)
```bash
curl -X GET http://localhost:8000/admin/users -H "Authorization: Bearer $ADMIN_TOKEN"
```
#### Обработка вебхука
```bash
curl -X POST http://localhost:8000/webhook -H "Content-Type: application/json" -d '{
  "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
  "user_id": 7,
  "account_id": 7,
  "amount": 777,
  "signature": "c79e4b612abe012bd7c7f08db55a8a1e65c7c5a4a157fd3a6d5940b2c81a79d8"
}'
```

## Выполненные задачи

Все функциональные требования и задачи, указанные в тестовом задании, были выполнены, включая:

- Реализация асинхронного веб-приложения в парадигме REST API с использованием Sanic и SQLAlchemy.
- Настройка базы данных PostgreSQL и взаимодействие с ней через SQLAlchemy.
- Создание Docker Compose конфигурации для развертывания проекта, включающей сервисы для PostgreSQL и приложения.
- Реализация сущностей:
  - Пользователь
  - Администратор
  - Счет - имеет баланс, привязан к пользователю.
  - Платеж - хранит уникальный идентификатор и сумму пополнения счета пользователя.
- Функции для пользователя:
  - Авторизация по email/password.
  - Получение данных о себе (id, email, full_name).
  - Получение списка своих счетов и балансов.
  - Получение списка своих платежей.
- Функции для администратора
  - Авторизация по email/password.
  - Получение данных о себе (id, email, full_name).
  - Создание, удаление и обновление пользователя.
  - Получение списка пользователей и их счетов с балансами.
- Реализация маршрута для обработки вебхука:
  - Проверка подписи объекта.
  - Проверка существования счета у пользователя, создание счета при его отсутствии.
  - Сохранение транзакции в базе данных.
  - Начисление суммы транзакции на счет пользователя.

## Контакты

Для вопросов и предложений, пожалуйста, свяжитесь с нами по адресу: vanechka.nikitin.20044@gmail.com


































