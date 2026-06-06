# Загрузка JSON-данных

Для потребителей parser — как загрузить данные cell из JSON.

## Из файла

Вызвать `load_json_file(path)` — вернёт CellGraph со всеми cells и зависимостями.
`project_root` определяется как родительская директория файла.

## Из stdin

Вызвать `load_json_stdin()` — читает JSON из stdin, вернёт CellGraph.
`project_root` определяется как текущая рабочая директория.

## Низкоуровневый парсинг

Если JSON уже загружен как строка — вызвать `parse_json(json_str, project_root="")`.
Все load-рутины делегируют парсинг в `parse_json`.
