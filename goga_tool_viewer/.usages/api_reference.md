# API Reference

Для потребителей — описание публичного API goga-tool-viewer.

## Вызов через goga ecosystem

```
goga tool viewer [JSON_PATH]
```

- `JSON_PATH` — необязательный путь к JSON-файлу
- Если не указан — чтение из stdin

## Фасадная функция main(argv)

```python
from goga_tool_viewer import main

main(["path/to/data.json"])  # из файла
main([])                     # из stdin
```

## Web API

После запуска доступен HTTP-сервер:

- `GET /` — SPA-страница
- `GET /api/graph` — JSON с данными графа
