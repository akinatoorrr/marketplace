# marketplace

## Установка и запуск

1. **Клонируйте репозиторий**:

```bash
git clone https://github.com/akinatoorrr/marketplace.git
cd marketplace
```

2. **Создайте `.env` файлы** (на примере шаблонов из репозитория)

3. **Запустите проект в Docker**:

```bash
make build   # Сборка контейнеров
make up      # Запуск в фоне
```

4. **Доступ к API**:
- Приложение будет доступно по адресу: `http://localhost:8000`
- Swagger-документация: `http://localhost:8000/docs`

5. **Создайте бакет для хранения файлов в MinIO**

---

## Тестирование

- Запуск тестов:

```bash
make tests
```

- Покрытие кода:

```bash
make test-cov
```

---

## Эндпойнты API

> Все эндпойнты, кроме `/auth/*` требуют авторизации (JWT access_token в cookie `users_access_token`)

### 🔐 Auth

#### `POST /auth/register/`
Регистрация пользователя.

**Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{ "message": "Вы успешно зарегистрированы!" }
```

---

#### `POST /auth/login/`
Авторизация пользователя, установка access_token в cookie.

**Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "access_token": "JWT",
  "refresh_token": null
}
```

---

#### `POST /auth/logout/`
Удаление access_token из cookie.

---

### 📝 Posts

> Требуется авторизация

#### `GET /posts/`
Получение списка статей.

**Query-параметры (опционально):**
- `search`: строка поиска
- `category_id`: фильтр по категории
- `page_size`: размер страницы
- `page_number`: номер страницы

**Response:**
```json
[
  {
    "id": 1,
    "title": "Пример статьи",
    "text": "Содержимое статьи...",
    "category_id": 2,
    ...
  }
]
```

---

#### `POST /posts/`
Создание новой статьи с возможной загрузкой изображения.

**Form-data:**
- `title`: string
- `text`: string
- `category_id`: int
- `image`: файл (опционально)

---

#### `PUT /posts/{post_id}`
Редактирование статьи.

**Body:**
```json
{
  "title": "Новое название",
  "text": "Обновлённый текст"
}
```

---

#### `DELETE /posts/{post_id}`
Удаление статьи (soft delete).

---

### 📂 Categories

> Требуется авторизация

#### `GET /categories/`
Получение списка категорий.

**Query-параметры:** `page_size`, `page_number`

---

#### `POST /categories/`
Создание новой категории.

**Body:**
```json
{
  "title": "Название категории"
}
```
