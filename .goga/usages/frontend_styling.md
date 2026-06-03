# Стили SPA — тёмная тема qarium.ru/goga

Требования к визуальному оформлению SPA.

## Структура SPA

SPA состоит из одного HTML-файла с встроенными CSS и JS.
Без сборки — JS-библиотеки встроены inline из static/.

Статические ассеты в static/:
- logo.png, favicon.png — брендированные ресурсы. Референс: qarium.ru/goga. Скачать с сайта: логотип из хедера, favicon из вкладки браузера.
- icon-telegram.svg, icon-github.svg, icon-email.svg — иконки контактов. Inline SVG, соответствующие иконкам из qarium.ru/goga.
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
- Содержимое форматируется как YAML: ключи (yaml-key) — цвет teal, строки (yaml-string) — #a5f3fc, null (yaml-null) — muted italic
- Поля: name, description, types, consumers, dependencies

## Граф (Cytoscape)

Cytoscape.js — библиотека визуализации графов.
Встроена inline в HTML из static/cytoscape.min.js. Подключить через <script> тег.
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

Sidebar фиксированной ширины (260px) слева от графа.
- Фон: var(--color-brand-card) (#121830)
- Граница справа: 1px solid rgba(255, 255, 255, 0.05)
- Высота: заполняет основную область (ниже хедера, выше футера)
- Содержимое: дерево вложенности cells + кнопка «показать все»
- z-index: 5 (ниже info-wrapper, выше cy)

Заголовок sidebar:
- Текст "Cells" — моноширинный шрифт, font-size 11px, font-weight 600
- Цвет var(--color-brand-muted), text-transform uppercase, letter-spacing 0.05em
- Padding: 12px 16px
- Border-bottom: 1px solid rgba(255, 255, 255, 0.05)

Дерево вложенности (контейнер #sidebar-tree):
- Flex: 1 (занимает всё доступное пространство)
- Overflow-y: auto — скроллируется при переполнении
- Scrollbar: тонкий (4px), цвет rgba(255, 255, 255, 0.1), border-radius 2px
- Полностью раскрыто — все узлы видны

Узлы дерева (.tree-node):
- Вложенность показана через padding-left (16px + 16px за уровень)
- Имя cell: короткое (последний сегмент пути), моноширинный шрифт, font-size 12px
- Цвет: var(--color-brand-text)
- White-space: nowrap, overflow: hidden, text-overflow: ellipsis
- Border-left: 3px solid transparent
- Cursor: pointer
- Hover: фон rgba(32, 212, 191, 0.08)
- Активный узел (.tree-node.active): border-left-color teal, фон rgba(32, 212, 191, 0.12)
- Transition: background 0.15s, border-color 0.15s

Подвал sidebar (#sidebar-footer):
- Padding: 8px 16px
- Border-top: 1px solid rgba(255, 255, 255, 0.05)

Кнопка «Show all» (.tree-show-all):
- Моноширинный шрифт, font-size 11px
- Цвет: var(--color-brand-muted)
- Hover: цвет var(--color-brand-teal)
- При клике сбрасывает подсветку в графе и убирает active класс у узлов дерева

Граф (#cy) смещён: left: 260px (ширина sidebar).