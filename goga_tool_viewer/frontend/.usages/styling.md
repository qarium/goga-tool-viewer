# Стили SPA — тёмная тема qarium.ru/goga

Для потребителей frontend — визуальные характеристики SPA.

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

- Узлы: скруглённые прямоугольники, градиентный фон #0f172a → #162040 (направление to bottom), бордер #20d4bf (1px), текст #fff
- Узлы: тень shadow-blur 8px, shadow-color rgba(32, 212, 191, 0.15), shadow-offset-y 2px
- Узлы: transition 0.3s на shadow-blur, border-width, border-color
- Рёбра: цвет rgba(32, 212, 191, 0.5), directed arrows, ширина 0.8, transition 0.3s
- Рёбра при подсветке (класс highlighted): цвет #20d4bf, ширина 1.5
- Подсветка: узел с классом highlight получает усиленный glow (shadow-blur 20px, shadow-color rgba(32, 212, 191, 0.4)), бордер 2px; остальные затемняются (opacity 0.15)
- Fade-in анимация: @keyframes fadeIn 0.6s ease-out при загрузке графа