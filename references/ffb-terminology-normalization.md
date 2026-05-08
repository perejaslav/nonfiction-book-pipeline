# FFB: Terminology Normalization Pass (Foreign Names in Russian-Language Manuscripts)

## Problem

After drafting, a Russian-language manuscript about foreign (especially Turkish) subject matter is virtually guaranteed to contain **inconsistent terminology**. Multiple variant forms of the same name appear across chapters written by different sub-agents:

- **Russian transliterations vs. original script:** `Гебекли-Тепе / Гёбекли-Тепе` vs. `Göbeklitepe`
- **Hyphenated vs. unhyphenated:** `Карахан-тепе` vs. `Karahantepe`
- **Mixed case endings on foreign names:** `на Sayburçа`, `в Göbeklitepeе`, `из Çatalhöyükа`
- **Mixed-script artifacts:** `Таş Tepeler` (Cyrillic Т + Latin ş)

## Root Cause

LLM sub-agents default to Russian transliteration of foreign names when writing in Russian. They also naturally add Russian case endings to foreign words (`на Sayburçа`, `Çatalhöyükом`), which is grammatically natural but visually inconsistent when the name stem is kept in Latin script.

## Solution: Scripted Mass Normalization

### Phase 1 — Inventory

Find all non-standard variants:

```bash
cd chapters/
grep -rn "Гебекли\|Гёбекли\|Таш-Тепелер\|Невалы-Чори\|Карахантепе\|Сайбурч\b" *.md
```

### Phase 2 — Fix pairs (patch with replace_all=True)

For each variant pair, use patch tool or a Python script:

```python
FIXES = {
    'Гебекли-Тепе': 'Göbeklitepe',
    'Гёбекли-Тепе': 'Göbeklitepe',
    'Таш-Тепелер': 'Taş Tepeler',
    'Невалы-Чори': 'Nevalı Çori',
    'Карахантепе': 'Karahantepe',
    'Карахан-тепе': 'Karahantepe',  # hyphenated variant
    'Гёбекли-тепе': 'Göbeklitepe',  # hyphenated variant
    'Курту-тепе': 'Kurt Tepe',
    'Ташлы-тепе': 'Taşlı Tepe',
    'Сефер-тепе': 'Sefertepe',
    'Хамзан-Тепе': 'Hamzan Tepe',
    'Сёют-Тарласы': 'Söğüt Tarlası',
    'Бирис-Мез арлыгы': 'Biris Mezarlığı',
    'Йоунбурч': 'Yoğunburç',
    'Йенимахалле': 'Yenimahalle',
    'Ая̆нлар-Хёюк': 'Ayanlar Höyük',
    'Чатал-Хююк': 'Çatalhöyük',
    'Чайоню': 'Çayönü',
}
```

Run a Python script that iterates all `.md` files and replaces each old→new pair with `str.replace()`.

### Phase 3 — Case Declension Removal

Turkish names ending in `-e`, `-a`, or `-ç` (Göbeklitepe, Karahantepe, Sayburç, Çatalhöyük, etc.) attract Russian genitive/dative/ablative endings. Strip all by treating each known declension form:

```python
DECLENSION_FIXES = {
    'Sayburçа': 'Sayburç',
    'Sayburçе': 'Sayburç',
    'Sayburçу': 'Sayburç',
    'Sayburçом': 'Sayburç',
    'Çatalhöyükа': 'Çatalhöyük',
    'Çatalhöyükе': 'Çatalhöyük',
    'Çatalhöyükу': 'Çatalhöyük',
    'Çatalhöyükом': 'Çatalhöyük',
    'Çatalhöyüka': 'Çatalhöyük',
    'Çatalhöyüke': 'Çatalhöyük',
    'Harbetsuvanу': 'Harbetsuvan',
    'Harbetsuvanе': 'Harbetsuvan',
    'Göbeklitepeа': 'Göbeklitepe',
    'Göbeklitepeу': 'Göbeklitepe',
    'Göbeklitepeе': 'Göbeklitepe',
    'Göbeklitepeом': 'Göbeklitepe',
    'Karahantepeа': 'Karahantepe',
    'Karahantepeу': 'Karahantepe',
    'Karahantepeе': 'Karahantepe',
    'Nevalı Çoria': 'Nevalı Çori',
    'Nevalı Çorie': 'Nevalı Çori',
}
```

After stripping, the text reads slightly ungrammatically (prepositions without expected cases), but this is acceptable in Russian popular-science prose when foreign names are used — the preposition context carries meaning.

### Phase 4 — Mixed-Script Detection

Find instances where a Cyrillic character stands in for a visually identical Latin letter (e.g. Cyrillic `Т` instead of Latin `T`):

```bash
grep -rn '[А-Яа-яёЁ][a-zA-Z]' chapters/*.md | grep -v 'href\|http\|\.md\|\.png\|\.jpg'
```

Fix each with the correct Latin spelling.

### Phase 5 — Verification

```bash
# Check zero remaining old Russian forms
grep -rc "Гебекли\|Гёбекли\|Таш-Тепелер" chapters/ | grep -v ":0"

# Check zero declined forms  
grep -rc "Sayburçа\|Sayburçе\|Çatalhöyükом" chapters/ | grep -v ":0"
```

### Phase 6 — Fix Self-Reference Bugs

When a prologue or style guide says "I will use X, not Y", auto-replacement may corrupt the explanation:

- **Before fix:** `Göbeklitepe, а не Гёбекли-Тепе`
- **After naive replace:** `Göbeklitepe, а не Göbeklitepe` (broken)
- **Required:** Manual fix to `Göbeklitepe, а не «Гёбекли-Тепе»`

Always check the prologue/terminology note for this bug after running replacements.

## Order of Operations

1. Start with hyphenated variants (most specific: `Карахан-тепе` → `Karahantepe`)
2. Then unhyphenated (`Карахантепе` → `Karahantepe`)  
3. Then declension stripping
4. Then mixed-script fix (`Таş` → `Taş`)
5. Then prologue self-reference fix
6. Then verify with grep

## Typical Scale

For a 60,000-70,000 word book with 28 chapters:
- 150-250 terminology replacements across 15-20 files
- 250-350 declension stripping fixes across 20+ files
- 2-5 mixed-script fixes
- 1-2 self-reference bugs in prologue
