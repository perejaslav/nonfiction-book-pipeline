# Word Count Plan

## Auto-Calculation

Для автоматического расчёта использовать скрипт:

```bash
python3 scripts/calc_word_count.py foundation/structure.md
```

Скрипт парсит `structure.md`, определяет тип каждой главы и считает диапазоны слов по формуле: **baseline × density multiplier**. Результат — заполненный план ниже.

Если структура ещё не готова, заполнить вручную по таблицам.

## Chapter Types — Baseline Ranges

| Type | Description | Min words | Max words |
|------|-------------|-----------|-----------|
| intro | Вводная / opening | 2 000 | 3 500 |
| overview | Основная обзорная | 3 000 | 4 500 |
| research | Основная исследовательская | 4 000 | 6 000 |
| practical | Основная практическая | 3 500 | 5 000 |
| narrative | Основная повествовательная | 4 000 | 6 000 |
| conclusion | Заключительная | 2 000 | 3 500 |

## Density Multipliers

| Density | Adjustment |
|---------|-----------|
| обзорная (survey) | −20% |
| практическая (practical) | base |
| исследовательская (research) | +20% |
| академическая (academic) | +30% |
| повествовательная (narrative) | +10% |

## Auto-Calculated Summary

_(заполняется скриптом `calc_word_count.py`)_

```
Chapters:     N
Total range:  XX,XXX – YY,YYY words
Average:      X,XXX – Y,YYY words/chapter
```

## Per-Chapter Plan

| Chapter | Type | Density | Min | Max | Planned | Drafted | Deficit | Status |
|---------|------|---------|-----|-----|---------|---------|---------|--------|
| Ch.01 | | | | | | | | |
| Ch.02 | | | | | | | | |
