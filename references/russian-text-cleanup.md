# Russian Text Cleanup: English Fragments & CJK Chars

## Problem

Generative output (GPT/Codex responses) frequently leaves English words embedded in Russian text, plus occasional Chinese/Japanese characters. The pattern is consistent across sessions.

## Detection

```python
import re

def check_russian_text(text):
    """Find English words in Russian context."""
    issues = []
    for i, line in enumerate(text.split('\n'), 1):
        en_words = re.findall(r'\b[a-zA-Z]{4,}\b', line)
        if en_words and re.search('[а-яА-ЯёЁ]', line):
            # Filter false positives (scientific terms, etc.)
            bad = [w for w in en_words if w.lower() not in
                   ['tea', 'egcg', 'cg', 'g', 'kg', 'mg', 'ml', 'cm', 'mm',
                    'km', 'ph', 'dna', 'pubmed', 'koichi', 'wakata',
                    'l-theanine', 'theanine', 'rna', 'dna', 'cg', 'cg']]
            if bad:
                issues.append((i, line[:100], bad))
    return issues

# CJK character check
def has_cjk(text):
    return bool(re.search(r'[\u4e00-\u9fff\u3040-\u30ff]', text))
```

## Known False Positives (safe to skip)

Terms that legitimately appear in Russian academic text:
`tea`, `egcg`, `l-theanine`, `theanine`, `pubmed`, `koichi`, `wakata`, `dna`, `rna`, `mg`, `kg`, `ml`, `cm`, `mm`, `km`, `ph`, `cg`

## Known English Fragments (always replace)

Word boundaries matter — `\b` is unreliable across script boundaries. Direct string matching often works better:

| English | Russian |
|---------|---------|
| lower | более низкий |
| data | данные |
| observed | наблюдаемые |
| potential | потенциальный |
| contributes | вносит вклад |
| hundred | сотен |
| peak | пиковая |
| roughly | примерно |
| partially | частично |
| less | меньше |
| erosion | эрозии |
| effect | эффект |
| sedation | седации |
| observational | наблюдательное |
| better | лучшее |
| aid | средство |
| single | единичное |
| damage | повредить |
| negative | негативный |
| twenty | двадцать |
| forty | сорок |
| three | три |
| five | пять |
| ten | десять |
| twelve | двенадцать |

Also patterns:
- `Koichi Wakata aboard` → `Коити Ваката на борту`
- Numbers embedded in English: `sixteen`, `three`, etc. → русские цифры

## Cleanup Workflow

1. **Pass 1**: Global regex replacements for common fragments
2. **Pass 2**: Direct `patch` for remaining stubborn fragments (regex `\b` fails on Cyrillic-adjacent words)
3. **Pass 3**: Verify with script — check CJK + English-in-Russian
4. **Pass 4**: Manual patch if verification still shows issues

Regex `\bword\b` is unreliable when the word is adjacent to Cyrillic characters. Prefer direct `text.replace(old, new)` or `re.sub(r'\bword\b', ...)` with careful testing.

## CJK Cleanup

Common artifact: `的大量ное` (残留 Chinese char). Fix: `text.replace('的大量ное', ' большое')` or similar.
