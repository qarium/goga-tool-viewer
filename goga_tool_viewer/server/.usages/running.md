# Запуск сервера

Для потребителей server — как запустить HTTP-сервер.

## Быстрый старт

Вызвать `run_server(json_path)` с путём к JSON-файлу.
Сервер найдёт свободный порт, загрузит данные и выведет URL.

## Если JSON через pipe

Передать `json_path=None` — сервер прочитает JSON из stdin.

## API Endpoints

- `GET /` — SPA-страница (HTML)
- `GET /api/graph` — данные графа (JSON, формат CellGraph)
- `GET /api/codemanifest?cell=<path>` — содержимое CODEMANIFEST (text/plain, Cache-Control: no-store)

## Получение URL

После создания GraphServer вызвать `url()` для получения полного адреса.
