# Garpix

Этот проект был разработан нашей командой в рамках практики. Целью было создать веб-приложение для нормоконтроля технических документов. Мы использовали Python, Streamlit для фронтенда и FastAPI для бэкенда, а также базу данных PostgreSQL для хранения данных.

Здесь можно посмотреть как работают ~~[основной сервис](http://85.92.110.57:8501/) и [админка](http://85.92.110.57:8502/)~~(уже не работают), но можно поднять самим по инструкцие в [Начало работы](#начало-работы).

## Содержание

- [Функционал](#функционал)
  - [Основной сайт](#основной-сайт)
  - [Админка](#админка)
- [Начало работы](#начало-работы)
  - [Требования](#требования)
  - [Установка](#установка)
  - [Запуск проекта](#запуск-проекта)
- [Использование админки](#использование-админки)
- [API Эндпоинты](#api-эндпоинты)

## Функционал

### Основной сайт

- Проверка загруженных файлов на соответствие ГОСТам

### Админка

- Просмотр всех ГОСТов
- Добавление новых ГОСТов
- Удаление существующих ГОСТов

## Начало работы

### Требования

- docker
- docker-compose
- make

### Установка

1. Клонируйте репозиторий:

```bash
git clone https://github.com/d33fur/garpix.git && cd garpix
```


2. Создайте файл `backend/auth.env` и добавьте следующую переменную окружения(токен для api GigaChat):

```auth.env
GIGACHAT_AUTH=
```

3. В файл .env необходимо добавить значения этим переменным окружения(токен и id для api adobe pdf):

```.env
CLIENT_ID=
CLIENT_SECRET=
```

### Запуск проекта

1. Соберите и запустите Docker контейнеры:

```bash
make all
```

2. Посмотреть логи можно через:

```bash
make logs
```

3. Доступ к приложению:

- Фронтенд: [http://localhost:8501](http://localhost:8501)
- Админка: [http://localhost:8502](http://localhost:8502)
- Бэкэнд: [http://localhost:8000](http://localhost:8000)

## Использование админки

- Для добавления ГОСТа перейдите в "Добавить" и заполните поля "Название ГОСТа" и "JSON данные ГОСТа".
- Для удаления ГОСТа перейдите в "Удалить" и введите "Название ГОСТа".
- Для просмотра всех ГОСТов выберите "Показать все данные".

## API Эндпоинты

- `GET /list` - Получить список всех ГОСТов
- `POST /check` - Проверить файл на соответствие ГОСТу
- `POST /add` - Добавить или обновить ГОСТ
- `POST /delete` - Удалить ГОСТ
- `GET /get_all` - Получить все ГОСТы
