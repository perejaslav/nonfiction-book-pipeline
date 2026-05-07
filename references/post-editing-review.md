# Post-Editing Review: Manuscript Cleanup After Subagent Patching

## Зачем этот документ

После субагентного патчинга manuscript.md возникают три класса дефектов, которые не ловятся стандартной регуляркой и требуют ручной верификации контекста.

---

## Класс 1: Субагентное удаление больше чем нужно

**Симптом:** after a `patch(mode=replace)` targeting a known artifact (e.g., `||` separator), a nearby paragraph or sentence disappears or its beginning is truncated.

**Причина:** субагент патчил по old_string, нашёл совпадение, но surrounding context — несколько предложений до или после — были частью того же paragraph и тоже исчезли.

**Пример из сессии «Держава Ахеменидов» (2026-05-04):**
- Абзац про цилиндр Кира содержал три `||` — это были разделители вставных фрагментов.
- Патч убрал все три `||`, но вместе с ними исчезло начало следующего предложения: «они должны были увидеть...»
- Восстановление: через `patch` с полным текстом абзаца.

**Протокол верификации после bulk-патчинга:**

```python
# 1. После любого bulk-прохода субагента на manuscript.md
# Проверить: не пропал ли текст между логическими блоками

# 2. Конкретная проверка для || в длинных абзацах
import re

with open('manuscript.md') as f:
    lines = f.readlines()

# Найти абзацы с 2+ ||
paragraphs_with_double_pipe = []
current_para = []
current_line = 0

for i, line in enumerate(lines, 1):
    if line.strip() == '':
        if current_para:
            para_text = ''.join(current_para)
            pipe_count = para_text.count('||')
            if pipe_count >= 2:
                paragraphs_with_double_pipe.append((current_line, pipe_count, para_text[:100]))
        current_para = []
        current_line = i
    else:
        current_para.append(line)

if paragraphs_with_double_pipe:
    print(f"⚠️  Абзацы с 2+ ||: {len(paragraphs_with_double_pipe)}")
    for start, count, preview in paragraphs_with_double_pipe:
        print(f"   Строка {start}: {count}x || — {preview!r}")
else:
    print("✅ Нет абзацев с множественными ||")
```

**Правило:** если `||` встречается 2+ раз в одном абзаце — это разделители вставных фрагментов, а не механические склейки. Лечение: превратить в текстовые переходы («Стоит присмотреться к конкретным формулировкам текста», «Это наблюдение важно, потому что...»), а не удалять.

---

## Класс 2: Orphaned paragraphs после удаления дублей

**Симптом:** after removing a duplicate block, an introductory sentence remains orphaned — it now leads nowhere or repeats material from the previous paragraph.

**Пример из сессии «Держава Ахеменидов»:**
- Блок «В следующие два года Александр занял Малую Азию...» был продублирован в главе 25 — он появлялся ДО блока «Два года лёгких побед» и ПОСЛЕ.
- Удалили дубликат перед блоком «Два года лёгких побед», но остался orphaned абзац: «Совет персидских сатрапов накануне Граника — ещё одна страница, заслуживающая внимания.» — который теперь висит без продолжения.

**Протокол:**

```python
# После удаления дублей — проверить на осиротевшие заголовки
import re

with open('manuscript.md') as f:
    content = f.read()

# Найти "ещё одна страница", "ещё один" — типичные маркеры orphaned-intro
orphaned_markers = [
    'ещё одна страница',
    'ещё один',
    'следующий эпизод',
    'перейдём к',
    'рассмотрим теперь',
]

for marker in orphaned_markers:
    positions = [m.start() for m in re.finditer(re.escape(marker), content)]
    for pos in positions:
        # Найти границы абзаца
        para_start = content.rfind('\n\n', 0, pos) + 2
        para_end = content.find('\n\n', pos)
        para = content[para_start:para_end]
        # Проверить: за абзацем идёт новый заголовок или такой же маркер?
        next_block = content[para_end:para_end+200]
        if re.match(r'\n## ', next_block) or marker in next_block:
            print(f"⚠️  Orphaned: {marker!r}")
            print(f"   Контекст: {para[:80]!r}")
```

---

## Класс 3: Bulk-субагентный патчинг ломает структуру

**Симптом:** при запуске 2 субагентов на патчинг разных частей manuscript.md возможна ситуация: субагент A и субагент B патчат один и тот же файл без координации. Субагент A удаляет 30-строчный блок X. Субагент B патчит old_string, который находится ВНУТРИ блока X — совпадение не находится → субагент B сообщает «not found» → файл остаётся в промежуточном состоянии.

**Профилактика:**
- Патчить вручную через `patch` ведущим.
- Если без субагента не обойтись — давать ему ОДНУ категорию правок и один диапазон строк.
- После любого субагентного прохода — верификация: grep на старую фразу, проверка word count.

---

## Класс 4: Двойные заголовки в начале manuscript

**Симптом:** после сборки или субагентного патчинга в начале файла:
```
## Пролог
## Пролог: Пламя над Персеполем
```
Frontmatter (`title` в YAML) уже создаёт титульный лист. Ручной `## Название` после frontmatter — избыточный дубликат.

**Лечение:** patch с удалением первого (более краткого) варианта.
```bash
grep -n '^## ' manuscript.md | head -5
```

---

## Класс 5: Нумерованные подразделы на уровне глав (`## 1.`)

**Симптом:** нумерованные секции (`## 1.`, `## 2.`) стоят на одном уровне с `## Глава X.` — нарушение иерархии.

**Правильная иерархия (4 уровня):**
```
## Часть I. Рождение державы   ← часть
## Глава 1. До Кира            ← глава
### 1. Поход на Египет          ← подраздел (НЕ ## 1.)
```

**Диагностика:**
```bash
grep -n '^## [0-9]' manuscript.md
```

**Исправление (## N. → ### N.):**
```python
import re
with open('manuscript.md') as f: text = f.read()
text = re.sub(r'^## (\d+)\. ', r'### \1. ', text, flags=re.MULTILINE)
with open('manuscript.md', 'w') as f: f.write(text)
```

---

## Класс 6: Overclaiming — «копировали» в Influence Ladder

**Симптом:** формулировки «копировали», «скопировали» создают впечатление прямой технической передачи без изменений.

```
❌ Селевкиды копировали ахеменидскую администрацию.
✅ Селевкиды переняли ахеменидскую администрацию.
✅ Парфяне унаследовали ахеменидский церемониал.
```

**Ключевые замены:**

| Слишком жёстко | Точнее |
|---|---|
| копировали | переняли, унаследовали, воспроизвели |
| скопировали | адаптировали, переосмыслили |
| заимствовали напрямую | использовали близкие принципы |

**Поиск:** `grep -n 'копировали' manuscript.md` — каждое вхождение проверить.

---

## Класс 7: Хронологический зигзаг при удалении дублей

**Симптом:** при удалении дублирующего блока「新текст вводит хронологическую линию, которая уже описана в другом месте главы.

**Пример (глава 25 «Держава Ахеменидов»):**
- Удалили «В следующие два года...» → orphaned «Два года лёгких побед» теперь дублирует сжатый текст про тот же период.
- Решение: объединить оба потока в единый хронологический порядок, сохранив все уникальные детали.

**Протокол:**
1. При удалении дубля — прочитать ±50 строк вокруг
2. Проверить перекрытие по содержанию
3. Объединить в единый поток
4. Убедиться:「新текст не создаёт хронологического конфликта

---

## Обновлённый чеклист верификации

```python
import re, subprocess
path = "manuscript.md"
with open(path) as f: text = f.read()
checks = {
    "||": len(re.findall(r'\|\|', text)),
    "fact_": len(re.findall(r'fact_\d+', text)),
    "confidence": text.count("confidence"),
    "страница Клита": text.count("страница Клита"),
    "копировали": text.count("копировали"),
    "## N. (нумерованные подразделы)": len(re.findall(r'^## \d+\.', text, re.MULTILINE)),
    "двойной заголовок Пролога": len(re.findall(r'^## Пролог\n## Пролог:', text)),
    "--- separators": text.count("\n---\n"),
    "CJK": len(re.findall(r'[\u4e00-\u9fff]', text)),
    "orphaned intro": sum(1 for m in ['ещё одна страница', 'ещё один'] if m in text),
}
for k, v in checks.items():
    print(f"{'OK' if v == 0 else 'FIX'} {v:3d}  {k}")
r = subprocess.run(["wc", "-w", path], capture_output=True, text=True)
print(f"Words: {r.stdout.strip()}")
```

**Пороги:** `||`, `fact_`, `confidence`, `страница Клита` > 0 = чинить немедленно. `---` > 1 = удалить лишние. `## N.` > 0 = понизить до `### N.`.

---

## Чеклист верификации после патчинга manuscript.md

```python
import re, subprocess

path = "manuscript.md"
with open(path) as f: text = f.read()

checks = {
    "|| (pipe separators)": len(re.findall(r'\|\|', text)),
    "fact_ markers": len(re.findall(r'fact_\d+', text)),
    "§ in headings": len(re.findall(r'^## § ', text, re.MULTILINE)),
    "--- separators": text.count("\n---\n"),
    "CJK chars": len(re.findall(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]', text)),
    "medium confidence": text.count("medium confidence"),
    "важно понимать": text.count("важно понимать"),
    "страница Клита": text.count("страница Клита"),
    "orphaned intro markers": sum(1 for m in ['ещё одна страница', 'ещё один'] if m in text),
}

print("=== Post-patching verification ===")
for k, v in checks.items():
    status = "✅" if v == 0 else f"⚠️  x{v}"
    print(f"  {status}  {k}")

r = subprocess.run(["wc", "-w", path], capture_output=True, text=True)
print(f"  Слов: {r.stdout.strip()}")

# Проверка: абзацы с 2+ ||
para_count = 0
for para in text.split('\n\n'):
    if para.count('||') >= 2:
        para_count += 1
        print(f"  ⚠️  Абзац с 2+ ||: {para[:60]!r}")
if para_count == 0:
    print("  ✅ Нет абзацев с множественными ||")
```

**Критические пороги:** любой nonzero для `||`, `fact_`, `medium confidence`, `страница Клита` — немедленная правка. `CJK > 0` — проверить, не декоративные символы. `---` — максимум 1 (перед финальным блоком).
