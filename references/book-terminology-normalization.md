# Terminology Normalization for Russian-Language Archaeology Books

## Проблема

При написании книги о ближневосточной археологии на русском языке возникает конфликт между русской академической традицией (транслитерация турецких названий: Гёбекли-Тепе, Карахан-Тепе) и международным научным стандартом (латинское написание: Göbeklitepe, Karahantepe).

## Установленный стандарт (Taş Tepeler book)

По решению пользователя: **использовать турецкое латинское написание везде**, включая русскоязычный текст.

### Названия памятников

| Ок | Нельзя |
|----|--------|
| Göbeklitepe | Гёбекли-Тепе, Гебекли-Тепе, Гёбекли-тепе |
| Karahantepe | Карахан-Тепе, Карахан-тепе, Карахантепе |
| Çakmaktepe | Чакмактепе |
| Sefertepe | Сефертепе, Сефер-Тепе |
| Gürcütepe | Гюрджютепе |
| Harbetsuvan Tepesi | Харбетсуван, Harbetsuvan-Тепеси |
| Sayburç | Сайбурч |
| Nevalı Çori | Невалы-Чори, Невали Чори |
| Ayanlar Höyük | Аянлар-Хёюк |
| Yoğunburç | Йоунбурч |
| Yenimahalle | Йенимахалле |
| Söğüt Tarlası | Сёют-Тарласы |
| Biris Mezarlığı | Бирис-Мез арлыгы |
| Taş Tepeler | Таш-Тепелер |
| Çatalhöyük | Чатал-Хююк |
| Çayönü | Чайоню |

### Склонение турецких названий (критично)

**Правило:** турецкие названия НЕ склоняются. Падеж переносится на родовое слово.

| Ок | Нельзя |
|----|--------|
| в поселении Sayburç | в Sayburçе, Sayburçа |
| на памятнике Karahantepe | на Karahantepeе, из Karahantepeа |
| с территории Çatalhöyük | с Çatalhöyükа, Çatalhöyükом |
| в Harbetsuvan | в Harbetsuvanе, из Harbetsuvanа |
| на Yoğunburç | на Yoğunburçе |
| рядом с памятником Sayburç | с Sayburçм |

### Типичные дефекты при генерации

1. **Смешанный шрифт:** первая буква кириллическая, остальное — латиница (Таş Tepeler → Taş Tepeler)
2. **Дефисные формы:** Гёбекли-Тепе → Göbeklitepe (дефис — маркер русской транслитерации)
3. **Английские слова в русском контексте:** civilisation → цивилизация
4. **Оборванные склонения:** Sayburçм → с памятником Sayburç, Harbetsuvanа → Harbetsuvan

### Регулярные выражения для поиска

```python
# Russian forms with hyphen
r'[ГГККСЧ][а-яё]*-[ТТ][еа-яё]+'

# Declined Turkish names (Latin + Russian case ending)
r'\b[A-ZÇŞĞİÖÜ][a-zçşğıöü]+[ауеы]'

# Mixed script (Cyrillic then Latin)
r'[А-ЯЁ][a-zçşğıöü]+\s'

# Latin words in Russian text (4+ letters, not proper nouns)
r'\b[a-z]{4,}\b'
```

### Сценарий поиска и замены (Python)

```python
import os, re

FIXES = {
    # Russian forms → Turkish standard
    'Гёбекли-тепе': 'Göbeklitepe',
    'Карахан-тепе': 'Karahantepe',
    'Таш-Тепелер': 'Taş Tepeler',
    'Невалы-Чори': 'Nevalı Çori',
    'Сайбурч': 'Sayburç',
    'Харбетсуван': 'Harbetsuvan',
    'Чакмактепе': 'Çakmaktepe',
    'Сефертепе': 'Sefertepe',
    'Курт-Тепе': 'Kurt Tepe',
    'Ташлы-Тепе': 'Taşlı Tepe',
    'Гюрджютепе': 'Gürcütepe',
    'Чатал-Хююк': 'Çatalhöyük',
    'Чайоню': 'Çayönü',
    
    # Declined forms → generic word pattern
    'на Sayburç': 'на памятнике Sayburç',
    'в Sayburç': 'в поселении Sayburç',
    'на Harbetsuvan': 'на Harbetsuvan',
    'с Çatalhöyük': 'с территории Çatalhöyük',
    'с Sayburçм': 'с памятником Sayburç',
    'на Yoğunburçе': 'на Yoğunburç',
    
    # English remnants
    'civilisation': 'цивилизация',
    
    # Mixed script
    'Таş ': 'Taş ',
}

for f in all_md_files:
    with open(f) as fh:
        text = fh.read()
    for old, new in FIXES.items():
        text = text.replace(old, new)
    with open(f, 'w') as fh:
        fh.write(text)
```
