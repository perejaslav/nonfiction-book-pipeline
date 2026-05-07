# Full-book expansion waves from a detailed synopsis

Use when a user provides a complete chapter-by-chapter synopsis and expects a real manuscript-length book, not a compressed draft.

## Trigger
- User asks: “write the book from this plan/synopsis”.
- Or user complains: “why did you write so little?” / “expand every chapter according to the plan”.

## Proven workflow

1. **Count first**
   - Count words for every `chapters/*.md`.
   - Compare against the synopsis target per chapter.
   - Create an explicit deficit list.

2. **Wave structure**
   - Run a context-map subagent for a cluster of chapters; it reads synopsis + foundation + current chapters and reports gaps without editing.
   - Run writing subagents for specific chapters or chapter halves.
   - After every wave, re-count and re-check artifacts.

3. **Avoid same-file races**
   - If two agents need to work on the same long chapter, only one writes `chapters/ch_XX.md` directly.
   - The other writes `chapters/ch_XX_expansion_section_range.md` with ready insertion blocks.
   - The lead agent merges manually, then verifies headings and word count.

4. **Verification after each wave**
   ```python
   import re, pathlib
   for p in pathlib.Path('chapters').glob('*.md'):
       t = p.read_text(encoding='utf-8')
       print(p.name, len(re.findall(r'[А-Яа-яЁёA-Za-z0-9]+', t)),
             'CJK', len(re.findall(r'[\u4e00-\u9fff\u3040-\u30ff]', t)),
             'mixed', len(re.findall(r'\b[a-zA-Z]{3,}[а-яА-ЯёЁ]{1,4}\b', t)))
   ```

5. **Final assembly**
   - Concatenate in chapter order to `manuscript.md`.
   - For Telegram delivery, copy final `.md` to `/root/outputs/` and attach it via `MEDIA:/absolute/path`.
   - PDF only if requested.

## Pitfalls
- A first-pass “book” can land at 30–40K even when the plan asks for 70K. Treat that as incomplete, not done.
- Timed-out subagents may have written usable files; always check disk before relaunching.
- Subagents can over-report target completion; trust your own word-count script.
- Parallel edits to the same file cause lost work or duplicate sections unless one agent writes a separate expansion file.
