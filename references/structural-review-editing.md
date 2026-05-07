# Structural review editing for NFP manuscripts

Use this when an external critic rates a complete nonfiction manuscript around 7–8/10 and asks for structural optimization rather than expansion.

## Pattern from session: Black Sea Greeks manuscript

Input review asked to:
- reorder chapters II–III to fix chronology;
- cut intro/chapter I repetition;
- compress chapter endings;
- strengthen the through-conflict (“battle for the sea”);
- standardize headings and remove unfinished editorial layers.

## Safe protocol

1. **Backup first.** Before any bulk edit or subagent pass:
   ```bash
   stamp=$(date +%Y%m%d_%H%M%S)
   mkdir -p backup_before_review_$stamp
   cp -a chapters manuscript.md backup_before_review_$stamp/
   ```

2. **Turn review into measurable constraints.** Examples:
   - intro: target cut 15–25%, not 60%; chapter I: target cut 10–20%; chapter V: target cut 10–15%;
   - chapter endings: 3–5 paragraphs, <=900 words;
   - no `###` if requested unified `#`/`##` hierarchy;
   - no `Ключевые понятия`, `3а`, TODO, CJK, HTML, markdown tables.

3. **Subagents are useful, but verify their scale immediately.** If a subagent rewrites/cuts far beyond the requested percentage (e.g. intro 6.2K → 2.2K, chapter 11.2K → 3.1K when asked for 15–20%), treat it as destructive. Restore from backup and do a surgical leading-agent pass. Do not accept the subagent's reconstruction narrative without checking the actual file.

3A. **Single-chapter destructive edit recovery.** If only one chapter was damaged (common with a long final chapter such as a war/biography section), restore that exact chapter from the timestamped pre-review backup before continuing:
   ```python
   from pathlib import Path
   import shutil
   root = Path('/root/hermes-nonfiction-pipeline/<slug>')
   shutil.copyfile(
       root/'backup_before_review_YYYYMMDD_HHMMSS/chapters/ch_05.md',
       root/'chapters/ch_05.md'
   )
   ```
   Then apply a deterministic/surgical cut yourself: remove only paragraphs whose content is clearly outside the review's requested focus, add at most short bridging replacements, and re-count words. Do **not** let the same subagent rebuild from side files such as `ch_05_expanded.md` unless the backup is unavailable; stale expansion files can silently change the chapter version.

4. **For chronology fixes, prefer assembly remapping over file renaming.** If `chapters/ch_02.md` contains classical material and `ch_03.md` contains Persian material, do not rename files unless the whole project expects it. Assemble in the new order and replace visible chapter headings in the final manuscript:
   ```python
   order=[('intro.md',None),('ch_01.md',None),('ch_03.md','persia_as_II'),('ch_02.md','classic_as_III'),('ch_04.md',None),('ch_05.md',None),('conclusion.md',None)]
   ```

5. **Cut by removing duplicate paragraphs, not by rewriting the book.** Good high-yield removals:
   - repeated myth/resource/geography blocks between introduction and chapter I;
   - repeated entity summaries already handled in later chapters;
   - overlong “Итог главы” sections that recap rather than bridge;
   - mechanical transition formulas (`Следующая глава покажет...`).

6. **Add conflict theses at chapter starts.** Each chapter should name the period’s contest in 1–2 paragraphs:
   - archaic: access to shores/markets/local alliances;
   - Persian: empire vs steppe vs straits;
   - classical: cities/Bosporus/Athens dependent on grain and steppe diplomacy;
   - Hellenistic: polis vs monarchy;
   - Mithridates: Black Sea system vs Rome.

7. **Final QA must be structural and textual.** Run word counts per chapter, heading scan, artifact scan, and review-specific checks. A QA subagent can verify, but the lead agent should also run deterministic checks. For Telegram delivery, copy the final `.md` to `/root/outputs/` and include `MEDIA:/absolute/path` in the same response that reports completion.

## Final 9/10 micro-optimization pass

Use this when the user asks for a late-stage “довести v3 до 9/10” pass with explicit percentage cuts and repeated-motif cleanup.

1. **Keep edits surgical and measurable.** Before cutting, record word counts for each target chapter. After each pass, report actual counts and make sure requested cuts are not accidentally doubled. If a cut overshoots, restore just that chapter/section from the backup and redo a narrower pass.
2. **Cut overloaded historical context by relevance to the book’s governing frame.** Example for Black Sea / ancient-border books: keep material tied to straits, ports, grain, fleet, local alliances, and resource control; remove background that turns a chapter into generic Achaemenid, Roman, or biographical exposition.
3. **For reference-heavy chapters, remove catalog paragraphs before touching narrative anchors.** High-yield cuts: coinage typologies, city planning, craft inventories, trade-route catalogues, generic chora descriptions. Preserve the 2–3 main city case studies and insert one compact sentence for secondary regions instead of a full subsection.
4. **For war/king chapters, audit every paragraph for geographic/resource anchoring.** If a paragraph about Sertorius, Lucullus, Pompey, Sulla, Roman civil politics, or a ruler’s childhood does not materially affect the Black Sea, Bosporus, Colchis, fleet, grain, ports, or manpower, compress or delete it. The goal is not a biography; it is the region’s political system under stress.
5. **Conclusion cuts need a hard guardrail.** A requested 10–15% conclusion cut means removing recap and extra final chords, not collapsing the conclusion by half. If the conclusion falls far below the requested range, restore from backup and remove only redundant recap paragraphs. End with one strong final thought.
6. **Repetition cleanup should verify zero or intentional residue.** For user-specified repeated formulas, run exact/lemma-ish searches after patching. If the user explicitly listed motifs like “не окраина, а центр”, “пространство борьбы”, “лаборатория”, “взаимозависимость”, “полисы лавировали”, treat remaining occurrences as defects unless they are deliberately preserved in a title and you can justify it.
7. **Assemble from canonical chapter files after patching.** If chapter file order differs from visible chronology, keep the remapping step in assembly and patch source chapters too; otherwise the final output can look clean while `chapters/` still contains stale repeated formulas.

## Deterministic checks

```python
import re, pathlib
man = pathlib.Path('manuscript.md').read_text(encoding='utf-8')
checks = {
    'CJK': len(re.findall(r'[\u4e00-\u9fff\u3040-\u30ff]', man)),
    'TODO': len(re.findall(r'TODO|FIXME|ПЛЕЙСХОЛДЕР|ЗАГЛУШКА', man, re.I)),
    'tables': sum(1 for l in man.splitlines() if re.match(r'\s*\|', l)),
    'html': len(re.findall(r'<[^>]+>|<!--', man)),
    'h3': len(re.findall(r'^### ', man, re.M)),
    '3a': man.count('3а'),
    'key_concepts': man.count('Ключевые понятия'),
    'mechanical_next': len(re.findall(r'Следующая глава|следующая глава', man)),
    'horizontal_rules': man.count('\n---\n'),
    'technical_markers': len(re.findall(r'КОНЕЦ_ДИАПАЗОНА|МОНТАЖ|ЧЕРНОВИК|===', man)),
    'english_common': len(re.findall(r'\b(chapter|section|draft|summary|TODO)\b', man, re.I)),
}
print(checks)
for s in re.split(r'(?m)^# ', man):
    if s.strip():
        print(s.splitlines()[0], len(re.findall(r'[А-Яа-яЁёA-Za-z0-9]+', s)))
for m in re.finditer(r'(?ms)^## Итог[^\n]*\n(.*?)(?=\n---\n|\n# |\Z)', man):
    body=m.group(1)
    paras=[p for p in body.strip().split('\n\n') if p.strip()]
    print('ИТОГ', len(paras), len(re.findall(r'[А-Яа-яЁёA-Za-z0-9]+', body)))
```

## Pitfalls

- Do not confuse “optimize” with “expand”. If the critic says the book is overloaded, stop adding material.
- Do not trust subagent summaries; verify actual file word counts and headings.
- Do not let physical file numbering dictate visible chapter chronology; final assembly can remap headings safely.
- Preserve enough volume: if the manuscript target is 60–80K and the edited result falls below 60K, reconsider cuts or restore selected material.