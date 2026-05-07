# Cleanup Patterns — чистка текста после расширения

Паттерны, обнаруженные при расширении глав разных книг (актуальны после любого прохода субагентов).
Всегда применять после каждого прохода расширения главы и после финальной сборки manuscript.md.

## Сборочные артефакты (manuscript assembly)

При конкатенации глав в manuscript.md возникают специфические артефакты, не встречающиеся в отдельных главах.

### Pipe-rows `|`
Строки, начинающиеся с `|`, — результат некорректного split при сборке:
```
|Набонид пришёл к власти в 556 году...
```
**Лечение:** `\n|Text` → ` Text` (объединить с предыдущим абзацем):
```python
text = re.sub(r'\n\|([А-ЯA-ZЁ])', r' \1', text)
```

### Видимые `\n`
Служебные `\n` из шаблонных строк, попавшие в текст. Найти: `re.findall(r'\\n', text)`. Удалить: `text.replace(r'\n', '')`.

### Fact-маркеры
Служебные ссылки `fact_XX_YY` из черновиков субагентов:
```python
text = text.replace('fact_06_03', '')
```

### Характерные слова-артефакты

| Артефакт | Замена |
|----------|--------|
| `общемиперский` | `общеимперский` |
| `актуально-вавилонская` | `вавилонская новогодняя` |
| `civilisation` (в русском тексте) | `цивилизации` |

### Дублированные абзацы
Характерный пример — центральная идея «империя как мозаика», повторяющаяся в соседних абзацах после расширения и склейки. Лечение: найти через `grep` дубликаты, удалить повтор.

### Быстрая проверка всех сборочных артефактов
```python
import re
path = 'manuscript.md'
with open(path) as f: text = f.read()
for k, v in {'pipe_rows |': len(re.findall(r'\n\|', text)),
             r'\\n': len(re.findall(r'\\n', text)),
             'fact_markers': len(re.findall(r'fact_\w+', text)),
             'общемиперский': len(re.findall(r'общемиперский', text)),
             'civilisation': len(re.findall(r'civilisation', text))}.items():
    if v: print(f"{k}: {v}")
```

## Mixed Writing Systems

Китайские/японские символы, вплетённые в русский текст без необходимости — систематический фейл LLM:

| Найдено | Замена |
|---------|--------|
| `大多数` (кит. «большинство») | `многие` |
| `同時` (яп. «одновременно») | `в то же время` |
| `正常` (нормальной) | `обычной` |
| Любые `\u4e00-\u9fff` | Перевести на русский |

**Проверка:**
```python
import re
with open('chapter.md') as f: text = f.read()
cjk = re.findall(r'[\u4e00-\u9fff]+', text)
if cjk: print(f"CJK найдены: {set(cjk)}")
```

## English Words in Russian Context

Любое English-слово (4+ букв) в строке с кириллицей — под подозрением.

**Автоматический скрипт проверки:**
```python
import re

with open('manuscript.md') as f:
    text = f.read()

ok_words = {
    'title', 'author', 'date', 'german', 'iii', 'xx', 'xxv', 'xxi', 'xii',
    'xiv', 'xix', 'etcs', 'etc', 'de', 'la', 'le', 'van', 'von',
    'when', 'then', 'more', 'most', 'only', 'also', 'have', 'were',
    'from', 'they', 'them', 'their', 'with', 'that', 'this', 'which',
    'what', 'where', 'each', 'every', 'some', 'back', 'over', 'down',
    'here', 'than', 'into', 'such', 'how', 'once'
}

eng_words = re.findall(r'\b[a-zA-Z]{4,}\b', text)
eng_filtered = [w for w in eng_words if w.lower() not in ok_words]

if eng_filtered:
    print(f"Осталось English-слов: {len(eng_filtered)}")
    print(eng_filtered)
else:
    print("Текст чист от English")
```

## Таблица замен English → Russian (100+ паттернов)

| English | Русский |
|---------|---------|
| `assembly` | ассамблея |
| `simultaneously` | одновременно |
| `prolonged` | затяжной |
| `funcionaba` | работала |
| `safeguards` | гарантии |
| `religious duty` | религиозный долг |
| `military` | военная |
| `security` | безопасность |
| `strange` | странной |
| `often` | часто |
| `rarely` | редко |
| `manager` | управляющий |
| `payroll` | штат |
| `corvee` | барщина |
| `concepts` | концепции |
| `practical problems` | практические проблемы |
| `effective` | эффективные |
| `separate` | отдельные |
| `personality` | личности |
| `instance` | пример |
| `too distant` | слишком далёкий |
| `commander armies` | командующий войсками |
| `inventor` | изобретатель |
| `troublemaker` | источник проблем |
| `later` | позже |
| `contrary` | напротив |
| `trouble making` | создание проблем |
| `purpose` | цель |
| `binding` | обязательны |
| `solitary` | в одиночку |
| `specific` | конкретные |
| `performed` | совершаемые |
| `machine` | машина |
| `quality` | качество |
| `supposed to` | должны были |
| `religions` (сущ.) | религиоведы |
| `pragmatic` | прагматичной |
| `useful` | полезны |
| `approachable` | доступны |
| `aspiration` | стремление |
| `influence` | влияние |
| `intriguing` | увлекательная |
| `principles` | принципы |
| `figurehead` | номинальный правитель |
| `executive` | управляющий |
| `petty` | мелкая |
| `limits` | пределы |
| `arbitrarily` | произвольно |
| `domain` | сфера деятельности |
| `compassion` | сострадание |
| `parties` | части |
| `divorced` | оторваны |
| `German` (экспедиция) | немецкая |
| `Madison` | Мэдисон |
| `night after night` | ночь за ночью |
| `year after year` | год за годом |
| `centuries` | столетий |
| `centuries ago` | века назад |
| `documented` | зафиксированный |
| `selling` | продавали |
| `biodiversity` | биоразнообразие |
| `population` | население |
| `not` (в русском предложении) | частица «не» |
| `once` | однажды |
| `life` | жизнь |
| `death` | смерть |
| `world` | мир |
| `king` | царь |
| `gods` | боги |
| `human` | человеческий |
| `state` | государство |
| `time` | время |
| `work` | работа |
| `power` | власть |
| `law` | закон |
| `system` | система |
| `form` | форма |
| `true` | истинный |
| `feared` | боялись |
| `needed` | нужный |
| `powerful` | могущественный |
| `divine` | божественный |
| `directly` | напрямую |
| `properly` | должным образом |
| `known` | известный |
| `meant` | означало |
| `made` | сделано |
| `became` | стал |
| `gave` | дал |
| `said` | сказал |
| `held` | держал |
| `called` | назывался |
| `born` | рождён |
| `lived` | прожил |
| `stood` | стоял |
| `fell` | упал |
| `way` | путь |
| `used` | использовал |
| `long` | долгий |
| `short` | короткий |
| `big` | большой |
| `small` | маленький |
| `wide` | широкий |
| `narrow` | узкий |
| `deep` | глубокий |
| `strong` | сильный |
| `weak` | слабый |
| `bright` | яркий |
| `huge` | огромный |
| `plain` | простой |
| `complex` | сложный |
| `simple` | простой |
| `natural` | естественный |
| `earthly` | земной |
| `cosmic` | космический |
| `sacred` | священный |
| `holy` | святой |
| `normal` | нормальный |
| `special` | особый |
| `central` | центральный |
| `local` | местный |
| `ancient` | древний |
| `modern` | современный |
| `original` | первоначальный |
| `primary` | первичный |
| `male` | мужской |
| `female` | женский |
| `public` | публичный |
| `private` | частный |
| `legal` | законный |
| `possible` | возможный |
| `impossible` | невозможный |
| `necessary` | необходимый |
| `important` | важный |
| `success` | успех |
| `failure` | неудача |
| `progress` | прогресс |

**Оставлять без изменений:**
- Римские цифры (XVII, XVIII, VIII)
- Научные латинские термины (Camellia sinensis, gidim, ziqqurratu)
- Латинские термины в кавычках (ius primae noctis)
- Аккадские/шумерские транслитерации (Ilum, gidim)
- Аббревиатуры (ETCSL, GPS)
- URL (https://...)

## Постпроцессинговая ревизия (после вычитки субагентами)

Субагенты-вычитки находят **реальные** проблемы. Исправления обязательны. Порядок:

1. **English-вкрапления** → заменить по таблице
2. **Дублирующийся контент** (тема X в главах A и B) → сократить вторичную, сохранить уникальное
3. **Мосты** → вставить 2–3 предложения где нарратив обрывается
4. **Библиография** <6 источников → расширить
5. **Заголовки с English** → перевести
6. **Хук во Введении** → добавить кинематографичную сцену если отсутствует
7. **Word count** → убедиться в целевом диапазоне (±5%)

**Чеклист перед финальной сборкой:**
- [ ] CJK = 0
- [ ] English-слов (реальных) ≈ 0
- [ ] Нет дублирующегося контента
- [ ] Мосты между всеми главами
- [ ] Библиография ≥ 6 источников
- [ ] Заголовки стандартизированы
- [ ] Хук во Введении
- [ ] Word count в диапазоне
