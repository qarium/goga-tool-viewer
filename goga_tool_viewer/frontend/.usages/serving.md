# Обслуживание SPA

Для потребителей frontend — как отдать SPA-страницу.

## Получение HTML

Вызвать `index_page(graph_json_url)` — вернёт HTML-страницу со ссылками на внешние CSS и JS.
graph_json_url — относительный URL к API-эндпоинту `/api/graph`.

## Статические файлы

HTML-страница ссылается на внешние ресурсы по пути `/static/<filename>`.
Потребитель должен обслуживать этот маршрут, возвращая файлы
с корректными MIME-типами: text/css, application/javascript,
image/png, image/svg+xml.

## Что ожидает фронтенд

SPA загружает данные графа через fetch() к `graph_json_url`.
Ответ должен быть JSON в формате CellGraph (cells + edges).
