# Manuscript repetition audit

Use for final-pass editing of an existing NFP manuscript when the main problem is repetition and rhythm rather than facts.

## Goal
- Remove accidental duplicate arguments, recap paragraphs, and near-identical sentence openings.
- Keep only intentional refrains that strengthen the ending or chapter transitions.

## Workflow
1. Scan the whole manuscript once for repeated anchors:
   - repeated formulae (`не просто X, а Y`, `империя ...`, `персепольские таблички ...`)
   - repeated proper-noun explanations
   - repeated closing arguments in late chapters / epilogue
2. Inspect each repetition in context before patching.
3. Prefer one of three fixes:
   - delete the weaker duplicate,
   - compress it into a shorter bridge,
   - rephrase it so the wording and rhythm differ.
4. Preserve only deliberate refrains in the final chapter / epilogue.
5. Verify with `search_files` that the old wording is gone and the remaining repetition is intentional.

## Practical rule
If a line explains the same fact in the same syntactic shape for the third time, it is usually noise.

## Useful checks
- `search_files` for repeated phrases
- `read_file(offset, limit)` around each match
- final pass should end with a short list of remaining intentional refrains, not many near-duplicates

## Lexical repetition detector (from booksmith-ru)

### Algorithm

1. Extract **5–10 key phrases** (3–5 words each) from the current chapter — theses, claims, scene descriptions, argumentative pivots.
2. Compare each phrase against `continuity_map.md` and all previously written chapters.
3. If similarity > 70% with any earlier passage → mark as potential repetition.
4. Decide: **remove** (if pure duplicate), **merge** (if partial overlap), or **move** (if belongs in a different chapter).
5. Record the decision in the self-check report.

### Python implementation sketch

```python
import re
from collections import Counter

def extract_key_ngrams(text: str, n: int = 3, top_k: int = 10) -> list[str]:
    \"\"\"Extract top-K n-grams as candidate key phrases.\"\"\"
    words = re.findall(r'[а-яё]+', text.lower())
    ngrams = [' '.join(words[i:i+n]) for i in range(len(words)-n+1)]
    return [ng for ng, _ in Counter(ngrams).most_common(top_k)]

def similarity(a_ngrams: list[str], b_ngrams: list[str]) -> float:
    \"\"\"Jaccard similarity between two n-gram sets.\"\"\"
    set_a, set_b = set(a_ngrams), set(b_ngrams)
    return len(set_a & set_b) / len(set_a | set_b) if set_a | set_b else 0.0

# Usage:
# current = extract_key_ngrams(chapter_text)
# previous = extract_key_ngrams(previous_chapter_text)
# if similarity(current, previous) > 0.7:
#     print(f"⚠ Potential repetition (J={similarity(current, previous):.2f})")
```

### Threshold note

- **>70%** — likely duplicate, requires action.
- **50–70%** — check context; may be acceptable if the phrases serve different arguments.
- **<50%** — safe.

### Integration with continuity_map.md

Use `continuity_map.md` "Repeated Motifs / Claims" section to track already-used key phrases across the book. Before writing each new chapter, scan this section to avoid accidental repetition.
