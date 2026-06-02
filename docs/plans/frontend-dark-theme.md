# План: `frontend-dark-theme`

## Цель

Доработать существующую функцию `index_page` в cell `frontend` до полноценного SPA с тёмной темой qarium.ru/goga: добавить дизайн-токены, хедер с логотипом, футер, favicon, информационную панель в виде карточки и тёмные стили Cytoscape. Реализация — исключительно изменение `pages.py`; структура контракта не меняется.

Основные разрывы между контрактом и текущей реализацией:
- Отсутствуют CSS-переменные и тёмная тема (сейчас минимальные стили без дизайн-токенов)
- Отсутствуют хедер, футер, favicon, логотип
- Отсутствует helper `_read_static_bytes` для бинарных ассетов
- Отсутствуют ассеты `logo.png`, `favicon.png`, `goga.svg` в `static/`
- Отсутствуют тёмные стили узлов и рёбер Cytoscape
- Информационная панель не стилизована как карточка

## Контекст

### Поверхность контракта

**Сущность: `index_page`**
- Тип: `function` (Routine)
- Объявленный `location`: `pages.py`
- Обязанность фасада: должна быть импортируема из `goga_tool_viewer.frontend`
- Сигнатура: `index_page(graph_json_url: str) -> html: str`
- Семантические требования из описаний:
  - Генерирует HTML-страницу SPA с тёмной темой qarium.ru/goga
  - Включает стили с дизайн-токенами, хедер с логотипом и backdrop-blur
  - Футер с копирайтом, стилизованный граф и информационную панель как карточку
  - JS-скрипт для загрузки данных из `graph_json_url` и инициализации Cytoscape
  - Все CSS стили inline (в теге `<style>`), favicon через `<link>`
  - Экранирование фигурных скобок для Python format: `{{` и `}}`
- Импортированные зависимости: нет (cell не содержит Imports)
- Контекст аннотаций:
  - Файл: использовать `conventions` для кода и тестов; `spa_structure` для структуры и дизайн-токенов; `cytoscape` для графа; `js_rendering` для inline JS
  - Сущность: генерирует HTML с тёмной темой, использует `spa_structure`, `cytoscape`, `js_rendering`

### Реэкспорты
Нет.

### Контекст Usages

- **`conventions`**: правила Python-кода (pydantic, docstrings, imports) и тестирования (pytest, ruff, `test_<what>_<scenario>` naming, Google-style docstrings)
- **`spa_structure`**: структура SPA-страницы и 6 CSS-переменных дизайн-токенов тёмной темы qarium.ru/goga. Хедер: фиксированный, backdrop-blur, логотип QArium. Основная область: граф (80%) + панель информации (20%). Футер: копирайт. Информационная панель: карточка с бордером white/5%. Статические ассеты: logo.png, favicon.png, goga.svg
- **`cytoscape`**: Cytoscape.js inline. Layout dagre. Стили узлов: round-rectangle, фон #121830, бордер #20d4bf, текст #fff. Рёбра: #20d4bf, направленные стрелки. Подсветка: teal для выбранного, затемнение остальных
- **`js_rendering`**: структура данных graph (cells[], edges[]). Функции: render_graph, highlight_cell, show_cell_info — вход/выход каждой

### Импортированные Usages
Нет — cell `frontend` не содержит Imports.

### Локальные Usages

- **Путь к файлу**: `.usages/styling.md`
- Функциональная категория: визуальные характеристики SPA
- Статус: расширяет существующий (обновлён пользователем вместе с CODEMANIFEST)
- Связанные сущности: `index_page`
- Описание: дизайн-токены, layout, стили Cytoscape для потребителей frontend

### Внешние зависимости

- Cytoscape.js — библиотека визуализации графов, встроена inline из `static/`
- dagre — layout-движок, встроен inline из `static/`
- base64 — stdlib, для кодирования ассетов в data URI

## Факты

- Cell `frontend` — один файл реализации `pages.py`, один фасад `__init__.py`
- `__init__.py` уже экспортирует `index_page` через `__all__`
- В `static/` уже есть: `cytoscape.min.js`, `dagre.min.js`, `cytoscape-dagre.min.js`
- В `static/` отсутствуют: `logo.png`, `favicon.png`, `goga.svg`
- Существующая реализация уже имеет `_read_static` для текстовых файлов и базовый HTML с Cytoscape
- Тесты уже существуют в `tests/frontend/test_index_page.py` с базовыми контрактными проверками
- Функция `_read_static_bytes` не существует — нужно создать

## Анализ разрывов

- Отсутствующие сущности контракта: нет (сущность `index_page` существует)
- Отсутствующее раскрытие фасада: нет (фасад корректен)
- Неверное размещение в `location`: нет
- Несоответствия API: нет (сигнатура `index_page(graph_json_url: str) -> str` корректна)
- Поведенческие несоответствия:
  - CSS-переменные тёмной темы отсутствуют
  - Хедер с логотипом и backdrop-blur отсутствует
  - Футер с копирайтом отсутствует
  - Favicon не подключается
  - Тёмные стили Cytoscape отсутствуют (узлы и рёбра без цветов)
  - Информационная панель не стилизована как карточка
  - Helper `_read_static_bytes` для бинарных ассетов не существует
  - Ассеты logo.png, favicon.png, goga.svg не скачаны
- Существующий код, который можно переиспользовать:
  - `_read_static` — полностью
  - JS-логика render_graph, highlight_cell, show_cell_info — с добавлением тёмных стилей
  - Существующие тесты — расширить и дополнить
- Разрывы в тестовом покрытии:
  - Нет тестов на тёмную тему, хедер, футер, favicon, стили Cytoscape
  - Нет тестов на `_read_static_bytes`
  - Нет негативных тестов на отсутствующие файлы
  - Нет краевых тестов на спецсимволы и экранирование

---

## Tasks

### Task 1: Скачать статические ассеты (инфраструктура)

Скачать брендированные ассеты с qarium.ru и поместить их в `goga_tool_viewer/frontend/static/`. Эти файлы необходимы для генерации HTML с логотипом и favicon.

**КРИТИЧЕСКИ: файлы `CODEMANIFEST` — определения контракта только для чтения. НЕ изменяйте их.**

- [x] Скачать `https://qarium.ru/images/logo.png` → `goga_tool_viewer/frontend/static/logo.png`
- [x] Скачать `https://qarium.ru/favicon.png` → `goga_tool_viewer/frontend/static/favicon.png`
- [x] Скачать `https://qarium.ru/images/goga.svg` → `goga_tool_viewer/frontend/static/goga.svg`
- [x] Проверить: `ls goga_tool_viewer/frontend/static/` — должны быть logo.png, favicon.png, goga.svg

### Task 2: Реализовать тёмную тему в `index_page` (TDD кодирование)

Расширить функцию `index_page` в `pages.py` для генерации HTML-страницы с тёмной темой qarium.ru/goga. Добавить CSS-переменные, хедер с логотипом, футер, favicon, тёмные стили Cytoscape, информационную панель-карточку и helper `_read_static_bytes`.

**Сущности контракта:** `index_page` (изменённая)
**location:** `pages.py`
**Фасад:** `__init__.py` — уже экспортирует `index_page`

**Usages, релевантные для этой задачи:**
- `conventions`: Google-style docstrings, relative imports, `test_<what>_<scenario>` naming, pytest с `tmp_path` для файлового I/O
- `spa_structure`: 6 CSS-переменных (`--color-brand-bg`, `--color-brand-card`, `--color-brand-teal`, `--color-brand-blue`, `--color-brand-text`, `--color-brand-muted`). Структура: хедер с backdrop-blur + логотип, основная область 80%/20%, футер с копирайтом, информационная панель как карточка с бордером white/5%. Шрифты: ui-sans-serif, system-ui, sans-serif; antialiased
- `cytoscape`: dagre layout (`spacingFactor: 1.5`, `rankDir: 'LR'`). Стили узлов: round-rectangle, фон #121830, бордер #20d4bf, текст #fff. Стили рёбер: bezier, направленные стрелки, цвет #20d4bf. Подсветка: teal для выбранного, затемнение остальных
- `js_rendering`: структура graph (cells[], edges[]). Функции render_graph, highlight_cell, show_cell_info

**Контекст из дизайн-документа — Алгоритм `index_page`:**
```
1. Прочитать static/cytoscape.min.js → cytoscape_js: str   (через _read_static)
2. Прочитать static/dagre.min.js → dagre_js: str            (через _read_static)
3. Прочитать static/cytoscape-dagre.min.js → cytoscape_dagre_js: str  (через _read_static)
4. Прочитать static/logo.png → logo_data: bytes             (через _read_static_bytes)
5. Прочитать static/favicon.png → favicon_data: bytes       (через _read_static_bytes)
6. base64_encode(logo_data) → logo_b64: str
7. base64_encode(favicon_data) → favicon_b64: str
8. Сформировать HTML через f-string:
   a. <!DOCTYPE html><html>
   b. <head>:
      - <meta charset="utf-8">
      - <link rel="icon" href="data:image/png;base64,{favicon_b64}">
      - <style>: CSS-переменные :root, стили body/header/main/#cy/#info/footer
      - <script>{cytoscape_js}</script>
      - <script>{dagre_js}</script>
      - <script>{cytoscape_dagre_js}</script>
   c. <body>:
      - <header>: <img src="data:image/png;base64,{logo_b64}"> + текст "QArium"
      - <main>: <div id="cy"> + <div id="info">
      - <footer>: © 2026 QArium. All rights reserved.
      - <script>: inline JS с fetch/render_graph/highlight_cell/show_cell_info
   d. </body></html>
9. Вернуть html: str
```

**Контекст из дизайн-документа — Контрольные точки трассировки:**
- Чтение статических файлов (JS): файлы существуют
- Чтение статических файлов (ассеты): logo.png, favicon.png читаются через `_read_static_bytes` с `Path.read_bytes()`
- Экранирование f-string: `{{`/`}}` корректны для JS-объектов
- Экранирование URL через `json.dumps`: корректно
- CSS-переменные в `<style>`: должны быть добавлены
- Тёмные стили Cytoscape в JS: должны быть добавлены

**КРИТИЧЕСКИ: файлы `CODEMANIFEST` — определения контракта только для чтения. НЕ изменяйте их. Если реализация не соответствует контракту, исправляйте реализацию — никогда не исправляйте контракт.**

- [x] **ШАГ 0 (ОБЪЯВЛЕНИЕ)**: Объявить работу над Task 2 — реализация тёмной темы в `index_page`
- [x] **ШАГ 1 (КОНТРАКТНЫЕ ТЕСТЫ)**: Написать контрактные тесты в `tests/frontend/test_index_page.py` для проверки:
  - `test_index_page_contains_dark_theme_css_variables`: 6 CSS-переменных в HTML (`--color-brand-bg: #0a0e1a`, `--color-brand-card: #121830`, `--color-brand-teal: #20d4bf`, `--color-brand-blue: #3882f6`, `--color-brand-text: #fff`, `--color-brand-muted: #a0aec0`)
  - `test_index_page_contains_header_with_logo`: `<header`, `"QArium"`, `"data:image/png;base64"`, `"backdrop-filter"` в HTML
  - `test_index_page_contains_footer_with_copyright`: `<footer`, `"© 2026 QArium. All rights reserved."` в HTML
  - `test_index_page_contains_favicon_link`: `<link rel="icon"` и `"data:image/png;base64"` в HTML
  - `test_index_page_cytoscape_dark_styles`: `"#121830"`, `"#20d4bf"`, `"round-rectangle"`, `"target-arrow-shape"` в HTML
  - `test_index_page_info_panel_card_style`: `"#info"`, `"rgba(255, 255, 255, 0.05)"` в HTML
  - `test_index_page_curly_brace_escaping`: JS-блоки не содержат `"{{"` в контексте JS (f-string корректно экранирован)
  - Использовать фикстуру `static_with_assets` из дизайн-документа для подготовки тестовых файлов
  - (Ожидаемо падают на этом этапе — реализация ещё не обновлена)
- [x] **ШАГ 2 (РЕАЛИЗАЦИЯ)**: Обновить `goga_tool_viewer/frontend/pages.py`:
  - Добавить `import base64` в imports модуля
  - Создать helper `_read_static_bytes(filename: str) -> bytes` — использует `Path.read_bytes()`
  - Обновить `index_page`:
    - Добавить чтение `logo.png` и `favicon.png` через `_read_static_bytes`
    - Добавить `base64.b64encode()` для обоих ассетов
    - Обновить CSS: добавить `:root` с 6 CSS-переменными, стили для `body` (тёмный фон, шрифты), `header` (fixed, backdrop-blur, logo), `main` (flex, 80%/20%), `#info` (карточка с rgba бордером), `footer` (фиксированный, копирайт), `.dimmed`, `.highlighted`
    - Добавить `<link rel="icon" href="data:image/png;base64,{favicon_b64}">` в `<head>`
    - Добавить `<header>` с `<img>` логотипа и текстом "QArium"
    - Добавить `<footer>` с `"© 2026 QArium. All rights reserved."`
    - Обернуть `#cy` и `#info` в `<main>`
    - Обновить стили Cytoscape в JS: node background-color `#121830`, border-color `#20d4bf`, color `#fff`; edge line-color `#20d4bf`
    - Сохранить существующую JS-логику render_graph, highlight_cell, show_cell_info
  - Все `{` и `}` в JS-коде внутри f-string удвоены (`{{`, `}}`)
- [x] **ШАГ 3 (ВЕРИФИКАЦИЯ ИНТЕРФЕЙСОВ)**: Запустить контрактные тесты: `pytest tests/frontend/test_index_page.py -v` — все должны пройти
- [x] **ШАГ 4 (ЛОГИЧЕСКИЕ ТЕСТЫ)**: Написать логические тесты в `tests/frontend/test_index_page.py`:
  - `test_index_page_missing_static_file_raises`: пустой `static/` → `pytest.raises(FileNotFoundError)`
  - `test_index_page_special_chars_in_url`: `"/api/graph?param=value&other=test"` → HTML генерируется без ошибок, URL встроен в `fetch()`
  - `test_index_page_empty_graph_url`: `""` → HTML генерируется, начинается с `"<!DOCTYPE html>"`
  - `test_read_static_bytes_returns_bytes_for_png`: `_read_static_bytes("logo.png")` возвращает `bytes`, начинается с `b'\x89PNG'`
  - `test_read_static_bytes_missing_file_raises`: `_read_static_bytes("logo.png")` в пустом static → `pytest.raises(FileNotFoundError)`
- [x] **ШАГ 5 (ОТЛАДКА)**: Запустить все тесты: `pytest tests/ -x` — исправлять код реализации, пока все тесты не пройдут (НЕ исправлять тестовый код)
- [x] **ШАГ 6 (ПЕРЕПРОВЕРКА КОНТРАКТА)**: Проверить все обязательства контракта:
  - `index_page` доступна из фасада: `python -c "from goga_tool_viewer.frontend import index_page"`
  - Сигнатура: `(graph_json_url: str) -> str`
  - HTML содержит все элементы тёмной темы
- [x] **ШАГ 7 (ЛИНТ)**: `ruff check goga_tool_viewer/frontend/` — исправить форматирование, при необходимости декомпозировать
- [x] **ШАГ 8 (ЗАВЕРШЕНИЕ)**: Отметить чекбоксы как выполненные
- [x] **→ РЕВЬЮ → ОДОБРЕНИЕ → СЛЕДУЮЩАЯ ЗАДАЧА**

### Task 3: Интеграционные тесты для `frontend` cell

Проверить сквозные сценарии генерации HTML: корректность всей страницы как единого целого, взаимосвязь CSS-переменных и стилей, полноту встроенных JS-библиотек.

**Сущности контракта:** `index_page` (верификация через сквозные тесты)
**Целевой файл тестов:** `tests/frontend/test_index_page.py`

**КРИТИЧЕСКИ: файлы `CODEMANIFEST` — определения контракта только для чтения. НЕ изменяйте их.**

**Usages, релевантные для этой задачи:**
- `conventions`: `test_<what>_<scenario>` naming, pytest с `tmp_path`
- `spa_structure`: 6 дизайн-токенов, структура хедер/футер/панель
- `cytoscape`: dagre layout, тёмные стили
- `js_rendering`: структура данных graph, функции render_graph/highlight_cell/show_cell_info

- [x] **ШАГ 0 (ОБЪЯВЛЕНИЕ)**: Объявить работу над Task 3 — интеграционные тесты для `index_page`
- [x] **ШАГ 1 (ТЕСТЫ)**: Создать/обновить файл тестов `tests/frontend/test_index_page.py` — добавить класс `TestIndexPageIntegration`:
  - `test_index_page_full_html_structure` — `<!DOCTYPE html>`, `<html>`, `<head>`, `<body>`, `<header>`, `<main>`, `<footer>` — все секции присутствуют в правильном порядке
  - `test_index_page_css_variables_used_in_inline_styles` — CSS-переменные объявлены в `:root` и используются через `var()` в стилях body/header/main/info/footer
  - `test_index_page_embeds_all_js_libraries` — содержимое файлов cytoscape.min.js, dagre.min.js, cytoscape-dagre.min.js встроено в `<script>` теги
- [x] **ШАГ 2 (ОТЛАДКА)**: Запустить тесты: `pytest tests/frontend/test_index_page.py -v` — исправлять тесты и/или код реализации, пока все не пройдут
- [x] **ШАГ 3 (ЛИНТ)**: `ruff check tests/frontend/` — исправить форматирование
- [x] **ШАГ 4 (ЗАВЕРШЕНИЕ)**: Отметить чекбоксы как выполненные
- [x] **→ РЕВЬЮ → ОДОБРЕНИЕ → СЛЕДУЮЩАЯ ЗАДАЧА**

---

## Команды валидации

- `pytest tests/ -x`: Запустить все тесты
- `ruff check goga_tool_viewer/frontend/`: Проверка линта
- `python -c "from goga_tool_viewer.frontend import index_page"`: Проверить, что `index_page` импортируема из фасада
- `pytest tests/frontend/test_index_page.py -v`: Запустить тесты frontend

---

## Критерии завершения

- [x] Сущность контракта `index_page` реализована в `pages.py`
- [x] `index_page` доступна из фасада `goga_tool_viewer.frontend`
- [x] Сигнатура `(graph_json_url: str) -> str` сохранена
- [x] HTML содержит CSS-переменные тёмной темы (6 дизайн-токенов)
- [x] HTML содержит хедер с логотипом и backdrop-blur
- [x] HTML содержит футер с копирайтом
- [x] HTML содержит favicon через `<link>`
- [x] HTML содержит тёмные стили Cytoscape
- [x] Информационная панель стилизована как карточка
- [x] Helper `_read_static_bytes` реализован для бинарных ассетов
- [x] Ассеты logo.png, favicon.png, goga.svg присутствуют в static/
- [x] Каждая задача кодирования следовала рабочему процессу TDD
- [x] Контрактные и логические тесты покрывают фасад, API и поведение
- [x] Интеграционные тесты покрывают сквозные сценарии
- [x] Файлы `CODEMANIFEST` не были изменены
- [x] Все команды валидации проходят