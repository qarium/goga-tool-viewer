# Стили SPA — тёмная тема qarium.ru/goga

Требования к визуальному оформлению SPA.

## Структура SPA

SPA состоит из HTML-файла со ссылками на внешние CSS и JS файлы.
Без сборки — статические файлы раздаются сервером из frontend/static/.

Статические ассеты в static/:
- style.css — все CSS-стили SPA
- app.js — JS-логика SPA
- logo.png, favicon.png — брендированные ресурсы. Референс: qarium.ru/goga. Скачать с сайта: логотип из хедера, favicon из вкладки браузера.
- icon-telegram.svg, icon-github.svg, icon-email.svg — иконки контактов. Inline SVG, соответствующие иконкам из qarium.ru/goga.
- icon-name.svg, icon-description.svg, icon-types.svg, icon-usages.svg, icon-consumers.svg, icon-dependencies.svg — иконки секций info panel. Передаются через CSS custom properties (--icon-*).
- icon-folder.svg, icon-layers.svg — иконки узлов дерева. Передаются через CSS custom properties.
- icon-code.svg, icon-reset.svg — иконки действий. Передаются через CSS custom properties.
- cytoscape.min.js — скачать с https://js.cytoscape.org/ (раздел Download)
- dagre.min.js — скачать с https://github.com/dagrejs/dagre (npm: dagre)
- cytoscape-dagre.min.js — скачать с https://github.com/cytoscape/cytoscape.js-dagre (npm: cytoscape-dagre)

## Дизайн-токены

| Токен                  | Значение  | Назначение           |
|------------------------|-----------|----------------------|
| --color-brand-bg       | #0a0e1a   | Основной фон         |
| --color-brand-card     | #121830   | Карточки, панели     |
| --color-brand-teal     | #20d4bf   | Акценты, подсветка   |
| --color-brand-blue     | #3882f6   | Вторичный акцент     |
| --color-brand-text     | #fff      | Основной текст       |
| --color-brand-muted    | #a0aec0   | Приглушённый текст   |

## Layout

- Хедер: фиксированный, backdrop-blur, логотип QArium слева
  - Текст "QArium" двухцветный: "QA" — teal, "rium" — белый
  - Иконки контактов справа: Telegram (t.me/QAriumCommunity), GitHub (github.com/qarium), Email (info@qarium.ru)
  - Иконки — inline SVG с opacity 0.6, hover — 1.0
- Основная область: граф (flex: 1, занимает всё свободное пространство) + информационная панель справа
- Футер: логотип QArium слева, копирайт "© 2026 QArium. All rights reserved." справа
- Шрифты: ui-sans-serif, system-ui, sans-serif; antialiased
- Панель info — моноширинный шрифт: ui-monospace, SFMono-Regular, monospace

## Информационная панель (OS-окно)

Панель справа стилизована как окно операционной системы:
- Title bar: заголовок с именем cell, кнопка закрытия (×)
- Фон панели: #0f172a, тень box-shadow
- По умолчанию скрыта (class="hidden"), открывается при клике на узел графа
- Закрывается по клику на кнопку ×
- Содержимое форматируется как markdown:
  - h2 — заголовки секций: uppercase, muted цвет, с SVG-иконкой через ::before (атрибут data-icon)
  - p — параграфы с текстом, белый цвет
  - .description — blockquote-стиль: левый teal бордер, полупрозрачный teal фон, курсив
  - ul/li — списки consumers и dependencies
  - .label — подсвеченные значения типов (#a5f3fc)
  - .type-link — кликабельные ссылки в секции Types, стилистически равнозначны .usage-link:
    цвет #a5f3fc, без подчёркивания, подчёркивание при hover, cursor pointer
  - .empty — placeholder для пустых значений (muted italic)
- Секции разделены .section div'ами с border-top разделителем
- Секции: Name (иконка tag), Description (иконка document), Types (иконка cube),
  Usages (иконка file-text), Consumers (иконка download, если есть), Dependencies (иконка upload, если есть)
- Footer (#info-footer): фиксированная зона внизу панели, прибит к низу (аналог #sidebar-footer).
  Padding: 8px 16px, border-top разделитель. Содержит ссылку CODEMANIFEST (.codemanifest-link).
  Не скроллируется — всегда видима.

## Граф (Cytoscape)

Cytoscape.js — библиотека визуализации графов.
Подключается через <script src="/static/cytoscape.min.js">. Сервер раздаёт файл из frontend/static/.
Использовать layout dagre для иерархического отображения.

Стили узлов:
- Скруглённые прямоугольники, форма: round-rectangle
- Градиентный фон #0f172a → #162040 (направление to bottom)
- Бордер #20d4bf (1px), текст #fff
- Тень shadow-blur 8px, shadow-color rgba(32, 212, 191, 0.15), shadow-offset-y 2px
- Transition 0.3s на shadow-blur, border-width, border-color
- Подсветка: teal для выбранного, затемнение остальных

Стили рёбер:
- Цвет rgba(32, 212, 191, 0.5), directed arrows, ширина 0.8, transition 0.3s
- При подсветке (класс highlighted): цвет #20d4bf, ширина 1.5

Подсветка узла (класс highlight):
- Усиленный glow: shadow-blur 20px, shadow-color rgba(32, 212, 191, 0.4), бордер 2px
- Остальные узлы затемняются (opacity 0.15)

Fade-in анимация: @keyframes fadeIn 0.6s ease-out при загрузке графа.

## Sidebar с деревом вложенности

Sidebar фиксированной ширины (260px) слева от графа, стилизован как OS-окно (единый стиль с информационной панелью справа).
- Фон: #0f172a
- Скругление углов: border-radius 8px
- Тень: box-shadow 0 4px 24px rgba(0, 0, 0, 0.4)
- Отступы от краёв основной области: 8px со всех сторон
- Overflow: hidden для корректного скругления
- Содержимое: дерево вложенности cells + кнопка «показать все»
- z-index: 5 (ниже info-wrapper, выше cy)

Заголовок sidebar (titlebar-стиль):
- Текст "Cells" — моноширинный шрифт, font-size 11px, font-weight 600
- Цвет var(--color-brand-muted), text-transform uppercase, letter-spacing 0.05em
- Центрирование: text-align center
- Фон: #1e293b
- Padding: 8px 12px
- Border-bottom: 1px solid rgba(255, 255, 255, 0.05)

Дерево вложенности (контейнер #sidebar-tree):
- Flex: 1 (занимает всё доступное пространство)
- Overflow-y: auto — скроллируется при переполнении
- Scrollbar: тонкий (6px), цвет rgba(255, 255, 255, 0.25), border-radius 3px
- Полностью раскрыто — все узлы видны

Узлы дерева (.tree-node):
- Вложенность показана через tree lines (::before — вертикальная линия, ::after — горизонтальный коннектор)
  с использованием CSS переменной --depth. Корневые узлы (data-depth="0") без линий.
- Иконка (.tree-icon): folder для cells с children, layers (перекрывающиеся прямоугольники) для leaf cells. SVG через data URI.
- Имя cell (.tree-name): короткое (последний сегмент пути), моноширинный шрифт, font-size 12px
- Цвет: var(--color-brand-text)
- White-space: nowrap, overflow: hidden, text-overflow: ellipsis
- Бейдж (.tree-badge): количество зависимостей, показывается только если > 0
- Border-left: 3px solid transparent
- Cursor: pointer
- Hover: фон rgba(32, 212, 191, 0.08)
- Активный узел (.tree-node.active): border-left-color teal, фон rgba(32, 212, 191, 0.12)
- .last-child: вертикальная линия обрезается на середине узла
- Transition: background 0.15s, border-color 0.15s

Подвал sidebar (#sidebar-footer):
- Padding: 8px 16px
- Border-top: 1px solid rgba(255, 255, 255, 0.05)

Кнопка «Show all» (.tree-show-all):
- Моноширинный шрифт, font-size 11px
- Цвет: var(--color-brand-muted)
- Hover: цвет var(--color-brand-teal)
- При клике сбрасывает фильтрацию графа, показывает все элементы, убирает active класс у узлов дерева

Граф (#cy) смещён: left: 276px (8px отступ sidebar + 260px ширина sidebar + 8px gap).

## Панель CODEMANIFEST (#codemanifest-panel)

Панель между левым sidebar и правой info panel:
- Фон: #0f172a, border-radius 8px, box-shadow
- Position: absolute, top/bottom: 8px (просветы как у sidebar и info-wrapper)
- Left: 276px (8px offset sidebar + 260px sidebar + 8px gap = выравнено с #cy)
- Right: 8px от правого края main; если info-wrapper видим — right устанавливается JS динамически
  с учётом позиции info-wrapper + 8px gap
- z-index: 8 (выше cy, ниже info-wrapper)
- Содержимое: titlebar (аналог info-titlebar) + код с номерами строк слева
- Titlebar: фиксирован, не скроллируется
- Номера строк: muted цвет, не выделяются при копировании, отделены от кода тонким border-разделителем
- Скроллинг: только содержимое (код), titlebar остаётся на месте

### Подсветка YAML-синтаксиса

YAML-контент подсвечивается синтаксически:
- Ключи (teal) — имя до двоеточия, включая ключи в двойных кавычках
  и ключи внутри элементов списка
- Комментарии (slate) — строки начинающиеся с # или # после значения
- Разделители (slate) — строки ---
- Операторы многострочности (muted) — | и >
- Логические значения (amber) — true, false, null
- Числа (violet)
- Inline-код в обратных кавычках (cyan) — `param`

Содержимое многострочных блоков (|, >) не подсвечивается —
символ # внутри таких блоков считается текстом, а не комментарием.

### Подсветка строки типа

При навигации к типу из info panel — найденная строка подсвечивается:
- .line-highlighted — teal фон с прозрачностью (rgba(32, 212, 191, 0.15)),
  левый teal бордер 3px, блочный элемент с отрицательными margin для заполнения строки
- Предыдущая подсветка снимается при каждом новом клике на тип
- Автоматический скролл к подсвеченной строке (block: center)
- Переоткрытие CODEMANIFEST через ссылку в футере сбрасывает подсветку

### Usage-ссылки в YAML

Внутри секции Usages: значения, содержащие путь к .md файлу, отображаются как кликабельные ссылки:
- Цвет: #3882f6 (var(--color-brand-blue))
- Подчёркивание: text-decoration: underline
- Hover: цвет #a5f3fc
- Обёрнуты в <a class="usage-link" data-path="path">

### Модальное окно Usage (#usage-overlay + #usage-modal)

При клике на usage-ссылку открывается модальное окно:
- Overlay (#usage-overlay): полупрозрачный тёмный фон rgba(0,0,0,0.6), z-index: 20
- Модальное окно (#usage-modal): центрировано, max-width 80%, max-height 80%
  - Фон: #0f172a, border-radius 8px, box-shadow, border teal
  - Titlebar: аналогично CODEMANIFEST panel
  - Скроллируемое содержимое с кастомным скроллбаром
  - Закрытие: клик на overlay, кнопка ×, клавиша Escape

Markdown-контент (.usage-content):
- Моноширинный шрифт, font-size 13px, line-height 1.6
- h1-h3: белый цвет, разные размеры
- p: цвет #c8d0dc
- code: cyan цвет, полупрозрачный фон
- pre: тёмный фон #0a0e1a, border-radius 6px
- a: синий #3882f6, hover cyan
- ul/ol: стандартные списки
- blockquote: левый teal border, полупрозрачный teal фон
- table: тонкие бордеры, th с фоном