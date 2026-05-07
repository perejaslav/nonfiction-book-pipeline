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
