# Загрузка CODEMANIFEST

Для потребителей loader — как загрузить содержимое CODEMANIFEST.

## Использование

Вызвать `load_codemanifest(cell_path)` — вернёт содержимое CODEMANIFEST как строку.
cell_path — относительный путь к cell (например "goga_tool_viewer/parser").

## Защита от path traversal

Двухуровневая проверка: строковая (запрет ".." и "/") и resolve-based (проверка что путь не выходит за корень проекта).

## Исключения

- `ValueError` — путь содержит "..", начинается с "/" или выходит за пределы проекта.
- `FileNotFoundError` — файл CODEMANIFEST не найден по указанному пути.