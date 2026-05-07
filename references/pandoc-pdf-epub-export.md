# Pandoc PDF + EPUB export for finished NFP manuscripts

Use when the user asks to create publication files from an existing `manuscript.md`, especially "PDF and EPUB" or "PDF with contents at the beginning".

## Confirmed workflow

From the project root:

```bash
mkdir -p exports
cat > pandoc-metadata.yaml <<'YAML'
---
title: "Название книги"
lang: ru-RU
mainfont: "DejaVu Serif"
sansfont: "DejaVu Sans"
monofont: "DejaVu Sans Mono"
fontsize: 12pt
geometry:
  - top=22mm
  - bottom=24mm
  - left=22mm
  - right=22mm
toc-title: "Содержание"
numbersections: false
---
YAML

pandoc pandoc-metadata.yaml manuscript.md \
  --from markdown \
  --pdf-engine=xelatex \
  --toc --toc-depth=2 \
  --top-level-division=chapter \
  -V documentclass=book \
  -V classoption=oneside \
  -o exports/<slug>.pdf

pandoc pandoc-metadata.yaml manuscript.md \
  --from markdown \
  --toc --toc-depth=2 \
  --split-level=2 \
  -o exports/<slug>.epub
```

## Why this shape

- `--toc` puts an automatic contents section at the beginning of the PDF, after the title page.
- `toc-title: "Содержание"` gives the Russian heading.
- `--toc-depth=2` is useful for manuscripts where the body contains `# Book Title` and `## Пролог/Часть/Глава`; it includes parts and chapter titles without flooding the TOC with `###` sections.
- `--top-level-division=chapter` + `documentclass=book` gives a book-like PDF structure.
- EPUB should also be built with `--toc`; Pandoc creates `EPUB/toc.ncx` and `EPUB/nav.xhtml`.

## Pre-flight checks

```bash
test -f manuscript.md
command -v pandoc
command -v xelatex
python3 - <<'PY'
from pathlib import Path
text = Path('manuscript.md').read_text(encoding='utf-8')
print('chars', len(text))
print('h1', sum(1 for l in text.splitlines() if l.startswith('# ')))
print('h2', sum(1 for l in text.splitlines() if l.startswith('## ')))
print('h3', sum(1 for l in text.splitlines() if l.startswith('### ')))
PY
```

## Verification

```bash
file exports/<slug>.pdf exports/<slug>.epub
ls -lh exports/<slug>.pdf exports/<slug>.epub
pdfinfo exports/<slug>.pdf | sed -n '1,12p'
pdftotext -f 1 -l 5 exports/<slug>.pdf - | head -80
python3 - <<'PY'
import zipfile, pathlib
p = pathlib.Path('exports/<slug>.epub')
with zipfile.ZipFile(p) as z:
    names = z.namelist()
    print('epub entries', len(names))
    print('mimetype', z.read('mimetype').decode('utf-8', 'ignore') if 'mimetype' in names else 'MISSING')
    print('toc files', [n for n in names if 'toc' in n.lower() or n.endswith('nav.xhtml')][:10])
PY
```

Expected:
- PDF is recognized as PDF and has nonzero pages.
- `pdftotext` shows: title page → `Содержание` → chapter/part list.
- EPUB is recognized as EPUB, `mimetype` is `application/epub+zip`, and it contains `EPUB/toc.ncx` plus `EPUB/nav.xhtml`.

## Pitfalls

- Do not hand-write a Markdown table of contents into the manuscript for PDF. Use Pandoc `--toc`; manual TOC duplicates the generated one and often has broken anchors.
- If the manuscript already starts with `# Название книги`, the PDF may show title twice: once from metadata and once as body H1/TOC entry. This may be acceptable for a quick export but for production remove the body title or build from a temporary export copy.
- If the book contains scripts beyond Cyrillic/Latin (Greek, Coptic, Hebrew), switch `mainfont` from DejaVu/Liberation to a font with coverage such as FreeSerif or Noto Serif.
- Always verify the PDF text extraction, not just file existence; missing fonts can produce a file that opens but has bad text output.
