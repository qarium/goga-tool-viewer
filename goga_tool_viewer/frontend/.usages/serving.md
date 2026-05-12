# Обслуживание SPA

Для потребителей frontend — как отдать SPA-страницу.

## Получение HTML

Вызвать `index_page(graph_json_url)` — вернёт полную HTML-страницу.
graph_json_url — относительный URL к API-эндпоинту `/api/graph`.

## Что ожидает фронтенд

SPA загружает данные графа через fetch() к `graph_json_url`.
Ответ должен быть JSON в формате CellGraph (cells + edges).
