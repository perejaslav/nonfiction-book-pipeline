# Evidence Packs vs Facts

`facts.json` is the atomic fact base: short, referenceable claims with confidence and verification metadata.

`foundation/evidence/ch_XX.md` is the chapter-level synthesis layer: it groups sources, caveats, expert positions, statistics, and safe wording for the specific argumentative needs of one chapter.

Use evidence packs when a chapter contains dense factual argumentation, contested interpretation, statistics, or source-sensitive narrative reconstruction.

Safe wording examples:
- "по некоторым оценкам..."
- "один из ранних известных примеров..."
- "источники расходятся в деталях..."
- "в историографии чаще всего считают..."

## Evidence Gaps

Для каждой главы, где есть фактические утверждения без надёжного источника, вести `foundation/evidence_gaps.md` (см. `templates/evidence_gaps.md`). Записи с риском **ВЫСОКИЙ** должны быть разрешены до финальной валидации манускрипта.
