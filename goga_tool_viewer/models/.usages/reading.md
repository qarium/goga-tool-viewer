# Чтение данных cell из JSON

Для потребителей model — как создавать экземпляры CellData из JSON-структуры.

## Парсинг одной cell

JSON-объект cell содержит поля:
- `"cell"` — имя cell → `CellData.name`
- `"description"` — описание → `CellData.description`
- `"types"` — массив типов → `CellData.types`
- `"usages"` — массив практик → `CellData.usages`
- `"children"` — массив вложенных cells → `CellData.children` (рекурсивно)
- `"dependencies"` — объект, где ключ = путь к cell, значение = `{types: [], usages: []}` → `CellData.dependencies`

## Преобразование dependencies

Dependencies в JSON — это dict. Для каждого ключа (путь к cell) создать `DependencyInfo`:
- `from_cell` = текущая cell
- `to_cell` = ключ из dict
- `types` = значение["types"]
- `usages` = значение["usages"]

## Построение CellGraph

Рекурсивно обойти корневой список JSON, собрать все CellData (включая children)
и все DependencyInfo в плоские списки.
