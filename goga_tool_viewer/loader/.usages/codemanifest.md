# Загрузка CODEMANIFEST

Для потребителей loader — как загрузить содержимое CODEMANIFEST.

## Использование

Вызвать `load_codemanifest(cell_path)` — вернёт содержимое CODEMANIFEST как строку.
cell_path — относительный путь к cell (например "goga_tool_viewer/parser").

Если файл не найден — выбрасывает FileNotFoundError.