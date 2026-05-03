# Валидация JSON-источников в NFP

## Структура facts.json

```json
{
  "metadata": {
    "book": "...",
    "version": "...",
    "last_updated": "..."
  },
  "facts": [
    {
      "id": "fact_001",
      "category": "date|name|term|event|number",
      "claim": "Утверждение",
      "source_type": "primary|secondary|legend",
      "source_ref": "Ссылка",
      "confidence": "high|medium|low",
      "verified": true|false,
      "verification_method": "...",
      "verification_note": "..."
    }
  ]
}
```

**Это словарь с ключами `metadata` и `facts`**, а не плоский массив.

## Частые ошибки при ручном редактировании

### 1. Одинарные кавычки как разделитель строки

```json
// ❌ Невалидно
"verification_note": 'Атрибуция традиции...'

// ✓ Валидно
"verification_note": "Атрибуция традиции..."
```

Одинарные кавычки не являются валидным JSON-разделителем строки. Парсер выдаёт `Expecting ',' delimiter`.

### 2. Неэкранированные внутренние кавычки

```json
// ❌ Невалидно — вложенные кавычки не экранированы
"verification_note": "Использовать как "по преданию"."

// ✓ Валидно — внутренние кавычки экранированы
"verification_note": "Использовать как \"по преданию\"."
```

### 3. Фигурные кавычки (curly quotes) как часть значения

```json
// ❌ Невалидно — U+201E („) выглядит как кавычка, но не закрывает строку
"verification_note": "Использовать как „по преданию"."

// ✓ Валидно — фигурные кавычки внутри строки без экранирования
"verification_note": "Использовать как \u201eпо преданию\u201c."
// или просто заменить на ASCII
"verification_note": "Использовать как \"по преданию\"."
```

## Валидация — всегда перед использованием

```python
import json

def validate_facts(path):
    with open(path) as f:
        content = f.read()
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        print(f"JSON ERROR at pos {e.pos}: '{content[e.pos-5:e.pos+5]}'")
        return None
    return data

# Базовые проверки
data = validate_facts('foundation/facts.json')
if data is None:
    raise ValueError("facts.json невалиден")

facts = data['facts']
print(f"Фактов: {len(facts)}")
print(f"Категории: {set(f['category'] for f in facts)}")
```

## Контрольный список после ручного редактирования

- [ ] `json.loads()` проходит без ошибок
- [ ] Файл читается и распознаётся как словарь с `metadata` и `facts`
- [ ] Количество фактов соответствует ожидаемому
- [ ] Все категории известны: `date`, `name`, `term`, `event`, `number`
- [ ] Нет одинарных кавычек в строковых значениях
- [ ] Нет неэкранированных вложенных кавычек
