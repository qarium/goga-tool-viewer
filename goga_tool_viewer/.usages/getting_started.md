# Быстрый старт goga-tool-viewer

Для потребителей — как использовать tool в экосистеме goga.

## Запуск с файлом

```bash
goga tool viewer path/to/schema.json
```

Выведет URL: http://localhost:PORT

## Запуск через pipe

```bash
cat data.json | goga tool viewer
```

## Что вы увидите

Откроется веб-страница с интерактивным графом зависимостей между cells.
При клике на cell — отобразится панель с типами, потребителями и зависимостями.
