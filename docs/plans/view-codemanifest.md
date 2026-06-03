# План: `view-codemanifest`

## Цель

Реализовать просмотр содержимого CODEMANIFEST в SPA: при клике на ссылку «CODEMANIFEST» в info panel загружается и отображается yaml-содержимое файла в центральной панели. Добавить новую ячейку `loader` для безопасного чтения CODEMANIFEST из файловой системы, интегрировать её в серверный роутинг и обновить frontend.

Разрывы: отсутствует реализация ячейки `loader` (нет `codemanifest.py`, нет `__init__.py`), в `server.py` нет роута `/api/codemanifest`, в `pages.py` нет JS-функции `show_codemanifest`, CSS для центральной панели и ссылки «CODEMANIFEST» в info panel.

## Контекст

### Поверхность контракта

**Сущность: `load_codemanifest`**
- Тип: `function` (Routine)
- Объявленный `location`: `codemanifest.py` (в `goga_tool_viewer/loader/`)
- Обязанность фасада: должна быть импортируема из `goga_tool_viewer.loader`
- Мутации: нет
- Свойства: нет
- Методы: нет
- Сигнатура: `load_codemanifest(cell_path: str) -> content:str`
- Семантические требования: безопасное чтение CODEMANIFEST — path traversal защита (два уровня: строковая проверка `".."` и `/` prefix + resolve/verify под base), FileNotFoundError при отсутствии файла, ValueError при невалидном пути
- Импортированные зависимости: нет
- Контекст аннотаций: «Читает файл CODEMANIFEST по пути cell. Возвращает содержимое как строку. Защита от path traversal: путь не должен содержать ".." и не должен начинаться с "/"»

**Сущность: `GraphServer.get_codemanifest`**
- Тип: `method` (Entity `GraphServer`)
- Объявленный `location`: `server.py` (в `goga_tool_viewer/server/`)
- Обязанность фасада: метод экземпляра GraphServer
- Мутации: нет
- Сигнатура: `get_codemanifest(cell_path: str) -> content:str`
- Семантические требования: HTTP-эндпоинт GET `/api/codemanifest?cell=<path>`, парсинг query-параметра `cell`, делегирование `load_codemanifest`, возврат 200 text/plain при успехе, 404 при FileNotFoundError, 400 при ValueError или отсутствии параметра `cell`
- Импортированные зависимости: `load_codemanifest` из `goga_tool_viewer.loader`
- Контекст аннотаций: «Возвращает содержимое CODEMANIFEST для указанного cell. Используй `codemanifest` для чтения файла»

**Сущность: `index_page` (изменённая)**
- Тип: `function` (Routine)
- Объявленный `location`: `pages.py` (в `goga_tool_viewer/frontend/`)
- Обязанность фасада: функция уровня модуля
- Сигнатура: `index_page(graph_json_url: str) -> html:str`
- Семантические требования: добавлена центральная панель `#codemanifest-panel` между sidebar и info panel, ссылка «CODEMANIFEST» в info panel (в `show_cell_info`), JS-функция `show_codemanifest(cell_name, graph)` — fetch без кеширования, отображение в `<pre><code>`, закрытие крестиком, обработка 404 и сетевых ошибок
- Контекст аннотаций: «При клике открывается центральная панель между sidebar и info panel. Содержимое загружается без кеширования. Панель закрывается крестиком. При 404 — "CODEMANIFEST not found"»

### Реэкспорты

Нет блоков реэкспорта в данном плане.

### Контекст Usages

- **`conventions`** (`goga/usages/conventions.md`): правила Python-кода, Google-style docstrings, pytest, relative imports, pydantic, logging. Обязательная практика для всего проекта.
- **`stdlib_http`** (inline в server/CODEMANIFEST): паттерн http.server из stdlib — BaseHTTPRequestHandler, MIME-типы, do_GET.
- **`js_rendering`** (inline в frontend/CODEMANIFEST): спецификации inline JS-функций для SPA — включает `show_codemanifest(cell_name, graph)`.
- **`frontend_styling`** (`goga/usages/frontend_styling.md`): дизайн-токены, layout, стили.

### Импортированные Usages

- **`codemanifest`** из `goga_tool_viewer/loader`
  - Путь источника: `goga_tool_viewer/loader/.usages/codemanifest.md`
  - Описание: инструкция по использованию API загрузчика CODEMANIFEST
  - Релевантность: используется сервером для вызова `load_codemanifest(cell_path)`, возвращает str, выбрасывает FileNotFoundError

### Локальные Usages

Нет новых файлов `.usages/` для создания — `codemanifest.md` в `goga_tool_viewer/loader/.usages/` создаётся вместе с ячейкой loader.

### Внешние зависимости

- `http.server` (stdlib) — HTTP-сервер
- `pathlib` (stdlib) — работа с путями
- `urllib.parse` (stdlib) — парсинг URL
- Cytoscape.js (inline в HTML) — визуализация графа
- pytest (тестирование)

## Факты

- Проект использует Python, язык конфигурации — `python`
- Сервер однопоточный (http.server.BaseHTTPRequestHandler)
- Frontend — SPA в одном HTML-файле с inline CSS и JS
- Темная тема qarium.ru/goga, дизайн-токены в `frontend_styling`
- Все новые файлы Python должны содержать Google-style docstrings
- Защита от path traversal — двухуровневая: строковая проверка + resolve/verify
- CSS центральной панели соответствует стилю info panel (#0f172a фон, #1e293b titlebar)
- Только stdlib — без внешних зависимостей

## Анализ разрывов

- **Отсутствующие сущности контракта:**
  - `load_codemanifest` — нет файла `goga_tool_viewer/loader/codemanifest.py`
  - `goga_tool_viewer/loader/__init__.py` — нет фасада ячейки loader
- **Отсутствующее раскрытие фасада:**
  - `goga_tool_viewer.loader` не экспортирует `load_codemanifest` (нет `__init__.py`)
- **Несоответствия API:**
  - `GraphServer` не имеет метода `get_codemanifest`
  - `do_GET` не обрабатывает роут `/api/codemanifest`
  - `show_cell_info` не содержит ссылку «CODEMANIFEST»
  - Нет JS-функции `show_codemanifest` в HTML
  - Нет CSS для `#codemanifest-panel`
- **Разрывы в тестовом покрытии:**
  - Нет `tests/loader/` — тесты для loader отсутствуют
  - Нет тестов для роута `/api/codemanifest` в `tests/server/test_server.py`
  - Нет тестов для обновлённого `index_page` в `tests/frontend/test_index_page.py`
- **Существующий код для переиспользования:**
  - `goga_tool_viewer/server/server.py` — добавить роут к существующему `do_GET`
  - `goga_tool_viewer/frontend/pages.py` — обновить существующую `index_page`
  - `goga_tool_viewer/loader/CODEMANIFEST` — уже существует

---

## Tasks

> **Правило упорядочивания по пакетам**: задачи кодирования каждого пакета завершаются перед началом следующего. Порядок: loader (листовая ячейка) → server → frontend. Внутри каждой задачи кодирования контрактные тесты пишутся первыми (рабочий процесс TDD).

### Task 1: Инфраструктура ячейки loader (инфраструктура)

Создать структуру ячейки `goga_tool_viewer/loader/`: фасад `__init__.py` с экспортом `load_codemanifest`. Ячейка loader — новая, является листовой (нет зависимостей от других ячеек). Контракт определяет одну Routine `load_codemanifest` в `location: codemanifest.py`.

**Usages, релевантные для этой задачи:**
- `conventions`: Google-style docstrings, relative imports, правила форматирования

**КРИТИЧЕСКИ: файлы `CODEMANIFEST` — определения контракта только для чтения. НЕ изменяйте их. Если реализация не соответствует контракту, исправляйте реализацию — никогда не исправляйте контракт.**

- [x] Создать файл `goga_tool_viewer/loader/__init__.py` с `__all__ = ["load_codemanifest"]` и импортом `from .codemanifest import load_codemanifest`
- [x] Создать пустой файл `goga_tool_viewer/loader/codemanifest.py` (заполнится в Task 2)
- [x] Создать директорию `tests/loader/` и файл `tests/loader/__init__.py`
- [x] Проверить доступность фасада: `python -c "from goga_tool_viewer.loader import load_codemanifest; print('OK')"` (провалится до Task 2 — это ожидаемо; проверить структуру: `ls goga_tool_viewer/loader/__init__.py`)

### Task 2: Реализация `load_codemanifest` (TDD кодирование)

Реализовать Routine `load_codemanifest(cell_path: str) -> content:str` в `goga_tool_viewer/loader/codemanifest.py`. Функция безопасно читает CODEMANIFEST по относительному пути cell. Защита от path traversal: строковая проверка (нет `".."`, не начинается с `"/"`) + resolve/verify что путь находится под корнем проекта.

**Сущности контракта:** `load_codemanifest` (Routine, location: `codemanifest.py`)

**Usages, релевантные для этой задачи:**
- `conventions`: Google-style docstrings, pytest, logging

**КРИТИЧЕСКИ: файлы `CODEMANIFEST` — определения контракта только для чтения. НЕ изменяйте их. Если реализация не соответствует контракту, исправляйте реализацию — никогда не исправляйте контракт.**

- [x] **ШАГ 0 (ОБЪЯВЛЕНИЕ)**: Объявить, что работа ведётся над Task 2 — реализация `load_codemanifest`
- [x] **Контрактные тесты**: создать файл `tests/loader/test_codemanifest.py`
  - `test_load_codemanifest_callable` — функция доступна из фасада `goga_tool_viewer.loader`, callable, принимает один позиционный аргумент
  - `test_load_codemanifest_signature` — возвращает str при корректном пути (создать tmp CODEMANIFEST, вызвать, проверить isinstance(result, str))
  - Все контрактные тесты ожидаемо падают (файл codemanifest.py пуст)
- [x] **Код**: реализовать `load_codemanifest(cell_path: str) -> str` в `goga_tool_viewer/loader/codemanifest.py`:
  - Валидация: если `".."` в `cell_path` → raise ValueError("path traversal detected")
  - Валидация: если `cell_path.startswith("/")` → raise ValueError("absolute path not allowed")
  - Построение пути: `Path(__file__).resolve().parent.parent.parent / cell_path / "CODEMANIFEST"`, затем `resolve()`
  - Верификация: проверить что `target.is_relative_to(base)` — если нет → raise ValueError
  - Чтение: `target.read_text(encoding="utf-8")`
  - FileNotFoundError пробрасывается естественно при отсутствии файла
  - Google-style docstring
- [x] **Верификация интерфейсов**: запустить `python -m pytest tests/loader/test_codemanifest.py -k "test_load_codemanifest_callable or test_load_codemanifest_signature" -x` — контрактные тесты должны пройти
- [x] **Логические тесты** (добавить в `tests/loader/test_codemanifest.py`):
  - Общий подход: использовать `monkeypatch` для подмены `Path(__file__)` в `codemanifest.py` на `tmp_path / "fake_cell" / "codemanifest.py"` — это позволяет `load_codemanifest` вычислять корень проекта относительно `tmp_path`
  - `test_load_codemanifest_reads_existing_file` — monkeypatch `__file__` на `tmp_path / "fake_cell" / "codemanifest.py"`, создать директорию `goga_tool_viewer/parser/` в `tmp_path`, поместить CODEMANIFEST с содержимым `"Usages:\n  test: value\n"`, вызвать `load_codemanifest("goga_tool_viewer/parser")`, проверить `result == "Usages:\n  test: value\n"`
  - `test_load_codemanifest_rejects_path_traversal` — `load_codemanifest("../../etc/passwd")` → pytest.raises(ValueError) (без monkeypatch — строковая валидация не зависит от filesystem)
  - `test_load_codemanifest_rejects_absolute_path` — `load_codemanifest("/etc/passwd")` → pytest.raises(ValueError) (без monkeypatch — строковая валидация не зависит от filesystem)
  - `test_load_codemanifest_raises_on_missing_file` — monkeypatch `__file__` на `tmp_path / "fake_cell" / "codemanifest.py"`, `load_codemanifest("nonexistent/cell")` с пустым tmp_path → pytest.raises(FileNotFoundError)
  - `test_load_codemanifest_empty_path` — monkeypatch `__file__` на `tmp_path / "fake_cell" / "codemanifest.py"`, `load_codemanifest("")` → pytest.raises(FileNotFoundError)
  - `test_load_codemanifest_path_traversal_encoded` — monkeypatch `__file__` на `tmp_path / "fake_cell" / "codemanifest.py"`, `load_codemanifest("cell/..%2F..%2Fsecret")` → pytest.raises((ValueError, FileNotFoundError))
- [x] **Отладка**: запустить `python -m pytest tests/loader/test_codemanifest.py -x` — исправлять код реализации, пока все тесты не пройдут (НЕ исправлять тесты)
- [x] **Перепроверка контракта**: проверить что `load_codemanifest` доступна из `goga_tool_viewer.loader`, сигнатура `(cell_path: str) -> str`, выбрасывает ValueError и FileNotFoundError
- [x] **Линт**: запустить `python -m ruff check goga_tool_viewer/loader/codemanifest.py tests/loader/test_codemanifest.py` — исправить форматирование
- [x] **ЗАВЕРШЕНИЕ**: отметить чекбоксы как выполненные

### Task 3: Добавление роута `/api/codemanifest` в GraphServer (TDD кодирование)

Добавить обработку GET `/api/codemanifest?cell=<path>` в `GraphServer.do_GET`. Роут парсит query-параметр `cell`, делегирует `load_codemanifest` из loader, возвращает 200 text/plain при успехе, 400 при отсутствии/пустом параметре или path traversal, 404 при FileNotFoundError.

**Сущности контракта:** `GraphServer.get_codemanifest(cell_path: str) -> content:str` (метод GraphServer, location: `server.py`)

**Usages, релевантные для этой задачи:**
- `conventions`: Google-style docstrings, pytest
- `stdlib_http`: BaseHTTPRequestHandler, MIME-типы, do_GET
- `codemanifest` (из Imports, путь: `goga_tool_viewer/loader/.usages/codemanifest.md`): Вызвать `load_codemanifest(cell_path)` — вернёт содержимое CODEMANIFEST как строку. cell_path — относительный путь к cell (например "goga_tool_viewer/parser"). Если файл не найден — выбрасывает FileNotFoundError

**КРИТИЧЕСКИ: файлы `CODEMANIFEST` — определения контракта только для чтения. НЕ изменяйте их. Если реализация не соответствует контракту, исправляйте реализацию — никогда не исправляйте контракт.**

- [x] **ШАГ 0 (ОБЪЯВЛЕНИЕ)**: Объявить, что работа ведётся над Task 3 — добавление роута `/api/codemanifest` в GraphServer
- [x] **Контрактные тесты**: добавить тесты в `tests/server/test_server.py`
  - `test_graphserver_has_get_codemanifest` — проверить что экземпляр GraphServer имеет метод `get_codemanifest`, callable
  - `test_server_codemanifest_route_returns_content` — GET `/api/codemanifest?cell=goga_tool_viewer/models` → 200, Content-Type text/plain, body содержит yaml
  - Все контрактные тесты ожидаемо падают (роут ещё не реализован)
- [x] **Код**: обновить `goga_tool_viewer/server/server.py`:
  - Добавить импорт: `from goga_tool_viewer.loader import load_codemanifest`
  - Добавить метод `get_codemanifest(self, cell_path: str) -> str` — делегирует `load_codemanifest(cell_path)`, возвращает content
  - В `do_GET`: добавить ветку для `self.path.startswith("/api/codemanifest")`:
    - Парсинг URL: `urlparse(self.path)`, `parse_qs(parsed.query)`
    - Извлечение `cell_path = params.get("cell", [None])[0]`
    - Если `cell_path is None or cell_path == ""` → send_response(400), `"Missing 'cell' parameter"`
    - Обёртка в try/except: вызов `self.get_codemanifest(cell_path)` → 200 text/plain; `FileNotFoundError` → 404; `ValueError` → 400 `"Invalid cell path"`
  - Google-style docstring для нового метода
- [x] **Верификация интерфейсов**: запустить `python -m pytest tests/server/test_server.py -k "test_graphserver_has_get_codemanifest or test_server_codemanifest_route_returns_content" -x` — контрактные тесты должны пройти
- [x] **Логические тесты** (добавить в `tests/server/test_server.py`):
  - `test_server_get_codemanifest_returns_404_for_missing` — GET `/api/codemanifest?cell=nonexistent/cell` → assert status == 404
  - `test_server_get_codemanifest_returns_400_without_cell_param` — GET `/api/codemanifest` → assert status == 400
  - `test_server_get_codemanifest_empty_cell_param` — GET `/api/codemanifest?cell=` → assert status == 400
- [x] **Отладка**: запустить `python -m pytest tests/server/test_server.py -x` — исправлять код реализации, пока все тесты не пройдут
- [x] **Перепроверка контракта**: проверить что `GraphServer` имеет метод `get_codemanifest`, роут `/api/codemanifest` обрабатывается, возвращаемые статусы корректны (200/400/404)
- [x] **Линт**: запустить `python -m ruff check goga_tool_viewer/server/server.py tests/server/test_server.py` — исправить форматирование
- [x] **ЗАВЕРШЕНИЕ**: отметить чекбоксы как выполненные

### Task 4: Обновление frontend — `show_codemanifest` и центральная панель (TDD кодирование)

Обновить `goga_tool_viewer/frontend/pages.py` — добавить JS-функцию `show_codemanifest(cell_name, graph)`, обновить `show_cell_info` ссылкой «CODEMANIFEST», добавить CSS для `#codemanifest-panel`. Функция выполняет fetch к `/api/codemanifest?cell=<path>`, отображает результат в центральной панели как `<pre><code>`, обрабатывает 404 и ошибки сети.

**Сущности контракта:** `index_page` (Routine, location: `pages.py`) — обновлённая аннотация с центральной панелью и ссылкой CODEMANIFEST

**Usages, релевантные для этой задачи:**
- `conventions`: Google-style docstrings, pytest
- `js_rendering`: спецификации `show_codemanifest` и обновлённый `show_cell_info` — fetch без кеширования, панель между sidebar и info panel, `<pre><code>`, крестик для закрытия
- `frontend_styling`: дизайн-токены, стили info panel для согласованности

**КРИТИЧЕСКИ: файлы `CODEMANIFEST` — определения контракта только для чтения. НЕ изменяйте их. Если реализация не соответствует контракту, исправляйте реализацию — никогда не исправляйте контракт.**

- [x] **ШАГ 0 (ОБЪЯВЛЕНИЕ)**: Объявить, что работа ведётся над Task 4 — обновление frontend для CODEMANIFEST viewer
- [x] **Контрактные тесты**: добавить тесты в `tests/frontend/test_index_page.py`
  - `test_index_page_contains_show_codemanifest_function` — проверить что HTML содержит `"function show_codemanifest"` и `"/api/codemanifest"`
  - `test_index_page_contains_codemanifest_panel_css` — проверить что HTML содержит `"#codemanifest-panel"` и стили для панели
  - Все контрактные тесты ожидаемо падают (функция и CSS ещё не добавлены)
- [x] **Код**: обновить `goga_tool_viewer/frontend/pages.py`:
  - Добавить CSS для `#codemanifest-panel`: position absolute, top/bottom 8px, left от sidebar (276px + 8px gap), background #0f172a, border-radius 8px, box-shadow, z-index 8, overflow-y auto, max-width ~50%
  - Добавить CSS для `.titlebar` в панели: стиль как info-titlebar (#1e293b фон, моноширинный)
  - Добавить CSS для `#codemanifest-panel pre code`: font-family monospace, font-size 12px, color var(--color-brand-text), white-space pre-wrap, padding 16px
  - Добавить CSS для `.codemanifest-link`: cursor pointer, color var(--color-brand-muted), font-size 11px, hover color var(--color-brand-teal)
  - Добавить JS-функцию `show_codemanifest(cell_name, graph)`:
    1. Найти cell: `graph.cells.find(c => c.name === cell_name)` → если не найдена, return
    2. Fetch: `fetch('/api/codemanifest?cell=' + encodeURIComponent(cell.name))`
    3. Обработка: 404 → "CODEMANIFEST not found"; ok → response.text(); иначе → "Failed to load CODEMANIFEST"
    4. Создание панели: удалить существующую `#codemanifest-panel`, создать div с titlebar (заголовок "CODEMANIFEST" + крестик ×) и body (`<pre><code>content</code></pre>`), append to main
    5. Привязка закрытия: крестик → remove panel
  - Обновить `show_cell_info`: после всех секций (Name, Description, Types, Consumers, Dependencies) добавить `<span class="codemanifest-link" data-cell="cell_name">CODEMANIFEST</span>` с addEventListener('click', () => show_codemanifest(cell_name, graph))
- [x] **Верификация интерфейсов**: запустить `python -m pytest tests/frontend/test_index_page.py -k "test_index_page_contains_show_codemanifest or test_index_page_contains_codemanifest_panel_css" -x` — контрактные тесты должны пройти
- [x] **Логические тесты** (добавить в `tests/frontend/test_index_page.py`):
  - `test_index_page_contains_codemanifest_link_in_info_panel` — `"codemanifest-link"` in html, `"show_codemanifest"` in html (привязка обработчика)
  - `test_index_page_codemanifest_error_messages` — `"CODEMANIFEST not found"` in html, `"Failed to load CODEMANIFEST"` in html
  - `test_show_codemanifest_no_cache_per_click` — проверить что HTML содержит `show_codemanifest` (каждый клик инициирует новый fetch)
- [x] **Отладка**: запустить `python -m pytest tests/frontend/test_index_page.py -x` — исправлять код реализации, пока все тесты не пройдут
- [x] **Перепроверка контракта**: проверить что `index_page` генерирует HTML с функцией `show_codemanifest`, CSS для `#codemanifest-panel`, ссылкой «CODEMANIFEST» в info panel
- [x] **Линт**: запустить `python -m ruff check goga_tool_viewer/frontend/pages.py tests/frontend/test_index_page.py` — исправить форматирование
- [x] **ЗАВЕРШЕНИЕ**: отметить чекбоксы как выполненные

### Task 5: Интеграционные тесты для CODEMANIFEST viewer

Протестировать сквозной сценарий: browser → server → loader → filesystem. Проверить корректность HTTP-ответов при разных состояниях файловой системы и корректность генерации HTML с компонентами CODEMANIFEST viewer.

**Usages, релевантные для этой задачи:**
- `conventions`: pytest, фикстуры
- `stdlib_http`: тестирование HTTP-эндпоинтов

- [ ] Создать/обновить файл `tests/loader/test_codemanifest.py` — интеграционный тест с реальной файловой системой
  - `test_load_codemanifest_real_project_file` — вызвать `load_codemanifest("goga_tool_viewer/models")` (реальный CODEMANIFEST проекта) → проверить что возвращает непустую строку, содержащую `"Usages:"` или `"Annotations:"`
- [ ] Обновить файл `tests/server/test_server.py` — интеграционный тест через HTTP
  - `test_server_codemanifest_full_flow` — запустить сервер, GET `/api/codemanifest?cell=goga_tool_viewer/models` → проверить 200, Content-Type text/plain, body начинается с реального содержимого CODEMANIFEST
- [ ] Обновить файл `tests/frontend/test_index_page.py` — интеграционный тест HTML
  - `test_index_page_codemanifest_full_markup` — вызвать `index_page("/api/graph")`, проверить: наличие `show_codemanifest` + `codemanifest-panel` + `codemanifest-link` + `/api/codemanifest` + закрытие панели — единый сценарий
- [ ] Запустить валидацию: `python -m pytest tests/ -x`

---

## Команды валидации

- `python -m pytest tests/ -x`: Запустить все тесты
- `python -m ruff check goga_tool_viewer/`: Проверка линта
- `python -c "from goga_tool_viewer.loader import load_codemanifest; print('loader OK')"`: Проверить фасад loader
- `python -c "from goga_tool_viewer.server import GraphServer; print(hasattr(GraphServer, 'get_codemanifest'))"`: Проверить метод сервера

---

## Критерии завершения

- [ ] Каждая сущность контракта реализована в правильном `location`
- [ ] Каждая сущность контракта доступна из фасада
- [ ] Свойства и методы соответствуют объявленному API
- [ ] Описания отражены в поведении
- [ ] Зависимости контракта соблюдены
- [ ] Реэкспорты доступны из фасада
- [ ] Каждая задача кодирования следовала рабочему процессу TDD (контрактные тесты → код → верификация → логические тесты → отладка → перепроверка → линт)
- [ ] Контрактные тесты и логические тесты покрывают фасад, API и поведение в рамках каждой задачи кодирования
- [ ] Интеграционные тесты существуют там, где межсущностные сценарии их требуют
- [ ] Ни одна граница пакета не была расширена
- [ ] Файлы `CODEMANIFEST` не были изменены (контракт только для чтения)
- [ ] Все команды валидации проходят
- [ ] Каждая запись Usages упомянута как минимум в одной задаче