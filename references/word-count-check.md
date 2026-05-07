# Word Count & Quality Check Script

Use this script at every expansion phase to get a complete picture of the book.

```python
import os, re

chapters_dir = '/root/hermes-nonfiction-pipeline/derzhava-ahemenidov/chapters'
out_path = '/root/hermes-nonfiction-pipeline/derzhava-ahemenidov/manuscript.md'

def count_words(text):
    return len(re.findall(r'[а-яА-ЯёЁa-zA-Z]+', text))

def check_chapters(chapters_dir):
    files = sorted(os.listdir(chapters_dir))
    print("=== CHAPTER QUALITY CHECK ===\n")
    total = 0
    short = []
    for f in files:
        path = os.path.join(chapters_dir, f)
        with open(path) as fh:
            content = fh.read()
        wc = count_words(content)
        total += wc
        is_special = 'prologue' in f or 'epilogue' in f
        target = 1500 if is_special else 3000
        ok = wc >= target * 0.8
        flag = '' if ok else ' ⚠'
        print(f"{f}: {wc} слов (цель ~{target}){flag}")
        if not ok and not is_special:
            short.append((f, wc, target))
    
    print(f"\n{'='*40}")
    print(f"ИТОГО: {total} слов")
    print(f"До цели (80К): {80000 - total} слов")
    if short:
        print(f"Короткие: {[(f, wc) for f, wc, _ in short]}")

def check_manuscript(out_path):
    with open(out_path) as f:
        text = f.read()
    words = count_words(text)
    required = ['Пролог', 'Глава 1', 'Глава 2', 'Глава 3', 'Глава 4', 'Глава 5',
                'Глава 6', 'Глава 7', 'Глава 8', 'Глава 9', 'Глава 10',
                'Глава 11', 'Глава 12', 'Глава 13', 'Глава 14', 'Глава 15', 'Глава 16',
                'Глава 17', 'Глава 18', 'Глава 19', 'Глава 20',
                'Глава 21', 'Глава 22', 'Глава 23', 'Глава 24',
                'Глава 25', 'Глава 26', 'Глава 27', 'Глава 28',
                'Эпилог']
    missing = [h for h in required if h not in text]
    print(f"\n=== MANUSCRIPT CHECK ===")
    print(f"Слов: {words:,} / 80 000")
    print(f"Процент: {words/80000*100:.1f}%")
    print(f"Отсутствуют разделы: {missing if missing else 'НЕТ'}")

# Run both
check_chapters(chapters_dir)
check_manuscript(out_path)
```

## Expansion Decision Thresholds

| Condition | Action |
|-----------|--------|
| Any chapter <80% of 3,000-word target | Run Expansion |
| Total <75% of 80,000-word target | Run Expansion + 2nd pass |
| All chapters ≥80% | Done — skip Expansion |
| ch_24 or ch_28 <85% after Expansion | Dedicated single-chapter pass |

## Thresholds for Accepting the Book

- Target: 80,000 words
- Acceptable range: 78,000–80,000 words (97.5–100%)
- Below 75,000 words (93.7%): mandatory additional expansion
- Above 80,000 words: acceptable, no trimming required
