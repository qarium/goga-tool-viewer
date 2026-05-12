# Загрузка JSON-данных

Для потребителей parser — как загрузить данные cell из JSON.

## Из файла

Вызвать `load_json_file(path)` — вернёт CellGraph со всеми cells и зависимостями.

## Из stdin

Вызвать `load_json_stdin()` — читает JSON из stdin, вернёт CellGraph.

## Низкоуровневый парсинг

Если JSON уже загружен как строка — вызвать `parse_json(json_str)`.
Все load-рутины делегируют парсинг в `parse_json`.
