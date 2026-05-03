# facts.json: типичные ошибки и ремонт

## Структура

```json
{
  "metadata": { "book": "...", "version": "...", "last_updated": "..." },
  "facts": [
    {
      "id": "fact_001",
      "category": "date|name|term|event|number",
      "claim": "...",
      "source_type": "primary|secondary",
      "source_ref": "...",
      "confidence": "high|medium|low",
      "verified": true|false,
      "verification_note": "..."        // опционально
    }
  ]
}
```

**Всегда** — два корневых ключа: `metadata` и `facts`. Facts — массив, не словарь.

---

## Валидация (перед любым использованием)

```python
import json
with open('facts.json') as f:
    data = json.load(f)
# Если не упало — файл валиден
print(f"Фактов: {len(data['facts'])}")
```

---

## Частые ошибки и ремонт

### 1. Одинарные кавычки как разделитель строки

**Симптом:** `json.JSONDecodeError: Expecting ',' delimiter`

**Причина:** значение в JSON начато с `'...'` вместо `"..."`.

```json
"verification_note": 'Атрибуция традиции afternoon tea...'
```

**Ремонт:** заменить внешние одинарные кавычки на двойные.

```python
import json

with open('facts.json') as f:
    content = f.read()

lines = content.split('\n')
# Найти строку где "verification_note": начинается с '
for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped.startswith('"verification_note":') and stripped[20] == "'":
        # Исправить: заменить первый ' на "
        lines[i] = line.replace(': \'', ': "', 1).rstrip() + '"'
        # Убрать trailing '
        lines[i] = lines[i].rstrip("'") + '"'

content = '\n'.join(lines)
with open('facts.json', 'w') as f:
    f.write(content)
```

### 2. Неэкранированные внутренние кавычки

**Симптом:** та же ошибка на позиции внутри строки.

**Причина:** внутри строкового значения JSON есть `"..."` без экранирования.

```json
"verification_note": "Атрибуция традиции... Использовать как \"по преданию\"."
```

```python
# Нужно \\"  (backslash-quote), не "
fixed = line.replace('"по преданию"', '\\"по преданию\\"')
```

**Байтовый детект проблемы:**
```python
enc = line.encode('utf-8')
print(' '.join(f'{b:02x}' for b in enc[-30:]))
# 5c 22 = экранированная кавычка (правильно)
# 22   = неэкранированная кавычка (ошибка)
```

### 3. Фигурные кавычки юникода

**Причина:** `„` (U+201E) или `"` (U+201C) внутри JSON-строки.

```json
"verification_note": "Использовать как „по преданию"."
```

Эти символы валидны в UTF-8, но если они появились при копировании из Word/Google Docs, они могут чередоваться с ASCII-кавычками и нарушать структуру.

**Ремонт:** заменить на ASCII или экранировать:
```python
line = line.replace('\u201e', '"').replace('\u201c', '"')  # на прямые
# или на экранированные:
line = line.replace('\u201e', '\\"').replace('\u201c', '\\"')
```

### 4. Двойной экранирование (backslash-backslash-quote)

**Симптом:** `JSONDecodeError` после ремонта п.1.

**Причина:** при патче через строковую замену `\\"` → `\\\"` вместо `"` → `\"`.

**Байтовый детект:**
```python
# 5c 5c 22 = два бэкслеша + кавычка (неправильно)
# 5c 22    = один бэкслеш + кавычка (правильно)
```

**Ремонт:** прочитать файл как текст, заменить `\\"` на `\"`:
```python
with open('facts.json') as f:
    content = f.read()
# Убрать лишний бэкслеш
content = content.replace('\\\\"', '\\"')  # \\" -> \"
with open('facts.json', 'w') as f:
    f.write(content)
```

---

## Порядок диагностики сломанного JSON

1. `python3 -c "import json; json.load(open('facts.json'))"` — показать точную позицию ошибки
2. Определить номер строки: `sum(len(l)+1 for l in lines[:n-1])` — накопительная сумма длин предыдущих строк
3. Прочитать файл как bytes, показать hex контекст вокруг позиции ошибки
4. Определить тип ошибки (п.1–4 выше)
5. Исправить
6. Перепроверить `json.loads()`

---

## Проверочный скрипт (финальный)

```python
import json, re

try:
    with open('facts.json') as f:
        data = json.load(f)
    facts = data['facts']
    print(f"✓ JSON валиден. Фактов: {len(facts)}")
    print(f"  Категории: {set(f['category'] for f in facts)}")
    print(f"  Verified: {sum(1 for f in facts if f.get('verified'))}/{len(facts)}")
except json.JSONDecodeError as e:
    print(f"✗ JSON ERROR: {e}")
    print(f"  Pos {e.pos}: {repr(content[max(0,e.pos-20):e.pos+20])}")
```
